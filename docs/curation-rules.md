# Curation rules

Editorial conventions the shipped `catalog/` follows. The engine doesn't
enforce any of these; they are the rules the *user* of AudiobookTools
applies when deciding what goes in the catalog and how it's tagged.

If you fork the catalog for your own library, you can keep these, replace
them with your own, or drop them. They're documented here because the
shipped data follows them consistently and because they explain otherwise
puzzling choices (Why aren't books 5-7 of Dark Tower here? Why is *The
Gunslinger* kept despite being the weakest novel of the seven?).

## The "high marks of audiobooks" principle

The catalog only holds audiobooks where the audio production itself meets
a high bar. A book in the ebook library that has no exceptional audio
edition does not earn a catalog entry.

What counts as "high marks":

1. **Full-cast dramatization or audio drama.** Examples in the shipped
   catalog: *Lincoln in the Bardo* (166-voice cast), *The Sandman*
   (Audible audio drama), *World War Z: The Complete Edition*, *Hyperion*
   (Audible Frontiers Full Cast), the GraphicAudio dramatized
   *Red Rising*.
2. **Author-narrated where the author is a great reader.** *Kitchen
   Confidential* (Bourdain), *Just Kids* (Patti Smith), *The Blacktongue
   Thief* and *The Lesser Dead* (Buehlman).
3. **Legendary single-narrator performance.** Steven Pacey for the entire
   First Law / Age of Madness arc. Jefferson Mays for *The Expanse*. Jeff
   Hays for *Dungeon Crawler Carl*. Frank Muller for *The Dark Tower*
   books 1-4. Andy Serkis for *The Lord of the Rings* (2021). Ray Porter
   for *Project Hail Mary*. Lee Horsley for *Lonesome Dove*. Jeremy Irons
   for *Lolita*. Julian Rhind-Tutt for *The Master and Margarita*.
4. **Production rescues a borderline work.** *The Gunslinger* is a 3/5
   novel; Frank Muller's reading is a high mark in its own right and
   carries it.

A 5/5 ebook with a workmanlike narration does not automatically earn a
catalog entry. Buy the prose, not the audio, in those cases.

## Year tag = recording year, not publication year

For the `year` tag on every catalog entry, use the **audiobook
recording / edition year**, not the underlying book's original
publication year.

**Why.** These are audiobooks. The edition year is the real attribute of
the file you own, and it avoids anachronisms (LOTR shows 2021 for the
Serkis recording, not 1954). It also matches what most publishers'
distributor tags already hold.

**How to apply.** When a work's print year and audiobook release differ,
tag the audio release year:

- *Blood Meridian* = 2007 (Richard Poe recording), not 1985.
- *The First Law* trilogy = 2010 (Pacey re-recording), not 2006-2008.
- *The Lord of the Rings* = 2021 (Serkis), not 1954-1955.
- *Lolita* = 2005 (Jeremy Irons), not 1955.

Audio-only productions (the Sandman drama, the Red Rising dramatization,
WWZ Complete Edition) use their own release year as the only year.

## Narrator quality as a curation criterion

When a series has been narrated by multiple readers over its lifetime,
only the production that meets the high-marks bar is acquired. Two
worked examples:

### Dark Tower

- **Books 1-4** are in the catalog: Frank Muller's recordings, widely
  considered some of the great fantasy narrations ever.
- **Books 5-7** are *not* in the catalog. After Muller's stroke in
  2001, George Guidall took over for the final three. Guidall is a
  capable narrator; the switch breaks immersion mid-saga. Off the shelf.

### Malazan-world

- **Malazan #1-3** (*Gardens of the Moon*, *Deadhouse Gates*, *Memories
  of Ice*) plus the **Witness duology** (*The God Is Not Willing*, *No
  Life Forsaken*) are in the catalog.
- **Malazan #4-10**, the Kharkanas trilogy, and all of Ian Cameron
  Esslemont's Empire and Path to Ascendancy novels are *not*. The
  back-half productions and the Esslemont audio are reported to be a
  step down. Off the shelf.

