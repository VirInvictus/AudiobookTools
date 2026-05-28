# CLAUDE.md (AudiobookTools)

Project-local guidance for AI sessions working in this repo. Read alongside
the global `~/.claude/CLAUDE.md`.

## What this project is

A declarative tag-and-folder normalizer for an audiobook library. One source
of truth (`catalog/books.py`) drives both the embedded metadata and the
on-disk folder tree.

Engine and catalog are intentionally separate. The engine
(`audiobooktools/`) is generic; the catalog (`catalog/`) is the user's data.
Don't mix them.

## Conventions

- **Stack.** Python 3.10+. Only runtime dependency is `mutagen`. Dev:
  `ruff` for lint+format, `pytest` for tests.
- **Run via `uv`.** Either install with `uv pip install -e .` or invoke
  ad-hoc via `uv run --with mutagen --with pytest pytest -q` etc.
- **Dry-run is the default mode** for both `retag` and `reorg`. Anything
  that writes to the library is gated behind `--apply` (or `--restore` /
  `--reverse`).
- **Never destructive.** `reorg` moves and renames; it never deletes audio.
  When the user culls a book from the shelf, that's an explicit `rm`, not a
  tool operation.
- **Reversible.** Every `--apply` writes a backup or manifest that fully
  reverses it. If you add a new mutating operation, add the inverse and
  test it.
- **Idempotent.** A second dry-run after `--apply` reports zero changes.
  Tests enforce this.

## Code style

Project follows the global Python conventions in `~/.claude/rules/python.md`:

- Type hints, `from __future__ import annotations` at the top.
- Ruff for format+lint (line length 100, selected rule set in
  `pyproject.toml`).
- Stay terse with comments. Reserve them for hidden invariants, NTFS-safety
  workarounds, or "this behavior surprises a reader" cases.
- Prefer editing existing modules to adding new ones. The package is small
  and meant to stay that way.

## Adding a new book to the catalog

1. Drop the source files under `Unfiltered/<work-group>/` in the library.
2. Read the existing tags to confirm narrator / year / series metadata:
   `uv run --with mutagen python -c "from mutagen import File; ..."`
3. Add the entry to `catalog/books.py`, near similar entries, using
   `single(folder, fname, ...)` for one-file books or a full dict literal
   for multi-file layouts. Reuse `ABERCROMBIE` / `PACEY` / `LINCOLN_CAST`
   constants and `DESC[key]` references where they fit.
4. If the book introduces a new synopsis, add a `DESC` entry in
   `catalog/descriptions.py` first.
5. Run `audiobooktools retag` (dry) — confirm the diff is sane.
6. Run `audiobooktools reorg` (dry) — confirm the destination path is what
   you expect.
7. Apply: `retag --apply`, then `reorg --apply`.

See `docs/workflows.md` for the long-form walkthrough.

## When the engine and the spec drift

The shipped catalog is the canonical test of the engine on real data. If
you change the schema (`audiobooktools/schema.py`) in a way that touches
required keys or layout semantics, run `pytest` and a dry-run pass against
the live library before declaring done.

## What the curation rules in `docs/curation-rules.md` mean for code

The rules are editorial (which books the *user* owns and tags), not
mechanical. Don't enforce "year = recording year" in the engine; do
document it. The catalog is the place where the rule lives.

## Patterns to avoid

- Adding a feature that bypasses dry-run as the default mode.
- Adding a feature that deletes audio.
- Coupling the engine to a single catalog (e.g. hard-coding paths to the
  shipped library).
- Re-introducing the module-level `ROOT` constant. `library_root` is a
  parameter, threaded explicitly, on purpose: it makes the tool testable
  with `tmp_path` and reusable across libraries.
- Adding third-party dependencies without checking with the user.

## Memory pointers

The author's library-specific memory (curation rules, narrator-quality
notes, tagging conventions) lives at
`~/.claude/projects/-mnt-SharedData-Audiobooks/memory/`. Those memories are
about the *library*, not the *tool*; consult them when working on the
catalog, not the engine.
