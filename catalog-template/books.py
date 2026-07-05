"""The owned-audiobooks catalog: one entry per audiobook (or per volume).

The dict shape is documented in :mod:`audiobooktools.schema` and in
``spec.md``. ``single(...)`` is the convenience constructor for one-file books;
multi-file layouts (``parts`` / ``chapters`` / ``discs``) are written as full
dicts. Tip: run ``abt discover --path <folder>`` to draft an entry from a
file's existing tags instead of writing it by hand.
"""

from __future__ import annotations

from audiobooktools.schema import single
from catalog.descriptions import DESC, EXAMPLE_AUTHOR

BOOKS: list[dict] = [
    # A one-file (.m4b) standalone. `single()` fills genre + description
    # defaults; the first two args are the source folder and filename,
    # relative to the library root.
    single(
        "Ada Author - Example Book",
        "Example Book.m4b",
        title="Example Book",
        subtitle="",
        author=EXAMPLE_AUTHOR,
        narrator="Reader Name",
        album="Example Book",
        year="2024",  # audio edition year, not original publication year
        series="",
        series_index="",
        description=DESC["example_book"],
    ),
    # A multi-file work (one chapter per file). Full-dict form:
    # {
    #     "name": "Another Book",
    #     "layout": "chapters",
    #     "glob": "Ada Author - Another Book/*.mp3",
    #     "tags": {
    #         "title": "Another Book",
    #         "subtitle": "",
    #         "author": EXAMPLE_AUTHOR,
    #         "narrator": "Reader Name",
    #         "album": "Another Book",
    #         "genre": "Audiobook",
    #         "year": "2024",
    #         "series": "",
    #         "series_index": "",
    #         "description": None,
    #     },
    # },
]
