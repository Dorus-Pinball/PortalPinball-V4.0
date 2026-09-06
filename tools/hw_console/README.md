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

Then open http://localhost:5000. (Flask and ruamel.yaml are installed in the project's `.venv`;
if either is missing, `pip install flask ruamel.yaml`.)

## Workflow

1. **Boards tab** — as you reconnect each physical board, flip its status from `scanned` (last
   known state) to `connected` to `verified`.
2. **Status tab** — one entry per playfield element (flipper, VUK, drop bank, etc.), each tracked
   through a 6-stage build lifecycle:
   1. Idea — no hardware yet
   2. Hardware — no idea yet (not renovated: old stickers, rough cables, etc.)
   3. Hardware with a purpose — not renovated
   4. Renovated hardware with a purpose — not wired to the playfield & controllers
   5. Fully connected (on playfield) — not tested
   6. Ready — fully connected & tested

   Click an element to edit its display name and status inline — both PATCH straight to
   `components.yaml`. Its switches/coils table is **read-only** here: pin numbers only change via
   chat (the `wire-component` skill), never through this UI.
3. **Add a new element** via the "+ Add element" button — just an internal ID, display name, and
   starting status. New elements start with no pins; they get real switch/coil numbers later, via
   chat, once they're actually being wired.
4. **Talking to Claude**: just say the element name in chat (e.g. "I'm wiring the flippers
   now"). Claude reads `tools/hw_console/data/components.yaml` directly — no need to copy/paste
   anything from the UI.

## Data

Everything lives in `data/components.yaml`, hand-editable if you'd rather skip the UI for a quick
change. See the comment at the top of that file for how it was seeded and what the 1-6 status
scale means (also defined in code as `registry.COMPONENT_STATUSES`).

`board Overviews.xlsx` is not parsed automatically — numbers are transcribed by hand when a
component gets planned, same as the process before this tool existed. This is deliberate: the
xlsx's own notes are sparse/inconsistent in places, so a manual double-check each time is safer
than an automated import.
