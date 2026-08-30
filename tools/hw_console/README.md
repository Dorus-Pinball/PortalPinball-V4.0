# Hardware Bring-Up Console

A small local web tool for tracking real-hardware wiring progress as boards and components get
connected to the cabinet. It's a **separate tracking layer**, not a replacement for MPF's own
config — `machinefolder/config/hardware-switches.yaml` and `hardware-coils.yaml` stay the
authoritative source of what MPF actually loads. This tool just tracks wiring status, board/chain
location, a wiring checklist, and catches number collisions before you wire something into an
already-used slot.

## Running it

```
cd tools/hw_console
..\..\.venv\Scripts\python.exe app.py
```

Then open http://localhost:5000. (Flask is installed in the project's `.venv`; if it's missing,
`pip install flask`.)

## Workflow

1. **Boards tab** — as you reconnect each physical board, flip its status from `scanned` (last
   known state) to `connected` to `verified`.
2. **Components tab** — filter by status, click a component to see its switches/coils, which
   board they land on, and a wiring checklist (flyback diode / common ground / same-board rule,
   per `TODO.md`'s OPP wiring checklist). Flip switch/coil/component status as you wire and test
   each one.
3. **Add a new component** via the "+ Add component" button. It runs a collision check against
   both `hardware-switches.yaml`/`hardware-coils.yaml` and the rest of the registry before saving
   — you'll get an error naming the conflict instead of a silent overwrite.
4. **Talking to Claude**: just say the component name in chat (e.g. "I'm wiring the flippers
   now"). Claude reads `tools/hw_console/data/components.yaml` directly — no need to copy/paste
   anything from the UI.

## Data

Everything lives in `data/components.yaml`, hand-editable if you'd rather skip the UI for a quick
change. See the comment at the top of that file for how it was seeded and what `planned` /
`wired` / `tested` mean.

`board Overviews.xlsx` is not parsed automatically — numbers are transcribed by hand when a
component gets planned, same as the process before this tool existed. This is deliberate: the
xlsx's own notes are sparse/inconsistent in places, so a manual double-check each time is safer
than an automated import.
