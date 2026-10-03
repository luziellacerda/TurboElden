"""Read-only snapshots and saved-state inventory for the authorized HUD test."""
from pathlib import Path
import os, sys, json, subprocess, shlex, datetime

os.environ['ANDROID_USER_HOME'] = r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
ADB = [r'G:\Android\Sdk\platform-tools\adb.exe', '-s', 'RQCY30751WY']
OUT = Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
ROOT = '/storage/emulated/0/EmulationStation/roms/.station-v2'

def adb(*args):
    return subprocess.run([*ADB, *args], capture_output=True, check=True).stdout

label = sys.argv[1]
assert label and all(c.isalnum() or c in '-_' for c in label)
result = {'time': datetime.datetime.now().astimezone().isoformat(), 'label': label}
activity = adb('shell', 'dumpsys', 'activity', 'activities').decode(errors='replace')
result['activity'] = [line.strip() for line in activity.splitlines() if 'topResumedActivity' in line]
processes = adb('shell', 'ps', '-A').decode(errors='replace')
result['processes'] = [line.strip() for line in processes.splitlines() if 'org.turboramastation.frontend' in line]
image = OUT / (label + '.png')
image.write_bytes(adb('exec-out', 'screencap', '-p'))
result['screenshot'] = str(image)
if '--states' in sys.argv:
    paths = adb('shell', 'find', ROOT, '-maxdepth', '6', '-type', 'f').decode().splitlines()
    result['states'] = []
    for path in paths:
        if not path.endswith(('.frz', '.gp', '.srm')): continue
        command = 'sha256sum ' + shlex.quote(path)
        digest = adb('shell', command).decode().split()[0]
        command = "stat -c '%s|%Y' " + shlex.quote(path)
        size, modified = adb('shell', command).decode().strip().split('|')
        result['states'].append({'path': path, 'sha256': digest, 'bytes': int(size), 'mtime': int(modified)})
(OUT / (label + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
