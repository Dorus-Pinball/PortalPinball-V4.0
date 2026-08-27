# Portal Pinball V4.0 — Resumption Roadmap

## Context

Portal Pinball V4.0 is a real, physically-built pinball machine running on **Mission Pinball
Framework (MPF) 0.80**, OPP `gen2` hardware (2 Cobra LED-driver boards + a 4-board PSOC chain
for switches/coils), with **mpf-gmc** (Godot 4) driving the score display. The project had a
burst of real activity in Sept–Oct 2024 (hardware was scanned, wired, and play-tested for 23
real games — logs and `audits.yaml` confirm clean runs), then went dormant for ~22 months. The
last commit (`d8e97eb`, "small") only added a stray 126k-line log file and a binary bump — no
real work.

The goal is a comprehensive roadmap to resume the project: finish the hardware, replace the
placeholder single-shot-scoring logic with the actual Portal-themed ruleset that was sketched out
in `board Overviews.xlsx` (the "Modes" planning sheet) but never implemented, build out the
missing display/audio, and clean up the repo so future sessions don't lose context the way this
one did.

The machine is currently working partially and is available for real-hardware testing right now
— this is not blocked waiting on flippers, so every phase below (including Phase 0/2 work) can be
verified on the actual cabinet as it lands, not just virtually.

Flipper status (confirmed by user): **mechs are physically mounted in the cabinet and fully
functioning; the coils are dual-wound with a mechanical/self-contained EOS interrupter** (the EOS
contact lives inside the coil/linkage assembly itself and switches current from the main to the
hold winding purely electromechanically — it is *not* a switch wired back to the OPP board, so MPF
never sees it). Each flipper therefore only needs **one driver "gate" signal** — driver wiring to
the OPP boards and MPF config are incomplete. This is the single hardest gate blocking any real
playtesting, so it's Phase 1.

*Cross-checked against MPF's own docs*: the EOS-switches reference page describes exactly this
setup as the historical/EM-era pattern — "the EOS switch was a normally-closed switch connected in
series with the flipper cabinet button which activated the power winding," i.e. mechanically
gating only the power winding while the hold winding runs off the same activation signal, with no
controller visibility. MPF's modern `eos_switch`/`hold_coil`/`use_eos`/`repulse_on_eos_open`
options exist for boards that *do* wire the EOS switch back to the controller (for software cutoff
+ breakthrough detection) — since this hardware doesn't, those options don't apply, and
`main_coil`-only (Phase 1 below) is the correct MPF config. (Source:
`missionpinball.org/latest/config/flippers/` and the flipper EOS switches doc.)

Source material used to build this plan: all `machinefolder/config/*.yaml`, `modes/base` and
`modes/attract`, `machinefolder/data/{audits,machine_vars}.yaml`, `project.godot`, `gmc.cfg`,
the mpf-gmc addon (`mpf_game.gd`, slide/scene files — confirmed **stock/unmodified**, so no custom
Godot engineering has happened yet beyond placeholder slides), the sounds/images folders (contents
are **temp placeholder assets ripped from Left 4 Dead 2** — `mp_coop_lobby_2_*`, `sp_a4_finale4_*`
— not final), git history, a full extraction of `board Overviews.xlsx` (11 sheets: board pinouts
plus a "Modes" brainstorm sheet naming features like Orbit L/R, Sling Combo, a lane "spell" mechanic,
skillshot, drop targets/"insinerator", an "aerial plate", and the game's namesake **Portal
ball-transfer feature** — dropper → portal-r/m → exit-success, with 5 staged "exit open" LEDs), and
MPF's official documentation (`missionpinball.org/latest/`).

---

## Phase 0 — Repo hygiene & continuity docs (done)

**Why first:** cheap, reversible, and prevents this exact problem (a year+ gap with zero
documented context) from recurring.

- Added `logs/` to `machinefolder/.gitignore`; left existing git history alone (not rewritten) but
  stopped tracking the 158 existing log files going forward.
- Created the four standard docs at repo root (`README.md`, `TODO.md`, `CHANGES.md`, `IDEAS.md`)
  plus a project `CLAUDE.md`, seeded with everything learned during the resumption assessment.
- No code/config changes in this phase.

---

## Phase 1 — Flippers (hardware completion + MPF config)

**Goal:** machine is flippable again. This gates all real playtesting for every later phase.

