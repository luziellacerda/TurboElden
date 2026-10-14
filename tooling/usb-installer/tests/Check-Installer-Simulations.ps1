param([Parameter(Mandatory=$true)][string]$InstallerPath)
$ErrorActionPreference = 'Stop'
$TargetPackage = 'org.turboramastation.frontend'
$testTokens = $null
$testErrors = $null
$sourceAst = [System.Management.Automation.Language.Parser]::ParseFile($InstallerPath, [ref]$testTokens, [ref]$testErrors)
if ($testErrors.Count -gt 0) { throw 'Syntax check failed.' }
foreach ($definition in $sourceAst.FindAll({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst]}, $false)) {
    . ([scriptblock]::Create($definition.Extent.Text))
}
if ((Quote-NativeArgument 'C:\Program Files\Turbo Stations.apk') -cne '"C:\Program Files\Turbo Stations.apk"') { throw 'Windows path quoting failed.' }
if ((Quote-NativeArgument 'a"b') -cne '"a\"b"') { throw 'Windows quote escaping failed.' }
if ((Quote-NativeArgument 'C:\A B\') -cne '"C:\A B\\"') { throw 'Windows trailing slash escaping failed.' }
# No real executable, USB operation or installation is used by these fixtures.
$script:NativeState = 'alive'
$script:HasOnlineActivity = $true
$script:RemotePathState = 'normal'
$script:RemoteHashState = 'matched'
$script:AppServiceState = 'none'
$script:AppHistoryState = 'normal'
$script:HashCommands = 0
$script:FallbackSingleSerial = $null
$script:FixtureWindowsSerials = @()
function Get-WindowsPresentUsbSerials { return @($script:FixtureWindowsSerials) }
function Invoke-Adb {
    param([string[]]$Arguments)
    if ($Arguments[0] -eq 'devices') {
        return [pscustomobject]@{ ExitCode=0; Output=@'
List of devices attached
synthetic-one device usb:1-1 model:Android_One transport_id:1
synthetic-two device model:Android_Two transport_id:2
synthetic-unauthorized unauthorized
synthetic-offline offline
192.0.2.1:5555 device model:Network
emulator-5554 device model:Emulator
synthetic-unknown device model:Unknown
'@ }
    }
    if ($Arguments[0] -eq '-d' -and $Arguments[1] -eq 'get-serialno') {
        if ($null -ne $script:FallbackSingleSerial) { return [pscustomobject]@{ExitCode=0; Output=$script:FallbackSingleSerial} }
        return [pscustomobject]@{ExitCode=1; Output='more than one USB device'}
    }
    if ($Arguments[2] -eq 'get-devpath') {
        if ($Arguments[1] -eq 'synthetic-two') { return [pscustomobject]@{ExitCode=0; Output='usb:2-2'} }
        return [pscustomobject]@{ExitCode=0; Output='unknown'}
    }
    if ($Arguments -contains 'pidof') {
        if ($script:NativeState -eq 'alive') { return [pscustomobject]@{ExitCode=0; Output='1234'} }
        if ($script:NativeState -eq 'none') { return [pscustomobject]@{ExitCode=1; Output=''} }
        return [pscustomobject]@{ExitCode=127; Output='pidof unavailable'}
    }
    if ($Arguments -contains 'services') {
        if ($script:AppServiceState -eq 'unavailable') { return [pscustomobject]@{ExitCode=1; Output='error'} }
        if ($script:AppServiceState -eq 'active') { return [pscustomobject]@{ExitCode=0; Output='ServiceRecord{example org.turboramastation.frontend/.DownloadService}'} }
        return [pscustomobject]@{ExitCode=0; Output='ACTIVITY MANAGER SERVICES (dumpsys activity services)`n  (nothing)'}
    }
    if ($Arguments -contains 'activities' -and $script:AppHistoryState -ne 'normal') {
        $idle = '    * Hist  #0: ActivityRecord{one u0 org.turboramastation.frontend/org.emulationstation.frontend.ESActivity t1}'
        $launcher = '    * Hist  #0: ActivityRecord{two u0 com.android.launcher/.Main t2}'
        $gallery = '    * Hist  #1: ActivityRecord{three u0 org.turboramastation.frontend/paulscode.android.mupen64plusae.GalleryActivity t1}'
        $game = '    * Hist  #1: ActivityRecord{four u0 org.turboramastation.frontend/.StationRetroActivity t1}'
        $prefix = 'topResumedActivity: ActivityRecord{one u0 org.turboramastation.frontend/org.emulationstation.frontend.ESActivity t1}'
        if ($script:AppHistoryState -eq 'idle') { $rows = @($prefix, $idle, $launcher) }
        elseif ($script:AppHistoryState -eq 'offline-game') { $rows = @($prefix, $idle, $gallery, $launcher) }
        elseif ($script:AppHistoryState -eq 'online-game') { $rows = @($prefix, $idle, $game, $launcher) }
        elseif ($script:AppHistoryState -eq 'two-resumed') { $rows = @($prefix, 'mResumedActivity: ActivityRecord{three u0 org.turboramastation.frontend/paulscode.android.mupen64plusae.GalleryActivity t1}', $idle, $gallery) }
        elseif ($script:AppHistoryState -eq 'other-app') { $rows = @($launcher) }
        else { $rows = @('unrecognized activity output') }
        return [pscustomobject]@{ExitCode=0; Output=($rows -join "`n")}
    }
    if ($Arguments -contains 'activity') {
        if (-not $script:HasOnlineActivity) {
            return [pscustomobject]@{ExitCode=0; Output='mResumedActivity: ActivityRecord{one u0 com.android.launcher/.Main t1}'}
        }
        return [pscustomobject]@{ExitCode=0; Output=@'
    mResumedActivity: ActivityRecord{one u0 com.android.launcher/.Main t1}
    topResumedActivity: ActivityRecord{two u0 org.turboramastation.frontend/.StationRetroActivity t2}
'@ }
    }
    if ($Arguments -contains 'pm') {
        if ($script:RemotePathState -eq 'unsafe') { return [pscustomobject]@{ExitCode=0; Output='package:/data/app/unsafe/base.apk;echo PRIVATE'} }
        if ($script:RemotePathState -eq 'split') {
            return [pscustomobject]@{ExitCode=0; Output="package:/data/app/~~example/pkg-example/base.apk`npackage:/data/app/~~example/pkg-example/split.apk"}
        }
        return [pscustomobject]@{ExitCode=0; Output='package:/data/app/~~example/pkg-example/base.apk'}
    }
    if ($Arguments -contains 'sha256sum') {
        $script:HashCommands++
        if ($script:RemoteHashState -eq 'unavailable') { return [pscustomobject]@{ExitCode=1; Output='permission denied'} }
        if ($script:RemoteHashState -eq 'mismatch') { $fixtureHash = 'b' * 64 }
        else { $fixtureHash = 'a' * 64 }
        return [pscustomobject]@{ExitCode=0; Output=($fixtureHash + '  /data/app/~~example/pkg-example/base.apk')}
    }
    throw 'Unexpected fixture request.'
}
$discovery = Get-UsbDevices
if ($discovery.Authorized.Count -ne 2) { throw 'USB selection failed.' }
if ($discovery.UnauthorizedCount -ne 1 -or $discovery.OfflineCount -ne 1 -or $discovery.ExcludedCount -ne 3) { throw 'Transport classification failed.' }
$script:FixtureWindowsSerials = @('synthetic-unknown')
$windowsDiscovery = Get-UsbDevices
if ($windowsDiscovery.Authorized.Count -ne 3 -or @($windowsDiscovery.Authorized | Where-Object { $_.UsbVerificationMethod -eq 'windows-present-usb' }).Count -ne 1) { throw 'Windows present USB fallback failed.' }
$script:FixtureWindowsSerials = @('synthetic-unknown-extra')
if ((Get-UsbDevices).Authorized.Count -ne 2) { throw 'Windows substring must not confirm USB.' }
$script:FixtureWindowsSerials = @()
$script:FallbackSingleSerial = 'synthetic-unknown'
$singleUsbDiscovery = Get-UsbDevices
if ($singleUsbDiscovery.Authorized.Count -ne 3 -or @($singleUsbDiscovery.Authorized | Where-Object { $_.UsbVerificationMethod -eq 'adb-single-usb' }).Count -ne 1) { throw 'ADB single USB fallback failed.' }
$script:FallbackSingleSerial = $null
if ((Get-ForegroundComponent 'synthetic-two') -ne ($TargetPackage + '/.StationRetroActivity')) { throw 'Active game component detection failed.' }
if (-not (Test-IdleFrontendComponent ($TargetPackage + '/org.emulationstation.frontend.ESActivity'))) { throw 'Idle frontend was blocked.' }
if (-not (Test-IdleFrontendComponent ($TargetPackage + '/org.emulationstation.frontend.auth.LoginActivity'))) { throw 'Idle login was blocked.' }
if (Test-IdleFrontendComponent ($TargetPackage + '/.StationRetroActivity')) { throw 'Active game was marked idle.' }
$script:AppHistoryState = 'idle'
if ((Get-ForegroundComponent 'synthetic-two') -ne ($TargetPackage + '/org.emulationstation.frontend.ESActivity')) { throw 'Idle frontend component not recognized.' }
if ((Get-IdleAppActivityState 'synthetic-two') -ne 'IDLE_APP_ACTIVITIES_ONLY') { throw 'Idle frontend history was blocked.' }
$script:AppHistoryState = 'offline-game'
if ((Get-IdleAppActivityState 'synthetic-two') -ne 'ACTIVE_OR_UNKNOWN_APP_ACTIVITY') { throw 'Paused offline emulator was allowed.' }
$script:AppHistoryState = 'online-game'
if ((Get-IdleAppActivityState 'synthetic-two') -ne 'ACTIVE_OR_UNKNOWN_APP_ACTIVITY') { throw 'Paused online game was allowed.' }
$script:AppHistoryState = 'two-resumed'
if ((Get-ForegroundComponent 'synthetic-two') -ne ($TargetPackage + '/paulscode.android.mupen64plusae.GalleryActivity')) { throw 'Game on second display lost priority.' }
$script:AppHistoryState = 'other-app'
if ((Get-IdleAppActivityState 'synthetic-two') -ne 'NO_APP_ACTIVITY_DETECTED') { throw 'Other app history classification failed.' }
$script:AppHistoryState = 'unknown'
if ((Get-IdleAppActivityState 'synthetic-two') -ne 'APP_ACTIVITY_CHECK_UNAVAILABLE') { throw 'Unknown activity layout did not block.' }
$script:AppHistoryState = 'normal'
if ((Get-InstallFailureCode 'Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE: details]') -ne 'INSTALL_FAILED_UPDATE_INCOMPATIBLE') { throw 'Failure classification failed.' }
if ((Get-InstallFailureCode 'ADB_TIMEOUT: no reply') -ne 'INSTALL_STATUS_UNKNOWN_TIMEOUT') { throw 'Uncertain timeout classification failed.' }
$script:HasOnlineActivity = $false
if ((Get-OnlineSessionState 'synthetic-two') -ne 'ACTIVE_NATIVE_PROCESS') { throw 'Background native session detection failed.' }
$script:NativeState = 'none'
$script:HasOnlineActivity = $true
if ((Get-OnlineSessionState 'synthetic-two') -ne 'ACTIVE_ONLINE_ACTIVITY') { throw 'Online activity detection failed.' }
$script:HasOnlineActivity = $false
if ((Get-OnlineSessionState 'synthetic-two') -ne 'NO_ONLINE_SESSION_DETECTED') { throw 'Finished session detection failed.' }
$script:NativeState = 'unsupported'
if ((Get-OnlineSessionState 'synthetic-two') -ne 'NATIVE_PROCESS_CHECK_UNAVAILABLE') { throw 'Conservative unknown process gate failed.' }
if ((Get-AppServiceState 'synthetic-two') -ne 'NO_APP_SERVICE_DETECTED') { throw 'Idle service detection failed.' }
$script:AppServiceState = 'active'
if ((Get-AppServiceState 'synthetic-two') -ne 'APP_SERVICE_ACTIVE') { throw 'Background download service detection failed.' }
$script:AppServiceState = 'unavailable'
if ((Get-AppServiceState 'synthetic-two') -ne 'APP_SERVICES_CHECK_UNAVAILABLE') { throw 'Unknown service state gate failed.' }
$script:AppServiceState = 'none'
$matching = Get-InstalledApkVerification 'synthetic-two' ('a' * 64)
if ($matching.State -ne 'matched') { throw 'Installed SHA match failed.' }
$script:RemoteHashState = 'mismatch'
if ((Get-InstalledApkVerification 'synthetic-two' ('a' * 64)).State -ne 'mismatch') { throw 'Installed SHA mismatch detection failed.' }
$script:RemoteHashState = 'unavailable'
if ((Get-InstalledApkVerification 'synthetic-two' ('a' * 64)).State -ne 'unavailable') { throw 'Unavailable installed SHA detection failed.' }
$beforeUnsafePath = $script:HashCommands
$script:RemotePathState = 'unsafe'
if ((Get-InstalledApkVerification 'synthetic-two' ('a' * 64)).Code -ne 'PACKAGE_PATH_FORMAT_UNSUPPORTED') { throw 'Unsafe remote path gate failed.' }
if ($script:HashCommands -ne $beforeUnsafePath) { throw 'Unsafe path reached hash command.' }
$script:RemotePathState = 'split'
if ((Get-InstalledApkVerification 'synthetic-two' ('a' * 64)).Code -ne 'SINGLE_BASE_APK_NOT_CONFIRMED') { throw 'Split APK gate failed.' }
[pscustomobject]@{syntax='passed'; simulatedUsbAuthorized=2; unauthorizedAndOfflineRecognized=$true; networkAndEmulatorExcluded=$true; windowsPresentUsbFallback=$true; adbSingleUsbFallback=$true; substringSerialDoesNotConfirmUsb=$true; idleFrontendAllowed=$true; idleLoginAllowed=$true; activeGameComponentBlocked=$true; pausedOfflineGameBlocked=$true; gameOnSecondDisplayBlocked=$true; unknownActivityStateBlocked=$true; backgroundGameBlocked=$true; closedGameRecognized=$true; unknownProcessBlocked=$true; backgroundServiceBlocked=$true; unknownServiceStateBlocked=$true; installedHashMatchMismatchAndUnavailableRecognized=$true; unsafeRemotePathBlocked=$true; unexpectedSplitApkDetected=$true; usbAccess=$false; installationPerformed=$false} | ConvertTo-Json
