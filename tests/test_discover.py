"""Tests for :mod:`audiobooktools.discover`: layout inference, book-folder
discovery, and the pure source-rendering. Tag reading (which needs real audio)
is exercised end-to-end elsewhere; here files are empty placeholders.
"""

from __future__ import annotations

from pathlib import Path

from audiobooktools import discover


def _touch(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"")
    return p


# ---- layout inference ------------------------------------------------------
def test_infer_layout_single(tmp_path):
    _touch(tmp_path / "book.m4b")
    assert discover.infer_layout(tmp_path) == "single"


def test_infer_layout_chapters(tmp_path):
    for i in range(3):
        _touch(tmp_path / f"{i:02d} chapter.mp3")
    assert discover.infer_layout(tmp_path) == "chapters"


def test_infer_layout_discs(tmp_path):
    _touch(tmp_path / "Disc 01" / "01.mp3")
    _touch(tmp_path / "Disc 02" / "01.mp3")
    assert discover.infer_layout(tmp_path) == "discs"


# ---- book-folder discovery -------------------------------------------------
def test_find_book_dirs_mixed_tree(tmp_path):
    _touch(tmp_path / "Solo" / "solo.m4b")
    _touch(tmp_path / "Chaptered" / "01 a.mp3")
    _touch(tmp_path / "Chaptered" / "02 b.mp3")
    _touch(tmp_path / "Disced" / "Disc 01" / "01.mp3")
    _touch(tmp_path / "Disced" / "Disc 02" / "01.mp3")

    found = {p.name: layout for p, layout in discover.find_book_dirs(tmp_path)}
    assert found == {"Solo": "single", "Chaptered": "chapters", "Disced": "discs"}


def test_find_book_dirs_does_not_descend_into_disc_folders(tmp_path):
    _touch(tmp_path / "Book" / "Disc 01" / "01.mp3")
    found = discover.find_book_dirs(tmp_path)
    # Only the parent "Book" folder is reported, never the Disc subfolder.
    assert [p.name for p, _ in found] == ["Book"]


def test_find_book_dirs_skips_dot_dirs(tmp_path):
    _touch(tmp_path / ".audiobooktools" / "junk.m4b")
    _touch(tmp_path / "Real" / "r.m4b")
    assert [p.name for p, _ in discover.find_book_dirs(tmp_path)] == ["Real"]


# ---- rendering -------------------------------------------------------------
def _tags(**over):
    base = {
        "title": "Title",
        "subtitle": "Sub",
        "author": "Author",
        "narrator": "Reader",
        "album": "Album",
        "year": "2020",
        "series": "",
        "series_index": "",
    }
    base.update(over)
    return base


def test_render_single_uses_single_constructor():
    out = discover.render_entry("Group", [Path("Group/x.m4b")], _tags(), "single")
    assert out.startswith("single(")
    assert '"Group",' in out
    assert '"x.m4b",' in out
    assert 'title="Title",' in out
    assert out.rstrip().endswith("),")
    # genre/description are single()'s defaults, not spelled out here.
    assert "genre" not in out


def test_render_chapters_is_full_dict_with_review_marker():
    files = [Path("Group/01.mp3"), Path("Group/02.mp3")]
    out = discover.render_entry("Group", files, _tags(), "chapters")
    assert '"layout": "chapters",  # TODO review' in out
    assert '"glob": "Group/*.mp3",' in out
    assert '"genre": "Audiobook",' in out
    assert '"description": None,' in out


def test_render_discs_emits_disc_root():
    out = discover.render_entry("Group", [Path("Group/Disc 01/01.mp3")], _tags(), "discs")
    assert '"layout": "discs",' in out
    assert '"disc_root": "Group",' in out


def test_q_quotes_with_double_quotes_and_escapes():
    assert discover._q('He said "hi"') == '"He said \\"hi\\""'


def test_discover_skips_known_paths(tmp_path, capsys):
    f = _touch(tmp_path / "Book" / "b.m4b")
    rc = discover.discover(tmp_path, tmp_path, known={f.resolve()})
    assert rc == 0
    assert "no new book folders" in capsys.readouterr().out
