# Portal Pinball V4.0 — Wiki

A real, physically-built Portal-themed pinball machine running **Mission Pinball Framework** on
**OPP `gen2`** hardware, currently being rewired from scratch. This wiki *is* the project's own
`docs/` — you're reading a git-synced mirror of the same files in the GitHub repo, not a separate
copy. Edit a page here and it round-trips back via the `wiki-sync` branch; edit the repo instead
and it shows up here on the next sync. Either way, there's one set of files, not two.

## How the information here is organized

A few different *kinds* of page live in this wiki, and knowing which kind you're looking at
tells you how much to trust it and where to go if it's wrong:

- **Generated, always current.** Pages like [Wiring pin map](/docs/wiring-pin-map) are rendered
  straight from the live data (`components.yaml`, `hardware-*.yaml`) every time something
  changes — never hand-edited, so what you see here always matches reality. If it's wrong, the
  *data* is wrong, not the page.
- **The rulebook.** [OPP hardware reference](/docs/opp-hardware-reference) is where the
  hardware's actual rules live (board priority, pairing rules, HV bank wiring) — written once,
  by hand, and everything else defers to it.
- **How the work actually happens.** [Wiring workflow](/docs/wiring-workflow) walks through what
  wiring a component looks like at the bench, step by step, in plain language.
- **The reference archive.** [External references](/docs/references/index) is a local, permanent copy
  of every outside doc/wiki page this project cites — so a citation never goes dead just because
  a live page moved.
- **The decision log.** [CHANGES](/CHANGES) records *why* things look the way they do — including
  approaches that were tried and abandoned, and why — numbered, dated, never silently rewritten.
- **The open list.** [TODO](/TODO) is what's rough, unfinished, or blocked right now.

That's the whole concept: generated pages you never hand-edit, hand-written pages that explain
the *why* and *how*, an archive so outside sources don't rot, and a log so decisions don't get
silently re-litigated. Everything below is organized the same way.

## Start here

- **[README](/README)** — stack overview, how to run MPF/tests/the display.
- **[Wiring guide](/docs/wiring-guide)** — board map, every component's current switch/coil
  numbers, and harness diagrams, in one browsable page. *(generated)* For the printable
  bench-test checklist itself (pass/fail history, pulse-ms tuning notes), open
  `design/physical-checklists/wiring-guide.html` directly — kept out of the wiki on purpose so
  that fast-changing log has exactly one home.
- **[Wiring pin map](/docs/wiring-pin-map)** — every component's current switch/coil numbers and
  bring-up status, in one plain table. *(generated)*
- **[Wiring workflow](/docs/wiring-workflow)** — how a component actually gets wired, tested, and
  recorded, step by step.
- **[OPP hardware reference](/docs/opp-hardware-reference)** — the CobraPin/red-board wiring
  rulebook (board priority, pairing rules, HV bank wiring).
- **[TODO](/TODO)** — known gaps, open decisions, what's blocked on physical hardware.
- **[CHANGES](/CHANGES)** — numbered log of key decisions, with status and the reasoning behind
  each one.

## Design & gameplay

- **[Design README](/design/README)** — the story → shots → modes workflow this project's
  feature design follows.
- **[STORY](/design/STORY)**, **[SCREENS](/design/SCREENS)**, **[GAME_MOMENTS](/design/GAME_MOMENTS)**
  — the Portal-themed narrative and presentation design docs.

## Hardware reference

- **[Board silkscreen reference](/docs/board-silkscreen-reference)** — identifying a physical pin
  from a board photo, cross-referenced against its MPF number.
- **[Stern SPIKE trough opto board](/docs/stern-spike-trough-opto)** — reading the salvaged
  trough sensor board without genuine Spike hardware.
- **[Trough opto bridge](/design/physical-checklists/trough-opto-bridge)** — the ATmega328P
  bridge project's physical checklist.
- **[External references](/docs/references/index)** — archived local copies of every outside source
  this project cites, so a citation survives a page moving or vanishing.

## Elsewhere

- **[Online services](/docs/online-services)** — where to browse this project's live data
  (parts inventory, this wiki, the NAS dashboard) from any device.
