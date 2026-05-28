"""Reorganize an audiobook library into a clean Audiobookshelf-standard tree.

Layout: ``Author/Series/"## - Title"/files``, where a series subfolder is used
only when 2+ books of that series are owned; standalones and lone series
entries go directly under the author. All target names are derived from the
catalog tags, so the tree and the embedded metadata can't drift.

Programmatic entry point is :func:`run`. Moves and renames only; nothing is
ever deleted, so the manifest fully reverses every operation.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from audiobooktools import retag, schema

AUDIO_EXT = {".m4b", ".mp3", ".m4a"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}


# ---- enumeration -----------------------------------------------------------
def source_root(book: dict, library_root: Path) -> Path:
    if book["layout"] == "discs":
        return library_root / book["disc_root"]
    if "file" in book:
        return (library_root / book["file"]).parent
    return library_root / Path(book["glob"]).parent


def audio_moves(book: dict, library_root: Path, counts: dict[str, int]) -> list[tuple[Path, Path]]:
    t = book["tags"]
    label = schema.sanitize(t["album"])
    layout = book["layout"]
    dest = schema.book_dir(book, counts)
    moves = []
    for i, (path, _ov) in enumerate(retag.resolve_files(book, library_root, counts), 1):
        ext = path.suffix
        if layout == "single":
            dst = dest / f"{label}{ext}"
        elif layout == "parts":
            dst = dest / f"{label}, Part {i}{ext}"
        elif layout == "chapters":
            dst = dest / path.name  # already-clean chapter names: keep
        elif layout == "discs":
            tn = retag.leading_track_num(path.name) or i
            dst = dest / path.parent.name / f"{tn:02d} - {label}{ext}"
        else:
            raise ValueError(layout)
        dst_abs = library_root / dst
        if path.resolve() != dst_abs.resolve():  # skip already-in-place files
            moves.append((path, dst_abs))
    return moves


def extra_moves(
    books: list[dict], library_root: Path, counts: dict[str, int]
) -> list[tuple[Path, Path]]:
    """Route cover images and .epub/.nfo/.cue/.txt to each book's destination."""
    by_root: dict[Path, list[int]] = defaultdict(list)
    for idx, b in enumerate(books):
        by_root[source_root(b, library_root)].append(idx)
    stems = {
        idx: {p.stem for p, _ in retag.resolve_files(books[idx], library_root, counts)}
        for idx in range(len(books))
    }

    moves, cover_taken, consumed = [], set(), set()

    # Pass 1: per-book extras living in the same dir as the book's audio
    # (covers, .nfo/.cue/.txt/.epub siblings).
    for root, idxs in by_root.items():
        if not root.exists():
            continue
        # At the library root itself, loose files (wishlist.md, etc.) are not
        # book extras: only stem-matched files belong to the lone root-level
        # book, if any.
        match_by_stem = len(idxs) > 1 or root == library_root
        for f in sorted(root.iterdir()):
            if not f.is_file() or f.suffix.lower() in AUDIO_EXT:
                continue
            if match_by_stem:
                target = next((i for i in idxs if f.stem in stems[i]), None)
            else:
                target = idxs[0]
            if target is None:
                continue  # left for Pass 2 (series-level extras)
            dest = schema.book_dir(books[target], counts)
            if f.suffix.lower() in IMAGE_EXT and target not in cover_taken:
                cover_taken.add(target)
                moves.append((f, library_root / dest / "cover.jpg"))
            else:
                moves.append((f, library_root / dest / "_extras" / f.name))
            consumed.add(f)

    # Pass 2: series-level / group-level extras. The Hyperion 'Collected
    # Artwork' subtree, Acts of Caine's Maps/ and eBooks/ subfolders,
    # Stephen King's whole-series epub at the parent of the four book
    # folders, Master & Margarita's parent-level PDF: things that belong to
    # the whole work-group rather than a specific book. Group books by their
    # Unfiltered/<work-group>/ ancestor.
    groups: dict[Path, list[int]] = defaultdict(list)
    for idx, b in enumerate(books):
        root = source_root(b, library_root)
        if root == library_root:
            continue
        try:
            rel = root.relative_to(library_root)
        except ValueError:
            continue
        if not rel.parts or rel.parts[0] != "Unfiltered" or len(rel.parts) < 2:
            continue
        groups[library_root / "Unfiltered" / rel.parts[1]].append(idx)

    for group, idxs in groups.items():
        if not group.exists() or not idxs:
            continue
        # Destination: series _extras when all group-books share a series with
        # a series folder, else the first book's own _extras.
        sers = {books[i]["tags"].get("series", "") for i in idxs}
        first_book = books[idxs[0]]
        if len(sers) == 1 and (s := next(iter(sers))) and counts.get(s, 0) >= 2:
            extras_dest = (
                library_root
                / schema.sanitize(first_book["tags"]["author"])
                / schema.sanitize(s)
                / "_extras"
            )
        else:
            extras_dest = library_root / schema.book_dir(first_book, counts) / "_extras"

        for f in sorted(group.rglob("*")):
            if not f.is_file() or f.suffix.lower() in AUDIO_EXT:
                continue
            if f in consumed:
                continue
            rel = f.relative_to(group)
            moves.append((f, extras_dest / rel))
    return moves


