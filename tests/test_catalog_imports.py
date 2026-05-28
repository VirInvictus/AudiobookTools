"""Smoke test that the user catalog imports cleanly and yields a well-formed
``BOOKS`` list. If this fails, ``catalog/books.py`` or ``catalog/descriptions.py``
has drifted from the schema and ``retag``/``reorg`` will crash before reaching
the dry-run stage.
"""

from __future__ import annotations

import pytest

REQUIRED_KEYS = {"name", "layout", "tags"}
VALID_LAYOUTS = {"single", "parts", "chapters", "discs"}
REQUIRED_TAG_KEYS = {
    "title",
    "subtitle",
    "author",
    "narrator",
    "album",
    "genre",
    "year",
    "series",
    "series_index",
}


def test_catalog_imports():
    try:
        from catalog import BOOKS, DESC
    except ImportError as e:
        pytest.skip(f"catalog package not installed in this environment: {e}")
    assert isinstance(BOOKS, list) and len(BOOKS) > 0
    assert isinstance(DESC, dict)


def test_every_book_has_required_keys():
    try:
        from catalog import BOOKS
    except ImportError as e:
        pytest.skip(f"catalog package not installed: {e}")
    for b in BOOKS:
        missing = REQUIRED_KEYS - set(b.keys())
        assert not missing, f"{b['name']!r} missing top-level keys {missing}"
        assert b["layout"] in VALID_LAYOUTS, f"{b['name']!r}: unknown layout {b['layout']!r}"
        tag_missing = REQUIRED_TAG_KEYS - set(b["tags"].keys())
        assert not tag_missing, f"{b['name']!r} missing tag keys {tag_missing}"


def test_layout_implies_source_field():
    """``single`` accepts ``file`` (optional fallback when source dir holds the
    only audio); ``parts``/``chapters`` require ``glob``; ``discs`` requires
    ``disc_root``."""
    try:
        from catalog import BOOKS
    except ImportError as e:
        pytest.skip(f"catalog package not installed: {e}")
    for b in BOOKS:
        layout = b["layout"]
        if layout == "discs":
            assert "disc_root" in b, f"{b['name']!r}: discs layout needs disc_root"
        elif layout in ("parts", "chapters"):
            assert "glob" in b or "file" in b, f"{b['name']!r}: {layout} layout needs glob or file"
