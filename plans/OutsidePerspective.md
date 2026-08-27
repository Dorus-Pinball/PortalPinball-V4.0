# Outside Perspective: MPF Community Research

Dated 2026-08-27. This is an external research pass into the wider Mission Pinball Framework
(MPF) ecosystem — the official project, other hobbyists' published machine repos, community
forums, OPP-hardware experience, and general home-brew pinball design wisdom — done to bring
outside perspective into Portal Pinball V4.0. It is not a to-do list; it's raw material. Where a
finding maps cleanly onto something already open in this project (`TODO.md`, `design/features/`,
`tests/`), that's called out as a direct, actionable suggestion. Everything cited was actually
read via web search/fetch or GitHub's API during this pass — see References at the end.

## Official MPF project resources & docs

- **Core repos** (all under `github.com/missionpinball`): `mpf` (the game-logic engine this
  project runs), `mpf-mc` (legacy Kivy-based display, not used here), `mpf-gmc` (the Godot
  display this project uses), `mpf-examples` (a `mc_demo` bundle and other example configs),
  `mpf-docs` (source of the docs site — very useful to browse directly on GitHub since it's plain
  Markdown/YAML, not just the rendered site), `mpf-ls` (a Language Server Protocol implementation
  — syntax highlighting, autocomplete, diagnostics, go-to-definition for MPF's YAML configs in
  VSCode/IntelliJ/Emacs), and `mpf-wizard` (a GUI config tool). `mpf-ls` is still active-ish (last
  push 2024, small but real) and directly answers this project's `TODO.md` line "No `mpf
  format`/lint tool exists" (Phase 5/`CHANGES.md` entry 7) — it's not a formatter, but it is a
  linter/diagnostics tool for exactly this project's `.yaml` configs. Worth a spike: point it at
  `machinefolder/config/*.yaml` and see what it flags.
- **`config_version: 6` migration notes** confirm this project is on the current config format
  (MPF 0.57 moved v5→v6, removing legacy YAML "hacks"; 0.80 still uses v6) — nothing to act on,
  just confirms the project isn't on a stale format.
- **The "showcase" directory** (`mpf-docs/showcase/*.yaml`, ~84 entries) is a structured list of
  real, built MPF machines with `controller:`, `code_link:`, `documentation_link:` fields — the
  single best index for finding comparable real projects (used extensively below).
- **Built-in `tilt` mode** — MPF ships a complete tilt mode; you don't build one from scratch.
  Adding `tilt` to your machine's `modes:` list, tagging your tilt-bob switch `tilt_warning` and
  your slam-tilt switch `slam_tilt`, gets slam tilt / instant tilt / tilt-warnings-with-counter
  for free, including `warnings_to_tilt`, `settle_time`, and `multiple_hit_window` settings that
  can be exposed in service-mode operator settings. **Directly actionable**: `TODO.md`'s "Tilt: no
  tilt switch exists at all yet" gap is a hardware task, but once a switch exists, the MPF-side
  work is almost entirely `modes: [tilt]` plus two tags — there's no need to design tilt logic
  from scratch the way the Phase 3 features were.
- **Official skill-shot recipe** (`docs/game_logic/skill_shot.md`) implements a 3-lane skill shot
  where the lit lane **rotates via the flipper buttons** (`shot_groups: rotate_left_events:
  s_left_flipper_active` / `rotate_right_events: s_right_flipper_active`), using a
  `state_machine` to arbitrate success-vs-failure races and a `timers:` device tied to
  `balldevice_plunger_lane_ball_eject_success` for the timeout. **Directly actionable**: `TODO.md`
  flags exactly this — "a 'rotate which lane counts each ball' version was proposed but never
  signed off" for the skillshot design decision — and MPF's own documentation treats
  rotate-via-flippers as the standard pattern, complete with a full worked example and inline
  tests (`##! test` block). This de-risks that design decision considerably; it's a known-good MPF
  idiom, not a novel mechanic to invent.
- **Achievements vs. achievement_groups** (`docs/game_logic/achievements/`): achievements track a
  fixed goal per player (a light that goes off→flashing→on); `achievement_groups` add
  group-level behavior — picking a random member to highlight, cycling the selection (e.g. a pop
  bumper hit advances which Addams Family mansion award is lit), and firing an event when the
  whole group completes. This independently **confirms** `CHANGES.md` entry 5's finding that
  `achievement_group` was the wrong device for portal's fixed 5-stage `exit_open` chain — a group
  is for "pick one of several," not a linear sequence — so the project's earlier
  course-correction there matches how the framework's own authors describe the two devices.
- **Logic blocks "Common Issues" doc** explicitly covers the "my block only works once" gotcha
  (`reset_on_complete`/`disable_on_complete` both default in a way that makes one-shot the
  default) — directly relevant background for `TODO.md`'s open "repeat dropbank completion during
  an active multiball is currently a no-op" design question, since that's the same
  reset/disable-on-complete interaction playing out one level up (MPF's own multiball device
  guard, not logic-block state, but the mental model is the same).
- **Multiball "Common Issues"**: the ~10s pause when MPF adds a ball to the playfield during
  multiball is expected — the launcher waits for its `eject_timeouts` (ball_devices config)
  rather than a playfield-switch confirm, because that confirm method doesn't work with >1 ball in
  play. Worth remembering once the physical trough/multiball is wired and being playtested for
  real — a "slow" multiball ball-add may just be an untuned `eject_timeouts`, not a bug.
- **Field/Mission/Wizard mode-layering pattern** (`docs/game_design/mode_layering.md`) — a
  documented approach (not the only one, but a named one) to structuring growing rule sets:
  *Field modes* (non-intrusive, always running — accruals, qualifiers), *Mission modes* (partial
  takeover — one at a time, doesn't block multiball/pop-bumper progress), *Wizard modes* (full
  takeover). Three helper modes (`field.yaml`, `global.yaml`, `base.yaml`) manage the
  transitions between layers. **Actionable**: this project currently has `base`/`attract` plus 8
  Phase 3 feature modes and a `super_wizard` gate (`CHANGES.md` entries 4 and 6) — as more
  features stack up, this Field/Mission/Wizard split (and the accompanying priority-banding
  convention — keep ~100 points of separation between mode priorities so there's room to
  reorder later) is a reasonable model to adopt in `design/README.md` rather than inventing a
  layering scheme from scratch when it's next needed.
- **`docs/game_design/index.md`**'s whole "How to design a game in MPF using Modes" section (mode
  selection/startup, game mode, wizard modes, ball-end modes, game-end modes, other modes, mode
  layering) is worth a skim as a checklist against `design/README.md`'s story→shots→modes
  workflow — it's answering the same questions from the framework-author side.
- **MPF's own testing framework** (`MpfTestCase`, `MpfGameTestCase`, `MpfFakeGameTestCase`) is
  what this project's `tests/` already uses per the project's own `README.md`. One class this
  project doesn't currently seem to lean on: `MpfFakeGameTestCase`, which overrides
  `start_game()`/`drain_ball()` so you can test game logic without any ball devices configured at
  all — could be useful for fast, hardware-independent tests of pure rules logic (e.g. the sling
  combo window, dropbank escalation) that don't need the real trough-fill machinery `plans/
  testing-strategy.md` had to work around.

## Config & repo organization — what other real MPF machine repos do

Cross-referencing the showcase list's `controller:` field turned up several real, OPP-controller
machines with public repos — directly comparable hardware to this project (vs. the more common
FAST/P3-ROC/Cobrapin entries):

- **`deathsave/grand-prix`** (Grand Prix '86, OPP "Cypress" interface + CobraPin satellite board,
  a solid-state re-theme of a 1976 EM) is the most professionally organized repo found in this
  whole pass. Notable structure choices:
  - `docs/` is a full **mkdocs site** (published at `grandprix.bham.diy`), including
    `docs/logic/` — one Markdown file per feature (`extra-ball.md`, `multiplier.md`, etc.) with
    prose plus a **Mermaid flowchart** (`docs/logic/index.md`) showing how all the game's modes
    connect (Attract → Pit → Green Flag → three multiball-qualifying sub-modes → Red Line wizard
    mode). This is a close analogue to this project's `design/features/*.yaml` +
    `design/README.md` — the flowchart specifically is an idea worth stealing: a single Mermaid
    diagram in `design/README.md` showing how the 8 Phase 3 features and `super_wizard` connect
    would be a cheap, high-value addition, since right now that relationship lives only in
    scattered mode configs and `CHANGES.md` prose.
  - `config/` splits into `common.yaml`, `development.yaml`, `production.yaml` (plus
    `production_linux.yaml`/`production_macos.yaml`) rather than one monolithic config —
    environment-specific overrides layered on a shared base. This project's virtual-vs-real split
    is currently handled via the `-X` CLI flag rather than separate config files (per this
    project's own `README.md`), which is simpler and arguably fine at this scale, but worth
    knowing the alternative exists if OPP-vs-virtual config ever needs to diverge more than a
    platform flag can express.
  - `.github/workflows/python-app.yml` runs the test suite in **GitHub Actions on every push/PR**
    (installs system deps for Kivy/mpf-mc, pins `mpf==0.57.4`/`mpf-mc==0.57.1`, then runs
    `bin/test`). **Directly actionable**: this project has a real test suite
    (`python -m unittest discover tests`) but, as far as this research pass could tell from the
    project context, no CI running it automatically — a simple GitHub Actions workflow that
    installs `mpf==0.80.0` into a venv and runs the existing test command would catch regressions
    on every push for very little setup cost, and is a much lighter lift here than grand-prix's
    workflow since this project doesn't depend on Kivy/mpf-mc's heavy system deps.
  - A `code/` folder (`class_name.py`, `configure.py`) holds custom Python mode-code, separate
    from `modes/`, `config/`, `tests/` — a convention worth matching if/when this project needs
    custom Python code beyond what YAML config can express (it currently doesn't, per the
    project's own docs, but the pattern is there if needed).
- **`deathsave/combat`** (Zaccaria Combat conversion, same team) follows the same structural
  conventions — reinforcing that this is a deliberate house style, not a one-off.
- **`avanwinkle/masseffect2`** (Mass Effect 2, FAST controller, built by the same person who later
  wrote `mpf-gmc` — see below) documents a real gotcha for extracted-media projects: audio is
  pulled directly from the source game and deliberately **not committed to the repo**, requiring a
  `--no-sound` test flag. This project is in an analogous spot — `TODO.md`'s open item about the
  DRAFT sound allocation pulled from the user's own Portal 2 extract — worth double-checking that
  `tests/` (and CI, if added per above) don't assume those sound files are present, the way
  masseffect2 explicitly guards against.
- **`BENETNATH/mpf_dealers_choice`** ("Reviving an old EM pinball...with Open Pinball Project and
  Mission Pinball Framework") is a smaller, rougher, very relevant project: real OPP hardware, a
  hand-written `Ruleset.md` documenting two full rule layers (a "Classical" ruleset matching the
  original EM machine, and a "Modern" ruleset with 9 named missions) with `[X]`/`[ ]` checkboxes
  tracking what's actually implemented vs. still an idea. That checkbox-per-rule style is a
  lighter-weight alternative worth comparing against this project's schema-validated
  `design/features/*.yaml` approach — this project's YAML+JSON-schema approach is more rigorous,
  but the Dealer's Choice doc is a good reminder that a plain "done/not done" ruleset doc is
  legitimate too when a feature needs a quick scratch-pad before it's ready for the schema.

Other real, published repos found via the showcase list, noted for reference rather than deep
review: `mwseiden/metroid_pinball` (FAST), `wildertronix/zelda` (FAST), `bosh/trogdor-pinball`
(FAST Neuron, original theme, well-documented at `trogdorpinball.com`), `borgdog/Nobs` (OPP,
cribbage-themed original), `travisbmartin/powerman` (OPP, Bally Heavy Metal Meltdown conversion),
`Topedal/Charlies-Angels` (OPP, GTB Sys1 conversion, also runs on LISY).

## Testing & CI

Covered above under both official docs and `grand-prix`'s workflow — summarizing the concrete
takeaway: this project's test suite and testing discipline (per `plans/testing-strategy.md` and
`README.md`) already line up well with what MPF's own docs recommend (write tests incrementally
as config grows, don't wait until it "seems necessary"). The one clear gap found by comparison is
**no CI workflow running those tests automatically on push** — `grand-prix`'s `python-app.yml` is
a usable template, simplified since this project doesn't need mpf-mc's Kivy/SDL2/GStreamer system
dependencies.

## OPP hardware tips

- **`mpf hardware scan`** — MPF's official troubleshooting doc for OPP leads with this command,
  which prints exactly the kind of board/port map this project already keeps pasted into
  `hardware-basic.yaml` (per `README.md`'s note to "re-run MPF's hardware scan and compare against
  the pasted scan output" if boards drift). Confirms that workflow is the officially-recommended
  one, not an improvised one.
- **`opp: debug: true`** in machine config enables verbose OPP-layer debug logging (at a
  performance cost — recommended to remove after debugging). Useful to know exists next time a
  board/switch mapping mystery comes up during real-hardware bring-up (flippers, diverter, tilt —
  all currently blocked per `TODO.md`).
- **`poll_hz:`** under `opp:` (default 100) can be lowered if the processor boards can't keep up
  with MPF's poll rate — but the doc explicitly warns lowering it risks missing fast double-hits,
  so it's a last resort, not a default tuning knob.
- **Windows COM port gotcha**: ports above `COM9` may need the `\\.\COM10` long form in `ports:`
  rather than the plain name — worth remembering if `COM4`/`COM5`/`COM6` ever need to move to a
  higher-numbered port after a USB re-enumeration (this project's `README.md` already flags port
  drift as a known risk).
- **`pinballmakers.com`'s OPP wiki page** (community-maintained, not MPF's own docs) fills in the
  electrical side MPF's docs deliberately don't cover: OPP gen2 moved from PSoC4200 chips to
  STM32F103C8T6 "blue pill" boards; each processor supports up to 4 Wing boards; solenoid wings
  are ground-sink MOSFET, 24-70V, need 4004-type flyback diodes across every coil; incandescent
  wings need a separate 6.3V@10A supply; and critically, **all grounds must be tied together at
  the power supplies** to avoid floating-ground board damage. Worth a checklist pass against this
  project's actual wiring once the flipper/diverter coil work resumes (`TODO.md`'s "Board number
  confirmation" and flipper items).
- **Google Groups `mpf-users`** OPP-specific threads turned up one hardware-rule gotcha
  specific to multi-CPU boards (relevant if this project's 4-board PSOC chain has similar
  constraints): **a driver and the switch that triggers it via a hardware rule (e.g. flipper EOS,
  autofire coils) must live on the same physical board/CPU** — OPP/CobraPin hardware rules don't
  cross CPU boundaries, so a flipper switch and its coil being on different boards in the chain
  will silently fail to produce a working hardware rule. Directly relevant to the still-open
  flipper wiring task in `TODO.md` — worth confirming switch and coil board assignment land on
  the same board before wiring, not just that both exist somewhere on the `2-x-x` chain.
- The Google Group is described (via search) as **not very active these days** — most hardware
  vendors have moved to private Slack/Discord channels — so it's better used as a searchable
  archive of past problems than a place to expect a fast live answer.

## Display: mpf-gmc/Godot vs. mpf-mc/Kivy

This is a genuinely under-populated area, worth reporting honestly rather than padding:

- **mpf-gmc is new and still niche.** It was created by Anthony van Winkle (the same person
  behind the Mass Effect 2 pinball project above, and `masseffectpinball.com`) as a Godot-based
  replacement for the legacy Kivy-based `mpf-mc`. As of this research pass it's described in
  MPF's own materials as "early-access development" — core functionality works, but rough edges
  are expected and user feedback is explicitly how it improves. None of the ~84 machines in the
  official showcase list reference Godot or GMC by name; every showcase entry with a visible
  `controller:` is paired with the older mpf-mc/Kivy stack as far as this pass could tell. That
  makes this project one of relatively few real, physically-built machines adopting GMC this
  early — useful to know going in: **expect to be closer to the edge of what's been battle-tested
  than a typical MPF choice**, and that filing issues/feedback against `mpf-gmc` when something
  doesn't work is genuinely useful to the tiny pool of people using it, not just noise.
- One second-hand data point from a Godot Asset Library / community listing (`gadgetgodot.com`)
  describes a user's experience as "about 1000x easier...to do everything related to making good
  slides than the previous MC" — anecdotal and unverified, but consistent with GMC's stated goal
  (visual, drag-and-drop slide editing vs. Kivy's `.kv` files).
  - **Actionable**: given how thin the community track record is, treat the official GMC docs
    (`missionpinball.org/latest/gmc/setup/`, `.../installation/`) as closer to a primary source
    than "ask the community" for anything nonstandard — the setup flow (window/scene config, audio
    bus setup, attract slide, keymap) matches what this project's `gmc.cfg`/`modes/base`/
    `modes/attract` already implement per this project's own `README.md`, which is a good sign
    it's following the documented path rather than improvising against a moving target.

## Show/slide authoring workflow

Coverage here was thinner than the other themes — MPF's own docs give one clear rule worth
carrying forward: **put a show in its own file once it gets non-trivial; keep small, one-off shows
inline** in the mode/machine config that uses them. This project's `modes/<name>/shows/*.yaml`
convention (per this project's own `README.md`) already matches that default. The one YAML
authoring gotcha worth flagging for anyone hand-editing shows: MPF's list syntax needs a **space
after the hyphen** (`- type: text`, not `-type: text`) — a silent-failure-prone typo class in
YAML generally, not specific to this project, but worth a quick manual/lint pass over
`shows/*.yaml` given `mpf-ls` (above) could catch this class of error automatically once
integrated.

## Rules & mode design ideas

**From official MPF game-design docs** (see also "Config & repo organization" above for the
Field/Mission/Wizard layering pattern and the rotate-lane skillshot recipe, both repeated here for
visibility since they're the two most directly actionable findings of this whole pass):

- The rotate-via-flippers skillshot pattern is MPF's own documented idiom for exactly the
  "rotate which lane counts each ball" mechanic flagged as an unconfirmed design decision in
  `TODO.md`.
- Field/Mission/Wizard mode layering, with ~100-point priority bands between mode tiers, is a
  named pattern for the kind of growth this project is already partway through (base/attract →
  8 feature modes → `super_wizard`).

**From general home-brew pinball design wisdom** (not MPF-specific):

- "Flow" — the ability to combo from shot to shot via inlanes/orbits feeding back into
  playable positions — came up repeatedly in community design-theory discussion as the thing
  that separates games that feel good from games that are just a list of shots with scores
  attached. Worth keeping in mind for the still-open ramp-diverter routing design question in
  `TODO.md` (what a diverted shot actually does) — a diverter is exactly the kind of mechanism
  that can either add flow (feeding back into a comboable position) or kill it (routing to a dead
  stop), and that's a design axis worth weighing explicitly, not just "what does it award."
- Classic combo-scoring convention: consecutive shots within a short window (commonly 3-5s)
  scoring progressively more (2x, 3x, ...). This project's sling-combo window (`CHANGES.md` entry
  5's `timers:`-based 3s sliding window) already lands squarely in that convention — good
  external validation that the DRAFT window length, while unbalanced, is the right shape of
  mechanic.
- Pat Lawlor-style thematic tie-ins (mode-specific physical/sensory changes, like Earthshaker's
  shaker motor during its mode) are a recurring theme in what makes homebrew rulesets feel
  designed rather than generic — worth keeping in mind for `super_wizard`'s still-undesigned real
  payoff (`TODO.md`: "what the wizard-mode payoff should actually involve...is still open").
- The `BENETNATH/mpf_dealers_choice` `Ruleset.md` (above) is a real example of a two-tier ruleset
  (a "faithful to the original" layer plus a "new modern layer" unlocked by a flipper-button
  hold at game start) — a pattern this project could consider if it ever wants a
  toggle between "classic Portal scoring" and an expanded ruleset, though nothing in the current
  project context suggests that's needed now.

## Community resources & where to ask questions

- **Google Groups `mpf-users`** — public, searchable, permanent, good for archived Q&A
  (especially OPP-specific threads), but not where to expect a fast live answer; described via
  search as less active now that most hardware vendors run their own private Slack/Discord
  channels.
- **GitHub Discussions on `github.com/orgs/missionpinball`** — where current MPF dev
  conversations and bug discussion actually happen now, per the official community page.
- **Pinside.com's "Homebrew pinball" and "Boutique pinball" subforums** — the most active
  general locus for MPF/OPP builder discussion found in this pass; several of the showcase-listed
  machines above (Grand Prix '86, Dealer's Choice, Charlie's Angels, Cuphead, etc.) link their
  primary build-log/support thread there rather than to GitHub Issues. Worth treating as the
  default place to search before assuming a question is novel.
- **The showcase directory itself** (`github.com/missionpinball/mpf-docs/tree/main/showcase`) is
  underused as a discovery tool — searching it by `controller:` (as done in this pass) is a fast
  way to find real repos on comparable hardware, and could be worth returning to later (e.g. once
  the physical diverter/flippers/tilt are wired) to look for how OPP builders specifically solved
  similar hardware problems.

## References

Official MPF project:
- [missionpinball/mpf](https://github.com/missionpinball/mpf) — core engine repo
- [missionpinball/mpf-mc](https://github.com/missionpinball/mpf-mc) — legacy Kivy media controller
- [missionpinball/mpf-gmc](https://github.com/missionpinball/mpf-gmc) — Godot media controller this project uses
- [missionpinball/mpf-examples](https://github.com/missionpinball/mpf-examples) — official example/demo configs
- [missionpinball/mpf-ls](https://github.com/missionpinball/mpf-ls) — MPF config language server (lint/autocomplete)
- [missionpinball/mpf-wizard](https://github.com/missionpinball/mpf-wizard) — GUI config tool
- [missionpinball org repositories list](https://github.com/orgs/missionpinball/repositories)
- [config_version 6 migration notes](https://missionpinball.org/latest/config/instructions/config_v6/)
- [MPF mode: config reference](https://missionpinball.org/latest/config/mode/)
- [Playfield layout considerations](https://missionpinball.org/latest/physical_building/layout_considerations/)
- [GMC setup guide](https://missionpinball.org/latest/gmc/setup/)
- [GMC installation guide](https://missionpinball.org/latest/gmc/installation/)
- [Godot Media Controller overview](https://missionpinball.org/latest/gmc/)
- [mpf-docs: docs/machines/homebrew.md](https://raw.githubusercontent.com/missionpinball/mpf-docs/main/docs/machines/homebrew.md) — homebrew control-system/power/parts guidance
- [mpf/docs/testing/writing_machine_tests.rst](https://raw.githubusercontent.com/missionpinball/mpf/dev/docs/testing/writing_machine_tests.rst)
- [developer.missionpinball.org testing docs](https://developer.missionpinball.org/en/dev/testing/) (via search snippet: MpfTestCase/MpfGameTestCase/MpfFakeGameTestCase)
- [mpf-docs: docs/hardware/opp/index.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/index.md)
- [mpf-docs: docs/hardware/opp/troubleshooting.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/troubleshooting.md) — hardware scan, debug:true, poll_hz
- [mpf-docs: docs/hardware/opp/connecting.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/connecting.md)
- [mpf-docs: docs/hardware/opp/config.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/config.md) — Windows COM10+ port format
- [mpf-docs: docs/game_logic/skill_shot.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/skill_shot.md) — rotate-lane skillshot recipe
- [mpf-docs: docs/game_logic/tilt/index.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/tilt/index.md) — built-in tilt mode
- [mpf-docs: docs/game_logic/logic_blocks/common_problems.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/logic_blocks/common_problems.md)
- [mpf-docs: docs/game_logic/achievements/index.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/achievements/index.md)
- [mpf-docs: docs/game_logic/achievements/achievement_groups.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/achievements/achievement_groups.md)
- [mpf-docs: docs/game_logic/multiballs/index.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/multiballs/index.md) — eject_timeouts common issue
- [mpf-docs: docs/game_design/index.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_design/index.md) — "How to design a game in MPF using Modes"
- [mpf-docs: docs/game_design/mode_layering.md](https://github.com/missionpinball/mpf-docs/blob/main/docs/game_design/mode_layering.md) — Field/Mission/Wizard layering pattern
- [mpf-docs: showcase/ directory](https://github.com/missionpinball/mpf-docs/tree/main/showcase) — ~84 real MPF machines with controller/code_link metadata (queried programmatically via GitHub API for this pass)

Real hobbyist MPF machine repos:
- [avanwinkle/masseffect2](https://github.com/avanwinkle/masseffect2) — Mass Effect 2, FAST, extracted-audio gotcha; built by mpf-gmc's author
- [masseffectpinball.com](https://masseffectpinball.com) — project site
- [deathsave/grand-prix](https://github.com/deathsave/grand-prix) — Grand Prix '86, OPP/CobraPin, mkdocs docs site, CI, mermaid mode-flow diagram
- [deathsave/combat](https://github.com/deathsave/combat) — Zaccaria Combat conversion, OPP, same team/conventions
- [BENETNATH/mpf_dealers_choice](https://github.com/BENETNATH/mpf_dealers_choice) — Dealer's Choice EM revival on OPP, checkbox-tracked Ruleset.md
- [borgdog/Nobs](https://github.com/borgdog/Nobs) — original cribbage-themed machine, OPP
- [travisbmartin/powerman](https://github.com/travisbmartin/powerman) — Powerman 5000 conversion, OPP
- [Topedal/Charlies-Angels](https://github.com/Topedal/Charlies-Angels) — GTB Sys1 conversion, OPP
- [mwseiden/metroid_pinball](https://github.com/mwseiden/metroid_pinball) — Metroid, FAST
- [wildertronix/zelda](https://github.com/wildertronix/zelda) — Zelda, FAST
- [bosh/trogdor-pinball](https://github.com/bosh/trogdor-pinball) — Trogdor, FAST Neuron, original theme

OPP hardware / community:
- [pinballmakers.com OPP wiki page](https://pinballmakers.com/wiki/index.php?title=OPP) — board types, gen2 STM32 details, grounding/flyback-diode wiring rules
- [openpinballproject GitHub org](https://github.com/openpinballproject)
- [Google Groups mpf-users](https://groups.google.com/g/mpf-users) — community mailing list archive
- [mpf-users: CobraPin arbitrary switch/coils firing](https://groups.google.com/g/mpf-users/c/4CujstYuaHI) (via search snippet — same-board hardware-rule requirement)
- [mpf-users: Revive an EM pinball with OPP and MPF](https://groups.google.com/g/mpf-users/c/C6n6ZnNYYAk) (via search snippet)

Display (GMC/Godot):
- [Godot Asset Library: GMC listing](https://godotengine.org/asset-library/asset/3125)
- [gadgetgodot.com: GMC user note](https://www.gadgetgodot.com/u/avanwinkle/gmc-media-controller-for-mpf) (via search snippet — "1000x easier" anecdote)

Community / general design wisdom:
- [Pinside: Homebrew pinball forum](https://pinside.com/pinball/forum/forum/homebrew-pinball) — general locus for MPF/OPP build discussion
- [Pinside: Design Theory Discussion 1: Flow](https://pinside.com/pinball/forum/topic/design-theory-discussion-1-flow) (found via search snippet; full thread not retrievable, 403)
- [Pinside: Homebrew hardware platforms pros and cons](https://pinside.com/pinball/forum/topic/homebrew-hardware-platforms-pros-and-cons) (via search snippet; full thread not retrievable, 403)
- [Wikipedia: Firepower (pinball)](https://en.wikipedia.org/wiki/Firepower_(pinball)) — first solid-state multiball
- [Wikipedia: Pat Lawlor](https://en.wikipedia.org/wiki/Pat_Lawlor) — thematic mode design examples
