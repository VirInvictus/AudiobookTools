"""Normalize embedded audio tags from a catalog.

Edits tags in place with mutagen (no audio re-encode; cover art and m4b chapter
tracks are left untouched). Default mode is a no-write dry run.

Programmatic entry point is :func:`run`; the CLI in :mod:`audiobooktools.cli`
calls it after resolving the library root and catalog. A legacy ``__main__``
block is preserved so ``python -m audiobooktools.retag --library PATH`` still
works for ad-hoc invocation, but the canonical CLI is ``audiobooktools retag``.

Idempotent: a second ``--apply`` (or dry run) after applying reports zero
changes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from mutagen.id3 import (
    COMM,
    ID3,
    TALB,
    TCOM,
    TCON,
    TDRC,
    TIT2,
    TIT3,
    TPE1,
    TPE2,
    TPOS,
    TRCK,
    TXXX,
    ID3NoHeaderError,
)
from mutagen.mp4 import MP4, MP4FreeForm

from audiobooktools import schema

# ---- physical tag keys -----------------------------------------------------
FF = "----:com.apple.iTunes:"
SERIES, SERIESPART = FF + "SERIES", FF + "SERIES-PART"
SUBTITLE, NARRATOR_FF = FF + "SUBTITLE", FF + "NARRATOR"

# Friendly labels for the dry-run report.
LABEL = {
    "\xa9nam": "title",
    "TIT2": "title",
    SUBTITLE: "subtitle",
    "TIT3": "subtitle",
    "\xa9ART": "author",
    "TPE1": "author",
    "aART": "album_artist",
    "TPE2": "album_artist",
    "\xa9wrt": "narrator",
    "TCOM": "narrator",
    NARRATOR_FF: "narrator·ff",
    "TXXX:NARRATOR": "narrator·ff",
    "\xa9alb": "album",
    "TALB": "album",
    "\xa9gen": "genre",
    "TCON": "genre",
    "\xa9day": "year",
    "TDRC": "year",
    SERIES: "series",
    "TXXX:SERIES": "series",
    SERIESPART: "series#",
    "TXXX:SERIES-PART": "series#",
    "trkn": "track",
    "TRCK": "track",
    "disk": "disc",
    "TPOS": "disc",
    "\xa9cmt": "comment",
    "desc": "desc",
    "COMM": "comment",
    "stik": "mediatype",
}

JUNK_COMMENT = re.compile(r"^\s*(chapter\s+\d+|read by\b.*)\s*;?\s*$", re.IGNORECASE)
_LEADING_NUM = re.compile(r"^\s*(\d+)\s*[-.]?\s*(.*)$")

_AUDIO_EXT = {".m4b", ".m4a", ".mp3"}


# ---- pure helpers (unit-tested) -------------------------------------------
def chapter_title_from_filename(name: str) -> str:
    """'01 Benna Murcatto Saves a Life.mp3' -> 'Benna Murcatto Saves a Life'.

    Returns ``""`` when the stem is only a number ('01.mp3' -> ''), so the
    caller can substitute the book title for sets with no real per-chapter
    names. An underscore directly before a space ('Chapter 01_ Legate') is the
    NTFS-safe stand-in for a colon and is restored.
    """
    stem = Path(name).stem
    m = _LEADING_NUM.match(stem)
    rest = m.group(2).strip() if m else stem
    rest = re.sub(r"[\s\-_:]+\d+$", "", rest).strip(" -_:\t")
    return re.sub(r"_(?=\s)", ":", rest)


def natkey(p: Path) -> list:
    """Natural sort key so '010.mp3' sorts after '09.mp3', not after '01.mp3'."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def leading_track_num(name: str) -> int | None:
    """Extract the leading track number from a filename."""
    m = _LEADING_NUM.match(Path(name).stem)
    return int(m.group(1)) if m else None


def disc_num_from_folder(name: str) -> int | None:
    """Extract the disc number from a folder name."""
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else None


def is_junk_comment(value: str) -> bool:
    """Check if a comment string is junk metadata."""
    return bool(value) and bool(JUNK_COMMENT.match(value))


