#!/usr/bin/env python3
"""Extract one release's notes from ``patchnotes.md``.

Prints the body of a version's section: the text under a ``## vX.Y.Z — DATE``
header, up to the next ``## `` header. With no version argument the topmost
(latest) section is used. Intended to populate a GitHub Release body or a
publish step from the changelog, so the release notes and the changelog never
drift.

    python scripts/release_notes.py            # latest section body
    python scripts/release_notes.py 0.2.0      # that version's body (exit 1 if absent)
    python scripts/release_notes.py --list     # list the versions found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_HEADER = re.compile(r"^##\s+v?(?P<version>\S+)")


def parse_sections(text: str) -> list[tuple[str, str]]:
    """Return ``(version, body)`` for each ``## vX ...`` section, in file order.

    ``version`` is the token straight after the header's ``v``; ``body`` is the
    section text with surrounding blank lines stripped.
    """
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if _HEADER.match(ln)]
    sections: list[tuple[str, str]] = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        version = _HEADER.match(lines[start]).group("version")  # type: ignore[union-attr]
        body = "\n".join(lines[start + 1 : end]).strip("\n")
        sections.append((version, body.strip()))
    return sections


def extract(text: str, version: str | None = None) -> tuple[str, str]:
    """Return the ``(version, body)`` for ``version`` (or the latest section).

    Raises ``KeyError`` if a specific version is requested but not present, and
    ``LookupError`` if the changelog has no version sections at all.
    """
    sections = parse_sections(text)
    if not sections:
        raise LookupError("no '## vX.Y.Z' sections found")
    if version is None:
        return sections[0]
    wanted = version.lstrip("v")
    for ver, body in sections:
        if ver.lstrip("v") == wanted:
            return ver, body
    raise KeyError(version)


def main(argv: list[str] | None = None) -> int:
    """Entry point: print the requested release body, or list versions."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("version", nargs="?", help="version to extract (default: latest)")
    ap.add_argument(
        "--file",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "patchnotes.md",
        help="path to the changelog (default: repo patchnotes.md)",
    )
    ap.add_argument("--list", action="store_true", help="list versions and exit")
    args = ap.parse_args(argv)

    text = args.file.read_text(encoding="utf-8")
    if args.list:
        for ver, _body in parse_sections(text):
            print(ver)
        return 0

    try:
        _ver, body = extract(text, args.version)
    except KeyError:
        print(f"error: no section for version {args.version!r} in {args.file}", file=sys.stderr)
        return 1
    except LookupError as e:
        print(f"error: {e} in {args.file}", file=sys.stderr)
        return 1
    print(body)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
