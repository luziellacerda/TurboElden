param(
    [string]$Apk = 'E:\ESTUDO APK\TurboRetroEmu-funcoes.apk',
    [string]$BaseRoot = 'E:\ESTUDO APK\TurboRetroEmu-build'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = $PSScriptRoot
$report = Join-Path $root ('verification\' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$decoded = Join-Path $report 'decoded'
$tempDirectory = Join-Path $root 'temp'
$aapt = Join-Path $BaseRoot 'android-build-tools\35.0.0\android-15\aapt2.exe'
New-Item -ItemType Directory -Path $report -Force | Out-Null
$oldTemp=$env:TEMP; $oldTmp=$env:TMP
$env:TEMP=$tempDirectory; $env:TMP=$tempDirectory
try {
    & $aapt dump badging $Apk | Set-Content -LiteralPath (Join-Path $report 'badging.txt') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw 'AAPT não conseguiu ler o APK.' }
    & $aapt dump xmltree --file AndroidManifest.xml $Apk | Set-Content -LiteralPath (Join-Path $report 'manifest-binary.txt') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw 'Manifesto binário inválido.' }
    & java -Xmx2G "-Djava.io.tmpdir=$tempDirectory" -jar (Join-Path $BaseRoot 'tools\apktool_3.0.3.jar') d -j 4 -p (Join-Path $BaseRoot 'rebuild\framework') -o $decoded $Apk 2>&1 |
        Tee-Object -FilePath (Join-Path $report 'decode.log')
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao reabrir o APK final.' }
    [xml]$manifest = Get-Content -LiteralPath (Join-Path $decoded 'AndroidManifest.xml') -Raw
    $ns='http://schemas.android.com/apk/res/android'
    $app=$manifest.manifest.application
    $login=@($app.activity | Where-Object { $_.GetAttribute('name',$ns) -eq 'org.emulationstation.frontend.auth.LoginActivity' })
    $es=@($app.activity | Where-Object { $_.GetAttribute('name',$ns) -eq 'org.emulationstation.frontend.ESActivity' })
    if ($login.Count -ne 1 -or $es.Count -ne 1) { throw 'Activities esperadas ausentes/duplicadas.' }
    if ($login[0].GetAttribute('exported',$ns) -ne 'true' -or $es[0].GetAttribute('exported',$ns) -ne 'false') { throw 'Exposição incorreta de activities.' }
    if ($null -eq $login[0].SelectSingleNode('intent-filter') -or $null -ne $es[0].SelectSingleNode('intent-filter')) { throw 'Launcher incorreto.' }
    if ($app.GetAttribute('debuggable',$ns) -ne 'false') { throw 'APK final inesperadamente depurável.' }
    $sdl = [IO.File]::ReadAllText((Join-Path $decoded 'smali_classes4\org\libsdl\app\SDLActivity.smali'))
    $guard = [regex]::Match($sdl,'(?s)\.method public static handleNativeState\(\)V(.*?)\.end method').Value
    $resumed=$guard.IndexOf('->RESUMED:'); $auth=$guard.IndexOf('AuthSession;->isAuthorized()Z'); $thread=$guard.IndexOf('new-instance v0, Ljava/lang/Thread;')
    if ($resumed -lt 0 -or $auth -le $resumed -or $thread -le $auth) { throw 'Guarda SDL fora da posição esperada.' }
    if ($guard.Substring($auth,$thread-$auth) -notmatch '(?s)move-result v0\s+if-nez v0, :\w+\s+return-void') { throw 'Caminho não autenticado não termina antes de SDLThread.' }
    $esSmali=[IO.File]::ReadAllText((Join-Path $decoded 'smali_classes3\org\emulationstation\frontend\ESActivity.smali'))
    if ($esSmali -notmatch '(?s)\.method protected onResume\(\)V.*?LoginActivity;->ensureAuthorized\(Landroid/app/Activity;\)V.*?\.end method') { throw 'Guarda de restauração ausente.' }
    foreach ($name in @('RestartActivity','DownloadService')) {
        $smali=[IO.File]::ReadAllText((Join-Path $decoded "smali_classes3\org\emulationstation\frontend\$name.smali"))
        if ($smali -notmatch 'const-class v\d+, Lorg/emulationstation/frontend/auth/LoginActivity;') { throw "Entrada não encaminhada ao login: $name" }
    }
    $authFolder=Join-Path $decoded 'smali_classes6\org\emulationstation\frontend\auth'
    foreach ($name in @('AuthSession','LocalPassword','LoginActivity')) {
        if (-not (Test-Path -LiteralPath (Join-Path $authFolder "$name.smali"))) { throw "Classe de login ausente: $name" }
    }
    $authSmali=Get-ChildItem -LiteralPath $authFolder -Filter '*.smali' | Get-Content -Raw
    if (($authSmali -join "`n") -match 'Ljava/net/|Landroid/content/SharedPreferences;') { throw 'Login local não deve usar rede ou persistência de sessão.' }
    $loginSmali=[IO.File]::ReadAllText((Join-Path $authFolder 'LoginActivity.smali'))
    $back=[regex]::Match($loginSmali,'(?s)\.method public onBackPressed\(\)V(.*?)\.end method').Value
    if ($back -notmatch 'android.intent.category.HOME') { throw 'Correção de navegação Voltar ausente.' }

    $httpPath='smali_classes3\org\emulationstation\frontend\HttpBridge.smali'
    $http=[IO.File]::ReadAllText((Join-Path $decoded $httpPath))
    $post=[regex]::Match($http,'(?s)\.method public static startPost\(Ljava/lang/String;Ljava/lang/String;\)I.*?\.end method').Value
    if (-not $post -or $post -match 'ExecutorService|->execute|Ljava/net/|HttpBridge\$1;') { throw 'POST ainda pode iniciar rede.' }
    if ($post -notmatch '(?s)const/4 v2, 0x4\s+iput v2, v1, .*?->status:I' -or $post -notmatch '->REQUESTS:' -or $post -notmatch 'return v0') { throw 'POST não retorna falha local com ID normal.' }
    # Compare complete method bodies for ALL methods except the deliberately replaced POST.
    # Ignore whitespace only; do not ignore instructions, labels or literal values.
    $originalHttp=[IO.File]::ReadAllText((Join-Path (Join-Path $BaseRoot 'rebuild\source') $httpPath))
    $methodPattern='(?sm)^\.method [^\r\n]+\r?\n.*?^\.end method'
    $originalMethods=[regex]::Matches($originalHttp,$methodPattern)
    $newMethods=[regex]::Matches($http,$methodPattern)
    if ($originalMethods.Count -ne $newMethods.Count) { throw 'Número de métodos HTTP alterado.' }
    $preservedMethods=0
    foreach ($method in $originalMethods) {
        $header=($method.Value -split '\r?\n')[0]
        if ($header -match ' startPost\(') { continue }
        $found=@($newMethods | Where-Object { (($_.Value -split '\r?\n')[0]) -eq $header })
        if ($found.Count -ne 1) { throw "Método HTTP ausente: $header" }
        if ([regex]::Replace($method.Value,'\s+','') -ne [regex]::Replace($found[0].Value,'\s+','')) { throw "Método funcional HTTP alterado: $header" }
        $preservedMethods++
    }

    $originalNative=[IO.File]::ReadAllBytes((Join-Path $BaseRoot 'rebuild\source\lib\arm64-v8a\libmain.so'))
    $newNative=[IO.File]::ReadAllBytes((Join-Path $decoded 'lib\arm64-v8a\libmain.so'))
    if ($originalNative.Length -ne $newNative.Length) { throw 'Tamanho da biblioteca nativa alterado.' }
    $diffs=0
    for ($i=0; $i -lt $originalNative.Length; $i++) {
        if ($originalNative[$i] -ne $newNative[$i]) {
            $diffs++
            if (-not (($i -ge 0x160D4C -and $i -le 0x160D53) -or ($i -ge 0x1AA148 -and $i -le 0x1AA14B))) { throw "Byte nativo inesperado em $i" }
        }
    }
    # IP patch changes 3 of its 4 bytes (0x03 is unchanged); startup changes all 8.
    if ($diffs -ne 11 -or [BitConverter]::ToString($newNative,0x160D4C,8) -ne 'F5-03-1F-2A-24-00-00-14' -or [BitConverter]::ToString($newNative,0x1AA148,4) -ne 'C0-03-5F-D6') { throw 'Patch nativo incorreto.' }
    $originalManifest = Get-Content -LiteralPath (Join-Path $BaseRoot 'logs\verificacao-final\manifest-original.txt') -Raw
    $newManifest = Get-Content -LiteralPath (Join-Path $report 'manifest-binary.txt') -Raw
    foreach ($pattern in @('theme\(0x01010000\)=@0x7f[0-9a-f]+','icon\(0x01010002\)=@0x7f[0-9a-f]+','resource\(0x01010025\)=@0x7f[0-9a-f]+')) {
        $expected=[regex]::Match($originalManifest,$pattern).Value
        if (-not $expected -or -not $newManifest.Contains($expected)) { throw 'Referência a recurso original alterada no manifesto.' }
    }
    $result=[ordered]@{
        Apk=$Apk; SHA256=(Get-FileHash -LiteralPath $Apk).Hash;
        DecodePassed=$true; LauncherAndExportedChecked=$true; SDLResumeGuardChecked=$true;
        RestoreRestartAndNotificationGuardsChecked=$true; NoNetworkOrPersistentSessionInLogin=$true;
        PostNetworkDisabled=$true; UnchangedHttpMethods=$preservedMethods; TelemetryIpLookupDisabled=$true;
        NativeChangedBytes=$diffs; ResourceIdsPreserved=$true; RuntimeTested=$false; Reports=$report
    }
    $result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'verification-result.json') -Encoding utf8
    $result | ConvertTo-Json
} finally { $env:TEMP=$oldTemp; $env:TMP=$oldTmp }
