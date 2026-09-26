<!--
DRAFT - not posted yet. Before posting:
- [ ] Cabinet test passed (empty trough, then ball by ball) - update the "Status" line.
- [ ] Fill in the MPF switch config once BIT_INVERT is set on the cabinet (marked TBD below).
- [ ] Either test the bare ATmega328P build or keep the wording to "tested on an Uno".
- [ ] Decide whether to keep Option B (spi_bit_bang is untested).
- [ ] Click every link (they point at the public GitHub repo, main branch).
- [ ] Convert formatting if the OPP site doesn't take Markdown.
-->

# Reading a Stern SPIKE trough opto board with OPP and MPF

If you've salvaged a ball trough from a Stern SPIKE / SPIKE 2 machine, its "Trough Serial Opto
Receiver" board (mine is a **520-8516-00**; the older **520-7001-00A** uses the same design) looks
like it needs Stern's node system. It doesn't. It's a standard **74HC165 shift register** behind a
**74HC540** buffer, with the seven opto sensors on a 6-pin header. Here's how I got it into MPF
through OPP.

**Status:** reading verified on the bench with an Arduino Uno. Cabinet test: *TBD.*

## The one gotcha: `RCK` is inverted

The board sends `RCK` through a spare inverter in the 74HC540 before it reaches the 165's
`SH/LD`. So on this board **`RCK` HIGH = load, `RCK` LOW = shift** — the opposite of every
74HC165 tutorial. To read it:

1. Idle `RCK` **low**.
2. Pulse `RCK` **high** for a few µs, then back **low**.
3. Clock 8 bits (SPI mode 0, MSB first) and read `MISO`.

If every read comes back `0x00` or `0xFF` no matter what you block, your latch polarity is
backwards. That cost me most of a day — and a board I wrongly declared dead.

## The connector

Use **`CN1` ("SERIAL IN")**: `VCC`, `RCK`, `SCK`, `MOSI`, `MISO`, `GND`, plus an empty 7th
position. `CN3` ("SERIAL OUT") is for chaining further boards and isn't needed, and `MOSI` does
nothing for a read. The board runs on 5V. Drive `RCK` with **5V logic**: it goes into a plain
74HC540, which needs about 3.5V to see a high, so 3.3V microcontrollers (or a Bus Pirate v3) won't
do.

**Bit map** (520-8516-00; first bit out = bit 7):

| Bit | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|---|
| Sensor | unused (always 0) | jam | trough 1 | trough 2 | trough 3 | trough 4 | trough 5 | trough 6 |

Each bit reads **1 = clear, 0 = blocked**. An empty trough reads `0b01111111`.

## Option A: a small ATmega bridge (what I'm using)

An Arduino Uno/Nano or a bare ATmega328P (5V) reads the board every 10ms and drives seven output
pins, one per sensor, into ordinary OPP switch inputs. MPF just sees normal OPP switches, so
nothing special is needed on the MPF side.

| Board `CN1` | ATmega (Arduino pin) |
|---|---|
| `RCK` | D8 |
| `SCK` | D13 |
| `MISO` | D12 |
| `VCC` / `GND` | 5V / GND |

Outputs D3, D4, D5, D6, D7, A0, A1 = trough 1–6 and jam → your OPP switch inputs. **Share ground**
between the ATmega and the OPP board. A bare ATmega328P needs only a 10kΩ reset pull-up and a
0.1µF decoupling cap, running on its internal 8MHz clock.

Firmware (debounced, with the bit map above built in):
[atmega328p-trough-bridge.ino](https://github.com/Dorus-Pinball/PortalPinball-V4.0/blob/main/tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino).
Set `BIT_INVERT` so MPF shows a switch active when a ball is present.

MPF switch config: *TBD — add the final `switches:` entries and `type:` after the cabinet test.*

## Option B: no microcontroller, MPF's `spi_bit_bang` (untested)

MPF 0.80 ships an `spi_bit_bang` platform that reads a 74HC165 through another platform's
hardware: two OPP outputs for `RCK` and `SCK` (each with a pull-up resistor to 5V, about 1–2.2kΩ)
and one OPP input for `MISO`. With pull-ups on OPP's low-side outputs, its default sequence happens
to match this board's inverted latch. The catch is speed: every bit is a round trip over the serial
link, so a full read takes about 0.5s at default settings. That's fine for a trough, but I haven't
tried it. There's a config sketch in the write-up below.

## More detail

The full write-up covers chip pinouts for probing, Stern's schematic for the older board, the
bench tools that did and didn't work, and the whole debugging story:
[stern-spike-trough-opto.md](https://github.com/Dorus-Pinball/PortalPinball-V4.0/blob/main/docs/stern-spike-trough-opto.md).
