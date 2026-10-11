param(
    [Parameter(Mandatory=$true)][string]$JdkBin,
    [Parameter(Mandatory=$true)][string]$R125ClassesJar,
    [Parameter(Mandatory=$true)][string]$WireSource,
    [Parameter(Mandatory=$true)][string]$OutputDir
)
$ErrorActionPreference='Stop'
$probeBase=Split-Path -Parent $PSScriptRoot
[System.IO.Directory]::CreateDirectory($OutputDir) | Out-Null
$probeSources=Get-ChildItem -LiteralPath "$PSScriptRoot\fixtures" -Recurse -Filter '*.java' | ForEach-Object FullName
$probeSources += "$PSScriptRoot\StationDolphinEndpointProbe.java"
$probeSources += "$probeBase\java\org\emulationstation\frontend\netplay\StationMultiplayerEndpoint.java"
$probeSources += "$probeBase\java\org\emulationstation\frontend\netplay\StationMultiplayerTunnel.java"
$probeSources += "$probeBase\java\org\emulationstation\frontend\netplay\StationMultiplayerSession.java"
$probeSources += $WireSource
& "$JdkBin\javac.exe" -encoding UTF-8 -cp $R125ClassesJar -d $OutputDir $probeSources
if($LASTEXITCODE -ne 0){throw 'Endpoint probe compilation failed'}
& "$JdkBin\java.exe" -cp "$OutputDir;$R125ClassesJar" org.emulationstation.frontend.netplay.StationDolphinEndpointProbe
if($LASTEXITCODE -ne 0){throw 'Endpoint probe failed'}
