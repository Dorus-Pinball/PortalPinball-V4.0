# Reading a Stern Spike-era trough opto board without genuine Spike hardware

A reference for anyone who has salvaged a Stern trough assembly (SPIKE or SPIKE 2 era) for a
homebrew machine and wants to read its opto sensors from non-Stern control hardware (OPP, a
generic microcontroller, etc.) instead of Stern's own CPU/node system. Written up here because
the "Serial Opto Receiver" name is misleading and the obvious assumption — that it needs Stern's
proprietary node-bus protocol — is wrong for at least one confirmed board revision. If you're
building a Portal Pinball V4.0-style machine and landed here from that project: this file is the
general-purpose writeup; `plans/read-opto.md` in this repo is the project-specific plan built on
top of it, and `tools/atmega328p-trough-bridge/` is a working reference implementation.

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
  schematic the equivalent Schmitt-trigger pair conditions `MISO` only). Note the U1/U2 numbering is swapped relative to the 520-7001-00A. The `RCK` path
  was confirmed with a meter in Ω mode: `CN1` `RCK` → 220Ω → U1 pin 9 (A8) → U1 pin 11 (Y8) → U2
  pin 1 (`SH/LD`). The 220Ω series resistor means continuity mode won't beep — measure resistance.
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

**A pitfall worth knowing if you use a pull-up to check whether a pin is driven:** during this
investigation, enabling a Bus Pirate's pull-ups made `MISO` change and seemed to show the output
"floating." Most likely (not separately retested) it was the pull-up also raising the undriven `SCK` line — a clock edge that
shifted the register. If you do this test, make sure the clock line is actively held while you do.

## Worked example

This repo (Portal Pinball V4.0) has a full reference implementation built on the above, bridging
this board to an OPP-based control system with no Stern hardware and no MPF Spike platform
involved:

- [`plans/read-opto.md`](../plans/read-opto.md) — the design writeup and rationale, including why
  the RS-485-bus assumption was wrong, the full bench history, and the "Resolution (2026-09-26)"
  section where the inverted latch was found.
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