# ---- MP4 read/write --------------------------------------------------------
def _mp4_read(audio: MP4, key: str) -> str:
    """Read a value from an MP4 audio tag."""
    if key not in audio:
        return ""
    val = audio[key]
    if key in ("trkn", "disk"):
        i, n = (val[0] + (0,))[:2]
        return f"{i}/{n}" if n else str(i)
    if key == "stik":
        return str(val[0])
    if key.startswith("----"):
        return bytes(val[0]).decode("utf-8", "replace")
    return str(val[0])


def _mp4_write(audio: MP4, key: str, value: str) -> None:
    """Write a value to an MP4 audio tag."""
    if value == "":
        audio.pop(key, None)
        return
    if key in ("trkn", "disk"):
        i, n = (value.split("/") + ["0"])[:2]
        audio[key] = [(int(i), int(n))]
    elif key == "stik":
        audio[key] = [int(value)]
    elif key.startswith("----"):
        audio[key] = [MP4FreeForm(value.encode("utf-8"))]
    else:
        audio[key] = [value]


# ---- MP3 read/write --------------------------------------------------------
_TEXT = {
    "TIT2": TIT2,
    "TIT3": TIT3,
    "TPE1": TPE1,
    "TPE2": TPE2,
    "TCOM": TCOM,
    "TALB": TALB,
    "TCON": TCON,
    "TDRC": TDRC,
    "TRCK": TRCK,
    "TPOS": TPOS,
}


def _mp3_read(id3: ID3, key: str) -> str:
    """Read a value from an MP3 ID3 tag."""
    if key == "COMM":
        frames = id3.getall("COMM")
        return str(frames[0].text[0]) if frames and frames[0].text else ""
    if key.startswith("TXXX:"):
        frame = id3.get(key)
        return str(frame.text[0]) if frame and frame.text else ""
    frame = id3.get(key)
    return str(frame.text[0]) if frame and getattr(frame, "text", None) else ""


def _mp3_write(id3: ID3, key: str, value: str) -> None:
    """Write a value to an MP3 ID3 tag."""
    if key == "COMM":
        id3.delall("COMM")
        if value:
            id3.add(COMM(encoding=3, lang="eng", desc="", text=[value]))
        return
    if key.startswith("TXXX:"):
        id3.delall(key)
        if value:
            id3.add(TXXX(encoding=3, desc=key.split(":", 1)[1], text=[value]))
        return
    if value == "":
        id3.delall(key)
    else:
        id3.setall(key, [_TEXT[key](encoding=3, text=[value])])


# ---- desired physical tags for one file ------------------------------------
def desired_physical(
    tags: dict,
    *,
    is_mp4: bool,
    title: str,
    narrator: str,
    track: str | None,
    disc: str | None,
) -> dict:
    """Map the logical catalog tags onto concrete physical tag keys.

    A value of ``""`` means "remove this tag"; keys omitted entirely are left
    as-is. ``narrator`` is resolved by the caller (catalog value, or the
    file's existing credit when the catalog says ``None``) so per-book casts
    are never flattened.
    """
    d: dict[str, str] = {}

    def put(mp4_keys, mp3_keys, value):
        for k in mp4_keys if is_mp4 else mp3_keys:
            d[k] = value

    put(["\xa9nam"], ["TIT2"], title)
    put([SUBTITLE], ["TIT3"], tags["subtitle"])
    put(["\xa9ART", "aART"], ["TPE1", "TPE2"], tags["author"])
    put(["\xa9wrt", NARRATOR_FF], ["TCOM", "TXXX:NARRATOR"], narrator)
    put(["\xa9alb"], ["TALB"], tags["album"])
    put(["\xa9gen"], ["TCON"], tags["genre"])
    put(["\xa9day"], ["TDRC"], tags["year"])
    put([SERIES], ["TXXX:SERIES"], tags["series"])
    put([SERIESPART], ["TXXX:SERIES-PART"], tags["series_index"])
    if tags.get("description") is not None:
        put(["\xa9cmt", "desc"], ["COMM"], tags["description"])
    if track is not None:
        put(["trkn"], ["TRCK"], track)
    if disc is not None:
        put(["disk"], ["TPOS"], disc)
    if is_mp4:
        d["stik"] = "2"  # iTunes media type: Audiobook
    return d


