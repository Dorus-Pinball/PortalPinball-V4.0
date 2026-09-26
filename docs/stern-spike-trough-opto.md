# Reading a Stern Spike-era trough opto board without genuine Spike hardware

A reference for anyone who has salvaged a Stern trough assembly (SPIKE or SPIKE 2 era) for a
homebrew machine and wants to read its opto sensors from non-Stern control hardware (OPP, a
generic microcontroller, etc.) instead of Stern's own CPU/node system. Written up here because
the "Serial Opto Receiver" name is misleading and the obvious assumption — that it needs Stern's
proprietary node-bus protocol — is wrong for at least one confirmed board revision. If you're
building a Portal Pinball V4.0-style machine and landed here from that project: this file holds
the knowledge (how the board works, how to read it, the tools and pitfalls, and the bench history
that got there — see "Bench history" at the end); `plans/read-opto.md` is that project's build plan
for the bridge, and `tools/atmega328p-trough-bridge/` is a working reference implementation.

**Confirmed by physically examining two boards** (parts 520-7001-00A and 520-8516-00, see below;
the read has been proven working end-to-end on the 520-8516-00). The rest of the part-number
family is inferred from how Stern/resellers describe and price them, not independently opened and
checked. If you have a different revision, verify before assuming it matches.

## TL;DR

- **The one gotcha that matters most: `RCK` is inverted on the board.** It reaches the shift
  register's `SH/LD` through an inverting buffer, so **`RCK` HIGH = load, `RCK` LOW = shift**. Idle
  `RCK` low, pulse it high to latch, return it low, then clock. Doing it the normal 74HC165 way
  (pulse low) clocks the register while it's stuck in load mode, and you read the same bit 8 times
  — every byte comes back all-0s or all-1s and never reacts to a sensor. This cost a very long bench
  session to find; see "Connector pinout" below.
- These boards are **not** talking Stern's proprietary Spike CPU↔node RS-485 bus by themselves.
  That's a different, unrelated link — see "What this is *not*" below.
- The board examined here is just a public, off-the-shelf **74HC165 shift register** reading 7-8
  opto channels in parallel and shifting them out serially — a completely standard, decades-old
  pattern, not a Stern invention.
- If your board's connector is silkscreened `VCC`/`RCK`/`SCK`/`MISO`/`GND` (or similar), you can
  read it with any microcontroller's SPI peripheral. No Stern hardware, no reverse engineering of
  an undocumented protocol.
- What genuinely isn't documented anywhere (Stern included) is **which bit corresponds to which
  physical opto channel**, and each channel's active-high/low polarity — that's specific to how
  the board was laid out and has to be traced/verified on your own unit. The verified map for a
  520-8516-00 is in the section on that revision below.

## The board family

Stern has sold several trough opto board revisions across the SPIKE/SPIKE 2 line, referenced in
parts listings as:

| Part | Description (as sold) |
|---|---|
| 520-5344-00 / 520-5345-00 | Trough Serial Opto Transmitter (early SPIKE) |
| 520-7001-00 | Node Board Serial Opto Trough Receiver Assembly (SPIKE II) |
| 520-1051-00 | Trough Opto Receiver Extension Node Board (replaces 520-7001-00) |
| 520-8516-00 | SPIKE 2 Trough Serial Opto Receiver (current, replaces 520-1051-00) |

Stern has not published schematics or a parts list for any of these (confirmed via their own
support/PinWiki — see Sources). A Stern schematic for the 520-7001-00A was later obtained and is in
this repo (`docs/520-7001-00A-TROUGH-RECEIVER-BOARD.pdf`); it is what shows the inverted `RCK`
routing. The board physically examined for this writeup is silkscreened
**520-7001-00A**, "...RD TROUGH" ("[STANDA]RD TROUGH" or similar, partially obscured by a label).
Whether the newer 520-1051-00/520-8516-00 revisions use the same shift-register design was an
open question when this section was first written — **since independently checked on a
520-8516-00 unit**, see "A different board revision (520-8516-00)" below for what's actually
confirmed there (a real 74HCT165 shift register is present, but with genuine differences from
this section's assumptions - don't assume this writeup transfers directly without reading that
section too). 520-1051-00 remains unchecked.

