title: Configuring your machine for OPP

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/config.md>. Full raw
markdown, as returned by the source fetch.

# Configuring your machine for OPP

Related Config File Sections:

* [hardware:](/missionpinball/mpf-docs/blob/main/docs/config/hardware.md)
* [opp:](/missionpinball/mpf-docs/blob/main/docs/config/opp.md)

## 1. Configure the Hardware platform for OPP

```yaml
hardware:
  platform: opp
```

## 2. Configure the OPP-specific hardware settings

MPF's default config (`mpfconfig.yaml`) has sane defaults — the only thing you must configure is
your ports.

### Understanding OPP hardware ports

OPP controllers are USB devices that present as "virtual" COM ports. Exact names/numbers vary by
computer. USB-to-serial converters add latency vs. a "real" serial port; a real serial port must
use 5V signal levels when talking to OPP hardware.

### Adding the port to your config file

```yaml
opp:
  ports: COM7
```

On Windows, COM port numbers greater than 9 may need the `\\.\COM10` form (though Windows 10 can
often just use `com10`, `com11`, etc. directly — try that first). On Linux, usually
`/dev/ttyACM0` or `/dev/ttyACM1`. On Mac, `/dev/cu.modemXXXX`.

## What if it did not work?

See the OPP troubleshooting guide (`mpf-docs-opp-troubleshooting` in this archive).
