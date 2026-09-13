# Layering Modes Example

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/game_design/mode_layering.md>.
Rendered-page summary, not a byte-perfect copy (the source declined a verbatim reproduction).
This is MPF's own documented precedent for the Field/Mission/Wizard mode-layering pattern this
project's `design/README.md` workflow already uses.

## Gameplay mode categories

- **Field Modes** — nonintrusive, run when no wizard/mission mode is active; used for accruals,
  multipliers, shots that qualify other modes. All field modes run together.
- **Mission Modes** — "partial takeover," ask for the player's attention but let other gameplay
  mechanics keep running.
- **Wizard Modes** — "complete takeover," stop nearly all other gameplay, force focus on that
  mode alone.

## Helper modes

Three helper modes run underneath the current gameplay to manage transitions:

- **Field Mode** (`field.yaml`) — consolidates all field modes.
- **Global Mode** (`global.yaml`) — manages transitioning between field mode and mission modes.
- **Base Mode** (`base.yaml`) — MPF's default background mode; manages transitioning between
  global mode and wizard modes.

## Starting and stopping layers

The full doc includes YAML examples for field/mission/global/wizard/base mode configs, showing
how each layer manages its own event handlers and transitions between gameplay states — see the
live URL for the actual config snippets, not captured in this summary.
