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
