# AudiobookTools

Declarative tag normalization and Audiobookshelf-friendly folder reorganization
for personal audiobook libraries. One source of truth (your catalog file)
drives both the embedded tags on the audio files and the on-disk folder tree,
so the two can't drift.

The library shipped with this repository is the author's; the engine is
generic. Bring your own `catalog/books.py` and the tools will normalize
yours.

## Features

- **Declarative.** You describe each audiobook once in `catalog/books.py`;
  `retag` and `reorg` derive the embedded metadata and the folder layout from
  the same dict.
- **Reversible.** Every apply pass writes a backup of the prior tag state
  (`backup.json`) and a manifest of every move (`reorg-manifest.json`). Both
  operations have explicit `--restore` / `--reverse` modes.
- **Idempotent.** A dry run after an apply reports zero remaining changes.
- **Dry-run by default.** Nothing is written unless you pass `--apply`.
- **In place.** Tags are edited via mutagen with no audio re-encode; cover
  art and m4b chapter tracks are preserved.
- **MP4 and ID3.** Writes both Apple-style atoms (`@nam`, `aART`,
  `----:com.apple.iTunes:SERIES`, `stik=2`) and ID3 frames (`TIT2`, `TPE1`,
  `TXXX:SERIES`, `COMM`) to the matching files.

## Install

Requires Python 3.10+ and `uv` (or pip).

```bash
git clone https://github.com/VirInvictus/AudiobookTools.git
cd AudiobookTools
uv pip install -e .
```

Or, without installing, run any subcommand via `uv run`:

```bash
uv run --with mutagen python -m audiobooktools.cli retag --help
```

## Three-command tour

Assuming your library is at `/path/to/Audiobooks` and your catalog file is at
`./catalog/books.py`:

```bash
# Plan: show every tag change that would be made; write nothing.
audiobooktools retag --library /path/to/Audiobooks

# Execute: back up the prior state, then write the new tags.
audiobooktools retag --library /path/to/Audiobooks --apply

# Undo: restore from the backup file the apply pass wrote.
audiobooktools retag --restore /path/to/Audiobooks/.audiobooktools/backup.json
```

The same dry/apply/reverse triple applies to `reorg`:

```bash
audiobooktools reorg --library /path/to/Audiobooks                # dry run
audiobooktools reorg --library /path/to/Audiobooks --apply        # execute
audiobooktools reorg --reverse /path/to/Audiobooks/.audiobooktools/reorg-manifest.json
```

Short alias `abt` is registered for both:

```bash
abt retag --library /path/to/Audiobooks
abt reorg --library /path/to/Audiobooks --apply
```

## Conventional layout produced by `reorg`

```
Audiobooks/
├── Andy Weir/
│   └── Project Hail Mary/
│       ├── Project Hail Mary.m4b
│       └── cover.jpg
├── Joe Abercrombie/
│   ├── The First Law/
│   │   ├── 1 - The Blade Itself/
│   │   ├── 2 - Before They Are Hanged/
│   │   └── 3 - Last Argument of Kings/
│   └── The Devils/             # lone series entry stays flat
└── Steven Erikson/
    └── Malazan Book of the Fallen/
        └── 1 - Gardens of the Moon/
```

A series gets its own subfolder when 2+ books of that series are owned;
standalones and lone series entries go directly under the author. Names are
NTFS-safe (illegal characters stripped, `": "` → `" - "`).

## Catalog shape

`catalog/books.py` exports `BOOKS: list[dict]`. Each dict describes one
audiobook (or one volume of a series). The shape is documented in full in
[`spec.md`](spec.md); the short version:

```python
from audiobooktools.schema import single, GENRE
from catalog.descriptions import DESC

BOOKS = [
    single(
        "Andy Weir - Project Hail Mary",        # source folder
        "Project Hail Mary.m4b",                # source filename
        title="Project Hail Mary",
        subtitle="",
        author="Andy Weir",
        narrator="Ray Porter",
        album="Project Hail Mary",
        year="2021",                            # audio edition year
        series="",
        series_index="",
        description=DESC["project_hail_mary"],  # optional
    ),
    # ... more entries
]
```

See [`docs/curation-rules.md`](docs/curation-rules.md) for the editorial
conventions the shipped catalog follows (year = recording year, high-marks
narrator policy, etc).

## What it does not do

- **Never deletes audio.** `reorg` moves and renames; it never removes a
  source file. Removing books from the shelf is an explicit user action.
- **Never re-encodes.** Tags are edited in place via mutagen; the audio
  stream is untouched.
- **No remote sync.** AudiobookTools is local-first. It produces an
  Audiobookshelf-shaped tree, but it doesn't talk to an Audiobookshelf
  server.

## Project layout

```
audiobooktools/    schema, retag engine, reorg engine, CLI
catalog/           user data: BOOKS list + DESC descriptions
docs/              workflows, curation rules
tests/             pytest helpers + catalog smoke test
```

See [`spec.md`](spec.md) for the data contract, [`roadmap.md`](roadmap.md)
for what's done and what's next, and [`patchnotes.md`](patchnotes.md) for the
release log.

## License

MIT. See [`LICENSE`](LICENSE).
