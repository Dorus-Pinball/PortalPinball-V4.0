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
   *(Wrong in one crucial detail, found 2026-09-26: `RCK` reaches `SH/LD` **inverted**, through the
   74HC540 — see "Resolution (2026-09-26)". Tracing it would have saved a very long bench session.)*

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
standalone support circuit to just the chip itself. Do this explicitly on every chip regardless of
history: these are inventory spares, and a chip previously configured for an external crystal will
sit dead with no clock and no error message if the fuses aren't rewritten first — silently waiting
for a crystal that was never connected.

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
pulse `RCK` (pin 14) **high-then-low** to latch (the board inverts `RCK` before the shift
register's `SH/LD` — see "Resolution (2026-09-26)" below; this line originally said low-then-high,
which was the bug behind every failed read), then clock one byte through SPI (e.g. write `0x00`
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

## Bench findings (2026-09-11): U1 is dead on this specific board

> **Probably wrong — see "Resolution (2026-09-26)" below.** This test used the same inverted
> latch polarity that was later found to be the real bug, which would hold the register in load
> mode during every clock and produce exactly this "good inputs, dead output" signature. Kept as
> the historical record; this board has not yet been retested with the corrected polarity.

Built the ATmega328P/Uno-based reader and bench-tested against the real trough board. Systematic
elimination (multimeter continuity/DC checks, then a cheap USB logic analyzer for waveform-level
confirmation once DC-level checks stopped being conclusive) ruled out, in order: power, ground,
wiring continuity, the Uno's own SPI read pipeline (proven directly with a loopback jumper test),
and `RCK`/`SCK` reaching the board correctly (confirmed as clean, correctly-timed SPI Mode 0
signals — a proper latch pulse plus an 8-toggle 250kHz clock burst — via the logic analyzer, not
just DC level).

What's left: **U1 (the 74HCT165) itself is dead.** Its parallel data inputs (`D0`–`D7`) carry real,
correctly-differentiated live sensor data (confirmed by both direct multimeter probing at U1's own
legs and a logic-analyzer capture showing genuine hand-timescale toggles while blocking sensors) —
so U2 and the opto/comparator chain upstream are all fine. But `QH` (serial out) never reflects any
of it, under any test, including an asynchronous-load-only test that should show `QH` mirroring the
first data bit immediately with no clocking required. Good inputs, dead output — the chip itself.
Full general writeup of this failure mode (useful beyond this project) is in
`docs/stern-spike-trough-opto.md`.

**Two ways forward, both worth keeping in `TODO.md`:**

1. **Hardwire U2's/U1's buffered per-channel legs directly into OPP**, bypassing the dead shift
   register (and the whole SPI-bridge approach) entirely — trades away the one-wire serialization
   this plan was built around, but needs no chip repair, no bridge firmware, no ATmega328P at all.
   Each leg is already a clean 0/5V per-channel signal, same electrical shape OPP's switch wing
   already expects. Needs the same "trace which physical leg is which trough position" calibration
   work either way.
2. **Replace U1** and keep the original SPI-bridge plan above. Confirmed correct replacement part:
   **Nexperia 74HCT165D, SOIC-16** (exact match to the chip's own markings) — available from
   sinuss.nl among others, ~€2.25/5 units. A plain (non-`T`) 74HC165 in the same SOIC-16 package
   also works in this specific circuit, since everything driving U1 here is already CMOS-level
   (the bridge microcontroller's GPIO, and U2's CMOS-output buffer) rather than true TTL, so the
   HC/HCT input-threshold difference doesn't matter — confirmed cheaper option
   (~€1.76/10 on AliExpress) if genuine stock isn't needed.

## Bench findings (2026-09-26): new board (520-8516-00), extensive Arduino + Bus Pirate session

> **Solved later the same day — see "Resolution (2026-09-26)" below.** The root cause was
> inverted `RCK` polarity. Several conclusions in this section are retracted there (the
> "output floats during load" discovery, the "hidden component" theory, and the next-steps list).
> Kept as the historical record of what was tried.

A brand-new replacement board was purchased instead of repairing the old salvaged unit's dead
U1. Silkscreened **520-8516-00** — the *current* SPIKE 2 "Trough Serial Opto Receiver" part
number, **not** `520-7001-00A` (the revision the rest of this plan and
`docs/stern-spike-trough-opto.md` were originally written against). The owner has personally
observed this exact physical board unit operating correctly in a real, running Stern machine —
treated as ground truth throughout this session; the board itself is not in question.

**Board differs from the old revision in real, confirmed ways:**
- Three ICs, not two: **U1 = 74HC540D** (octal buffer, conditions opto sensor signals into U2's
  parallel inputs), **U2 = 74HCT165D** (the shift register — confirmed via close-up photo of the
  chip's own printed marking), **U3 = 74HC14D** (hex Schmitt-trigger inverter, confirmed
  unambiguously via a second close-up after an earlier misread) — U3 almost certainly conditions
  `RCK`/`SCK`/`MISO` between the connector and U1/U2, architecturally consistent with Stern's own
  schematic for the *older* board (`docs/520-7001-00A-TROUGH-RECEIVER-BOARD.pdf`, now in this
  repo), which shows two small inverter gates in the same role — though those specific gates are
  confirmed non-tri-state parts, so that schematic doesn't itself resolve the mystery below.
- **Two 6-pin connectors, not one**: `CN1` ("SERIAL IN") and `CN3` ("SERIAL OUT"), pin orders
  *mirrored* between them (`CN1`: `VCC, RCK, SCK, MOSI, MISO, GND`; `CN3`: `GND, MISO, MOSI, SCK,
  RCK, VCC`). They are **not** a simple shared/bussed pass-through — `CN1` and `CN3` were found to
  carry independently different fixed values (`CN1` read a constant `0`, `CN3` a constant `1` —
  exact logical complements, consistent with tapping a register's true/complementary outputs, not
  proof either way). `CN1` also has a confirmed 7th physical pin position beyond the 6 labeled
  signals — genuinely unpopulated, no wire even in the real Stern machine's own harness, ruling it
  out as a missing enable/select line. `CN2` is a separate small 3-pin power-only tap
  (`JAM`/`GND`/`VCC`), sharing `VCC`/`GND` (and apparently `RCK`) with `CN3` — not an independent
  data path, and **the jam sensor is not wired separately from the other 6 channels** (confirmed
  by the owner; it goes through the same shift register like everything else).
- `MOSI` is an actual connector signal here (unlike the old board, which never broke it out) — but
  exhaustively proven irrelevant (see below).

**Bugs found and fixed along the way (both real, both worth remembering for next time):**
1. **Arduino `MISO`/`MOSI` pin swap** — `D11`/`D12` were physically wired to the wrong roles early
   in bench testing, making the Uno drive what should have been an input. Symptom: `MISO` stuck at
   a constant `0x00` no matter what. Fix: swap the two wires. After the fix, reads became a real,
   non-floating constant value — proof the SPI link was alive, just still unresponsive.
2. **Bus Pirate `RCK` never reached a valid logic-high level** — driving `RCK` through the Bus
   Pirate's `AUX` pin (or, after moving it, its `CS` pin) only produced **~3.2V** at the board's
   own `RCK` pin, not the ~4.9V the board's `SCK`/`MOSI` correctly reached via the identical
   pull-up mechanism. Originally attributed to a board-side pull-down overpowering the weak
   (~10kΩ) external pull-up; an electronics-review agent later found a more parsimonious
   explanation worth trusting more — Dangerous Prototypes' own Bus Pirate docs describe `AUX` as a
   fixed ~3.3V push-pull output, not routed through the pull-up-referenced mechanism at all, and
   3.2V is suspiciously close to that rail minus a small drop. `CS`'s own output-type ("Normal"
   push-pull vs. open-drain) was never confirmably reconfigured either (see below), so it may have
   the same issue for a different reason. Either way, root cause on the Bus Pirate side is not
   fully pinned down — but the fix doesn't depend on knowing which: **manually hand-wiring `RCK`
   directly between the board's own `GND` and `+5V` pins** (bypassing the Bus Pirate's I/O for that
   signal entirely) sidesteps the question. The Bus Pirate's own 3WIRE-mode "Normal" (push-pull)
   output-type menu proved un-navigable in this firmware (every setup prompt auto-defaults within
   well under a second; repeated attempts, including pre-queued multi-line input bursts, never
   reliably landed on it) and was abandoned as a dead end. **This isn't fixable on the v3.6 even if
   that menu had worked** — its "Normal" push-pull mode is documented as `H=3.3V`, not 5V; the only
   path to a genuine ~4.9V high on this hardware is the passive pull-up-to-`VPU` scheme, which
   worked for `SCK`/`MOSI` but not `RCK`/`CS`. A **Bus Pirate 5** would genuinely solve this
   natively (confirmed against its official hardware docs, docs.buspirate.com): its I/O pins use
   74LVC1T45 level-shifting buffers powered from the board's own settable 1-5V supply, so a driven
   "high" is a real, actively-sourced logic level up to 5V, not a pull-up reference — architecturally
   the exact capability the v3.6 lacks. Worth acquiring if more Bus-Pirate-driven bench work on this
   board continues; not needed for the hand-wire workaround already in use.

