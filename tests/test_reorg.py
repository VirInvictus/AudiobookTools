"""Tests for :mod:`audiobooktools.reorg`: name sanitizing, target-path
derivation, and collision detection on a synthetic catalog.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from audiobooktools import reorg, schema


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("World War Z: The Complete Edition", "World War Z - The Complete Edition"),
        ("The Sandman: Act I", "The Sandman - Act I"),
        ('a*b?c"d<e>f|g/h\\i', "abcdefghi"),
        ("trailing dot.", "trailing dot"),
        ("  spaced   out  ", "spaced out"),
        ("Carl's Doomsday Scenario", "Carl's Doomsday Scenario"),
        ("J. R. R. Tolkien", "J. R. R. Tolkien"),
    ],
)
def test_sanitize(raw, expected):
    assert schema.sanitize(raw) == expected


def _book(album, author, series="", index="", layout="single"):
    return {
        "name": album,
        "layout": layout,
        "file": f"src/{album}.m4b",
        "tags": {
            "album": album,
            "author": author,
            "series": series,
            "series_index": index,
        },
    }


def test_book_dir_series_member_gets_numbered_subfolder():
    counts = {"The First Law": 7}
    b = _book("The Blade Itself", "Joe Abercrombie", "The First Law", "1")
    assert schema.book_dir(b, counts) == Path("Joe Abercrombie/The First Law/1 - The Blade Itself")


def test_book_dir_standalone_has_no_series_folder():
    b = _book("Project Hail Mary", "Andy Weir")
    assert schema.book_dir(b, {}) == Path("Andy Weir/Project Hail Mary")


def test_book_dir_lone_series_entry_is_flat():
    counts = {"The Devils": 1}  # only one owned => no series subfolder
    b = _book("The Devils", "Joe Abercrombie", "The Devils", "1")
    assert schema.book_dir(b, counts) == Path("Joe Abercrombie/The Devils")


def test_book_dir_colon_album_sanitized():
    counts = {"The Sandman": 3}
    b = _book("The Sandman: Act II", "Neil Gaiman", "The Sandman", "2")
    assert schema.book_dir(b, counts) == Path("Neil Gaiman/The Sandman/2 - The Sandman - Act II")


def test_owned_counts_groups_by_series():
    books = [
        _book("A", "Author X", "S", "1"),
        _book("B", "Author X", "S", "2"),
        _book("C", "Author Y"),
        _book("D", "Author Z", "T", "1"),
    ]
    counts = schema.owned_counts(books)
    assert counts == {"S": 2, "T": 1}


def test_check_reports_destination_collision(tmp_path):
    """Two source files mapping to the same destination must be flagged."""
    src1 = tmp_path / "a.m4b"
    src2 = tmp_path / "b.m4b"
    dst = tmp_path / "out" / "same.m4b"
    src1.write_bytes(b"x")
    src2.write_bytes(b"x")
    problems = reorg._check([(src1, dst), (src2, dst)])
    assert any("two sources map to" in p for p in problems)


def test_check_passes_for_distinct_targets(tmp_path):
    src1 = tmp_path / "a.m4b"
    src2 = tmp_path / "b.m4b"
    dst1 = tmp_path / "out" / "a.m4b"
    dst2 = tmp_path / "out" / "b.m4b"
    src1.write_bytes(b"x")
    src2.write_bytes(b"y")
    assert reorg._check([(src1, dst1), (src2, dst2)]) == []


def test_diff_summary_collapses_by_destination_dir(tmp_path, capsys):
    """--diff collapses to one line per destination folder with a count, rather
    than listing every file."""
    moves = [
        (tmp_path / "a.m4b", tmp_path / "Author" / "Series" / "1 - A" / "A.m4b"),
        (tmp_path / "b.m4b", tmp_path / "Author" / "Series" / "1 - A" / "cover.jpg"),
        (tmp_path / "c.m4b", tmp_path / "Author" / "Series" / "2 - B" / "B.m4b"),
    ]
    reorg.print_diff_summary(moves, tmp_path)
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 2  # two destination dirs, not three files
    assert any("1 - A" in ln and ln.strip().startswith("2") for ln in lines)
    assert any("2 - B" in ln and ln.strip().startswith("1") for ln in lines)
