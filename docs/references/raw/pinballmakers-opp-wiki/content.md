# Open Pinball Project (OPP) — pinballmakers.com wiki

Archived 2026-09-13 from <http://pinballmakers.com/wiki/index.php/OPP>. Rendered-page summary,
not a byte-perfect copy — the wiki itself notes "This page should be considered as a Work In
Progress."

## Overview

The Open Pinball Project represents an accessible framework for custom pinball machine builders.
"[The Open Pinball Project (OPP)] was started in 2012 as a resource for pinball makers to have an
inexpensive, fully open sourced project for controlling custom pinball machines."

The system underwent significant redesign in Q1 2020 due to processor board unavailability,
transitioning from Cypress PSoC4200 boards to more readily available STM32F103C8T6 "blue pill"
boards.

## Hardware Architecture

### Core Components

1. **Processor Board**: STM32F103C8T6 microcontroller unit available via eBay/Aliexpress
   (~$1.50-$2.00 plus shipping)
2. **Wing Boards**: Modular expansion boards for controlling outputs and reading inputs
3. **Power Filter Board**: Bulk capacitance management for inexpensive switching power supplies

### Processor Capabilities

Each processor board supports up to four wing boards using eight-pin connections:

- 16 solenoids with 16 direct switch inputs (via solenoid wings)
- 32 switch inputs (via switch wings)
- 32 lamp outputs (via incandescent wings)

The processor performs no game logic — it's a physical interface layer. A separate controller
running software like Mission Pinball handles scoring and device activation.

### Wing Board Types

**Solenoid Wing** — up to four coils via ground-sink MOSFETs, 24-48V at 10A+. Six-pin connector
for coils, four-pin connector for direct switch inputs (autofire capability). IRL540NPBF
N-Channel MOSFETs with 10K pull-down resistors.

**Incandescent Wing** — eight individual lamps via ground-sink architecture, 6.3V at 10A
(~0.25A per bulb at full brightness). Eight-pin connector for direct lamp control. BS-170
N-Channel MOSFETs (not 2N7000TA, which requires reversed orientation).

**Switch Wing** — direct connection to processor pins with high-side configuration: "Unlike the
Solenoid and Incandescent wings, the Switch wing is set up as High-side, where the switch pins
are at 5V and playfield and cabinet switches are tied to Ground." Eight-pin locking header with
built-in pull-up resistors.

**Power Filter Board** — bulk capacitance for coil firing transient current. NTC thermistor
inrush current limiting, LED indicator for capacitor charge status, configurable for single or
dual power supplies, optional enable/disable control via processor pin.

## Firmware Installation (STM32F103C8T6)

Linux/macOS: install `libusb-1.0-0-dev`/`git`, build stlink, connect ST-LINK V2 to
3.3V/SWD/SWCLK/GND, move Boot0 jumper to position 1, `sudo st-flash --format ihex write
OppStm32.2.0.0.6.hex`, move Boot0 jumper back, verify with `sudo python Gen2Test.py
-port=/dev/ttyACM0`.

Windows: download/install STSW-LINK004, same hardware connections, use STM32 ST-Link Utility GUI.

## Multi-board configuration (chaining)

Boards chain via 8-wire ribbon/FC-8P IDC connectors. First processor: USB to host, 4-wire Molex
(5V/GND/TX/RX) to Interface wing OUT. Middle processors: ribbon cable IN, ribbon cable OUT to
next. Last processor: ribbon cable IN, jumper pins 3-4 on OUT connector to terminate the chain.

Verification via `Gen2Test.py` should list every chained processor's address and wing config.

## Wiring specifications

**Critical safety note**: "When wiring up multiple power supplies for logic, coils and
lamps/LEDs, it is critical to connect all grounds together at the power supplies to avoid a
potential floating ground issue that can easily destroy your OPP boards."

Solenoid connections: positive from HV supply (24-70V), negative to the solenoid wing's Molex
connector. **Essential**: 4004 diode across positive/ground, band toward positive, for flyback
protection.

## Power supply requirements

- 5V @ 3A — logic/processing
- 6.3V @ 10A — incandescent lamps
- 24-48V @ 10A — solenoids (depends on coil specs)

## Troubleshooting

- `IndexError: string index out of range` — verify firmware, wing config matches hardware, power
  LED status (yellow when USB-connected), correct serial port.
- `ImportError: No module named serial` — `pip install pyserial`.
- Hardware checklist: verify 5V at multiple points, confirm grounds with multimeter, test RX/TX
  line separation, verify ribbon cable orientation, confirm termination jumper on the last board.
