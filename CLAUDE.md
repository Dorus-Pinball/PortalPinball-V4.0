# Portal Pinball V4.0 — Project Instructions

Project-specific detail only. The standing collaboration workflow (working modes, git/deploy
loop, documentation discipline, etc.) is inherited from the user's global `CLAUDE.md` — this file
just fills in what's specific to this machine.

## What this is

A real, physically-built pinball machine (Portal-themed) running **Mission Pinball Framework
0.80** (`config_version: 6`) on **OPP `gen2`** hardware, with a **mpf-gmc** (Godot 4) score
display. See `README.md` for the full stack breakdown and how to run it.

## Key facts

- Machine folder: `machinefolder/` (this is MPF's working directory — `cd` there before running
  `mpf`).
- Hardware config is split by concern: `config/hardware-basic.yaml`, `-switches.yaml`,
  `-coils.yaml`, `-leds.yaml`, `-devices.yaml`. Follow that convention for new hardware config
  rather than adding to one monolith.
- Modes live in `modes/<name>/config/<name>.yaml` (+ optional `slides/<name>.tscn`,
  `shows/*.yaml`). A mode must be added to `modes:` in `config.yaml` to actually load — check
  there when a mode "isn't doing anything."
- `data/audits.yaml` and `data/machine_vars.yaml` are MPF-managed runtime state, not
  hand-edited.
- The **physical machine is available for real-hardware testing** (not just virtual) — per the
  global workflow's "local success isn't done if a real deployment step exists" rule, verify
  config/logic changes on the actual cabinet, not only via `mpf`'s virtual platform, before
  calling something done.
- `board Overviews.xlsx` at the repo root is the hardware/design reference (board pinouts +
  early game-design notes) — check it before assigning new switch/coil numbers, to avoid
  colliding with something already planned there.
- **Starting/stopping `mpf` from a session (this includes Claude Code tool calls):** use
  `tools/mpf-session.ps1 -Action Start|Stop|Status|Log`, run via a PowerShell tool/shell, not
  Bash — plain `mpf` crashes its text UI in a non-interactive shell, and a Bash-tracked PID for a
  backgrounded Windows process doesn't match its real PID, so `kill` from Bash can silently miss
  a still-running session against real hardware. See the script's header comment for the full
  story. Always check with the user before a real-hardware `Start` (the script itself can't
  prompt — no interactive stdin).

## Current known gaps

Kept current in `TODO.md` — check there before assuming a feature (flippers, tilt, specific
modes) is wired up.
