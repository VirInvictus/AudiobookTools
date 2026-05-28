# Workflows

Operational walkthroughs for everyday AudiobookTools tasks. Assumes you've
already installed (`uv pip install -e .`) or set up the `uv run` invocation
pattern.

## Daily: normal apply cycle

Run any time you've edited `catalog/books.py`.

```bash
# 1. Dry run: see what would change.
audiobooktools retag --library /path/to/Audiobooks

# 2. If the diff looks right, apply.
audiobooktools retag --library /path/to/Audiobooks --apply

# 3. Confirm idempotency: a second dry run should report 0 changes.
audiobooktools retag --library /path/to/Audiobooks
```

`reorg` is the same triple:

```bash
audiobooktools reorg --library /path/to/Audiobooks            # dry
audiobooktools reorg --library /path/to/Audiobooks --apply    # execute
audiobooktools reorg --library /path/to/Audiobooks            # confirm idempotent
```

Order matters when both have changes pending: **`retag --apply` first, then
`reorg --apply`**. `retag` operates on files where they currently sit;
`reorg` moves them after.

## Adding a book from `Unfiltered/`

Convention: drop new audio under `<library>/Unfiltered/<work-group>/` so the
extras router has a stable group boundary for cover art and series
artwork.

### 1. Stage the files

```
Unfiltered/
└── Red Rising Series Audible/
    ├── Red Rising by Pierce Brown Book 1.m4b
    ├── Golden Son by Pierce Brown Book 2.m4b
    ├── ...
    └── (optional) cover.jpg, Maps/, eBooks/
```

### 2. Read the existing tags

You want to confirm the narrator, year, and any series metadata embedded by
the publisher before writing your own:

```bash
uv run --no-project --with mutagen python -c "
from mutagen import File
for p in ['Unfiltered/Red Rising Series Audible/Red Rising by Pierce Brown Book 1.m4b']:
    f = File(p)
    for k in ('\xa9nam','\xa9ART','\xa9wrt','\xa9day','\xa9alb'):
        print(k, '->', f.tags.get(k, ['<missing>']))
"
```

For unfamiliar narrators, cross-check on Audible / AudioFile Magazine
before committing — there are usually multiple editions in the wild and
the catalog should name the one you actually own.

### 3. Write the catalog entry

In `catalog/books.py`, near similar entries:

```python
single(
    "Unfiltered/Red Rising Series Audible",
    "Red Rising by Pierce Brown Book 1.m4b",
    title="Red Rising",
    subtitle="Red Rising Saga, Book One",
    author="Pierce Brown",
    narrator="Tim Gerard Reynolds",
    album="Red Rising",
    year="2014",
    series="Red Rising",
    series_index="1",
    description=DESC["red_rising"],          # add to descriptions.py first
),
```

`folder` is relative to the library root. Use the `single` helper for
one-file books; write a full dict literal for `parts` / `chapters` /
`discs` layouts.

### 4. Dry-run both engines

```bash
audiobooktools retag --library /path/to/Audiobooks
audiobooktools reorg --library /path/to/Audiobooks
```

Look for the new book's name in each report. `retag` should show the new
tags being written; `reorg` should show the moves into the
`Pierce Brown/Red Rising/` destination.

### 5. Apply

```bash
audiobooktools retag --library /path/to/Audiobooks --apply
audiobooktools reorg --library /path/to/Audiobooks --apply
```

Both record an artifact under `<library>/.audiobooktools/`:

- `backup.json` — pre-change tags for everything `retag` modified.
- `reorg-manifest.json` — every `(src, dst)` pair `reorg` executed.

These are how you undo if something goes wrong.

## Undo: restore

If a `retag --apply` produced unexpected results, restore the previous
tags:

```bash
audiobooktools retag --restore /path/to/Audiobooks/.audiobooktools/backup.json
```

The restore reads every entry in `backup.json` and writes the recorded tags
back to each file. Cover art and chapter tracks are untouched (they always
are; `retag` never wrote them).

## Undo: reverse

If a `reorg --apply` produced an unexpected tree, reverse the moves:

```bash
audiobooktools reorg --reverse /path/to/Audiobooks/.audiobooktools/reorg-manifest.json
```

`reorg --reverse` walks the manifest in reverse order and renames every
`dst` back to its `src`. Empty destination directories that result are
left in place (you can `find -type d -empty -delete` if you want them
gone).

## Removing a book from the shelf

The tool itself never deletes audio. The recipe:

1. Cull the source files (`rm -rf "Pierce Brown/Red Rising (Dramatized
   Adaptation)/"`).
2. Remove the matching catalog entry from `catalog/books.py`.
3. Run `audiobooktools retag --library ...` (dry) — the removed entry
   should not appear (since it's no longer in the catalog), and no
   surviving entry should reference its files.
4. If `series` counts changed (e.g. you culled the only Red Rising entry),
   any remaining entries of the same series get re-routed at next
   `reorg --apply` — confirm with a dry run before applying.

## Troubleshooting

### `!! <book name>: no files matched`

The catalog entry references a source path that doesn't exist on disk.
Either:

- The file moved (e.g. a prior `reorg --apply` placed it in its destination,
  and the catalog's `file`/`glob` still points at the staging path).
  `retag` handles this automatically by also checking the destination
  derived from `schema.book_dir`. If that's also empty, the file is genuinely
  missing.
- The catalog entry is stale (the book was culled but the entry remains).
  Remove the entry.
- A typo in `file`/`glob`. Check the path.

### `REFUSING: pre-flight problems`

`reorg`'s collision check found two source files mapping to the same
destination, or a destination that already exists with no source
mapped to it. The message names the offending paths.

Fix: usually a duplicate catalog entry (two books resolved to the same
album/series), or a hand-renamed destination that the catalog doesn't know
about.

### Junk comment warnings

`retag` reports `⚠ <file>: junk comment preserved: 'Chapter 72'`. The
description field of that file looks like noise (a chapter number or a
"Read by X" credit) rather than a real synopsis. Either:

- Add a real description to the catalog (preferred), or
- Leave the warning. The tool isn't going to overwrite a `None` description
  silently; the warning is just a flag.

### Tag diff shows changes you didn't make

When you first apply, every file with non-canonical tags will diff. That's
expected; the catalog is now the source of truth. After that first apply,
subsequent dry runs should be empty.

If a dry run keeps producing changes, that's a bug — open an issue or read
`spec.md`'s idempotency section.
