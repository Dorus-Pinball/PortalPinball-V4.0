# Story-to-shots-to-modes workflow + design schema

> **Status: implemented.** Confirmed via plan mode and built in full (`design/README.md`,
> `design/schema/feature.schema.json`, `design/features/*.yaml`, `tests/test_design_docs.py`).
> Kept here as the durable record of the approach, per the collaboration workflow's "confirmed
> plans belong in the repo" rule.

## Context

So far, feature ideas for this machine live in two places that don't talk to each other: the
free-form "Modes" sheet in `board Overviews.xlsx` (a messy brainstorm — mechanic names, switch
scribbles, no consistent structure) and prose bullets in `plans/resumption-roadmap.md` Phase 3
(8 features already identified: `lanes`, `orbits`, `slings`, `skillshot`, `dropbank`, `aerial`,
`portal`, `ramps`). Neither captures the *story* side (this is a Portal-themed machine, but no
document currently holds "what narrative beat does this feature express") or gives a repeatable
process for turning a story idea into a buildable MPF mode. The user wants both: a **workflow**
for going story idea → shots → mode, and a **structured, schema-based way to track and document**
these layered feature designs going forward — replacing the xlsx as the living source for new
feature design (the xlsx stays as a historical hardware-planning reference, not deleted).

## The layer model

Every feature in this game decomposes into 5 layers, and this model **is** the workflow — moving
a feature idea from top to bottom *is* the process:

1. **Story** — the narrative beat (freeform; can be "TBD" while a feature is still mechanic-first).
2. **Feature** — the named gameplay feature that expresses that beat.
3. **Shots** — the physical playfield elements involved. Each shot **references real hardware by
   name** (switches/coils/lights already defined in `machinefolder/config/hardware-*.yaml`) — the
   design doc never re-specifies hardware, only points at it, so hardware config stays the single
   source of truth.
4. **Rules/Mode** — the MPF devices needed (shots/shot_groups/logic_blocks/achievements, per the
   scaffolding already planned in `plans/resumption-roadmap.md` Phase 2) and the mode name that
   will live under `machinefolder/modes/<name>/`.
5. **Presentation** — the slide/show/sound treatment (`machinefolder/modes/<name>/slides|shows`).

## What gets built

```
design/
  README.md                    # the workflow doc itself (steps below, written out for reuse)
  schema/
    feature.schema.json        # JSON Schema for a feature design doc
  features/
    _template.yaml             # copy this to start a new feature
    lanes.yaml
    orbits.yaml
    slings.yaml
    skillshot.yaml
    dropbank.yaml
    aerial.yaml
    portal.yaml
    ramps.yaml
tests/
  test_design_docs.py          # validates every design/features/*.yaml against the schema
                                # AND cross-checks every shot ref against real hardware config
```

### `design/schema/feature.schema.json`

A real JSON Schema (not just documented convention) with these top-level fields:
- `id`, `name` — required strings.
- `status` — required enum: `idea` / `designed` / `implementing` / `implemented` / `tested` /
  `live`. This is the tracking mechanism — a feature's position in the workflow is always visible
  at a glance across all files.
- `story` — object `{ hook, beats[] }`, nullable/TBD allowed (a feature can be mechanic-first and
  get its narrative pass later — never blocks progress).
- `shots` — array of `{ ref, role }`, where `ref` must name a real switch/coil/light.
- `rules` — object `{ mode, devices[] (each { type: enum[shot|shot_group|counter|accrual|
  achievement|ball_save|...], name, notes}), scoring }`.
- `presentation` — object `{ slide, show, sound }`, freeform notes, placeholder allowed.
- `phase` — optional cross-reference to a `plans/resumption-roadmap.md` phase.
- `notes` — freeform.

### The 8 existing features, pre-populated

