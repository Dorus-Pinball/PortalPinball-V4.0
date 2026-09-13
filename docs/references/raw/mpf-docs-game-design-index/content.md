title: How to design a game in MPF using Modes

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/game_design/index.md>. Full raw
markdown, as returned by the source fetch. This is MPF's own top-level game-design guide — the
"Layering Modes Example" section links to `mpf-docs-mode-layering` in this same archive, the
pattern `design/README.md`'s Field/Mission/Wizard layering already follows.

# How to design a game in MPF using Modes

Assumes hardware devices (especially ball devices) are already configured. This section is
structured into:

## Mode Selection and Game Startup

How to select modes/players at start? Implement a (timed) skill shot? How does a player qualify
for a mode? How to start it? Can multiple modes run at once?

## Game Mode

How to track progress inside a mode? How does it end? Always succeed? Can it time out? Restart if
failed? Where does it continue on restart? Roll-over lanes, mystery awards, stand-up target bank
modes?

## Wizard Modes

Track achievements toward one/multiple wizard modes? How to start one? What happens after?

## Ball End Modes

Start a mode after a player's ball drains? Implement a bonus mode?

## Game End Modes

Start a mode after the last player's last ball drains? Highscore mode? Match mode?

## Other Modes

Which modes run outside a game? Attract control? Credits? Tilt? Service mode?

## Layering Modes Example

Defining mode categories/helper modes; moving in/out of game and wizard modes; tracking/
persisting progress outside modes — see `mpf-docs-mode-layering` in this archive.
