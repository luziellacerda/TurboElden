"""Install the visual update only if no emulator activity is running; preserve all data."""
from pathlib import Path
import datetime, hashlib, json, re, sys
P = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(P / 'emulator-audit'))
from device_audit import adb, shell
report_path = P / 'system-videos/build-result.json'
build = json.loads(report_path.read_text())
apk = Path(build['apk'])
assert hashlib.sha256(apk.read_bytes()).hexdigest() == build['sha256']
activities = shell('dumpsys', 'activity', 'activities')
if re.search(r'(?:\* Hist #|mResumedActivity|topResumedActivity)[^\n]*EmulationActivity', activities):
    raise SystemExit('GAME_ACTIVE: ask user to exit the emulation before installing.')
response = adb('install', '-r', str(apk)).decode('utf8', 'replace')
print(response)
if 'Success' not in response:
    raise SystemExit('Installation did not succeed; no success record written.')
remote = shell('pm', 'path', 'org.emulationstation.frontend').strip().splitlines()[0].removeprefix('package:')
actual = shell('sha256sum', remote).split()[0]
assert actual == build['sha256'], (actual, build['sha256'])
launch = shell('am', 'start', '-n', 'org.emulationstation.frontend/.auth.LoginActivity')
record = dict(time=datetime.datetime.now().isoformat(), apk=str(apk), sha256=actual,
    result=response.strip(), startup_command=launch.strip(), data_cleared=False,
    uninstalled=False, settings_changed=False, games_and_saves_preserved=True,
    visual_check_performed=False)
(P / 'system-videos/installed.json').write_text(json.dumps(record, indent=2), encoding='utf8')
build['installed'] = True
report_path.write_text(json.dumps(build, indent=2), encoding='utf8')
print(json.dumps(record, indent=2))

