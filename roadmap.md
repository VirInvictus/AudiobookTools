# Roadmap

## Phase 1 — extraction (v0.1.0, current)

- [x] Repo bootstrap: README, spec, roadmap, patchnotes, CLAUDE, LICENSE,
      VERSION, logo, pyproject.
- [x] Split the original `spec.py` into `audiobooktools/schema.py` (helpers)
      and `catalog/books.py` + `catalog/descriptions.py` (user data).
- [x] Adapt `retag.py` and `reorg.py` to take `library_root` as a parameter
      instead of deriving it from the script location.
- [x] Top-level CLI (`audiobooktools` / `abt`) with `retag` and `reorg`
      subcommands, plus discovery rules for `--library` and `--catalog`.
- [x] Tests carried over with import updates; catalog smoke test added.
- [x] Catalog pruned to currently-owned entries; six Pierce Brown Audible
      Studios m4bs onboarded from `Unfiltered/Red Rising Series Audible/`.
- [x] Live library verified: `retag --apply` and `reorg --apply` both clean.

## Maintenance (workspace sweep, 2026-06-09)

- [ ] Restore the test environment: all three test modules import pytest,
      but pytest is not installed in `.venv`, so the suite cannot run at
      all. `uv add --dev pytest`, and pin it in `pyproject.toml`'s dev
      group so this cannot silently regress.
- [ ] Commit or revert the uncommitted changes to `catalog/books.py` and
      `catalog/descriptions.py` (working tree dirty since ~1 Jun).

## Phase 2 — quality of life (planned)

- [ ] `audiobooktools discover` — auto-scan a directory and emit catalog
      entries from existing tags. Speeds up adding a batch of books from
      `Unfiltered/`.
- [ ] `audiobooktools validate` — lint pass: warn on missing covers, unused
      DESC keys, mismatched series counts, suspicious narrator strings,
      `year` values that look like publication years rather than audio
      editions.
- [ ] `audiobooktools status` — short summary: total books, total hours
      (from m4b duration), unowned-series gaps, files that don't match any
      catalog entry.
- [ ] `--diff` mode that shows what `reorg` would change without enumerating
      every file (collapsed by destination directory).
- [ ] Catalog autocompletion: when adding an entry, read the source m4b's
      existing tags and propose a draft dict.

## Phase 3 — packaging / distribution (planned)

- [ ] Publish to PyPI. Ship without a bundled catalog (the data ships
      separately).
- [ ] Provide a `cookiecutter`-style template for a fresh `catalog/`
      directory.
- [ ] CI: GitHub Actions runs ruff + pytest on every push and tag.
- [ ] Release notes automated from `patchnotes.md` via a small script.

## Phase 4 — integrations (speculative)

- [ ] Audiobookshelf API push: after `reorg --apply`, optionally trigger a
      library rescan over HTTP.
- [ ] Calibre bridge: when a catalog entry references a book that also lives
      in a Calibre library, surface a cross-link or copy the cover art.
- [ ] Watch mode: long-running process that re-scans `Unfiltered/` and
      proposes new catalog entries as files appear.

## Out of scope

- Audio re-encoding, chapter editing, or audio normalization. Use ffmpeg,
  audiobookshelf-converter, or m4b-tool for those.
- Hosted services, cloud sync, or any non-local operation. The project is
  local-first.
- A graphical UI. The catalog file is the UI.
