# Wiring a component: how it actually happens

This is the human-readable version of the wiring process — what it feels like at the bench,
component by component, during the from-scratch rewire. For the technical rulebook (board
priority, pairing rules, HV bank wiring), see
[OPP hardware reference](/docs/opp-hardware-reference). For the exact bookkeeping steps Claude
follows to keep the config/registry/generated docs in sync, see
`.claude/skills/wire-component/SKILL.md` in the repo.

The short version: **wire it, then figure out together exactly what got wired.** Since this is a
full rewire — new pieces going to whatever board location is physically convenient, not
constrained by the old wiring — pre-planning every number down to the pin before touching a wire
doesn't fit how the work actually goes. Instead, the numbers get discovered right after the
physical connection is made, while it's still on the bench.

## The four steps

### 1. Name the thing

Dorus decides what a newly-wired object is called — "left slingshot," "VUK eject," "tilt
switch." Just a name at this point, no numbers. This is what shows up everywhere downstream:
`components.yaml`, the generated wiring guide, MPF's own device names.

### 2. Name the coil link

If the component has a coil (a slingshot, a pop bumper, an eject, anything that fires or moves),
Dorus identifies which coil driver channel it's physically connected to — which board, which
bank, which numbered terminal. Read straight off the board's silkscreen or connector labels (see
[Board silkscreen reference](/docs/board-silkscreen-reference) if a label needs decoding from a
photo).

### 3. Together, identify the switches

This is the step that changed the most. Rather than assuming a switch's MPF name up front,
`tools/wiring_test.py --monitor` gets run against the live machine: it prints every switch's
current state, then streams every open/close as it happens in real time. Tap the switch (or
switches) that belong to this component, on the actual cabinet, and its real name and address
print immediately — no need to already know it. This is how "which switches did I just wire"
gets answered together, on the spot, instead of guessed at from a plan.

### 4. Test it — low voltage, then high voltage

Two passes, in order, both using `tools/wiring_test.py`:

- **Low voltage first.** With the 50V/high-voltage supply off, the script confirms switch
  continuity (press/release) and pulses any coil just enough to light its driver activation LED —
  safe to do with HV off, and enough to catch a wiring mistake before it can blow a FET, coil, or
  fuse.
- **High voltage second**, once the no-HV pass is clean. The same script's `--pulse-ms` option
  drives a real pulse with HV present, so the mechanism's actual motion (a slingshot kicking, a
  coil firing) gets confirmed for real, not just the driver logic.

See `tools/wiring_test.py --help` for the exact commands — confirmation prompts are a single
Enter press, not typed text, so this whole loop stays fast to repeat component after component.

## What happens after

Once a component's name, coil channel, and switch(es) are known and tested, they get recorded
into `tools/hw_console/data/components.yaml` and `machinefolder/config/hardware-*.yaml` — the
board-priority and pairing rules from the
[OPP hardware reference](/docs/opp-hardware-reference) still apply here, they just get *checked
against* the physical connection that was actually made, rather than *dictating* it beforehand.
`python tools/hw_console/check_registry.py` catches a collision or pairing-rule violation at this
point, and the wiring guide / pin map regenerate automatically from the same data. That
bookkeeping is what `.claude/skills/wire-component/SKILL.md` walks through step by step.