**Everything tested, and it all came back negative — this is the important part.** With clean 5V
signals confirmed via both a USB logic analyzer (`sigrok-cli`/`fx2lafw`) and, later, a Bus Pirate
with hand-verified voltage levels:
- `RCK`/`SCK` reaching the board: clean, correctly-timed SPI Mode 0 waveforms (logic analyzer),
  confirmed at the board's own connector pins with a multimeter, not just at the driving tool.
- All 256 possible `MOSI` byte values, both fast-cycled (Arduino, `tools/atmega328p-trough-bridge/
  diag-mosi-patterns/diag-mosi-patterns.ino`) and each held for 24+ continuous seconds (Bus
  Pirate) — zero effect. `MOSI` held continuously low vs. continuously high for 24+ seconds — zero
  effect. (Consistent with the old board never having `MOSI` at all and reportedly working.)
- A full power-cycle from cold start, captured from the very first line of output — no transient
  or different behavior.
- **Discovered a real, previously-undocumented detail**: the output is **tri-stated (floating)
  during the register's load phase (`RCK` low) and only actively drives once `RCK` goes high**
  (confirmed via a pull-up-resistor loading test — a weak external pull-up swings the floating
  pin, but can't budge it once `RCK` is high). A CMOS push-pull output's ~tens-of-ohms drive
  impedance should dominate a 10kΩ pull-up by roughly 100:1, so this is a sound way to distinguish
  floating from driven — caveat (flagged by an electronics-review agent) that it technically proves
  "high output impedance," not literally infinite/floating, so it can't fully rule out a damaged
  output with abnormally high-but-finite impedance being partly swayed without being genuinely
  tri-stated. This is genuinely new information, not previously known for this board family.
- Despite properly exploiting that discovery (real latch, confirmed-driven output, full 8-clock
  shift, both `SCK` idle polarities, the corrected 5V `RCK`), the shifted-out byte is **completely
  flat and unresponsive** to any of the 7 physical sensors, individually and in combination,
  confirmed via careful explicit-confirmation-at-every-step protocol after early sessions had some
  timing mix-ups (blocking state changing at the same moment as a mode/RCK change, since discarded
  and redone).
- **Datasheet-confirmed dead end on one theory**: a bare 74HC/HCT165 has **no output-enable pin at
  all** — `QH` is a plain, always-actively-driven push-pull output in every mode. That means the
  float-during-load/drive-during-shift behavior found above **cannot come from U2 alone** — there
  must be a second, still-unidentified active component (or a fault) sitting between U2's `QH` and
  the `MISO` connector pin. U3 (confirmed genuine `74HC14D`, no tri-state capability either) does
  not obviously explain it either, on its own.

**Independent multi-agent review (two separate rounds, five agents total)** was used explicitly to
get a fresh read on this reasoning, given how long the session ran. Consistent findings across
both rounds: the "output floats vs. drives" distinction is real and important; the fault/gating
component has genuinely never been identified; `U2`'s own `D0`–`D7` input legs have **never been
directly probed** (every test so far instruments the `RCK`/`SCK`/`MOSI`/`MISO` side only — the
"good sensor data reaches U2" conclusion rests on the board's own indicator LEDs, which may branch
off before U2's actual input pins, not a direct probe of the claimed node); `SCK`/`MOSI`'s "~4.8V,
confirmed good" reading was a single static DC spot-check, never reconfirmed during actual dynamic
clocking, so a smaller-magnitude version of the `RCK` loading problem can't be ruled out there
either; and the individual-channel test matrix was never fully redone with the corrected 5V `RCK`
(only channels 1, 5, and 6 were — 2, 3, 4, and jam were not). Research (including getting past the
earlier 403 wall on the relevant Pinside threads via a proxy) confirmed Stern's system manual
classifies this board as a "node extension," read by a full smart Playfield Node board's own
onboard microcontroller running Stern's closed firmware — not the main Spike CPU, and genuinely
not documented anywhere publicly at the bit level. This is closed-source-only information, not
merely unfound.

**Real pin numbers for U2 (74HCT165D)**, confirmed from Stern's own schematic for the related
older board (industry-standard pinout, applies regardless of which board it's soldered to):
`SH/LD`=pin 1 (`RCK`), `CLK`=pin 2 (`SCK`), `QH̄`=pin 7 (complementary output — **not** the one to
probe), `GND`=pin 8, **`QH`=pin 9 (the true serial output — this is the one to probe)**, `SER`=pin
10 (`MOSI`), `VCC`=pin 16. Pin 1 is marked by the small dot/notch on the chip body. (Corrected
2026-09-26 by an electronics-review agent that cross-checked this against the datasheet — the
first version of this note had `QH`/`QH̄` swapped.)

**Where this leaves things** — next actions, roughly in priority order:
1. Probe `U2` pin 9 (`QH`, the true output — not pin 7, that's `QH̄`) directly at the chip while
   driving `RCK`/`SCK` as before, comparing against the connector's `MISO` in real time. Also worth
   checking directly: whether `CN1`/`CN3`'s exact-complement values (`0` vs `1`) simply come from
   one connector tapping `QH` and the other `QH̄` — a much simpler explanation than a hidden buffer
   stage, and easy to rule in/out once you're probing the chip's actual pins anyway. If pin 9 also
   stays frozen, the fault is internal
   to U2 (or its inputs); if it differs from the connector, the fault/missing signal is downstream,
   between U2 and the connector (likely in or around U3).
2. At the same time, directly probe `U2`'s `D0`–`D7` input legs while blocking each sensor — the
   one link in this whole chain that has never been independently verified, only inferred from the
   board's indicator LEDs.
3. Re-verify `SCK`/`MOSI` reach a clean level *during actual dynamic clocking*, not just as a
   static DC spot-check, to rule out a smaller version of the `RCK` loading problem.
4. Complete the per-channel test matrix (2, 3, 4, jam) with the corrected 5V `RCK` — only 1, 5,
   and 6 have been tested under the fully-corrected signal conditions.
5. If the real machine becomes accessible again, capture its actual `RCK`/`SCK`/`MOSI`/`MISO`
   waveforms with the logic analyzer for a direct, ground-truth comparison — still the single most
   conclusive test available, just not possible yet.
6. If steps 1-2 confirm U2 itself is genuinely non-responsive despite good inputs, fall back to
   this plan's original two paths below (bypass the shift register, or replace U2) — the owner has
   said they do not want to modify this specific board, so a replacement/bypass would need a
   different unit or the owner's explicit sign-off first.

## Resolution (2026-09-26): `RCK` is inverted on the board — the read works

**Root cause.** The board does not wire `RCK` straight to the shift register's `SH/LD`. It routes
it through a spare channel of the 74HC540 inverting buffer: `CN1` `RCK` → 220Ω series resistor →
U1 (74HC540) pin 9 (input A8) → inverted → U1 pin 11 (output Y8) → U2 (74HCT165) pin 1 (`SH/LD`).
Measured with the meter in Ω mode, power off: `RCK`→U1 pin 9 = 219.5Ω, U1 pin 11→U2 pin 1 = 0.1Ω.
Stern's schematic for the older board (`docs/520-7001-00A-TROUGH-RECEIVER-BOARD.pdf`) shows the
same routing (R15 → 540 A8 → Y8 labelled `LDIN` → `SH/LD`). It was in this repo the whole time;
reading it for the latch path first would have found this in minutes.

So `RCK` HIGH = parallel load and `RCK` LOW = shift, the opposite of a bare 74HC165. Every earlier
read pulsed `RCK` low and then clocked with `RCK` high, i.e. with the register held in load mode,
where the clock is ignored and `QH` just repeats input H. That is why every read ever taken had all
8 bits identical (`0x00`/`0xFF`) and never reacted to a sensor.

**Correct read sequence:** idle `RCK` LOW → pulse `RCK` HIGH (≥5µs) to load → back to LOW → clock
8 bits (SPI Mode 0, MSB first). Implemented in `tools/atmega328p-trough-bridge/
atmega328p-trough-bridge.ino` and verified on the bench with an Arduino Uno (5V logic): the first
mixed byte ever read was `0b01111111`, and blocking each sensor cleared exactly one bit.

**Bit map (520-8516-00, bench-verified by blocking one sensor at a time):**

| Raw bit (bit7 shifted out first) | Signal |
|---|---|
| 7 | unused 74HC165 input H — always 0 |
| 6 | jam |
| 5 | trough position 1 |
| 4 | trough position 2 |
| 3 | trough position 3 |
| 2 | trough position 4 |
| 1 | trough position 5 |
| 0 | trough position 6 |

All seven channels read **1 = clear, 0 = blocked** (jam included). `BIT_CHANNEL` in the firmware
is set to this map. `BIT_INVERT` is still unset: which output polarity OPP needs depends on its
`type: NC` switch config and the documented "`s-trough-jam` active = clear path" quirk, and that
should be checked against MPF's live switch states on the cabinet, not assumed.

**Retracted from the sections above:**
- *"The output floats during load and drives during shift."* Most likely an artifact (the
  explanation fits every observation, but wasn't separately retested). In the Bus Pirate's DIO
  mode `CLK` was an undriven input, so enabling the pull-up also raised `CLK`: a clock edge that
  shifted the register. That's why `MISO` changed and then *stayed* changed after the pull-up was
  removed (a floating pin wouldn't hold its level). The later `RCK`-high test "resisted" the
  pull-up because the register was in load mode, where clock edges are ignored.
- *"A hidden active component sits between the shift register and the connector."* Built on the
  artifact above. No such component was needed to explain anything.
- *The 2026-09-11 "U1 is dead" diagnosis of the old `520-7001-00A` board.* Same inverted polarity,
  same symptom. Most likely a misdiagnosis; untested with the fix.
- *"U3 conditions `RCK`."* `RCK` goes through U1 (the 74HC540), confirmed by measurement. U3's role
  is still untraced (on the older board's schematic, the equivalent Schmitt-trigger pair conditions
  `MISO` only), and doesn't matter for reading the board.
- The earlier "Where this leaves things" list — superseded by the next steps below.

**Still true and worth keeping:** the Arduino `MISO`/`MOSI` pin-swap bug; the Bus Pirate v3.6's
`AUX`/`CS` only reaching ~3.2V. That matters here because `RCK` enters a 74HC540 (plain HC, not
HCT), which at 5V needs about 3.5V to see a valid high — so drive `RCK` from a 5V-logic source (the
Uno, a bare ATmega328P at 5V, or a Bus Pirate 5), not a v3.6 Bus Pirate.

**Lesson worth carrying forward:** trace where every control line actually goes (schematic, or a
meter in Ω mode — series resistors don't beep in continuity mode) before experimenting with
timing and protocol. And "all 8 bits always identical" from a 74HC165 means the register is being
clocked while held in load mode.

**Next steps:**
1. ~~Pick an approach~~ — **decided 2026-09-26: the ATmega bridge** ("Permanent build" below).
   Reading the board directly from OPP with MPF's `spi_bit_bang` (the section after that) is kept
   on file as the untested alternative.
2. Set `BIT_INVERT` with the Uno on the cabinet, then build the bridge and wire it into OPP.
3. Run `TODO.md`'s empty-trough + ball-by-ball test on the real cabinet.
4. Optional: retest the old `520-7001-00A` board with the corrected firmware. It may not be dead.

## Permanent build: bare ATmega328P bridge (2026-09-26)

The build sheet (`design/physical-checklists/trough-opto-bridge.html`) still holds after the
polarity fix; this is the condensed version, updated for the 520-8516-00.

**Parts** (checked against the `Component_database` inventory on 2026-09-26):

| Part | In stock |
|---|---|
| ATmega328P-PU, DIP-28 | 5 |
| 10kΩ resistor (reset pull-up) | 20 |
| 0.1µF ceramic capacitor (decoupling, from the ceramic assortment) | yes |
| Uno + ArduinoISP shield (programmer only) | yes |
| Perfboard, DIP-28 socket, mating plug for the Stern board's `CN1` header | not in the database (may just be unrecorded) |

The socket is worth it: pull the chip to reprogram it on the ISP shield instead of in-circuit.

**Wiring** (DIP pin numbers):

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
| 5, 6, 11, 12, 13, 23 | `s-trough1`…`s-trough6` → OPP chain2-0x21 inputs 2-1-16…21 |
| 24 (PC1) | `s-trough-jam` → OPP 2-1-22 |

Stern `CN1` `VCC`/`GND` go to the same +5V/GND; its `MOSI` stays unconnected. The ATmega's ground
**must** be shared with the OPP board. Power from the machine's 5V logic supply — during the bench
test a Uno on USB powered the whole opto board without trouble, so the draw is modest (not measured).
The OPP inputs are the same positions the old soldered taps used, so no MPF config changes beyond
the output polarity.

**Programming:** flash `tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino` with
`tools/flash-atmega328p.ps1` (ArduinoISP on the Uno, MiniCore, 8MHz internal clock). No firmware
changes needed — the SPI and serial speeds work at 8MHz.

**Order:** set `BIT_INVERT` first with the *Uno* connected on the cabinet, watching MPF's live
switch states (reflashing over USB takes seconds), then program the bare chip once with the final
values.

**Simpler alternatives:** leave the Uno in permanently (works as-is, no soldering, just bigger), or
use the inventory's Pro Micro (ATmega32U4, 16MHz = 5V version; small, with USB — but its SPI pins
differ, so the firmware's pin map would need changing).

## Alternative: read the board directly from OPP with MPF's `spi_bit_bang` (untested)

*Considered and not chosen (2026-09-26): the owner went with the ATmega bridge. Kept here in case
the bridge ever needs replacing.*

MPF 0.80 ships a `spi_bit_bang` platform (`mpf/platforms/spi_bit_bang.py`) made for exactly this
kind of board: it reads a 74HC165-style register by bit-banging it through *another* platform's
hardware — two MPF `digital_outputs` for the latch and clock, and one ordinary switch input for the
data line. The OPP firmware itself has no shift-register input mode (MPF's OPP platform supports
only solenoid, input, incandescent, matrix, and neopixel wing types), so this is the only
no-extra-microcontroller way.

**How it would map onto this board.** OPP outputs are low-side FETs, so each needs a pull-up
resistor to 5V (roughly 1–2.2kΩ; check it reaches ≥3.5V at the Stern pin, since `RCK` enters a
plain 74HC540). With pull-ups, "output enabled" = line LOW and "disabled" = HIGH. That happens to
match the board: the platform holds its chip-select *disabled* (HIGH = load) between reads and
*enabled* (LOW = shift) while clocking, which is exactly the inverted `RCK` this board wants. The
clock idles HIGH and each 1ms pulse ends on a rising edge, which is when the 74HC165 shifts. The
first bit read is input H (the unused bit 7), MSB first, so switch numbers `"0"`–`"6"` equal raw
bits 0–6. Because an OPP input reads active when pulled low, the bits arrive inverted: a switch
is active when its sensor is **blocked**.

**Config sketch** (untested; output/input numbers are placeholders):

```yaml
digital_outputs:
  trough_rck: {number: "<free OPP output>", type: driver}   # -> CN1 RCK, with pull-up to 5V
  trough_sck: {number: "<free OPP output>", type: driver}   # -> CN1 SCK, with pull-up to 5V
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
  bit_time: 50ms   # default; must exceed OPP's switch-report latency (poll_hz defaults to 100)
```

**Trade-offs versus the ATmega bridge:**
- **For:** no microcontroller, no firmware, no flashing, no `BIT_INVERT` — polarity is just each
  switch's `type` in MPF config. Uses 1 OPP input instead of 7 (frees 6).
- **Against:** slow — every bit is a round trip through MPF and OPP's serial link, so a full read
  takes about 0.5s at the default `bit_time` (tunable down, but it must stay above OPP's polling
  latency). Fine for trough ball counting, noticeably laggier than the bridge's ~10ms.
- Needs 2 free OPP driver outputs plus the pull-ups; the outputs must not have flyback diodes to a
  coil rail that can be switched off (that would clamp the logic lines low when coil power is off).
- Reads only while MPF is running, and the switches can't be used in OPP hardware rules (not needed
  for a software-driven ball device).
- The `s-trough-jam` "active = clear path" quirk came from the old tap wiring; here jam would read
  active = blocked unless its `type` is flipped, so the ball device config needs a look either way.
- At startup the platform reports every switch inactive until its first read completes; watch for
  spurious ball-count events on boot.

**Suggested order:** since it's only config plus two resistors, try `spi_bit_bang` first if two
free OPP outputs exist. Fall back to the ATmega bridge if it proves too slow or flaky.

## Verification

*Written for the original plan, before the 520-8516-00 findings above — "the board's identity"
below means the original `520-7001-00A` unit. For the new board, the "Resolution (2026-09-26)"
section's next steps are the current checklist; this section is kept as the record of what the
original plan intended to verify once a working bridge existed.*

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