The same principle ruled out the Bobiverse books past *We Are Legion*
(work decline) and *Acts of Caine* books 3-4 (work decline), even though
the narrators (Ray Porter and Stefan Rudnicki respectively) are strong.

## Series treated as standalones

Some series are best entered through a single doorway. Catalog
modeling:

- **Hyperion Cantos** is owned as the Hugo-winning book 1 (Full Cast)
  plus *The Fall of Hyperion* (Bevine solo). The Endymion duology is
  not in the catalog: weaker novels, weaker production. The series
  folder still uses `Hyperion Cantos` to keep the door open.
- **Bobiverse** is owned only as book 1. Same logic.
- **The Expanse** mainline novels are in the catalog; the novellas
  (`The Churn`, `Strange Dogs`, *Memory's Legion*, etc.) are not.

## Series modeling conventions

Mostly mechanical, but documented here so the catalog stays consistent
as it grows:

- **First Law standalones #4-7** (*Best Served Cold* through *Sharp
  Ends*) live under the single `The First Law` series (1-7). *The Age
  of Madness* is its own series 1-3.
- **Black Company** preserves Cook's sub-trilogy arcs (three series
  under Glen Cook: Books of the North 1-3, Books of the South 1-2,
  Books of the Glittering Stone 1-4). *The Silver Spike* is a
  standalone spin-off.
- **The Expanse** novels and novellas share one series with
  Goodreads-style zero-padded indices (`00.1`, `00.2`, `00.5`, `01`,
  `02`, `02.5`, … `09.5`, `10`).
- **Hyperion Cantos** keeps both narrator editions when owned; the
  album carries the narrator suffix (`Hyperion (Various Full Cast)`,
  `The Fall of Hyperion (Bevine)`) so the folders are unique.
- **Witness** is a series under Steven Erikson (#1 *The God Is Not
  Willing*, #2 *No Life Forsaken*); *Gardens of the Moon* lives in
  `Malazan Book of the Fallen` as series #1.
- **Mixed-author series finales** (Gormenghast's *Titus Awakes* by
  Maeve Gilmore) live under the main author's folder, co-author noted
  in the subtitle.

## Single-File (M4B) vs. Multi-File (MP3) Layouts

Where possible, a single `.m4b` file per audiobook is the preferred layout. It provides a cleaner directory structure, unified chapter metadata, and guaranteed correct playback order across all devices.

However, massive multi-file collections (e.g., a 109-part `.mp3` layout for a book with a 160+ person cast) can be preserved as individual tracks if merging them via tools like `m4b-tool` risks dropping embedded per-track metadata or corrupting the files. 

When preserving multi-file layouts, ensure the tracks are correctly zero-padded (e.g., `001 - Title.mp3` to `109 - Title.mp3`) so lexicographical sorting matches chronological playback.

## What gets culled

In descending order of severity:

1. **Lower-quality production of a work that already has a high-marks
   edition on the shelf.** Cull immediately.
2. **Completionism for a series whose work-quality clearly declines.**
   Keep the peak entries (typically books 1-N where N is the cutoff),
   cull the rest, and document the cutoff in this file if it's
   non-obvious.
3. **Standalone works where the audio is a step below excellent and
   the book is below 4/5.** These rarely earn a catalog spot in the
   first place.
4. **Story collections appended to series.** *Sharp Ends* sits in the
   catalog only because the rest of First Law does; if the catalog is
   ever pruned harder, story collections go first.

## Adding a new book: the checklist

Before committing a new catalog entry, walk through:

1. Is the audio production a high mark? Full cast / author-narrated /
   legendary solo? If no, prefer the ebook.
2. If it's part of a series where you own other entries, does this entry
   meet the same bar as the others?
3. Is the `year` set to the audio edition year (not the publication
   year)?
4. Is the narrator string the *actual* narrator on the production you
   own, not the one Wikipedia lists for some other edition?
5. Does the series modeling match the conventions above?

If you can answer yes to all five, commit. If not, leave it in
`Unfiltered/` until the question resolves.