## What this is *not*

Genuine Stern Spike/Spike 2 machines have a separate, actually-proprietary link: node boards talk
RS-485 over Cat5e back to a Spike CPU board, and that protocol has only been partially
reverse-engineered (see Mission Pinball Framework's `spike:` platform, which rides that bus via a
real Spike CPU board's own USB debug/bridge port — it does not synthesize the bus from scratch).
**That bus is not what's on this trough board's connector.** If you don't have a genuine Spike
CPU + node board and were about to go source one just to read a trough, stop — you very likely
don't need it. The two links get conflated easily because both use the word "serial" and both are
Stern/Spike-branded; they are unrelated protocols solving different problems (inter-board bus
vs. local sensor serialization on one small board).

In a real Stern machine the trough board isn't read by the Spike CPU at all. Stern's SPIKE System
Manual classifies it as a **"node extension"**: it hangs off a full node board (e.g. a Playfield
Node) over a short serial cable, and that node's own microcontroller reads it, using Stern's closed
firmware. That's why no bit-level description of the read exists anywhere public — which turned out
not to matter, since the board is just a shift register behind a buffer (archived copy of the
manual's relevant pages: `docs/references/raw/stern-spike-system-manual/content.md`).

## What it actually is

Two ICs on the board examined:

- **U1 — NXP 74HCT165D**: a standard, publicly-datasheeted 8-bit parallel-in/serial-out shift
  register. This is the entire "serial" mechanism — decades-old, used in a huge range of
  unrelated electronics, nothing Stern-specific about it.
- **U2 — NXP 74HC540D**: a standard octal inverting buffer. Seven of its eight channels condition
  the opto sensor signals before they reach U1's parallel inputs. **The eighth channel inverts
  `RCK`** on its way to U1's `SH/LD` — the detail that decides how the board has to be read.

So "Trough Serial Opto Receiver" means: up to 8 opto sensors' states get parallel-loaded into a
shift register and clocked out over one wire, instead of running 8 individual wires back to
whatever's reading them. That's it — a wiring-reduction trick, not a data protocol Stern
designed.

### Connector pinout

The board's populated connector is silkscreened directly with the signal names — no probing or
guessing required:

| Pin | Meaning |
|---|---|
| `VCC` | 5V supply |
| `GND` | ground |
| `SCK` | shift clock — 74HC165's `CLK` |
| `RCK` | register/latch clock — reaches the 74HC165's `SH/LD` **inverted**, through a 220Ω resistor and one channel of the 74HC540. `RCK` HIGH = parallel load, LOW = shift |
| `MISO` | serial data out — 74HC165's `QH` |

This naming (`MISO`/`SCK`/`RCK`) is the standard convention hobbyists use for bare 74HC165
breakout boards, and it maps onto any microcontroller's hardware SPI peripheral — **except that the
latch polarity is the reverse of a bare 74HC165 breakout**:

1. Keep `RCK` **low** while idle (register in shift mode).
2. Pulse `RCK` **high** for a few µs to load the current sensor states, then return it **low**.
3. Clock `SCK` 8 times (e.g. an SPI `transfer(0x00)` in master mode, SPI Mode 0, MSB first) while
   reading `MISO` — the 74HC165 presents input **H first, A last**.
4. The resulting byte has one bit per opto channel. There are 7 opto channels, so one bit is a
   spare input tied to a fixed level (confirmed on the 520-8516-00: the first bit out is always 0).

Drive `RCK` from a 5V-logic source. It enters a plain 74HC (not HCT) buffer, which at 5V needs
about 3.5V to see a valid high — a 3.3V microcontroller or a Bus Pirate v3's `AUX` pin (which only
reached ~3.2V at the board) isn't enough.

**How the wrong polarity shows up:** if you pulse `RCK` low and clock with it high, the register
sits in load mode, ignores the clock, and `MISO` shows input H the whole time — so every byte has all
8 bits identical, no matter what you block. If you ever see only `0x00`/`0xFF`, suspect the latch
polarity before suspecting the chip.

On the 520-7001-00A, `MOSI` isn't part of the connector. On the 520-8516-00 it is broken out, but
has no effect on the read.

## What's still genuinely unknown per-unit

Two things Stern doesn't document anywhere and that this writeup can't hand you either, because
they're facts about how a specific board was laid out, not about the shift-register mechanism:

- **Which bit is which physical opto channel.** The shift order is fixed by the 74HC165 datasheet
  (D7 first), but whether D7 is trough-position-1 or trough-position-6 or the jam sensor is board
  layout, and wasn't traced here beyond confirming the chip identity and connector labels.
- **Each channel's active-high/low polarity** — whether "beam broken" (ball present) reads as 1
  or 0 depends on U2's buffering and isn't safe to assume from the 74HC165 datasheet alone.

For the 520-8516-00 both are now known — see its section below. For any other revision, trace or
verify both empirically (hand-block one opto channel at a time and watch which bit of the read
byte changes) before trusting a mapping. Don't ship a build that assumes an unverified
mapping — get it wrong and a working trough position can silently misreport, which is a bad
failure mode for a machine that trusts the trough for ball-count logic.

## A misdiagnosis to avoid: the "dead U1" that was really an inverted latch

On the 520-7001-00A, `MISO` read a constant byte no matter what was blocked, while power, ground,
wiring, clean SPI waveforms at the connector, and live sensor data on U1's own input legs were all
verified. That was diagnosed as **U1 (the 74HC165) being dead** — good inputs, dead output.

**That diagnosis was most likely wrong.** Every test pulsed `RCK` low and clocked with it high,
which — because the board inverts `RCK` — held the register in load mode the whole time. In load
mode the clock is ignored and `QH` just shows input H — confirmed to be a spare, fixed input on the
520-8516-00, and apparently unused on the 520-7001-00A's schematic too (its 74HC540 has 7 sensor
channels plus the `RCK` inverter). That produces exactly "good inputs, constant output," including in the
"latch-without-clocking" test that seemed to prove the chip dead. A brand-new 520-8516-00 showed the
identical symptom, and reading it with the corrected polarity worked immediately. The 520-7001-00A
itself hasn't been retested yet.