# ---- file enumeration per layout -------------------------------------------
def _top_audio(d: Path) -> list[Path]:
    """Return all audio files in the top level of a directory."""
    return sorted(
        (p for p in d.iterdir() if p.is_file() and p.suffix.lower() in _AUDIO_EXT),
        key=natkey,
    )


def _book_root(book: dict, library_root: Path, counts: dict[str, int]) -> Path:
    """Pick this book's actual on-disk root.

    Probe order (use the first existing match):

    1. The canonical destination from :func:`schema.book_dir` for the current
       owned counts.
    2. The alternate destination this book would have if its series had ≥2
       entries (``Author/Series/{idx} - {Album}/``). This handles the case
       where a series was previously multi-entry and got culled down to one,
       leaving the surviving file at the old series-subfoldered path.
    3. The catalog's staging path (``file``/``glob``/``disc_root``), where
       pre-reorg additions sit.

    Picking the source via the catalog means retag and reorg both work
    correctly whether or not the library has been reorganized yet, AND
    whether or not the series count has shifted since the last reorg.
    """
    dest = library_root / schema.book_dir(book, counts)
    if dest.exists() and any(dest.rglob("*")):
        return dest

    # Probe 2: the series-subfoldered alternate, if this book is in a series.
    t = book["tags"]
    series = t.get("series") or ""
    if series:
        alt = (
            library_root
            / schema.sanitize(t["author"])
            / schema.sanitize(series)
            / f"{t['series_index']} - {schema.sanitize(t['album'])}"
        )
        if alt.exists() and any(alt.rglob("*")):
            return alt

    # Probe 2.5: the standalone alternate.
    standalone_alt = library_root / schema.sanitize(t["author"]) / schema.sanitize(t["album"])
    if standalone_alt.exists() and any(standalone_alt.rglob("*")):
        return standalone_alt

    # Probe 3: the catalog-provided staging path.
    if book["layout"] == "discs":
        return library_root / book["disc_root"]
    if "file" in book:
        return (library_root / book["file"]).parent
    return library_root / Path(book["glob"]).parent


def resolve_files(
    book: dict, library_root: Path, counts: dict[str, int]
) -> list[tuple[Path, dict]]:
    """Return ``(path, per_file_overrides)`` for every file the book covers.

    ``per_file_overrides`` carries the per-file title, track, and disc that
    the diff stage needs, layered on top of the book's uniform tags.
    """
    layout, tags = book["layout"], book["tags"]
    base = _book_root(book, library_root, counts)
    if not base.exists():
        return []

    if layout == "single":
        if "file" in book:
            p = library_root / book["file"]
            if p.exists():
                return [(p, {"title": tags["title"], "track": None, "disc": None})]
            if base == p.parent:
                return []
        files = _top_audio(base)
        if not files:
            return []
        return [(files[0], {"title": tags["title"], "track": None, "disc": None})]

    if layout in ("parts", "chapters"):
        files = _top_audio(base)
        n = len(files)
        out = []
        for i, f in enumerate(files, 1):
            if layout == "chapters":
                title = chapter_title_from_filename(f.name) or tags["album"]
            else:
                title = tags["title"]
            out.append((f, {"title": title, "track": f"{i}/{n}", "disc": None}))
        return out

    if layout == "discs":
        disc_dirs = sorted(
            (d for d in base.iterdir() if d.is_dir() and re.search(r"\d", d.name)),
            key=natkey,
        )
        nd = len(disc_dirs)
        out = []
        for d_idx, ddir in enumerate(disc_dirs, 1):
            disc_no = disc_num_from_folder(ddir.name) or d_idx
            files = sorted(ddir.glob("*.mp3"), key=natkey)
            nt = len(files)
            for t_idx, f in enumerate(files, 1):
                track_no = leading_track_num(f.name) or t_idx
                out.append(
                    (
                        f,
                        {
                            "title": tags["title"],
                            "track": f"{track_no}/{nt}",
                            "disc": f"{disc_no}/{nd}",
                        },
                    )
                )
        return out

    raise ValueError(f"unknown layout: {layout}")


