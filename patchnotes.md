# Patch notes

## v0.1.1 — 2026-05-30

### Bug Fixes
- **File Resolution Fallback:** Fixed a critical bug in `retag.py`'s `resolve_files`. Previously, if a `single` layout explicitly requested a file via the `file` attribute and that file was missing from its staging directory, the tool would fall back to `_top_audio` and incorrectly overwrite the tags of the first unrelated audio file it found. It now correctly returns an empty list and prints a missing file warning.

## v0.1.0 — 2026-05-28

Initial release. Extracts and formalizes the toolset that previously lived
inside the author's audiobook library as a private `.retag/` directory.

### Highlights

- **Two-engine design.** `retag` writes embedded tags from the catalog;
  `reorg` derives the folder tree from the same catalog. Both are dry-run
  by default and idempotent.
- **Reversible.** Each apply pass writes a backup (`backup.json`) or
  manifest (`reorg-manifest.json`) that fully reverses the operation via
  `--restore` / `--reverse`.
- **Catalog separated from engine.** `audiobooktools/` is the engine;
  `catalog/` is the user's data. The CLI loads the catalog by file path so
  one engine install can drive many catalogs.

### Engine

- `audiobooktools.schema` — `sanitize`, `owned_counts`, `book_dir`, `single`
  convenience constructor, `GENRE` constant. Helpers now take `books` as a
  parameter instead of reading from module-level globals.
- `audiobooktools.retag` — refactored from the original `retag.py`; the
  module-level `ROOT` constant is gone; `library_root` is threaded through
  the call chain. Programmatic entry point: `retag.run(library_root, books,
  *, apply, verbose, backup_path)`.
- `audiobooktools.reorg` — same treatment. `reorg.run(library_root, books,
  *, apply, manifest_path)`.
- `audiobooktools.cli` — top-level CLI with `retag` / `reorg` subcommands,
  registered as both `audiobooktools` and `abt` console scripts via
  `pyproject.toml`. Discovery: `--catalog` defaults to the nearest
  `catalog/books.py` walking up from `$PWD`; `--library` defaults to the
  catalog's grandparent if it looks like a library, else `$PWD`.

### Catalog

- Pruned to 54 currently-owned audiobook series-entries (from the prior
  103-entry spec). DESC dictionary pruned from 74 to 30 entries to match.
- Six Pierce Brown Audible Studios m4bs onboarded as `Red Rising` series
  entries 1-6 (Tim Gerard Reynolds narration), replacing the prior
  `Red Rising (Dramatized Adaptation)` entry.
- Past entries remain available in the original `.retag/spec.py` and the
  pre-extraction git history.

### Docs

- `README.md` — public-facing pitch and three-command tour.
- `spec.md` — full data contract: BOOK dict schema, layout vocabulary,
  MP4/ID3 tag mapping, folder scheme, idempotency guarantee.
- `roadmap.md` — Phase 1 (extraction) done, Phase 2 candidates listed.
- `docs/workflows.md` — operational walkthroughs (adding from `Unfiltered/`,
  normal apply, restore, reverse).
- `docs/curation-rules.md` — high-marks principle, narrator-quality
  decisions, year = recording year.
- `CLAUDE.md` — project-local guidance for AI sessions.

### Tests

- All pure-helper tests carried over with import updates.
- `tests/test_catalog_imports.py` — smoke test that catalog imports cleanly
  and every entry is well-formed.
- The original on-disk integration test (which poked the live library) is
  replaced with a `tmp_path`-based collision-detection test.
