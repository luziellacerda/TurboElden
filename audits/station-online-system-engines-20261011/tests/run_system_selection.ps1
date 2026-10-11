param(
    [Parameter(Mandatory=$true)][string]$JdkBin,
    [Parameter(Mandatory=$true)][string]$RoomsJar,
    [Parameter(Mandatory=$true)][string]$ClientJar,
    [Parameter(Mandatory=$true)][string]$AndroidJar,
    [Parameter(Mandatory=$true)][string]$JsonJar,
    [Parameter(Mandatory=$true)][string]$Apk,
    [Parameter(Mandatory=$true)][string]$AuditReceipt,
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [Parameter(Mandatory=$true)][string]$Receipt
)
$ErrorActionPreference='Stop'
function Get-TaskSha([string]$TaskPath){
    return (Get-FileHash -LiteralPath $TaskPath -Algorithm SHA256).Hash.ToLowerInvariant()
}
if(Test-Path -LiteralPath $OutputDir){throw 'Use um diretório novo de prova.'}
if((Get-TaskSha $RoomsJar) -ne '44cfdeed223caf6ff47b607d8460137cf80428299c602b97b2e8923b47eaa61b'){throw 'Rooms JAR não é a R126 exata.'}
if((Get-TaskSha $ClientJar) -ne '011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313'){throw 'Client JAR não é a R124 preservada.'}
$taskApkSha=Get-TaskSha $Apk
if($taskApkSha -ne 'f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d'){throw 'APK não é a R126 exata.'}
$taskAudit=Get-Content -LiteralPath $AuditReceipt -Raw|ConvertFrom-Json
if($taskAudit.failures -ne 0 -or $taskAudit.apkSha256 -ne $taskApkSha -or $taskAudit.canonicalSystems -ne 50 -or $taskAudit.catalogAliases -ne 78){throw 'Recibo estrutural não corresponde à prova.'}
$taskSources=@(
    (Join-Path $PSScriptRoot 'StationSystemSelectionProbe.java'),
    (Join-Path $PSScriptRoot 'fixtures\android\content\Context.java'),
    (Join-Path $PSScriptRoot 'fixtures\android\content\res\AssetManager.java')
)
New-Item -ItemType Directory -Path $OutputDir|Out-Null
$taskClasspath=$JsonJar+';'+$AndroidJar+';'+$RoomsJar+';'+$ClientJar
& (Join-Path $JdkBin 'javac.exe') -encoding UTF-8 -cp $taskClasspath -d $OutputDir @taskSources
if($LASTEXITCODE -ne 0){throw 'Seletor isolado não compilou.'}
$taskWatch=[System.Diagnostics.Stopwatch]::StartNew()
$taskOutput=& (Join-Path $JdkBin 'java.exe') -cp ($OutputDir+';'+$taskClasspath) org.emulationstation.frontend.netplay.StationSystemSelectionProbe $Apk $AuditReceipt 2>&1|Out-String
if($LASTEXITCODE -ne 0){throw ('Seletor falhou: '+$taskOutput)}
$taskWatch.Stop()
$taskResult=$taskOutput.Trim()|ConvertFrom-Json
if($taskResult.checks -ne 342 -or $taskResult.aliases -ne 78 -or $taskResult.selectedAliases -ne 25 -or $taskResult.blockedAliases -ne 53){throw 'Cobertura do seletor inesperada.'}
Set-Content -LiteralPath (Join-Path $OutputDir 'probe.log') -Value $taskOutput -Encoding utf8
$taskEvidence=[ordered]@{
    schemaVersion=1
    recordedUtc=[DateTime]::UtcNow.ToString('o')
    kind='actual-r126-engine-selection-isolated-jvm'
    checks=$taskResult.checks
    failures=0
    elapsedMs=$taskWatch.ElapsedMilliseconds
    aliases=$taskResult.aliases
    selectedAliases=$taskResult.selectedAliases
    blockedAliases=$taskResult.blockedAliases
    apkSha256=$taskApkSha
    auditReceiptSha256=(Get-TaskSha $AuditReceipt)
    roomsJarSha256=(Get-TaskSha $RoomsJar)
    clientJarSha256=(Get-TaskSha $ClientJar)
    androidApiJarSha256=(Get-TaskSha $AndroidJar)
    jsonJarSha256=(Get-TaskSha $JsonJar)
    assetSha256=$taskAudit.enginesAssetSha256
    sourceSha256=(Get-TaskSha $taskSources[0])
    fixtureSha256=@((Get-TaskSha $taskSources[1]),(Get-TaskSha $taskSources[2]))
    contextFixtureOnly=$true
    actualCompiledSelectionInvoked=$true
    nativeCoreExecuted=$false
    androidExecuted=$false
    serverAuthenticated=$false
    physicalGameplayValidated=$false
    apkChanged=$false
}
Set-Content -LiteralPath $Receipt -Value ($taskEvidence|ConvertTo-Json -Depth 8) -Encoding utf8
$taskOutput.Trim()
