from pathlib import Path
import subprocess,os,json,hashlib
from datetime import datetime,timezone
W=Path(r'E:\ESTUDO APK\work\station-actions-gear-r31-20261005');out=W/'poco-evidence';out.mkdir(exist_ok=True)
build=json.loads((W/'build-result.json').read_text());apk=Path(build['apk'])
os.environ['ANDROID_USER_HOME']=r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
adb=[r'G:\Android\Sdk\platform-tools\adb.exe','-s','EYRWKVSWBQTSEUPV'];pkg='org.turboramastation.frontend'
def run(args):return subprocess.check_output(adb+args,text=True,encoding='utf8',errors='replace').strip()
def phone_hash():
 base=next(v.removeprefix('package:') for v in run(['shell','pm','path',pkg]).splitlines() if v.endswith('/base.apk'))
 return run(['shell','sha256sum',base]).split()[0]
with apk.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==build['sha256']
present=run(['shell','pm','list','packages','--user','0',pkg])
before=phone_hash() if 'package:'+pkg in present.splitlines() else None
assert before in [None,'438010ddd716b67731c59462caebb6e163d216ed99a1e8b9a347ddd6b1a2c4ac']
receipt={'startedAt':datetime.now(timezone.utc).isoformat(),'apk':str(apk),'expectedSHA256':build['sha256'],'previousSHA256':before,'uninstallPerformed':False,'dataCleared':False,'screenSettingTemporary':False,'deviceModel':'POCO 2412DPC0AG','activationPerformed':False}
print('Installing R31 native visual changes, preserving existing data...',flush=True)
r=subprocess.run(adb+['install','--no-incremental','-r','--user','0',str(apk)],capture_output=True,text=True)
receipt.update(installOutput=(r.stdout+r.stderr).strip(),exitCode=r.returncode,installed=r.returncode==0 and 'Success' in r.stdout)
if receipt['installed']:
 receipt['installedSHA256']=phone_hash();receipt['hashMatches']=receipt['installedSHA256']==build['sha256']
 if receipt['hashMatches']:receipt['launchOutput']=run(['shell','am','start','-n',pkg+'/org.emulationstation.frontend.auth.LoginActivity'])
receipt['finishedAt']=datetime.now(timezone.utc).isoformat()
(out/('installation-'+build['sha256'][:8]+'.json')).write_text(json.dumps(receipt,indent=2)+'\n','utf8')
(out/'installation.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8');print(json.dumps(receipt,indent=2),flush=True)
assert receipt['installed'] and receipt['hashMatches']
