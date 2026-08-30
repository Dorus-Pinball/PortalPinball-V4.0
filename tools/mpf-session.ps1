<#
.SYNOPSIS
    Reliable start/stop of an MPF session from a non-interactive shell (e.g. a Claude Code
    tool session), including against the real OPP hardware.

.DESCRIPTION
    Two problems with running `mpf` directly from a non-interactive shell on this machine:

    1. MPF's default text UI (asciimatics) crashes trying to open a console screen buffer
       when there's no real console attached (`SetConsoleScreenBufferSize` error). MPF's own
       `-t` flag disables it in favor of plain console logging - this script always passes it.
    2. A backgrounded `mpf` process's PID as seen by a Bash/MSYS shell (`ps`) does not match
       its real Windows PID (`Get-Process`) - `kill` from Bash can silently fail to find it,
       leaving a session against real hardware running unnoticed. This script tracks the real
       Windows PID via `Start-Process -PassThru`, so it must be run through a PowerShell
       tool/shell, not Bash, or the same mismatch happens again.

    This script does NOT prompt for confirmation before starting a real-hardware session (no
    interactive stdin to prompt on). Checking with the user before a real-hardware Start is
    the caller's responsibility.

.EXAMPLE
    ./mpf-session.ps1 -Action Start -Virtual -NoBcp
    ./mpf-session.ps1 -Action Status
    ./mpf-session.ps1 -Action Log -Tail 40
    ./mpf-session.ps1 -Action Stop
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Start", "Stop", "Status", "Log")]
    [string]$Action,

    [switch]$Virtual,
    [switch]$NoBcp,
    [int]$Tail = 40,
    [switch]$Follow
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path $PSScriptRoot -Parent
$MachineFolder = Join-Path $RepoRoot "machinefolder"
$MpfExe = Join-Path $RepoRoot ".venv\Scripts\mpf.exe"
$LogsDir = Join-Path $MachineFolder "logs"
$StateFile = Join-Path $LogsDir ".mpf-session.json"
$StdoutLog = Join-Path $LogsDir "mpf-session-stdout.log"
$StderrLog = Join-Path $LogsDir "mpf-session-stderr.log"

function Get-SessionState {
    if (-not (Test-Path $StateFile)) {
        return $null
    }
    try {
        return Get-Content $StateFile -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-AliveProcess($ProcessId) {
    if (-not $ProcessId) {
        return $null
    }
    return Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
}

function Show-LogTail($Path, $Count) {
    if (Test-Path $Path) {
        Write-Host "--- last $Count lines of $(Split-Path $Path -Leaf) ---"
        Get-Content $Path -Tail $Count
    }
}

switch ($Action) {

    "Start" {
        if (-not (Test-Path $MpfExe)) {
            Write-Error "mpf.exe not found at $MpfExe - run install.ps1 first."
        }
        New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null

        $state = Get-SessionState
        if ($state -and (Get-AliveProcess $state.pid)) {
            Write-Host "Already running: PID $($state.pid), mode '$($state.mode)', started $($state.startedAt)."
            Write-Host "Use -Action Stop first if you want to restart it."
            return
        }
        if ($state) {
            Write-Host "Clearing stale session state (PID $($state.pid) is no longer running)."
            Remove-Item $StateFile -Force
        }

        $mpfArgs = @("-t")
        $mode = "hardware"
        if ($Virtual) {
            $mpfArgs += "-X"
            $mode = "virtual"
        }
        if ($NoBcp) {
            $mpfArgs += "-b"
        }

        Write-Host "Starting mpf ($mode mode) ..."
        $proc = Start-Process -FilePath $MpfExe -ArgumentList $mpfArgs -WorkingDirectory $MachineFolder `
            -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog

        $elapsed = 0
        $intervalMs = 400
        $timeoutMs = 4000
        while ($elapsed -lt $timeoutMs) {
            Start-Sleep -Milliseconds $intervalMs
            $elapsed += $intervalMs
            if ($proc.HasExited) {
                break
            }
        }

        if ($proc.HasExited) {
            Write-Host "mpf exited immediately (exit code $($proc.ExitCode)) - did not start cleanly."
            Show-LogTail $StderrLog 30
            return
        }

        $state = [PSCustomObject]@{
            pid        = $proc.Id
            startedAt  = (Get-Date).ToString("o")
            mode       = $mode
            stdoutLog  = $StdoutLog
            stderrLog  = $StderrLog
        }
        $state | ConvertTo-Json | Set-Content $StateFile

        Write-Host "Started: PID $($proc.Id), mode '$mode'."
        Show-LogTail $StderrLog 15
    }

    "Stop" {
        $state = Get-SessionState
        if (-not $state) {
            Write-Host "No tracked mpf session."
            return
        }

        $proc = Get-AliveProcess $state.pid
        if (-not $proc) {
            Write-Host "Session (PID $($state.pid)) already stopped - clearing stale state."
            Remove-Item $StateFile -Force
            return
        }

        Write-Host "Stopping PID $($state.pid) ..."
        Stop-Process -Id $state.pid -Force

        $elapsed = 0
        $intervalMs = 300
        $timeoutMs = 3000
        while ((Get-AliveProcess $state.pid) -and $elapsed -lt $timeoutMs) {
            Start-Sleep -Milliseconds $intervalMs
            $elapsed += $intervalMs
        }

        if (Get-AliveProcess $state.pid) {
            Write-Warning "PID $($state.pid) still alive after stop attempt - check manually."
            return
        }

        Remove-Item $StateFile -Force
        Write-Host "Stopped and confirmed. If this was a real-hardware session, `mpf hardware scan` can confirm the COM ports were released."
    }

    "Status" {
        $state = Get-SessionState
        if (-not $state) {
            Write-Host "No tracked session."
            return
        }

        $proc = Get-AliveProcess $state.pid
        if (-not $proc) {
            Write-Host "Tracked session (PID $($state.pid)) is not running (stale state - not yet cleaned up)."
            return
        }

        $started = [datetime]$state.startedAt
        $uptime = (Get-Date) - $started
        Write-Host "Running: PID $($state.pid), mode '$($state.mode)', uptime $($uptime.ToString('hh\:mm\:ss'))."
        Show-LogTail $state.stderrLog 10
    }

    "Log" {
        $state = Get-SessionState
        $logPath = if ($state) { $state.stderrLog } else { $StderrLog }
        if (-not (Test-Path $logPath)) {
            Write-Host "No session log found at $logPath."
            return
        }
        if ($Follow) {
            Get-Content $logPath -Tail $Tail -Wait
        } else {
            Get-Content $logPath -Tail $Tail
        }
    }
}
