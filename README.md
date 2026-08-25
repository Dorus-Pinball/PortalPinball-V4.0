# Portal Pinball V4.0

A real, physically-built pinball machine, Portal-themed, running on the **Mission Pinball
Framework (MPF)**.

## Stack

- **MPF 0.80** (`config_version: 6`) — the game logic / rules engine, Python. Config lives in
  `machinefolder/` as YAML.
- **OPP hardware platform**, `gen2` driver boards — real switches, coils, and addressable LEDs.
  Three serial chains:
  - `COM4` (chain 0) and `COM5` (chain 1) — Cobra boards, drive the LEDs (NeoPixel chains
    `NEO0`/`NEO1`).
  - `COM6` (chain 2) — a 4-board PSOC chain, handles all switches and coils
    (`2-0-x` through `2-3-x`).
- **mpf-gmc** (`machinefolder/addons/mpf-gmc`) — the score display, built on Godot 4. It's a
  separate process that talks to MPF core over BCP (a local socket protocol). Currently stock/
  unmodified beyond the two placeholder slides in `modes/base` and `modes/attract`.

`board Overviews.xlsx` at the repo root is the hardware planning reference — board pinouts per
wing, plus a "Modes" sheet of early game-design notes for the Portal-themed features (orbits,
ramps, lane spells, sling combos, skillshot, drop targets, an "aerial plate", and the game's
namesake ball-transfer "portal" feature).

## Running it

**Setup (one-time):** run `install.ps1` from the repo root — creates a `.venv` and installs
`mpf==0.80.0` into it (matches `config_version: 6` / the "MPF 0.80" comment in `config.yaml`).
See `plans/testing-strategy.md` for how this was verified.

**Virtual, no hardware/cabinet needed (recommended for dev):** from `machinefolder/`, run
`../.venv/Scripts/mpf -X -t -b`. `-X` forces the `smart_virtual` platform regardless of the
committed `platform: opp`, so no config edits are needed and nothing to accidentally leave
committed; it auto-simulates ball devices (trough eject, drop-target resets, etc.) so the ball
routing skeleton works with no manual switch toggling. `-t` disables MPF's console UI (needed in
non-interactive shells) and `-b` skips the BCP/Godot connection for a pure backend run — drop `-b`
to run the Godot mpf-gmc app alongside for a full display+audio playtest. `gmc.cfg`'s `[keyboard]`
section maps a few switches to number keys for manual testing; extend that mapping as more of the
game gets wired up in code.

**Automated tests, no manual interaction at all:** `.venv/Scripts/python -m unittest discover
tests` from the repo root. (Not `mpf test` — that command requires `kivy`/legacy `mpf-mc`, which
this project doesn't use.)

**Real hardware:** `../.venv/Scripts/mpf` (no `-X`) from `machinefolder/` — MPF uses the `opp`
platform from `config.yaml` and talks to the boards over `COM4`/`COM5`/`COM6`. Board/port
assignments can drift if USB enumeration changes — re-run MPF's hardware scan and compare against
the pasted scan output in `machinefolder/config/hardware-basic.yaml` if switches/coils stop
responding.

**Display:** open `machinefolder/` as a Godot 4 project (it autoloads `mpf_gmc.gd` per
`project.godot`) and run it alongside a running `mpf` instance — it connects over BCP
automatically.

## Layout

```
machinefolder/
  config/           # config.yaml + hardware-*.yaml (switches, coils, LEDs, ball devices)
  modes/<name>/
    config/<name>.yaml   # mode logic
    slides/<name>.tscn   # Godot slide for this mode
    shows/                # optional LED/sound shows
  data/             # audits.yaml, machine_vars.yaml (runtime state, not hand-edited)
  addons/mpf-gmc/   # the Godot display addon (stock)
  sounds/, images/  # currently placeholder assets, not final
tests/              # MpfTestCase/MpfGameTestCase suite - run with `python -m unittest discover tests`
design/             # story -> shots -> modes workflow + schema-tracked feature design docs
install.ps1          # one-time dev environment setup (.venv + mpf + jsonschema)
```

## Designing a new feature

See `design/README.md` for the workflow (story idea -> shots -> MPF mode) and the schema-tracked
design docs in `design/features/*.yaml` — this is the living source for feature design, replacing
`board Overviews.xlsx`'s "Modes" sheet going forward.

## Status

See `TODO.md` for known gaps and `CHANGES.md` for the project history. The full resumption
roadmap (phased plan covering flippers, rules architecture, feature modes, and display/audio) is
tracked separately with the project owner.
