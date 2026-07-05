"""Scan a directory of audio files and emit draft catalog entries.

Read-only: prints Python source (``single(...)`` calls for one-file books, full
dict literals otherwise) pre-filled from each file's existing tags, ready to
paste into ``catalog/books.py``. Layout is inferred from the folder shape; a
multi-file layout is emitted as ``chapters`` with a review marker, since
parts-vs-chapters can't be told apart from disk alone.

This also serves the "catalog autocompletion" idea: point it at a single new
folder and it drafts that one entry.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from audiobooktools import reorg, retag

_DISC_DIR = re.compile(r"\bdisc\b", re.IGNORECASE)

# Logical tag -> physical key, per container. Mirrors retag's write map.
_MP4_KEYS = {
    "title": "\xa9nam",
    "subtitle": retag.SUBTITLE,
    "author": "\xa9ART",
    "narrator": "\xa9wrt",
    "album": "\xa9alb",
    "year": "\xa9day",
    "series": retag.SERIES,
    "series_index": retag.SERIESPART,
}
_MP3_KEYS = {
    "title": "TIT2",
    "subtitle": "TIT3",
    "author": "TPE1",
    "narrator": "TCOM",
    "album": "TALB",
    "year": "TDRC",
    "series": "TXXX:SERIES",
    "series_index": "TXXX:SERIES-PART",
}


def read_tags(path: Path) -> dict[str, str]:
    """Read the logical catalog tags off ``path`` (empty string when absent)."""
    audio, is_mp4 = retag.open_audio(path)
    read = retag._mp4_read if is_mp4 else retag._mp3_read
    keys = _MP4_KEYS if is_mp4 else _MP3_KEYS
    return {logical: read(audio, physical) for logical, physical in keys.items()}  # type: ignore[arg-type]


def _top_audio(folder: Path) -> list[Path]:
    return sorted(
        (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in reorg.AUDIO_EXT),
        key=retag.natkey,
    )


def _disc_subdirs(folder: Path) -> list[Path]:
    return [
        d for d in folder.iterdir() if d.is_dir() and _DISC_DIR.search(d.name) and _top_audio(d)
    ]


def infer_layout(folder: Path) -> str:
    """Guess a layout from a folder's shape.

    ``discs`` when it holds ``Disc N`` subfolders of audio; ``single`` for one
    top-level audio file; ``chapters`` for several (a stand-in the user
    downgrades to ``parts`` when the files are one work split, not one per
    chapter).
    """
    if _disc_subdirs(folder):
        return "discs"
    return "single" if len(_top_audio(folder)) <= 1 else "chapters"


def find_book_dirs(scan_root: Path) -> list[tuple[Path, str]]:
    """Walk ``scan_root`` and return ``(folder, layout)`` for each book folder.

    A folder qualifies if it directly holds audio, or holds ``Disc N`` audio
    subfolders. Disc subfolders are not descended into (they belong to their
    parent), and dot-directories are skipped.
    """
    results: list[tuple[Path, str]] = []
    for dirpath, dirnames, filenames in os.walk(scan_root):
        d = Path(dirpath)
        dirnames[:] = [sub for sub in dirnames if not sub.startswith(".")]
        disc_subs = _disc_subdirs(d)
        if disc_subs:
            results.append((d, "discs"))
            disc_names = {s.name for s in disc_subs}
            dirnames[:] = [sub for sub in dirnames if sub not in disc_names]
            continue
        if any(Path(f).suffix.lower() in reorg.AUDIO_EXT for f in filenames):
            results.append((d, infer_layout(d)))
    return results


def _q(value: str) -> str:
    """Double-quoted Python string literal matching the catalog's quoting."""
    return json.dumps(value, ensure_ascii=False)


def _tags_source(tags: dict[str, str], *, indent: str) -> list[str]:
    lines = []
    for key in (
        "title",
        "subtitle",
        "author",
        "narrator",
        "album",
        "year",
        "series",
        "series_index",
    ):
        lines.append(f'{indent}"{key}": {_q(tags.get(key, ""))},')
    lines.append(f'{indent}"genre": {_q("Audiobook")},')
    lines.append(f'{indent}"description": None,')
    return lines


def render_entry(rel_folder: str, files: list[Path], tags: dict[str, str], layout: str) -> str:
    """Render one draft catalog entry as pasteable Python source."""
    if layout == "single":
        fname = files[0].name if files else "TODO.m4b"
        body = ["single(", f"    {_q(rel_folder)},", f"    {_q(fname)},"]
        for key in (
            "title",
            "subtitle",
            "author",
            "narrator",
            "album",
            "year",
            "series",
            "series_index",
        ):
            body.append(f"    {key}={_q(tags.get(key, ''))},")
        body.append("),")
        return "\n".join(body)

    lines = ["{"]
    lines.append(f'    "name": {_q(tags.get("title", "") or rel_folder)},')
    if layout == "discs":
        lines.append('    "layout": "discs",  # TODO review')
        lines.append(f'    "disc_root": {_q(rel_folder)},')
    else:
        ext = files[0].suffix if files else ".mp3"
        lines.append('    "layout": "chapters",  # TODO review: chapters vs parts')
        lines.append(f'    "glob": {_q(f"{rel_folder}/*{ext}")},')
    lines.append('    "tags": {')
    lines.extend(_tags_source(tags, indent="        "))
    lines.append("    },")
    lines.append("},")
    return "\n".join(lines)


def discover(scan_root: Path, library_root: Path, known: set[Path] | None = None) -> int:
    """Print draft entries for every book folder under ``scan_root``. Returns 0.

    ``known`` is a set of already-catalogued absolute paths; a folder whose
    audio is entirely accounted for there is skipped.
    """
    known = known or set()
    book_dirs = find_book_dirs(scan_root)
    emitted = 0
    for folder, layout in book_dirs:
        if layout == "discs":
            files = [f for sub in _disc_subdirs(folder) for f in _top_audio(sub)]
        else:
            files = _top_audio(folder)
        if not files:
            continue
        if all(f.resolve() in known for f in files):
            continue
        try:
            rel_folder = str(folder.relative_to(library_root))
        except ValueError:
            rel_folder = str(folder)
        tags = read_tags(files[0])
        print(f"# {rel_folder}  ({layout}, {len(files)} file(s))")
        print(render_entry(rel_folder, files, tags, layout))
        print()
        emitted += 1

    if not emitted:
        print(f"discover: no new book folders found under {scan_root}")
    else:
        print(
            f"# {emitted} draft entr{'y' if emitted == 1 else 'ies'}; "
            "review, then paste into catalog/books.py"
        )
    return 0
