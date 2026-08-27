# Testing Portal Pinball V4.0 without a machine connection

## Context

The resumption roadmap (`plans/resumption-roadmap.md`) calls for hardware checkpoints on every
phase, but that shouldn't be the *only* way to validate config/rules changes — especially once
Phase 2 (rules architecture) and Phase 3 (feature modes) start landing config-heavy changes that
are cheap to get subtly wrong. This is a concrete, verified design for testing this MPF machine
without needing the physical cabinet connected. It supersedes the one-line "Unit tests" bullet in
the main roadmap's Verification section.

**The local MPF install was broken when this investigation started**:
`C:\Users\dorus\.local\bin\mpf.exe` (on PATH) was a 0-byte stub file — nothing worked, virtual or
real hardware. Fixed as Tier 0 below. Every tier past Tier 0 has been run for real against this
repo's actual `machinefolder/` config (not just read about) — two claims from initial doc research
turned out to be wrong for the installed MPF 0.80.0 and are corrected inline below.

## Tier 0 — Local MPF install (done)

- `.venv/` at the repo root (gitignored), MPF **0.80.0** installed via `pip install mpf==0.80.0`
  — matches both the `config_version: 6` and the "MPF 0.80" comment in `config.yaml`, and supports
  Python 3.10–3.14 (this machine runs 3.14.6).
- Verified: `./.venv/Scripts/mpf --version` → `Mission Pinball Framework v0.80.0`.
- No mpf-mc/kivy package needed for normal use — this project's display is **mpf-gmc** (Godot),
  vendored in `machinefolder/addons/mpf-gmc`, not installed via pip. (Kivy *does* still matter for
  one specific thing — see the Tier 2 correction below.)

## Tier 1 — Interactive testing: smart_virtual + keyboard (verified working)

Verified command, run from `machinefolder/`:
```
../.venv/Scripts/mpf -X -t -b
```
- **`-X`** forces the **smart_virtual** platform regardless of the committed
  `hardware: platform: opp` in `config.yaml` — nothing to revert, no risk of a "test mode" config
  getting committed by accident. (`-x` gives plain `virtual`; `-X` is the smarter one that
  auto-simulates ball devices.)
- **`-t`** disables MPF's ASCII text UI (an `asciimatics`-based curses-style console). This is
  required in any non-interactive/piped terminal (it crashed with a Windows console-buffer error
  otherwise) and is also just the right choice for scripted/CI-style runs.
- **`-b`** skips the BCP connection attempt, for a pure backend run with no Godot needed. Drop
  `-b` to also run the Godot mpf-gmc app alongside for a full display+audio playtest loop — it
  connects over BCP automatically (stock/unmodified addon).
- **Confirmed clean boot**: full startup through `init_done`, `machine_reset_phase_1-3`, and into
  the `attract` mode run loop, with **zero ERROR/WARNING lines** in the run or in the generated
  `machinefolder/logs/*.log` file.
- **`gmc.cfg`'s `[keyboard]` block** covers manual switch presses for anything smart_virtual
  doesn't auto-drive (lane/target/orbit switches, flipper activation once Phase 1 lands) — today
  it only maps 4 switches (`s-trough1`, `s-start`, `s-plunger-lane`, `s-toplane1`). Extend this
  incrementally as each Phase 2/3 switch becomes part of active rules.

This tier is the fast-iteration replacement for "play it on the machine" during active
config/rules work — not a replacement for the real hardware checkpoint, but the thing to reach for
constantly in between.

## Tier 2 — Automated regression suite (verified working)

