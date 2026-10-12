# Windows PowerShell 5.1 ou PowerShell 7. Não requer execução como administrador.
# Seleção por manifesto explícito: nunca escolhe APK por data ou nome de revisão.
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ApkPath,
    [string]$ManifestPath,
    [string]$AdbPath,
    [switch]$ValidateOnly
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$TargetPackage = 'org.turboramastation.frontend'
$script:AdbExecutable = $null
$script:ApkReadLock = $null

function Resolve-ExistingFile {
    param([string]$Path, [string]$BaseDirectory, [string]$Description)
    if ([string]::IsNullOrWhiteSpace($Path)) { throw "$Description não informado." }
    $candidate = $Path
    if (-not [System.IO.Path]::IsPathRooted($candidate)) {
        $candidate = Join-Path -Path $BaseDirectory -ChildPath $candidate
    }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "$Description não encontrado. Verifique o caminho configurado."
    }
    return (Get-Item -LiteralPath $candidate).FullName
}

function Get-ManifestValue {
    param($Manifest, [string]$Name)
    $property = $Manifest.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Invoke-Adb {
    param([string[]]$Arguments)
    # Array de argumentos e operador &: nenhum dado vira comando de shell.
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $captured = @(& $script:AdbExecutable @Arguments 2>&1 | ForEach-Object { $_.ToString() })
        $nativeExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    return [pscustomobject]@{ ExitCode = $nativeExit; Output = ($captured -join "`n") }
}

function Find-Adb {
    param([string]$Override, [string]$ManifestAdb, [string]$ManifestDirectory)
    $candidates = New-Object 'System.Collections.Generic.List[string]'
    if (-not [string]::IsNullOrWhiteSpace($Override)) {
        return Resolve-ExistingFile $Override $PSScriptRoot 'ADB informado'
    }
    if (-not [string]::IsNullOrWhiteSpace($ManifestAdb)) {
        if ([System.IO.Path]::IsPathRooted($ManifestAdb)) { $candidates.Add($ManifestAdb) }
        else { $candidates.Add((Join-Path $ManifestDirectory $ManifestAdb)) }
    }
    $candidates.Add((Join-Path $PSScriptRoot 'platform-tools\adb.exe'))
    $candidates.Add((Join-Path $PSScriptRoot 'adb.exe'))
    foreach ($sdkDirectory in @($env:ANDROID_SDK_ROOT, $env:ANDROID_HOME)) {
        if (-not [string]::IsNullOrWhiteSpace($sdkDirectory)) {
            $candidates.Add((Join-Path $sdkDirectory 'platform-tools\adb.exe'))
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        $candidates.Add((Join-Path $env:LOCALAPPDATA 'Android\Sdk\platform-tools\adb.exe'))
    }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Get-Item -LiteralPath $candidate).FullName
        }
    }
    $fromPath = Get-Command -Name 'adb.exe' -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $fromPath) { return $fromPath.Source }
    throw 'ADB não encontrado. Coloque platform-tools ao lado do instalador ou configure adbPath no manifesto.'
}

function Get-WindowsPresentUsbSerials {
    # No Windows, get-devpath pode retornar "unknown". A lista PnP presente
    # confirma USB pelo identificador inteiro, nunca por trecho ou pelo modelo.
    $confirmedSerials = New-Object 'System.Collections.Generic.List[string]'
    try {
        $pnpDevices = @(Get-CimInstance -ClassName Win32_PnPEntity -Filter "PNPDeviceID LIKE 'USB%'" -ErrorAction Stop)
        foreach ($pnpDevice in $pnpDevices) {
            if ($pnpDevice.ConfigManagerErrorCode -ne 0 -or $pnpDevice.PNPDeviceID -notmatch '^USB\\') { continue }
            $serialToken = ($pnpDevice.PNPDeviceID -split '\\')[-1]
            if (-not [string]::IsNullOrWhiteSpace($serialToken)) { $confirmedSerials.Add($serialToken) }
        }
    } catch {
        # Falha PnP deixa somente as outras confirmações USB explícitas.
    }
    return @($confirmedSerials.ToArray())
}

