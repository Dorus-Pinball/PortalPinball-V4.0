# Standard pinball moments

`design/SCREENS.md` flagged six standard pinball moments - `ball_start`/match, `tilt_warning`,
`ball_over`, `multiball_start`/jackpot, `game_over`, `high_score_entry` - as net-new, with no
owning design doc, since they aren't playfield "features" in the `design/features/` shots/
hardware sense. This is that design pass.

**Finding that reshapes the whole list**: MPF ships several of these as **built-in modes**
(`.venv/Lib/site-packages/mpf/modes/`: `attract, bonus, carousel, credits, game, high_score,
match, service*, tilt`), separate from the always-loaded baseline (`mpfconfig.yaml` hardcodes
`modes: [attract, game]` under every project, which is why `attract` already worked without
being in this project's own `config.yaml` `modes:` list). The others need to be added to
`config.yaml`'s `modes:` list to activate, but need little-to-no project-specific config beyond
that for most of them. This means most of this list is "wire up what MPF already provides," not
"design a mechanic from scratch."

## Per-moment status

### `ball_start` / match
Built-in `match` mode compares players' last-two-digits scores at game end and awards a free
game/credit. **Action**: add `match` to `config.yaml`'s `modes:` list. No new hardware or shots
needed. Presentation: `resumption-roadmap.md` Phase 4 already notes mpf-gmc ships its own match
slide in the addon's default `slides/` folder, currently unused - check that before building a
custom one.

### `tilt_warning`
MPF ships a `tilt:` device (config keys: `tilt_warning_switch_tag`/`tilt_slam_tilt_switch_tag`,
`warnings_to_tilt`, etc.) plus a built-in `tilt` mode. **Genuinely blocked**, not just
unregistered: `TODO.md` already flags no tilt switch exists in `hardware-switches.yaml` at all -
this needs the same physical-continuity/board-assignment pass as Phase 1 flippers before the
`tilt:` device config can be written for real (a DRAFT config without a real switch would be
pure guesswork, unlike flippers where the roadmap had already reasoned out real pin numbers).

### `ball_over`
Not a separate device/mechanic at all - `ball_will_end`/`ball_ended` are core MPF events that
already fire automatically as part of the ball_devices/game flow (used today, e.g., by the
existing `auditor:` config's `save_events`). This is a **presentation-only** moment: a transient
slide played on `ball_will_end`, no new rules needed. Add to `design/SCREENS.md`'s inventory
directly (transient overlay, trigger `ball_will_end`) once art exists - no rules work blocks it.

### `multiball_start` / jackpot
Not bundled as a default mode - built from a `multiball:` device (config keys: `ball_count`,
`shoot_again`, `enable_events`, etc.) plus a physical ball-lock mechanism. **Genuinely an open
design fork**, not just unregistered: `plans/resumption-roadmap.md` Phase 5 already notes this
depends on which ball-lock hardware ends up feeding it, and ties into the still-undecided wizard
mode shape (one big end-of-game mode vs. tiered mini-wizards, `portal` as the likely final key
either way). No action until that fork is resolved - tracked in Phase 5, not duplicated here.

### `game_over`
Same shape as `ball_over` - `game_ended` is a core event MPF already posts (game mode's own
lifecycle, no device needed). **Presentation-only** moment: a transient/persistent slide on
`game_ended`. Add to `design/SCREENS.md` directly once art exists.

### `high_score_entry`
Built-in `high_score` mode (initials entry, top-N tracking) exists and mpf-gmc ships a default
high_score slide in its own `slides/` folder (same "currently unused" note as match, per
`resumption-roadmap.md` Phase 5). **Action**: add `high_score` to `config.yaml`'s `modes:` list.
No new hardware needed - MPF's default initials-entry input handling works via the same keyboard/
switch input already in use for other testing.

## Summary of concrete next actions

- Cheap, unblocked, no design decisions needed: add `match` and `high_score` to `config.yaml`'s
  `modes:` list, and check whether mpf-gmc's bundled default slides for each are usable as-is
  before building custom ones.
- Presentation-only, no rules work: `ball_over` and `game_over` just need a slide once art
  exists - add both directly to `design/SCREENS.md`'s inventory.
- Genuinely blocked, not just undesigned: `tilt_warning` (needs a real tilt switch wired first,
  same class of gap as Phase 1 flippers) and `multiball_start`/jackpot (needs the ball-lock
  hardware + wizard-mode shape decided first, tracked in `plans/resumption-roadmap.md` Phase 5).
