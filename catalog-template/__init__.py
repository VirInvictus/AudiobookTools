"""Template catalog package for AudiobookTools.

Copy this directory to ``catalog/`` next to your library, then replace the
example entries with your own. AudiobookTools loads a catalog by the path to
its ``books.py``; the package only needs to export ``BOOKS`` (and, by
convention, ``DESC``).
"""

from __future__ import annotations

from catalog.books import BOOKS
from catalog.descriptions import DESC

__all__ = ["BOOKS", "DESC"]
