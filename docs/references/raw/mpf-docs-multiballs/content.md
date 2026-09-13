---
title: Multiballs
---

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/multiballs/index.md>. Full
raw markdown, as returned by the source fetch. The "Common Issues" `eject_timeouts` note below is
directly relevant to this project's multiball work once physically wired/playtested (see
`plans/OutsidePerspective.md`/`TODO.md`).

# Multiballs

Related Config File Sections: `multiballs:`, `multiball_locks:`.

MPF's `multiball` feature auto-starts/stops multiballs. Each multiball has a separate name.
Several types exist (run-until-one-ball-left, timed, etc.). Multiball saves can auto-relaunch
balls lost within a window (e.g. first 15s). MPF supports stacking multiple multiballs at once.
Balls can be locked for multiball via `multiball_locks:`.

## Common Issues

**Why does MPF wait ~10s when adding balls to the playfield from the trough during a
multiball?** MPF normally waits for a playfield-switch hit to confirm an ejected ball landed —
but that doesn't work with more than one ball already in play. In that case the launcher instead
waits for its `eject_timeouts` (in `ball_devices`, default 10s) to elapse. Tune `eject_timeouts`
on your launcher device to fix a slow multiball ball-add.

## Monitorable properties

Prefix `device.multiballs.(name)`: `_balls_added_live` (count added into play),
`_balls_live_target` (target ball count), `_enabled` (boolean), `_shoot_again` (boolean, whether
currently trying to keep the multiball live).

## Related How To guides

Multiball locks, multiball with a traditional/virtual ball lock, multiball with multiple lock
devices, add-a-ball multiball — all under mpf-docs `game_logic/multiballs/`.

## Related Events

`multiball_(name)_started`, `_hurry_up`, `_grace_period`, `_shoot_again`, `_lost_ball`,
`_shoot_again_ended`, `_ended`, `_restart_grace_period_started`, `_restarted`;
`ball_save_(multiball_name)_timer_start`, `_add_a_ball_timer_start`.
