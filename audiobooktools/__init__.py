"""AudiobookTools: declarative tag normalization and folder reorganization.

Run ``audiobooktools --help`` (or the short ``abt``) for the CLI. Use
:mod:`audiobooktools.schema` for the data model helpers and call
:func:`audiobooktools.retag.run` / :func:`audiobooktools.reorg.run` from your
own code if you'd rather drive the engine directly.
"""

from __future__ import annotations

from pathlib import Path

_VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"
try:
    __version__ = _VERSION_FILE.read_text().strip()
except OSError:
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
