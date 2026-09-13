# Wiring pin map

A single, readable reference of every component's current switch/coil pin assignments and
bring-up status, in one place — easier to scan than `tools/hw_console/data/components.yaml`'s
YAML or `design/physical-checklists/wiring-guide.html`'s interactive checklist.

**This is a snapshot, not the source of truth.** If it and another file disagree, the other file
wins:
- Real MPF pin numbers: `machinefolder/config/hardware-switches.yaml` / `hardware-coils.yaml` /
  `hardware-leds.yaml` / `hardware-devices.yaml`.
- Bring-up status, checklists, and the full history/notes behind each number (swaps, test
  results, root causes): `tools/hw_console/data/components.yaml`.
- The rules for picking a number in the first place (board priority, pairing rules, HV bank
  wiring): `docs/opp-hardware-reference.md`.
- The step-by-step physical bring-up checklist: `design/physical-checklists/wiring-guide.html`.

**Generated** by `tools/hw_console/generate_docs.py` from `components.yaml` +
`machinefolder/config/hardware-*.yaml` — do not hand-edit this file, it will be overwritten. Runs
automatically via the `PostToolUse` hook after those source files change, or manually:
`python tools/hw_console/generate_docs.py`.

Generated: 2026-09-13.

## Board map

Switch/coil/LED counts below are real, derived from `hardware-switches.yaml` /
`hardware-coils.yaml` / `hardware-leds.yaml` — not a hand-typed estimate. Remaining free capacity
per board isn't tracked as structured data anywhere in this repo (see `board Overviews.xlsx` or
physical inspection for that); this table only shows what's confirmed in use.

| Board | Port | Role | Switches in use | Coils in use | Reserved (off-limits) | LEDs in use |
|---|---|---|---|---|---|---|
| Chain 0 / Board 0x20 (Cobra LED driver) | COM4 | led-driver | 8 | 7 | 4 | 40 |
| Chain 1 / Board 0x20 (Cobra LED driver) | COM5 | led-driver | 0 | 0 | 0 | 1 |
| Chain 2 / Board 0x20 (PSOC card 0) | COM6 | psoc-switches-coils | 16 | 4 | 0 | 0 |
| Chain 2 / Board 0x21 (PSOC card 1) | COM6 | psoc-switches-coils | 16 | 1 | 0 | 0 |
| Chain 2 / Board 0x22 (PSOC card 2, incl. incandescent card) | COM6 | psoc-switches-coils-incand | 0 | 0 | 0 | 0 |
| Chain 2 / Board 0x23 (PSOC card 3) | COM6 | psoc-switches-coils | 20 | 0 | 0 | 0 |

Board-priority policy and CobraPin/red-board pairing rules: `docs/opp-hardware-reference.md`.

## Components

Status is the 1-6 build-lifecycle stage from `components.yaml`
(`registry.COMPONENT_STATUSES`): 1 idea · 2 hardware, no purpose · 3 hardware with a purpose,
not renovated · 4 renovated, not wired · 5 wired, not tested · 6 wired & tested.

