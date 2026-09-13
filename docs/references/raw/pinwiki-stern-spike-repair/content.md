# Stern SPIKE™ System Repair — PinWiki

Archived 2026-09-13 from
<https://pinwiki.com/wiki/index.php/Stern_SPIKE%E2%84%A2_System_Repair>. Rendered-page summary,
not a byte-perfect copy. Cited from `docs/stern-spike-trough-opto.md` — confirms Stern hasn't
supplied schematics/part lists for these boards, and covers the genuine node-bus (RS-485 over
Cat5e) that `docs/stern-spike-trough-opto.md`'s own writeup explicitly is *not* about (this
project's trough opto board is a plain 74HC165 shift register, not this SPIKE node-bus).

## Overview / architecture

SPIKE is Stern's current board architecture (first full production: Wrestlemania, 2015) — a CPU
board paired with multiple "node boards" on a 48VDC bus, each node regulating voltage for its own
devices (lamps/coils/switches). Nodes connect via CAT 5e cabling — **not standard Ethernet**;
connecting SPIKE nodes to computer Ethernet damages boards.

SPIKE 1: 2012-2018. SPIKE 2: 2016-2024. SPIKE 3: 2025-2026.

## Key hardware

- **Power supply**: 48V @ 10.5A + fan, Mean Well RSP-500-48.
- **Playfield node board (520-7017-72D)**: 8 coils, 32 switches, 8 GI/LED outputs, serial
  daisy-chain out, LPC1313F microcontroller.
- **Cabinet node board (520-6967-72B)**: status LEDs (red=48V present, yellow=CPU comms, green=6V
  rail); coin door/meters/tilt/shaker/ticket-dispenser/bill-acceptor connectors.
- **LED driver boards**: daisy-chained, SPI-commanded from node boards. Common failure: bad
  serial IN/OUT connector → blackout/flicker/wrong colors across the chain.
- **Node 10 board (520-5781-02)**: stepper motor control (Godzilla, Rush). Common failure: U1
  (TMC5041-LA).

## Common failures & repairs

- **MP24943 buck converter** — most frequent node-board failure; only red 48V LED lights up.
  Needs hot-air reflow (soldered ground pad). MBR760 diode often fails alongside it.
- **Long-range opto switches** — TX (515-0215-00/515-6940-00) / RX (515-0215-01/515-6940-01) fail
  due to receiver design; locks switches "open" despite blocked IR. Repair: replace TX IR LED
  with Lite-on HSDL-4220 (875nm, 30°), RX phototransistor with Osram SFH313FA (870nm NPN),
  replace the 2N7002 switching transistor. Matched pairs required; power-cycling masks the issue
  temporarily.
- **LED DMD vertical line** — a failed 8x8 LED segment; one dark pixel within the line identifies
  it. Warranty replacement recommended for newer games.

## Shaker motor

Connector CN16 (CN2 on early versions). Pinout: 1=motor neg (blue), 5=motor pos (red). **Warning**:
third-party shaker motors (notably Pinball Life) contain capacitors that destroy node boards
(Service Bulletin 184) — symptom: start button/plumb-bob/coin-door GI lamps stop working. Some
owners removed the offending capacitor successfully, but Stern's official position mandates OEM
replacement motors.

## Boot/reset issues

MPU boot failure — check the SD card is seated. Game resets — check shaker motor, software bugs
in early revisions, failing SD cards.

## Linux OS (backbox CPU)

NXP i.MX6 Wandboard-derived hardware, Linux, SD card with ext4 (root fs + `/games`). Unpopulated
serial console connector CN2 for debug access. Game executable has a text debug menu (`coil`,
`credit`, `sound`, `node`, `display`, `score`, `mode` commands).

## Additional resources

- Stern technical video (SPIKE 1): <https://www.youtube.com/watch?v=MvefdrNaAPg>
- Stern technical video (SPIKE 2): <https://www.youtube.com/watch?v=d1xdmgeAylQ&t=190s>
- Mission Pinball SPIKE connection docs:
  <https://docs.missionpinball.org/en/latest/hardware/spike/connection.html>
