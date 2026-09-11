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

    Fuse values come from MiniCore (https://github.com/MCUdude/MiniCore), a maintained board
    package with a clean "internal 8 MHz" clock option - not hand-typed avrdude fuse bytes.
    Getting AVR fuse bytes wrong (especially the clock-source bits) can leave a chip unable to
    receive further ISP commands at all, needing a high-voltage programmer to recover - not
    something to retype from memory.

.NOTES
    Prerequisite (not installed on this machine as of this writing): arduino-cli on PATH.
        winget install ArduinoSA.CLI
    Then run this script once with -Action InstallCore before anything else.

    Confirm the exact MiniCore "Arduino as ISP" programmer id via -Action ListProgrammers before
    your first BurnFuses/UploadSketch run - the default below (Arduino_as_ISP) is MiniCore's
    documented id but hasn't been hand-verified on this machine since arduino-cli isn't
    installed here.

.EXAMPLE
    ./flash-atmega328p.ps1 -Action InstallCore
    ./flash-atmega328p.ps1 -Action FlashIsp -HostBoard uno -HostPort COM7
    ./flash-atmega328p.ps1 -Action ListProgrammers
    ./flash-atmega328p.ps1 -Action BurnFuses -HostPort COM7
    ./flash-atmega328p.ps1 -Action UploadSketch -HostPort COM7 -SketchDir tools/atmega328p-trough-bridge
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("InstallCore", "FlashIsp", "BurnFuses", "UploadSketch", "ListProgrammers")]
    [string]$Action,

    [ValidateSet("uno", "duemilanove")]
    [string]$HostBoard = "uno",

    [string]$HostPort,

    [string]$SketchDir = (Join-Path $PSScriptRoot "atmega328p-trough-bridge"),

    [string]$Programmer = "Arduino_as_ISP",

    # Default matches arduino-cli's default data directory on Windows; override if yours was
    # customized (check with `arduino-cli config dump`).
    [string]$Arduino15Dir = (Join-Path $env:LOCALAPPDATA "Arduino15")
)

$ErrorActionPreference = "Stop"

$MiniCoreUrl = "https://mcudude.github.io/MiniCore/package_MCUdude_MiniCore_index.json"
$MiniCoreFqbn = "MiniCore:avr:328:bootloader=no_bootloader,clock=8MHz_internal,BOD=2v7,LTO=Os,variant=328standard,pinout=standard"
$HostFqbn = if ($HostBoard -eq "uno") { "arduino:avr:uno" } else { "arduino:avr:diecimila" }

function Assert-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "$name not found on PATH. See the .NOTES block in this script for install steps."
    }
}

function Assert-Port {
    if (-not $HostPort) {
        throw "Pass -HostPort <COMn> (the port the host Arduino enumerates as - check Device " +
              "Manager, or 'arduino-cli board list' with the host plugged in)."
    }
}

Assert-Command "arduino-cli"

switch ($Action) {

    "InstallCore" {
        arduino-cli core update-index --additional-urls $MiniCoreUrl
        arduino-cli core install "arduino:avr"
        arduino-cli core install "MiniCore:avr" --additional-urls $MiniCoreUrl
        Write-Host "`nCores installed. Run -Action ListProgrammers next to confirm the ISP programmer id."
    }

    "ListProgrammers" {
        arduino-cli board details -b $MiniCoreFqbn --additional-urls $MiniCoreUrl
    }

    "FlashIsp" {
        Assert-Port
        $avrCoreRoot = Join-Path $Arduino15Dir "packages\arduino\hardware\avr"
        if (-not (Test-Path $avrCoreRoot)) {
            throw "arduino:avr core not found under $avrCoreRoot - run -Action InstallCore first " +
                  "(or pass -Arduino15Dir if your data directory is elsewhere)."
        }
        $ispSketch = Get-ChildItem -Path $avrCoreRoot -Recurse -Filter "ArduinoISP.ino" -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if (-not $ispSketch) {
            throw "Could not find the ArduinoISP example under $avrCoreRoot."
        }
        Write-Host "Uploading ArduinoISP ($($ispSketch.FullName)) to the host board on $HostPort ..."
        arduino-cli compile --fqbn $HostFqbn --upload -p $HostPort $ispSketch.DirectoryName
        Write-Host "`nHost board is now an ISP programmer. Seat the target ATmega328P-PU in the ISP shield's ZIF socket next."
    }

    "BurnFuses" {
        Assert-Port
        Write-Host "Burning fuses (internal 8 MHz, no bootloader) on the target chip via $Programmer on $HostPort ..."
        arduino-cli burn-bootloader --fqbn $MiniCoreFqbn --programmer $Programmer -P $HostPort `
            --additional-urls $MiniCoreUrl
    }

    "UploadSketch" {
        Assert-Port
        if (-not (Test-Path $SketchDir)) {
            throw "Sketch directory not found: $SketchDir - write the trough-bridge firmware there first."
        }
        arduino-cli compile --fqbn $MiniCoreFqbn --additional-urls $MiniCoreUrl $SketchDir
        arduino-cli upload --fqbn $MiniCoreFqbn --programmer $Programmer -P $HostPort `
            --additional-urls $MiniCoreUrl $SketchDir
    }
}
