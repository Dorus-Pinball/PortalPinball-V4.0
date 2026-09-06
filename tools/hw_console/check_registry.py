"""Standalone collision + pairing-rule checker for the hardware config.

Run directly (`python tools/hw_console/check_registry.py`) or via the PostToolUse hook configured
in .claude/settings.json, which runs this after every edit to the hardware config/registry files.
Exits non-zero with every violation listed if anything is wrong; see docs/opp-hardware-reference.md
for the rules this enforces.
"""
import sys

import registry


def main():
    violations = registry.full_scan()
    if not violations:
        print("check_registry: OK - no collisions or pairing-rule violations found.")
        return 0

    print(f"check_registry: {len(violations)} violation(s) found:")
    for v in violations:
        print(f"  - {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
