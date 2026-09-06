<#
.SYNOPSIS
    Start the hw_console Flask app and open it in your default browser.

.DESCRIPTION
    Double-click this file (or run it from a terminal) to launch the hardware bring-up console
    at http://localhost:5000. The Flask dev server runs in the foreground - close the window (or
    Ctrl+C) to stop it.
#>

$ErrorActionPreference = "Stop"

$toolDir = $PSScriptRoot
$python = Join-Path $toolDir "..\..\.venv\Scripts\python.exe"
$url = "http://localhost:5000"

Start-Job -ScriptBlock {
    param($url)
    for ($i = 0; $i -lt 20; $i++) {
        try {
            Invoke-WebRequest -Uri $url -TimeoutSec 1 -UseBasicParsing | Out-Null
            Start-Process $url
            return
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }
} -ArgumentList $url | Out-Null

Set-Location $toolDir
& $python app.py
