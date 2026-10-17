"""Bind the GBA console-only renderer change to the exact signed R178 package."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,zipfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
BASE_SHA='0ceb4146bb031b923d101f0aba2773f8b10a6afc30222c16697664ae4c3b445c'
PREFIX='lib/arm64-v8a/';ENGINE='assets/station-online/engines.json'
WRAPPERS={'psx':'libstation_psx_online.so','n64':'libstation_mupen64plus_runtime.so','dolphin':'libstation_dolphin_runtime.so'}
ALLOWED={'AndroidManifest.xml',ENGINE,PREFIX+'libturbo_carousel.so',*[PREFIX+n for n in WRAPPERS.values()]}
NATIVE=['StationPsxEntry.cpp','StationPsxOwner.cpp','StationPsxProtocol.cpp','StationPsxSha256.cpp']
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def run(command,log):
 r=subprocess.run(list(map(str,command)),capture_output=True,text=True,timeout=1800);Path(log).write_text(r.stdout+r.stderr)
 need(r.returncode==0,'Build failed: '+Path(log).name);return r.stdout+r.stderr
def entry_sha(z,name):
 with z.open(name) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def fingerprint(raw):
 matches=[]
 for m in re.finditer(rb'\{"',raw):
  end=raw.find(b'\0',m.start())
  try:
   value=json.loads(raw[m.start():end].decode('ascii'))
   if isinstance(value,dict) and isinstance(value.get('payloadSha256'),dict):
    need(raw[m.start():end]==canonical(value),'Noncanonical native identity');matches.append(value)
  except (ValueError,UnicodeError):pass
 need(len(matches)==1,'Exactly one inherited runtime fingerprint required');return matches[0]
def freeze(commit,task):
 need(re.fullmatch('[0-9a-f]{40}',commit) is not None,'Full frozen source commit required')
 sources=list(HERE.glob('*.py'))+list((HERE.parent/'signing').glob('*.py'))+list((HERE.parent/'native').glob('*.h'))
 sources += [REPO/'integration/gba-console-r177/recipe/build_console.py', REPO/'integration/gba-console-r177/native/station_gba_console_aliases.h']
 sources+=list((REPO/'integration/psx-online/native').glob('*.cpp'))+list((REPO/'integration/psx-online/native').glob('*.hpp'))+[REPO/'integration/psx-online/native/PsxPinnedOptions.h',REPO/'integration/psx-updater-r170/recipe/manifest_delta.py']
 pins={}
 for p in sorted(set(sources)):
  name=p.relative_to(REPO).as_posix();raw=subprocess.check_output(['git','-C',str(REPO),'show',commit+':'+name])
  need(raw==p.read_bytes(),'Frozen source differs: '+name);pins[name]=digest(raw)
 renderer=read(task/'renderer/receipt.json')
 need(renderer['passed'] and renderer['baselineRuntimeReproduced'] and sha(task/'renderer/libturbo_carousel.so')==renderer['outputSha256'],'Reviewed renderer required')
 for name,pin in renderer['sourceSha256'].items():need(pins[name]==pin,'Compiled renderer source differs from final source')
 return pins
def base(task):
 p=Path(read(task/'inputs/base-apk.json')['path']);need(p.is_file() and sha(p)==BASE_SHA,'Exact signed R178 donor required');return p
def prepare(task,commit):
 pins=freeze(commit,task);out=task/'compile';out.mkdir(exist_ok=False)
 patcher=load('r179_manifest',HERE/'manifest_delta.py')
 with zipfile.ZipFile(base(task)) as z:manifest=patcher.patch(z.read('AndroidManifest.xml'))
 (out/'AndroidManifest.xml').write_bytes(manifest)
 save(out/'receipt.json',{'schema':'station.r179.compile.v1','passed':True,'sourceCommit':commit,'sourceSha256':pins,'baselineApkSha256':BASE_SHA,
      'manifestSha256':digest(manifest),'minimumSdk':26,'targetSdk':34,'dexModified':False,'all40DexPartitionsPreserved':True,'rendererReceiptSha256':sha(task/'renderer/receipt.json')})
 print('MANIFEST_AND_RENDERER_SOURCE_PASSED',flush=True)
def native(task,ndk,commit):
 pins=freeze(commit,task);compiled=read(task/'compile/receipt.json');need(compiled['passed'] and compiled['sourceSha256']==pins,'Same frozen preparation required')
 need('Pkg.Revision = 28.2.13676358' in (ndk/'source.properties').read_text(),'Production NDK r28c required')
 out=task/'native';out.mkdir(exist_ok=False);tools=ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin'
 with zipfile.ZipFile(base(task)) as z:
  previous={k:fingerprint(z.read(PREFIX+n)) for k,n in WRAPPERS.items()};payload=previous['psx']['payloadSha256']
  need(all(v['payloadSha256']==payload for v in previous.values()),'Parent identity disagreement')
  need(all(entry_sha(z,n)==h for n,h in payload.items()),'Actual R178 payload differs');registry=json.loads(z.read(ENGINE))
 payload={**payload,'AndroidManifest.xml':sha(task/'compile/AndroidManifest.xml'),PREFIX+'libturbo_carousel.so':sha(task/'renderer/libturbo_carousel.so')}
 transforms={**previous['psx']['productiveTransforms'],**{'station-r179/'+n:h for n,h in pins.items()}}
 markers={};abi={}
 for kind,name in WRAPPERS.items():
  identity=copy.deepcopy(previous[kind]);identity.update(baseApkSha256=BASE_SHA,payloadSha256=payload,productiveTransforms=transforms,parentFingerprintSha256=digest(canonical(previous[kind])))
  if kind!='psx':identity['psxRuntimeSha256']=markers['psx']['runtimeSha256']
  raw=canonical(identity);stem='StationPsxRuntime' if kind=='psx' else 'StationMupenRuntime' if kind=='n64' else 'StationDolphinRuntime'
  source=out/(kind+('.cpp' if kind=='psx' else '.c'));prefix='extern "C" ' if kind=='psx' else ''
  source.write_text(prefix+'__attribute__((visibility("default"))) const char* '+stem+'Identity(){return "'+digest(raw)+'";}\n'+prefix+'__attribute__((visibility("default"))) const char* '+stem+'Manifest(){return '+json.dumps(raw.decode('ascii'))+';}\n',encoding='ascii')
  binary=out/name
  if kind=='psx':
   root=REPO/'integration/psx-online/native'
   command=[tools/'aarch64-linux-android28-clang++','-std=c++20','-O2','-fPIC','-shared','-fno-omit-frame-pointer','-fno-optimize-sibling-calls','-Wall','-Wextra','-Werror','-Wl,-z,max-page-size=16384','-Wl,-z,relro,-z,now','-Wl,--no-undefined','-Wl,-soname,'+name,'-I'+str(root),*[root/n for n in NATIVE],source,'-ldl','-o',binary]
  else:command=[tools/'clang','--target=aarch64-linux-android24','-std=c11','-Oz','-fPIC','-fvisibility=hidden','-Wall','-Wextra','-Werror','-shared',source,'-o',binary,'-Wl,--no-undefined','-Wl,--build-id=sha1','-Wl,-soname,'+name,'-Wl,-z,max-page-size=16384','-Wl,-z,common-page-size=16384']
  run(command,out/(kind+'-compile.log'))
  if kind!='psx':run([tools/'llvm-strip','--strip-unneeded',binary],out/(kind+'-strip.log'))
  need(fingerprint(binary.read_bytes())==identity,'Compiled identity differs')
  with zipfile.ZipFile(base(task)) as z:parent=out/(kind+'-parent.so');parent.write_bytes(z.read(PREFIX+name))
  symbol=lambda p:{l.split()[-1] for l in run([tools/'llvm-nm','-D','--defined-only',p],out/(p.stem+'-symbols.log')).splitlines() if len(l.split())>=2}
  actual=symbol(binary);need(actual==symbol(parent),'Native wrapper exports changed')
  if kind=='psx':
   bridge=(REPO/'integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxBridge.java').read_text()
   need(set(re.findall(r'public static native \S+\s+(\w+)\(',bridge))=={n.removeprefix('Java_org_emulationstation_frontend_netplay_StationPsxBridge_') for n in actual if n.startswith('Java_org_emulationstation_frontend_netplay_StationPsxBridge_')},'PSX JNI contract differs')
  save(out/(kind+'-fingerprint.json'),identity)
  markers[kind]={'runtimeLibrary':name,'runtimeSha256':sha(binary),'runtimeBytes':binary.stat().st_size,'fingerprintSha256':digest(raw)}
  abi[kind]={'exportsPreserved':True,'parentSha256':sha(parent),'candidateSha256':sha(binary),'nativeCoreCodeUnchanged':True}
 selected={};before=copy.deepcopy(registry)
 for row in registry['engines']:
  platform=row['platform']
  if platform not in ['psx','n64','gamecube','wii']:continue
  kind='dolphin' if platform in ['gamecube','wii'] else platform
  if platform=='psx':need(row['options'].count('inputDelayFrames=8\n')==1,'Stable PSX delay must remain 8')
  row.update(engineId=row['engineId'].rsplit('-',1)[0]+'-'+markers[kind]['runtimeSha256'][:12],runtimeSha256=markers[kind]['runtimeSha256']);selected[platform]=row['engineId']
 need(len(selected)==4 and len(registry['engines'])==13,'Exactly four inherited owners renewed')
 for a,b in zip(before['engines'],registry['engines']):need({k:v for k,v in a.items() if k not in ['engineId','runtimeSha256']}=={k:v for k,v in b.items() if k not in ['engineId','runtimeSha256']},'Emulation or approval policy changed')
 save(out/'engines.json',registry);save(out/'abi-contract.json',{'passed':True,'schema':'station.r179.identity-wrapper-abi.v1','wrappers':abi})
 need(freeze(commit,task)==pins,'Source changed during build')
 save(out/'receipt.json',{'schema':'station.r179.native.v1','passed':True,'sourceCommit':commit,'sourceSha256':pins,'markers':markers,'engineIds':selected,'payloadSha256':payload,'preservedCoreBinaries':True,'preservedAllDex':True,'psxInputDelayFramesBefore':8,'psxInputDelayFramesAfter':8,'otherEmulationOptionsPreserved':True})
 print('R179_NATIVE_IDENTITIES_PASSED',json.dumps(selected),flush=True)
def package(task,commit):
 pins=freeze(commit,task);compiled=read(task/'compile/receipt.json');identity=read(task/'native/receipt.json')
 need(compiled['passed'] and identity['passed'] and compiled['sourceSha256']==identity['sourceSha256']==pins,'Same frozen build required')
 out=task/'package';out.mkdir(exist_ok=False)
 replacements={'AndroidManifest.xml':task/'compile/AndroidManifest.xml',ENGINE:task/'native/engines.json',PREFIX+'libturbo_carousel.so':task/'renderer/libturbo_carousel.so',**{PREFIX+n:task/'native'/n for n in WRAPPERS.values()}}
 need(set(replacements)==ALLOWED,'Exactly six requested APK entries may change')
 expected={};before={};unsigned=out/'TurboStations-Premium-R179-unsigned.apk';zipfile.ZIP64_LIMIT=(1<<32)-1
 with zipfile.ZipFile(base(task)) as source,zipfile.ZipFile(unsigned,'x',allowZip64=False) as target:
  names=source.namelist();need(len(names)==len(set(names))==13861,'Exact parent entry set required')
  for entry in source.infolist():
   name=entry.filename;before[name]=entry_sha(source,name)
   with target.open(copy.copy(entry),'w',force_zip64=False) as stream:
    if name in replacements:
     with replacements[name].open('rb') as content:shutil.copyfileobj(content,stream,1024*1024)
    else:
     with source.open(name) as content:shutil.copyfileobj(content,stream,1024*1024)
   expected[name]=sha(replacements[name]) if name in replacements else before[name]
 need({n for n in names if expected[n]!=before[n]}==ALLOWED,'Unexpected APK difference')
 with zipfile.ZipFile(unsigned) as z:need(z.namelist()==names and all(entry_sha(z,n)==h for n,h in expected.items()),'Complete APK readback failed')
 need(freeze(commit,task)==pins,'Source changed during packaging')
 save(out/'unsigned-package.json',{'schema':'station.r179.package.v1','passed':True,'sourceCommit':commit,'sourceSha256':pins,'baseApkSha256':BASE_SHA,'unsignedApkSha256':sha(unsigned),'unsignedApkBytes':unsigned.stat().st_size,'entryCount':len(names),'expectedEntrySha256':expected,'replacedEntries':sorted(ALLOWED),'preservedEntryCount':13855,'changedDexPartitions':[],'preservedDexPartitions':40,'compileReceiptSha256':sha(task/'compile/receipt.json'),'nativeReceiptSha256':sha(task/'native/receipt.json')})
 print('R179_ALL40_DEX_AND_13855_ENTRIES_PRESERVED',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','native','package']);p.add_argument('--task',type=Path,required=True);p.add_argument('--ndk',type=Path);p.add_argument('--source-commit',required=True)
 a=p.parse_args()
 if a.stage=='native':need(a.ndk is not None,'NDK required');native(a.task,a.ndk,a.source_commit)
 elif a.stage=='prepare':prepare(a.task,a.source_commit)
 else:package(a.task,a.source_commit)
