# Achievement Groups

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/achievements/achievement_groups.md>.
Full raw markdown, as returned by the source fetch.

Related Config File Sections: `achievement_groups:`

Achievement groups group together individual achievements. In the Addams Family, the "mansion
awards" achievement group would contain individual achievements: 9 Mil, 6 Mil, 3 Mil, Thing,
Quick Multiball, Grave Yard at Max, Raise the Dead, etc. — each with its own state
(enabled/started/completed/etc.).

The achievement group enables group-level actions:

- Randomly select one of the incomplete achievements (to flash its light as "selected").
- Change which achievement is selected (e.g. each pop-bumper hit rotates the lit achievement in
  TAF).
- Post an event when all achievements are complete (e.g. to start a wizard mode).
- Post a "start" event for whichever achievement is currently lit (shoot the lit target to start
  it).

## Monitorable properties

Prefix `device.achievement_groups.(name)`. `_enabled_` — boolean, whether the group is enabled.
`_selected_member_` — the currently-selected achievement, or `None`.

## Related How To guides

Recipe: The Addams Family Mansion Awards (mpf-docs `cookbook/TAF_mansion_awards.md`).

## Related Events

Custom events as defined in each achievement's own configuration.
