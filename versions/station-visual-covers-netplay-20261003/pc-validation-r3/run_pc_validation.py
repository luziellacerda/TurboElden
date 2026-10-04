from pathlib import Path
import concurrent.futures,datetime,hashlib,json,os,shutil,subprocess,time,zipfile,struct
SOURCE=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
ROOT=SOURCE/('pc-validation-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
HERE=Path(__file__).resolve().parent
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
CLANG=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
PY=Path(r'C:\Python314\python.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
APK=SOURCE/'TurboStations-Capas4-Sinopses-LED-Netplay-R3-20261003.apk'
BASE=Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003\TurboStations-SNES-Mega-HUD-LZGames-R2-20261003.apk')
ROOT.mkdir();(ROOT/'evidence').mkdir();(ROOT/'temp').mkdir()
os.environ['TEMP']=os.environ['TMP']=str(ROOT/'temp')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for sub in ['src','tests']:shutil.copytree(SOURCE/'station'/sub,ROOT/'station'/sub)
for name in ['run_tests.py','build_module.py','build_frontend.py']:copy(SOURCE/'station'/name,ROOT/'station'/name)
(ROOT/'station/temp').mkdir()
shutil.copytree(SOURCE/'netplay/src',ROOT/'netplay/src')
for p in (SOURCE/'netplay').iterdir():
 if p.is_file() and p.suffix in ('.java','.py','.h','.xml','.json'):copy(p,ROOT/'netplay'/p.name)
for name in ['native_info.h','native_formation.h','native_magazine.h','premium-magazine-led-android.glsl','station_game_infos.h','game_infos.h','native_menu_power.h','native_console.h','station_info_layout.h','native_carousel.cpp','native_catalog_identity.h']:
 copy(SOURCE/'native'/name,ROOT/'native'/name)
for sub in ['assets','evidence','server-inputs']:shutil.copytree(SOURCE/sub,ROOT/sub,dirs_exist_ok=True)
for name in ['test_visual_metadata.py','test_shader_angle.py','test_station_info_layout.cpp','test_catalog_identity.cpp']:copy(SOURCE/name,ROOT/name)
copy(HERE/'StationCoverLoadTest.java',ROOT/'station/tests/StationCoverLoadTest.java')
protected={str(p):sha(p) for p in [APK,SOURCE/'station/build/dex/classes.dex',SOURCE/'native/libturbo_carousel.so',SOURCE/'station/build/native/arm64-v8a/libstation_frontend.so',SOURCE/'netplay/build/dex/classes.dex']}
results=[]
def run(name,args,cwd=ROOT,timeout=180):
 start=time.monotonic();out=subprocess.run(list(map(str,args)),cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
 (ROOT/(name+'.log')).write_text(out.stdout+out.stderr,'utf-8')
 record={'name':name,'passed':out.returncode==0,'exitCode':out.returncode,'seconds':round(time.monotonic()-start,3),'log':name+'.log'}
 results.append(record);print(json.dumps(record),flush=True)
 if out.returncode:raise RuntimeError(name+': '+(out.stdout+out.stderr)[-3500:])
 return out.stdout
def station():
 run('station-suite',[PY,ROOT/'station/run_tests.py'])
 run('station-dex-rebuild',[PY,ROOT/'station/build_module.py'])
 assert sha(ROOT/'station/build/dex/classes.dex')==protected[str(SOURCE/'station/build/dex/classes.dex')]
 run('station-arm64-rebuild',[PY,ROOT/'station/build_frontend.py'])
 # Relocated source paths may alter symbol/build metadata; output is a compile check.
 java=[JDK/'java.exe','-Xmx256m','-cp',str(ROOT/'station/build/host-classes')+r';E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar']
 run('cover-load-4096',java+['org.emulationstation.frontend.station.StationCoverLoadTest',ROOT/'station/build/load4096'])
 for index in range(10):
  run('cover-race-repeat-'+str(index+1),java+['org.emulationstation.frontend.station.StationCoverConcurrencyTest',ROOT/'station/build'/('race-'+str(index))])
def netplay():
 run('netplay-contracts',[PY,ROOT/'netplay/test_contracts.py'])
 run('netplay-dex-rebuild',[PY,ROOT/'netplay/build_netplay.py'])
 assert sha(ROOT/'netplay/build/dex/classes.dex')==protected[str(SOURCE/'netplay/build/dex/classes.dex')]
def native():
 for name in ['station_cover_plan_test','station_cover_retry_test']:
  exe=ROOT/(name+'.exe');run(name+'-compile',[CLANG,'-std=c++17','-O2',ROOT/'station/tests'/(name+'.cpp'),'-o',exe]);run(name,[exe])
 run('catalog-identity-9-cases',[CLANG,'-std=c++17','-fsyntax-only',ROOT/'test_catalog_identity.cpp'])
 run('layout-98-cases',[CLANG,'-std=c++17','-fsyntax-only',ROOT/'test_station_info_layout.cpp'])
def visual():
 run('metadata-16-tests',[PY,ROOT/'test_visual_metadata.py'])
 run('gles100-angle',[PY,ROOT/'test_shader_angle.py'])
def apk():
 assert sha(APK)==json.loads((SOURCE/'build-result.json').read_text('utf8'))['sha256']
 run('apk-signature',[JDK/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--verbose','--print-certs',APK])
 run('apk-alignment',[BT/'zipalign.exe','-c','-P','16','4',APK])
 with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(APK) as new:
  assert new.testzip() is None
  def signatures(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.RSA','.DSA','.EC','.SF'))
  oldnames={n for n in old.namelist() if not signatures(n)};newnames={n for n in new.namelist() if not signatures(n)}
  assert oldnames<=newnames and len(new.namelist())==len(set(new.namelist()))
  changed=[];same=0
  for name in oldnames:
   with old.open(name) as f:a=hashlib.file_digest(f,'sha256').digest()
   with new.open(name) as f:b=hashlib.file_digest(f,'sha256').digest()
   if a==b:same+=1
   else:changed.append(name)
  assert same==10871 and set(changed)=={'AndroidManifest.xml','classes28.dex','lib/arm64-v8a/libstation_frontend.so','lib/arm64-v8a/libturbo_carousel.so'}
  receipt={'zipCrcValid':True,'preservedEntries':same,'changedEntries':sorted(changed),'additions':len(newnames-oldnames),'sha256':sha(APK)}
  (ROOT/'evidence/apk-audit.json').write_text(json.dumps(receipt,indent=2)+'\n','utf-8')
  print('PASS complete APK CRC/payload preservation',flush=True)

print('PC validation root: '+str(ROOT),flush=True)
failures=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as workers:
 tasks={workers.submit(job):job.__name__ for job in [station,netplay,native,visual,apk]}
 for task in concurrent.futures.as_completed(tasks):
  try:task.result()
  except Exception as error:failures.append({'stage':tasks[task],'error':str(error)});print('FAIL '+str(error),flush=True)
unchanged=all(sha(Path(p))==value for p,value in protected.items())
assert unchanged
summary={'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(ROOT),'apk':str(APK),'apkSha256':protected[str(APK)],'results':results,'failures':failures,'passed':not failures,'releasedArtifactsUnchanged':unchanged,'phoneUsed':False,'productionServerUsed':False,'androidRuntimeTested':False,'twoDeviceNetplayTested':False}
load=ROOT/'station/build/load4096/load-result.json'
if load.exists():summary['syntheticCoverLoad']=json.loads(load.read_text('utf-8'))
(ROOT/'PC-TEST-RESULT.json').write_text(json.dumps(summary,indent=2)+'\n','utf-8')
(SOURCE/'latest-pc-validation.json').write_text(json.dumps({'path':str(ROOT),'passed':not failures},indent=2)+'\n','utf-8')
print(json.dumps({'passed':not failures,'result':str(ROOT/'PC-TEST-RESULT.json'),'failures':failures}),flush=True)
if failures:raise SystemExit(1)
