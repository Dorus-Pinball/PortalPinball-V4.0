# Story -> shots -> modes workflow

This is the process for turning a game-story idea into a buildable MPF mode, and the structured
way we track where each feature is in that process. It replaces `board Overviews.xlsx`'s "Modes"
sheet as the *living* source for new feature design — the xlsx stays as a historical
hardware-planning reference, not deleted.

## The layer model

Every feature decomposes into 5 layers. Moving a feature from top to bottom *is* the workflow:

1. **Story** — the narrative beat. Can be `"TBD - needs a narrative pass"` while a feature is
   still mechanic-first — this never blocks progress on the other layers.
2. **Feature** — the named gameplay feature that expresses that beat.
3. **Shots** — the physical playfield elements involved. Each shot **references real hardware by
   name** (switches/coils/lights already defined in `machinefolder/config/hardware-*.yaml`) — a
   feature doc never re-specifies hardware, only points at it, so the hardware config stays the
   single source of truth. `tests/test_design_docs.py` checks every reference actually exists.
4. **Rules/Mode** — the MPF devices needed (`shot`, `shot_group`, `counter`, `accrual`,
   `sequence`, `achievement`/`achievement_group`, `ball_save`, `drop_target_bank`, ...) and the
   mode name that will live under `machinefolder/modes/<name>/`. See
   `plans/resumption-roadmap.md` Phase 2 for the scaffolding these devices build on, and Phase 2's
   guidance on picking the right device type (e.g. an ordered target run is an `accrual`, a
   staged progression is `achievements`, not a bare counter).
5. **Presentation** — the slide/show/sound treatment (`machinefolder/modes/<name>/slides|shows`).

## Tracking: one YAML file per feature

`design/features/<id>.yaml`, one per feature, validated against `design/schema/feature.schema.json`.
`status` is the tracking field — a feature's position in the workflow is visible at a glance
across every file, without needing a separate dashboard:

```
idea -> designed -> implementing -> implemented -> tested -> live
```

Run `python -m unittest discover tests` (from the repo root, venv active — see
`plans/testing-strategy.md`) any time to validate every feature file against the schema and
cross-check every shot reference against the real hardware config.

## The workflow, step by step

1. **Jot the raw story idea** in `IDEAS.md` first (already the user's freeform space — no process
   change there).
2. **Copy `design/features/_template.yaml`** to `design/features/<id>.yaml`. `status: idea`.
3. **Fill Shots.** Pick real hardware from `hardware-switches.yaml`/`hardware-coils.yaml`/
   `hardware-leds.yaml` that can realize the feature. If the right hardware doesn't exist yet,
   stop here and add it to `TODO.md` instead of inventing a shot that isn't wired.
4. **Fill Rules/Mode.** Sketch which MPF device types are needed and name the mode. Set
   `status: designed`.
5. **Fill Presentation.** At minimum note what slide/show/sound this needs, even as a
   placeholder.
6. **Implement.** Build the real `machinefolder/modes/<name>/config/<name>.yaml` (+ slide/show),
   following the existing `base`/`attract` pattern, and add the mode to `config.yaml`'s `modes:`
   list. Set `status: implementing` while in progress.
7. **Test.** Interactive check via `mpf -X -t -b` (Tier 1) and a new `tests/test_<name>.py`
   (Tier 2) per `plans/testing-strategy.md`. Set `status: implemented` once the mode boots clean,
   `tested` once it has a passing automated test.
8. **Playtest on real hardware** per the resumption roadmap's verification standard. Set
   `status: live` once confirmed working on the cabinet. Log anything decision-worthy in
   `CHANGES.md`.

## Current features

The 8 features already identified in `plans/resumption-roadmap.md` Phase 3 are pre-populated in
`design/features/` at `status: designed` (Shots + Rules layers filled from what's already known;
several have an explicit `story.hook: "TBD"` and/or open questions noted under `notes:` — those
are real gaps, not oversights, left for a design pass rather than invented): `lanes`, `orbits`,
`slings`, `skillshot`, `dropbank`, `aerial`, `portal`, `ramps`.