Populate `lanes.yaml` through `ramps.yaml` now, using facts already established in this
repo (hardware names from `hardware-*.yaml`, mechanic descriptions from
`plans/resumption-roadmap.md` Phase 3) — **not inventing new story content**. Where the xlsx/
roadmap only gives a mechanic (no narrative beat), `story.hook` is explicitly set to
`"TBD - needs a narrative pass"` rather than fabricated Portal lore; that's a real, visible gap
for the user to fill in, not something to guess at. `portal.yaml` (the namesake feature) is the
fullest example since it has the richest existing detail (dropper → portal-r/m → exit-success,
5-stage `led-exit-open-1..5`).

### `tests/test_design_docs.py`

Follows the existing pattern from `tests/test_bringup.py` (plain `unittest`, run via
`python -m unittest discover tests` — consistent with `plans/testing-strategy.md`). For every
`design/features/*.yaml` except `_template.yaml`:
- Validates structurally against `feature.schema.json` via the `jsonschema` package (new small
  dev-only dependency — added to `install.ps1` alongside the existing `mpf` pin, since that's
  already the established one-command setup path).
- Cross-checks every `shots[].ref` against the real names parsed out of
  `hardware-switches.yaml`/`hardware-coils.yaml`/`hardware-leds.yaml` (via `ruamel.yaml`, already
  installed as an MPF dependency — no extra parsing dependency needed). This is the concrete
  payoff of tying the schema to real hardware: a renamed/typo'd switch reference in a design doc
  fails the test suite instead of silently drifting from reality.

### `design/README.md` — the workflow, written out

1. Jot the raw story idea in `IDEAS.md` first (already the user's freeform space — no process
   change there).
2. Copy `design/features/_template.yaml` to `design/features/<id>.yaml`, `status: idea`.
3. Fill **Shots**: pick real hardware from `hardware-*.yaml` that can realize the feature. If the
   right hardware doesn't exist yet, stop here and add it to `TODO.md` instead of inventing a shot
   that isn't wired.
4. Fill **Rules/Mode**: sketch which MPF device types are needed and name the mode, cross-checking
   against the Phase 2 scaffolding in `plans/resumption-roadmap.md` (e.g. an ordered target run is
   an `accrual`, a staged progression is `achievements`, not a bare counter). Set `status:
   designed`.
5. Fill **Presentation**: at minimum note what slide/show/sound this needs, even if placeholder.
6. Implement: build the real `machinefolder/modes/<name>/config/<name>.yaml` (+ slide/show),
   following the `base`/`attract` pattern, add the mode to `config.yaml`'s `modes:` list. Set
   `status: implementing` while in progress.
7. Test: interactive check via `mpf -X -t -b` (Tier 1) and a new `tests/test_<name>.py`
   (Tier 2) per `plans/testing-strategy.md`. Set `status: implemented` once the mode boots clean,
   `tested` once it has a passing automated test.
8. Playtest on real hardware per the resumption roadmap's verification standard; set `status:
   live` once confirmed working on the cabinet. Log anything decision-worthy in `CHANGES.md`.

## Files to change

- New: `design/README.md`, `design/schema/feature.schema.json`, `design/features/_template.yaml`
  + the 8 populated feature files, `tests/test_design_docs.py`.
- `install.ps1`: add a pinned `jsonschema` install alongside the existing `mpf==0.80.0` line.
- `plans/resumption-roadmap.md`: Phase 3 section gets a pointer to `design/features/*.yaml` as the
  now-living source for these 8 features (xlsx stays referenced as historical hardware-planning
  context, not removed).
- `README.md`: one-line addition to the layout tree for `design/`.
- `TODO.md`: no new entries needed unless the Shots pass above surfaces a real hardware gap while
  populating the 8 files (possible for `ramps`, already flagged in the roadmap as under-specified).

## Verification

- `python -m unittest discover tests` (from repo root, venv active) passes, including the new
  `test_design_docs.py` — proves the schema is valid JSON Schema, all 8 pre-populated feature
  files conform to it, and every shot reference in them resolves to real hardware.
- Manually confirm `design/features/_template.yaml` alone (copy it, fill nothing in beyond `id`)
  intentionally *fails* validation on required fields — proves the schema is actually enforcing
  something, not just decorative.
