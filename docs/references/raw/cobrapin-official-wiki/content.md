Archived 2026-09-14 from <https://pinballmakers.com/wiki/CobraPin>. Converted to Markdown via a
fetch/summarization pass (pinballmakers.com is a MediaWiki site, not raw Markdown source like the
GitHub-hosted `mpf-docs-*` archives in this same directory) - close to the source content, not a
byte-exact scrape.

# CobraPin - Pinball Makers

## Overview

CobraPin is a pinball controller designed as "a basic all-in-one assembled affordable solution"
intended to work with the Mission Pinball Framework (MPF) and based on the Open Pinball Project
(OPP). It was released publicly in 2021 via Kickstarter.

## Key Features

The board offers substantial control capabilities:

- **24 coil drivers** organized into 3 banks of 8 outputs each
- **38 direct switch inputs** OR **22 direct inputs** with an **8x8 switch matrix**
- Support for **512 RGB/RGBW Neopixel LEDs** across two chains
- **12-50V power filtering** with ground provision
- **Fused outputs** for solenoid banks and Neopixels
- **Relay control output** for dual relay boards
- Socketed processor boards and replaceable transistors for serviceability

## Power Requirements

The board requires specific power supply characteristics. Users should avoid supplies with
overload protection that "shuts down its output," instead selecting supplies with
"constant-current limiting" or automatic recovery features.

An NTC thermistor limits initial power draw when charging large capacitors at startup. A jumper
(JP9) allows bypassing this thermistor if initial play performance seems weak.

## Switch Configuration

CobraPin supports both active-low and active-high switch matrices. The default configuration
uses an active-low matrix where columns are pulled down during selection. Active-high matrices
reverse this logic, requiring column pull-up instead.

For active-high matrices in MPF, switches may appear inverted, requiring developers to add
`type: NC` designations to switch definitions to correct the logic inversion.

A separate fetch of this same page (prompted specifically about silkscreen labeling) returned
these direct quotes: "The switch inputs are labeled in silkscreen with the MPF compatible
numbers." and, for coil outputs, "The coil outputs are labeled in silkscreen with the MPF
compatible numbers." Not reproduced verbatim on this broader pass - likely drawn from a linked
sub-page (the pinout PDF/sections referenced above) rather than this page's own visible prose.

## Input Voltage Limitation

A critical warning states: "the switch inputs should be limited to 3.3V since the STM32 is a
3.3V device." Active switches like drop target opto boards must be verified to prevent exceeding
this threshold.

## Expansion Boards

Two expansion options extend functionality:

**Xpansion Board** provides an 8x8 lamp matrix, 8 coil outputs, and 8 direct switch inputs for
controlling existing machines with flashers and matrix lamps.

**Satellite Board** offers 23 direct switch inputs, 8 coil outputs, a Neopixel output for 256
LEDs, and I/O protection with selectable 5V or 12V LED power.

## Firmware Configuration

Two processor boards (Board 0 and Board 1) require different configurations. A critical warning
emphasizes: "Putting a Board 1 config in a Board 0 slot could result in blown FETs, coils, or
fuses."

Board 1 supports three variants: Standard (active-low matrix), Direct (38 direct inputs), and
HighMatrix (active-high matrix).

## Troubleshooting

Testing without coil power is recommended to verify output behavior using the onboard yellow
indicator LEDs before applying high voltage.

The STM32 processor includes a heartbeat LED (PB21 on USB-C Type-C versions) that toggles every
second when operating normally and shows increased activity when receiving USB packets from the
host.

Component replacement follows specific procedures: processor boards pull straight out and in;
blown transistors use TO-251 through-hole replacements; fuses are 5x20mm slow-blow rated to
maximum 10A.

## Availability

CobraPin is available through the Cobra Amusements shop on Pinside.

---

**Source files:** Available on [CobraPin Github](https://github.com/cobra18t/CobraPin)

**Last updated (on the live wiki):** September 20, 2024
