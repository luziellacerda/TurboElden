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
# No real executable, USB operation or installation is used by these fixtures.
$script:NativeState = 'alive'
$script:HasOnlineActivity = $true
$script:RemotePathState = 'normal'
$script:RemoteHashState = 'matched'
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
if ((Get-ForegroundPackage 'synthetic-two') -ne $TargetPackage) { throw 'Active app detection failed.' }
if ((Get-InstallFailureCode 'Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE: details]') -ne 'INSTALL_FAILED_UPDATE_INCOMPATIBLE') { throw 'Failure classification failed.' }
$script:HasOnlineActivity = $false
if ((Get-OnlineSessionState 'synthetic-two') -ne 'ACTIVE_NATIVE_PROCESS') { throw 'Background native session detection failed.' }
$script:NativeState = 'none'
$script:HasOnlineActivity = $true
if ((Get-OnlineSessionState 'synthetic-two') -ne 'ACTIVE_ONLINE_ACTIVITY') { throw 'Online activity detection failed.' }
$script:HasOnlineActivity = $false
if ((Get-OnlineSessionState 'synthetic-two') -ne 'NO_ONLINE_SESSION_DETECTED') { throw 'Finished session detection failed.' }
$script:NativeState = 'unsupported'
if ((Get-OnlineSessionState 'synthetic-two') -ne 'NATIVE_PROCESS_CHECK_UNAVAILABLE') { throw 'Conservative unknown process gate failed.' }
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
[pscustomobject]@{syntax='passed'; simulatedUsbAuthorized=2; unauthorizedAndOfflineRecognized=$true; networkAndEmulatorExcluded=$true; unconfirmedUsbExcluded=$true; windowsPresentUsbFallback=$true; adbSingleUsbFallback=$true; substringSerialDoesNotConfirmUsb=$true; activeAppOnSecondDisplayRecognized=$true; backgroundGameBlocked=$true; closedGameRecognized=$true; unknownProcessBlocked=$true; installedHashMatchMismatchAndUnavailableRecognized=$true; unsafeRemotePathBlocked=$true; unexpectedSplitApkDetected=$true; usbAccess=$false; installationPerformed=$false} | ConvertTo-Json
