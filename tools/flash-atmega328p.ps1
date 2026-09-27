<#
.SYNOPSIS
    Flash a bare ATmega328P-PU for the trough-opto bridge (see plans/read-opto.md), using an
    Arduino (Uno/Duemilanove) running ArduinoISP as the programmer.

.DESCRIPTION
    Three steps, run in order, each a separate -Action:

      1. FlashIsp       - upload the ArduinoISP sketch onto the HOST board (normal USB upload,
                           no target chip involved yet). One-time per host board - once done, it
                           stays an ISP programmer until you upload something else to it.
      2. BurnFuses       - with the TARGET ATmega328P-PU seated in the ISP shield's ZIF socket,
                           set its fuses for the internal 8 MHz oscillator (no external crystal
                           needed) and confirm no bootloader is written (unused - the chip is
                           always reprogrammed via ISP, never over serial). One-time per chip.
      3. UploadSketch    - with the target chip still seated, compile and upload the actual
                           trough-bridge firmware to it via the same ISP link. Repeat any time
                           the firmware changes.

    Compile builds the firmware without any hardware attached - a quick check after editing
    the sketch.

    Fuse values come from MiniCore (https://github.com/MCUdude/MiniCore), a maintained board
    package with a clean "internal 8 MHz" clock option - not hand-typed avrdude fuse bytes.
    Getting AVR fuse bytes wrong (especially the clock-source bits) can leave a chip unable to
    receive further ISP commands at all, needing a high-voltage programmer to recover - not
    something to retype from memory.

.NOTES
    arduino-cli: used from PATH if present, otherwise the copy bundled with Arduino IDE 2
    (resources\app\lib\backend\resources\arduino-cli.exe). Run -Action InstallCore once first.

    Verified on this machine 2026-09-27 (arduino-cli 1.1.1, MiniCore 3.1.3): programmer id
    `arduinoasisp`, and BurnFuses writes lfuse 0xE2 / hfuse 0xD7 / efuse 0xFD. MiniCore 3.x has
    no `pinout` option and names the 328P variant `modelP`.

    ISP shield "disable auto reset" switch: OFF for FlashIsp (the Uno's bootloader needs the
    reset), ON for BurnFuses/UploadSketch - with auto reset active, opening the port reboots the
    Uno, and avrdude only gets in sync after several retries, if at all.

    Observed 2026-09-27: once the chip was running the bridge firmware, reflashing it in the
    ZIF socket failed every time (shield ERR LED on from power-up, avrdude "not in sync:
    resp=0x15"), though the same shield had programmed it fine while blank. Likely cause: the
    chip runs whenever ArduinoISP isn't holding it in reset, and its debug serial output (TX,
    pin 3) reaches the Uno's RX through the shield. Untested workaround: program it in-circuit
    on the breadboard instead - Uno D10 -> pin 1 (RESET), D11 -> pin 17, D12 -> pin 18,
    D13 -> pin 19, plus 5V and GND, with the Stern CN1 cable unplugged (it shares pins 18/19).

.EXAMPLE
    ./flash-atmega328p.ps1 -Action InstallCore
    ./flash-atmega328p.ps1 -Action FlashIsp -HostBoard uno -HostPort COM6
    ./flash-atmega328p.ps1 -Action ListProgrammers
    ./flash-atmega328p.ps1 -Action BurnFuses -HostPort COM6
    ./flash-atmega328p.ps1 -Action Compile
    ./flash-atmega328p.ps1 -Action UploadSketch -HostPort COM6 -SketchDir tools/atmega328p-trough-bridge
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("InstallCore", "FlashIsp", "BurnFuses", "Compile", "UploadSketch", "ListProgrammers")]
    [string]$Action,

    [ValidateSet("uno", "duemilanove")]
    [string]$HostBoard = "uno",

    [string]$HostPort,

    [string]$SketchDir = (Join-Path $PSScriptRoot "atmega328p-trough-bridge"),

    [string]$Programmer = "arduinoasisp",

    # Default matches arduino-cli's default data directory on Windows; override if yours was
    # customized (check with `arduino-cli config dump`).
    [string]$Arduino15Dir = (Join-Path $env:LOCALAPPDATA "Arduino15")
)