So: if a board like this returns a constant byte, **check the `RCK` polarity first**. Only if the
byte stays constant with `RCK` idling low and pulsed high is a dead 165 worth considering.

**Two ways forward if the chip really is dead:**

1. **Bypass the shift register entirely.** U1's own `D0`–`D7` parallel input pins (or U2's output
   pins directly upstream of them) already carry a clean, per-channel, buffered 0/5V digital
   signal — exactly what you actually want. Tap those directly into your switch matrix instead of
   reading the serial output, and you don't need U1 working, or even present, at all. This trades
   away the shift register's wiring-reduction benefit (one wire vs. up to 8) but needs no repair
   and no protocol/timing work.
2. **Replace U1.** It's a standard, cheap, widely-stocked part (well under €0.50/unit at typical
   quantities). Order the exact same part if you can match it from the chip's own markings
   (here: **Nexperia 74HCT165D, SOIC-16**) — but a plain, non-`T` **74HC165** in the same SOIC-16
   package works too in a circuit like this one, where everything driving U1 is already
   CMOS-level (a microcontroller's own GPIO, and U2's CMOS-output buffer) rather than true TTL —
   the HC/HCT input-threshold difference only matters when a TTL-level source is involved. Verify
   your own board's inputs are similarly CMOS-driven before assuming this substitution is safe.

## A different board revision (520-8516-00): confirmed differences, and a working read

