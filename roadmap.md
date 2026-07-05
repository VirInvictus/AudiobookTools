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

- [x] Restore the test environment. Dev deps (`pytest`, `ruff`) moved from
      `[project.optional-dependencies]` to a PEP 735 `[dependency-groups]`
      block so a plain `uv sync` installs them by default; that closes the
      regression at its root (the old extra had to be requested explicitly,
      so a fresh `.venv` came up without pytest). Suite runs green (40
      passed) and is pinned in `pyproject.toml` + `uv.lock`.
- [x] Commit or revert the uncommitted changes to `catalog/books.py` and
      `catalog/descriptions.py` (committed; working tree clean).

## Phase 2 — quality of life (v0.2.0)

- [x] `audiobooktools discover` — auto-scan a directory and emit catalog
      entries from existing tags. Speeds up adding a batch of books from
      `Unfiltered/`. Infers layout from folder shape; dedups against a
      discoverable catalog so it only surfaces new books.
- [x] `audiobooktools validate` — lint pass: missing covers, unused DESC
      keys, duplicate/mismatched series indices, suspicious narrator strings,
      `year` values that look like publication years rather than audio
      editions. Exits non-zero on findings (CI-usable).
- [x] `audiobooktools status` — short summary: total books, on-disk vs.
      catalogued count, total runtime (from decoded durations), catalogue
      entries not present on disk, files that match no catalog entry, and
      possible series-index gaps.
- [x] `--diff` mode that shows what `reorg` would change without enumerating
      every file (one line per destination directory).
- [x] Catalog autocompletion: read the source file's existing tags and
      propose a draft entry. Folded into `discover` (point `--path` at a
      single new folder to draft that one entry).

## Phase 3 — packaging / distribution

- [~] Publish to PyPI. Packaging is ready: the wheel is engine-only and the
      sdist excludes `catalog/`, so the author's data never ships (verified in
      CI). A dormant `publish.yml` builds, cuts a GitHub Release from the
      changelog, and publishes via PyPI trusted publishing on a `vX.Y.Z` tag.
      **Remaining:** configure the trusted publisher on PyPI, then push the
      first tag. Nothing publishes until then.
- [x] Provide a `cookiecutter`-style template for a fresh `catalog/`
      directory (`catalog-template/`: minimal `books.py` + `descriptions.py`
      + README, copyable to `catalog/`).
- [x] CI: GitHub Actions runs ruff (lint + format check) + pytest on Python
      3.10–3.13 on every push and PR, plus a build-and-verify job.
- [x] Release notes automated from `patchnotes.md` via a small script
      (`scripts/release_notes.py`), wired into `publish.yml`.

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
