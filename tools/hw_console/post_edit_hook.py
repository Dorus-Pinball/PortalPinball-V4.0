"""Claude Code PostToolUse hook: after Edit/Write touches a wiring config file or the external
reference manifest, run check_registry.py and, if that passes, generate_docs.py - surfacing any
failure back to Claude immediately.

Wired up in .claude/settings.json under hooks.PostToolUse (matcher "Write|Edit"). Reads the hook
input JSON on stdin, checks whether the edited file is one of the files this project cares about
(hardware/component config, or docs/references/index.yaml), and if so runs check_registry.py then
generate_docs.py and reports failures as a {"decision": "block", "reason": ...} JSON line - on
PostToolUse this feeds the reason back to Claude without undoing the edit (the edit already
happened; "block" here means "make Claude look at this," not "prevent it"). generate_docs.py only
runs after check_registry.py passes, since there's no point re-rendering
wiring-guide.html/wiring-pin-map.md/references/index.md from data that's already known to violate
a collision/pairing rule - check_registry.py only checks hardware data, so it's a harmless no-op
on a references-only edit.
"""
import json
import subprocess
import sys
from pathlib import Path

WATCHED_SUFFIXES = (
    "machinefolder/config/hardware-switches.yaml",
    "machinefolder/config/hardware-coils.yaml",
    "machinefolder/config/hardware-leds.yaml",
    "machinefolder/config/hardware-devices.yaml",
    "tools/hw_console/data/components.yaml",
    "docs/references/index.yaml",
)


def edited_path(payload):
    tool_input = payload.get("tool_input") or {}
    return tool_input.get("file_path") or (payload.get("tool_response") or {}).get("filePath")


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    path = edited_path(payload)
    if not path:
        return 0

    normalized = path.replace("\\", "/")
    if not any(normalized.endswith(suffix) for suffix in WATCHED_SUFFIXES):
        return 0

    tool_dir = Path(__file__).resolve().parent
    result = subprocess.run(
        [sys.executable, str(tool_dir / "check_registry.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        reason = f"Wiring config check failed after editing {path}:\n{result.stdout}{result.stderr}"
        print(json.dumps({"decision": "block", "reason": reason}))
        return 0

    gen_result = subprocess.run(
        [sys.executable, str(tool_dir / "generate_docs.py")],
        capture_output=True,
        text=True,
    )
    if gen_result.returncode != 0:
        reason = (
            f"Wiring config check passed after editing {path}, but regenerating "
            f"wiring-guide.html/wiring-pin-map.md failed:\n{gen_result.stdout}{gen_result.stderr}"
        )
        print(json.dumps({"decision": "block", "reason": reason}))
    else:
        print((result.stdout + gen_result.stdout).strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
