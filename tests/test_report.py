"""Tests for :mod:`audiobooktools.report`.

The mechanical lints are pure functions over synthetic ``books`` lists; the two
on-disk checks (unmatched files, missing covers) use ``tmp_path`` with empty
placeholder files, so nothing here needs real audio.
"""

from __future__ import annotations

from audiobooktools import report


def _book(
    name,
    *,
    series="",
    index="",
    subtitle="",
    narrator: str | None = "Reader",
    year="2020",
    description=None,
    album=None,
    author="Author",
    file="src/x.m4b",
):
    return {
        "name": name,
        "layout": "single",
        "file": file,
        "tags": {
            "title": name,
            "subtitle": subtitle,
            "author": author,
            "narrator": narrator,
            "album": album or name,
            "genre": "Audiobook",
            "year": year,
            "series": series,
            "series_index": index,
            "description": description,
        },
    }


# ---- duration formatting ---------------------------------------------------
def test_fmt_duration_pads_minutes():
    assert report.fmt_duration(0) == "0h 00m"
    assert report.fmt_duration(3600) == "1h 00m"
    assert report.fmt_duration(3600 + 5 * 60) == "1h 05m"
    assert report.fmt_duration(60 * 725) == "12h 05m"


# ---- series-index analysis -------------------------------------------------
def test_series_gaps_flags_missing_middle_index():
    books = [
        _book("A", series="S", index="1"),
        _book("B", series="S", index="2"),
        _book("D", series="S", index="4"),
    ]
    assert report.series_gaps(books) == {"S": [3]}


def test_series_gaps_ignores_contiguous_and_endpoint_cutoff():
    # Dark-Tower-style 1-4 cutoff is contiguous, not a gap.
    books = [_book(str(i), series="DT", index=str(i)) for i in (1, 2, 3, 4)]
    assert report.series_gaps(books) == {}


def test_series_gaps_ignores_subone_novella_indices():
    books = [
        _book("novella", series="E", index="00.5"),
        _book("one", series="E", index="1"),
        _book("two", series="E", index="2"),
    ]
    assert report.series_gaps(books) == {}


def test_duplicate_indices_detected():
    books = [
        _book("A", series="S", index="1"),
        _book("B", series="S", index="1"),
        _book("C", series="T", index="2"),
    ]
    assert report.duplicate_indices(books) == {"S": ["1"]}


def test_subtitle_index_mismatch_word_and_number():
    books = [
        _book("A", series="S", index="3", subtitle="The Age of Madness, Book Two"),
        _book("B", series="S", index="2", subtitle="The Age of Madness, Book Two"),  # ok
        _book("C", series="S", index="5", subtitle="Series, Book 4"),
    ]
    out = {name for name, _sub, _claimed in report.subtitle_index_mismatches(books)}
    assert out == {"A", "C"}


def test_subtitle_decimal_index_is_not_a_mismatch():
    # 'Book 12.5' with index '12.5' must not false-positive (Dresden .5 entries).
    books = [
        _book("Side Jobs", series="D", index="12.5", subtitle="The Dresden Files, Book 12.5"),
        _book("Heroic Hearts", series="D", index="17.6", subtitle="The Dresden Files, Book 17.6"),
    ]
    assert report.subtitle_index_mismatches(books) == []


# ---- tag lints -------------------------------------------------------------
def test_unused_desc_keys():
    desc = {"used": "hello world", "orphan": "nobody uses me"}
    books = [_book("A", description="hello world")]
    assert report.unused_desc_keys(books, desc) == ["orphan"]


def test_unused_desc_keys_empty_when_no_desc():
    assert report.unused_desc_keys([_book("A")], None) == []


def test_narrator_warnings_flags_empty_and_junk_not_none():
    books = [
        _book("preserve", narrator=None),  # intentional: not flagged
        _book("empty", narrator="   "),
        _book("junk", narrator="Read by the author"),
        _book("fine", narrator="Steven Pacey"),
    ]
    names = {name for name, _msg in report.narrator_warnings(books)}
    assert names == {"empty", "junk"}


def test_year_warnings():
    books = [
        _book("ok", year="2019"),
        _book("nondigit", year="MMXIX"),
        _book("too_old", year="1954"),
        _book("future", year="2099"),
    ]
    names = {name for name, _msg in report.year_warnings(books, this_year=2026)}
    assert names == {"nondigit", "too_old", "future"}


# ---- on-disk checks --------------------------------------------------------
def test_unmatched_files(tmp_path):
    (tmp_path / "src").mkdir()
    matched = tmp_path / "src" / "x.m4b"
    stray = tmp_path / "src" / "stray.m4b"
    matched.write_bytes(b"")
    stray.write_bytes(b"")
    books = [_book("X", file="src/x.m4b", author="Author", album="X")]
    unmatched = report.unmatched_files(books, tmp_path)
    assert [p.name for p in unmatched] == ["stray.m4b"]


def test_unmatched_skips_dot_dirs(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.m4b").write_bytes(b"")
    dot = tmp_path / ".audiobooktools"
    dot.mkdir()
    (dot / "leftover.m4b").write_bytes(b"")
    books = [_book("X", file="src/x.m4b", album="X")]
    assert report.unmatched_files(books, tmp_path) == []


def test_missing_covers(tmp_path):
    with_cover = tmp_path / "src_a"
    without = tmp_path / "src_b"
    with_cover.mkdir()
    without.mkdir()
    (with_cover / "a.m4b").write_bytes(b"")
    (with_cover / "cover.jpg").write_bytes(b"")
    (without / "b.m4b").write_bytes(b"")
    books = [
        _book("A", file="src_a/a.m4b", album="A"),
        _book("B", file="src_b/b.m4b", album="B"),
    ]
    assert report.missing_covers(books, tmp_path) == ["B"]