A second project unit, silkscreened **`520-8516-00`** (the current SPIKE 2 part number), has been
read successfully with the corrected `RCK` polarity. It differs from the 520-7001-00A in a few
confirmed ways:

- **Two connectors**: `CN1` ("SERIAL IN", pin order `VCC, RCK, SCK, MOSI, MISO, GND`) and `CN3`
  ("SERIAL OUT", same signals in mirrored order). **`CN1` is the one to read from** — that's where
  the working read was done. `CN3` is presumably the cascade to a further board and isn't needed.
  `CN1` also has an unlabelled 7th pin position that carries nothing, even in a real machine.
- **Three ICs**: U1 = 74HC540D (sensor buffering plus the `RCK` inversion), U2 = 74HCT165D (the
  shift register), U3 = 74HC14D hex Schmitt-trigger inverter (role untraced; on the older board's
  schematic the equivalent Schmitt-trigger pair conditions `MISO` only). Note the U1/U2 numbering
  is swapped relative to the 520-7001-00A. The `RCK` path was confirmed with a meter in Ω mode:
  `CN1` `RCK` → 220Ω → U1 pin 9 (A8) → U1 pin 11 (Y8) → U2 pin 1 (`SH/LD`).
- `CN2` is a small 3-pin power-only tap (`JAM`/`GND`/`VCC`). The jam sensor is *not* wired
  separately — it goes through the shift register like the other six.
- `MOSI` is broken out, but has no effect on the read.

**Verified bit map** (blocking one sensor at a time; first bit shifted out = raw bit 7):

| Raw bit | Signal |
|---|---|
| 7 | spare input H — always 0 |
| 6 | jam |
| 5 | trough position 1 |
| 4 | trough position 2 |
| 3 | trough position 3 |
| 2 | trough position 4 |
| 1 | trough position 5 |
| 0 | trough position 6 |

All seven channels read **1 = clear, 0 = blocked**. With everything clear the byte is `0b01111111`.

### Probing reference (pin numbers)

Pin 1 is at the dot/bevel on each chip. SOIC pins run down one side from pin 1 and back up the
other, so the last pin sits directly opposite pin 1.

| Chip | Pins worth knowing |
|---|---|
| 74HCT165D (the shift register; U2 on the 520-8516-00, U1 on the 520-7001-00A), 16 pins | 1 `SH/LD` (from `RCK`, inverted) · 2 `CLK` (`SCK`) · 3–6 inputs E–H · 7 `QH̄` (complementary out) · 8 GND · **9 `QH` (serial out)** · 10 `SER` · 11–14 inputs A–D · 15 `CLK INH` · 16 VCC |
| 74HC540D (U1 on the 520-8516-00), 20 pins | 1/19 output enables · 2–9 inputs A1–A8 (**9 = A8, fed by `RCK` through 220Ω**) · 10 GND · 11–18 outputs Y8–Y1 (**11 = Y8, drives `SH/LD`**) · 20 VCC |
| 74HC14D (U3 on the 520-8516-00), 14 pins | inputs 1, 3, 5, 9, 11, 13 · 7 GND · 14 VCC |

Measured on a 520-8516-00, power off: `CN1` `RCK` → U1 pin 9 = 219.5Ω (the series resistor), U1
pin 11 → U2 pin 1 = 0.1Ω. Use the meter's Ω mode, not continuity mode — most meters stay silent
through 220Ω.

## Reading it from MPF without a microcontroller: `spi_bit_bang` (untested)