# ---- diffing ---------------------------------------------------------------
def open_audio(path: Path):
    """Open an audio file and return the parsed metadata object and a boolean indicating if it is MP4."""
    is_mp4 = path.suffix.lower() in (".m4b", ".m4a", ".mp4")
    if is_mp4:
        audio = MP4(path)
        if audio.tags is None:
            audio.add_tags()
        return audio, is_mp4
    try:
        audio = ID3(path)
    except ID3NoHeaderError:
        audio = ID3()
    return audio, is_mp4


def file_diff(path: Path, overrides: dict, tags: dict, layout: str = ""):
    """Compute the difference between current tags and desired tags for a file."""
    audio, is_mp4 = open_audio(path)
    read = _mp4_read if is_mp4 else _mp3_read
    narrator = tags["narrator"]
    if narrator is None:
        narrator = read(audio, "\xa9wrt" if is_mp4 else "TCOM")
    desired = desired_physical(
        tags,
        is_mp4=is_mp4,
        title=overrides["title"],
        narrator=narrator,
        track=overrides["track"],
        disc=overrides["disc"],
    )
    # For chapter sets, prefer a meaningful existing title over the derived one
    # ('00: Prologue' on Hyperion, '001 - Introduction' on Bourdain, etc.). Only
    # overwrite when the existing title is empty or a bare number.
    if layout == "chapters":
        title_key = "\xa9nam" if is_mp4 else "TIT2"
        existing = read(audio, title_key)
        if existing.strip() and not re.fullmatch(r"\s*\d+\s*", existing.strip()):
            desired.pop(title_key, None)
    changes, warnings = [], []
    for key, want in desired.items():
        cur = read(audio, key)
        if cur != want:
            changes.append((key, cur, want))
    if tags.get("description") is None:
        cmt = read(audio, "\xa9cmt" if is_mp4 else "COMM")
        if is_junk_comment(cmt):
            warnings.append(f"junk comment preserved: {cmt!r}")
    return audio, is_mp4, desired, changes, warnings


# ---- apply / restore -------------------------------------------------------
def apply_file(audio, is_mp4: bool, desired: dict, path: Path | None = None) -> None:
    """Apply desired tag changes to an audio file and save it."""
    write = _mp4_write if is_mp4 else _mp3_write
    for key, val in desired.items():
        write(audio, key, val)
    if is_mp4:
        audio.save()
    else:
        audio.save(path)


_SNAPSHOT_KEYS_MP4 = [
    "\xa9nam",
    SUBTITLE,
    "\xa9ART",
    "aART",
    "\xa9wrt",
    NARRATOR_FF,
    "\xa9alb",
    "\xa9gen",
    "\xa9day",
    SERIES,
    SERIESPART,
    "trkn",
    "disk",
    "\xa9cmt",
    "desc",
    "stik",
]
_SNAPSHOT_KEYS_MP3 = [
    "TIT2",
    "TIT3",
    "TPE1",
    "TPE2",
    "TCOM",
    "TXXX:NARRATOR",
    "TALB",
    "TCON",
    "TDRC",
    "TXXX:SERIES",
    "TXXX:SERIES-PART",
    "TRCK",
    "TPOS",
    "COMM",
]


def snapshot(path: Path) -> dict:
    """Take a snapshot of the current tags of an audio file for backup."""
    audio, is_mp4 = open_audio(path)
    read = _mp4_read if is_mp4 else _mp3_read
    keys = _SNAPSHOT_KEYS_MP4 if is_mp4 else _SNAPSHOT_KEYS_MP3
    return {k: read(audio, k) for k in keys}


def restore(backup_path: Path, library_root: Path) -> None:
    """Restore the tags of audio files from a backup snapshot."""
    data = json.loads(Path(backup_path).read_text())
    for rel, tagmap in data.items():
        path = library_root / rel
        audio, is_mp4 = open_audio(path)
        for key, val in tagmap.items():
            (_mp4_write if is_mp4 else _mp3_write)(audio, key, val)
        audio.save()
        print(f"restored {rel}")
    print(f"\nRestored {len(data)} files from {backup_path}")


