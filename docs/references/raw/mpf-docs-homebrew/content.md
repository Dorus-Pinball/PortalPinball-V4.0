---
title: Controlling a custom homebrew machine with MPF
---

Archived 2026-09-13 from
<https://raw.githubusercontent.com/missionpinball/mpf-docs/main/docs/machines/homebrew.md>. Full
raw markdown, as returned by the source fetch.

# Controlling a custom "homebrew" machine with MPF

Details for how to build custom machine hardware are covered on the [PinballMakers.com
Wiki](http://pinballmakers.com). We cover some general areas here and suggest you investigate
those on your own.

## Control System

To power a new *custom* pinball machine you build yourself, buy new custom driver boards. Common
choices:

* FAST Pinball
* CobraPin Pinball Controller
* Multimorphic P3-Roc
* Open Pinball Project (OPP)
* LISY Home (custom pinball version of LISY)
* Arduino Pinball Controller

FAST and Multimorphic are commercial systems. OPP is open source/open hardware — cheaper, but
barebones and requires time/skill. CobraPin is based on OPP with the goal of making OPP more
accessible, providing something closer to an all-in-one solution.

You might also want control boards for servos, steppers, and lights — common choices: Fadecandy
(WS2812 lights — FAST and P3-Roc offer this too), Pololu Maestro (servos).

## Power and Wiring

Invest time early into your power supply and wiring — see mpf-docs' "Voltages and Power" and
"Wiring and Connectors in Pinball Machines" pages.

## Parts and Assemblies

MPF supports a variety of pinball mechs. Look at manuals of existing machines to find mech part
numbers. For homebrew machines it's wise to buy assemblies rather than individual parts — mechs
have many parts and assemblies are often cheaper. Pinballlife has a homebrew section worth
checking; Marcos Specialities offers more raw parts but is less homebrew-focused.
