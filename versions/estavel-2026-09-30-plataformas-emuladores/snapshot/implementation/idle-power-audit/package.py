from pathlib import Path
import hashlib,json,os,subprocess,zipfile,datetime,copy,struct
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'idle-power-audit'
BASE=P/'TurboramaStation-Xbox360-XenDroid-0b11201.apk';OUT=P/'TurboramaStation-Plataformas-Organizadas.apk'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp');sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())=='929339aeb74a3460cc44f2ec4cc0aa461dca581c2c75dd30b8ace4a52ff9c7a1'
replacements={
 'lib/arm64-v8a/libturbo_carousel.so':(P/'libturbo_carousel.so').read_bytes(),
 'assets/turbo-system-videos/720-jaguar.mp4':(P/'system-videos-missing/720-jaguar.mp4').read_bytes(),
}
for f in [P/'native_carousel.cpp',P/'system_video720_assets.h',P/'system-videos-missing/media-manifest.json',R/'package.py']:
 replacements['assets/platform-layout-update/source/'+f.name]=f.read_bytes()
for name in ['native_skin.h','native_space.h','native_space3d.h','native_laser.h','native_system_video720.h','native_wiiu.h','native_xbox360.h']:
 replacements['assets/idle-power-update/source/'+name]=(P/name).read_bytes()
with zipfile.ZipFile(P/'xbox360-integration/merged-template.apk') as template,zipfile.ZipFile(BASE) as base_zip:
 assert template.read('resources.arsc')==base_zip.read('resources.arsc'),'Resource table changed: manifest-only replacement must preserve resource IDs'
 replacements['AndroidManifest.xml']=template.read('AndroidManifest.xml')
 replacements['classes21.dex']=template.read('classes21.dex')
for part in ['wiiu-integration','xbox360-integration']:
 replacements['assets/provider-startup-fix/source/'+part+'-prepare.py']=(P/part/'prepare.py').read_bytes()
replacements['assets/provider-startup-fix/source/xbox360-integrate.py']=(P/'xbox360-integration/integrate.py').read_bytes()
removed=set()
aligned=R/'platforms-aligned.apk'
# Write ZIP entries with their final Android alignment to avoid an extra full-size temporary APK.
def write_aligned(out,entry,data):
 info=copy.copy(entry) if isinstance(entry,zipfile.ZipInfo) else zipfile.ZipInfo(entry)
 if not isinstance(entry,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if entry.endswith(('.so','.dex','.arsc','.mp4')) else zipfile.ZIP_DEFLATED
 if info.filename.startswith('assets/') and info.filename.endswith('.mp4'):info.compress_type=zipfile.ZIP_STORED
 info.extra=b''
 if info.compress_type==zipfile.ZIP_STORED:
  alignment=16384 if info.filename.endswith('.so') else 4
  offset=out.fp.tell()+30+len(info.filename.encode('utf-8'))
  if offset%alignment:
   pad=(-(offset+4))%alignment;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
 out.writestr(info,data)
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(aligned,'w',allowZip64=True) as out:
 seen=set()
 for info in z.infolist():
  n=info.filename
  if n.startswith('META-INF/') or n in removed:continue
  write_aligned(out,info,replacements[n] if n in replacements else z.read(n));seen.add(n)
 for n,b in replacements.items():
  if n not in seen:write_aligned(out,n,b)
def run(*a):subprocess.run(list(map(str,a)),check=True)
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
aligned.unlink()
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
 for n in a.namelist():
  if n.startswith('META-INF/') or n in removed or n in replacements:continue
  assert a.read(n)==b.read(n),n
 for n in a.namelist():
  if (n.endswith('.dex') and n!='classes21.dex') or (n.startswith('lib/') and not n.endswith('/libturbo_carousel.so')):assert a.read(n)==b.read(n),n
 assert a.read('assets/turboretro/catalog.json')==b.read('assets/turboretro/catalog.json')
 changed=[n for n in a.namelist() if n in b.namelist() and not n.startswith('META-INF/') and a.read(n)!=b.read(n)]
 added=sorted(set(b.namelist())-set(a.namelist()))
record={'apk':str(OUT),'sha256':sha(OUT.read_bytes()),'bytes':OUT.stat().st_size,'base_sha256':sha(BASE.read_bytes()),'native_module_sha256':sha((P/'libturbo_carousel.so').read_bytes()),'update':'Fix protected Wii U/Xbox360 DocumentsProvider export and Xbox folder shortcut authority; remove stars and aircraft model/textures/hull/depth/exhaust; suspend hidden background/laser; reduce repeated JNI work; clear Wii U/Xbox360 labels; keep videos720p60 and manufacturer order','upstream_engine_rebuilt':False,'integration_compiled':True,'installed':False,'runtime_verified':False,'promoted_to_stable':False,'built_at':datetime.datetime.now().isoformat(),'removed':sorted(removed),'changed':changed,'added':added,'preserved_classes':'all DEX byte identical except classes21 Xbox file-provider authority literal','other_engines_byte_identical':True}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['changed','added']},ensure_ascii=False,indent=2))
