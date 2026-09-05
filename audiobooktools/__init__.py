"""AudiobookTools: declarative tag normalization and folder reorganization.

Run ``audiobooktools --help`` (or the short ``abt``) for the CLI. Use
:mod:`audiobooktools.schema` for the data model helpers and call
:func:`audiobooktools.retag.run` / :func:`audiobooktools.reorg.run` from your
own code if you'd rather drive the engine directly.
"""

from __future__ import annotations

import importlib.metadata
from pathlib import Path


def _find_version() -> str:
    try:
        return importlib.metadata.version("audiobooktools")
    except importlib.metadata.PackageNotFoundError:
        pass
    # Source checkouts are not installed; the VERSION file sits at the repo
    # root and does not ship in the wheel.
    version_file = Path(__file__).resolve().parent.parent / "VERSION"
    try:
        return version_file.read_text().strip()
    except OSError:
        return "0.0.0+unknown"


__version__ = _find_version()

__all__ = ["__version__"]