**Correction from initial doc research**: the `mpf test` CLI command unconditionally imports
`kivy` (`mpf/commands/test.py`) — it's built for MPF's own internal doc-test suite tied to the
legacy Kivy-based `mpf-mc`, and fails with `ModuleNotFoundError: No module named 'kivy'` in this
project (which correctly has no mpf-mc/kivy dependency). **Don't install kivy just to unblock
this** — `MpfTestCase`/`MpfGameTestCase` themselves have no kivy dependency at all; just run tests
the plain Python way instead:
```
./.venv/Scripts/python -m unittest discover tests
```
- First test written and passing: `tests/test_bringup.py` — starts a real game against the actual
  `machinefolder/config.yaml`, fills the trough, confirms ball 1 is in play, hits `s-toplane1`,
  and asserts the score reaches 100 (matches `base.yaml`'s `variable_player` config). **Verified
  green: `Ran 1 test in 0.271s / OK`.**
- Key API confirmed by reading the installed `mpf.tests.MpfTestCase`/`MpfGameTestCase` source
  directly (not just docs):
  - `get_machine_path()` / `get_config_file()` — override per test class. `get_machine_path()`
    must return an **absolute path** (verified: `tests/test_bringup.py` computes it from
    `os.path.dirname(__file__)`) — a relative path gets resolved against the *installed mpf
    package's* own directory, not the repo, which would silently point at the wrong place.
  - `get_platform()` — override to return `'smart_virtual'` (default is plain `'virtual'`).
    **Confirmed the test harness always sets `force_platform` from this method** regardless of
    `config.yaml`'s committed `platform: opp` — tests can never accidentally touch real hardware.
  - `hit_switch_and_run(name, delta)` / `release_switch_and_run(name, delta)` — simulate switch
    activity and advance the mocked clock in one call (no wall-clock waiting).
  - `mock_event(name)` / `assertEventCalled(name)` / `assertEventNotCalled(name)` /
    `post_event(name, run_time, **kwargs)` — event-based assertions.
  - `MpfGameTestCase` adds `fill_troughs()`, `start_game()`, `add_player()`,
    `assertBallNumber(n)`, `drain_one_ball()`/`drain_all_balls()`, `assertGameIsRunning()`, etc.
    for full game-flow tests using the real ball devices. `MpfFakeGameTestCase` exists for tests
    that only care about mode/logic-block behavior and don't want real ball-device friction.
- Write one file per feature area as Phase 2/3 build it out (e.g. `tests/test_ball_save.py`,
  `tests/test_lanes.py`, `tests/test_flippers.py`, `tests/test_portal.py`), each exercising the
  real production YAML — no duplicated test-only config.
- This tier runs with **no keyboard, no Godot, no manual anything** — the layer worth trusting for
  unattended regression checking (including in CI later, if this project ever wants that).

## Tier 3 — Config validation

**Correction from initial doc research**: there is **no `mpf format`/lint command in the installed
MPF 0.80.0** — the actual command set is `both`, `build`, `core`, `create_config`, `diagnosis`,
`game`, `hardware`, `init`, `service`, `test`, `wire` (verified by listing
`mpf/commands/*.py` directly). `wire` is FAST-platform-specific wiring-diagram tooling (not
relevant, this project uses OPP), and none of the others do YAML/schema linting.

In practice this doesn't leave a gap: MPF's config loader validates schema/typos as part of a
normal boot, so **Tier 1's clean-boot check already *is* the fast config-validation step** — a
bad config value fails immediately on `mpf -X -t -b`, before a game can even start. No separate
tool needed.

## Tier 2 addendum — gotchas found while writing the Phase 3-5 test suite (2026-08-27)

Real findings from writing ~30 additional tests across the feature/bonus/multiball/wizard-gate
work, kept here so they're not rediscovered the hard way again:

- **`MpfGameTestCase.fill_troughs()` overfills relative to `balls_installed`.** It activates
  *every* `ball_switch` configured on a trough device — for this project's `bd-trough` that's 7
  (`s-trough1-6` + `s-trough-jam`, a real trough capacity larger than the 4 balls actually
  installed), which conflicts with `hardware-basic.yaml`'s `balls_installed: 4` and confuses the
  ball controller's bookkeeping (logs "Found a new ball which was captured from playfield",
  known-ball count inflates past what the machine actually has). Any test that runs a full
  multi-ball-drain game needs a trimmed fill instead, matching
  `virtual_platform_start_active_switches`:
  ```python
  for name in ("s-trough1", "s-trough2", "s-trough3", "s-trough4"):
      self.hit_switch_and_run(name, 0)
  self.advance_time_and_run()
  ```
- **Launch each ball before draining it.** `bd-plunger` uses `mechanical_eject`, so a ball sits
  in the plunger lane (not the playfield) until `s-launch` is hit. Calling `drain_all_balls()`
  before that desyncs `playfield.available_balls`, and every later `ball_starting` hangs forever
  in `BallController.wait_until_playfields_are_empty()` (a silent hang, not an exception — watch
  for repeating "Playfields still contain balls" in the log). This was the root cause of an
  earlier "match/high_score can't be verified, test gets stuck" finding that turned out not to be
  a real bug at all.
- **`bd-plunger`'s eject onto the (switchless) playfield has no confirming switch**, so
  `confirm_eject_type: target` falls back to its ~10s default eject timeout before
  `playfield.balls` actually updates. A test that checks playfield ball count right after a
  launch needs to `advance_time_and_run(10+)` first, not just a couple seconds.
