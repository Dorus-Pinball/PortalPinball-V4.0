# Switch/coil wiring test tool (no-HV, LED-based coil check)

## Context

Flipper switches (`s-left-flipper` 0-0-1, `s-right-flipper` 0-0-2) and coils
(`c-flipper-left` 0-0-8, `c-flipper-right` 0-0-9) were just wired for real onto the Cobra
board (chain 0, board `0x20`), per `TODO.md`/`hardware-switches.yaml`/`hardware-coils.yaml`.
Per this project's own documented OPP bring-up guidance (`docs/opp-hardware-reference.md`,
quoted in `design/physical-checklists/wiring-guide.html`): mixing up bank power and driver
wiring "could cause blown FETs, coils, and fuses" (CobraPin's own words) — "test without coil
power first." CobraPin boards have a per-channel **activation LED** (lights when a driver
output is switched on at the logic level, independent of whether 50V is actually connected to
that bank) — so pulsing a coil with 50V off and watching for the right LED is a safe way to
confirm coil driver wiring before ever applying high voltage. Switches need a parallel
continuity check.

This tool is deliberately **not flipper-specific** — it's the standard check to run against
*any* switch/coil pair as more of the machine gets wired for real. `TODO.md` still lists tilt,
the right ramp diverter, and the VUK eject coils as needing this same physical continuity/LED
check before their config comes off DRAFT.

## Approach — reuse MPF's own service-mode BCP commands, don't reinvent coil pulsing

MPF 0.80 already has the primitives needed, reachable without touching the (unwired) physical
service-mode nav switches:

- MPF runs a BCP **server** on `127.0.0.1:5051` by default (`mpf/mpfconfig.yaml`, `bcp:
  servers:` block) — no config change needed.
- `mpf/commands/service.py`'s `ServiceCli` (the `mpf service <machine_path>` CLI) talks to
  that server via `mpf.core.bcp.bcp_socket_client.AsyncioBcpClientSocket` and already
  implements `list_switches` (board/number/name/state for every switch), `list_coils`
  (board/number/name), and `coil_pulse <name> [pulse_ms:N] [pulse_power:N]`
  (`mpf/core/bcp/bcp_interface.py`'s `_service()`/`_coil_pulse()`, ~line 127-204). Omitting
  `pulse_ms` falls back to the coil's configured default (`Driver.pulse()`,
  `mpf/devices/driver.py:332` — confirmed `pulse_ms=None` uses the config value, e.g.
  `c-flipper-left`'s `default_pulse_ms: 25`).
  It also sends `{"subcommand": "start"}`/`"stop"` around the session, which puts MPF into
  its real `service` mode (pauses normal attract/game logic) — worth keeping for the same
  reason `ServiceCli` does it.
- So the new script doesn't implement any BCP/OPP protocol itself — it imports
  `AsyncioBcpClientSocket` (same class `service.py` uses) and drives the same three
  subcommands in a fixed, prompted sequence instead of an interactive `cmd.Cmd` shell.

**Prerequisite (not handled by this script):** an `mpf` instance must already be running
against real hardware with the BCP *service server* up — i.e. started via
`tools/mpf-session.ps1 -Action Start -NoBcp`. Keeping session lifecycle (start/stop mpf)
separate from this wiring-test logic matches how `mpf-session.ps1` and `hw_console` are
already split by concern.

**Correction from real-hardware verification (2026-09-06):** the plan originally said *not*
to pass `-NoBcp` — that was backwards. Without `-NoBcp`, mpf blocks on its outbound BCP
connection to a display (`local_display`, `required: True` in `mpfconfig.yaml`) that isn't
running, and never reaches the init phase that starts the inbound service server on port
5051 — confirmed live: without `-NoBcp` the connection to `localhost:5051` was refused
indefinitely. `-NoBcp`/`-b` only disables that one outbound connection attempt; the inbound
service server (which `list_switches`/`list_coils`/`coil_pulse` all depend on) starts either
way.

## `tools/wiring_test.py`

Python, run via `.venv\Scripts\python.exe tools\wiring_test.py [--switches name,...]
[--coils name,...]` (no new dependencies — `AsyncioBcpClientSocket` is already part of the
installed `mpf` package). Defaults to the flipper pair when no args given; **pass
`--switches`/`--coils` to run it against any other component** (tilt, diverter, VUKs, etc.) —
that's the whole point of keeping the device list a CLI argument instead of hardcoding it.

1. **Connect**: open a socket to `localhost:5051`. On refusal, print a message pointing at
   `tools/mpf-session.ps1 -Action Start` and exit — don't try to start MPF itself.
2. **Safety gate**: print the same style of explicit warning MPF's own
   `mpf/commands/hardware.py` `benchmark()` command uses ("Turn off high voltage!") and
   require the user to type an exact confirmation phrase before continuing.
3. Send `{"subcommand": "start"}` (enters service mode); always send
   `{"subcommand": "stop"}` on exit, including on Ctrl+C/error (`try/finally`).
4. **Switch test**, per switch: `list_switches` → find the target by name → print its real
   board/address (from the response, not hardcoded) and current state → prompt "press and
   hold, then Enter" → re-query → expect closed → prompt "release, then Enter" → re-query →
   expect open → PASS/FAIL each transition.
5. **Coil test**, per coil: `list_coils` → print its board/address → prompt "Enter to pulse
   (uses configured pulse_ms)" → send `coil_pulse <name>` → ask "did the LED light? (y/n)" →
   record.
6. Print a final PASS/FAIL/UNCONFIRMED summary table over all switches/coils tested.

## Docs touched

- `README.md` — short bit near "Hardware bring-up console" pointing at this script, its
  prerequisite, and that it's the no-HV switch/coil wiring check.
- `design/physical-checklists/wiring-guide.html` — the existing "test without coil power
  first" passage gets a one-line pointer to this script.
- `TODO.md` — note the tool exists next to the flipper wiring entry (no checkbox flips; the
  physical check still needs the user to actually run it).

## Verification

1. Start a real-hardware session: `tools/mpf-session.ps1 -Action Start` (confirm with the
   user first — live on the cabinet).
2. Run `wiring_test.py` with 50V confirmed off; confirm it refuses to proceed without the
   typed safety confirmation.
3. Switch test: physically press/release each target switch when prompted, confirm the
   script reports the correct board/address and correctly detects open→closed→open.
4. Coil test: confirm each pulse prompt reports the correct board/address, pulse the coil,
   visually confirm the activation LED on the Cobra board, answer the y/n prompt, confirm the
   final summary reflects it correctly.
5. Stop the session via `tools/mpf-session.ps1 -Action Stop` afterward.

## Findings from the first real-hardware run (flippers, 2026-09-06)

- **`-NoBcp` is required**, not forbidden — see the correction above.
- **Windows USB selective suspend caused a mid-session serial disconnect.** ~70s into an idle
  service-mode session (well after the last coil pulse, so not pulse-caused), one Cobra
  board's COM port threw `ClearCommError failed ... PermissionError(13, 'The device does not
  recognize the command.')`, crashing mpf. Classic USB-serial-CDC-idle-suspend symptom on
  Windows. Fixed at the OS level: `powercfg` USB selective suspend disabled for both AC and
  battery on this laptop's active power plan (GUID `2a737441-1930-4402-8d77-b2bebba308a3` /
  `48e6b7a6-50f5-4782-a5d4-53bb8f07e226`). Not previously documented anywhere in this repo —
  now noted in `TODO.md` since a reimage/new power plan would silently reintroduce it.
