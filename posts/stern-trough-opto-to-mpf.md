---
title: How to read a Stern SPIKE trough opto board with OPP
---

# How to read a Stern SPIKE trough opto board with OPP

<!--
DRAFT - not posted yet. Before posting:
- [ ] Cabinet test passed (empty trough, then ball by ball) - update the "Tested so far" note.
- [ ] Fill in Option 1's switch polarity once BIT_INVERT is set on the cabinet (marked TBD).
- [ ] Either test the bare ATmega328P build or keep the wording to "tested on an Arduino Uno".
- [ ] Option 2 is untested on OPP - test it, or keep it clearly marked as untested.
- [ ] Click every link (Portal Pinball links point at the public GitHub repo, main branch).
- [ ] If this goes somewhere other than MkDocs, convert the !!! admonitions and front matter.
-->

Related Config File Sections:

* [switches:](https://missionpinball.org/latest/config/switches/)
* [spi_bit_bang:](https://missionpinball.org/latest/config/spi_bit_bang/)
* [digital_outputs:](https://missionpinball.org/latest/config/digital_outputs/)
* [ball_devices:](https://missionpinball.org/latest/config/ball_devices/)

This how to guide explains how to read the opto sensors of a Stern SPIKE / SPIKE 2 ball trough
with MPF when your machine runs on Open Pinball Project (OPP) hardware. It adds the board-level
details — the connector, the bit order, and one polarity trap — to MPF's general
[Using the Stern Spike Trough](https://missionpinball.org/latest/mechs/troughs/spike_trough/)
guide.

The trough's receiver board ("Trough Serial Opto Receiver", for example 520-8516-00 or the older
520-7001-00A) looks like it needs Stern's node system, but it doesn't. It is a standard 74HCT165
shift register behind a 74HC540 buffer. It reads seven opto sensors (six ball positions plus the
jam opto) and shifts them out over a small header.

!!! note

    This page is not about the
    [Stern SPIKE platform](https://missionpinball.org/latest/hardware/spike/). If your machine
    runs on Stern SPIKE, configure the trough as a normal opto trough instead.

!!! note

    Tested so far: Option 1 below, on the bench with an Arduino Uno and a 520-8516-00 board.
    Cabinet test: TBD. Option 2 has not been tested on OPP yet.

## The connector

Use the header marked **`CN1`** ("SERIAL IN"):

| `CN1` pin | Signal |
|---|---|
| `VCC` | 5V supply |
| `RCK` | latch (register clock) |
| `SCK` | shift clock |
| `MOSI` | not needed |
| `MISO` | serial data out |
| `GND` | ground |

`CN1` also has an unlabelled 7th position, which is empty. `CN3` ("SERIAL OUT") carries the same
signals for chaining another board, and you don't need it. The board runs on 5V, so drive `RCK`
and `SCK` with **5V logic**. `RCK` enters a plain 74HC540, which needs about 3.5V to see a high,
so a 3.3V microcontroller is not enough.

## The latch is inverted

!!! warning

    `RCK` does not go straight to the 74HCT165's `SH/LD`. The board sends it through a spare
    channel of the inverting 74HC540 first. So on this board **`RCK` high = load and `RCK` low =
    shift** — the opposite of most 74HC165 examples.

To read the board:

1. Keep `RCK` low while idle.
2. Pulse `RCK` high for a few microseconds, then set it low again.
3. Clock 8 bits (SPI mode 0, MSB first) and read `MISO`.

If every read returns all zeros or all ones no matter which opto you block, the latch polarity is
backwards: you're clocking the register while it's still in load mode.

## Bit order

The first bit out is bit 7:

| Bit | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|---|
| Sensor | unused (always 0) | jam | trough 1 | trough 2 | trough 3 | trough 4 | trough 5 | trough 6 |

On the wire each bit is **1 when the opto is clear and 0 when it's blocked**, so an empty trough
reads `0b01111111`. This was measured on a 520-8516-00 by blocking one opto at a time. Note that
it differs from the numbering in the generic trough guide's example, which has the jam opto at 7.

## Option 1: A small microcontroller bridge

An Arduino Uno or Nano, or a bare ATmega328P at 5V, reads the board every 10ms and drives seven
output pins, one per opto, into ordinary OPP switch inputs. MPF then sees normal OPP switches,
updated about as fast as mechanical ones.

| `CN1` pin | ATmega (Arduino pin) |
|---|---|
| `RCK` | D8 |
| `SCK` | D13 |
| `MISO` | D12 |
| `VCC` / `GND` | 5V / GND |

Outputs D3, D4, D5, D6, D7, A0 and A1 carry trough 1–6 and the jam opto. Wire them to free OPP
switch inputs, and connect the microcontroller's ground to the OPP board's ground. A bare
ATmega328P needs only a 10kΩ reset pull-up and a 0.1µF decoupling capacitor, running on its
internal 8MHz clock.

The firmware, with the bit order above already built in:
[atmega328p-trough-bridge.ino](https://github.com/Dorus-Pinball/PortalPinball-V4.0/blob/main/tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino).
Set its `BIT_INVERT` array so each switch reads active when a ball is present. *(TBD: the final
setting after the cabinet test.)*

``` yaml
switches:
  s_trough1:
    number: 0-0-16      # the OPP input wired to the bridge's trough 1 output
  s_trough2:
    number: 0-0-17
  s_trough3:
    number: 0-0-18
  s_trough4:
    number: 0-0-19
  s_trough5:
    number: 0-0-20
  s_trough6:
    number: 0-0-21
  s_trough_jam:
    number: 0-0-22
```

Configure the ball devices as in the
[trough guide](https://missionpinball.org/latest/mechs/troughs/spike_trough/).

## Option 2: MPF's SPI Bit Bang platform

MPF's [SPI Bit Bang platform](https://missionpinball.org/latest/hardware/spi_bit_bang/) reads
the board without any extra microcontroller. It uses two OPP outputs for the latch and clock, and
one OPP switch input for `MISO`.

OPP outputs only switch to ground, so give each of those two lines a **pull-up resistor to 5V**
(about 1–2.2kΩ). With the pull-ups, an enabled output reads low and a disabled one reads high.
That happens to match this board's inverted latch: SPI Bit Bang holds its chip-select disabled
(high = load) between reads and enabled (low = shift) while clocking. Because an OPP input is
active when pulled low, each switch reads active when its opto is blocked, which is what the ball
devices expect.

``` yaml
hardware:
  platform: opp, spi_bit_bang
spi_bit_bang:
  miso_pin: s_trough_miso
  cs_pin: o_trough_rck
  clock_pin: o_trough_sck
  inputs: 8
  bit_time: 50ms
digital_outputs:
  o_trough_rck:
    number: 0-0-8       # adjust for your OPP board; pull-up to 5V -> CN1 RCK
    type: driver
  o_trough_sck:
    number: 0-0-9       # adjust for your OPP board; pull-up to 5V -> CN1 SCK
    type: driver
switches:
  s_trough_miso:
    number: 0-0-23      # adjust for your OPP board; <- CN1 MISO
  s_trough1:
    number: 5
    platform: spi_bit_bang
  s_trough2:
    number: 4
    platform: spi_bit_bang
  s_trough3:
    number: 3
    platform: spi_bit_bang
  s_trough4:
    number: 2
    platform: spi_bit_bang
  s_trough5:
    number: 1
    platform: spi_bit_bang
  s_trough6:
    number: 0
    platform: spi_bit_bang
  s_trough_jam:
    number: 6
    platform: spi_bit_bang
```

Keep in mind that this is slow. Every bit is a round trip over OPP's serial link, so at the
default 50ms `bit_time` MPF reads the trough about twice a second. That's fine for counting balls,
but it's slower than Option 1. If you shorten `bit_time`, keep it above the time OPP takes to
report a switch change.

## What if it did not work?

* **Every read is all zeros or all ones:** the latch polarity is backwards. Idle `RCK` low and
  pulse it high.
* **`RCK` or `SCK` doesn't reach about 3.5V at the board:** check the pull-ups (Option 2) or use a
  5V microcontroller (Option 1).
* **The Arduino reads a stuck value:** check that `MISO` goes to D12 and nothing is on D11.
* **Continuity checks on `RCK` stay silent:** there's a 220Ω resistor in series. Measure in
  ohms mode instead.
* For general ball device problems, see the
  [ball device troubleshooting guide](https://missionpinball.org/latest/mechs/ball_devices/troubleshooting/).

## More information

The full write-up covers chip pinouts for probing, Stern's schematic for the older board, bench
tools that did and didn't work, and how the inverted latch was found:
[stern-spike-trough-opto.md](https://github.com/Dorus-Pinball/PortalPinball-V4.0/blob/main/docs/stern-spike-trough-opto.md)
(from the Portal Pinball V4.0 project).