- **The `bonus` mode adds ~6s between a ball draining and the next one starting** once enabled
  (`display_delay_ms` × 3 steps at MPF's 2000ms default — bonus_start → entry → total → end).
  Any cross-ball test written before `bonus` was enabled needs its post-drain
  `advance_time_and_run()` budget bumped accordingly.
- **`disable_on_complete` defaults to `true` for every `logic_block`** (`counters:`/`accruals:`/
  `sequences:` — `mpf/config_spec.yaml`'s shared `logic_blocks_common`). A logic block that needs
  to complete more than once per ball (e.g. feeding a repeat-completion achievement chain) needs
  `disable_on_complete: false` explicitly, or it silently caps at one completion, ever, per mode
  instance.
- **`persist_state` defaults to `false` for every `logic_block`.** Progress that needs to survive
  across balls within the same game (e.g. a game-long feature-tier tracker) needs
  `persist_state: true` explicitly — the default resets every ball like a normal per-ball
  sequence.
- **`achievements:` DOES default a clean per-stage completion event**
  (`events_when_completed` → `achievement_<name>_state_completed`, filled in by
  `validate_and_parse_config` whenever not set explicitly) — don't assume only the generic
  `achievement_<name>_changed_state` event exists without checking the installed source first.
- **`achievement_group` is for player-selectable "pick one" mechanics** (rotation/random-select),
  not a fixed linear chain — chaining N plain `achievements:` by their own default completion
  events is the right tool for "stage 2 unlocks after stage 1 completes," not
  `achievement_group`.
- **`MpfTestCase.assertLightOn`/`assertLightOff` are broken for multi-channel `subtype: led`
  lights** in this MPF version — they read `light.hw_driver` (singular), which doesn't exist on
  RGB lights (`AttributeError: 'Light' object has no attribute 'hw_driver'` — it's `hw_drivers`,
  plural). Use `assertLightColor(name, "off")` / `assertLightColor(name, "on")` instead for any
  RGB light.
- **Calling `GMCMedia` (mpf-gmc's sound/slide registry) methods directly outside its normal
  scene-tree lifecycle hangs indefinitely** rather than erroring — tried this to verify
  `sound_player:` filenames resolve correctly in Godot (the audio equivalent of the slide
  screenshot-verification below) and it never completed after 10+ minutes of active CPU use, no
  output. Killed rather than debugged further. No verified way to check sound-name resolution
  without a real BCP-connected Godot session exists yet — unlike slides, audio also can't be
  visually confirmed from a screenshot, so this tier of verification currently just doesn't
  exist for sound.

## Tier 2.5 — Godot slide verification (verified working, real rendering)

MPF's own boot check (Tier 1) validates `slide_player:`/`show_player:` config syntax but never
actually renders a `.tscn` slide — that's mpf-gmc/Godot's job. Godot 4.3 is installed on this
machine (`C:\Program Files (x86)\Godot\Godot_v4.3-stable_win64_console.exe`), so a slide can be
rendered for real and reviewed as a screenshot:

```
Godot_v4.3-stable_win64_console.exe --path machinefolder --script capture.gd
```

where `capture.gd` (a `SceneTree`-extending script, not committed to the repo — write it to the
scratchpad per-use) loads the `.tscn`, instantiates it, waits a couple of `process_frame`s, and
saves `get_root().get_texture().get_image()` as a PNG. **Do not pass `--headless`** — that forces
a null/dummy renderer and produces blank textures; the plain (non-headless) console binary still
runs to completion non-interactively and renders for real via Vulkan. This caught one genuine
rendering bug during the original 10-slide art pass (`Line2D` closed-loop rectangles
triangulating incorrectly — switched to `ColorRect`) and was used again to verify the multiball
slide and iterate on an icon's scale/position (2026-08-27).

This only verifies *slides* (visual). The equivalent check for *sounds* does not currently exist
— see the `GMCMedia` finding in the Tier 2 addendum above.

## Tier 4 (optional, later) — Fuzz testing

MPF ships a fuzz-testing mode (`mpf/tests` includes fuzz-test infrastructure) that randomly hits
switches to shake out crashes/hangs that deliberate Tier 2 test cases wouldn't think to try. Worth
adding once the Tier 2 suite has enough real coverage to be worth stress-testing — not a day-one
item, not yet independently verified.

## Tier 5 (optional, heavier lift, not built here) — VPX integration

**Confirmed real**: `mpf game --help` shows a `--vpx` flag (`force_platform: virtual_pinball`),
so bridging to a Visual Pinball X table for actual ball-physics simulation is a real, one-flag-away
MPF capability — the most realistic non-cabinet test possible. It still requires building and
maintaining a VPX table file matching this machine's actual layout, which is a real design/asset
task in its own right. Flagged as a future option, intentionally not built as part of this design.

---

## What changed

- `.venv/` created and MPF 0.80.0 installed (gitignored via the repo-root `.gitignore` added
  alongside this work — Python's `venv` module also drops its own internal `.gitignore` inside
  `.venv/`, so it was already excluded either way).
- `tests/test_bringup.py` — first passing example test (Tier 2).
- `README.md` — "Running it" section corrected to match what was actually verified here (the venv
  setup, `mpf -X -t -b`, `python -m unittest discover tests`), replacing the previous text which
  assumed a working `mpf` install that didn't actually exist.
- `TODO.md` — broken `mpf.exe` stub checked off as fixed; the `mpf test`/kivy and `mpf
  format`-doesn't-exist corrections added so they're not rediscovered the hard way again.

## Verification

- Tier 0: `./.venv/Scripts/mpf --version` → `Mission Pinball Framework v0.80.0`. **Done.**
- Tier 1: `mpf -X -t -b` from `machinefolder/` boots to the `attract` mode run loop with no
  ERROR/WARNING in the console output or the generated log file. **Done.**
- Tier 2: `python -m unittest discover tests` from the repo root passes
  `tests/test_bringup.py::test_game_starts_and_scores` in well under a second. **Done — extend
  this suite alongside each new Phase 2/3 feature going forward.**
