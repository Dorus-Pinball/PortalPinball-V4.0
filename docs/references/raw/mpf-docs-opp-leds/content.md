title: OPP LEDs

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/leds.md>. Full raw
markdown, as returned by the source fetch.

# OPP LEDs

Related Config File Sections:

* [lights:](/missionpinball/mpf-docs/blob/main/docs/config/lights.md)

OPP hardware can directly drive LED strips. LEDs work similar to matrix lights (chain 0, board 1,
LED 1):

```yaml
lights:
  some_led:
    number: 0-1-1
    subtype: led
    type: rgb
```

Counting always starts at 0, so LED 1 in the example above is the 2nd LED of the strip. OPP
assumes RGB lights by default — for anything else (e.g. RGBW) you need to use channels.

## Light Numbers

Format: `serial_chain-card_num-index`. `chain_serial` only matters with multiple USB-connected
chains — omit it for a single chain, giving `card_num-index`. `card_num` is the board's index on
the chain; the first board is always `0x20`, so `addr = 0x20 + card_num`. With only one board,
omit it too, giving just `index`.

Examples: `0-0-0` = first RGB LED on chain 0, card `0x20` (also writable as `0-0` or `0`,
channels `0-2`). `0-0-1`/`0-1`/`1` = second LED (channels `3-5`). `3-2-6` = 6th LED on board 2
(addr `0x22`) of chain 3 (channels `18-20`).

## Channels

Format: `serial_chain-card_num-internal_index`, where `internal_index = 3 * index` (RGB/GRB
LEDs have exactly 3 channels — doesn't hold for RGBW). Chain lights with `previous:` and MPF
calculates internal channels automatically:

```yaml
lights:
  led_0:
    start_channel: 0-0-0
    subtype: led
    type: rgb    # red: 0-0-0, green: 0-0-1, blue: 0-0-2
  led_1:
    previous: led_0
    subtype: led
    type: rgbw   # red: 0-0-3, green: 0-0-4, blue: 0-0-5, white: 0-0-6
  led_2:
    previous: led_1
    subtype: led
    type: rgbw   # red: 0-0-7, green: 0-0-8, blue: 0-0-9, white: 0-0-10
```

### What if it did not work?

See the OPP troubleshooting guide (`mpf-docs-opp-troubleshooting` in this archive).
