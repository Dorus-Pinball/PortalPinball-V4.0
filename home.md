---
title: PinballWiki
description: 
published: true
date: 2026-09-13T20:07:33.122Z
tags: 
editor: markdown
dateCreated: 2026-09-13T17:42:14.553Z
---

# Portal Pinball V4.0 — Wiki

A real, physically-built Portal-themed pinball machine running **Mission Pinball Framework**
on **OPP `gen2`** hardware. This wiki is a git-synced mirror of the project repo's own docs —
edits here round-trip back to GitHub via the `wiki-sync` branch, everything else stays
generated from `components.yaml`/`hardware-*.yaml` as the real source of truth. See
[README](/README) for the full "what is this, how do I run it" story.

## Start here

- **[README](/README)** — stack overview, how to run MPF/tests/the display.
- **[Wiring pin map](/docs/wiring-pin-map)** — every component's current switch/coil numbers and
  bring-up status, in one table.
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

- **[Stern SPIKE trough opto board](/docs/stern-spike-trough-opto)** — reading the salvaged
  trough sensor board without genuine Spike hardware.
- **[Trough opto bridge](/design/physical-checklists/trough-opto-bridge)** — the ATmega328P
  bridge project's physical checklist.

## Elsewhere

- **[Online services](/docs/online-services)** — where to browse this project's live data
  (parts inventory, this wiki, the NAS dashboard) from any device.
