# Skill Shot

Archived 2026-09-13 from
<https://raw.githubusercontent.com/missionpinball/mpf-docs/main/docs/game_logic/skill_shot.md>.
Full raw markdown, as returned by the source fetch. Directly relevant: this project's `skillshot`
feature uses the same rotate-lit-lane-via-flippers idiom shown in the worked example below.

Related Config File Sections: `mode:`, `shots:`, `shot_groups:`, `timers:`, `state_machines:`.

Types of skill shots: time based; hit some target before another target; super skill shot;
lane-change skill shot.

A simple skill shot mode (full working example, three lanes rotated via flipper buttons):

```yaml
mode:
  start_events: ball_started
  stop_events:
    - skill_success
    - skill_failed
  priority: 500
shots:
  skill_l:
    switch: s_lane_l
    profile: skill_shot_profile
    advance_events: mode_skill_shot_started
    show_tokens:
      light: l_lane_l
  skill_m:
    switch: s_lane_m
    profile: skill_shot_profile
    show_tokens:
      light: l_lane_m
  skill_r:
    switch: s_lane_r
    profile: skill_shot_profile
    show_tokens:
      light: l_lane_r
shot_groups:
  skill_shot:
    shots: skill_l, skill_m, skill_r
    rotate_left_events: s_left_flipper_active
    rotate_right_events: s_right_flipper_active
shot_profiles:
  skill_shot_profile:
    states:
      - name: unlit
        show: off
      - name: flashing
        show: flash_color
        show_tokens:
          color: red
        speed: 4
      - name: lit
        show: on
    loop: true
variable_player:
  skill_success:
    score: 42
timers:
  skill_shot_timeout:
    start_value: 0
    end_value: 5
    direction: up
    tick_interval: 1s
    start_running: false
    control_events:
      - action: start
        event: balldevice_plunger_lane_ball_eject_success
state_machines:
  skill_shot_success:
    debug: true
    states:
      start:
        label: Skill shot ready
      success:
        label: Skill successful
        events_when_started: skill_success
      failed:
        label: Skill failed
        events_when_started: skill_failed
    transitions:
      - source: start
        target: success
        events: skill_shot_flashing_hit
      - source: start
        target: failed
        events: skill_shot_unlit_hit, timer_skill_shot_timeout_complete
```

How it works: the three shots (`skill_l`/`skill_m`/`skill_r`) represent the three lanes;
`skill_l` starts lit. The `skill_shot` group rotates via the flippers
(`rotate_left_events`/`rotate_right_events`). Hitting a lit shot posts `skill_shot_lit_hit`;
hitting an unlit one posts `skill_shot_unlit_hit`. A `state_machine` (`skill_shot_success`) with
states `start`/`success`/`failed` avoids a race between those two events — transitions to
`success` or `failed` post `skill_success`/`skill_failed` respectively. A `timers:` entry
(`skill_shot_timeout`) fails the skill shot 5s after the ball leaves the plunger. Typically you'd
create a mode that starts on `skill_success` and another on `skill_failed` to play shows.

## Related How To guides

* How to design a game in MPF using Modes (`mpf-docs-game-design-index` in this archive)
