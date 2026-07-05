"""Tests for ``scripts/release_notes.py`` (changelog extraction).

The script lives outside the package, so it is loaded by file path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parent.parent / "scripts" / "release_notes.py"
_spec = importlib.util.spec_from_file_location("release_notes", _PATH)
assert _spec and _spec.loader
release_notes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release_notes)


_SAMPLE = """# Patch notes

## v0.2.0 — 2026-07-05

Latest body line one.
Latest body line two.

## v0.1.0 — 2026-05-28

First release body.
"""


def test_parse_sections_order_and_versions():
    secs = release_notes.parse_sections(_SAMPLE)
    assert [v for v, _ in secs] == ["0.2.0", "0.1.0"]


def test_extract_latest_is_topmost():
    ver, body = release_notes.extract(_SAMPLE)
    assert ver == "0.2.0"
    assert body.startswith("Latest body line one.")
    assert "First release" not in body  # stops at the next header


def test_extract_specific_version_tolerates_v_prefix():
    ver, body = release_notes.extract(_SAMPLE, "v0.1.0")
    assert ver == "0.1.0"
    assert "First release body." in body


def test_extract_missing_version_raises_keyerror():
    with pytest.raises(KeyError):
        release_notes.extract(_SAMPLE, "9.9.9")


def test_extract_empty_changelog_raises_lookuperror():
    with pytest.raises(LookupError):
        release_notes.extract("# Patch notes\n\nno versions here\n")
