"""Read-only reporting over a catalog + library: ``status`` and ``validate``.

Neither command writes to the library. ``status`` summarizes what the catalog
covers (book/file counts, total duration, files on disk that no entry claims,
possible series-index gaps). ``validate`` lints the catalog for drift before an
apply (missing covers, unused ``DESC`` keys, duplicate/mismatched series
indices, suspicious narrator strings, implausible ``year`` values).

The mechanical checks are pure functions over the ``books`` list (and the
library root for the on-disk ones), so they unit-test without real audio; the
``*_report`` drivers wrap them with formatting.
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

import mutagen

from audiobooktools import reorg, retag, schema

# Audio editions predate ~1980 only rarely; anything older usually means a
# publication year slipped in where the recording year belongs (curation rule).
_OLDEST_PLAUSIBLE_YEAR = 1980

_ORDINALS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

_READ_BY = re.compile(r"\bread by\b", re.IGNORECASE)
# Capture a decimal index ("Book 12.5") whole, or a word ordinal ("Book Two").
_BOOK_ORDINAL = re.compile(r"\bBook\s+(\d+(?:\.\d+)?|[A-Za-z]+)\b", re.IGNORECASE)


# ---- audio duration --------------------------------------------------------
def audio_length(path: Path) -> float | None:
    """Return the duration of ``path`` in seconds, or ``None`` if unreadable."""
    try:
        f = mutagen.File(str(path))  # type: ignore[attr-defined]  # public API, pyright miss
    except Exception:
        return None
    info = getattr(f, "info", None)
    return getattr(info, "length", None) if info is not None else None


def fmt_duration(seconds: float) -> str:
    """Render a second count as ``"12h 05m"`` (minutes zero-padded)."""
    total_min = int(round(seconds / 60))
    h, m = divmod(total_min, 60)
    return f"{h}h {m:02d}m"


# ---- file coverage ---------------------------------------------------------
def resolved_paths(books: list[dict], library_root: Path) -> list[Path]:
    """Every on-disk audio file the catalog resolves to (skips unresolvable
    entries rather than raising, so status still reports on a partial library)."""
    counts = schema.owned_counts(books)
    out: list[Path] = []
    for b in books:
        try:
            out.extend(p for p, _ in retag.resolve_files(b, library_root, counts))
        except (FileNotFoundError, ValueError, OSError):
            continue
    return out


def books_without_files(books: list[dict], library_root: Path) -> list[str]:
    """Names of catalog entries that resolve to no files on disk (in the catalog
    but not present in this library yet)."""
    counts = schema.owned_counts(books)
    out: list[str] = []
    for b in books:
        try:
            files = retag.resolve_files(b, library_root, counts)
        except (FileNotFoundError, ValueError, OSError):
            files = []
        if not files:
            out.append(b["name"])
    return out


def scan_audio(root: Path) -> list[Path]:
    """All audio files under ``root``, skipping dot-directories (``.audiobooktools``)."""
    if not root.exists():
        return []
    out = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in reorg.AUDIO_EXT:
            continue
        if any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        out.append(p)
    return sorted(out)


def unmatched_files(books: list[dict], library_root: Path) -> list[Path]:
    """Audio files present on disk that no catalog entry claims."""
    claimed = {p.resolve() for p in resolved_paths(books, library_root)}
    return [p for p in scan_audio(library_root) if p.resolve() not in claimed]


# ---- series-index analysis -------------------------------------------------
def _index_num(idx: object) -> float | None:
    """Parse a ``series_index`` string to a float, or ``None`` if not numeric."""
    try:
        return float(idx)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _indices_by_series(books: list[dict]) -> dict[str, list[str]]:
    by_series: dict[str, list[str]] = {}
    for b in books:
        s = b["tags"].get("series")
        if s:
            by_series.setdefault(s, []).append(b["tags"].get("series_index", ""))
    return by_series


def series_gaps(books: list[dict]) -> dict[str, list[int]]:
    """Series whose owned integer indices have an internal gap.

    Only whole-number indices ``>= 1`` are considered, so sub-1 novella indices
    (``00.5``) don't register as gaps and a deliberate cutoff at the *end* of a
    run (Dark Tower 1-4) is contiguous, not a gap. A missing middle index
    (owning 1, 2, 4) is the signal.
    """
    gaps: dict[str, list[int]] = {}
    for s, idxs in _indices_by_series(books).items():
        ints = sorted({int(n) for i in idxs if (n := _index_num(i)) is not None and n >= 1})
        if len(ints) < 2:
            continue
        missing = [i for i in range(ints[0], ints[-1] + 1) if i not in ints]
        if missing:
            gaps[s] = missing
    return gaps


def duplicate_indices(books: list[dict]) -> dict[str, list[str]]:
    """Series that assign the same ``series_index`` to more than one entry."""
    dups: dict[str, list[str]] = {}
    for s, idxs in _indices_by_series(books).items():
        seen: set[str] = set()
        repeated: set[str] = set()
        for i in idxs:
            if i in seen:
                repeated.add(i)
            seen.add(i)
        if repeated:
            dups[s] = sorted(repeated)
    return dups


def subtitle_index_mismatches(books: list[dict]) -> list[tuple[str, str, str]]:
    """Entries whose subtitle claims 'Book N' but whose ``series_index`` differs.

    Returns ``(name, subtitle, claimed)`` tuples, ``claimed`` being the token as
    written in the subtitle. Decimal indices ('Book 12.5' with index '12.5') are
    compared numerically, so they don't false-positive. Catches the common
    copy-paste slip where the subtitle wasn't updated alongside the index.
    """
    out: list[tuple[str, str, str]] = []
    for b in books:
        sub = b["tags"].get("subtitle") or ""
        m = _BOOK_ORDINAL.search(sub)
        if not m:
            continue
        token = m.group(1)
        if token.lower() in _ORDINALS:
            claimed: float | None = float(_ORDINALS[token.lower()])
        else:
            claimed = _index_num(token)
        if claimed is None:
            continue
        actual = _index_num(b["tags"].get("series_index", ""))
        if actual is not None and claimed != actual:
            out.append((b["name"], sub, token))
    return out


# ---- tag-value lints -------------------------------------------------------
def unused_desc_keys(books: list[dict], desc: dict[str, str] | None) -> list[str]:
    """``DESC`` keys whose synopsis is not attached to any owned book.

    The catalog resolves ``DESC[key]`` to its value at import time, so by the
    time ``books`` is loaded the key is gone; a synopsis is "used" when its text
    equals some entry's ``description`` tag.
    """
    if not desc:
        return []
    used = {b["tags"].get("description") for b in books}
    return sorted(k for k, v in desc.items() if v not in used)


def narrator_warnings(books: list[dict]) -> list[tuple[str, str]]:
    """Entries with an empty or junk-looking narrator credit.

    ``narrator is None`` means "preserve the file's existing credit" and is
    intentional, so it is not flagged.
    """
    out: list[tuple[str, str]] = []
    for b in books:
        n = b["tags"].get("narrator")
        if n is None:
            continue
        if not n.strip():
            out.append((b["name"], "empty narrator (use None to preserve, or name the reader)"))
        elif retag.is_junk_comment(n) or _READ_BY.search(n):
            out.append((b["name"], f"suspicious narrator string: {n!r}"))
    return out


def year_warnings(books: list[dict], this_year: int) -> list[tuple[str, str]]:
    """Entries whose ``year`` isn't a plausible 4-digit audio-edition year."""
    out: list[tuple[str, str]] = []
    ceiling = this_year + 1
    for b in books:
        y = b["tags"].get("year", "") or ""
        if not re.fullmatch(r"\d{4}", y):
            out.append((b["name"], f"year is not a 4-digit value: {y!r}"))
            continue
        yi = int(y)
        if yi < _OLDEST_PLAUSIBLE_YEAR or yi > ceiling:
            out.append(
                (
                    b["name"],
                    f"year {yi} is outside the plausible audio-edition range "
                    f"({_OLDEST_PLAUSIBLE_YEAR}–{ceiling}); is it a publication year?",
                )
            )
    return out