| Component | Switches | Coils | Board(s) | Status |
|---|---|---|---|---|
| Slings (autofire) | s-left-sling 0-0-19, s-right-sling 0-0-25 | c-sling-left 0-0-12, c-sling-right 0-0-0 | chain0-0x20 | 6 — wired & tested |
| Ball saver post | s-ball-saver 0-0-24 | c-ball-saver 0-0-13 | chain0-0x20 | 6 — wired & tested |
| Pop bumpers (autofire) | s-popbumper-1 2-0-8, s-popbumper-2 2-0-9, s-popbumper-3 2-0-10 | c-popbumper-1 2-0-4, c-popbumper-2 2-0-5, c-popbumper-3 2-0-6 | chain2-0x20 | 4 — renovated, not wired |
| Plunger lane / auto-launch | s-plunger-lane 0-0-26 | c-plunger 0-0-10 | chain0-0x20 | 6 — wired & tested |
| Start / launch cabinet buttons | s-start 0-0-27, s-launch 0-0-3 | — | chain0-0x20 | 6 — wired & tested |
| Ball trough | s-trough1 2-1-16, s-trough2 2-1-17, s-trough3 2-1-18, s-trough4 2-1-19, s-trough5 2-1-20, s-trough6 2-1-21, s-trough-jam 2-1-22 | c-trough-eject 0-0-11 | chain0-0x20, chain2-0x21 | 4 — renovated, not wired |
| Drop target bank | s-drop1 2-1-23, s-drop2 2-1-24, s-drop3 2-1-25 | c-drop 2-0-7 | chain2-0x20, chain2-0x21 | 3 — hardware with a purpose, not renovated |
| Top lanes (3) | s-toplane1 2-0-19, s-toplane2 2-0-20, s-toplane3 2-0-21 | — | chain2-0x20 | 4 — renovated, not wired |
| Bottom lanes (5) | s-bottomlane1 2-0-22, s-bottomlane2 2-0-23, s-bottomlane3 2-0-24, s-bottomlane4 2-0-25, s-bottomlane5 2-0-26 | — | chain2-0x20 | 4 — renovated, not wired |
| Orbits (left/right/top) | s-orbit-l 2-0-28, s-orbit-r 2-0-27, s-orbit-top 2-1-28 | — | chain2-0x20, chain2-0x21 | 1 — idea, no hardware yet |
| Standup targets (E/R/M/L banks) | s-target-e1 2-0-29, s-target-e2 2-0-30, s-target-r1 2-3-0, s-target-r2 2-3-1, s-target-m1 2-3-2, s-target-m2 2-3-3, s-target-m3 2-3-4, s-target-m4 2-3-5, s-target-l1 2-3-6 | — | chain2-0x20, chain2-0x23 | 1 — idea, no hardware yet |
| Ramps (left/right, entry+exit) | s-ramp-r1 2-3-7, s-ramp-l1 2-3-8, s-ramp-r2 2-3-9, s-ramp-l2 2-3-10 | — | chain2-0x23 | 1 — idea, no hardware yet |
| VUKs (mid-field, top) | s-vukmid 2-1-26, s-vuktop 2-1-27 | — | chain2-0x21 | 1 — idea, no hardware yet |
| Portal ball transfer (dropper -> portal -> exit) | s-dropper 2-1-30, s-portal-r 2-1-29, s-portal-m 2-3-12, s-exit-success 2-1-31 | — | chain2-0x21, chain2-0x23 | 1 — idea, no hardware yet |
| Aerial plate / Insinerator target | s-aerial 2-3-11, s-insinerator 2-3-13 | — | chain2-0x23 | 3 — hardware with a purpose, not renovated |
| Cabinet action button | s-button 2-0-31 | — | chain2-0x20 | 4 — renovated, not wired |
| Flippers | s-left-flipper 0-0-1, s-right-flipper 0-0-2 | c-flipper-left 0-0-8, c-flipper-right 0-0-9 | chain0-0x20 | 6 — wired & tested |
| Right ramp diverter + subway | s-subway-entry 2-3-18, s-subway-exit 2-3-19 | c-ramp-diverter 2-1-2 | chain2-0x21, chain2-0x23 | 1 — idea, no hardware yet |
| Service mode nav switches | sw_service_enter 2-3-14, sw_service_esc 2-3-15, sw_service_up 2-3-16, sw_service_down 2-3-17 | — | chain2-0x23 | 1 — idea, no hardware yet |

Full history/notes (test results, swaps found during bring-up, root causes, open questions) live
per-component in `tools/hw_console/data/components.yaml` — this table only carries the current
numbers and a one-line status, not the story behind them.

## Lights

All LEDs are on Cobra chain 0 (`0-0-0`…`0-0-39`, `grb`), per the project's
board-priority policy (lights always go on CobraPin). Individual LED names/numbers aren't tracked
in `components.yaml` — see `machinefolder/config/hardware-leds.yaml` for the full list.

## Known gaps

Components whose notes flag an explicit `GAP:` in `components.yaml` — see `TODO.md` for full
detail and status:

- **VUKs (mid-field, top)**
- **Portal ball transfer (dropper -> portal -> exit)**
