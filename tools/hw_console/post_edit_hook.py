"""Claude Code PostToolUse hook: after Edit/Write touches a wiring config file, run
check_registry.py and surface any violation back to Claude immediately.

Wired up in .claude/settings.json under hooks.PostToolUse (matcher "Write|Edit"). Reads the hook
input JSON on stdin, checks whether the edited file is one of the wiring config files this
project cares about, and if so runs check_registry.py and reports failures as a
{"decision": "block", "reason": ...} JSON line - on PostToolUse this feeds the reason back to
Claude without undoing the edit (the edit already happened; "block" here means "make Claude look
at this," not "prevent it").
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
    else:
        print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
