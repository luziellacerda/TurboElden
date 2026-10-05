from pathlib import Path
import subprocess,json,hashlib,datetime,os,re
W=Path(r'E:\ESTUDO APK\work\station-download-performance-20261005')
out=W/'device-evidence';out.mkdir(exist_ok=True)
apk=W/'TurboStations-Desempenho-Offline-R16-20261005.apk'
expected='b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1'
adb=r'G:\Android\Sdk\platform-tools\adb.exe'
serial=os.environ['STATION_ADB_SERIAL'];pkg='org.turboramastation.frontend'
os.environ['ANDROID_USER_HOME']=r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
def run(args):
    p=subprocess.run([adb,'-s',serial,*args],capture_output=True,text=True,encoding='utf8',errors='replace')
    if p.returncode:raise RuntimeError(p.stderr or p.stdout)
    return p.stdout.strip()
assert run(['get-state'])=='device'
activities=run(['shell','dumpsys','activity','activities'])
top='\n'.join(l.strip() for l in activities.splitlines() if 'topResumedActivity=' in l or 'mResumedActivity=' in l)
assert 'org.emulationstation.frontend.ESActivity' in top, 'Not safely on platforms: '+top
processes=[s.strip() for s in run(['shell','ps','-A','-o','NAME']).splitlines() if s.strip().startswith(pkg)]
assert processes==[pkg], 'An emulator or another app process is open: '+repr(processes)
with apk.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
before=run(['shell','pm','path',pkg])
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
print('Updating installed app without uninstall or data cleanup',flush=True)
result=run(['install','--no-incremental','-r','--user','0',str(apk)])
(out/'adb-install.txt').write_text(result,'utf8');assert 'Success' in result
path=run(['shell','pm','path',pkg]).removeprefix('package:')
assert re.fullmatch(r'/data/app/[A-Za-z0-9_~./=+-]+/base\.apk',path),path
remote=run(['shell','sha256sum',path]).split()[0];assert remote==expected
launch=run(['shell','am','start','-W','-n',pkg+'/org.emulationstation.frontend.auth.LoginActivity'])
(out/'launch.txt').write_text(launch,'utf8')
record={'createdAt':start,'package':pkg,'model':run(['shell','getprop','ro.product.model']),
        'apk':str(apk),'apkSHA256':expected,'installedBaseSHA256':remote,'installResult':result,
        'updatedWithoutUninstall':True,'clearedData':False,'startedThroughPublicLauncher':True,
        'downloadMeasured':False,'offlineValidated':False,'gameplayValidated':False}
(out/'installation.json').write_text(json.dumps(record,indent=2),'utf8')
print(json.dumps(record,indent=2),flush=True)
