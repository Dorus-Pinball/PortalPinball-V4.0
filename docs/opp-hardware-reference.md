# OPP hardware reference: CobraPin vs. the red boards

This is the canonical, cited reference for how this machine's two OPP hardware families address
switches/coils/lights and what rules govern pairing a switch to a coil for a hardware-autofire
device (flippers, slings, pop bumpers). It exists because the two families follow **meaningfully
different rules** and this project is being rewired from scratch, picking board assignments fresh
component by component — getting this wrong risks a non-working hardware rule at best and a blown
FET/coil/fuse at worst.

`tools/hw_console/data/components.yaml` stays the live "what's actually wired where" tracker;
this doc is the rulebook it and `design/physical-checklists/wiring-guide.html` both draw on, so
the rules only need to be figured out once. See also `.claude/skills/wire-component/SKILL.md`,
which encodes the process built on top of these rules, and `docs/wiring-pin-map.md` for a single
readable table of every component's current pin assignments and status.

## Project board-priority policy

**Use CobraPin first wherever possible (chain 0 before chain 1); the red boards (chain 2, boards
`0x20`-`0x23`) are the fallback, used only when CobraPin can't fit a component. All LEDs go on
CobraPin, always, regardless of remaining CobraPin coil/switch capacity.**

This applies to every component being freshly assigned during the rewire: VUK eject coils,
dropper coil, ramp-diverter, service-mode nav switches, a future tilt switch, and anything else
not yet wired for real.

## CobraPin (chain 0 / chain 1)

One physical PCB, two independent STM32 controllers sharing it — chain 0 (`COM4`, "Board 0") and
chain 1 (`COM5`, "Board 1"). **Switch inputs are 3.3V logic** (STM32-based) — keep this in mind
when probing a switch pin with a meter.

### Solenoid banks and power

- 3 solenoid banks — **A, B, C** — 8 driver outputs each (24 total), on connectors `J6`/`J7`/`J8`.
- Each bank has its own **fused** HV supply pin on a 3-pin connector, `J13`: `HV_A`, `HV_B`,
  `HV_C`. **A coil's positive lead must come from the HV pin matching its own bank** — never a
  generic shared "+50V bus." Powering a Bank B coil from `HV_A` or `HV_C` puts current through
  the wrong bank's fuse.
- Official CobraPin doc's own words: mixing this up **"could cause blown FETs, coils, and
  fuses."** Recommended practice: test without coil power first, and use the yellow per-bank coil
  LED (each bank has one) to confirm a bank actually has power before trusting it.
- A bank's connector pins can be **pre-broken-out to a wall-mounted terminal block** for
  convenience without any coil actually being wired to them yet — wires present on a bank's
  connector doesn't by itself mean the bank is in use. Check the far end of the run.

### Switch inputs can be silently repurposed by the board's own flashed config

