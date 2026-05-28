"""Pure-helper tests for :mod:`audiobooktools.retag`.

The end-to-end idempotency check that lived next to the old script is replaced
by an integration test built on a :func:`tmp_path` fixture (see
``test_apply_idempotency``); these unit tests don't touch any real audio files.
"""

from __future__ import annotations

import pytest

from audiobooktools import retag


@pytest.mark.parametrize(
    "name,expected",
    [
        ("01 Benna Murcatto Saves a Life.mp3", "Benna Murcatto Saves a Life"),
        ("001 - Lincoln in the Bardo.mp3", "Lincoln in the Bardo"),
        ("14 Interview with Joe.mp3", "Interview with Joe"),
        ("02 I TALINS.mp3", "I TALINS"),
        ("06 Two’s Company.mp3", "Two’s Company"),
        ("No Number Here.mp3", "No Number Here"),
    ],
)
def test_chapter_title_from_filename(name, expected):
    assert retag.chapter_title_from_filename(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("01 Benna Murcatto Saves a Life.mp3", 1),
        ("009 - Lincoln in the Bardo.mp3", 9),
        ("14 Interview with Joe.mp3", 14),
        ("no number.mp3", None),
    ],
)
def test_leading_track_num(name, expected):
    assert retag.leading_track_num(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Disc 01", 1),
        ("Disc 9", 9),
        ("CD2", 2),
        ("bonus", None),
    ],
)
def test_disc_num_from_folder(name, expected):
    assert retag.disc_num_from_folder(name) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Chapter 72", True),
        ("Chapter 6", True),
        ("Read by Steven Pacey;", True),
        ("Read by Steven Pacey", True),
        ("", False),
        ("Unfolding in a graveyard over the course of a single night...", False),
        ("A man. His ex-girlfriend's cat.", False),
    ],
)
def test_is_junk_comment(value, expected):
    assert retag.is_junk_comment(value) is expected


def test_desired_physical_mp4_sets_both_author_slots_and_audiobook_type():
    d = retag.desired_physical(
        {
            "subtitle": "",
            "author": "Joe Abercrombie",
            "narrator": "Steven Pacey",
            "album": "The Devils",
            "genre": "Audiobook",
            "year": "2025",
            "series": "The Devils",
            "series_index": "1",
            "description": "x",
        },
        is_mp4=True,
        title="The Devils",
        narrator="Steven Pacey",
        track=None,
        disc=None,
    )
    assert d["\xa9ART"] == "Joe Abercrombie" and d["aART"] == "Joe Abercrombie"
    assert d["\xa9wrt"] == "Steven Pacey" and d[retag.NARRATOR_FF] == "Steven Pacey"
    assert d["stik"] == "2"
    assert d[retag.SERIES] == "The Devils" and d[retag.SERIESPART] == "1"
    assert "trkn" not in d  # single-file book gets no track


def test_desired_physical_empty_subtitle_marks_removal():
    d = retag.desired_physical(
        {
            "subtitle": "",
            "author": "A",
            "narrator": "B",
            "album": "C",
            "genre": "Audiobook",
            "year": "2021",
            "series": "",
            "series_index": "",
            "description": None,
        },
        is_mp4=False,
        title="C",
        narrator="B",
        track="1/2",
        disc=None,
    )
    assert d["TIT3"] == ""  # "" => caller removes the frame
    assert d["TXXX:SERIES"] == ""
    assert d["TRCK"] == "1/2"
    assert "COMM" not in d  # description None => preserved, not in desired
