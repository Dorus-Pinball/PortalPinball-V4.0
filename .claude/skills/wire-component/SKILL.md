---
name: wire-component
description: Use when the user says they're wiring a specific Portal Pinball component now ("I'm wiring X", "let's assign numbers for X", "add X to the registry"), or asks to (re)assign a board/switch/coil/light number as part of the from-scratch rewire. Applies this project's CobraPin-first board-priority policy and the CobraPin/red-board pairing rules, and keeps hardware-*.yaml, tools/hw_console/data/components.yaml, wiring-guide.html, and TODO.md in sync in one pass.
---

# Wiring a component: process

This project (Portal Pinball V4.0) is being rewired from scratch: board/number assignments are
picked fresh, component by component, as each one is actually wired. This skill is the checklist
to follow every time so every component gets added the same consistent way, and a change in one
place propagates everywhere it needs to.

The rules this encodes live in **`docs/opp-hardware-reference.md`** — read that file first if
it's been a while, don't re-derive the rules from memory. This skill is the process; that doc is
the rulebook.

## Steps

1. **Identify the component.** Name it, and work out:
   - How many switches / coils / lights it needs.
   - Whether it's a **hardware-autofire device** (flipper/sling/pop-bumper-style — switch and
     coil linked as a hardware rule inside the controller) or **software-triggered** (a
     `ball_device`, `diverter`, plain switch, etc. — MPF fires it via an event, no hardware
     pairing constraint applies).

2. **Pick a board, in priority order** (`docs/opp-hardware-reference.md`'s policy section):
   - Lights → **always CobraPin** (chain 0 first, chain 1 if chain 0 is full).
   - Switches/coils → **CobraPin chain 0 first, then chain 1, then chain 2 (red boards) only if
     CobraPin genuinely can't fit it.**
   - Check current free capacity in `tools/hw_console/data/components.yaml`'s `boards:` section
     before proposing numbers — don't assume capacity, look it up.

3. **If it's a hardware-autofire device, apply the right pairing rule:**
   - **On CobraPin** (chain 0 or 1): switch and coil just need the same leading chain digit.
   - **On a red board** (chain 2+): switch and coil need the same chain *and* board, and the
     switch must fall in the coil's wing's own range — a coil in wing N (`4N..4N+3`) pairs only
     with a switch in `8N..8N+3`. See `docs/opp-hardware-reference.md` for why and worked
     examples from this project's own existing wiring.
   - If the coil is on CobraPin, also check `docs/opp-hardware-reference.md`'s per-pin table for
     which lettered bank (A/B/C) it's in, so its `+50V` lead gets wired from the matching
     `HV_A`/`HV_B`/`HV_C` feed — never a generic shared bus.

4. **Check for collisions before finalizing numbers.** Run:
   ```
   python tools/hw_console/check_registry.py
   ```
   (also fires automatically via a `PostToolUse` hook after editing the hardware config files —
   but run it explicitly here too, before you've committed to a number, not just after). It also
   reuses `tools/hw_console/registry.py`'s `check_collision()` — don't hand-pick a number without
   this check; don't reimplement collision detection ad hoc.

5. **Update, together, in the same pass** — this is what keeps everything in sync:
   - `machinefolder/config/hardware-switches.yaml` / `-coils.yaml` / `-leds.yaml` as applicable.
   - `machinefolder/config/hardware-devices.yaml` if a higher-level MPF device is needed
     (`autofire_coils:`, `flippers:`, `ball_devices:`, `diverters:`, `drop_targets:`, etc.).
   - `tools/hw_console/data/components.yaml` — add/update the component entry (board, numbers,
     status). This is what the hw_console UI and this skill both read as the live tracker.
   - `design/physical-checklists/wiring-guide.html` — update the board-map free/used counts and
     the component's row/sketch in its wiring table.
   - `TODO.md` — check off or update the relevant gap bullet if this closes one.

6. **Verify:**
   - `python tools/hw_console/check_registry.py` again — should report no violations.
   - Run `mpf` in virtual mode (`tools/mpf-session.ps1 -Action Start -Virtual -NoBcp` from a
     PowerShell tool/shell, not Bash — see the project `CLAUDE.md`) to confirm the config still
     loads clean.
   - If renumbering an existing entry, grep the repo for the old number to confirm nothing was
     missed.

7. **Commit** (standing git authorization from the project's collaboration workflow already
   covers this once tested/working — branch first if not already on a feature branch).

## Don't

- Don't hand-pick a number "because it looked free" without running `check_registry.py` — the
  free/used counts in `wiring-guide.html` and `components.yaml` can drift from reality mid-rewire.
- Don't put a new component's coil on a red board "because there's room" if CobraPin also has
  room — the project policy is CobraPin first, red boards last, no exceptions without asking.
- Don't assume a CobraPin bank's connector is unused just because the wiring-status looks clear —
  a bank's pins can be pre-broken-out to a terminal block without a coil actually being wired
  (see `docs/opp-hardware-reference.md`).
