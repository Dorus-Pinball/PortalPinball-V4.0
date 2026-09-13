title: OPP Switches

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/switches.md>. Full raw
markdown, as returned by the source fetch.

# OPP Switches

Related Config File Sections:

* [switches:](/missionpinball/mpf-docs/blob/main/docs/config/switches.md)

For switches, you can use most of the settings as outlined in the `switches:` section of the
config file reference. There are only a few things that are OPP-specific:

## Number

OPP switches are numbered sequentially depending on which wing board is the switch input. Wing
position 0 contains switch numbers 0 to 7. Wing position 1 contains switch numbers 8 to 15. Wing
position 2 contains switch numbers 16 to 23. Wing position 3 contains switch numbers 24 to 31.
The switch is numbered using the position of the OPP card (starting at 0), then a '-', and
finally the switch number on the card.

Enter them as a combination of board-switch, like `0-12`.

```yaml
switches:
  some_switch:
    number: 0-15
```

The above example configures a switch input as the first OPP card, and the second wing board,
last input. On the microprocessor card, the input is marked as 1.7 (wing port 1, position 7).

Switch inputs for solenoids follow the same number convention. Since only four inputs are
available for each wing card, it uses the first four switch numbers. Solenoid wing 0 uses switch
numbers 0 to 3. Solenoid wing 1 uses switch numbers 8 to 11. Solenoid wing 2 uses switch numbers
16 to 19. Solenoid wing 3 uses switch numbers 24 to 27.

Switch inputs for a switch matrix are numbered slightly differently. To configure an 8x8 switch
matrix, wing 2 is configured as the matrix input and wing 3 as the matrix output. The OPP
hardware strobes the eight outputs while reading from the eight inputs, allowing 64 inputs to be
read using only 16 wires. The matrix switch inputs are numbered from 32 to 95. Switches 32-39 are
column 0, 40-47 column 1, 48-55 column 2, 56-63 column 3, 64-71 column 4, 72-79 column 5, 80-87
column 6, 88-95 column 7.

## Fully working example

A minimal working set for the Cobra controller (only needs the microcontrollers powered, no HV
supply, one switch connected):

```yaml
#config_version=5

hardware:
   platform: opp
   driverboards: gen2

opp:
   ports: /dev/ttyACM0, /dev/ttyACM1 # change this if you are not using Linux

switches:
   my_test_switch:
      debug: true
      number: 0-0-16 # change this if you have connected the switch to a different input
      tags: switch_tag1, switch_tag2
      events_when_activated: active_event1, active_event2
      events_when_deactivated: inactive_event1
```

With `debug: true` set, `mpf monitor` will show the events posted when pressing/releasing the
switch: `my_test_switch_active`/`_inactive`, `sw_switch_tag1[_active/_inactive]`,
`sw_switch_tag2[_active/_inactive]`, and the configured `active_event1`/`active_event2`/
`inactive_event1`.

### What if it did not work?

See the OPP troubleshooting guide (`mpf-docs-opp-troubleshooting` in this archive).