def all_moves(books: list[dict], library_root: Path) -> list[tuple[Path, Path]]:
    counts = schema.owned_counts(books)
    moves = []
    for b in books:
        moves += audio_moves(b, library_root, counts)
    moves += extra_moves(books, library_root, counts)
    return moves


# ---- apply / reverse -------------------------------------------------------
def _check(moves):
    seen, problems = {}, []
    for src, dst in moves:
        if not src.exists():
            problems.append(f"missing source: {src}")
        if dst in seen:
            problems.append(f"two sources map to {dst}:\n   {seen[dst]}\n   {src}")
        seen[dst] = src
        if dst.exists() and dst not in {d for _, d in moves}:
            problems.append(f"destination exists: {dst}")
    return problems


def prune_empty_dirs(books: list[dict], library_root: Path) -> None:
    """Remove now-empty original top-level folders.

    Only walks directories that were source roots for at least one book.
    Never touches new author dirs.
    """
    old_tops = set()
    for b in books:
        rel = source_root(b, library_root).relative_to(library_root)
        if rel.parts:
            old_tops.add(library_root / rel.parts[0])
    for top in old_tops:
        if not top.exists():
            continue
        for dirpath, _dirnames, _filenames in os.walk(top, topdown=False):
            p = Path(dirpath)
            if not any(p.iterdir()):
                p.rmdir()
                print(f"  rmdir {p.relative_to(library_root)}")


def default_manifest_path(library_root: Path) -> Path:
    return library_root / ".audiobooktools" / "reorg-manifest.json"


def do_apply(
    moves, books: list[dict], library_root: Path, manifest_path: Path | None = None
) -> None:
    manifest = []
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        manifest.append({"src": str(src), "dst": str(dst)})
    prune_empty_dirs(books, library_root)
    mpath = manifest_path or default_manifest_path(library_root)
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    print(f"\nmoved {len(manifest)} files; manifest at {mpath}")


def do_reverse(manifest_path: Path) -> None:
    data = json.loads(Path(manifest_path).read_text())
    for entry in reversed(data):
        src, dst = Path(entry["src"]), Path(entry["dst"])
        if not dst.exists():
            print(f"!! missing (skip): {dst}")
            continue
        src.parent.mkdir(parents=True, exist_ok=True)
        dst.rename(src)
    print(f"reversed {len(data)} moves from {manifest_path}")


# ---- reporting -------------------------------------------------------------
def print_dry_run(moves, library_root: Path) -> None:
    by_dir = defaultdict(list)
    for src, dst in moves:
        by_dir[dst.parent.relative_to(library_root)].append((src, dst))
    for d in sorted(by_dir, key=str):
        print(f"\n■ {d}{os.sep}")
        for src, dst in by_dir[d]:
            same = src.parent == dst.parent
            arrow = src.name if not same else f"(in place) {src.name}"
            print(f"    {arrow}\n        → {dst.name}")


def run(
    library_root: Path,
    books: list[dict],
    *,
    apply: bool = False,
    manifest_path: Path | None = None,
) -> int:
    """Plan or execute the reorganization pass.

    When ``apply`` is False, prints a dry-run diff and returns 0 if the move
    plan has no problems. When ``apply`` is True, executes the moves and
    writes a reversible manifest.
    """
    moves = all_moves(books, library_root)
    problems = _check(moves)
    if problems:
        print("REFUSING: pre-flight problems:")
        for p in problems:
            print("  - " + p)
        return 1

    if apply:
        do_apply(moves, books, library_root, manifest_path=manifest_path)
    else:
        print_dry_run(moves, library_root)
        print(f"\n{'=' * 60}\nDRY RUN: {len(moves)} files would move. --apply to execute.")
    return 0


# ---- legacy CLI entry (canonical CLI lives in audiobooktools.cli) ----------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--library", required=True, type=Path)
    ap.add_argument("--catalog", required=True, type=Path)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true")
    g.add_argument("--reverse", metavar="JSON", type=Path)
    ap.add_argument("--manifest", type=Path, default=None)
    args = ap.parse_args(argv)

    if args.reverse:
        do_reverse(args.reverse)
        return 0

    from audiobooktools.cli import load_catalog

    books, _ = load_catalog(args.catalog)
    return run(args.library, books, apply=args.apply, manifest_path=args.manifest)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
