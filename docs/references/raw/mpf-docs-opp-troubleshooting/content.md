title: Troubleshooting OPP

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/troubleshooting.md>.
Full raw markdown, as returned by the source fetch.

# Troubleshooting OPP

General troubleshooting guide first, then these OPP-specific steps:

## Run Hardware Scan

`mpf hardware scan` shows whether OPP boards are talking to MPF over USB:

```
$ mpf hardware scan

Connected CPUs:
 - Port: com1 at 115200 baud
 -> Board: 0x20 Firmware: 0x10100
 -> Board: 0x21 Firmware: 0x10100

Incand cards:
 - CPU: com1 Board: 0x20 Card: 0 Numbers: [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]

Input cards:
 - CPU: com1 Board: 0x20 Card: 0 Numbers: [0, 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15]
 - CPU: com1 Board: 0x21 Card: 1 Numbers: [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

Solenoid cards:
 - CPU: com1 Board: 0x20 Card: 0 Numbers: [0, 1, 2, 3]
 - CPU: com1 Board: 0x21 Card: 1 Numbers: [12, 13, 14, 15]

LEDs:
 - CPU: com1 Board: 0x21 Card: 1
```

## Enable Debugging

Add `debug: true` to the `opp:` config section for verbose diagnostics (slows MPF down a bit —
disable after debugging):

```yaml
opp:
  debug: true
```

## Reducing the polling rate

If OPP boards can't answer polls fast enough, lower `poll_hz` (default 100):

```yaml
opp:
  ports: COM7
  poll_hz: 50
```

Note: this increases time between switch reads — too low and you can miss hits between polls
(only do this if you're actually hitting issues).

## Coils Are Not Firing

(Points to the shared `troubleshooting_coils.md`/`troubleshooting_lights.md`/`troubleshooting.md`
snippets in mpf-docs — general driver/lighting troubleshooting steps, not OPP-specific content
beyond what's captured above.)
