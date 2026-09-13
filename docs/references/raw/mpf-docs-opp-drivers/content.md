title: OPP coils / drivers

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/drivers.md>. Full raw
markdown, as returned by the source fetch.

# OPP coils / drivers

Related Config File Sections:

* [coils:](/missionpinball/mpf-docs/blob/main/docs/config/coils.md)
* [opp_coils:](/missionpinball/mpf-docs/blob/main/docs/config/opp_coils.md)

There are a few things to know about controlling drivers and coils with OPP hardware.

## Number

OPP coils are numbered sequentially depending on which wing board is the coil output. Wing
position 0 contains coil numbers 0 to 3. Wing position 1 contains coil numbers 4 to 7. Wing
position 2 contains coil numbers 8 to 11. Wing position 3 contains coil numbers 12 to 15. The
coil is numbered using the position of the OPP card (starting at 0), then a '-', and finally the
coil number on the card.

```yaml
coils:
  some_coil:
    number: 0-12
```

The above example configures a coil output as the first OPP card, third wing board, first
output. On the microprocessor card, the output is marked as 3.4 (wing port 3, position 4).

## Pulse time

```yaml
coils:
  some_coil:
    number: 0-12
    default_pulse_ms: 30
```

When MPF sends this coil a pulse command, it fires for 30ms.

## Hold Power

`default_hold_power` (0.0-1.0) defines the time share the coil is on. The period is fixed at
16ms for OPP — 0.25 = 4ms/16ms = 25% hold.

```yaml
coils:
  some_coil:
    number: 0-3
    default_pulse_ms: 32
    default_hold_power: 0.5
```

## Pulse Power

(OPP firmware 2.3.0.5+ only.) `default_pulse_power` (0.0-1.0) tunes the initial pulse's power
share, useful with lower-voltage coils on a 48V source. Values under 0.03125 are forced to
3.125%.

```yaml
coils:
  some_coil:
    number: 0-3
    default_pulse_ms: 32
    default_pulse_power: 0.8125
    default_hold_power: 0.125
```

## Recycle Factor

`recycle: True` + `platform_settings.recycle_factor` sets cooldown time =
`default_pulse_ms * recycle_factor`.

```yaml
coils:
  some_coil:
    number: 0-3
    default_pulse_ms: 10
    default_recycle: true
    platform_settings:
      recycle_factor: 2
```

### What if it did not work?

See the OPP troubleshooting guide (`mpf-docs-opp-troubleshooting` in this archive).

### Related How To guides

Coil resistance/hardware details, dual-wound coil wiring, dual- vs single-wound coils, hold
power, pulse power tuning, recycle/cool-down time, flipper details, single/dual-wound flipper
config, flipper EOS switches — all under `mechs/coils/` and `mechs/flippers/` in mpf-docs.
