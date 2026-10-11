param(
    [Parameter(Mandatory=$true)][string]$JdkBin,
    [Parameter(Mandatory=$true)][string]$RoomsJar,
    [Parameter(Mandatory=$true)][string]$ClientJar,
    [Parameter(Mandatory=$true)][string]$AndroidJar,
    [Parameter(Mandatory=$true)][string]$JsonJar,
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [Parameter(Mandatory=$true)][string]$Receipt
)
$ErrorActionPreference='Stop'
$repoRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
$r126=Join-Path $repoRoot 'versions\station-dolphin-online-r126-20261011'
$r125=Join-Path $repoRoot 'versions\station-mupen-online-r125-20261011'
$r124=Join-Path $repoRoot 'versions\station-video-room-footer-r124-20261011'
if(Test-Path -LiteralPath $OutputDir){throw 'Use um diretório novo de prova.'}
if((Get-FileHash -LiteralPath $RoomsJar -Algorithm SHA256).Hash.ToLowerInvariant() -ne '44cfdeed223caf6ff47b607d8460137cf80428299c602b97b2e8923b47eaa61b'){throw 'Rooms JAR não é a R126 exata.'}
if((Get-FileHash -LiteralPath $ClientJar -Algorithm SHA256).Hash.ToLowerInvariant() -ne '011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313'){throw 'Classpath cliente não é a R124 preservada.'}
New-Item -ItemType Directory -Path $OutputDir | Out-Null
$classpath=$JsonJar+';'+$AndroidJar+';'+$RoomsJar+';'+$ClientJar
$probeResults=@()
foreach($taskProbe in @(
    @{name='n64';source=(Join-Path $r125 'tests\StationN64ProtocolProbe.java');main='StationN64ProtocolProbe';expected=282},
    @{name='profile';source=(Join-Path $r126 'tests\StationDolphinProfileProbe.java');main='StationDolphinProfileProbe';expected=98},
    @{name='launch';source=(Join-Path $r126 'tests\StationDolphinLaunchProbe.java');main='StationDolphinLaunchProbe';expected=231}
)){
    $taskOut=Join-Path $OutputDir $taskProbe.name
    New-Item -ItemType Directory -Path $taskOut|Out-Null
    & (Join-Path $JdkBin 'javac.exe') -encoding UTF-8 -cp $classpath -d $taskOut $taskProbe.source
    if($LASTEXITCODE -ne 0){throw ('Prova '+$taskProbe.name+' não compilou.')}
    $taskArgs=@('-cp',($taskOut+';'+$classpath),('org.emulationstation.frontend.netplay.'+$taskProbe.main))
    if($taskProbe.name -eq 'launch'){$taskArgs += (Join-Path $taskOut 'fixtures')}
    $taskWatch=[System.Diagnostics.Stopwatch]::StartNew()
    $taskOutput= & (Join-Path $JdkBin 'java.exe') @taskArgs 2>&1 | Out-String
    if($LASTEXITCODE -ne 0){throw ('Prova '+$taskProbe.name+' falhou: '+$taskOutput)}
    $taskWatch.Stop()
    Set-Content -LiteralPath (Join-Path $taskOut 'probe.log') -Value $taskOutput -Encoding utf8
    if($taskProbe.name -eq 'launch'){
        if($taskOutput -notmatch 'launchChecks=(\d+) physicalGameplayValidated=false'){throw 'Saída launch inválida.'}
        $taskCount=[int]$Matches[1]
    }else{$taskCount=[int](($taskOutput.Trim()|ConvertFrom-Json).checks)}
    if($taskCount -ne $taskProbe.expected){throw ('Cobertura inesperada '+$taskProbe.name)}
    $probeResults += @{name=$taskProbe.name;checks=$taskCount;failures=0;elapsedMs=$taskWatch.ElapsedMilliseconds;sourceSha256=(Get-FileHash -LiteralPath $taskProbe.source -Algorithm SHA256).Hash.ToLowerInvariant()}
}
$taskEndpointOut=Join-Path $OutputDir 'endpoint'
$taskWatch=[System.Diagnostics.Stopwatch]::StartNew()
$taskOutput=& (Join-Path $r126 'tests\run_endpoint_probe.ps1') -JdkBin $JdkBin -R125ClassesJar $RoomsJar -WireSource (Join-Path $r124 'java\netplay-src\org\emulationstation\frontend\netplay\StationMultiplayerWire.java') -OutputDir $taskEndpointOut 2>&1 | Out-String
$taskWatch.Stop()
if($taskOutput -notmatch 'PASS checks=(\d+) elapsedMs=(\d+)'){throw ('Prova endpoint falhou: '+$taskOutput)}
$taskCount=[int]$Matches[1]
if($taskCount -ne 470){throw 'Cobertura endpoint inesperada.'}
Set-Content -LiteralPath (Join-Path $taskEndpointOut 'probe.log') -Value $taskOutput -Encoding utf8
$probeResults += @{name='endpoint';checks=$taskCount;failures=0;elapsedMs=$taskWatch.ElapsedMilliseconds;sourceSha256=(Get-FileHash -LiteralPath (Join-Path $r126 'tests\StationDolphinEndpointProbe.java') -Algorithm SHA256).Hash.ToLowerInvariant()}
$taskReceipt=[ordered]@{
    schemaVersion=1
    recordedUtc=[DateTime]::UtcNow.ToString('o')
    kind='fresh-isolated-jvm-r126-system-probes'
    roomsJarSha256=(Get-FileHash -LiteralPath $RoomsJar -Algorithm SHA256).Hash.ToLowerInvariant()
    clientJarSha256=(Get-FileHash -LiteralPath $ClientJar -Algorithm SHA256).Hash.ToLowerInvariant()
    androidApiJarSha256=(Get-FileHash -LiteralPath $AndroidJar -Algorithm SHA256).Hash.ToLowerInvariant()
    jsonJarSha256=(Get-FileHash -LiteralPath $JsonJar -Algorithm SHA256).Hash.ToLowerInvariant()
    probes=$probeResults
    nativeCoreExecuted=$false
    androidExecuted=$false
    signedServerStateCaptured=$false
    physicalGameplayValidated=$false
    apkChanged=$false
}
Set-Content -LiteralPath $Receipt -Value ($taskReceipt|ConvertTo-Json -Depth 8) -Encoding utf8
$probeResults | Select-Object name,checks,failures|ConvertTo-Json -Compress