function Get-UsbDevices {
    $listing = Invoke-Adb @('devices', '-l')
    if ($listing.ExitCode -ne 0) { throw 'Não foi possível consultar o ADB. Confira platform-tools e o cabo USB.' }
    $accepted = New-Object 'System.Collections.Generic.List[object]'
    $unauthorized = 0
    $offline = 0
    $excluded = 0
    $windowsFallbackLoaded = $false
    $singleUsbSerial = $null
    $windowsUsbSerials = @()
    foreach ($line in ($listing.Output -split '\r?\n')) {
        if ($line -notmatch '^\s*(?<serial>\S+)\s+(?<state>device|unauthorized|offline)\b(?<details>.*)$') { continue }
        $deviceSerial = $Matches['serial']
        $deviceState = $Matches['state']
        $details = $Matches['details']
        # TCP/IP, emuladores e serviços mDNS nunca são alvos deste instalador.
        if ($deviceSerial -match ':|^emulator-|\._adb') { $excluded++; continue }
        if ($deviceState -eq 'unauthorized') { $unauthorized++; continue }
        if ($deviceState -eq 'offline') { $offline++; continue }
        $usbConfirmed = $details -match '\busb:\S+'
        $usbVerificationMethod = 'usb-marker'
        if (-not $usbConfirmed) {
            $devPath = Invoke-Adb @('-s', $deviceSerial, 'get-devpath')
            $usbConfirmed = ($devPath.ExitCode -eq 0 -and $devPath.Output.Trim() -match '^usb:')
            if ($usbConfirmed) { $usbVerificationMethod = 'adb-get-devpath' }
        }
        if (-not $usbConfirmed) {
            if (-not $windowsFallbackLoaded) {
                $singleUsb = Invoke-Adb @('-d', 'get-serialno')
                if ($singleUsb.ExitCode -eq 0) { $singleUsbSerial = $singleUsb.Output.Trim() }
                $windowsUsbSerials = @(Get-WindowsPresentUsbSerials)
                $windowsFallbackLoaded = $true
            }
            if (-not [string]::IsNullOrWhiteSpace($singleUsbSerial) -and $singleUsbSerial -ceq $deviceSerial) {
                $usbConfirmed = $true
                $usbVerificationMethod = 'adb-single-usb'
            } elseif (@($windowsUsbSerials | Where-Object { $_ -ieq $deviceSerial }).Count -gt 0) {
                $usbConfirmed = $true
                $usbVerificationMethod = 'windows-present-usb'
            }
        }
        if (-not $usbConfirmed) { $excluded++; continue }
        $deviceModel = 'Android'
        if ($details -match '\bmodel:(?<model>[A-Za-z0-9_.-]+)') {
            $deviceModel = $Matches['model'] -replace '_', ' '
        }
        $accepted.Add([pscustomobject]@{
            Serial = $deviceSerial
            Model = $deviceModel
            Alias = ('Telefone {0}' -f ($accepted.Count + 1))
            UsbVerificationMethod = $usbVerificationMethod
        })
    }
    return [pscustomobject]@{
        Authorized = @($accepted.ToArray())
        UnauthorizedCount = $unauthorized
        OfflineCount = $offline
        ExcludedCount = $excluded
    }
}

function Get-ForegroundPackage {
    param([string]$DeviceSerial)
    $activities = Invoke-Adb @('-s', $DeviceSerial, 'shell', 'dumpsys', 'activity', 'activities')
    $foregroundPackages = New-Object 'System.Collections.Generic.List[string]'
    if ($activities.ExitCode -eq 0) {
        foreach ($line in ($activities.Output -split '\r?\n')) {
            if ($line -match '(mResumedActivity|topResumedActivity)' -and $line -match '\s(?<pkg>[A-Za-z][A-Za-z0-9_.]*)/') {
                $foregroundPackages.Add($Matches['pkg'])
            }
        }
    }
    # Um jogo em outra tela também impede a atualização.
    foreach ($foregroundPackage in $foregroundPackages) {
        if ($foregroundPackage -eq $TargetPackage -or $foregroundPackage.StartsWith($TargetPackage + '.')) {
            return $foregroundPackage
        }
    }
    if ($foregroundPackages.Count -gt 0) { return $foregroundPackages[0] }
    $window = Invoke-Adb @('-s', $DeviceSerial, 'shell', 'dumpsys', 'window', 'windows')
    if ($window.ExitCode -eq 0) {
        foreach ($line in ($window.Output -split '\r?\n')) {
            if ($line -match '(mCurrentFocus|mFocusedApp)' -and $line -match '\s(?<pkg>[A-Za-z][A-Za-z0-9_.]*)/') {
                return $Matches['pkg']
            }
        }
    }
    return $null
}