Not used in Portal Pinball V4.0 (the ATmega bridge was chosen instead, `CHANGES.md` #29), but a
real option for anyone running Mission Pinball Framework. MPF 0.80 ships a `spi_bit_bang` platform
(`mpf/platforms/spi_bit_bang.py`, config spec in `mpf/config_spec.yaml`) that reads a 74HC165-style
register by bit-banging it through *another* platform's hardware: two MPF `digital_outputs` for the
latch and clock, and one ordinary switch input for the data line. OPP's own firmware has no
shift-register input mode (MPF's OPP platform only knows solenoid, input, incandescent, matrix and
neopixel wings), so on OPP this is the only no-extra-microcontroller way.

**How it maps onto this board.** OPP outputs are low-side FETs, so each needs a pull-up resistor
to 5V (roughly 1–2.2kΩ; check the Stern pin reaches ≥3.5V, since `RCK` enters a plain 74HC540).
With pull-ups, "output enabled" = LOW and "disabled" = HIGH. That matches the board: the platform
holds its chip-select *disabled* (HIGH = load) between reads and *enabled* (LOW = shift) while
clocking — exactly the inverted `RCK` this board wants. The clock idles HIGH and each 1ms pulse
ends on a rising edge, when the 74HC165 shifts. The first bit read is input H (the unused bit 7),
MSB first, so switch numbers `"0"`–`"6"` equal raw bits 0–6. An OPP input reads active when pulled
low, so the bits arrive inverted: a switch is active when its sensor is **blocked**.

```yaml
# Untested sketch - output/input numbers are placeholders
digital_outputs:
  trough_rck: {number: "<free OPP output>", type: driver}   # -> CN1 RCK, pull-up to 5V
  trough_sck: {number: "<free OPP output>", type: driver}   # -> CN1 SCK, pull-up to 5V
switches:
  trough_miso: {number: "<free OPP input>"}                 # <- CN1 MISO
  s-trough1: {number: "5", platform: spi_bit_bang}
  s-trough2: {number: "4", platform: spi_bit_bang}
  s-trough3: {number: "3", platform: spi_bit_bang}
  s-trough4: {number: "2", platform: spi_bit_bang}
  s-trough5: {number: "1", platform: spi_bit_bang}
  s-trough6: {number: "0", platform: spi_bit_bang}
  s-trough-jam: {number: "6", platform: spi_bit_bang}
spi_bit_bang:
  cs_pin: trough_rck
  clock_pin: trough_sck
  miso_pin: trough_miso
  inputs: 8
  bit_time: 50ms   # default; must exceed OPP's switch-report latency (OPP poll_hz defaults to 100)
```

**Trade-offs versus a microcontroller bridge:**
- **For:** no microcontroller, firmware or flashing; polarity is just each switch's `type` in MPF.
  Uses 1 OPP input instead of 7.
- **Against:** slow — every bit is a round trip through MPF and OPP's serial link, so a full read
  takes about 0.5s at the default `bit_time`. Fine for trough ball counting, much laggier than a
  bridge's ~10ms. Reads only while MPF runs, and the switches can't be used in OPP hardware rules.
- Needs 2 free OPP driver outputs plus pull-ups; those outputs must not have flyback diodes to a
  coil rail that can be switched off (that would clamp the logic lines low when coil power is off).
- At startup the platform reports every switch inactive until its first read completes; watch for
  spurious ball-count events on boot.

## Bench tools: what worked, and the gotchas

- **Arduino Uno (5V logic)** — the tool that finally read the board. Its hardware SPI pins are
  D13 = `SCK`, **D12 = `MISO` (input)**, D11 = `MOSI` (output). Swapping D11/D12 makes the Uno
  drive the board's output line, and every read comes back as a stuck constant.
- **USB logic analyzer** (Saleae-clone, `fx2lafw` driver via `sigrok-cli`) — good for proving the
  waveforms at the connector are clean. Two limits: this clone stops after roughly 470k samples per
  capture (about 0.47s at 1MHz, however long you ask for), so take several short captures; and a
  clean waveform at the connector proves nothing about what the board does with it internally — it
  couldn't have revealed the on-board `RCK` inversion.
- **Bus Pirate v3.6** (SparkFun, firmware 5.10) — **not suitable for driving `RCK`**. Its `AUX`
  pin (and `CS`, as it was configured) reached only ~3.2V at the board, below the ~3.5V a 74HC540
  needs at 5V; its "Normal" push-pull output type is 3.3V-high by design. The only way to a ~4.8V
  high is open-drain with the pull-ups referenced to 5V (jumper `VPU` to `+5V`), which worked for
  `SCK`/`MOSI`. Its mode-setup menus auto-select defaults within a fraction of a second unless the
  answers are already sent, which makes them hard to script. And in DIO mode, turning the pull-ups
  on also raises any undriven line — including `CLK`, which is a clock edge. That is the most
  likely source of this investigation's false "output floats during load" finding (not separately
  retested). Workaround used: drive `RCK` by hand with a wire moved between the board's `GND` and
  `+5V`.
