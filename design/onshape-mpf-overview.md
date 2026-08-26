# Feature overview: Onshape CAD ↔ MPF config

One row per feature, generated from `design/features/*.yaml` (the source of truth) cross-checked
against `machinefolder/config/hardware-switches.yaml`/`hardware-coils.yaml`/`hardware-leds.yaml`.
"Onshape part/assembly name(s)" cells are only as complete as the CAD research has gone so far —
see `design/research/onshape-cad-findings.md` for the full writeup behind each entry, including
honest gaps where no CAD match has been found yet. "Mode status" mirrors each feature file's own
`status:` field.

| Feature | Onshape part/assembly name(s) | MPF switch(es) | MPF coil(s) | MPF LED(s) | Mode status |
|---|---|---|---|---|---|
| [lanes](features/lanes.yaml) | `toprail` (top-lane zone only, not per-lane); bottom lanes — no CAD match found | `s-toplane1/2/3`, `s-bottomlane1..5` | — | `led-toplane1..3`, `led-lane-b1..4` | designed |
| [orbits](features/orbits.yaml) | `left orbit`, `right orbit` | `s-orbit-l`, `s-orbit-r`, `s-orbit-top` | — | `led-orbit-l`, `led-orbit-r`, `led-orbit-t` | designed |
| [slings](features/slings.yaml) | `Slingshot Rubber Left`, `Slingshot Rubber Right` | `s-left-sling`, `s-right-sling` | `c-sling-left`, `c-sling-right` (via `ac-sling-left`/`ac-sling-right` autofire) | `led-sling-l`, `led-sling-r` | designed |
| [skillshot](features/skillshot.yaml) | `shooter ramp` (shares `toprail`/lane geometry with `lanes` for candidate targets) | `s-launch`, `s-plunger-lane`, `s-toplane1/2/3` (candidate targets) | — | `led-launch`, `led-save` | designed |
| [dropbank](features/dropbank.yaml) | no drop-bank/insinerator CAD match found; `Button` assembly matches `s-button` | `s-drop1/2/3`, `s-insinerator`, `s-button`, `s-target-l1` | `c-drop` | `led-insinerator`, `led-button`, `led-target-l1` | designed |
| [aerial](features/aerial.yaml) | `Faithplate walls` | `s-aerial` | — | `led-aerial` | designed |
| [portal](features/portal.yaml) | ball-lock hole-pairing mechanism unresolved; `balldropper`/`VUK`/`Exit`/`DropperAssy` not yet opened | `s-dropper`, `s-portal-r`, `s-portal-m`, `s-exit-success` | — | `led-dropper`, `led-portal-r`, `led-portal-m`, `led-exit-success`, `led-exit-open-1..5` | designed |
| [ramps](features/ramps.yaml) | `light bridge rail right`/`left`, `Diverter_Rod`, `Diverter_Base`, `Bridge_Diverter_Cover`, `Subway` | `s-ramp-l1/l2`, `s-ramp-r1/r2` | — (diverter coil not yet wired) | `led-ramp-l`, `led-ramp-r` | designed |

None of the 8 features have a real `machinefolder/modes/<name>/` folder yet (only the non-feature
`base`/`attract` modes exist) — "designed" here means the story/shots/rules/presentation layers
are filled in per `design/README.md`'s workflow, not that the mode is built.