A CobraPin board's per-channel behavior isn't fully determined by `mpf hardware scan` (which only
reports coarse wing-level type — solenoid/input/NeoPixel/etc). A separate, external tool -
CobraPin's own board-config toolchain, on this machine at
`C:\Users\dorus\Documents\Pinball-Code\Tools\Boardconfig files\Cobra\` (config scripts) and
`...\Tools\OPP - open-pinball-project-code\` (full source) - can set a *per-channel* config byte
that MPF's hardware scan never surfaces, silently taking an input off the table for plain switch
use without it ever showing as "in use" anywhere in this repo's own config.

**Confirmed case (2026-09-06):** chain 0 board `0x20`'s `CobraPin_Board0_servos.py` config
(vs. the plain `CobraPin_Board0.py`) sets a special `\x96` byte on input indices **8, 9, 10, 11**
instead of the normal `rs232Intf.CFG_INP_STATE` - dedicating those four inputs to servo/PWM use.
A switch wired to one of them reads stuck/garbage regardless of press/release (not a simple NO/NC
reversal, which would just invert). Found after `s-start` was wired to `0-0-8` and wouldn't work;
moved to `0-0-27` instead.

**This is enforced in code, not just documented here:** `tools/hw_console/registry.py`'s
`RESERVED_NUMBERS` dict lists every number known to be off-limits this way, and both
`check_collision()` (the interactive pre-check in `wire-component`'s step 4) and `full_scan()`
(run automatically by the PostToolUse hook after any edit to `hardware-switches.yaml`/
`-coils.yaml`) check against it. If a board is ever reflashed back to a plain (non-servo) config,
or a new board turns out to have its own repurposed channels, update `RESERVED_NUMBERS` to match
reality - it's a manually-maintained list, not something derived from a live board query.

### Same-microcontroller pairing rule (hardware-autofire devices)

For a hardware-autofire device (flippers, slings, pop bumpers — switch and coil linked as a
hardware rule, not software-triggered), **the switch and the coil must be addressed by the same
microcontroller**: the first digit of both numbers must match. A coil on `0-x-y` pairs only with
a switch on `0-a-b`; never mixed across `0-` and `1-`. This is CobraPin's *only* pairing
constraint — there is no further sub-range requirement (contrast with the red boards, below).

### Full per-pin bank / HV-feed / color reference

| Coil number(s) | Bank | HV feed pin | Wire color |
|---|---|---|---|
| `0-0-0`, `0-0-8`, `0-0-9`, `0-0-10`, `0-0-11`, `0-0-12`, `0-0-13`, `0-0-14` | A | `HV_A` | brown |
| `0-0-1`, `0-0-2`, `0-0-3`, `0-0-4`, `0-0-5`, `0-0-6`, `0-0-7`, `0-0-15` | B | `HV_B` | teal |
| `1-0-0`, `1-0-1`, `1-0-2`, `1-0-3`, `1-0-4`, `1-0-5`, `1-0-6`, `1-0-7` | C | `HV_C` | purple |

This project's flipper coils (`c-flipper-left`=`0-0-8`, `c-flipper-right`=`0-0-9`) are both **Bank
A**, so they draw +50V from the **brown `HV_A`** wire. Its flipper switches
(`s-left-flipper`=`0-0-1`, `s-right-flipper`=`0-0-2`) are on chain 0 too, satisfying the
same-microcontroller pairing rule above; switches don't have a "bank" (that's a coil-only, HV
power concept), so their numbers landing in what the table above calls coil Bank B's range is
irrelevant here.

Other confirmed wire colors: main incoming supply `VIN` = red, `GND` = black. The 8-pin
driver-output signal wires observed in photos cycle through blue/yellow/purple/teal, but this
isn't confidently a strict per-pin-number code — don't assert a specific pin always gets a
specific color without checking.

### Sources

- `board Overviews.xlsx`, sheets `Cobrapin - Doc` and `Cobrapin - Game Funtion` (silkscreen
  pin-to-address dump).
- Board close-up photos and an HV-distribution terminal-block photo taken of this cabinet
  (2026-09-06 session).
- [Official CobraPin doc](https://missionpinball.org/latest/hardware/opp/cobrapin/) /
  [GitHub markdown source](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/cobrapin/index.md).

## Red boards — classic/modular OPP (chain 2, boards `0x20`-`0x23`)

A fundamentally different architecture from CobraPin: each processor board (PSoC4200, this
project's gen2 hardware) can carry **up to 4 plug-in "wing" boards**, each independently a
solenoid wing, switch wing, or incandescent-lamp wing, mixed freely. **Switch inputs are 5V
logic** — a different idle voltage than CobraPin's 3.3V.

### Numbering scheme

Format is `board-index` (two-part) in MPF's generic docs, or `chain-board-index` (three-part) once
multiple serial chains exist — this project always uses the three-part form (`2-0-0`, `2-1-16`,
etc.), same underlying scheme with the chain prefix added.

- **Switches** (pure switch wing): wing 0 → `0-7`, wing 1 → `8-15`, wing 2 → `16-23`, wing 3 →
  `24-31` (8 per wing).
- **Coils** (solenoid wing): wing 0 → `0-3`, wing 1 → `4-7`, wing 2 → `8-11`, wing 3 → `12-15`
  (4 per wing).
- **Lamps** (incandescent wing): same 8-per-wing pattern as switches.

### Pairing rule — tighter than CobraPin

A solenoid wing's own dedicated direct-switch inputs (for hardware-autofire pairing) are **the
first four switch numbers of that same wing position**: a coil in wing N (`4N..4N+3`) pairs only
with a switch in `8N..8N+3` — not just "anywhere on the same board." This is a real, separate
constraint from CobraPin's simpler same-controller-digit rule.

Cross-validated against this project's own already-working hardware (not just theoretical):

- Board `0x20`, wing 0 (coils `2-0-0..3`, dedicated switches `2-0-0..3`): `c-sling-right`/`left` =
  `2-0-0`/`2-0-1`, paired switches `s-right-sling`/`s-left-sling` = `2-0-0`/`2-0-1` — both inside
  wing 0's dedicated range. (Since moved to the Cobra board, chain 0, 2026-09-13 — see
  `hardware-coils.yaml`/`hardware-switches.yaml` — this is left as the historical example that
  cross-validated the rule.) `c-plunger`/`c-trough-eject` (`2-0-2`/`2-0-3`) are wing 0's remaining
  2 coils but are software-triggered (`ball_device`), so no paired switch is needed for them.
- Board `0x20`, wing 1 (coils `2-0-4..7`, dedicated switches `2-0-8..11`): `c-popbumper-1/2/3`
  (`2-0-4/5/6`) paired with `s-popbumper-1/2/3` (`2-0-8/9/10`) — the first 3 of wing 1's 4
  dedicated slots (`2-0-11` unused). `c-drop` (`2-0-7`) is wing 1's 4th coil, software-triggered.

Any future hardware-autofire pairing added to chain 2 must follow this same wing-relative rule.

### Connectors and power

- Solenoid wing: 6-pin Molex Mini-Fit (coils) + a separate 4-pin connector (the 4 dedicated
  direct-switch inputs described above).
- Switch wing: 8-pin 2.54mm locking header.
- Incandescent/lamp wing: 1x8 locking header + 2-pin 12V ground.
- Boards chain together via 8-wire ribbon/FC-8P IDC connectors.
- Voltages: logic 5V/3A, lamps 6.3V/10A, solenoids 24-48V/10A — matches this cabinet's real
  `RSP-320-48` (48V) supply.
- Flyback diode (4004-type, band toward the positive lead) and common-ground-at-the-supply
  requirements are **identical to CobraPin** — same rule, no separate treatment needed.

### LEDs on red boards (context only — this project puts all LEDs on CobraPin)

Format `chain-board-index`, e.g. `0-0-0` = first RGB LED on chain 0, card `0x20` (`card_num` is
the board's hex address minus `0x20`). Channels use `internal_index = 3 * index` for 3-channel
RGB/GRB pixels; RGBW doesn't fit this directly (chain LED entries instead and let MPF
auto-calculate channels). Same underlying convention CobraPin's own LED numbering uses — included
here only so the pattern in `hardware-leds.yaml` makes sense, not because this project uses red
boards for LEDs (it doesn't, per the priority policy above).

### Connecting & config

- `mpf hardware scan` verifies connected boards (ports, firmware, per-category card counts) — this
  project's standard check, per the reference scan pasted into `hardware-basic.yaml`.
- Platform config: `hardware: {platform: opp}`, `opp: {ports: COM7}` (or a list, as this project
  already has for `COM4`/`COM5`/`COM6`). Windows COM ports above 9 need the `\\.\COM10` form.
- `debug: true` under the `opp:` config section for verbose diagnostics; `poll_hz: 50` (default
  100) to reduce polling rate if boards can't keep up — trades off slower switch response.

### Sources

- [pinballmakers.com OPP wiki](http://pinballmakers.com/wiki/index.php/OPP)
- MPF doc sources (fetched from GitHub, since the rendered doc site only returns nav-shell content
  for these pages): [switches](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/switches.md),
  [drivers](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/drivers.md),
  [leds](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/leds.md),
  [lights](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/lights.md),
  [connecting](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/connecting.md),
  [config](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/config.md),
  [troubleshooting](https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/troubleshooting.md).
