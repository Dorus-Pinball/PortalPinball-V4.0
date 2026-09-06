"""Test switch/coil wiring against real hardware, without 50V present.

Confirms a switch's continuity (press/release), and pulses a coil driver so its
CobraPin activation LED can be visually checked - both safe with the 50V/high-voltage
supply off, per this project's OPP bring-up guidance (docs/opp-hardware-reference.md:
"test without coil power first").

Reuses MPF's own service-mode BCP commands (the same ones `mpf service <machine_path>`
uses interactively) rather than talking to the hardware directly - no new protocol code,
just a scripted, prompted sequence instead of a manual shell.

Requires an mpf instance already running against real hardware with the BCP *service*
server up, e.g.:
    tools\\mpf-session.ps1 -Action Start -NoBcp

Use -NoBcp: without it, mpf blocks waiting on its outbound BCP connection to a display
(required: True in mpfconfig.yaml) that isn't running, and never reaches the init phase
that starts the service server on port 5051 - `-NoBcp`/`-b` only disables that outbound
connection attempt; the inbound service server starts either way. (Confirmed on real
hardware 2026-09-06: no -NoBcp -> connection to localhost:5051 refused indefinitely.)

Usage:
    .venv\\Scripts\\python.exe tools\\wiring_test.py
    .venv\\Scripts\\python.exe tools\\wiring_test.py --switches s-tilt --coils c-some-coil
    .venv\\Scripts\\python.exe tools\\wiring_test.py --pulse-ms 200   # e.g. for a real-motion
                                                                       # check with HV present,
                                                                       # if a coil's configured
                                                                       # default is too short to
                                                                       # see move (confirmed on
                                                                       # the flippers: 25ms
                                                                       # default -> no visible
                                                                       # motion, 200ms worked)
"""
import argparse
import asyncio
import sys

from mpf.core.bcp.bcp_socket_client import AsyncioBcpClientSocket

DEFAULT_SWITCHES = ["s-left-flipper", "s-right-flipper"]
DEFAULT_COILS = ["c-flipper-left", "c-flipper-right"]

SAFETY_PHRASE = "HIGH VOLTAGE IS OFF"

BCP_HOST = "localhost"
BCP_PORT = 5051


async def connect():
    """Connect to MPF's BCP service port."""
    try:
        reader, writer = await asyncio.open_connection(BCP_HOST, BCP_PORT)
    except (ConnectionRefusedError, OSError) as e:
        print(f"Could not connect to MPF's service port ({BCP_HOST}:{BCP_PORT}): {e}")
        print(r"Start an mpf session first: tools\mpf-session.ps1 -Action Start -NoBcp")
        sys.exit(1)
    return AsyncioBcpClientSocket(writer, reader)


async def fetch_switches(client):
    client.send("service", {"subcommand": "list_switches"})
    _, args = await client.wait_for_response("list_switches")
    return args["switches"]


async def fetch_coils(client):
    client.send("service", {"subcommand": "list_coils"})
    _, args = await client.wait_for_response("list_coils")
    return args["coils"]


async def pulse_coil(client, name, pulse_ms=None):
    bcp_args = {"subcommand": "coil_pulse", "coil": name}
    if pulse_ms is not None:
        bcp_args["pulse_ms"] = pulse_ms
    client.send("service", bcp_args)
    _, args = await client.wait_for_response("coil_pulse")
    return args.get("error")


def find_by_name(devices, name, name_index):
    for device in devices:
        if device[name_index] == name:
            return device
    return None


