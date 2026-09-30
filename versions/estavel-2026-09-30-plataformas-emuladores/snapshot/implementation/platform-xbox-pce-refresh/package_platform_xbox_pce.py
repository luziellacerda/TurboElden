from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile,xml.etree.ElementTree as ET
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-xbox-pce-refresh';M=R/'merged'
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk';FROZEN=Path(r'F:\Turborama-build-archive\TurboramaStation-before-NetherSX2-ca5556ac.apk');EXPECTED='ca5556ac81e96e49d67ac0134533604908dd5122351c898ac2125d03a223cee7'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(*a):subprocess.run(list(map(str,a)),check=True)
assert sha(BASE)==EXPECTED and sha(FROZEN)==EXPECTED
def public(p):return {(e.get('type'),e.get('name')):e.get('id') for e in ET.parse(p).getroot() if e.tag=='public'}
oldpub=public(R/'frontend-decoded/res/values/public.xml');newpub=public(M/'res/values/public.xml');assert all(newpub[k]==v for k,v in oldpub.items())
# Keep every other emulator byte-identical. Only the host startup guard/catalog DEX is reassembled.
changes={}
with zipfile.ZipFile(R/'merged-template.apk') as z:
 for n in z.namelist():
  if n in ['AndroidManifest.xml','resources.arsc','classes.dex','classes8.dex','classes26.dex'] or n.startswith('res/'):changes[n]=z.read(n)
changes['classes27.dex']=(R/'bridge-dex/classes.dex').read_bytes()
changes['lib/arm64-v8a/libturbo_carousel.so']=(R/'libturbo_carousel.so').read_bytes()
changes['lib/arm64-v8a/libmednafen_pce_libretro_android.so']=(R/'libmednafen_pce_libretro_android.so').read_bytes()
for p in (M/'lib/arm64-v8a').glob('*.so'):changes['lib/arm64-v8a/'+p.name]=p.read_bytes()
for p in (M/'assets').rglob('*'):
 if p.is_file() and not p.relative_to(M/'assets').as_posix().startswith('dexopt/') and p.name!='gamecontrollerdb.txt':changes[p.relative_to(M).as_posix()]=p.read_bytes()
media=json.loads((R/'media-manifest.json').read_text(encoding='utf-8'))+json.loads((R/'naomi-media-manifest.json').read_text(encoding='utf-8'))
for row in media:changes[row['asset']]=(R/'media'/Path(row['asset']).name).read_bytes()
changes['assets/turboretro/catalog.json']=(R/'catalog-refresh.json').read_bytes()
catalog_sha=hashlib.sha256(changes['assets/turboretro/catalog.json']).hexdigest();assert catalog_sha.encode() in changes['classes8.dex']
sources={n:P/n for n in ['native_carousel.cpp','native_xboxclassic.h','native_pcecd.h','local_game_covers.h','system_infos.h','system_video720_assets.h','theme-infos-mapping.json','laser_assets.h','laser-user-overrides.json']}
for n,p in sources.items():changes['assets/platform-refresh/source/'+n]=p.read_bytes()
for p in (R/'java').rglob('*.java'):changes['assets/platform-refresh/source/'+p.name]=p.read_bytes()
for n in ['media-manifest.json','naomi-media-manifest.json','covers-manifest.json','local-setup-provenance.json','pce-provenance.json','catalog-hidden-metadata.json']:
 changes['assets/platform-refresh/'+n]=(R/n).read_bytes()
for n in ['pce-LICENSE','pce-README.md']:changes['assets/platform-refresh/'+n]=(R/'upstream'/n).read_bytes()
with zipfile.ZipFile(FROZEN) as z:
 for n in z.namelist():
  if n.startswith('assets/') and Path(n).name in sources:changes[n]=sources[Path(n).name].read_bytes()
# DEX class identity and native library collisions are reviewed before replacing any output.
def dexclasses(data):
 def read32(offset):return struct.unpack_from('<I',data,offset)[0]
 ns,so=struct.unpack_from('<II',data,0x38);nt,to=struct.unpack_from('<II',data,0x40);nc,co=struct.unpack_from('<II',data,0x60)
 strings=[]
 for i in range(ns):
  o=read32(so+i*4)
  while data[o]&128:o+=1
  o+=1;strings.append(data[o:data.index(b'\0',o)].decode('utf-8','replace'))
 types=[strings[read32(to+i*4)] for i in range(nt)]
 return [types[read32(co+i*32)] for i in range(nc)]
