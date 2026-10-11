"""Explicit, direct R121 update; preserve package data and verify the full installed APK.

Run only for a user-authorized USB target already on the carousel, with no game
or download active. The receipt contains no device serial, UID or session data.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'org.turboramastation.frontend'
EXPECTED = 'eadb83cc2b797eed7d6c3cbdcae09fae7fdfbff0004c3b9db791aaadf68113b0'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('adb', 'apk', 'receipt'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--device-label', required=True)
    args = parser.parse_args()
    with args.apk.open('rb') as f:
        assert hashlib.file_digest(f, 'sha256').hexdigest() == EXPECTED, 'Unexpected APK'

    def adb(*command, timeout=60):
        result = subprocess.run([str(args.adb), '-s', args.serial, *command],
                                capture_output=True, timeout=timeout)
        if result.returncode:
            raise RuntimeError('ADB operation failed; installation is not confirmed')
        return result.stdout.decode('utf-8', 'replace')

    def package_state():
        value = adb('shell', 'dumpsys', 'package', PACKAGE)
        out = {}
        for key in ('firstInstallTime', 'lastUpdateTime', 'dataDir'):
            match = re.search(r'^\s*'+key+r'=(.+)$', value, re.M)
            assert match, 'Missing installed package field: '+key
            out[key] = match.group(1).strip()
        uid = adb('shell', 'cmd', 'package', 'list', 'packages', '-U', PACKAGE)
        match = re.search(r'package:'+re.escape(PACKAGE)+r'\s+uid:(\d+)', uid)
        assert match, 'Missing original package UID'
        out['uid'] = match.group(1)
        return out

    activities = adb('shell', 'dumpsys', 'activity', 'activities')
    resumed = re.findall(r'(?:mResumedActivity|topResumedActivity|ResumedActivity)\s*[:=][^\n]+', activities)
    assert any(PACKAGE+'/org.emulationstation.frontend.ESActivity' in row for row in resumed), \
        'Leave the authorized phone on the carousel before updating'
    before = package_state()
    result = adb('install', '--streaming', '-r', str(args.apk), timeout=300)
    assert re.search(r'^Success\s*$', result, re.M), 'Installer did not confirm success'
    after = package_state()
    for key in ('firstInstallTime', 'uid', 'dataDir'):
        assert after[key] == before[key], 'Package identity/data preservation check failed'
    paths = adb('shell', 'pm', 'path', PACKAGE).strip().splitlines()
    assert len(paths) == 1 and paths[0].startswith('package:/data/app/'), 'Unexpected installed APK layout'
    installed = paths[0][len('package:'):]
    assert re.fullmatch(r'[A-Za-z0-9/_+=.~-]+', installed), 'Unexpected package path'
    digest = adb('shell', 'sha256sum', installed, timeout=180).split()[0]
    assert digest == EXPECTED, 'Installed full APK hash does not match R121'
    record = {'version': 'R121', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'deviceModel': args.device_label, 'apkSHA256': EXPECTED, 'apkBytes': args.apk.stat().st_size,
              'installed': True, 'installedAPKHashMatchesPackage': True,
              'dataPreserved': True, 'originalUIDPreserved': True,
              'firstInstallTime': after['firstInstallTime'], 'updateTime': after['lastUpdateTime'],
              'directStreamingUpdate': True, 'extraAPKCopyOnPhone': False, 'uninstalledOrClearedData': False,
              'launchRequested': False, 'physicalVisualValidation': False,
              'thermalValidation': False, 'gameplayValidation': False,
              'containsDeviceSerialOrPersonalSessionData': False}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
