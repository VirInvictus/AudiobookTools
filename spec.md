# AudiobookTools — specification

This is the data contract for AudiobookTools. It documents the BOOK dict
schema that `retag` and `reorg` consume, the layout vocabulary, the embedded
tag scheme they write, and the folder scheme they produce.

Read this if you intend to write your own `catalog/books.py`, port the tools
to another library, or modify the engines.

## Catalog file

`catalog/books.py` is a Python module that exports:

- `BOOKS: list[dict]` (required) — one entry per audiobook.
- `DESC: dict[str, str]` (optional convention) — synopsis text keyed by a
  short slug. Catalog entries can reference `DESC[key]` in their
  `description` field; the tool itself does not require this key. Any string
  works.

The CLI loads the catalog by file path (`--catalog PATH`) via
`importlib.util.spec_from_file_location`; the module does not need to be on
`sys.path`. When `--catalog` is omitted, the CLI walks up from `$PWD` looking
for the first `catalog/books.py`.

## BOOK dict shape

Every entry in `BOOKS` is a dict with these top-level keys:

| Key      | Type      | Meaning                                                    |
|----------|-----------|------------------------------------------------------------|
| `name`   | `str`     | Human-readable label used in dry-run output.               |
| `layout` | `str`     | One of `single`, `parts`, `chapters`, `discs`.             |
| `tags`   | `dict`    | The logical tag values; see below.                         |

Plus exactly one source-location key, depending on layout:

| Key         | Used by                | Meaning                                       |
|-------------|------------------------|-----------------------------------------------|
| `file`      | `single` (and others)  | Relative path to the single audio file.       |
| `glob`      | `parts`, `chapters`    | Relative glob, sorted naturally.              |
| `disc_root` | `discs`                | Folder holding `Disc *` subfolders.           |

### `tags` dict

| Key            | Type            | Notes                                                |
|----------------|-----------------|------------------------------------------------------|
| `title`        | `str`           | Per-file title; ignored for chapter-layout when the file already has a meaningful title. |
| `subtitle`     | `str`           | `""` removes the subtitle frame.                     |
| `author`       | `str`           | Written to both author and album-artist slots.       |
| `narrator`     | `str` or `None` | `None` preserves the file's existing narrator credit. |
| `album`        | `str`           | The album / book-level title.                        |
| `genre`        | `str`           | Convention: `"Audiobook"` (the `GENRE` constant).    |
| `year`         | `str`           | **Audio edition / recording year**, not original publication year. See [`docs/curation-rules.md`](docs/curation-rules.md). |
| `series`       | `str`           | `""` for standalones.                                |
| `series_index` | `str`           | `""` for standalones. Examples: `"1"`, `"00.5"`, `"06.5"`. Stored as string so zero-padded indices sort. |
| `description`  | `str` or `None` | `None` preserves the file's existing description; junk descriptions are flagged in the dry-run report. |

## Layout vocabulary

### `single`
One audio file (typically `.m4b`) holding the whole work. Use `file` to
point at it. Track and disc tags are not written.

### `parts`
Several files = ONE work split across files; uniform title/album, files
numbered as `track i/total`. Use `glob` (sorted naturally) to enumerate. The
title set on every file is the catalog `title`.

Examples in the shipped catalog: World War Z Complete Edition, the
dramatized Red Rising.

### `chapters`
Several files = ONE work, one chapter per file. Per-file title is derived
from the filename (`chapter_title_from_filename`); files numbered as
`track i/total`. Use `glob` to enumerate.

If a file already has a meaningful title tag (not empty, not a bare number),
that tag is preserved instead of being overwritten by the derived name.

Examples: Lincoln in the Bardo, the Bourdain Kitchen Confidential chaptered
edition.

### `discs`
Several files inside `Disc NN` subfolders. Uniform title; disc and track are
recomputed from the folder/filename layout. Use `disc_root` to point at the
parent folder.

Example: Just Kids, ripped from physical CDs.

## Embedded tag scheme

For each catalog tag, the tool writes the matching physical key on both
MP4-style and ID3-style files. The mapping is canonical and shared between
`retag` and any consumer of the tagged files (e.g. Audiobookshelf):