- **Bus Pirate 5** — would avoid those limits: its I/O pins go through 74LVC1T45 level-shifting
  buffers powered from its own settable 1–5V supply, so a driven high is a real 5V (each I/O pin
  has a 330Ω series resistor, plenty for logic inputs). Archived:
  `docs/references/raw/buspirate5-hardware-rev10/content.md`.
- **Multimeter** — `RCK`'s 220Ω series resistor keeps continuity mode silent; measure in Ω mode.

## Bench history (Portal Pinball V4.0)

Condensed. The full blow-by-blow (every test, including the retracted theories) is preserved in
git: `plans/read-opto.md` as of commit `21a9e8b`; decisions are logged in `CHANGES.md` #27–#29.

**2026-09-11 — old board (520-7001-00A).** The first bridge (ATmega328P/Uno) read a constant byte.
Power, ground, wiring, the Uno's own SPI (a loopback test), clean `RCK`/`SCK` waveforms at the
connector, and live sensor data on the 165's input legs were all verified, so the 165 was declared
dead. Most likely a misdiagnosis — the firmware already used the inverted latch polarity. That
board hasn't been retested with the fix.

**2026-09-26 — new board (520-8516-00).** A new board, seen working in a real Stern machine,
showed the same constant byte. A long session with a Uno, the logic analyzer and a Bus Pirate v3.6:
- *Real bugs found:* the Uno's `MISO`/`MOSI` wires swapped; the Bus Pirate unable to drive `RCK`
  to a valid high (see "Bench tools").
- *Ruled out:* anything on `MOSI` (all 256 byte values, fast and each held for 24+ seconds, and
  held low/high), power-up sequencing, both `SCK` idle polarities, `CN1`'s unlabelled 7th pin (no
  wire even in a real machine), and `CN3` (it read a constant `1` where `CN1` read `0`; never
  explained, and not needed).
- *False leads:* an address/command byte on `MOSI`; the output "tri-stating during load" and a
  "hidden component" between the register and the connector (both built on the pull-up artifact).
  Two rounds of independent review agents sharpened the gaps but didn't find the cause.
- *Resolution:* a fresh review went back to Stern's schematic for the older board, already in the
  repo, and saw `RCK` routed through the 74HC540. Confirmed on the new board with a meter,
  firmware flipped to idle `RCK` low / pulse high, and the read worked first time. The bit map
  came from blocking one sensor at a time.

**Lessons:**
- Trace where every control line actually goes — schematic first, then a meter in Ω mode — before
  experimenting with timing and protocol. It would have saved most of a day.
- A 74HC165 returning all-identical bits is being clocked while held in load mode.
- "Signals verified at the connector" is not "protocol verified": on-board logic can invert or
  reroute them.
- When using a pull-up to test whether a pin is driven, make sure the pull-up can't also move a
  clock line.

## Worked example

This repo (Portal Pinball V4.0) has a full reference implementation built on the above, bridging
this board to an OPP-based control system with no Stern hardware and no MPF Spike platform
involved:

- [`plans/read-opto.md`](../plans/read-opto.md) — the build plan for the bridge: parts, wiring,
  programming, build order and verification.
- [`docs/520-7001-00A-TROUGH-RECEIVER-BOARD.pdf`](520-7001-00A-TROUGH-RECEIVER-BOARD.pdf) — Stern's
  schematic for the older revision, showing the `RCK` → 74HC540 → `SH/LD` inversion.
