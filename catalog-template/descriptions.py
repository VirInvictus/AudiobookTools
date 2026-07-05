"""Per-book synopsis text plus reused author / narrator constants.

Pull any string you repeat across entries (an author, a full cast, a narrator)
into a constant here, and put each book's synopsis in ``DESC`` keyed by a short
slug. Entries in ``books.py`` reference these by name. Everything here is
optional: a catalog with no descriptions is valid.
"""

from __future__ import annotations

# Reused constants: define once, reference from many entries in books.py.
EXAMPLE_AUTHOR = "Ada Author"

DESC: dict[str, str] = {
    "example_book": (
        "A one-paragraph synopsis of the audiobook, lightly rewritten for voice "
        "and length. This text is written to the description tag by `retag`."
    ),
}
