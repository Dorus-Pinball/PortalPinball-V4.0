# Trough opto bridge: bare ATmega328P build plan

## Goal

Replace the fragile hand-soldered taps on the Stern trough opto board — the wiring damage logged in
commit `859a6b9` — with a small bridge. A bare ATmega328P reads the board's own serial connector
and mirrors the 7 sensors onto OPP's switch inputs, so the MPF/OPP config stays as it is apart
from the addressing/board and the output polarity.

**2026-09-27 update:** actually wired into **chain2-0x20 (`2-0-16…22`)**, not chain2-0x21
(`2-1-16…22`) as this section originally planned and as `board Overviews.xlsx`'s design sheet
calls for (`docs/board-silkscreen-reference.md`) — confirmed live via `tools/wiring_test.py
--monitor`. Live hardware wins over the design sheet per the user. The wiring table below is kept
as-written for the historical build (it's still what's soldered on the ATmega board itself); only
the OPP-side addressing changed, tracked in `hardware-switches.yaml`/`components.yaml` now instead
of here.

How the Stern board works, its bit map, the tools and pitfalls, and the bench history behind all
this: `docs/stern-spike-trough-opto.md`. The alternative of reading the board straight from OPP
with MPF's `spi_bit_bang` platform was considered and not chosen (`CHANGES.md` #29); it's written
up in that doc.

**Why a bare chip:** the parts are already in stock, it's 5V like the rest of the OPP wiring (no
level shifters), and it keeps the ready-made Arduino boards free while giving a small, permanent
footprint.

## Status (2026-09-26)

- **Serial read proven on the bench** with an Arduino Uno on a 520-8516-00 board, via its `CN1`
  ("SERIAL IN") connector.
- **Firmware ready:** `tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino`. It uses the
  board's inverted latch (idle `RCK` low, pulse high) and `BIT_CHANNEL` is set to the verified bit
  map.
- **Open:** `BIT_INVERT` (the output polarity OPP needs), the build itself, wiring into OPP, and
  the cabinet test. Tracked in `TODO.md`.

## How it works

Every 10ms the firmware pulses `RCK` high then low to latch the sensors (the board inverts `RCK`
before the shift register), clocks one byte over hardware SPI, requires 3 matching reads in a row
(debounce), and sets 7 output pins. Each output pin replaces one of the old soldered taps.

## Parts

Checked against the `Component_database` inventory on 2026-09-26:

| Part | In stock |
|---|---|
| ATmega328P-PU, DIP-28 | 5 |
| 10kΩ resistor (reset pull-up) | 20 |
| 0.1µF ceramic capacitor (decoupling, from the ceramic assortment) | yes |
| Uno + ArduinoISP shield (programmer only) | yes |
| Perfboard, DIP-28 socket, mating plug for the Stern board's `CN1` header | not in the database (may just be unrecorded) |

The socket is worth it: pull the chip to reprogram it on the ISP shield instead of in-circuit. Use a
proper plug on the Stern board's `CN1` header rather than soldering to the board — that fragility is
what caused the original damage.

## Wiring

DIP pin numbers:

| ATmega pin | Connects to |
|---|---|
| 7 VCC, 20 AVCC | +5V |
| 8, 22 GND | GND |
| 1 RESET | +5V through 10kΩ |
| 7–8 | 0.1µF ceramic, right at the chip |
| 16 SS | +5V (forces SPI master) |
| 9, 10 XTAL, 17 MOSI | not connected (internal 8MHz clock) |
| 14 (PB0) | Stern `CN1` `RCK` |
| 19 (PB5) | Stern `CN1` `SCK` |
| 18 (PB4) | Stern `CN1` `MISO` |
| 5 (PD3), 6 (PD4), 11 (PD5), 12 (PD6), 13 (PD7), 23 (PC0) | `s-trough1`…`s-trough6` → OPP inputs 2-0-16…21 |
| 24 (PC1) | `s-trough-jam` → OPP input 2-0-22 |

- Stern `CN1` `VCC`/`GND` go to the same +5V/GND. Its `MOSI` stays unconnected.
- The ATmega's ground **must** be shared with the OPP board.
- Power from the machine's 5V logic supply. During the bench test a Uno on USB powered the whole
  opto board without trouble, so the draw is modest (not measured).
- **2026-09-27:** actually landed on chain2-0x20, not chain2-0x21 as originally planned here (see
  the note at the top of this doc) — NOT the same board the old soldered taps used, despite the
  original plan. Table above updated to match what's actually wired.

## Programming

Flash `tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino` with
`tools/flash-atmega328p.ps1` (ArduinoISP sketch on the Uno with the ISP shield, MiniCore, 8MHz
internal clock). No firmware changes are needed; the SPI and serial speeds work at 8MHz.

Set the fuses ("Burn Bootloader") on **every** chip, whatever its history. These are inventory
spares, and a chip previously set for an external crystal sits dead with no clock and no error
message until its fuses are rewritten.

## Build order

1. **Calibrate `BIT_INVERT` on the Uno, at the cabinet.** Wire the Uno the same way (`CN1` →
   D8/D13/D12; outputs D3, D4, D5, D6, D7, A0, A1 → OPP 2-0-16…22; shared GND). Watch MPF's live
   switch states and set `BIT_INVERT` until `s-trough1…6` read correctly with balls present, and
   `s-trough-jam` matches what the ball device config expects (today: active = clear path).
   Reflashing the Uno over USB takes seconds, which is why this happens before the bare chip.
2. **Build the ATmega board** from the wiring table, with the chip socketed.
3. **Program the chip** with the calibrated firmware.
4. **Bench-test off the machine:** put a 220–330Ω resistor and an LED on each output, block each
   sensor by hand, and check the matching LED toggles.
5. **Install** in place of the Uno and run the verification below.

## Verification

- Re-run the repro from `TODO.md`'s trough entry on the real cabinet: empty-trough read, then
  ball-by-ball.
- Confirm `bd-trough` stops misreading with the trough empty over an idle period (the original
  symptom) before marking the TODO item done.
- Update `TODO.md`, and add a short note near the trough switches in
  `machinefolder/config/hardware-switches.yaml` saying they're driven by the bridge (pointing here),
  so it isn't re-derived from scratch next time.

## Alternatives on file

- **Leave the Uno in permanently:** works as-is with no soldering, just bigger.
- **Pro Micro from the inventory** (ATmega32U4, the 16MHz/5V version): small, with USB, but its
  SPI pins differ, so the firmware's pin map would need changing.
- **No microcontroller at all:** MPF's `spi_bit_bang` platform (see the doc above).

## Printable build sheet

`design/physical-checklists/trough-opto-bridge.html` — an A4 version of this build: parts list,
DIP-28 pinout diagram, wiring tables, and the firmware read sequence.
