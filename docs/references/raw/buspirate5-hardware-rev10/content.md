# Hardware Design (5 REV 10) — Bus Pirate 5 documentation

Archived 2026-09-26 from <https://docs.buspirate.com/docs/hardware/bp5rev10/hardware/>. Summary of
the relevant sections with the key sentences quoted, not a byte-perfect copy.

Cited from `docs/stern-spike-trough-opto.md` ("Bench tools") for why a Bus Pirate 5 can drive a
genuine 5V logic high on its I/O pins where a Bus Pirate v3.6 can't.

## IO pin buffers

"IO pins are fitted with 74LVC1T45 bidirectional buffers." "Half of the buffer is powered at
3.3volts to interface the RP2040. The other half is powered from the VREF/VOUT pin at 1.2-5volts
to interface with the outside world."

The part is made by several manufacturers with different ranges (TI and Diodes Inc 1.65–5.5V;
Nexperia and WuXi I-Core 1.2–5.5V). REV10 uses the WuXi I-Core part (1.2–5.5V).

## Programmable power supply (PPSU)

"1-5volts adjustable output, 300mA max", with "0-500mA current sense" and "0-500mA current limit
with digital fuse."

## Series resistors on the IO pins

"we limit the maximum current draw with 330R series resistors on each 74LVC1T45 IO pin."
