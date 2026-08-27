# Screen (slide) catalog

This catalogs every display screen ("slide" in MPF/mpf-gmc terms) the game will eventually need,
and the architecture they follow. It exists so that when a feature mode gets built, its slide's
shape has already been decided here rather than improvised at build time. This is a planning
document only — no Godot scenes exist yet for anything beyond `base`/`attract`, and none are
created by this doc.

## How slides work here

The display runs on **mpf-gmc** (Godot 4), vendored at `machinefolder/addons/mpf-gmc`
(`0.1.0.dev2`, stock/unmodified — no bundled CHANGELOG or docs, so this section is derived
directly from its source). There's exactly one mechanism for authoring a slide:

- A slide is a hand-authored `.tscn` scene, root node `Control`, with the `mpf_slide.gd` script
  attached (class `MPFSlide`, extends `MPFSceneBase` — `addons/mpf-gmc/classes/mpf_slide.gd` /
  `mpf_scene_base.gd`).
- **File placement is the registration.** `GMCMedia.traverse_tree_for()`
  (`addons/mpf-gmc/scripts/media.gd`) recurses every `machinefolder/modes/<mode>/slides/` folder
  and builds a name -> path lookup keyed by filename. A scene named `foo.tscn` under a mode's
  `slides/` folder becomes playable as slide `foo` — no separate registry to update.
- **Wiring** happens in that mode's `config/<name>.yaml` via `slide_player:`, keyed by MPF event:
  ```yaml
  slide_player:
    mode_base_started: base
  ```
- **`MPFDisplay`** (`addons/mpf-gmc/classes/mpf_display.gd`) holds a **priority-sorted slide
  stack** per display, not a single "current slide" — this is what makes layered/transient
  overlays possible instead of one slide replacing another outright.
- Display resolution is 1900x1000 (`machinefolder/project.godot`).

## Architecture: persistent HUD + transient overlays

Two kinds of screen:

- **Persistent** — stays at the bottom of the slide stack for the duration of a game state:
  `attract` while idle, `base` while a ball is in play (score/ball/credits).
- **Transient overlay** — a short-lived, higher-priority slide pushed on top of whichever
  persistent slide is currently showing, for a feature hit or game moment. It expires itself
  after a few seconds via `slide_player`'s `priority`/`expire` keys, which pops it back off the
  stack and reveals the persistent slide underneath again — no manual "restore base" step needed.

  ```yaml
  slide_player:
    orbits_orbit_hit:
      orbit_hit:
        priority: 200
        expire: 2s
  ```

  `priority: 200` and `expire: 2s` above are **illustrative placeholders**, not verified values —
  no feature mode has been built yet to tune them against. Confirm/adjust once the first
  transient overlay is actually wired up and played on the display.

Each feature gets **bespoke** overlay content rather than one shared parameterized template:
every feature in `design/features/*.yaml` already has its own distinct `presentation.show` idea
(flame-wipe, portal-ring flash, spring-launch, etc.), so a shared template would just be building
toward throwing that specificity away later.

## Screen inventory

### Persistent

| Screen | Trigger | File | Notes |
|---|---|---|---|
| `attract` | attract mode start | `modes/attract/slides/attract.tscn` (exists) | Uses `images/mainscreen.jpg` deliberately (not a placeholder) — the user liked its moody atmosphere and confirmed reuse is fine for this private, non-commercial project despite it reading as Portal-themed fan art. Title label kept in the blue accent color. |
| `base` | `mode_base_started` | `modes/base/slides/base.tscn` (exists) | In-game HUD: score, ball, credits, on the same `mainscreen.jpg` background as `attract`. Score label kept in the orange accent color. |

### Feature-hit overlays (bespoke, one per `design/features/*.yaml` entry)

All transient, pushed over `base` during play. "Notes" column carries forward each feature's
own `presentation.show` idea so the visual direction isn't re-invented here.