async def test_switch(client, name, results):
    print(f"\n=== Switch: {name} ===")
    switches = await fetch_switches(client)
    device = find_by_name(switches, name, 2)
    if not device:
        print("  Not found in MPF's switch list - check the name.")
        results.append((name, "switch", "NOT FOUND"))
        return

    board, number, _, state = device
    print(f"  Board: {board}  Address: {number}  Currently: {'CLOSED' if state else 'OPEN'}")

    input("  Press and HOLD it now, then press Enter...")
    switches = await fetch_switches(client)
    _, _, _, state_pressed = find_by_name(switches, name, 2)
    pass_pressed = bool(state_pressed)
    print(f"  -> {'CLOSED, as expected' if pass_pressed else 'still OPEN - check wiring'}")

    input("  Release it now, then press Enter...")
    switches = await fetch_switches(client)
    _, _, _, state_released = find_by_name(switches, name, 2)
    pass_released = not bool(state_released)
    print(f"  -> {'OPEN, as expected' if pass_released else 'still CLOSED - check wiring'}")

    results.append((name, "switch", "PASS" if (pass_pressed and pass_released) else "FAIL"))


async def test_coil(client, name, results, pulse_ms=None):
    print(f"\n=== Coil: {name} ===")
    coils = await fetch_coils(client)
    device = find_by_name(coils, name, 2)
    if not device:
        print("  Not found in MPF's coil list - check the name.")
        results.append((name, "coil", "NOT FOUND"))
        return

    board, number, _ = device
    print(f"  Board: {board}  Address: {number}")
    print("  Watch this channel's activation LED on the CobraPin board.")

    pulse_desc = f"{pulse_ms}ms" if pulse_ms is not None else "its configured pulse_ms"
    input(f"  Press Enter to pulse it ({pulse_desc})...")
    error = await pulse_coil(client, name, pulse_ms)
    if error:
        print(f"  ERROR pulsing coil: {error}")
        results.append((name, "coil", "ERROR"))
        return

    answer = input("  Did the LED light up? (y/n): ").strip().lower()
    results.append((name, "coil", "PASS" if answer.startswith("y") else "FAIL"))


def print_summary(results):
    print("\n=== Summary ===")
    if not results:
        print("  Nothing was tested.")
        return
    for name, kind, verdict in results:
        print(f"  [{verdict:>9}] {kind:<7} {name}")


async def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--switches", default=",".join(DEFAULT_SWITCHES),
                         help="Comma-separated switch names to test (default: flipper switches)")
    parser.add_argument("--coils", default=",".join(DEFAULT_COILS),
                         help="Comma-separated coil names to test (default: flipper coils)")
    parser.add_argument("--pulse-ms", type=int, default=None,
                         help="Override pulse_ms for all coils (default: each coil's own "
                              "configured pulse_ms). Passing this means you intend a real-motion "
                              "check with HV present, not the default no-HV LED check.")
    args = parser.parse_args()

    switch_names = [s.strip() for s in args.switches.split(",") if s.strip()]
    coil_names = [c.strip() for c in args.coils.split(",") if c.strip()]

    if args.pulse_ms is None:
        print("This test pulses real coil drivers on the machine.")
        print("Confirm the 50V/high-voltage supply is OFF before continuing - coil driver")
        print("LEDs work fine with HV off, that's the whole point of testing this way first.")
        confirm = input(f"Type '{SAFETY_PHRASE}' to continue: ")
        if confirm != SAFETY_PHRASE:
            print("Confirmation not received - exiting without testing anything.")
            return
    else:
        print(f"--pulse-ms {args.pulse_ms} means this is a REAL-MOTION check with HV present.")
        print("Confirm: HV is ON, and the mechanism's travel path is clear (no fingers/tools).")
        confirm = input(f"Type '{SAFETY_PHRASE.replace('OFF', 'ON')}' to continue: ")
        if confirm != SAFETY_PHRASE.replace("OFF", "ON"):
            print("Confirmation not received - exiting without testing anything.")
            return

    client = await connect()
    client.send("service", {"subcommand": "start"})

    results = []
    try:
        for name in switch_names:
            await test_switch(client, name, results)
        for name in coil_names:
            await test_coil(client, name, results, pulse_ms=args.pulse_ms)
    finally:
        client.send("service", {"subcommand": "stop"})
        try:
            await asyncio.wait_for(client.wait_for_response("service_stop"), timeout=2)
        except asyncio.TimeoutError:
            pass

    print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
