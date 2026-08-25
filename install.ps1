<#
.SYNOPSIS
    One-time dev environment setup for Portal Pinball V4.0: creates a local
    Python virtual environment and installs the pinned MPF version into it.

.DESCRIPTION
    This only sets up the MPF (game logic) side of the stack. The display
    side (mpf-gmc) is vendored in machinefolder/addons/mpf-gmc and needs a
    separately-installed Godot 4 editor to run - this script does not
    install Godot.

    Safe to re-run: skips creating the venv if it already exists, and
    (re)installs the pinned mpf version either way so the environment stays
    in sync with this script.

.EXAMPLE
    ./install.ps1
#>

$ErrorActionPreference = "Stop"

# MPF version pin. Matches config_version: 6 / the "MPF 0.80" comment in
# machinefolder/config/config.yaml. Verified working against this repo's
# actual config - see plans/testing-strategy.md.
$MpfVersion = "0.80.0"

$RepoRoot = $PSScriptRoot
$VenvPath = Join-Path $RepoRoot ".venv"

if (-not (Test-Path (Join-Path $RepoRoot "machinefolder"))) {
    Write-Error "machinefolder/ not found next to this script - run install.ps1 from the repo root."
}

# --- Find a usable Python (3.10+, per mpf's supported range) ---
$PythonCmd = $null
foreach ($candidate in @("python", "python3")) {
    $found = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($found) {
        try {
            $versionOutput = & $candidate --version 2>&1
        } catch {
            continue
        }
        if ($versionOutput -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -eq 3 -and $minor -ge 10) {
                $PythonCmd = $candidate
                break
            }
        }
    }
}

if (-not $PythonCmd) {
    Write-Error "No Python 3.10+ interpreter found on PATH (tried 'python', 'python3'). Install Python 3.10-3.14 first."
}

Write-Host "Using $PythonCmd ($(& $PythonCmd --version))"

# --- Create the venv (skip if it already exists) ---
if (Test-Path $VenvPath) {
    Write-Host ".venv already exists, reusing it."
} else {
    Write-Host "Creating .venv ..."
    & $PythonCmd -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create .venv"
    }
}

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$VenvMpf = Join-Path $VenvPath "Scripts\mpf.exe"

# --- Install MPF (pinned) ---
Write-Host "Upgrading pip ..."
& $VenvPython -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to upgrade pip"
}

Write-Host "Installing mpf==$MpfVersion ..."
& $VenvPython -m pip install "mpf==$MpfVersion"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install mpf==$MpfVersion"
}

# --- Verify ---
Write-Host ""
Write-Host "Verifying install ..."
& $VenvMpf --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "mpf --version failed after install - something is wrong with the environment."
}

Write-Host ""
Write-Host "Done. Next steps:"
Write-Host "  Interactive, no hardware needed:  cd machinefolder; ..\.venv\Scripts\mpf -X -t -b"
Write-Host "  Automated test suite:             .venv\Scripts\python -m unittest discover tests"
Write-Host "  Real hardware:                    cd machinefolder; ..\.venv\Scripts\mpf"
Write-Host ""
Write-Host "Display (Godot 4, installed separately, not handled by this script):"
Write-Host "  Open machinefolder/ as a Godot 4 project and run it alongside a running mpf instance."
