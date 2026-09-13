# Config Version 6 Migration Guide

Archived 2026-09-13 from <https://missionpinball.org/latest/config/instructions/config_v6/>.
Rendered-page summary, not a byte-perfect copy. Cited in `plans/OutsidePerspective.md` to confirm
this project (on config_version 6) is on the current format, not a stale one.

## Overview

Config version 6 updates MPF to remove accumulated implementation workarounds ("hacks") from
earlier versions, reducing complexity and enabling cleaner future development. Existing
configuration files need updating to align with v6.

## Migration notes

- Specific YAML changes are detailed in the full reference sections (not captured in this
  summary — check the live URL for the complete list if migrating from an older config version).
- **High score data**: existing high score data files need updating for v6 compatibility, to keep
  historical records accessible after upgrading.

## Why v6 exists

Removes temporary workarounds that had accumulated in prior config versions, simplifying MPF's
underlying systems and clearing the way for future enhancements.
