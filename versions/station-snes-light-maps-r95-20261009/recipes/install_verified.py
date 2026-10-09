"""Install the exact R95 on an explicitly connected device without an active game.

Direct streaming update only. Never uninstall, clear data, copy an extra APK to
shared storage, change Android settings or start a game. Public receipts omit
device serials, package paths, account data and session tokens.
"""
import argparse, datetime, hashlib, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(r'E:\ESTUDO APK\work\station-snes-light-maps-r95-20261009')
ADB = r'G:\Android\Sdk\platform-tools\adb.exe'
PACKAGE = 'org.turboramastation.frontend'
EXPECTED = json.loads((ROOT / 'evidence/package.json').read_text('utf8'))['sha256']
PREVIOUS = ('1aacf46a1e98fc21642363cab959ef40931517bb303706e35af485680bd2486e',)
ALLOWED = {'org.emulationstation.frontend.ESActivity',
           'org.emulationstation.frontend.auth.LoginActivity',
           'org.emulationstation.frontend.netplay.StationRoomsActivity'}


def require(value, message):
    if not value: raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--device-label', choices=('motorola', 'samsung'), required=True)
    args = parser.parse_args()
    require(re.fullmatch(r'[A-Za-z0-9._:-]+', args.serial), 'Invalid explicit device serial')
    receipt = json.loads((ROOT / 'evidence/package.json').read_text('utf8'))
    active = json.loads((ROOT.parents[1] / 'release-channels/ACTIVE.json').read_text('utf8'))
    channel = active['channels']['test-4p']
    require(channel['version'] == 'R95' and channel['apkSHA256'] == EXPECTED, 'Exact canonical R95 channel required')
    apk = Path(active['backupRoot']) / channel['directory'] / channel['apk']
    with apk.open('rb') as source: digest = hashlib.file_digest(source, 'sha256').hexdigest()
    require(digest == receipt['sha256'] == EXPECTED and apk.stat().st_size == receipt['bytes'], 'Exact signed R95 required')
    evidence = WORK / 'installation'
    evidence.mkdir(parents=True, exist_ok=True)

    def run(*command):
        result = subprocess.run([ADB, '-s', args.serial, *map(str, command)], capture_output=True,
                                encoding='utf8', errors='replace')
        if result.returncode:
            (evidence / (args.device_label + '-failure-private.txt')).write_text(result.stdout + result.stderr, 'utf8')
            raise RuntimeError('Device command failed; inspect the private local failure record: ' + command[0])
        return result.stdout

    def identity():
        text = run('shell', 'dumpsys', 'package', PACKAGE)
        fields = {
            'uid': re.search(r'uid:(\d+)', run('shell', 'cmd', 'package', 'list', 'packages', '-U', PACKAGE)),
            'first': re.search(r'firstInstallTime=([^\r\n]+)', text),
            'data': re.search(r'dataDir=([^\r\n]+)', text)}
        require(all(fields.values()), 'Existing package identity is incomplete')
        return {key: value.group(1).strip() for key, value in fields.items()}

    def installed_hash():
        path = run('shell', 'pm', 'path', PACKAGE).strip().removeprefix('package:')
        require(path.startswith('/data/app/') and path.endswith('/base.apk') and '\n' not in path, 'Expected a single installed APK')
        value = run('shell', 'sha256sum', path).split()[0]
        require(re.fullmatch('[0-9a-f]{64}', value), 'Installed APK hash unavailable')
        return value

    def activity_preflight():
        services=run('shell','dumpsys','activity','services',PACKAGE)
        require('org.emulationstation.frontend.DownloadService' not in services,'A download is active; wait for completion before updating')
        activities = run('shell', 'dumpsys', 'activity', 'activities')
        names = []
        for line in activities.splitlines():
            if re.search(r'\* Hist\s+#', line) and PACKAGE + '/' in line:
                match = re.search(re.escape(PACKAGE) + r'/([^\s}]+)', line)
                require(match is not None, 'Unrecognized package Activity')
                names.append(match.group(1))
        require(all(name in ALLOWED for name in names), 'An emulator or another app panel is open; request human exit before updating')
        return sorted(set(names))

    require(run('get-state').strip() == 'device', 'Explicit device must be authorized and connected')
    before = identity()
    previous = installed_hash()
    require(previous in (*PREVIOUS, EXPECTED), 'Installed version differs from verified R87/R95; inspect before updating')
    model = run('shell', 'getprop', 'ro.product.model').strip()
    require(('motorola' in model.lower() if args.device_label == 'motorola' else model.startswith('SM-A56')), 'Device label/model mismatch')
    foreground = activity_preflight()
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    performed = previous != EXPECTED
    if performed:
        print('Installing R95 by direct streaming; preserving existing package data', flush=True)
        result = run('install', '--streaming', '--no-incremental', '-r', '--user', '0', apk)
        require('Success' in result, 'Android did not confirm installation: ' + result[-700:])
    after = identity()
    actual = installed_hash()
    require(actual == EXPECTED, 'Installed APK differs from signed R95')
    require(before == after, 'Package UID, original installation date or data directory changed')
    record = dict(version='R95', deviceLabel=args.device_label, model=model, package=PACKAGE,
        startedUTC=start, completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        previousAPK_SHA256=previous, apkSHA256=EXPECTED, deviceAPK_SHA256=actual, apkBytes=receipt['bytes'],
        installPerformed=performed, installSuccess=True, uidPreserved=True, originalInstallTimestampPreserved=True,
        dataDirectoryPreserved=True, uninstalled=False, dataCleared=False, deviceSettingsChanged=False,
        activeEmulatorBeforeInstall=False, preInstallAppActivities=foreground,
        directStreaming=True, extraAPKCopiedToPhone=False, officialEntryRequested=False,
        launchVerified=False, authenticatedEntryVerified=False, physicalDisplayVerified=False,
        serverRegistryActivationVerified=False, twoDeviceGameplayVerified=False,
        inheritedR77OnlineQualificationStillRequired=True, serverChanged=False,
        installCommand=['install','--streaming','--no-incremental','-r','--user','0'])
    name = 'installation-' + args.device_label + '-r95.json'
    destination = evidence / name
    destination.write_text(json.dumps(record, indent=2) + '\n', 'utf8')
    (ROOT / 'evidence' / name).write_bytes(destination.read_bytes())
    print(json.dumps(record, indent=2), flush=True)
    result = run('shell', 'am', 'start', '-n', PACKAGE + '/org.emulationstation.frontend.auth.LoginActivity')
    require('Error:' not in result and 'Exception' not in result, 'Official launch failed; installation receipt retained')
    record['officialEntryRequested'] = True
    destination.write_text(json.dumps(record, indent=2) + '\n', 'utf8')
    (ROOT / 'evidence' / name).write_bytes(destination.read_bytes())
    print('Official entry requested; authenticated opening requires separate observation.', flush=True)


if __name__ == '__main__': main()