- [`design/physical-checklists/trough-opto-bridge.html`](../design/physical-checklists/trough-opto-bridge.html) —
  a printable (A4) build sheet: parts list, DIP-28 pinout diagram, breadboard wiring tables.
- [`tools/flash-atmega328p.ps1`](../tools/flash-atmega328p.ps1) — scripts flashing a bare
  ATmega328P-PU as the bridge chip via an Arduino-as-ISP, using MiniCore for correct
  internal-oscillator fuse values instead of hand-typed `avrdude` fuse bytes.
- [`tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino`](../tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino) —
  the bridge firmware: reads the shift register over hardware SPI, debounces, and mirrors the
  channels onto GPIO pins for the downstream switch matrix. Includes a serial-debug mode
  specifically for the per-unit bit-mapping/polarity tracing described above.
- `tools/atmega328p-trough-bridge/diag-slow-toggle/`, `diag-hold-latch/`, `diag-multichannel-read/`,
  `diag-mosi-patterns/` — small bench-only sketches from the investigation: a multimeter-visible
  slow toggle for `RCK`/`SCK`, a latch-then-hold for probing `QH` (which on the 520-8516-00 only ever
  shows the spare input, so it can't show sensor data), a multi-channel pin streamer, and a
  `MOSI` byte sweep. Their latch polarity has been corrected to match the board.

The approach generalizes beyond ATmega328P/OPP — any microcontroller with an SPI peripheral (or
even a bit-banged 3-wire interface) and a way to drive a few GPIOs works the same way.

## Sources

- [520-8516-00 — SPIKE 2 Trough Serial Opto Receiver (Stern shop)](https://shop.sternpinball.com/products/spike-2-trough-serial-opto-receiver)
- [520-5344-00 — Trough Serial Opto Transmitter Board (Stern shop)](https://shop.sternpinball.com/products/520-5344-00-trough-serial-opto-transmitter-board)
- [Trough Serial Opto Receiver Extension 520-1051-00 replaces 502-7001-00 (Nitro Pinball USA)](https://nitropinballusa.com/products/node-board-serial-opto-receiver-stern-spike-ii-1)
- [Node Board Serial Opto Trough Receiver Assembly 520-7001-00 (Little Shop Of Games)](https://littleshopofgames.com/shop/boards/stern-boards/node-board-serial-opto-trough-receiver-assembly-for-stern-spike-ii-pinball-machine-520-7001-00-2/)
- [Stern SPIKE™ System Repair — PinWiki](https://pinwiki.com/wiki/index.php/Stern_SPIKE%E2%84%A2_System_Repair)
  (archived copy: `docs/references/raw/pinwiki-stern-spike-repair/content.md`) —
  confirms Stern hasn't supplied schematics/part lists for these boards, and covers the *separate*
  genuine node-bus (RS-485 over Cat5e) that this writeup explicitly is not about.
  - How to configure MPF for Stern SPIKE hardware — Mission Pinball Framework docs
- NXP 74HC/HCT165 datasheet (8-bit parallel-in/serial-out shift register) — any major distributor
  (Nexperia, TI, ON Semi second-source parts all interoperate to the same public spec).
- NXP 74HC540 datasheet (octal inverting buffer/line driver).
- [Stern SPIKE System Manual (775-7640-00)](https://www.sternpinball.com/wp-content/uploads/2020/11/SPIKE-System-Manual.pdf)
  (archived: `docs/references/raw/stern-spike-system-manual/content.md`; full PDF:
  `docs/SPIKE-System-Manual.pdf`) — the "node extension" classification.
- [Hardware Design (5 REV 10) — Bus Pirate 5 docs](https://docs.buspirate.com/docs/hardware/bp5rev10/hardware/)
  (archived: `docs/references/raw/buspirate5-hardware-rev10/content.md`) — Bus Pirate 5 I/O levels.
- Stern's schematic for the 520-7001-00A: `docs/520-7001-00A-TROUGH-RECEIVER-BOARD.pdf`.
