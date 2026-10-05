param(
 [Parameter(Mandatory=$true)][string]$Root,
 [Parameter(Mandatory=$true)][string]$AngleDll,
 [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
& $Python (Join-Path $PSScriptRoot 'test_console_led_angle_R20.py') --root $Root --baseline (Join-Path $PSScriptRoot 'w16') --angle-dll $AngleDll --ordinary-control (Join-Path $PSScriptRoot 'controls/ordinary-console-snes.png')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$latest = Get-Content -LiteralPath (Join-Path $Root 'led-tests/latest.json') -Raw | ConvertFrom-Json
if (-not $latest.passed) { throw 'ANGLE suite reported a failed criterion; inspect report.json.' }