function Get-InstallFailureCode {
    param([string]$Output)
    if ($Output -match '\b(INSTALL_FAILED_[A-Z0-9_]+)\b') { return $Matches[1] }
    if ($Output -match '\bunauthorized\b') { return 'USB_UNAUTHORIZED' }
    if ($Output -match '\boffline\b') { return 'USB_OFFLINE' }
    if ($Output -match 'device.*not found|no devices|device disconnected') { return 'USB_DISCONNECTED' }
    return 'INSTALL_NOT_CONFIRMED'
}

function Get-OnlineSessionState {
    param([string]$DeviceSerial)
    # Home não encerra uma partida: o processo nativo pode continuar vivo.
    $nativeProcess = Invoke-Adb @('-s', $DeviceSerial, 'shell', 'pidof', ($TargetPackage + ':station_netplay'))
    $processOutput = $nativeProcess.Output.Trim()
    if ($nativeProcess.ExitCode -eq 0 -and $processOutput -match '^\d+(?:\s+\d+)*$') {
        return 'ACTIVE_NATIVE_PROCESS'
    }
    if (-not ($nativeProcess.ExitCode -eq 1 -and [string]::IsNullOrWhiteSpace($processOutput))) {
        return 'NATIVE_PROCESS_CHECK_UNAVAILABLE'
    }
    $activities = Invoke-Adb @('-s', $DeviceSerial, 'shell', 'dumpsys', 'activity', 'activities')
    if ($activities.ExitCode -ne 0) { return 'ONLINE_ACTIVITY_CHECK_UNAVAILABLE' }
    foreach ($line in ($activities.Output -split '\r?\n')) {
        # ActivityRecord/Hist identificam uma Activity existente, inclusive pausada.
        # Texto solto de intent/data não é usado para declarar uma partida ativa.
        if ($line -match '(ActivityRecord|\bHist\s*#)' -and
            $line -match 'org\.turboramastation\.frontend/[^\s}]*StationRetroActivity\b') {
            return 'ACTIVE_ONLINE_ACTIVITY'
        }
    }
    return 'NO_ONLINE_SESSION_DETECTED'
}

function Get-InstalledApkVerification {
    param([string]$DeviceSerial, [string]$ExpectedHash)
    $packagePaths = Invoke-Adb @('-s', $DeviceSerial, 'shell', 'pm', 'path', $TargetPackage)
    if ($packagePaths.ExitCode -ne 0) {
        return [pscustomobject]@{ State = 'unavailable'; Code = 'PACKAGE_PATH_UNAVAILABLE'; Hash = $null }
    }
    $apkPaths = @($packagePaths.Output -split '\r?\n' | Where-Object { $_ -match '^package:' })
    if ($apkPaths.Count -ne 1) {
        return [pscustomobject]@{ State = 'unavailable'; Code = 'SINGLE_BASE_APK_NOT_CONFIRMED'; Hash = $null }
    }
    $remoteApkPath = $apkPaths[0].Substring('package:'.Length).Trim()
    # adb shell junta argumentos; só aceitamos o caminho Android esperado e
    # caracteres sem metacaracteres de shell antes de chamar sha256sum.
    if ($remoteApkPath -notmatch '^/data/app/[A-Za-z0-9._~+=@/-]+/base\.apk$') {
        return [pscustomobject]@{ State = 'unavailable'; Code = 'PACKAGE_PATH_FORMAT_UNSUPPORTED'; Hash = $null }
    }
    $remoteHashResult = Invoke-Adb @('-s', $DeviceSerial, 'shell', 'sha256sum', $remoteApkPath)
    if ($remoteHashResult.ExitCode -ne 0) {
        $remoteHashResult = Invoke-Adb @('-s', $DeviceSerial, 'shell', 'toybox', 'sha256sum', $remoteApkPath)
    }
    $hashLinePattern = '(?m)^\s*(?<hash>[a-fA-F0-9]{64})\s+\*?' + [regex]::Escape($remoteApkPath) + '\s*$'
    if ($remoteHashResult.ExitCode -ne 0 -or $remoteHashResult.Output -notmatch $hashLinePattern) {
        return [pscustomobject]@{ State = 'unavailable'; Code = 'INSTALLED_HASH_UNAVAILABLE'; Hash = $null }
    }
    $remoteHash = $Matches['hash'].ToLowerInvariant()
    if ($remoteHash -ceq $ExpectedHash.ToLowerInvariant()) {
        return [pscustomobject]@{ State = 'matched'; Code = 'INSTALLED_HASH_MATCHED'; Hash = $remoteHash }
    }
    return [pscustomobject]@{ State = 'mismatch'; Code = 'INSTALLED_HASH_MISMATCH'; Hash = $remoteHash }
}