1. **Board assignment.** Only **2 solenoid outputs** are needed (one gate per flipper — the
   main→hold transition happens mechanically inside the coil, invisible to the controller), plus
   2 switch inputs for the cabinet activation buttons. Per the PSOC chain pinout extracted from
   the xlsx, chain `2-1-x` (0–7) sits fully commented-out and unused in `hardware-coils.yaml`
   today — plenty of room. Activation switches need a free `2-1-x`/`2-3-x` switch slot the same
   way. Still needs a physical continuity check against the cabinet (which physical wing pins the
   flipper wiring actually lands on).
2. **Wire it** (physical task, outside this repo, but the resulting pin numbers feed directly
   into config).
3. **MPF config** — one coil per side, single `main_coil`, no `hold_coil`, no `eos_switch` (the
   controller has no visibility into the mechanical EOS at all, so nothing to configure for it):
   ```yaml
   coils:
     c-flipper-left:
       number: 2-1-0
       default_pulse_ms: 25
     c-flipper-right:
       number: 2-1-1
       default_pulse_ms: 25

   flippers:
     left_flipper:
       main_coil: c-flipper-left
       activation_switch: s-left-flipper
     right_flipper:
       main_coil: c-flipper-right
       activation_switch: s-right-flipper
   ```
   (Reuses the commented-out `flippers:` stub already sitting in `hardware-devices.yaml` — same
   shape, just filled in and trimmed to match the single-gate-per-side reality.)
4. **Verify on real hardware**: `mpf` connected to the boards, manual flip test both sides,
   listen/feel for the mechanical EOS engaging cleanly (a healthy click at end-of-stroke, no
   buzzing that would indicate it's not dropping to hold current), then update
   `hardware-basic.yaml`'s pasted hardware-scan comment block to reflect the new board state.

---

## Phase 2 — Rules architecture foundation

**Why before feature work:** `base.yaml` currently does flat `variable_player` scoring per
switch — fine for a bring-up test, not a real ruleset. Build the scaffolding every later feature
mode will lean on, once, rather than repeating ad hoc patterns per mode.

- **Ball save**: MPF's built-in `ball_save:` device (config keys: `active_time`, `grace_period`,
  `hurry_up_time`, `balls_to_save`, `auto_launch`, `eject_delay`, `only_last_ball`,
  `enable_events`/`disable_events`), armed via `enable_events: ball_starting` for a few seconds —
  the xlsx explicitly flags this as "not in shot yet."
