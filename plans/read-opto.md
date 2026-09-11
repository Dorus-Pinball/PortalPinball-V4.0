# Reading the Stern trough opto board's serial output via a bare ATmega328P bridge

## Context

The trough uses a salvaged Stern trough assembly (board silkscreened "...RD TROUGH", part
**520-7001-00A** — same family as the SPIKE/SPIKE 2 "Trough Serial Opto Receiver" boards, an
earlier revision of 520-1051-00/520-8516-00). The current setup extracts switch state by
soldering small tap wires directly onto board component legs and feeding them into OPP as plain
direct switches (`s-trough1..6` / `s-trough-jam` on chain2-0x21, `hardware-switches.yaml`).
Commit `859a6b9` logged physical wiring damage at exactly this board (`s-trough2/3/4` and
`s-trough-jam` reading intermittently/incorrectly with an empty, unobstructed trough) — those fly
wires soldered to small SMD pads are fragile and this already caused a real fault. The user wants
to read the board's actual serial output instead of tapping individual sensor legs.

## What the research + photos found

Initial research (before seeing the board) assumed "serial" meant Stern's proprietary Spike
node-bus protocol (RS-485, only usable via a genuine Spike CPU board's bridge port) — which would
have needed sourcing Spike CPU/node hardware the user doesn't have, for uncertain payoff. That
assumption was wrong, corrected by two things seen in the user's own photos:

1. **The ICs are standard, public parts**: U1 is an **NXP 74HCT165D**, a textbook 8-bit
   parallel-in/serial-out shift register. U2 is an **NXP 74HC540D**, a standard octal buffer
   (conditioning the opto comparator outputs into U1's parallel inputs). "Serial Opto Receiver"
   just means Stern used a shift register to serialize the opto channels onto one wire — no
   undocumented Stern protocol involved.
2. **The board's populated connector is silkscreened with the signal names**: `VCC`, `RCK`,
   `SCK`, `MISO`, `GND` — the standard naming for a bare 74HC165 breakout (`MISO` = serial data
   out / Q7, `SCK` = clock, `RCK` = register/latch clock i.e. SH-LD). Nothing to trace or guess.

Reading this board is "read a documented shift register over SPI-style signals," a well-trodden
Arduino/AVR pattern, not blind reverse engineering.

## Recommended approach: bare ATmega328P-PU bridge

The `Component_database` inventory (`data/components.db`) has **5 spare bare ATmega328P-PU**
DIP chips, an **Arduino ISP Programmer Shield**, and an **Arduino Uno R3** / **Duemilanove**
(either usable as the ISP host) already on hand. Chosen over dedicating a full Uno/Duemilanove
permanently, or a 3.3V ESP32/RP2040/STM32 board (which would need one of the on-hand logic-level
converter modules since this opto board is 5V TTL/CMOS like the rest of the OPP-side wiring) —
the bare chip keeps the ready-built boards free and gives a small, permanently-installable
footprint, at the cost of a bit more build/wiring work than just using a complete board.

**1. Flash one ATmega328P-PU** using the Arduino ISP Programmer Shield hosted on the Uno (or
Duemilanove) running the standard `ArduinoISP` sketch, targeting the **"ATmega328 on a
breadboard" / 8 MHz internal oscillator** board profile — no external crystal needed, keeping the
standalone support circuit to just the chip itself.

**2. Minimal standalone support circuit** (small, robust — not the kind of fragile hand-tap that
broke last time): decoupling capacitor across VCC/GND at the chip, and a pull-up resistor on
RESET. That's the full parts list beyond the chip.

**3. Wire the chip to the Stern board's existing connector** (build a proper mating connector for
that populated header rather than any new solder joints on the Stern board itself — the actual
fix for the fragility that caused the original damage):
   - `SCK` -> ATmega328P **PB5 / D13** (hardware SPI clock)
   - `MISO` -> ATmega328P **PB4 / D12** (hardware SPI data in)
   - `RCK` -> any spare GPIO, toggled manually to latch (not part of hardware SPI)
   - `VCC`/`GND` shared with the bridge chip's own supply

**4. Firmware**: use the ATmega328P's hardware SPI peripheral in master mode (SCK output, MISO
input) — pulse the `RCK` pin to latch the 8 parallel opto bits, then clock out a dummy byte via
SPI to shift `MISO` in, one bit per opto channel (standard "74HC165 over hardware SPI" pattern).
Drive 7 more GPIO pins to mirror `s-trough1..6`/`s-trough-jam`'s states, wired into OPP's existing
switch wing exactly as today (same chain2-0x21 positions, same NC semantics, same inverted
`s-trough-jam` meaning already documented in `hardware-switches.yaml`) — so no MPF/OPP config
changes are needed, only what drives those 7 wires changes.