function Write-Receipt {
    param($Receipt)
    $receiptDirectory = Join-Path $PSScriptRoot 'recibos-usb'
    if (-not (Test-Path -LiteralPath $receiptDirectory -PathType Container)) {
        New-Item -ItemType Directory -Path $receiptDirectory -Force | Out-Null
    }
    $receiptName = 'instalacao-{0}-{1}.json' -f ([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')), ([Guid]::NewGuid().ToString('N').Substring(0, 8))
    $receiptPath = Join-Path $receiptDirectory $receiptName
    $Receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
    Write-Host ('Recibo: recibos-usb\{0}' -f $receiptName)
}

try {
    if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
        $ManifestPath = Join-Path $PSScriptRoot 'turbostations-apk-teste.json'
    }
    $resolvedManifest = Resolve-ExistingFile $ManifestPath $PSScriptRoot 'Manifesto'
    $manifestDirectory = Split-Path -Parent $resolvedManifest
    $manifest = Get-Content -LiteralPath $resolvedManifest -Raw -Encoding UTF8 | ConvertFrom-Json
    if ((Get-ManifestValue $manifest 'schemaVersion') -ne 1) { throw 'Versão de manifesto não suportada.' }
    if ((Get-ManifestValue $manifest 'package') -cne $TargetPackage) { throw 'O manifesto não identifica o pacote oficial do TurboStations.' }
    $expectedHash = [string](Get-ManifestValue $manifest 'sha256')
    if ($expectedHash -notmatch '^[a-fA-F0-9]{64}$') { throw 'O manifesto precisa conter um SHA256 completo válido.' }
    $revision = [string](Get-ManifestValue $manifest 'revision')
    if ($revision -notmatch '^R[0-9]+(?:[A-Za-z0-9._-]*)$') { throw 'Revisão inválida no manifesto.' }
    if ([string]::IsNullOrWhiteSpace($ApkPath)) {
        $ApkPath = [string](Get-ManifestValue $manifest 'apkPath')
        $resolvedApk = Resolve-ExistingFile $ApkPath $manifestDirectory 'APK'
    } else {
        $resolvedApk = Resolve-ExistingFile $ApkPath (Get-Location).Path 'APK informado'
    }
    if ([System.IO.Path]::GetExtension($resolvedApk) -ine '.apk') { throw 'O arquivo escolhido precisa ter extensão .apk.' }
    Write-Host ('Conferindo o APK {0}. Aguarde; o arquivo é grande.' -f $revision)
    # Mantém o APK disponível para leitura pelo ADB, mas impede alteração/troca
    # do arquivo entre a verificação do SHA256 e o fim das instalações.
    $script:ApkReadLock = [System.IO.File]::Open($resolvedApk, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    $actualHash = (Get-FileHash -InputStream $script:ApkReadLock -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -cne $expectedHash.ToLowerInvariant()) {
        throw 'O SHA256 do APK não corresponde ao manifesto. Não será instalado. Para uma nova compilação, atualize o manifesto com a identidade conferida dessa versão.'
    }
    if ($ValidateOnly) {
        [pscustomobject]@{
            validation = 'passed'
            revision = $revision
            package = $TargetPackage
            sha256Verified = $true
            deviceAccess = $false
            installationPerformed = $false
        } | ConvertTo-Json
        exit 0
    }
    Write-Host ''
    Write-Host ('TurboStations {0} — instalação para testes por USB' -f $revision)
    $warningText = [string](Get-ManifestValue $manifest 'warning')
    if (-not [string]::IsNullOrWhiteSpace($warningText)) { Write-Host $warningText -ForegroundColor Yellow }
    Write-Host 'A atualização usa install -r: preserva os dados e exige assinatura compatível.'
    Write-Host 'O instalador não fecha o jogo, não apaga dados e não abre o aplicativo.'
    $script:AdbExecutable = Find-Adb $AdbPath ([string](Get-ManifestValue $manifest 'adbPath')) $manifestDirectory
    $discovery = Get-UsbDevices
    if ($discovery.UnauthorizedCount -gt 0) {
        Write-Host ('{0} aparelho(s) sem autorização: desbloqueie a tela e aceite a depuração USB.' -f $discovery.UnauthorizedCount) -ForegroundColor Yellow
    }
    if ($discovery.OfflineCount -gt 0) {
        Write-Host ('{0} aparelho(s) offline: reconecte o cabo e confira a depuração USB.' -f $discovery.OfflineCount) -ForegroundColor Yellow
    }
    if ($discovery.ExcludedCount -gt 0) {
        Write-Host 'Foram ignorados transportes de rede, emuladores ou aparelhos cujo USB não pôde ser confirmado.'
    }
    $devices = @($discovery.Authorized)
    if ($devices.Count -eq 0) { throw 'Nenhum telefone USB autorizado encontrado. Conecte, desbloqueie e autorize a depuração; depois execute o BAT novamente.' }
    Write-Host ''
    for ($deviceIndex = 0; $deviceIndex -lt $devices.Count; $deviceIndex++) {
        Write-Host ('{0}. {1} — {2} (USB)' -f ($deviceIndex + 1), $devices[$deviceIndex].Alias, $devices[$deviceIndex].Model)
    }
    if ($devices.Count -gt 1) { Write-Host 'T. Todos os telefones listados' }
    Write-Host '0. Cancelar'
    $selection = (Read-Host 'Escolha o número do telefone ou T para todos').Trim()
    if ($selection -eq '0' -or [string]::IsNullOrWhiteSpace($selection)) { Write-Host 'Instalação cancelada.'; exit 0 }
    $selectedDevices = @()
    if ($selection -ieq 'T' -and $devices.Count -gt 1) {
        $selectedDevices = $devices
    } else {
        $selectedNumber = 0
        if (-not [int]::TryParse($selection, [ref]$selectedNumber) -or $selectedNumber -lt 1 -or $selectedNumber -gt $devices.Count) {
            throw 'Escolha inválida. Execute novamente e selecione um dos números listados.'
        }
        $selectedDevices = @($devices[$selectedNumber - 1])
    }
    $failedCount = 0
    foreach ($device in $selectedDevices) {
        $receipt = [ordered]@{
            schemaVersion = 1
            revision = $revision
            package = $TargetPackage
            apkSha256 = $actualHash
            deviceAlias = $device.Alias
            deviceModel = $device.Model
            transport = 'USB'
            usbVerificationMethod = $device.UsbVerificationMethod
            startedUtc = [DateTime]::UtcNow.ToString('o')
            installAttempted = $false
            installSuccess = $false
            resultCode = 'NOT_STARTED'
            installExitCode = $null
            nativeSessionCheck = 'NOT_CHECKED'
            downloadsCompletedConfirmedByUser = $false
            installedHashVerified = $false
            installedApkSha256 = $null
            installedHashVerificationCode = 'NOT_CHECKED'
            dataPreservationRequested = $true
            forceStopped = $false
            uninstalledOrClearedData = $false
            downgradeRequested = $false
            appLaunched = $false
            containsSerialOrPersonalData = $false
        }
        try {
            Write-Host ''
            Write-Host ('Preparar {0} — {1}' -f $device.Alias, $device.Model)
            $answer = (Read-Host 'Saia da partida, conclua downloads e volte à tela inicial do Android. Enter para conferir ou 0 para pular').Trim()
            if ($answer -eq '0') { $receipt.resultCode = 'SKIPPED_BY_USER'; $failedCount++; continue }
            $receipt.downloadsCompletedConfirmedByUser = $true
            $foreground = Get-ForegroundPackage $device.Serial
            if ([string]::IsNullOrWhiteSpace($foreground)) {
                $receipt.resultCode = 'FOREGROUND_NOT_VERIFIED'
                Write-Host 'Não foi possível conferir a tela em uso. Desbloqueie o aparelho e tente novamente.' -ForegroundColor Yellow
                $failedCount++
                continue
            }
            if ($foreground -eq $TargetPackage -or $foreground.StartsWith($TargetPackage + '.')) {
                $receipt.resultCode = 'APP_STILL_IN_FOREGROUND'
                Write-Host 'TurboStations ainda está aberto na tela. Saia da partida e volte à tela inicial do Android antes de repetir.' -ForegroundColor Yellow
                $failedCount++
                continue
            }
            # Reconfere autorização e transporte imediatamente antes da operação.
            $recheck = Get-UsbDevices
            $sameUsbDevice = @($recheck.Authorized | Where-Object { $_.Serial -ceq $device.Serial })
            if ($sameUsbDevice.Count -ne 1) {
                $receipt.resultCode = 'USB_NO_LONGER_AUTHORIZED'
                Write-Host 'O telefone perdeu a conexão USB autorizada. Reconecte e tente novamente.' -ForegroundColor Yellow
                $failedCount++
                continue
            }
            $onlineSession = Get-OnlineSessionState $device.Serial
            $receipt.nativeSessionCheck = $onlineSession
            if ($onlineSession -ne 'NO_ONLINE_SESSION_DETECTED') {
                $receipt.resultCode = 'ONLINE_SESSION_NOT_CLOSED'
                if ($onlineSession -eq 'ACTIVE_NATIVE_PROCESS' -or $onlineSession -eq 'ACTIVE_ONLINE_ACTIVITY') {
                    Write-Host 'A partida ainda está aberta, mesmo que você tenha tocado em Home. Volte ao jogo e use Sair da partida.' -ForegroundColor Yellow
                    Write-Host 'Se já saiu, aguarde alguns segundos e execute o BAT novamente; o jogo pode estar concluindo o encerramento.'
                } else {
                    Write-Host 'Não foi possível conferir se a partida terminou. Confira a conexão e execute novamente após sair do jogo.' -ForegroundColor Yellow
                }
                $failedCount++
                continue
            }
            Write-Host ('Instalando {0} em {1}. Mantenha o cabo conectado; pode levar vários minutos.' -f $revision, $device.Alias)
            $receipt.installAttempted = $true
            $installation = Invoke-Adb @('-s', $device.Serial, 'install', '-r', $resolvedApk)
            $receipt.installExitCode = $installation.ExitCode
            if ($installation.ExitCode -eq 0 -and $installation.Output -match '(?m)^\s*Success\s*$') {
                $receipt.installSuccess = $true
                $receipt.resultCode = 'SUCCESS'
                Write-Host ('{0}: atualização instalada. Conferindo o APK no telefone; aguarde.' -f $device.Alias)
                $installedVerification = Get-InstalledApkVerification $device.Serial $actualHash
                $receipt.installedHashVerificationCode = $installedVerification.Code
                $receipt.installedApkSha256 = $installedVerification.Hash
                if ($installedVerification.State -eq 'matched') {
                    $receipt.installedHashVerified = $true
                    Write-Host ('{0}: instalação e SHA256 conferidos. Abra o TurboStations quando quiser testar.' -f $device.Alias) -ForegroundColor Green
                } elseif ($installedVerification.State -eq 'mismatch') {
                    $receipt.resultCode = 'SUCCESS_HASH_MISMATCH'
                    $failedCount++
                    Write-Host ('{0}: o APK instalado não corresponde ao arquivo esperado. Consulte o recibo antes de testar.' -f $device.Alias) -ForegroundColor Red
                } else {
                    $receipt.resultCode = 'SUCCESS_HASH_UNVERIFIED'
                    $failedCount++
                    Write-Host ('{0}: o Android confirmou a instalação, mas não foi possível conferir o SHA256 no telefone. O recibo registra essa limitação.' -f $device.Alias) -ForegroundColor Yellow
                }
            } else {
                $receipt.resultCode = Get-InstallFailureCode $installation.Output
                $failedCount++
                Write-Host ('{0}: instalação não concluída ({1}).' -f $device.Alias, $receipt.resultCode) -ForegroundColor Yellow
                if ($receipt.resultCode -eq 'INSTALL_FAILED_UPDATE_INCOMPATIBLE') {
                    Write-Host 'A assinatura é incompatível. Preserve os dados; é necessário corrigir o APK com a assinatura original.'
                } elseif ($receipt.resultCode -eq 'INSTALL_FAILED_VERSION_DOWNGRADE') {
                    Write-Host 'O aparelho tem versão superior. O instalador não força o retorno a uma versão anterior.'
                } elseif ($receipt.resultCode -eq 'INSTALL_FAILED_INSUFFICIENT_STORAGE') {
                    Write-Host 'O aparelho não tem espaço suficiente para concluir a atualização.'
                }
            }
        } catch {
            $receipt.resultCode = 'LOCAL_OPERATION_FAILED'
            $failedCount++
            Write-Host ('{0}: não foi possível concluir a operação. Confira cabo, autorização e arquivos.' -f $device.Alias) -ForegroundColor Yellow
        } finally {
            $receipt.completedUtc = [DateTime]::UtcNow.ToString('o')
            Write-Receipt $receipt
        }
    }
    if ($failedCount -gt 0) { exit 1 }
    exit 0
} catch {
    Write-Host ''
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    if ($null -ne $script:ApkReadLock) { $script:ApkReadLock.Dispose() }
}