$ErrorActionPreference = "Stop"

$MiniCoreUrl = "https://mcudude.github.io/MiniCore/package_MCUdude_MiniCore_index.json"
$MiniCoreFqbn = "MiniCore:avr:328:bootloader=no_bootloader,clock=8MHz_internal,BOD=2v7,LTO=Os,variant=modelP"
$HostFqbn = if ($HostBoard -eq "uno") { "arduino:avr:uno" } else { "arduino:avr:diecimila" }

function Resolve-ArduinoCli {
    $onPath = Get-Command "arduino-cli" -ErrorAction SilentlyContinue
    if ($onPath) {
        return $onPath.Source
    }
    $bundled = @(
        (Join-Path $env:ProgramFiles "Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe")
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($bundled) {
        return $bundled
    }
    throw "arduino-cli not found on PATH or in an Arduino IDE 2 install. Install Arduino IDE 2, " +
          "or: winget install ArduinoSA.CLI"
}

function Assert-Port {
    if (-not $HostPort) {
        throw "Pass -HostPort <COMn> (the port the host Arduino enumerates as - check Device " +
              "Manager, or 'arduino-cli board list' with the host plugged in)."
    }
}

$Cli = Resolve-ArduinoCli

switch ($Action) {

    "InstallCore" {
        & $Cli core update-index --additional-urls $MiniCoreUrl
        & $Cli core install "arduino:avr"
        & $Cli core install "MiniCore:avr" --additional-urls $MiniCoreUrl
        Write-Host "`nCores installed. Run -Action ListProgrammers next to confirm the ISP programmer id."
    }

    "ListProgrammers" {
        & $Cli board details -b $MiniCoreFqbn --list-programmers --additional-urls $MiniCoreUrl
    }

    "FlashIsp" {
        Assert-Port
        # ArduinoISP is a built-in example: inside the avr core on older installs, in the IDE's
        # own Examples folder (next to its bundled arduino-cli) on Arduino IDE 2.
        $searchRoots = @(
            (Join-Path $Arduino15Dir "packages\arduino\hardware\avr"),
            (Join-Path (Split-Path $Cli -Parent) "Examples")
        ) | Where-Object { Test-Path $_ }
        $ispSketch = $searchRoots | ForEach-Object {
            Get-ChildItem -Path $_ -Recurse -Filter "ArduinoISP.ino" -ErrorAction SilentlyContinue
        } | Select-Object -First 1
        if (-not $ispSketch) {
            throw "Could not find the ArduinoISP example under: $($searchRoots -join ', ')."
        }
        Write-Host "Uploading ArduinoISP ($($ispSketch.FullName)) to the host board on $HostPort ..."
        & $Cli compile --fqbn $HostFqbn --upload -p $HostPort $ispSketch.DirectoryName
        Write-Host "`nHost board is now an ISP programmer. Set the shield's 'disable auto reset' switch ON, then seat the target ATmega328P-PU."
    }

    "BurnFuses" {
        Assert-Port
        Write-Host "Burning fuses (internal 8 MHz, no bootloader) on the target chip via $Programmer on $HostPort ..."
        & $Cli burn-bootloader --fqbn $MiniCoreFqbn --programmer $Programmer -p $HostPort `
            --additional-urls $MiniCoreUrl
    }

    "Compile" {
        if (-not (Test-Path $SketchDir)) {
            throw "Sketch directory not found: $SketchDir"
        }
        & $Cli compile --fqbn $MiniCoreFqbn --additional-urls $MiniCoreUrl $SketchDir
    }

    "UploadSketch" {
        Assert-Port
        if (-not (Test-Path $SketchDir)) {
            throw "Sketch directory not found: $SketchDir - write the trough-bridge firmware there first."
        }
        & $Cli compile --fqbn $MiniCoreFqbn --additional-urls $MiniCoreUrl $SketchDir
        & $Cli upload --fqbn $MiniCoreFqbn --programmer $Programmer -p $HostPort `
            --additional-urls $MiniCoreUrl $SketchDir
    }
}
