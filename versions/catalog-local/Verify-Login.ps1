param(
    [string]$Apk = 'E:\ESTUDO APK\TurboRetroEmu-catalogo-local.apk',
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
function Canonical-Smali([string]$Code) {
    # Baksmali renumbers branch labels when a branch is added. Preserve the graph via
    # deterministic first-reference names, then compare every other instruction/directive.
    $labels=@{}
    foreach ($match in [regex]::Matches($Code,':[a-z][a-z0-9_]*')) {
        if (-not $labels.ContainsKey($match.Value)) { $labels[$match.Value]=':label_'+$labels.Count }
    }
    $normalized=[regex]::Replace($Code,':[a-z][a-z0-9_]*',{ param($match) $labels[$match.Value] })
    return ($normalized -replace '\s','')
}
try {
    & $aapt dump badging $Apk | Set-Content -LiteralPath (Join-Path $report 'badging.txt') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw 'AAPT não conseguiu ler o APK.' }
    $badging=Get-Content -LiteralPath (Join-Path $report 'badging.txt') -Raw
    if ($badging -notmatch "versionCode='5'" -or $badging -notmatch "versionName='1.0.2-catalogo-local'") { throw 'Versão de atualização incorreta.' }
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
    [xml]$baselineManifest=Get-Content -LiteralPath (Join-Path $BaseRoot 'rebuild\source\AndroidManifest.xml') -Raw
    foreach ($attribute in @('debuggable','label','theme','icon','requestLegacyExternalStorage')) {
        if ($app.GetAttribute($attribute,$ns) -ne $baselineManifest.manifest.application.GetAttribute($attribute,$ns)) { throw "Atributo original alterado: $attribute" }
    }
    $permissionNames=@($baselineManifest.manifest.'uses-permission' | ForEach-Object { $_.GetAttribute('name',$ns) } | Sort-Object)
    $newPermissionNames=@($manifest.manifest.'uses-permission' | ForEach-Object { $_.GetAttribute('name',$ns) } | Sort-Object)
    if (($permissionNames -join '|') -ne ($newPermissionNames -join '|')) { throw 'Permissões originais alteradas.' }
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

    $originalNative=[IO.File]::ReadAllBytes((Join-Path $BaseRoot 'rebuild\source\lib\arm64-v8a\libmain.so'))
    $newNative=[IO.File]::ReadAllBytes((Join-Path $decoded 'lib\arm64-v8a\libmain.so'))
    if ($originalNative.Length -ne $newNative.Length) { throw 'Tamanho da biblioteca nativa alterado.' }
    $diffs=0
    for ($i=0; $i -lt $originalNative.Length; $i++) {
        if ($originalNative[$i] -ne $newNative[$i]) {
            $diffs++
            if (-not (($i -ge 0x23B644 -and $i -le 0x23B647) -or ($i -ge 0x239790 -and $i -le 0x239793))) { throw "Byte nativo inesperado em $i" }
        }
    }
    if ($diffs -ne 8 -or [BitConverter]::ToString($newNative,0x23B644,4) -ne '1B-FD-FF-17' -or [BitConverter]::ToString($newNative,0x239790,4) -ne '1F-20-03-D5') { throw 'Patch nativo incorreto.' }
    # All other native bytes are identical, including startup, configuration IO and telemetry.
    foreach ($class in @('AssetInstaller')) {
        $relative="smali_classes3\org\emulationstation\frontend\$class.smali"
        $before=[IO.File]::ReadAllText((Join-Path (Join-Path $BaseRoot 'rebuild\source') $relative)) -replace '\s',''
        $after=[IO.File]::ReadAllText((Join-Path $decoded $relative)) -replace '\s',''
        if ($before -cne $after) { throw "Classe original alterada: $class" }
    }
    $httpRelative='smali_classes3\org\emulationstation\frontend\HttpBridge.smali'
    $oldHttp=[IO.File]::ReadAllText((Join-Path (Join-Path $BaseRoot 'rebuild\source') $httpRelative))
    $newHttp=[IO.File]::ReadAllText((Join-Path $decoded $httpRelative))
    $methodPattern='(?ms)^\.method (?<signature>[^\r\n]+)\r?\n.*?^\.end method'
    $newMethods=@{}
    foreach ($method in [regex]::Matches($newHttp,$methodPattern)) { $newMethods[$method.Groups['signature'].Value]=$method.Value }
    $originalMethodCount=0
    foreach ($method in [regex]::Matches($oldHttp,$methodPattern)) {
        $originalMethodCount++
        $signature=$method.Groups['signature'].Value
        if (-not $newMethods.ContainsKey($signature)) { throw "Método HTTP removido: $signature" }
        $after=$newMethods[$signature]
        if ($signature.StartsWith('private static execute(')) {
            $hookPattern='(?m)^[ \t]*invoke-static/range \{p0 \.\. p2\}, Lorg/emulationstation/frontend/HttpBridge;->tryLocalCatalog\(Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/HttpBridge\$Request;\)Z\s+move-result v0\s+if-eqz v0, (?<target>:\w+)\s+return-void\s+(?<debug>\.line 373\s+)?\k<target>\s*'
            if ([regex]::Matches($after,$hookPattern).Count -ne 1) { throw 'Interceptação do catálogo ausente ou inesperada.' }
            $hookPosition=[regex]::Match($after,$hookPattern).Index
            if ($hookPosition -gt $after.IndexOf('->normalizeUrl(')) { throw 'Catálogo interceptado depois da rede.' }
            $after=[regex]::Replace($after,$hookPattern,'${debug}')
        }
        if ((Canonical-Smali $method.Value) -cne (Canonical-Smali $after)) { throw "Corpo original HTTP alterado: $signature" }
    }
    if ($newMethods.Count -ne $originalMethodCount+1) { throw 'Métodos novos HTTP inesperados.' }
    $localHook=$newMethods['private static tryLocalCatalog(Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/HttpBridge$Request;)Z']
    if (-not $localHook -or $localHook -notmatch 'LocalCatalog;->read' -or $localHook -notmatch 'CatalogData;->matches' -or $localHook -match 'openConnection|startPost|startInternal') { throw 'Hook local inválido.' }
    $catalogAsset=Join-Path $decoded 'assets\turboretro\catalog.json'
    if ((Get-FileHash -LiteralPath $catalogAsset).Hash -ne '4C09C066C592ACD5481067FF2B9DF0409F01016BF93CD517E298655A899F7792') { throw 'Catálogo incorporado divergente.' }
    $catalogJson=[IO.File]::ReadAllText($catalogAsset)
    if ($catalogJson -match '(?i)WAYOS-[A-Z0-9]{5}') { throw 'Possível chave de acesso incorporada no catálogo.' }
    $catalogObjects=$catalogJson | ConvertFrom-Json -Depth 100
    if (@($catalogObjects).Count -ne 46 -or @($catalogObjects | ForEach-Object { $_.Files }).Count -ne 17911) { throw 'Itens do catálogo divergentes.' }
    $catalogFolder=Join-Path $decoded 'smali_classes6\org\emulationstation\frontend\catalog'
    $catalogCode=(Get-ChildItem -LiteralPath $catalogFolder -Filter '*.smali' | Get-Content -Raw) -join "`n"
    if ($catalogCode -match 'Ljava/net/(URL|HttpURLConnection|Socket);|openConnection|WAYOS-[A-Z0-9]{5}') { throw 'Rede ou credencial inesperada no módulo de catálogo.' }
    if ($catalogCode -notmatch 'Landroid/content/res/AssetManager;->open' -or $catalogCode -notmatch 'Ljava/security/MessageDigest;->isEqual') { throw 'Leitura/verificação de asset ausente.' }
    $workingVerification=Get-Content -LiteralPath 'E:\ESTUDO APK\TurboRetroEmu-somente-login\verification-result.json' -Raw | ConvertFrom-Json
    $workingDecoded=Join-Path $workingVerification.Reports 'decoded'
    foreach ($relative in @(
        'smali_classes3\org\emulationstation\frontend\ESActivity.smali',
        'smali_classes3\org\emulationstation\frontend\RestartActivity.smali',
        'smali_classes3\org\emulationstation\frontend\DownloadService.smali',
        'smali_classes4\org\libsdl\app\SDLActivity.smali'
    )) {
        $before=[IO.File]::ReadAllText((Join-Path $workingDecoded $relative)) -replace '\s',''
        $after=[IO.File]::ReadAllText((Join-Path $decoded $relative)) -replace '\s',''
        if ($before -cne $after) { throw "Fluxo da versão que abriu foi alterado: $relative" }
    }
    $workingNative=Join-Path $workingDecoded 'lib\arm64-v8a\libmain.so'
    if ((Get-FileHash -LiteralPath $workingNative).Hash -ne (Get-FileHash -LiteralPath (Join-Path $decoded 'lib\arm64-v8a\libmain.so')).Hash) { throw 'Biblioteca nativa diferente da versão que abriu.' }
    $baselineES=[IO.File]::ReadAllText((Join-Path $BaseRoot 'rebuild\source\smali_classes3\org\emulationstation\frontend\ESActivity.smali'))
    foreach ($method in @('getHomeDir','getStorageRoot','getArguments','hasStorageAccess','requestStorageAccess','installResources')) {
        $pattern='(?ms)^\.method [^\r\n]* '+$method+'\([^\r\n]*\r?\n.*?^\.end method'
        $before=[regex]::Match($baselineES,$pattern).Value -replace '\s',''
        $after=[regex]::Match($esSmali,$pattern).Value -replace '\s',''
        if (-not $before -or $before -cne $after) { throw "Rotina original alterada: $method" }
    }
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
        NativeChangedBytes=$diffs; ResourceIdsPreserved=$true; OriginalAppAttributesAndPermissions=$true;
        OriginalHttpMethodsPreserved=$originalMethodCount; OnlyCatalogGetIntercepted=$true;
        CatalogAssetHashChecked=$true; CatalogCategories=46; CatalogFiles=17911; CatalogCredentialPatternAbsent=$true;
        NativeAndActivityFlowIdenticalToWorkingVersion=$true;
        AssetInstallerPreserved=$true; StorageMethodsPreserved=$true;
        OriginalNativeStartupStoreAndTelemetryPreserved=$true; RuntimeTested=$false; Reports=$report
    }
    $result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'verification-result.json') -Encoding utf8
    $result | ConvertTo-Json
} finally { $env:TEMP=$oldTemp; $env:TMP=$oldTmp }
