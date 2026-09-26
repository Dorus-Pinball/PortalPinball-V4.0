# Stern SPIKE System Manual (775-7640-00, Release 2)

Archived 2026-09-26 from
<https://www.sternpinball.com/wp-content/uploads/2020/11/SPIKE-System-Manual.pdf>. This is a
large, mostly image-based PDF (diagrams/scans) — full text extraction was not possible; this is a
summary of the relevant, readable content only, not a byte-perfect copy. The full PDF is also
saved locally at `docs/SPIKE-System-Manual.pdf` in this repo.

Cited from `plans/read-opto.md`'s 2026-09-26 bench findings section, while investigating why a
`520-8516-00` trough opto board's serial output couldn't be read from non-Stern electronics
despite clean, correctly-timed signals reaching it.

## Relevant finding: "Node extension" classification

Section 2.1/2.7 of the manual classifies boards like the trough opto receiver (part family
`520-7001-00`/`520-8516-00`) as a **"Node extension"**, explicitly distinct from a full "Node":

> "Node extensions - These LED boards add additional low-power input and outputs to a specific
> Power or I/O node and are connected with simple serial bus."

Page 11's example hardware map shows the trough opto receiver ("8a") hanging off **Playfield Node
8** (part `520-7017-72`) via a "Serial Data Cable" (`036-8054-XX`) — not the RJ45 node-bus cable
used for CPU↔node communication.

Playfield/full node boards are described (page 5) as having their own onboard processors running
embedded code "programmed automatically by the CPU" — i.e., a genuine Spike CPU does not bit-bang
a node extension's shift register directly; a full smart node board's own microcontroller does,
using whatever bit-level timing/sequencing Stern's own closed firmware for that node implements.
That firmware's exact behavior (clock idle level, setup/hold margins, inter-frame timing, etc.) is
not documented anywhere in this manual, and was not found documented anywhere else either after a
genuine search attempt (including previously-inaccessible Pinside.com threads, reached this time
via a proxy).

## Why this matters for reading a trough board standalone

It means the "protocol" a genuine machine uses to read this specific connector isn't the Spike
CPU's own (documented-nowhere-either) node-bus protocol — it's one layer further down, inside a
full node board's own closed firmware, talking to its own extension board over a simple 4-6 wire
serial link. This explains why no public documentation of the bit-level extension-board read
protocol exists: it was never part of the (already minimally documented) CPU↔node link that
hobbyists have partially reverse-engineered (e.g. MPF's `spike:` platform) — it's a separate,
even-less-visible link one level further into Stern's proprietary firmware.

## Not directly useful

Node bus addressing/command protocol (CPU↔node RS-485 layer), power supply voltage
specifications, and any standalone/bench-testing procedure for a node extension board were not
found in the readable portions of this manual.