- **Shots/shot_groups**: convert the raw switch-hit scoring in `base.yaml` into proper
  `shots:`/`shot_groups:` devices (lanes as a group, orbits as a group, etc.) — this is what
  unlocks "spell" mechanics (2x-hit-to-complete, tracked automatically by MPF's shot state) rather
  than hand-rolled counters.
  - `active_switches` `variable_player` block on `base.yaml` becomes lower-level scoring; shots
    layer on top for the higher-level rules and LED feedback.
- **Logic blocks** (`counters:`/`accruals:`/`sequences:`) for the multi-step things in the xlsx
  notes: `counters:` for the "count to 100" bonus and the "Step #" tally; **`accruals:`** (a logic
  block type not in the original assessment — requires switches hit *in order*, not just any N
  times) is a better fit than a generic counter for anything the xlsx implies is a
  left-to-right/sequenced shot (the `target-m1..m4` and `target-r1/r2`/`target-l1` rows read like
  an ordered target run, not an unordered set).
- **Achievements/achievement_groups** (an MPF device type not in the original assessment): a
  better structural fit than a bare logic block for the Phase 3 `portal` mode's 5-stage
  "exit-open" progression and for gating a Phase 5 wizard mode — each stage becomes an
  `achievement` (`enabled`→`started`→`completed`), and an `achievement_group` ties multiple
  Phase-3 features together as the wizard-mode gate, with built-in show/event hooks per state
  instead of hand-rolled event chains.
- **Service mode**: MPF ships one; just needs enabling + a couple of custom service-menu slides
  later in Phase 4. Cheap, high value for a machine that's about to get physically test-heavy
  again.
- **Tilt**: not currently configured at all (no tilt switch in `hardware-switches.yaml`). Flag as
  a hardware gap for the same physical-continuity pass as Phase 1's flipper wiring; add `tilt:`
  config once a switch exists.
- **Ball search** (not in the original assessment): not configured anywhere in the current
  config. This is a real gap independent of the above — without it, a ball stuck on a switchless
  part of the playfield stalls the machine instead of self-recovering. Most devices support
  `include_in_ball_search`/`ball_search_hold_time`/`ball_search_order`; add basic config alongside
  the shot_group work since it's cheap and this project is about to get physically test-heavy
  again.

Files: `modes/base/config/base.yaml` (restructured), new `machinefolder/config/rules-*.yaml` or
keep in mode-scoped files — match existing convention of one YAML per concern
(`hardware-*.yaml` split already establishes this project prefers small, named config files over
one monolith).

---

## Phase 3 — Feature modes (the actual game)

Each feature becomes its own mode under `machinefolder/modes/`, following the existing
`base`/`attract` pattern (`config/<name>.yaml` + `slides/<name>.tscn`), started/stopped by
shot-completion or switch events rather than always-on. This directly fulfills the `orbit` and
`lanes` entries already referenced (commented out) in `config.yaml`'s `modes:` list.

Each of these 8 features now has a living, structured design doc at `design/features/<name>.yaml`
(schema-validated by `tests/test_design_docs.py`, workflow documented in `design/README.md`) —
that's the current source for shots/rules/presentation detail on each one, superseding the prose
below and the xlsx notes it was drawn from. Use `design/README.md`'s workflow for any *new*
feature idea going forward, not just these 8.

Priority order, driven by wiring status (everything here already has switches/coils/LEDs mapped
in `hardware-*.yaml` today — no new hardware needed):

1. **`lanes`** — top lane (3) + bottom lane (5) shot groups with the "spell"/2x-hit mechanic
   noted in the xlsx ("Top Lanes Complete: spells... orange when hit 2x... blinking").
2. **`orbits`** — left/right orbit shots (`s-orbit-l/r`, `s-orbit-top`), reuses shot_group
   scaffolding from Phase 2.
3. **`slings`** — "Sling Combo" mechanic called out explicitly in the xlsx (back-to-back sling
   hits within a window).
4. **`skillshot`** — plunger-lane-into-lane-switch on `s-launch`/`s-plunger-lane`, one-shot at
   ball start.
5. **`dropbank`** — drop target bank completion (`db-dropbank` already exists as a device) firing
   the "insinerator" target/light and the extra target near the button (`s-button`,
   `s-target-l1`).
6. **`aerial`** — the "aerial plate" mechanic (`s-aerial`, `led-aerial`), currently just a switch
   with no logic.
7. **`portal`** — the namesake feature: ball dropper (`s-dropper`) → portal transfer
   (`s-portal-r`, `s-portal-m`) → success exit (`s-exit-success`), with the 5-stage
   `led-exit-open-1..5` progression from the xlsx as a Phase-2 achievement/logic block. This is
   the most involved mode (multi-switch ball-tracking state machine) — build it last, once the
   simpler shot-group pattern is proven out by lanes/orbits.
8. **Ramps** (`s-ramp-l1/2`, `s-ramp-r1/2`) — xlsx notes are sparsest here ("right ramp", a bare
   "?" placeholder); treat as lower priority / needs a design pass with the user before building.

`config.yaml`'s `modes:` list gets each new mode uncommented/added as it's built, not all at once
— keep the machine bootable after every step (tested increment by increment).

---

## Phase 4 — Display & audio

- **Replace placeholder assets.** Current sounds are Left 4 Dead 2 rips (`mp_coop_lobby_2_*`,
  `sp_a4_finale4_*`) and a single generic alarm sweep; images are one shared `mainscreen.jpg` used
  as background for both `base` and `attract` slides. Needs a real asset pass (sourced/licensed
  music+SFX) — a separate creative task, not something to auto-generate.
  **Update (2026-08-27)**: `mainscreen.jpg` is in fact Portal-themed (it quotes GLaDOS's Portal 2
  opening line) — the "none of this is Portal-themed" framing above was wrong about that image.
  Both the audio and `mainscreen.jpg` were explicitly kept rather than replaced: the user
  confirmed reuse is fine for this private, non-commercial project despite the licensing
  question. See `TODO.md`'s accepted-keeper notes. The 8 Phase 3 feature slides did get real
  (original) per-mode art, per the item below.
- **Per-mode slides**, mirroring the `modes/<name>/slides/<name>.tscn` pattern already
  established by `base` and `attract`: each Phase 3 mode gets its own slide/shot-callout instead
  of everything reusing the single background.
- **Shows**, mirroring `modes/attract/shows/laneshow.yaml`: LED shows per feature (the current
  attract-mode rainbow chase is themed as an obvious placeholder — same pattern extends to
  feature-complete flourishes, e.g. a portal-open LED chase across `led-exit-open-1..5`).
- **Service mode slides** (pairs with Phase 2's service mode enablement).

---

## Phase 5 — Progression / stretch goals

Only after Phases 1–4 give a genuinely playable machine:
- Bonus tally at ball end (xlsx mentions "count to 100"). **Done (2026-08-27)** - see TODO.md.
- Multiball (natural fit for the trough/plunger ball devices already in place).
- Wizard mode gated behind full Portal-feature completion, tying Phase 3's `portal` mode into a
  machine-wide payoff. Open design fork (from pinball design research, see
  `design/research/portal-themes-and-pinball-design.md` Part 2): real machines build this two
  ways — one big end-of-game wizard mode gated on all 8 Phase 3 features, or several tiered
  mini-wizard modes (2-3 features each) feeding one final "super" wizard mode. `portal`, as the
  namesake feature, is a natural choice for the final required key either way. Not decided yet —
  needs a deliberate choice before Phase 5 starts, not a default.
- High score / audits polish (audits.yaml already tracks basics; mpf-gmc ships bonus/high_score
  slides in the addon's own `slides/` folder, currently unused).

---

## Additional opportunities found in MPF documentation research

Beyond what the original assessment (based on this repo's own code + the xlsx) surfaced, reading
MPF's docs (`missionpinball.org/latest/`) turned up capabilities worth folding in:

- **`accruals:`** and **`achievements:`/`achievement_groups:`** — already folded into Phase 2/3
  above; these are purpose-built devices for exactly the ordered-target and staged-progression
  mechanics the xlsx sketches out, better than generic counters/hand-rolled event chains.
- **Ball search config** — a genuine gap (not previously flagged); folded into Phase 2 above.
- **MPF's unit testing framework** — MPF ships a real test framework for machine config/rules
  logic (independent of the cabinet or even the virtual keyboard platform). Worth adopting once
  Phase 2's shot/logic-block scaffolding exists, so rules regressions get caught without needing
  either the physical machine or a manual `mpf` run — a genuine addition to the Verification
  section below, not just a phase task.
- **`mpf format`/lint-style config tooling** — MPF's own config validation/formatting tools exist;
  worth a pass over the existing `hardware-*.yaml` files as part of Phase 0/2 hygiene, catching
  config mistakes before they reach the cabinet.
- **VPX / virtual pinball integration** — MPF supports driving a full virtual-pinball-table
  simulation (physics included), not just the keyboard/switch-toggle virtual platform already in
  use (`gmc.cfg`'s `[keyboard]` section). This is a meaningfully richer test loop for Phase 3
  feature-mode work — actual ball physics on shots/orbits/ramps — worth evaluating once a couple
  of Phase 3 modes exist, rather than relying solely on manual switch toggling.
- **Secondary/delayed/inverted/weak flipper types, magnets, diverters, servos/steppers** — all
  available in MPF but nothing in this machine's current hardware inventory calls for them; noted
  for completeness, not added to any phase.
- **High scores by category, bonus multipliers, multiball grace periods/add-a-ball** — confirms
  Phase 5's stretch goals are all natively supported, no custom code needed; `grace_period` in
  particular is directly relevant to a Phase 5 multiball built on the existing trough/plunger ball
  devices.

---

## Verification approach (applies to every phase)

- **Virtual-platform loop for logic work**: `hardware-basic.yaml` already sets
  `virtual_platform_start_active_switches` for the trough, and `gmc.cfg`'s `[keyboard]` section
  maps switches 1–4 to keys — extend that mapping as new switches come into play so each new mode
  can be exercised without the cabinet. Run `mpf` from `machinefolder/` after every config change;
  treat a clean startup log (no `ERROR`/`WARNING` beyond expected config-cache notices, matching
  the pattern seen in the last real session log) as the fast regression check.
- **Real hardware checkpoint before calling a phase done**: virtual success isn't done when a
  physical target exists. The cabinet is currently working partially and testable right now, so
  this isn't a future gate: every phase above, including Phase 0/2 config changes, should get an
  actual play test on the real machine as it lands, not just a virtual-platform run.
  `audits.yaml`/session logs are the evidence trail (same as the 23-game record from Sept 2024).
- **Godot side**: launch the mpf-gmc project and confirm each new slide/show renders against a
  running `mpf` instance (BCP connection) before marking a Phase 3/4 mode complete.
- **Unit tests**: see `plans/testing-strategy.md` for the full, verified design (a working local
  MPF install, `mpf -X -t -b` for interactive smart_virtual testing, and a real passing example
  `MpfGameTestCase` in `tests/`) — run without the cabinet or even a manual `mpf` launch,
  complementing rather than replacing the real-hardware checkpoint.