with zipfile.ZipFile(FROZEN) as z:
 present={};duplicates=[]
 for n in sorted(set(z.namelist())|set(changes)):
  if n.endswith('.dex') and '/' not in n:
   data=changes[n] if n in changes else z.read(n)
   for c in dexclasses(data):
    if c in present:duplicates.append((c,present[c],n))
    present[c]=n
 assert not duplicates,duplicates[:20]
 for n in changes:
  if n.startswith('lib/') and n in z.namelist():assert n=='lib/arm64-v8a/libturbo_carousel.so',n
assert (P/'native_ps2.h').read_bytes()==(R/'before/native_ps2.h').read_bytes()
assert (P/'native_wiiu.h').read_bytes()==(R/'before/native_wiiu.h').read_bytes()
aligned=R/'refresh-aligned.apk';assert not aligned.exists()
def put(z,old,data):
 info=copy.copy(old) if isinstance(old,zipfile.ZipInfo) else zipfile.ZipInfo(old)
 if not isinstance(old,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if old.endswith(('.so','.dex','.mp4','.arsc')) else zipfile.ZIP_DEFLATED
 info.extra=b''
 if info.compress_type==zipfile.ZIP_STORED:
  align=16384 if info.filename.endswith('.so') else 4;off=z.fp.tell()+30+len(info.filename.encode())
  if off%align:pad=(-(off+4))%align;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
 z.writestr(info,data)
with zipfile.ZipFile(FROZEN) as z,zipfile.ZipFile(aligned,'w') as out:
 seen=set()
 for info in z.infolist():
  if info.filename.startswith('META-INF/'):continue
  put(out,info,changes.get(info.filename,z.read(info.filename)));seen.add(info.filename)
 for n,data in changes.items():
  if n not in seen:put(out,n,data)
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(J/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',BASE,aligned)
run(J/'java.exe','-jar',BT/'lib/apksigner.jar','verify',BASE)
previous=json.loads((R/'before/entry-hashes.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(BASE) as z:
 for n,h in previous.items():
  if n not in changes:assert hashlib.sha256(z.read(n)).hexdigest()==h,n
 for n,data in changes.items():assert z.read(n)==data,n
 videos=[n for n in z.namelist() if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4')]
 assert all(z.getinfo(n).compress_type==zipfile.ZIP_STORED for n in videos)
 for n in ['classes15.dex','classes16.dex','lib/arm64-v8a/libturbo_saturn.so']:
  assert hashlib.sha256(z.read(n)).hexdigest()==previous[n],n
aligned.unlink();shutil.copy2(R/'libturbo_carousel.so',P/'libturbo_carousel.so')
record={'built_at':datetime.datetime.now().astimezone().isoformat(),'apk':str(BASE),'sha256':sha(BASE),'bytes':BASE.stat().st_size,'base_sha256':EXPECTED,'frozen_base':str(FROZEN),'catalog_sha256':catalog_sha,'local_game_covers':58,'jaguar_games':56,'pcecd_games':2,'hidden_non_game_entries':68,'pspbr_games':59,'xbox_games':54,'xbox_engine':'X1 BOX 1.2.8','pcecd_engine':'Beetle PCE accurate, official Android arm64 build','media':media,'naomi_catalog':'two empty platform categories: server game lists not found','naomi3':'video/name/catalog not identified; not added','nesbr_added':False,'ps2_unchanged':True,'other_existing_engine_libraries_unchanged':True,'existing_resource_ids_preserved':True,'all_unmodified_entries_identical':True,'changed_entries':{n:hashlib.sha256(v).hexdigest() for n,v in changes.items()},'installed':False,'runtime_verified':False,'git_published':False,'stable_promoted':False}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
profile_path=P/'stable-design/active-profile.json';profile=json.loads(profile_path.read_text(encoding='utf-8'));profile.update({'pending_apk':str(BASE),'pending_apk_sha256':record['sha256'],'pending_build':str(R/'build-result.json'),'pending_update':'PSP BR, Xbox classic, PCE CD BIOS/core, local Jaguar/PCE covers, platform media','installation_pending':True,'installed_apk_local_file_replaced_by_pending':True,'latest_built_apk':str(BASE),'latest_built_apk_sha256':record['sha256'],'latest_build_record':str(R/'build-result.json')});profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8')
for n in ['prepare_xbox_classic.py','finish_xbox_merge.py','prepare_refresh_catalog.py','apply_refresh_sources.py','package_platform_xbox_pce.py']:shutil.copy2(Path(__file__).parent/n,R/n)
print(json.dumps({k:record[k] for k in ['apk','sha256','bytes','ps2_unchanged','local_game_covers','pspbr_games','installed']},ensure_ascii=False))