# ---- reporting -------------------------------------------------------------
def fmt(v: str, width: int = 60) -> str:
    """Format a string for display in the dry-run report."""
    v = v.replace("\n", " ")
    return (v[:width] + "…") if len(v) > width else v


def default_backup_path(library_root: Path) -> Path:
    """Return the default path for the tag backup file."""
    return library_root / ".audiobooktools" / "backup.json"


def run(
    library_root: Path,
    books: list[dict],
    *,
    apply: bool = False,
    verbose: bool = False,
    backup_path: Path | None = None,
) -> int:
    """Drive the dry-run-or-apply pass over ``books`` rooted at ``library_root``.

    Returns the process exit code. ``backup_path`` defaults to
    ``<library_root>/.audiobooktools/backup.json`` when ``apply`` is set.
    """
    counts = schema.owned_counts(books)
    backup: dict[str, dict] = {}
    total_files = total_changed = total_warn = 0

    for book in books:
        try:
            files = resolve_files(book, library_root, counts)
        except FileNotFoundError as e:
            print(f"!! {book['name']}: {e}")
            continue
        if not files:
            print(f"!! {book['name']}: no files matched")
            continue

        book_changes = 0
        shown = False
        for path, overrides in files:
            if not path.exists():
                print(f"!! missing: {path}")
                continue
            total_files += 1
            audio, is_mp4, desired, changes, warnings = file_diff(
                path, overrides, book["tags"], layout=book["layout"]
            )

            if apply and changes:
                rel = str(path.relative_to(library_root))
                backup[rel] = snapshot(path)
                apply_file(audio, is_mp4, desired, path)

            if changes:
                book_changes += 1
                total_changed += 1
            for w in warnings:
                total_warn += 1
                print(f"   ⚠ {path.name}: {w}")

            if changes and (verbose or not shown):
                if not shown:
                    print(
                        f"\n■ {book['name']}  ({len(files)} file{'s' if len(files) != 1 else ''})"
                    )
                tag = f"  · {path.name}" if (verbose or len(files) > 1) else ""
                print(f"  {tag}".rstrip())
                for key, old, new in changes:
                    label = LABEL.get(key, key)
                    if new == "":
                        print(f"      {label:<12} {fmt(old)!r}  →  (removed)")
                    else:
                        print(f"      {label:<12} {fmt(old)!r}  →  {fmt(new)!r}")
                shown = True
        if book_changes and not verbose and len(files) > 1:
            print(
                f"      … {book_changes}/{len(files)} files change "
                "(per-file title/track shown above)"
            )

    print("\n" + "=" * 70)
    mode = "APPLIED" if apply else "DRY RUN"
    print(
        f"{mode}: {total_changed}/{total_files} files "
        f"{'changed' if apply else 'need changes'}; {total_warn} warning(s)"
    )

    if apply and backup:
        bpath = backup_path or default_backup_path(library_root)
        bpath.parent.mkdir(parents=True, exist_ok=True)
        bpath.write_text(json.dumps(backup, ensure_ascii=False, indent=1))
        print(f"backup of pre-change tags written to {bpath}")
    elif not apply and total_changed:
        print("re-run with --apply to write these changes")
    return 0


# ---- legacy CLI entry (canonical CLI lives in audiobooktools.cli) ----------
def main(argv: list[str] | None = None) -> int:
    """Legacy CLI entry point for the retag subcommand."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--library", required=True, type=Path, help="library root")
    ap.add_argument(
        "--catalog",
        required=True,
        type=Path,
        help="catalog file (Python module exporting BOOKS)",
    )
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true")
    g.add_argument("--restore", metavar="JSON", type=Path)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--backup", type=Path, default=None)
    args = ap.parse_args(argv)

    if args.restore:
        restore(args.restore, args.library)
        return 0

    from audiobooktools.cli import load_catalog

    books, _ = load_catalog(args.catalog)
    return run(
        args.library,
        books,
        apply=args.apply,
        verbose=args.verbose,
        backup_path=args.backup,
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
