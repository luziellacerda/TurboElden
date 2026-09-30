from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');S=P/'platform-media-refresh/psvita'
R=P/'emulator-completion/vita-rar-fix';D=R.parent/'vita-rar-diagnosis';R.mkdir(parents=True,exist_ok=True)
(R/'tmp').mkdir(exist_ok=True);os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk'
EXPECTED='f0cd5ef1d06f89401a9707241ea0e9c96b966565c1ee050b6d00e43679c78438'
FROZEN=Path(r'F:\Turborama-build-archive\TurboramaStation-emulators-f0cd5ef1.apk')
N=Path(r'E:\TurboEdenEngine\android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(*args):subprocess.run(list(map(str,args)),check=True)
assert sha(BASE)==EXPECTED
if not FROZEN.exists():shutil.copy2(BASE,FROZEN)
assert sha(FROZEN)==EXPECTED
proposal=Path(__file__).parent/'proposed-vita-rar-fix/vita_archive_bridge.c'
shutil.copy2(proposal,R/'vita_archive_bridge.c');shutil.copy2(S/'vita_sdl_registry.c',R/'vita_sdl_registry.c')
shutil.copy2(D/'archive_read_support_format_rar5.c',R/'archive_read_support_format_rar5.c')
shutil.copy2(S/'vita_archive_bridge.c',R/'before-vita_archive_bridge.c')
lib=R/'libturbo_vita_jni.so'
run(N/'bin/clang.exe','--target=aarch64-linux-android26','--sysroot='+str(N/'sysroot'),'-std=c11','-D_GNU_SOURCE','-O2','-fPIC','-shared','-Wl,-z,max-page-size=16384','-Wl,-z,defs','-Wl,-s','-Wl,-soname,libturbo_vita_jni.so','-I'+str(S/'archive/libarchive-3.8.9/libarchive'),R/'vita_sdl_registry.c',R/'vita_archive_bridge.c',D/'libarchive-rar5-eof.a','-lz','-ldl','-llog','-lm','-o',lib)
changes={'lib/arm64-v8a/libturbo_vita_jni.so':lib.read_bytes()}
provenance=json.loads((D/'patch-record.json').read_text())
provenance.update({'base_apk_sha256':EXPECTED,'scope':'Only Vita archive JNI helper; original Vita engine and every other emulator/frontend/DEX preserved','firmware_bundled':False,'game_bundled':False,'real_game_archive_verified':False,'runtime_verified':False})
changes['assets/vita-rar-fix/provenance.json']=(json.dumps(provenance,indent=2)+'\n').encode()
for name in ['vita_archive_bridge.c','vita_sdl_registry.c','archive_read_support_format_rar5.c']:changes['assets/vita-rar-fix/'+name]=(R/name).read_bytes()
changes['assets/vita-rar-fix/libarchive-LICENSE']=(S/'archive/libarchive-3.8.9/COPYING').read_bytes()
with zipfile.ZipFile(FROZEN) as z:
 previous={}
 for name in z.namelist():
  if not name.startswith('META-INF/'):previous[name]=hashlib.sha256(z.read(name)).hexdigest()
  if name.startswith('assets/') and Path(name).name=='vita_archive_bridge.c':changes[name]=(R/'vita_archive_bridge.c').read_bytes()
 (R/'before-native.so').write_bytes(z.read('lib/arm64-v8a/libturbo_vita_jni.so'))
(R/'before-entry-hashes.json').write_text(json.dumps(previous,indent=2),encoding='utf-8')
aligned=R/'aligned.apk';assert not aligned.exists()
def put(z,old,data):
 info=copy.copy(old) if isinstance(old,zipfile.ZipInfo) else zipfile.ZipInfo(old)
 if not isinstance(old,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if old.endswith(('.so','.dex','.mp4','.arsc')) else zipfile.ZIP_DEFLATED
 info.extra=b''
 if info.compress_type==zipfile.ZIP_STORED:
  alignment=16384 if info.filename.endswith('.so') else 4
  offset=z.fp.tell()+30+len(info.filename.encode())
  if offset%alignment:
   pad=(-(offset+4))%alignment;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
 z.writestr(info,data)
with zipfile.ZipFile(FROZEN) as original,zipfile.ZipFile(aligned,'w') as out:
 seen=set()
 for info in original.infolist():
  if info.filename.startswith('META-INF/'):continue
  put(out,info,changes.get(info.filename,original.read(info.filename)));seen.add(info.filename)
 for name,data in changes.items():
  if name not in seen:put(out,name,data)
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(J,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',BASE,aligned)
run(J,'-jar',BT/'lib/apksigner.jar','verify',BASE)
with zipfile.ZipFile(BASE) as z:
 for name,h in previous.items():
  if name not in changes:assert hashlib.sha256(z.read(name)).hexdigest()==h,name
 for name,data in changes.items():assert z.read(name)==data,name
 videos=[n for n in z.namelist() if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4')]
 assert len(videos)==33 and all(z.getinfo(n).compress_type==zipfile.ZIP_STORED for n in videos)
aligned.unlink()
record={'built_at':datetime.datetime.now().astimezone().isoformat(),'apk':str(BASE),'sha256':sha(BASE),'bytes':BASE.stat().st_size,'base_sha256':EXPECTED,'frozen_base':str(FROZEN),'changed_entries':{n:hashlib.sha256(v).hexdigest() for n,v in changes.items()},'all_other_entries_identical':True,'all_dex_unchanged':True,'original_engine_libraries_unchanged':True,'installed':False,'runtime_verified':False,'git_published':False,'stable_promoted':False}
(R/'build-result.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
shutil.copy2(R/'vita_archive_bridge.c',S/'vita_archive_bridge.c');shutil.copy2(lib,S/lib.name)
shutil.copy2(Path(__file__),R/'package.py');shutil.copy2(Path(__file__).parent/'build_vita_rar_fix.py',R/'build-patched-library.py')
profile_path=P/'stable-design/active-profile.json';profile=json.loads(profile_path.read_text(encoding='utf-8'))
profile.update({'pending_apk':str(BASE),'pending_apk_sha256':record['sha256'],'pending_build':str(R/'build-result.json'),'pending_update':'Vita RAR5 empty-final-block and directory handling; diagnostics','installation_pending':True,'installed_apk_local_file_replaced_by_pending':True,'latest_built_apk':str(BASE),'latest_built_apk_sha256':record['sha256'],'latest_build_record':str(R/'build-result.json')})
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['apk','sha256','bytes','all_other_entries_identical','installed']},ensure_ascii=False))
