# Catalog template

A minimal starting point for your own AudiobookTools catalog. The engine
(`audiobooktools`) is generic; this directory is the shape of the data it
consumes. Nothing here is installed by the package: your catalog is your data
and lives beside your library, not inside the tool.

## Use it

Copy this directory to `catalog/` somewhere near your audiobook library:

```bash
cp -r catalog-template /path/to/Audiobooks/catalog
```

Then edit the two modules:

- `descriptions.py` — reused constants (authors, narrators, casts) and the
  `DESC` synopsis dictionary. Optional; a catalog with no descriptions is valid.
- `books.py` — the `BOOKS` list, one dict per owned audiobook.

Draft entries from a file's existing tags instead of writing them by hand:

```bash
abt discover --library /path/to/Audiobooks --path "/path/to/Audiobooks/Some New Book"
```

Then dry-run to confirm before writing anything:

```bash
abt retag  --library /path/to/Audiobooks --catalog /path/to/Audiobooks/catalog/books.py
abt reorg  --library /path/to/Audiobooks --catalog /path/to/Audiobooks/catalog/books.py
```

When `--catalog` is omitted, the CLI walks up from `$PWD` looking for the
nearest `catalog/books.py`, so running from inside your library just works.

See [`../spec.md`](../spec.md) for the full data contract and
[`../docs/curation-rules.md`](../docs/curation-rules.md) for the editorial
conventions the shipped catalog follows.
