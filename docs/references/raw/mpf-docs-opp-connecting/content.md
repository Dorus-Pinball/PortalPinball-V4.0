title: Connecting OPP to your computer

Archived 2026-09-13 from
<https://github.com/missionpinball/mpf-docs/blob/main/docs/hardware/opp/connecting.md>. Full raw
markdown, as returned by the source fetch.

# Connecting OPP to your computer

Connect the OPP board to your computer via USB. Make sure OPP chains don't get too long since
serial throughput is limited per chain. You can connect multiple chains.

## Verify Connected Boards via mpf hardware scan

`mpf hardware scan` lists connected node boards:

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

If boards don't show up, see the OPP troubleshooting guide (`mpf-docs-opp-troubleshooting` in
this archive).

## On Linux: Blacklist cytherm module

The Cypress thermometer module conflicts with OPP. In `/etc/modprobe.d/blacklist.conf`:

```
blacklist cytherm
```

Create the file as root if it doesn't exist, then reboot.

## On Linux: Add udev rules for persistent device names

With more than one `ttyACM` device, assign stable names based on USB port. Find the port's
`DEVPATH` via `udevadm info /dev/ttyACM0`, then add a rule in `/etc/udev/rules.d/opp.rules`:

```
SUBSYSTEM=="tty", ACTION=="add", DEVPATH=="/devices/pci0000:00/0000:00:14.0/usb1/1-4/1-4:1.1/*", SYMLINK+="ttyOPP1", GROUP="adm", MODE="0660"
```

After reboot, that USB port yields `/dev/ttyOPP1`.

## On Ubuntu: Stop ModemManager

ModemManager tries to initialize `/dev/ttyACMxx` devices as modems, causing delays/garbage on
the bus. If you don't use modems:

```
sudo systemctl disable ModemManager
sudo systemctl stop ModemManager
```

## What if it did not work?

See the OPP troubleshooting guide (`mpf-docs-opp-troubleshooting` in this archive).