| Feature | Planned file | Notes |
|---|---|---|
| `orbits` | `modes/orbits/slides/orbit_hit.tscn` | Portal-ring "pop" flash on the relevant orbit icon — **blue for left, orange for right**, per `STORY.md`'s Portal B/A color split. |
| `slings` | `modes/slings/slides/sling_hit.tscn` | Blue springy squash-and-bounce flash on the sling icon (Repulsion Gel motif). |
| `skillshot` | `modes/skillshot/slides/skillshot_hit.tscn` | Lit/rotating top lane pulses to show "this one counts" for the ball in play. |
| `dropbank` | `modes/dropbank/slides/dropbank_hit.tscn` | Fire/incinerator flame-wipe flash on the insinerator shot. |
| `lanes` | `modes/lanes/slides/lanes_hit.tscn` | Turret pop-up-and-topple animation per top-lane hit. |
| `aerial` | `modes/aerial/slides/aerial_hit.tscn` | Springboard/launch flash + brief ballistic-arc trail animation on hit. |
| `portal` | `modes/portal/slides/portal_transfer.tscn` | Portal-ring burn-open/close animation on transfer, then an LED-chase tie-in across the 5-stage exit-open progression. Most involved feature (multi-switch state machine) — build its slide last, per `design/README.md`'s note to prove the pattern out on simpler features first. |
| `ramps` | `modes/ramps/slides/ramps_hit.tscn` | Glowing "bridge extends" animation across the ramp icon while lit (Hard Light Bridge motif). |

### Standard pinball moments

See `design/GAME_MOMENTS.md` for the full design pass on these six. Key finding there: most are
**built into MPF already** (`match`, `high_score` are bundled default modes - just needed adding
to `config.yaml`'s `modes:` list, now done) rather than needing design from scratch.

| Screen | Likely trigger | Notes |
|---|---|---|
| `ball_start` / match | ball start | Built-in `match` mode now active; mpf-gmc ships a default match slide, unused. |
| `tilt_warning` | tilt warning event | Genuinely hardware-blocked (no tilt switch exists yet), not just undesigned. See `design/GAME_MOMENTS.md`. |
| `ball_over` | `ball_will_end` | Presentation-only - no device/rules work needed, just a slide once art exists. |
| `multiball_start` / jackpot | `multiball_mb-dropbank_started` | **Implemented (2026-08-27)**: `modes/multiball/slides/multiball_start.tscn` - user chose a dropbank tie-in (reuses `dropbank_hit.tscn`'s exact background tint/flame shape, 3 white ball circles bursting outward around it) over a feature-independent treatment. Rendered and visually verified in Godot 4.3 (headless, real Vulkan). |
| `game_over` | `game_ended` | Presentation-only, same as `ball_over`. |
| `high_score_entry` | new high score | Built-in `high_score` mode now active; mpf-gmc ships a default slide, unused. |

## Sequencing

A slide is only worth building once its feature mode is actually being implemented — this
document's job is to pre-decide *shape*, not to schedule the build, matching the project roadmap
(`CHANGES.md` #3) which sequences display/audio work after flippers, rules architecture, and
feature modes.

Once a feature's slide design here is confirmed against a real build, loop back and update that
feature's `design/features/<id>.yaml` `presentation.slide` field from `TBD` to reference this
catalog, instead of leaving the two out of sync.

## Open items

- All 10 screens now carry original vector iconography and per-screen palette (an aperture-iris
  mark for `attract`, a lit terminal frame for `base`, a distinct line-art icon per feature),
  approved first as a published Artifact ("Aperture Display Signage") before any `.tscn` file was
  touched — see each feature's `presentation.slide` note in `design/features/*.yaml` for the
  per-screen rationale. This is still short of final production art (hand-drawn/painted assets,
  animation), but has now been **rendered and visually verified** in Godot 4.3 (found installed
  on this machine) — one real rendering bug (dropbank's drop-target icons) was caught and fixed
  this way. See `TODO.md`.
- `priority`/`expire` values above are unverified guesses pending the first real feature-mode
  build and on-display test.
- The standard pinball moments listed above have no owning design doc yet — they'll need their
  own pass (possibly a `design/features/` entry each, or a lighter-weight doc, since they aren't
  playfield "features" in the shots/hardware sense) before they can move past being named here.
