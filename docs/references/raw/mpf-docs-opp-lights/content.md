title: OPP Lights

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/lights.md>. Full raw
markdown, as returned by the source fetch. Covers incandescent-wing (matrix) bulbs, not the
serial LED strips — see `mpf-docs-opp-leds` in this archive for those.

# OPP Lights

Related Config File Sections:

* [lights:](/docs/config/lights.md)

If you're using an OPP incandescent wing card, the lights are numbered the same as the input
switches. OPP bulbs are numbered sequentially depending on which wing board controls the output.
Wing position 0 contains bulbs 0 to 7. Wing position 1 contains bulbs 8 to 15. Wing position 2
contains bulbs 16 to 23. Wing position 3 contains bulbs 24 to 31. The bulb is numbered using the
position of the OPP card (starting at 0), then a '-', and finally the bulb number on the card.

```yaml
lights:
  some_light:
    number: 1-16
    subtype: matrix
```

The above example configures a bulb on the second OPP card, third wing board, first bulb. On the
microprocessor card, the input is marked as 2.0 (wing port 2, position 0).

## What if it did not work?

See the OPP troubleshooting guide (`mpf-docs-opp-troubleshooting` in this archive).
