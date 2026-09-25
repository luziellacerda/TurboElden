param(
    [string]$BaseRoot = 'E:\ESTUDO APK\TurboRetroEmu-build',
    [string]$OriginalApk = 'E:\ESTUDO APK\TurboramaStation-24-09.apk',
    [string]$AndroidJar = 'G:\Android\Sdk\platforms\android-34\android.jar',
    [string]$OutputApk = 'E:\ESTUDO APK\TurboRetroEmu-funcoes.apk',
    [string]$Keystore = 'C:\Users\Admin\.android\debug.keystore'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Add-Type -AssemblyName System.IO.Compression.FileSystem
$variantRoot = $PSScriptRoot
if ([IO.Path]::GetPathRoot($variantRoot) -ne 'E:\') { throw 'Execute esta variante a partir de E:.' }
if (Test-Path -LiteralPath $OutputApk) { throw 'APK de destino já existe. Escolha outro -OutputApk.' }
$originalHash = '9DC39817F23975F15E9FB75BBE98E7A7519567E06805F5746C1F475CBCF57396'
if ((Get-FileHash -LiteralPath $OriginalApk).Hash -ne $originalHash) { throw 'APK base inesperado.' }
$run = Join-Path $variantRoot ('runs\' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$source = Join-Path $run 'source'
$tempDirectory = Join-Path $variantRoot 'temp'
$classes = Join-Path $run 'classes'
$testClasses = Join-Path $run 'test-classes'
$dex = Join-Path $run 'dex'
$androidTools = Join-Path $BaseRoot 'android-build-tools\35.0.0\android-15'
$apktool = Join-Path $BaseRoot 'tools\apktool_3.0.3.jar'
$framework = Join-Path $BaseRoot 'rebuild\framework'
$utf8 = [Text.UTF8Encoding]::new($false)
foreach ($directory in @($run,$source,$tempDirectory,$classes,$testClasses,$dex)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}
$previousTemp = $env:TEMP
$previousTmp = $env:TMP
$env:TEMP = $tempDirectory
$env:TMP = $tempDirectory

function Replace-ExactlyOnce([string]$Path, [string]$Old, [string]$New) {
    $content = [IO.File]::ReadAllText($Path).Replace("`r`n", "`n")
    $matches = [regex]::Matches($content, [regex]::Escape($Old)).Count
    if ($matches -ne 1) { throw "Esperava uma ocorrência; encontrei $matches em $Path" }
    [IO.File]::WriteAllText($Path, $content.Replace($Old, $New), $utf8)
}

function Zip-Methods([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $reader = [IO.BinaryReader]::new($stream)
    try {
        $tailSize = [int][math]::Min(65557, $stream.Length)
        $stream.Position = $stream.Length - $tailSize
        $tail = $reader.ReadBytes($tailSize)
        $eocd = -1
        for ($i = $tail.Length - 22; $i -ge 0; $i--) {
            if ([BitConverter]::ToUInt32($tail,$i) -eq 0x06054b50) { $eocd=$i; break }
        }
        if ($eocd -lt 0) { throw 'ZIP sem diretório central.' }
        $count = [BitConverter]::ToUInt16($tail,$eocd+10)
        $stream.Position = [BitConverter]::ToUInt32($tail,$eocd+16)
        $methods = @{}
        for ($i=0; $i -lt $count; $i++) {
            $header = $reader.ReadBytes(46)
            if ([BitConverter]::ToUInt32($header,0) -ne 0x02014b50) { throw 'ZIP inválido.' }
            $nameLength = [BitConverter]::ToUInt16($header,28)
            $extraLength = [BitConverter]::ToUInt16($header,30)
            $commentLength = [BitConverter]::ToUInt16($header,32)
            $name = [Text.Encoding]::UTF8.GetString($reader.ReadBytes($nameLength))
            $methods[$name] = [BitConverter]::ToUInt16($header,10)
            [void]$stream.Seek($extraLength+$commentLength, [IO.SeekOrigin]::Current)
        }
        return $methods
    } finally { $reader.Dispose(); $stream.Dispose() }
}

function Hash-Entry($Entry) {
    $stream = $Entry.Open()
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','') }
    finally { $sha.Dispose(); $stream.Dispose() }
}

try {
    # Work on an isolated copy. Baseline APK, baseline decoded source and user data stay intact.
    Get-ChildItem -LiteralPath (Join-Path $BaseRoot 'rebuild\source') -Force |
        Where-Object Name -notin @('build','dist') |
        Copy-Item -Destination $source -Recurse

    $manifestPath = Join-Path $source 'AndroidManifest.xml'
    [xml]$manifest = Get-Content -LiteralPath $manifestPath -Raw
    $ns = 'http://schemas.android.com/apk/res/android'
    $application = $manifest.manifest.application
    $entry = @($application.activity | Where-Object { $_.GetAttribute('name',$ns) -eq 'org.emulationstation.frontend.ESActivity' })
    if ($entry.Count -ne 1) { throw 'Activity principal não identificada.' }
    $entry = $entry[0]
    $entry.SetAttribute('exported',$ns,'false') | Out-Null
    $application.SetAttribute('label',$ns,'TurboRetro') | Out-Null
    $application.SetAttribute('debuggable',$ns,'false') | Out-Null
    $login = $manifest.CreateElement('activity')
    $attributes = @{
        name='org.emulationstation.frontend.auth.LoginActivity'; exported='true';
        launchMode='singleTask'; taskAffinity='org.emulationstation.frontend.login';
        screenOrientation='sensorLandscape'; windowSoftInputMode='adjustResize|stateAlwaysHidden';
        theme='@android:style/Theme.Material.NoActionBar';
        configChanges='keyboard|keyboardHidden|navigation|orientation|screenLayout|uiMode|screenSize|smallestScreenSize|density'
    }
    foreach ($attribute in $attributes.GetEnumerator()) {
        $login.SetAttribute($attribute.Key,$ns,$attribute.Value) | Out-Null
    }
    $intentFilter = $entry.SelectSingleNode('intent-filter')
    if ($null -eq $intentFilter) { throw 'Launcher original não encontrado.' }
    [void]$entry.RemoveChild($intentFilter)
    [void]$login.AppendChild($intentFilter)
    [void]$application.PrependChild($login)
    $manifest.Save($manifestPath)
    Replace-ExactlyOnce (Join-Path $source 'apktool.yml') '  versionCode: 1' '  versionCode: 3'
    Replace-ExactlyOnce (Join-Path $source 'apktool.yml') '  versionName: 1.0' '  versionName: 1.0-funcoes'

    $es = Join-Path $source 'smali_classes3\org\emulationstation\frontend\ESActivity.smali'
    $resumeMethod = @'
.method protected onResume()V
    .locals 0
    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onResume()V
    invoke-static {p0}, Lorg/emulationstation/frontend/auth/LoginActivity;->ensureAuthorized(Landroid/app/Activity;)V
    return-void
.end method

'@
    if ([IO.File]::ReadAllText($es) -match '\.method .* onResume\(\)V') { throw 'ESActivity já possui onResume; revisar integração.' }
    Replace-ExactlyOnce $es '.method protected onDestroy()V' ($resumeMethod + "`n.method protected onDestroy()V")
    $sdl = Join-Path $source 'smali_classes4\org\libsdl\app\SDLActivity.smali'
    # Block only RESUMED. Keep INIT and PAUSED lifecycle transitions functional.
    $old = @'
    .line 708
    sget-object v0, Lorg/libsdl/app/SDLActivity;->mSurface:Lorg/libsdl/app/SDLSurface;
'@
    $new = @'
    invoke-static {}, Lorg/emulationstation/frontend/auth/AuthSession;->isAuthorized()Z
    move-result v0
    if-nez v0, :turbo_local_authorized
    return-void
    :turbo_local_authorized
    .line 708
    sget-object v0, Lorg/libsdl/app/SDLActivity;->mSurface:Lorg/libsdl/app/SDLSurface;
'@
    Replace-ExactlyOnce $sdl $old $new
    foreach ($class in @('RestartActivity','DownloadService')) {
        $path = Join-Path $source "smali_classes3\org\emulationstation\frontend\$class.smali"
        $register = if ($class -eq 'RestartActivity') { 'v3' } else { 'v1' }
        Replace-ExactlyOnce $path "const-class $register, Lorg/emulationstation/frontend/ESActivity;" "const-class $register, Lorg/emulationstation/frontend/auth/LoginActivity;"
    }

    # In this EXACT original version, the only two native startPost callers are
    # LicenseService.send and TelemetryService.update. Functional requests use GET.
    # Return a real local failure, preserving request ID/poll/error/release lifecycle.
    # No worker, socket, POST body or success response is produced.
    $httpPath = Join-Path $source 'smali_classes3\org\emulationstation\frontend\HttpBridge.smali'
    $httpSource = [IO.File]::ReadAllText($httpPath)
    $postPattern = '(?s)\.method public static startPost\(Ljava/lang/String;Ljava/lang/String;\)I.*?\.end method'
    $postMethods = [regex]::Matches($httpSource,$postPattern)
    if ($postMethods.Count -ne 1) { throw 'POST original não identificado de forma única.' }
    $disabledPost = @'
.method public static startPost(Ljava/lang/String;Ljava/lang/String;)I
    .locals 4
    .param p0, "url"    # Ljava/lang/String;
    .param p1, "formBody"    # Ljava/lang/String;
    sget-object v0, Lorg/emulationstation/frontend/HttpBridge;->NEXT_ID:Ljava/util/concurrent/atomic/AtomicInteger;
    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicInteger;->getAndIncrement()I
    move-result v0
    new-instance v1, Lorg/emulationstation/frontend/HttpBridge$Request;
    const/4 v2, 0x0
    invoke-direct {v1, v2}, Lorg/emulationstation/frontend/HttpBridge$Request;-><init>(Lorg/emulationstation/frontend/HttpBridge-IA;)V
    const-string v2, "Servico fora desta versao local: licenciamento e telemetria desativados"
    iput-object v2, v1, Lorg/emulationstation/frontend/HttpBridge$Request;->error:Ljava/lang/String;
    const/4 v2, 0x4
    iput v2, v1, Lorg/emulationstation/frontend/HttpBridge$Request;->status:I
    sget-object v2, Lorg/emulationstation/frontend/HttpBridge;->REQUESTS:Ljava/util/concurrent/ConcurrentHashMap;
    invoke-static {v0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v3
    invoke-virtual {v2, v3, v1}, Ljava/util/concurrent/ConcurrentHashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    return v0
.end method
'@
    Replace-ExactlyOnce $httpPath ($postMethods[0].Value.Replace("`r`n","`n")) $disabledPost

    # Exact, version-bound startup change. Do not change LicenseService or fake server replies.
    # Skip the entire GuiLicense allocation/closure/push/cleanup block, not just its constructor.
    # Preserve w21=0 at the join point; the event loop immediately initializes w19 and w20.
    $nativePath = Join-Path $source 'lib\arm64-v8a\libmain.so'
    if ((Get-FileHash -LiteralPath $nativePath).Hash -ne 'D29ECD5A819563ECEBC76FEEEDD705F064A6D89B96AABAD033644461BB460273') {
        throw 'libmain.so inesperada. Recusando aplicar patch em outra versão.'
    }
    $native = [IO.File]::ReadAllBytes($nativePath)
    if ([BitConverter]::ToString($native,0x160D4C,8) -ne 'E8-12-00-D0-08-6D-42-F9') { throw 'Instruções originais divergentes.' }
    $blockHash = [Security.Cryptography.SHA256]::Create()
    try { $blockDigest = [BitConverter]::ToString($blockHash.ComputeHash($native,0x160D4C,0x94)).Replace('-','') }
    finally { $blockHash.Dispose() }
    if ($blockDigest -ne '77DA98BF4C5FBF6180486A6E0DA1BC207ED197732C9D1F25BD31F6C9F945C6B6') { throw 'Bloco startup divergente.' }
    # PT_LOAD file offset = VA here: p_offset=0, p_vaddr=0, p_filesz=0x3A62C0.
    # 0x160D4C: mov w21,wzr; 0x160D50: b 0x160DE0 (imm26 = 0x24).
    [byte[]]$patch = 0xF5,0x03,0x1F,0x2A,0x24,0x00,0x00,0x14
    [Array]::Copy($patch,0,$native,0x160D4C,8)
    # TelemetryService::startIpLookup is void. Return before stack allocation, so
    # neither the default IP service nor a configured TelemetryIpUrl is contacted.
    if ([BitConverter]::ToString($native,0x1AA148,16) -ne 'FF-03-02-D1-FD-7B-04-A9-F8-5F-05-A9-F6-57-06-A9') { throw 'Prologo IP lookup inesperado.' }
    [byte[]]$noIpLookup = 0xC0,0x03,0x5F,0xD6
    [Array]::Copy($noIpLookup,0,$native,0x1AA148,4)
    [IO.File]::WriteAllBytes($nativePath,$native)

    $javaFiles = @(Get-ChildItem -LiteralPath (Join-Path $variantRoot 'java') -Recurse -Filter '*.java' | Select-Object -ExpandProperty FullName)
    & javac "-J-Djava.io.tmpdir=$tempDirectory" -encoding UTF-8 --release 8 -classpath $AndroidJar -d $classes @javaFiles
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar login Java.' }
    $tests = @(Get-ChildItem -LiteralPath (Join-Path $variantRoot 'tests') -Recurse -Filter '*.java' | Select-Object -ExpandProperty FullName)
    & javac "-J-Djava.io.tmpdir=$tempDirectory" -encoding UTF-8 --release 8 -classpath $classes -d $testClasses @tests
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar testes.' }
    & java "-Djava.io.tmpdir=$tempDirectory" -cp "$classes;$testClasses" org.emulationstation.frontend.auth.AuthSessionTest |
        Tee-Object -FilePath (Join-Path $run 'auth-tests.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Testes locais de autenticação falharam.' }
    $jar = Join-Path $run 'login.jar'
    & jar "-J-Djava.io.tmpdir=$tempDirectory" cf $jar -C $classes .
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao empacotar classes.' }
    & java "-Djava.io.tmpdir=$tempDirectory" -cp (Join-Path $androidTools 'lib\d8.jar') com.android.tools.r8.D8 --release --min-api 26 --lib $AndroidJar --output $dex $jar
    if ($LASTEXITCODE -ne 0) { throw 'D8 falhou.' }
    if (@(Get-ChildItem -LiteralPath $dex -Filter '*.dex').Count -ne 1) { throw 'DEX do login inesperado.' }

    $rebuiltPath = Join-Path $run 'rebuilt.apk'
    & java -Xmx2G "-Djava.io.tmpdir=$tempDirectory" -jar $apktool b -f -j 4 -p $framework -o $rebuiltPath $source 2>&1 |
        Tee-Object -FilePath (Join-Path $run 'apktool-build.log')
    if ($LASTEXITCODE -ne 0) { throw 'Recompilação Apktool falhou.' }

    # Preserve ALL original entries except manifest, classes3/4 and the scoped native startup.
    # Original resource table, resource paths, assets, other DEX and seven native libs stay exact.
    $changedNames = @('AndroidManifest.xml','classes3.dex','classes4.dex','lib/arm64-v8a/libmain.so')
    $methods = Zip-Methods $OriginalApk
    $unsigned = Join-Path $run 'unsigned-preserved.apk'
    $original = [IO.Compression.ZipFile]::OpenRead($OriginalApk)
    $rebuilt = [IO.Compression.ZipFile]::OpenRead($rebuiltPath)
    $output = [IO.Compression.ZipFile]::Open($unsigned,[IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($entry in $original.Entries) {
            if ($entry.FullName -match '^META-INF/([^/]+\.(RSA|DSA|EC|SF)|MANIFEST\.MF)$') { continue }
            $from = $entry
            if ($entry.FullName -in $changedNames) {
                $from = $rebuilt.GetEntry($entry.FullName)
                if ($null -eq $from) { throw "Falta entrada recompilada: $($entry.FullName)" }
            }
            $level = switch ($methods[$entry.FullName]) {
                0 { [IO.Compression.CompressionLevel]::NoCompression }
                8 { [IO.Compression.CompressionLevel]::Optimal }
                default { throw 'Compressão inesperada.' }
            }
            $newEntry = $output.CreateEntry($entry.FullName,$level)
            $newEntry.LastWriteTime = $entry.LastWriteTime
            $inputStream=$from.Open(); $outputStream=$newEntry.Open()
            try { $inputStream.CopyTo($outputStream) }
            finally { $inputStream.Dispose(); $outputStream.Dispose() }
        }
        [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($output,(Join-Path $dex 'classes.dex'),'classes6.dex',[IO.Compression.CompressionLevel]::Optimal)
    } finally { $output.Dispose(); $rebuilt.Dispose(); $original.Dispose() }

    $aligned = Join-Path $run 'aligned.apk'
    & (Join-Path $androidTools 'zipalign.exe') -P 16 4 $unsigned $aligned
    if ($LASTEXITCODE -ne 0) { throw 'Alinhamento falhou.' }
    & java "-Djava.io.tmpdir=$tempDirectory" -jar (Join-Path $androidTools 'lib\apksigner.jar') sign --ks $Keystore --ks-key-alias androiddebugkey --ks-pass pass:android --key-pass pass:android --min-sdk-version 26 --v1-signing-enabled false --v2-signing-enabled true --v3-signing-enabled false --v4-signing-enabled false --out $OutputApk $aligned
    if ($LASTEXITCODE -ne 0) { throw 'Assinatura falhou.' }
    & java "-Djava.io.tmpdir=$tempDirectory" -jar (Join-Path $androidTools 'lib\apksigner.jar') verify --verbose --print-certs $OutputApk 2>&1 |
        Tee-Object -FilePath (Join-Path $run 'signature-verification.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Verificação de assinatura falhou.' }
    & (Join-Path $androidTools 'zipalign.exe') -c -P 16 4 $OutputApk
    if ($LASTEXITCODE -ne 0) { throw 'Verificação do alinhamento falhou.' }

    $original = [IO.Compression.ZipFile]::OpenRead($OriginalApk)
    $result = [IO.Compression.ZipFile]::OpenRead($OutputApk)
    try {
        $comparison = @(foreach ($entry in $original.Entries) {
            if ($entry.FullName -match '^META-INF/([^/]+\.(RSA|DSA|EC|SF)|MANIFEST\.MF)$') { continue }
            $actual = $result.GetEntry($entry.FullName)
            if ($null -eq $actual) { throw "Entrada removida: $($entry.FullName)" }
            $before=Hash-Entry $entry; $after=Hash-Entry $actual
            if (($before -ne $after) -and ($entry.FullName -notin $changedNames)) { throw "Alteração não autorizada: $($entry.FullName)" }
            [pscustomobject]@{Name=$entry.FullName;OriginalSha256=$before;LocalSha256=$after;Changed=($before -ne $after)}
        })
        $added = @($result.Entries | Where-Object { $null -eq $original.GetEntry($_.FullName) })
        if ($added.Count -ne 1 -or $added[0].FullName -ne 'classes6.dex') { throw 'Entradas novas inesperadas.' }
        if (@($comparison | Where-Object Changed).Count -ne 4) { throw 'Diferenças do APK inesperadas.' }
        $comparison | Export-Csv -LiteralPath (Join-Path $run 'component-comparison.csv') -NoTypeInformation -Encoding utf8
        $summary = [ordered]@{
            Output=$OutputApk; SHA256=(Get-FileHash -LiteralPath $OutputApk).Hash;
            OriginalEntries=$original.Entries.Count; LocalEntries=$result.Entries.Count;
            ByteIdentical=@($comparison | Where-Object { -not $_.Changed }).Count;
            Changed=$changedNames; Added='classes6.dex';
            AssetsIdentical=@($comparison | Where-Object { $_.Name -like 'assets/*' -and -not $_.Changed }).Count;
            NativeIdentical=@($comparison | Where-Object { $_.Name -like 'lib/*' -and -not $_.Changed }).Count;
            NativePatch=@('0x160D4C..0x160D53: mov w21,wzr; b 0x160DE0','0x1AA148..0x1AA14B: ret (telemetry IP lookup disabled)');
            LocalPassword='turbo123'; ServerLoginImplemented=$false;
            OldLicenseAndTelemetryPostEnabled=$false; TelemetryPublicIpLookupEnabled=$false;
            FunctionalGetAndDownloadCodeUnchanged=$true; CatalogAuthorizationBypassed=$false;
            DeviceRuntimeTested=$false; RunDirectory=$run
        }
        $summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $variantRoot 'build-result.json') -Encoding utf8
        $summary | ConvertTo-Json -Depth 5
    } finally { $result.Dispose(); $original.Dispose() }
} finally { $env:TEMP=$previousTemp; $env:TMP=$previousTmp }
