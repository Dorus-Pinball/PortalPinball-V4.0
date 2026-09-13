title: Achievements

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/game_logic/achievements/index.md>.
Full raw markdown, as returned by the source fetch.

# Achievements

Related Config File Sections: `achievements:`

MPF "achievements" track major goals a player must reach across a game. Achievements typically
have an associated playfield light/LED (not always) and are tracked separately per player.

The biggest use is for modes: a set of modes each with a light, where the light turns on as each
mode completes. Lights often have multiple states (off=not complete, flashing=active, on=complete,
etc.).

Real-machine examples that map to "achievements" in MPF:

- Attack from Mars: the countries (France/Germany/Italy/England/USA), the Capture inserts
  (1/2/3), the Big-O-Beam inserts (1/2/3), the Atomic Blaster inserts (1/2/3), the blue
  Rule-The-Universe circles (Super Jackpot, Super Jets, Martian Attack Multiball, Total
  Annihilation, Conquer Mars, 5-way Combo).
- Indiana Jones (example cut off in source).

## Monitorable properties

Prefix `device.achievements.(name)`. `_state_` — string name of the current state: `disabled`,
`enabled`, `started`, `stopped`, `selected`, `completed`.
