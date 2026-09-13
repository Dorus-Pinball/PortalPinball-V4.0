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

Update this file in the same pass as those, per `.claude/skills/wire-component/SKILL.md` — it's
a companion snapshot, not a replacement for keeping `components.yaml` as the live tracker.

Last updated: 2026-09-13.

## Board map

| Board | Port | Chain | Role |
|---|---|---|---|
| chain0-0x20 (Cobra A) | COM4 | 0 | LED driver + spare switch/coil I/O — 1st choice for new wiring |
| chain1-0x20 (Cobra B) | COM5 | 1 | LED driver + spare switch/coil I/O — 2nd choice |
| chain2-0x20 (PSOC card 0) | COM6 | 2 | Switches + coils — fallback only |
| chain2-0x21 (PSOC card 1) | COM6 | 2 | Switches + coils — fallback only |
| chain2-0x22 (PSOC card 2, incl. incandescent) | COM6 | 2 | Switches + coils + incand — fallback only |
| chain2-0x23 (PSOC card 3) | COM6 | 2 | Switches + coils — fallback only |

Board-priority policy and CobraPin/red-board pairing rules: `docs/opp-hardware-reference.md`.

## Components

Status is the 1-6 build-lifecycle stage from `components.yaml` (`registry.COMPONENT_STATUSES`):
1 idea · 2 hardware, no purpose · 3 hardware with a purpose · 4 renovated, not wired · 5 wired,
not tested · 6 wired & tested.

| Component | Switches | Coils | Board(s) | Status |
|---|---|---|---|---|
| Flippers | s-left-flipper 0-0-1, s-right-flipper 0-0-2 | c-flipper-left 0-0-8, c-flipper-right 0-0-9 | chain0-0x20 (Cobra) | 6 — wired & tested |
| Start / launch buttons | s-start 0-0-27, s-launch 0-0-3 | — | chain0-0x20 (Cobra) | 6 — wired & tested |
| Plunger lane / auto-launch | s-plunger-lane 0-0-26 | c-plunger 0-0-10 | chain0-0x20 (Cobra) | 6 — wired & tested |
| Slings (autofire) | s-left-sling 0-0-19, s-right-sling 0-0-25 | c-sling-left 0-0-12, c-sling-right 0-0-0 | chain0-0x20 (Cobra) | 6 — wired & tested |
| Ball saver post | s-ball-saver 0-0-24 | c-ball-saver 0-0-13 (40ms pulse) | chain0-0x20 (Cobra) | 6 — wired & tested (no game logic yet) |
| Pop bumpers (autofire) | s-popbumper-1/2/3 2-0-8/9/10 | c-popbumper-1/2/3 2-0-4/5/6 | chain2-0x20 | 4 — not yet wired |
| Ball trough | s-trough1-6 2-1-16…21, s-trough-jam 2-1-22 | c-trough-eject 0-0-11 | chain2-0x21 / chain0-0x20 (Cobra) | 4 — coil tested, switches blocked on opto repair |
| Drop target bank | s-drop1/2/3 2-1-23…25 | c-drop 2-0-7 | chain2-0x21 / chain2-0x20 | 3 — hardware with a purpose, not renovated |
| Top lanes (3) | s-toplane1/2/3 2-0-19…21 | — | chain2-0x20 | 4 — not yet wired |
| Bottom lanes (5) | s-bottomlane1-5 2-0-22…26 | — | chain2-0x20 | 4 — not yet wired |
| Cabinet action button | s-button 2-0-31 | — | chain2-0x20 | 4 — not yet wired |
| Aerial plate / Insinerator | s-aerial 2-3-11, s-insinerator 2-3-13 | — | chain2-0x23 | 3 — hardware with a purpose, not renovated |
| Orbits (left/right/top) | s-orbit-l 2-0-28, s-orbit-r 2-0-27, s-orbit-top 2-1-28 | — | chain2-0x20 / chain2-0x21 | 1 — idea, no hardware yet |
| Standup targets (E/R/M/L) | s-target-e1/e2 2-0-29/30, s-target-r1/r2 2-3-0/1, s-target-m1-4 2-3-2…5, s-target-l1 2-3-6 | — | chain2-0x20 / chain2-0x23 | 1 — idea, no hardware yet |
| Ramps (L/R, entry+exit) | s-ramp-r1/l1/r2/l2 2-3-7…10 | — | chain2-0x23 | 1 — idea, no hardware yet |
| VUKs (mid-field, top) | s-vukmid 2-1-26, s-vuktop 2-1-27 | **missing** — GAP | chain2-0x21 | 1 — switches wired, no eject coil configured |
| Portal transfer (dropper→portal→exit) | s-dropper 2-1-30, s-portal-r 2-1-29, s-portal-m 2-3-12, s-exit-success 2-1-31 | **dropper coil missing** — GAP | chain2-0x21 / chain2-0x23 | 1 — switches configured, dropper's release mechanism not wired |
| Right ramp diverter + subway | s-subway-entry/exit 2-3-18/19 | c-ramp-diverter 2-1-2 | chain2-0x23 / chain2-0x21 | 1 — DRAFT numbers, not wired for real |
| Service mode nav switches | sw_service_enter/esc/up/down 2-3-14…17 | — | chain2-0x23 | 1 — DRAFT numbers, not wired for real |

Full history/notes (test results, swaps found during bring-up, root causes, open questions) live
per-component in `tools/hw_console/data/components.yaml` — this table only carries the current
numbers and a one-line status, not the story behind them.

## Lights

All 40 LEDs are on Cobra chain 0 (`0-0-0`…`0-0-39`, `grb`), per the project's board-priority
policy (lights always go on CobraPin). Individual LED names/numbers aren't tracked in
`components.yaml` — see `machinefolder/config/hardware-leds.yaml` for the full list.

## Known gaps (see `TODO.md` for full detail)

- **VUK eject coils missing** — `s-vukmid`/`s-vuktop` wired, no coil configured.
- **Portal dropper coil missing** — `s-dropper` has no matching coil.
- **Trough switches blocked** — chain2-0x21 opto board has a dead U1 shift register; coil side is
  fine.
- **Tilt** — no physical switch installed yet.
- **Ball saver / right ramp diverter / service mode nav** — game logic and/or physical wiring
  still open, see their rows above and `TODO.md`.
