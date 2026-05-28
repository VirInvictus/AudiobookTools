"""Command-line interface for AudiobookTools.

Two subcommands::

    audiobooktools retag    [--library PATH] [--catalog PATH]
                            [--apply | --restore PATH] [--verbose]
    audiobooktools reorg    [--library PATH] [--catalog PATH]
                            [--apply | --reverse PATH]

Discovery rules when ``--catalog`` or ``--library`` are omitted are documented
on :func:`discover_catalog` and :func:`discover_library`. Either flag can be
passed explicitly to override.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

from audiobooktools import __version__


# ---- discovery -------------------------------------------------------------
def discover_catalog(start: Path | None = None) -> Path | None:
    """Walk up from ``start`` (or ``$PWD``) looking for ``catalog/books.py``.

    Returns the first match, or ``None`` if none is found before the
    filesystem root.
    """
    here = (start or Path.cwd()).resolve()
    for parent in (here, *here.parents):
        candidate = parent / "catalog" / "books.py"
        if candidate.is_file():
            return candidate
    return None


def _looks_like_library(p: Path) -> bool:
    """A directory looks like an audiobook library if it has at least two
    immediate subdirectories that are not dotfiles or the magic
    ``Unfiltered`` staging area. Cheap heuristic, deliberately loose."""
    if not p.is_dir():
        return False
    visible_dirs = [
        d
        for d in p.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "Unfiltered"
    ]
    return len(visible_dirs) >= 2


def discover_library(catalog_path: Path | None) -> Path | None:
    """Pick a library root.

    Preferred: the directory two levels above the catalog file
    (``<X>/catalog/books.py`` -> ``<X>``), if it looks like a library.
    Fallback: ``$PWD`` if it looks like a library. Otherwise ``None``.
    """
    if catalog_path is not None:
        candidate = catalog_path.resolve().parent.parent
        if _looks_like_library(candidate):
            return candidate
    cwd = Path.cwd().resolve()
    if _looks_like_library(cwd):
        return cwd
    return None


# ---- catalog loading -------------------------------------------------------
def load_catalog(catalog_path: Path) -> tuple[list[dict], dict[str, str] | None]:
    """Import a catalog module by file path and return ``(BOOKS, DESC)``.

    The catalog module is loaded via ``importlib.util.spec_from_file_location``
    so it doesn't need to be on ``sys.path``. ``BOOKS`` is required; ``DESC``
    is optional (returned ``None`` if absent).
    """
    catalog_path = catalog_path.resolve()
    parent_dir = catalog_path.parent.parent  # repo root containing catalog/
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    spec = importlib.util.spec_from_file_location("catalog.books", catalog_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load catalog from {catalog_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if not hasattr(mod, "BOOKS"):
        raise RuntimeError(f"catalog {catalog_path} does not export BOOKS")
    desc = getattr(mod, "DESC", None)
    return mod.BOOKS, desc


# ---- argument parser -------------------------------------------------------
def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--library",
        type=Path,
        default=None,
        help="library root (default: discover from catalog or $PWD)",
    )
    p.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="catalog file (default: walk up from $PWD looking for catalog/books.py)",
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="audiobooktools",
        description="Tag and folder normalization for personal audiobook libraries.",
    )
    ap.add_argument("--version", action="version", version=f"audiobooktools {__version__}")
    sub = ap.add_subparsers(dest="command", required=True)

    retag_p = sub.add_parser("retag", help="normalize embedded tags from the catalog")
    _add_common_args(retag_p)
    g = retag_p.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true", help="write changes (after backing up)")
    g.add_argument(
        "--restore",
        metavar="JSON",
        type=Path,
        help="restore tags from a previous backup file",
    )
    retag_p.add_argument("--verbose", action="store_true", help="show per-file diffs in full")
    retag_p.add_argument(
        "--backup",
        type=Path,
        default=None,
        help="backup path (default: <library>/.audiobooktools/backup.json)",
    )

    reorg_p = sub.add_parser("reorg", help="reorganize files into the canonical tree")
    _add_common_args(reorg_p)
    g = reorg_p.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true", help="execute the moves")
    g.add_argument(
        "--reverse",
        metavar="JSON",
        type=Path,
        help="undo a prior apply using its manifest",
    )
    reorg_p.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="manifest path (default: <library>/.audiobooktools/reorg-manifest.json)",
    )

    return ap


# ---- main ------------------------------------------------------------------
def _resolve_inputs(args: argparse.Namespace) -> tuple[Path, Path]:
    catalog = args.catalog or discover_catalog()
    if catalog is None:
        raise SystemExit(
            f"no --catalog given and no catalog/books.py found walking up from {Path.cwd()}"
        )
    library = args.library or discover_library(catalog)
    if library is None:
        raise SystemExit(
            "no --library given and could not infer one from the catalog location or $PWD"
        )
    return library.resolve(), catalog.resolve()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # restore / reverse short-circuit catalog discovery: they only need the
    # library root (and not even that for reverse, since the manifest holds
    # absolute paths).
    if args.command == "retag" and args.restore:
        from audiobooktools.retag import restore

        library = args.library or discover_library(args.catalog or discover_catalog())
        if library is None:
            raise SystemExit("restore requires --library or an inferable library root")
        restore(args.restore, library.resolve())
        return 0

    if args.command == "reorg" and args.reverse:
        from audiobooktools.reorg import do_reverse

        do_reverse(args.reverse)
        return 0

    library, catalog = _resolve_inputs(args)
    books, _desc = load_catalog(catalog)

    if args.command == "retag":
        from audiobooktools.retag import run as retag_run

        return retag_run(
            library,
            books,
            apply=args.apply,
            verbose=args.verbose,
            backup_path=args.backup,
        )

    if args.command == "reorg":
        from audiobooktools.reorg import run as reorg_run

        return reorg_run(library, books, apply=args.apply, manifest_path=args.manifest)

    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
