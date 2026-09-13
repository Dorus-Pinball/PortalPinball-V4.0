---
name: cite-reference
description: Use when about to cite a new external doc/wiki page/forum thread in any project doc ("per this doc...", adding a URL as a source, referencing outside material). Archives a local copy under docs/references/raw/<slug>/content.md and adds a matching docs/references/index.yaml entry in the same pass as the doc edit, so a citation doesn't go dead if the live page changes or vanishes.
---

# Citing an external reference: process

This project's docs cite outside sources (MPF docs, hardware wikis, datasheets) directly. To keep
those citations from rotting when a page moves or disappears, every citation gets archived
locally, not just linked. This skill is the checklist for doing that consistently - the rule
itself is stated in the project `CLAUDE.md`'s "Key facts"; this skill is the repeatable process
for applying it.

## Steps

1. **Fetch the source** you're about to cite and confirm it's actually worth archiving - see the
   `Don't` list below for what to skip.

2. **Pick a slug** - short, kebab-case, descriptive (e.g. `cobrapin-official-doc`,
   `mpf-docs-opp-switches`). Check `docs/references/index.yaml` first to avoid a collision or a
   near-duplicate of an existing entry for the same source.

3. **Save a local copy** under `docs/references/raw/<slug>/content.md` - the page's content in
   Markdown (or a close plain-text equivalent), not just a link. This is what survives if the
   live page goes away.

4. **Add one entry to `docs/references/index.yaml`**, matching the existing entries' shape:
   ```yaml
   - slug: <slug>
     title: "<page title>"
     url: "<source url>"
     date_archived: "<YYYY-MM-DD>"
     cited_by: "<doc path citing it>"
     note: "<one line on why this source matters / what it's cited for>"
   ```
   Do this **in the same pass** as the doc edit that cites the source - don't leave the citation
   dangling without a matching archive entry, even briefly.

5. **Regenerate `docs/references/index.md`** - fires automatically via the `PostToolUse` hook
   after saving `index.yaml` (same hook that regenerates the wiring docs), but running
   `python tools/hw_console/generate_docs.py` by hand is a fine sanity check.

6. **Cite it in the doc** using the source's title/url as normal prose - the archive entry is
   backing, not a replacement for a readable inline citation.

## Don't

- Don't hand-edit `docs/references/index.md` - it's generated from `index.yaml` and overwritten
  on the next run.
- Don't archive everything indiscriminately - a plain GitHub repo landing page or a 403/snippet-
  only forum thread with nothing durable to save can be skipped deliberately (see the one-time
  sweep note at the top of `docs/references/index.yaml` for the precedent - skip with judgment,
  not silently omit without considering it).
- Don't cite a new external source in a project doc without adding the matching archive entry in
  the same pass - a citation with no `docs/references/` backing is exactly the gap this skill
  exists to close.
