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

**Virtual (no hardware needed):** from `machinefolder/`, run `mpf` — the config sets
`virtual_platform_start_active_switches` for the trough so a game can start immediately.
`gmc.cfg`'s `[keyboard]` section maps a few switches to number keys for manual testing; extend
that mapping as more of the game gets wired up in code.

**Real hardware:** same command, but MPF auto-detects the `opp` platform from `config.yaml` and
talks to the boards over `COM4`/`COM5`/`COM6`. Board/port assignments can drift if USB
enumeration changes — re-run MPF's hardware scan and compare against the pasted scan output in
`machinefolder/config/hardware-basic.yaml` if switches/coils stop responding.

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
```

## Status

See `TODO.md` for known gaps and `CHANGES.md` for the project history. The full resumption
roadmap (phased plan covering flippers, rules architecture, feature modes, and display/audio) is
tracked separately with the project owner.
