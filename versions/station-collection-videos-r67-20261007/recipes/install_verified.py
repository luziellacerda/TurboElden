"""Update one authorized Android with no active emulation; preserve and verify package data identity."""
import argparse, datetime, hashlib, json, re, subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
a=p.parse_args()
w=Path(a.workspace).resolve()
assert w.drive.upper()=='E:'
receipt=json.loads((w/'evidence/package.json').read_text('utf8'))
apk=Path(receipt['apk'])
with apk.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==receipt['sha256']
adb=r'G:\Android\Sdk\platform-tools\adb.exe'
package='org.turboramastation.frontend'

def run(*args):
 r=subprocess.run([adb,*map(str,args)],capture_output=True,text=True,encoding='utf8',errors='replace')
 if r.returncode: raise RuntimeError('ADB operation failed: '+str(args[0]))
 return r.stdout

devices=[s for s in run('devices').splitlines()[1:] if s.strip()]
assert len(devices)==1 and devices[0].split()[1]=='device', 'Need one authorized phone'
activities=run('shell','dumpsys','activity','activities')
hist=[s for s in activities.splitlines() if re.search(r'\* Hist\s+#',s) and package+'/' in s]
allowed=['org.emulationstation.frontend.ESActivity','org.emulationstation.frontend.auth.LoginActivity','org.emulationstation.frontend.netplay.StationRoomsActivity']
assert all(any('/'+name+' ' in s for name in allowed) for s in hist), 'An emulator Activity is active; request human exit'

def identity():
 text=run('shell','dumpsys','package',package)
 uid=re.search(r'uid:(\d+)',run('shell','cmd','package','list','packages','-U',package)).group(1)
 first=re.search(r'firstInstallTime=([^\r\n]+)',text).group(1).strip()
 return uid,first

def installed_hash():
 path=run('shell','pm','path',package).strip().removeprefix('package:')
 assert path.endswith('/base.apk') and '\n' not in path
 return run('shell','sha256sum',path).split()[0]

before=identity()
base_hash=installed_hash()
assert base_hash==receipt['baseSHA256'], 'Installed base differs; inspect before updating'
model=run('shell','getprop','ro.product.model').strip()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
print('Installing verified APK; preserving existing data',flush=True)
result=run('install','--no-incremental','-r','--user','0',apk)
assert 'Success' in result, 'Android did not confirm installation'
after=identity()
actual=installed_hash()
assert actual==receipt['sha256'], 'Installed APK hash mismatch'
assert before==after, 'Package identity or original installation timestamp changed'
record=dict(startedUTC=start,completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 model=model,package=package,apkSHA256=receipt['sha256'],deviceAPK_SHA256=actual,
 previousAPK_SHA256=base_hash,apkBytes=receipt['bytes'],installSuccess=True,
 uidPreserved=True,originalInstallTimestampPreserved=True,uninstalled=False,dataCleared=False,
 deviceSettingsChanged=False,activeEmulatorBeforeInstall=False,launchVerified=False,
 securityHandshakeVerified=False,twoDeviceGameplayVerified=False,thermalSavingsMeasured=False)
(w/'evidence/installation.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
print(json.dumps(record,indent=2),flush=True)
run('shell','am','start','-n',package+'/org.emulationstation.frontend.auth.LoginActivity')
print('Official entry requested; check foreground and authentication separately.')
