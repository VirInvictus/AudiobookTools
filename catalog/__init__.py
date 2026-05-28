"""Personal catalog data for AudiobookTools.

This package is the user's own library description. It is intentionally
separate from the :mod:`audiobooktools` package so the tool stays generic and
the data can be swapped out (or kept in a private fork) without touching the
engine.

Two modules:

- :mod:`catalog.descriptions` — per-book synopsis text and reused author /
  narrator string constants.
- :mod:`catalog.books` — the ``BOOKS`` list, one dict per owned audiobook.
"""

from __future__ import annotations

from catalog.books import BOOKS
from catalog.descriptions import DESC

__all__ = ["BOOKS", "DESC"]
