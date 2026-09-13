title: Tilt

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/tilt/index.md>. Full raw
markdown, as returned by the source fetch. Directly relevant to this project's open "Tilt: no
switch exists yet" gap (`TODO.md`) — once a switch exists, the MPF-side work below is nearly all
that's needed.

# Tilt

Tilt is a built-in mode — add `tilt` to your machine config's mode list. Tag your tilt bob switch
`tilt_warning` and your slam-tilt switch `slam_tilt`. Tilt runs at all times (the machine has to
watch for slam tilts even between games).

Three logic paths, each configurable via a switch tag or event list:

- **Slam tilt** (`slam_tilt`) — usually the coin-door slam switch. Clears all credits, ends the
  current game.
- **Instant tilt** (`tilt`) — rarely used on normal machines; useful for custom tilt logic or
  special modes.
- **Tilt warnings** (`tilt_warning`) — usually the tilt bob switch. Gives `warnings_to_tilt`
  warnings before ending the current ball. Warnings reset via `reset_warnings_events` (default:
  ball end, changeable to game end). Count stored in `tilt_warnings_player_var` (default
  `tilt_warnings`).

## Minimal config

```yaml
modes:
  - tilt
```

## Change defaults

```yaml
# machine config
modes:
  - tilt
# modes/tilt/config/tilt.yaml
tilt:
  multiple_hit_window: 300ms
  settle_time: 5s
  warnings_to_tilt: 3
```

## Add operator settings to service mode

```yaml
modes:
  - tilt
settings:
  warnings_to_tilt:
    label: Number of tilt warnings
    values: {0: "no warnings", 1: "1", 2: "2", 3: "3", 5: "5", 10: "10"}
    default: 3
    key_type: int
    sort: 600
  settle_time:
    label: Time to wait on tilt to settle bob
    values: {3000: "3s", 5000: "5s", 10000: "10s"}
    default: 5000
    key_type: int
    sort: 610
  multiple_hit_window:
    label: Tilt sensitivity
    values: {150: "sensitive", 300: "normal", 500: "insensitive", 1000: "very insensitive"}
    default: 300
    key_type: int
    sort: 620
# modes/tilt/config/tilt.yaml
tilt:
  multiple_hit_window: settings.multiple_hit_window
  settle_time: settings.settle_time
  warnings_to_tilt: settings.warnings_to_tilt
```

## Monitorable properties

Prefix `mode.tilt.<name>`: `_tilt_settle_ms_remaining` (ms until bob considered settled),
`_tilt_warnings_remaining` (warnings left until tilt).

## Related How To guides

Overwriting the default tilt slides (mpf-docs `game_logic/tilt/overwrite_tilt_slides.md`).
