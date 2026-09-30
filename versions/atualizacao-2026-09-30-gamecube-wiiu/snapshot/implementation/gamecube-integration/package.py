from pathlib import Path
import zipfile,hashlib,json,subprocess,os,shutil,datetime,struct,zlib
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'gamecube-integration'
BASE=P/'TurboramaStation-PSP-PPSSPP-1.20.4.apk';OUT=P/'TurboramaStation-GameCube-Dolphin.apk'
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15');JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def sha(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(BASE)=='3631c668ad127e523b50163867f4ea6feb67dd835dd80639658eeddaac9bf897'
replacements={'assets/turboretro/catalog.json':R/'catalog-gamecube.json','lib/arm64-v8a/libturbo_carousel.so':P/'libturbo_carousel.so','assets/turbo-system-videos/720-gc.mp4':R/'720-gc.mp4'}
# Reassemble the catalog DEX so string IDs remain correctly sorted.
with zipfile.ZipFile(R/'catalog-module-built.apk') as z:
 dex=z.read('classes.dex');assert sha(R/'catalog-gamecube.json').encode() in dex
 (R/'classes8.dex').write_bytes(dex)
 replacements['classes8.dex']=R/'classes8.dex'
for n in ['native_carousel.cpp','system_video720_assets.h','system_infos.h']:
 replacements['assets/gamecube-integration/source/'+n]=P/n
source=json.loads((R/'cache-atual-catalogo.json').read_text())
provenance={'platform':'GameCube','games':37,'covers':37,'source':'User-provided local catalog cache 2026-09-30','source_sha256':sha(R/'cache-atual-catalogo.json'),'core':'Dolphin 2609-7 already integrated','rom_folder':'gamecube','native_command':'libretro: core=dolphin_libretro_android.so','video_asset':'turbo-system-videos/720-gc.mp4','video_source':r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas\gc.mp4','visibility_mapping':{'Android':True,'R2Pasta':'gamecube','CatalogLabel':'roms','AndroidPackage':'same as original RequiredPackage','AndroidDemo':'same as original Demo','AndroidMensal':'same as original Mensal'},'source_access_metadata_preserved':True,'remote_availability_checked':False,'game_runtime_verified':False}
(R/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
replacements['assets/gamecube-integration/provenance.json']=R/'provenance.json'
unsigned=R/'gamecube-unsigned.apk';aligned=R/'gamecube-aligned.apk'
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
 seen=set()
 for info in z.infolist():
  n=info.filename
  if n.startswith('META-INF/'):continue
  with (replacements[n].open('rb') if n in replacements else z.open(n)) as src,out.open(info,'w') as dst:shutil.copyfileobj(src,dst,1024*1024)
  seen.add(n)
 for n,f in replacements.items():
  if n not in seen:out.write(f,n,compress_type=zipfile.ZIP_STORED if n.endswith('.mp4') else zipfile.ZIP_DEFLATED)
def run(*a):subprocess.run(list(map(str,a)),check=True)
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink()
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',os.environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',os.environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
 for n in a.namelist():
  if n.startswith('META-INF/') or n in replacements:continue
  with a.open(n) as x,b.open(n) as y:assert hashlib.file_digest(x,'sha256').digest()==hashlib.file_digest(y,'sha256').digest(),n
 old=json.loads(a.read('assets/turboretro/catalog.json'));new=json.loads(b.read('assets/turboretro/catalog.json'))
 assert new[:-1]==old and new[-1]['Name']=='GameCube' and len(new[-1]['Files'])==37
 original=next(c for c in source if c['Name']=='GameCube')
 assert new[-1]['Files']==original['Files']
 for k in ['Id','Name','DefaultSubPath','RequiredPackage','Demo','Mensal']:assert new[-1][k]==original[k]
 assert b.getinfo('assets/turbo-system-videos/720-gc.mp4').compress_type==zipfile.ZIP_STORED
record={'apk':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,'base_sha256':sha(BASE),'native_sha256':sha(P/'libturbo_carousel.so'),'games':37,'covers':37,'other_catalog_categories_preserved':len(old),'unchanged_dex':'all except reassembled classes8.dex with updated catalog SHA256','other_engine_binaries_byte_identical':True,'catalog_sha256':sha(R/'catalog-gamecube.json'),'installed':False,'runtime_verified':False,'built_at':datetime.datetime.now().astimezone().isoformat(),'changed':list(replacements)}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
