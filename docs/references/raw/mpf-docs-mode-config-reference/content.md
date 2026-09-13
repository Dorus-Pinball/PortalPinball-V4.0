# MPF Mode Config Reference

Archived 2026-09-13 from <https://missionpinball.org/latest/config/mode/>. Rendered-page
summary, not a byte-perfect copy.

## Overview

Documents the configuration options for `mode:` sections in MPF. Modes organize game logic into
discrete, startable/stoppable units.

## Optional settings

- **asset_paths** — custom directories for mode-specific assets (images/sounds/video).
- **code** — custom Python code files for the mode, for logic beyond plain config.
- **console_log** / **file_log** — mode-specific logging verbosity/output.
- **events_when_started** / **events_when_stopped** — events fired on mode start/stop.
- **game_mode** — boolean, whether this mode is a game mode (runs during active gameplay).
- **path** — filesystem path for the mode's config/assets.
- **priority** — mode-stack priority (higher runs before lower).
- **restart_on_next_ball** — whether the mode auto-restarts on the next ball.
- **start_events** / **stop_events** — events that trigger start/stop.
- **start_priority** / **stop_priority** — startup/shutdown sequencing priority.
- **stop_on_ball_end** — boolean, whether the mode auto-stops at ball end.
- **use_wait_queue** — whether the mode participates in MPF's wait-queue synchronization system.