This keeps the failure surface small: one clean connector-to-connector link at the Stern board,
a minimal, well-understood support circuit around the bridge chip, and the OPP-facing wiring
stays exactly as already verified working.

## Bench breadboard wiring

Standalone ATmega328P-PU (28-pin DIP, internal 8 MHz oscillator, no crystal), already flashed
via the ArduinoISP shield. Pin numbers are physical DIP pin numbers; Arduino names in
parentheses.

**Power & support (the only passive parts needed):**
| Pin | Signal | Wire to |
|-----|--------|---------|
| 7 | VCC | breadboard `+` rail |
| 20 | AVCC | breadboard `+` rail |
| 8 | GND | breadboard `-` rail |
| 22 | GND | breadboard `-` rail |
| 1 | RESET | `+` rail via a 10kΩ pull-up resistor |
| 7/8 | VCC/GND | a 0.1µF ceramic cap directly across these two pins, as close to the chip as possible |
| 21 | AREF | 0.1µF cap to `-` rail (standard practice, optional) |
| 9, 10 | XTAL1/XTAL2 | leave unconnected — internal-oscillator fuse means no crystal needed |
| 16 | SS (PB2) | tie directly to `+` rail — forces SPI master mode regardless of firmware init order |
| 17 | MOSI (PB3) | leave unconnected — nothing on the Stern board listens to it |

**Link to the Stern board's connector** (its own 5 labeled pins):
| Stern board pin | Wire to ATmega328P pin | Notes |
|---|---|---|
| `GND` | breadboard `-` rail | shared ground with the bridge chip |
| `VCC` | breadboard `+` rail | **verify the opto board's actual current draw before backfeeding it from the same 5V bench supply** — don't just assume |
| `SCK` | pin 19 (PB5/D13) | hardware SPI clock |
| `MISO` | pin 18 (PB4/D12) | hardware SPI data in |
| `RCK` | pin 14 (PB0/D8) | plain GPIO, toggled by firmware to latch — any spare pin works, this is just a clean choice |

**7 switch-mirror outputs** (bench: through a 220-330Ω resistor to an LED to `-` rail, one per
channel, so you can see each toggle by hand-blocking that opto channel; on final install these
same 7 pins go straight to OPP's existing switch-wing positions instead):
| Pin | Signal | Mirrors |
|---|---|---|
| 5 (PD3) | `s-trough1` | |
| 6 (PD4) | `s-trough2` | |
| 11 (PD5) | `s-trough3` | |
| 12 (PD6) | `s-trough4` | |
| 13 (PD7) | `s-trough5` | |
| 23 (PC0) | `s-trough6` | |
| 24 (PC1) | `s-trough-jam` | |

Firmware detail: on startup, set `SS`/`MOSI`/`SCK` per above and enable SPI master mode; to read,
pulse `RCK` (pin 14) low-then-high to latch, then clock one byte through SPI (e.g. write `0x00`
to `SPDR` and wait for `SPIF`) — the byte received in `SPDR` has one bit per opto channel, MSB
first. Confirm bit-to-channel mapping and active-high/active-low polarity empirically against the
known NC semantics already documented for these switches (`s-trough-jam` in particular reads
active = clear path, not jammed) before wiring into OPP, rather than assuming from the datasheet
alone.

## Deliverable: printable build sheet

`design/physical-checklists/trough-opto-bridge.html` — a standalone, printable (A4) HTML build
sheet, matching this project's existing `design/physical-checklists/wiring-guide.html` visual
style (IBM Plex Sans/Mono + Big Shoulders Stencil, same masthead/section/card/table components,
light+dark theme tokens), with print-specific CSS (`@page { size: A4; }`, page-break-safe
sections). Contents: parts list (from `Component_database` inventory), the fuse-programming
steps, the power/support-circuit table and DIP-28 pinout diagram, the Stern-connector link table,
the 7 switch-mirror output table, and the firmware read-sequence steps.

## Verification

- Bench-test the flashed chip + support circuit on a breadboard against the opto board off the
  machine first: manually block/unblock each opto channel and confirm the corresponding GPIO
  output toggles correctly, before installing in the cabinet.
- Re-run the existing repro from `TODO.md`'s trough entry (empty-trough read, then ball-by-ball)
  on the real cabinet once wired in.
- Confirm `bd-trough` stops misreading with the trough empty over an idle period (the original
  symptom) before marking the TODO item done.
- Update `TODO.md` and add a short note (near the trough switches in `hardware-switches.yaml` or
  in `docs/opp-hardware-reference.md`) documenting the board's identity (520-7001-00A, 74HCT165
  shift register, `VCC`/`RCK`/`SCK`/`MISO`/`GND` connector pinout), the bridge-chip approach, and
  which spare ATmega328P-PU/inventory items were used, so this isn't re-derived from scratch next
  time.
