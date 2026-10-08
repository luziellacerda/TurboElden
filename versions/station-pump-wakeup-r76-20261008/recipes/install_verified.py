"""Update one authorized Android with no active emulation; preserve and verify package data identity."""
import argparse, datetime, hashlib, json, re, subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
p.add_argument('--serial', required=True, help='Explicit authorized device; permits two connected phones')
p.add_argument('--receipt-name', required=True, choices=['samsung','motorola'])
p.add_argument('--expected-installed-sha256', help='Explicitly verified installed version on another authorized phone')
a=p.parse_args()
w=Path(a.workspace).resolve()
assert w.drive.upper()=='E:'
receipt=json.loads((w/'evidence/package.json').read_text('utf8'))
apk=Path(receipt['apk'])
with apk.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==receipt['sha256']
adb=r'G:\Android\Sdk\platform-tools\adb.exe'
package='org.turboramastation.frontend'
target=None

def run(*args):
 r=subprocess.run([adb,*(['-s',target] if target else []),*map(str,args)],capture_output=True,text=True,encoding='utf8',errors='replace')
 if r.returncode:
  error=(r.stdout+'\n'+r.stderr).strip()
  (w/'evidence/adb-last-failure.txt').write_text(error,'utf8')
  raise RuntimeError('ADB operation failed: '+str(args[0])+': '+error[-1500:])
 return r.stdout

devices=[s for s in run('devices').splitlines()[1:] if s.strip()]
matches=[s.split() for s in devices if s.split()[0]==a.serial]
assert len(matches)==1 and matches[0][1]=='device', 'Explicit target must be connected and authorized'
target=a.serial # Never follow another phone after a cable swap.
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
expected_base=a.expected_installed_sha256 or receipt['baseSHA256']
assert re.fullmatch('[0-9a-f]{64}',expected_base)
assert base_hash==expected_base, 'Installed base differs; inspect before updating'
model=run('shell','getprop','ro.product.model').strip()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
print('Installing verified APK; preserving existing data',flush=True)
result=run('install','--streaming','--no-incremental','-r','--user','0',apk)
assert 'Success' in result, 'Android did not confirm installation'
after=identity()
actual=installed_hash()
assert actual==receipt['sha256'], 'Installed APK hash mismatch'
assert before==after, 'Package identity or original installation timestamp changed'
record=dict(version='R76',serverRegistryActivationVerified=True,startedUTC=start,completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 model=model,package=package,apkSHA256=receipt['sha256'],deviceAPK_SHA256=actual,
 previousAPK_SHA256=base_hash,apkBytes=receipt['bytes'],installSuccess=True,
 uidPreserved=True,originalInstallTimestampPreserved=True,uninstalled=False,dataCleared=False,
 deviceSettingsChanged=False,activeEmulatorBeforeInstall=False,launchVerified=False,
 directStreaming=True,extraAPKCopiedToPhone=False,
 installCommand=['install','--streaming','--no-incremental','-r','--user','0'],
 securityHandshakeVerified=False,twoDeviceGameplayVerified=False,thermalSavingsMeasured=False)
(w/('evidence/installation-'+a.receipt_name+'-r76.json')).write_text(json.dumps(record,indent=2)+'\n','utf8')
print(json.dumps(record,indent=2),flush=True)
run('shell','am','start','-n',package+'/org.emulationstation.frontend.auth.LoginActivity')
print('Official entry requested; check foreground and authentication separately.')
