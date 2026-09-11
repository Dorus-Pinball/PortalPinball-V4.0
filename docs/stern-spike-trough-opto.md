# Reading a Stern Spike-era trough opto board without genuine Spike hardware

A reference for anyone who has salvaged a Stern trough assembly (SPIKE or SPIKE 2 era) for a
homebrew machine and wants to read its opto sensors from non-Stern control hardware (OPP, a
generic microcontroller, etc.) instead of Stern's own CPU/node system. Written up here because
the "Serial Opto Receiver" name is misleading and the obvious assumption — that it needs Stern's
proprietary node-bus protocol — is wrong for at least one confirmed board revision. If you're
building a Portal Pinball V4.0-style machine and landed here from that project: this file is the
general-purpose writeup; `plans/read-opto.md` in this repo is the project-specific plan built on
top of it, and `tools/atmega328p-trough-bridge/` is a working reference implementation.

**Confirmed by physically examining one board** (part 520-7001-00A, see below) — the rest of the
part-number family is inferred from how Stern/resellers describe and price them, not independently
opened and checked. If you have a different revision, verify before assuming it matches.

## TL;DR

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
  the board was laid out and has to be traced/verified on your own unit.

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
support/PinWiki — see Sources). The board physically examined for this writeup is silkscreened
**520-7001-00A**, "...RD TROUGH" ("[STANDA]RD TROUGH" or similar, partially obscured by a label).
Whether the newer 520-1051-00/520-8516-00 revisions use the same shift-register design is
**not confirmed** — worth independently checking if you have one of those instead, rather than
assuming this writeup transfers directly.

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
- **U2 — NXP 74HC540D**: a standard octal inverting tri-state buffer, almost certainly
  conditioning the opto comparator outputs before they reach U1's parallel inputs.

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
| `RCK` | register/latch clock — 74HC165's `SH/LD` (pulse to parallel-load the 8 sensor states) |
| `MISO` | serial data out — 74HC165's `Q7` |

This naming (`MISO`/`SCK`/`RCK`) is the standard convention hobbyists use for bare 74HC165
breakout boards, and it maps directly onto any microcontroller's hardware SPI peripheral:

1. Pulse `RCK` low then high to latch the current sensor states into the shift register.
2. Clock `SCK` 8 times (e.g. an SPI `transfer(0x00)` in master mode, SPI Mode 0, MSB first) while
   reading `MISO` — the 74HC165 presents bit **D7 first, D0 last**, which lines up naturally with
   SPI Mode 0's sample timing.
3. The resulting byte has one bit per opto channel (fewer than 8 if the trough has fewer than 8
   positions — spare bits are presumably tied to a fixed level, unconfirmed).

`MOSI` isn't part of this connector and doesn't need to be connected to anything on the Stern
board — the 165 has no serial-cascade input broken out here (its `DS`/`CLK INH` pins are
presumably tied off internally; not confirmed).

## What's still genuinely unknown per-unit

Two things Stern doesn't document anywhere and that this writeup can't hand you either, because
they're facts about how a specific board was laid out, not about the shift-register mechanism:

- **Which bit is which physical opto channel.** The shift order is fixed by the 74HC165 datasheet
  (D7 first), but whether D7 is trough-position-1 or trough-position-6 or the jam sensor is board
  layout, and wasn't traced here beyond confirming the chip identity and connector labels.
- **Each channel's active-high/low polarity** — whether "beam broken" (ball present) reads as 1
  or 0 depends on U2's buffering and isn't safe to assume from the 74HC165 datasheet alone.

Trace or verify both empirically (hand-block one opto channel at a time and watch which bit of
the read byte changes) before trusting a mapping. Don't ship a build that assumes an unverified
mapping — get it wrong and a working trough position can silently misreport, which is a bad
failure mode for a machine that trusts the trough for ball-count logic.

## Worked example

This repo (Portal Pinball V4.0) has a full reference implementation built on the above, bridging
this board to an OPP-based control system with no Stern hardware and no MPF Spike platform
involved:

- [`plans/read-opto.md`](../plans/read-opto.md) — the design writeup and rationale, including why
  the RS-485-bus assumption was wrong and how it was corrected.
- [`design/physical-checklists/trough-opto-bridge.html`](../design/physical-checklists/trough-opto-bridge.html) —
  a printable (A4) build sheet: parts list, DIP-28 pinout diagram, breadboard wiring tables.
- [`tools/flash-atmega328p.ps1`](../tools/flash-atmega328p.ps1) — scripts flashing a bare
  ATmega328P-PU as the bridge chip via an Arduino-as-ISP, using MiniCore for correct
  internal-oscillator fuse values instead of hand-typed `avrdude` fuse bytes.
- [`tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino`](../tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino) —
  the bridge firmware: reads the shift register over hardware SPI, debounces, and mirrors the
  channels onto GPIO pins for the downstream switch matrix. Includes a serial-debug mode
  specifically for the per-unit bit-mapping/polarity tracing described above.

The approach generalizes beyond ATmega328P/OPP — any microcontroller with an SPI peripheral (or
even a bit-banged 3-wire interface) and a way to drive a few GPIOs works the same way.

## Sources

- [520-8516-00 — SPIKE 2 Trough Serial Opto Receiver (Stern shop)](https://shop.sternpinball.com/products/spike-2-trough-serial-opto-receiver)
- [520-5344-00 — Trough Serial Opto Transmitter Board (Stern shop)](https://shop.sternpinball.com/products/520-5344-00-trough-serial-opto-transmitter-board)
- [Trough Serial Opto Receiver Extension 520-1051-00 replaces 502-7001-00 (Nitro Pinball USA)](https://nitropinballusa.com/products/node-board-serial-opto-receiver-stern-spike-ii-1)
- [Node Board Serial Opto Trough Receiver Assembly 520-7001-00 (Little Shop Of Games)](https://littleshopofgames.com/shop/boards/stern-boards/node-board-serial-opto-trough-receiver-assembly-for-stern-spike-ii-pinball-machine-520-7001-00-2/)
- [Stern SPIKE™ System Repair — PinWiki](https://pinwiki.com/wiki/index.php/Stern_SPIKE%E2%84%A2_System_Repair) —
  confirms Stern hasn't supplied schematics/part lists for these boards, and covers the *separate*
  genuine node-bus (RS-485 over Cat5e) that this writeup explicitly is not about.
  - How to configure MPF for Stern SPIKE hardware — Mission Pinball Framework docs
- NXP 74HC/HCT165 datasheet (8-bit parallel-in/serial-out shift register) — any major distributor
  (Nexperia, TI, ON Semi second-source parts all interoperate to the same public spec).
- NXP 74HC540 datasheet (octal inverting buffer/line driver).
