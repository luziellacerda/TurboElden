from pathlib import Path
import datetime,hashlib,json,os,shlex,subprocess
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'saturn-leds'
adb=Path(__file__).parent/'work/android-tools/platform-tools/adb.exe';os.environ['ADB_USB_LEGACY']='1'
build=json.loads((R/'build-result.json').read_text());apk=Path(build['apk'])
with apk.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==build['sha256']
def run(*args,timeout=45):return subprocess.run([str(adb),*args],capture_output=True,timeout=timeout)
state=run('shell','dumpsys','activity','activities');assert state.returncode==0
lines=state.stdout.decode(errors='replace').splitlines()
top=[s.strip() for s in lines if 'topResumedActivity=' in s]
own=[s.strip() for s in lines if 'Hist  #' in s and 'org.emulationstation.frontend/' in s]
assert not own or all('org.emulationstation.frontend/.ESActivity ' in s or 'org.emulationstation.frontend/.auth.LoginActivity ' in s for s in own),own
assert not top or all('org.emulationstation.frontend/' not in s or 'org.emulationstation.frontend/.ESActivity ' in s for s in top),top
(R/'before-install-focus.txt').write_text('\n'.join(top+own),encoding='utf-8')
result=run('install','--no-streaming','-r',str(apk),timeout=300)
output=result.stdout.decode(errors='replace')+result.stderr.decode(errors='replace');(R/'install.log').write_text(output,encoding='utf-8');print(output,flush=True)
assert result.returncode==0 and 'Success' in output
paths=run('shell','pm','path','org.emulationstation.frontend').stdout.decode().splitlines()
base=[x.removeprefix('package:').strip() for x in paths if x.startswith('package:') and x.endswith('/base.apk')]
assert len(base)==1 and base[0].startswith('/data/app/')
actual=run('shell','sha256sum '+shlex.quote(base[0])).stdout.decode().split()[0];assert actual==build['sha256']
record={'installed_at':datetime.datetime.now().astimezone().isoformat(),'apk':str(apk),'sha256':actual,'device_sha256':actual,'result':'Success','mode':'adb install --no-streaming -r','data_preserved':True,'runtime_verified':False,'gameplay_verified':False,'tests_run':False}
(R/'installed.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
build['installed']=True;(R/'build-result.json').write_text(json.dumps(build,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
profile_path=P/'stable-design/active-profile.json';profile=json.loads(profile_path.read_text(encoding='utf-8'))
profile.update({'installation_pending':False,'installed_apk_sha256':actual,'installed_apk':str(apk),'installed_apk_local_file_replaced_by_pending':False,'installation_record':str(R/'installed.json'),'build':str(R/'build-result.json')})
for key in ['pending_apk','pending_apk_sha256','pending_build','pending_update']:profile.pop(key,None)
profile['saturn']['installed']=True
profile['led_user_palette_2026_09_30']=build['leds']
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record),flush=True)
