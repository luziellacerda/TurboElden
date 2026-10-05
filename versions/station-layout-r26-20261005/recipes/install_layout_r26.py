from pathlib import Path
import datetime,hashlib,json,os,re,subprocess
W=Path(r'E:\ESTUDO APK\work\station-layout-r26-20261005');D=W/'device-evidence';D.mkdir(exist_ok=True)
r=json.loads((W/'build-result.json').read_text('utf8'))
apk=Path(r['apk'])
with apk.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
os.environ['ANDROID_USER_HOME']=r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
adb=[r'G:\Android\Sdk\platform-tools\adb.exe','-s',os.environ.get('STATION_ADB_SERIAL','RQCY30751WY')]
pkg='org.turboramastation.frontend'
def run(args):
 p=subprocess.run(adb+args,capture_output=True);assert p.returncode==0,p.stderr.decode(errors='replace');return p.stdout
assert run(['get-state']).decode().strip()=='device'
activity=run(['shell','dumpsys','activity','activities']).decode('utf8',errors='replace')
top='\n'.join(x.strip() for x in activity.splitlines() if 'topResumedActivity=' in x)
assert pkg in top and 'ESActivity' in top, 'Leave Station platforms/collections open; active emulator session will not be closed'
prior=run(['shell','pm','path','--user','0',pkg]).decode().strip()
assert prior.startswith('package:') and prior.count('\n')==0
prior_hash=run(['shell','sha256sum',prior.removeprefix('package:')]).decode().split()[0]
assert prior_hash==r['baseSHA256'], 'Unexpected installed APK; coordinate before replacing another revision'
print('Updating the verified layout base to R26 with the existing data retained',flush=True)
output=run(['install','--no-incremental','-r','--user','0',str(apk)]).decode('utf8',errors='replace')
(D/'adb-install.txt').write_text(output,'utf8');assert 'Success' in output
installed=run(['shell','pm','path','--user','0',pkg]).decode().strip().removeprefix('package:')
actual=run(['shell','sha256sum',installed]).decode().split()[0];assert actual==r['sha256']
launch=run(['shell','am','start','-n',pkg+'/org.emulationstation.frontend.auth.LoginActivity']).decode('utf8',errors='replace')
(D/'launch.txt').write_text(launch,'utf8')
record={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':pkg,'priorSHA256':prior_hash,
 'apk':str(apk),'apkSHA256':r['sha256'],'installedBaseSHA256':actual,'installResult':output.strip(),
 'updatedWithoutUninstall':True,'clearedData':False,'startedThroughPublicLauncher':True,'panelVisuallyValidated':False}
(D/'installation.json').write_text(json.dumps(record,indent=2)+'\n','utf8');print(json.dumps(record))
