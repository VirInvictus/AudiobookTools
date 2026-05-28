"""Data model for AudiobookTools.

The catalog is a list of ``BOOK`` dicts, each describing exactly one owned
audiobook (or one volume of a series) and the tag values it should end up
with. ``retag`` reads this and writes those tags onto the underlying audio
files; ``reorg`` reads this and moves the files into the matching folder
tree. Both derive every target from the same dict, so the embedded metadata
and the on-disk layout can't drift.

BOOK dict shape
---------------

::

    {
        "name":   str,          # human-readable label for log output
        "layout": "single" | "parts" | "chapters" | "discs",
        # exactly one of these, per layout:
        "file":      str,       # relative path; layout=single (or any layout
                                # that wants an explicit single source file)
        "glob":      str,       # relative glob, sorted; layout=parts/chapters
        "disc_root": str,       # folder holding "Disc *" subfolders; layout=discs
        "tags": {
            "title":        str,
            "subtitle":     str,   # "" to remove
            "author":       str,
            "narrator":     str | None,  # None preserves the file's existing credit
            "album":        str,
            "genre":        str,   # GENRE constant; "Audiobook" by convention
            "year":         str,   # recording / audio-edition year, not pub year
            "series":       str,   # "" for standalones
            "series_index": str,   # "" for standalones; e.g. "1", "00.5"
            "description":  str | None,  # None preserves existing comment
        },
    }

Layout vocabulary
-----------------

``single``
    One audio file (typically ``.m4b``) holding the whole work. ``file``
    points at it.

``parts``
    Several files = ONE work split across files; uniform title/album,
    files numbered as track ``i/total``. Examples: World War Z complete,
    Red Rising dramatization.

``chapters``
    Several files = ONE work, one chapter per file. Per-file title is
    derived from the filename; files numbered as track ``i/total``.

``discs``
    Several files inside ``Disc NN`` subfolders. Uniform title; disc and
    track are recomputed from the folder/filename layout.

description = None
    Preserve the file's existing description tag. ``retag`` flags a junk
    description rather than silently keeping it.
"""

from __future__ import annotations

import re
from pathlib import Path

GENRE = "Audiobook"
"""Default value for the genre tag across every entry in the catalog."""

_ILLEGAL = re.compile(r'[\\/:*?"<>|]')


def sanitize(name: str) -> str:
    """Make ``name`` safe to use as an NTFS folder or file name.

    Colons followed by a space (``": "``) are rewritten as ``" - "``; other
    illegal NTFS characters (``\\ / : * ? " < > |``) are stripped. Whitespace
    is collapsed and any trailing dot/space is dropped.
    """
    name = name.replace(": ", " - ")
    name = _ILLEGAL.sub("", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.rstrip(". ")


def owned_counts(books: list[dict]) -> dict[str, int]:
    """Return ``{series_name: count}`` for every series that appears in
    ``books``. Used by :func:`book_dir` to decide whether to give a series its
    own subfolder.

    A series with one owned entry stays at ``Author/Title``; two or more
    promotes the series to ``Author/Series/## - Title``.
    """
    counts: dict[str, int] = {}
    for b in books:
        s = b["tags"].get("series")
        if s:
            counts[s] = counts.get(s, 0) + 1
    return counts


def book_dir(book: dict, counts: dict[str, int]) -> Path:
    """Target folder for ``book`` under the library root.

    Returns either ``Author/Series/## - Title`` (when the series has 2+
    entries in ``counts``) or ``Author/Title`` (standalone, or lone series
    entry). All path components are :func:`sanitize`-d.
    """
    t = book["tags"]
    author = sanitize(t["author"])
    series = t.get("series") or ""
    label = sanitize(t["album"])
    if series and counts.get(series, 0) >= 2:
        return Path(author) / sanitize(series) / f"{t['series_index']} - {label}"
    return Path(author) / label


def single(folder: str, fname: str, **tags) -> dict:
    """Convenience constructor for a ``layout=single`` BOOK entry.

    Sets sensible defaults for ``genre`` (:data:`GENRE`) and ``description``
    (``None`` = preserve). Equivalent to writing the full dict by hand;
    catalog files use it to keep one-file books compact.
    """
    tags.setdefault("genre", GENRE)
    tags.setdefault("description", None)
    return {
        "name": tags["title"],
        "layout": "single",
        "file": f"{folder}/{fname}",
        "tags": tags,
    }
