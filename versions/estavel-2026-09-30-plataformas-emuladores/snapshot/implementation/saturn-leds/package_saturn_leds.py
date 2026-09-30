from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'saturn-leds';C=R/'catalog-final'
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk';EXPECTED='33e84a20049b832bfba68992d7e054826fc996455865abc5b4658d11746a6477'
frozen=Path(json.loads((R/'before/source-manifest.json').read_text())['frozen_base'])
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15');J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(*args):subprocess.run(list(map(str,args)),check=True)
assert sha(BASE)==EXPECTED and sha(frozen)==EXPECTED
media=json.loads((R/'media-manifest.json').read_text());catalog=json.loads((C/'catalog-change.json').read_text());palette=json.loads((R/'requested-leds.json').read_text())
actual_palette={row['key']:row['color'] for row in json.loads((P/'laser-system-colors.json').read_text())}
assert all(actual_palette[key]==values[0] for key,values in palette.items())
assert sha(C/'catalog-with-saturn.json')==catalog['catalog_sha256']
assert catalog['catalog_sha256'].encode('ascii') in (C/'classes8.dex').read_bytes()
with zipfile.ZipFile(BASE) as z:
 before_catalog=json.loads(z.read('assets/turboretro/catalog.json'))
after_catalog=json.loads((C/'catalog-with-saturn.json').read_text(encoding='utf-8'))
assert after_catalog[:-1]==before_catalog and after_catalog[-1]['Name']=='saturn' and len(after_catalog[-1]['Files'])==32
changes={'lib/arm64-v8a/libturbo_carousel.so':(P/'libturbo_carousel.so').read_bytes(),'classes8.dex':(C/'classes8.dex').read_bytes(),'assets/turboretro/catalog.json':(C/'catalog-with-saturn.json').read_bytes(),media['asset']:(R/'media/720-saturn.mp4').read_bytes()}
source_names=['native_carousel.cpp','native_saturn.h','system_video720_assets.h','system_infos.h','theme-infos-mapping.json','laser-user-overrides.json','prepare_laser.py','laser-system-colors.json','laser_assets.h']
sources={name:P/name for name in source_names};assert all(path.exists() for path in sources.values())
for name,path in sources.items():changes['assets/saturn-leds/source/'+name]=path.read_bytes()
changes['assets/saturn-leds/media-manifest.json']=(R/'media-manifest.json').read_bytes()
changes['assets/saturn-leds/requested-leds.json']=(R/'requested-leds.json').read_bytes()
changes['assets/saturn-leds/catalog-change.json']=(C/'catalog-change.json').read_bytes()
with zipfile.ZipFile(BASE) as z:
 for name in z.namelist():
  if name.startswith('assets/') and Path(name).name in sources:changes[name]=sources[Path(name).name].read_bytes()
assert hashlib.sha256(changes[media['asset']]).hexdigest()==media['sha256']
aligned=R/'saturn-aligned.apk';assert not aligned.exists()
def put(z,old,data):
 info=copy.copy(old) if isinstance(old,zipfile.ZipInfo) else zipfile.ZipInfo(old)
 if not isinstance(old,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if old.endswith(('.so','.dex','.mp4','.arsc')) else zipfile.ZIP_DEFLATED
 info.extra=b''
 if info.compress_type==zipfile.ZIP_STORED:
  alignment=16384 if info.filename.endswith('.so') else 4;offset=z.fp.tell()+30+len(info.filename.encode())
  if offset%alignment:
   pad=(-(offset+4))%alignment;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
 z.writestr(info,data)
with zipfile.ZipFile(frozen) as original,zipfile.ZipFile(aligned,'w') as out:
 seen=set()
 for info in original.infolist():
  if info.filename.startswith('META-INF/'):continue
  put(out,info,changes.get(info.filename,original.read(info.filename)));seen.add(info.filename)
 for name,data in changes.items():
  if name not in seen:put(out,name,data)
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(J,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',BASE,aligned)
run(J,'-jar',BT/'lib/apksigner.jar','verify',BASE)
previous=json.loads((R/'before/entry-hashes.json').read_text())
with zipfile.ZipFile(BASE) as z:
 for name,h in previous.items():
  if name not in changes:assert hashlib.sha256(z.read(name)).hexdigest()==h,name
 for name,data in changes.items():assert z.read(name)==data,name
 videos=[n for n in z.namelist() if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4')]
 assert len(videos)==34 and all(z.getinfo(n).compress_type==zipfile.ZIP_STORED for n in videos)
 assert hashlib.sha256(z.read('lib/arm64-v8a/libyabasanshiro_libretro_android.so')).hexdigest()=='84d4eb18ae94d97b6d189e40168abb1f449c7a859510b2125e2b83c64b76795b'
aligned.unlink()
record={'built_at':datetime.datetime.now().astimezone().isoformat(),'apk':str(BASE),'sha256':sha(BASE),'bytes':BASE.stat().st_size,'base_sha256':EXPECTED,'frozen_base':str(frozen),'saturn_games':32,'saturn_covers':32,'saturn_core':'bundled YabaSanshiro v3.4.2 09ed8e5','saturn_rom_folder':'saturn','saturn_video':media,'leds':palette,'changed_entries':{n:hashlib.sha256(v).hexdigest() for n,v in changes.items()},'all_other_entries_identical':True,'original_engine_libraries_unchanged':True,'vita_rar_fix_preserved':True,'existing_catalog_items_preserved':17972,'expected_visible_platforms':39,'installed':False,'runtime_verified':False,'tests_run':False,'git_published':False,'stable_promoted':False}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');shutil.copy2(Path(__file__),R/'package_saturn_leds.py')
profile_path=P/'stable-design/active-profile.json';profile=json.loads(profile_path.read_text(encoding='utf-8'))
profile.update({'pending_apk':str(BASE),'pending_apk_sha256':record['sha256'],'pending_build':str(R/'build-result.json'),'pending_update':'Sega Saturn32CHD/catalog/video/settings and eight owner LED colors','installation_pending':True,'installed_apk_local_file_replaced_by_pending':True,'latest_built_apk':str(BASE),'latest_built_apk_sha256':record['sha256'],'latest_build_record':str(R/'build-result.json')})
profile['saturn']={'core':record['saturn_core'],'folder':'saturn','games':32,'covers':32,'catalog_hash':catalog['catalog_sha256'],'new_engine_downloaded':False,'runtime_verified':False}
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['apk','sha256','bytes','saturn_games','all_other_entries_identical','installed']},ensure_ascii=False))