def missing_covers(books: list[dict], library_root: Path) -> list[str]:
    """Owned books whose on-disk folder has no cover image.

    Uses the same source-root probe as retag/reorg, so it checks wherever the
    book actually lives (canonical tree or staging). Entries whose files aren't
    on disk yet are skipped: that's a status concern, not a cover concern.
    """
    counts = schema.owned_counts(books)
    out: list[str] = []
    for b in books:
        root = retag._book_root(b, library_root, counts)
        if not root.exists():
            continue
        has_cover = any(
            p.is_file() and p.suffix.lower() in reorg.IMAGE_EXT for p in root.rglob("*")
        )
        if not has_cover:
            out.append(b["name"])
    return out


# ---- drivers ---------------------------------------------------------------
def status_report(library_root: Path, books: list[dict]) -> int:
    """Print a one-screen summary of the catalog against the library. Returns 0."""
    resolved = resolved_paths(books, library_root)
    total_seconds = 0.0
    unreadable = 0
    for p in resolved:
        length = audio_length(p)
        if length is None:
            unreadable += 1
        else:
            total_seconds += length

    unmatched = unmatched_files(books, library_root)
    absent = books_without_files(books, library_root)
    gaps = series_gaps(books)

    print(f"library: {library_root}")
    present = len(books) - len(absent)
    print(f"catalog: {len(books)} books ({present} on disk) · {len(resolved)} files")
    dur = fmt_duration(total_seconds) if total_seconds else "unknown"
    tail = f" ({unreadable} file(s) unreadable)" if unreadable else ""
    print(f"runtime: {dur}{tail}")

    if absent:
        print(f"\nnot on disk: {len(absent)} catalog entr{'y' if len(absent) == 1 else 'ies'}")
        for name in absent[:20]:
            print(f"  · {name}")
        if len(absent) > 20:
            print(f"  … and {len(absent) - 20} more")

    if unmatched:
        print(f"\nunmatched on disk: {len(unmatched)} audio file(s) no entry claims")
        for p in unmatched[:20]:
            print(f"  · {p.relative_to(library_root)}")
        if len(unmatched) > 20:
            print(f"  … and {len(unmatched) - 20} more")
    else:
        print("\nunmatched on disk: none")

    if gaps:
        print("\npossible series gaps (informational):")
        for s in sorted(gaps):
            missing = ", ".join(str(i) for i in gaps[s])
            print(f"  · {s}: missing index {missing}")
    return 0


def validate_report(library_root: Path, books: list[dict], desc: dict[str, str] | None) -> int:
    """Lint the catalog; print findings. Returns 1 if any were found, else 0.

    A non-zero exit on findings makes ``validate`` usable as a CI gate; a clean
    catalog exits 0.
    """
    this_year = datetime.date.today().year
    findings: list[str] = []

    for name in missing_covers(books, library_root):
        findings.append(f"no cover image in folder: {name}")
    for key in unused_desc_keys(books, desc):
        findings.append(f"unused DESC key: {key!r}")
    for s, idxs in duplicate_indices(books).items():
        findings.append(f"duplicate series_index in {s!r}: {', '.join(idxs)}")
    for name, sub, claimed in subtitle_index_mismatches(books):
        findings.append(f"subtitle says {sub!r} but series_index isn't {claimed} [{name}]")
    for name, msg in narrator_warnings(books):
        findings.append(f"{msg} [{name}]")
    for name, msg in year_warnings(books, this_year):
        findings.append(f"{msg} [{name}]")

    if not findings:
        print(f"validate: {len(books)} books, no issues found.")
        return 0

    print(f"validate: {len(findings)} issue(s) across {len(books)} books\n")
    for f in findings:
        print(f"  ⚠ {f}")
    return 1