| Logical tag     | MP4 atom                                  | ID3 frame                |
|-----------------|-------------------------------------------|--------------------------|
| title           | `@nam`                                    | `TIT2`                   |
| subtitle        | `----:com.apple.iTunes:SUBTITLE`          | `TIT3`                   |
| author          | `@ART`, `aART`                            | `TPE1`, `TPE2`           |
| narrator        | `@wrt`, `----:com.apple.iTunes:NARRATOR`  | `TCOM`, `TXXX:NARRATOR`  |
| album           | `@alb`                                    | `TALB`                   |
| genre           | `@gen`                                    | `TCON`                   |
| year            | `@day`                                    | `TDRC`                   |
| series          | `----:com.apple.iTunes:SERIES`            | `TXXX:SERIES`            |
| series_index    | `----:com.apple.iTunes:SERIES-PART`       | `TXXX:SERIES-PART`       |
| description     | `@cmt`, `desc`                            | `COMM`                   |
| track           | `trkn`                                    | `TRCK`                   |
| disc            | `disk`                                    | `TPOS`                   |
| mediatype       | `stik = 2` (iTunes Audiobook)             | n/a                      |

A tag value of `""` is written as "remove the frame". A logical key
omitted from the `desired_physical` mapping is left alone on the file.

## Folder scheme

`reorg` derives the destination tree from the catalog tags via
`audiobooktools.schema.book_dir`. The rule:

- **Standalone**, or a lone owned entry of a series: `Author/Album/...`
- **Series with 2+ owned entries**:
  `Author/Series/{series_index} - {Album}/...`

`{Album}` is `tags["album"]`; the `series_index` prefix is the raw catalog
value (so a zero-padded `"01"` sorts before `"02"`).

File renames within a destination folder follow per-layout rules:

- `single`: `<sanitized album><ext>`
- `parts`: `<sanitized album>, Part N<ext>`
- `chapters`: keep the existing filename (catalog assumes filenames are
  already clean)
- `discs`: `Disc NN/NN - <sanitized album><ext>`

All path components pass through `sanitize`, which:

1. Replaces `": "` with `" - "`.
2. Removes NTFS-illegal characters (`\ / : * ? " < > |`).
3. Collapses whitespace.
4. Strips trailing dots and spaces.

## Cover art and extras

`reorg` runs a two-pass extras router after audio moves:

**Pass 1** — for each source folder, any non-audio sibling files (cover
images, `.epub`, `.nfo`, `.cue`, `.txt`) are routed to the destination:

- The first matching image becomes `cover.jpg` in the destination folder.
- Other files go to `_extras/<original-name>` in the destination.
- When multiple books share a source folder, files are matched to the book
  whose audio filename stem they share; unmatched files fall through to
  Pass 2.

**Pass 2** — group-level extras (everything left in an
`Unfiltered/<work-group>/` source root, e.g. series-wide artwork or
eBooks) are routed to the **series** `_extras/` folder when all
group-members share a series; otherwise to the first member's own
`_extras/`. The relative subpath inside the source group is preserved.

## Idempotency guarantee

A dry run immediately after `--apply` must report `0/N files need
changes`. The shipped tests include an end-to-end check of this property
against the live catalog. Any patch that breaks idempotency is a bug.

## Restore and reverse

- `retag --apply` writes `backup.json` (default:
  `<library>/.audiobooktools/backup.json`) containing each modified file's
  pre-change tag state. `retag --restore PATH` reads that file and writes
  the recorded tags back, fully reversing the apply pass.
- `reorg --apply` writes `reorg-manifest.json` (default:
  `<library>/.audiobooktools/reorg-manifest.json`) containing every move as
  `{"src": ..., "dst": ...}`. `reorg --reverse PATH` walks the manifest in
  reverse order and renames each `dst` back to its `src`.

Both files are JSON for human inspection; both default to under
`<library>/.audiobooktools/` so the library directory carries its own
history.

## What the tool will not do

- **Delete audio files.** `reorg` moves and renames; it never `rm`s an
  audio file. Removing books from the shelf is an explicit user action
  (`rm -rf Author/Title`).
- **Re-encode.** Tags are edited in place via mutagen; the audio stream
  bytes are untouched.
- **Modify cover art.** Cover images are moved by the extras router but
  their bytes are not touched.
- **Talk to Audiobookshelf.** The produced tree happens to be the layout
  Audiobookshelf expects, but the tool does not call any server API. Use
  Audiobookshelf's own scanner against the produced tree.