- **`c-flipper-left`/`c-flipper-right`'s `default_pulse_ms: 25` is too weak for real
  mechanical travel with HV present** — produced no visible flipper motion; `pulse_ms: 200`
  worked. 25ms was fine for the no-HV LED check (that only needs the driver logic to switch,
  not real travel). Real tuning (lower than 200ms, ideally with the coil's actual specs in
  mind, especially since there's no EOS switch to cut hold power) is still an open question —
  `wiring_test.py` grew a `--pulse-ms` override for exactly this case.
- **Testing gameplay-triggered devices (flippers-in-a-game, not just isolated pulses)
  without a physically-wired start/launch button**: MPF's BCP interface accepts an inbound
  `switch` command (`{"name": "s-start", "state": 1}`, then `0`) that calls
  `switch_controller.process_switch_obj(..., logical=True)` — the same code path a real
  switch activation takes. This is the same mechanism the Godot display's `[keyboard]`
  mapping in `gmc.cfg` uses. Used live to start a game and plunge a ball with neither
  `s-start` nor `s-launch` physically wired yet, confirming the `flippers:` device (enables
  on `ball_started`) responds correctly to real button holds during actual gameplay, not
  just isolated `coil_pulse` calls.
- **New gap found, not flipper-related**: with a real game running, `bd-trough`'s eject to
  `bd-plunger` kept failing and retrying every ~10s (`balldevice_..._ball_eject_failed`) —
  the plunger-lane eject-confirm switch likely isn't registering the ball's arrival. Logged
  in `TODO.md`; not investigated further this session.

## Status: active — used first for the flipper pair (switches, coils via LED with no HV, and
real gameplay hold behavior with HV, all confirmed working); reuse for the next component as
it gets wired for real (see `TODO.md`'s "Blocked on physical hardware work" list).
