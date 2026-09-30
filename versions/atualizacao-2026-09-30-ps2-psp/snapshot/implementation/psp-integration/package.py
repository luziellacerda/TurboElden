from pathlib import Path
import hashlib,json,os,subprocess,zipfile,datetime
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'psp-integration'
BASE=P/'TurboramaStation-PS2-ARMSX2-2.7.2.apk';OUT=P/'TurboramaStation-PSP-PPSSPP-1.20.4.apk'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp');sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())=='6e76035e9943896bc7ff0044047749f5c4781821210e2953d697221bdd769911'
removed=set()
replacements={}
with zipfile.ZipFile(R/'merged-template.apk') as z:
 for n in z.namelist():
  if n in ['AndroidManifest.xml','resources.arsc','classes.dex','classes17.dex'] or n.startswith('res/') or (n.startswith('assets/') and not n.startswith('assets/dexopt/')):replacements[n]=z.read(n)
for f in (R/'merged/lib/arm64-v8a').glob('*.so'):replacements['lib/arm64-v8a/'+f.name]=f.read_bytes()
replacements['lib/arm64-v8a/libturbo_carousel.so']=(P/'libturbo_carousel.so').read_bytes()
replacements['classes18.dex']=(R/'bridge-dex/classes.dex').read_bytes()
for f in [R/'prepare.py',R/'integrate.py',R/'package.py',P/'native_psp.h']:
 replacements['assets/psp-integration/source/'+f.name]=f.read_bytes()
for f in (R/'java').rglob('*.java'):replacements['assets/psp-integration/source/'+f.relative_to(R/'java').as_posix()]=f.read_bytes()
assert not (set(replacements)&removed)
unsigned=R/'psp-unsigned.apk';aligned=R/'psp-aligned.apk'
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
 seen=set()
 for info in z.infolist():
  n=info.filename
  if n.startswith('META-INF/') or n in removed:continue
  out.writestr(info,replacements.get(n,z.read(n)));seen.add(n)
 for n,b in replacements.items():
  if n not in seen:out.writestr(n,b,compress_type=zipfile.ZIP_STORED if n.endswith(('.so','.dex','.arsc')) else zipfile.ZIP_DEFLATED)
def run(*a):subprocess.run(list(map(str,a)),check=True)
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink()
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',os.environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',os.environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
 for n in a.namelist():
  if n.startswith('META-INF/') or n in removed or n in replacements:continue
  assert a.read(n)==b.read(n),n
 for i in range(2,17):assert a.read('classes'+str(i)+'.dex')==b.read('classes'+str(i)+'.dex')
 for n in a.namelist():
  if n.startswith('lib/') and n not in removed and not n.endswith('/libturbo_carousel.so'):assert a.read(n)==b.read(n),n
 assert not any(n in b.namelist() for n in removed)
 changed=[n for n in a.namelist() if n in b.namelist() and not n.startswith('META-INF/') and a.read(n)!=b.read(n)]
 added=sorted(set(b.namelist())-set(a.namelist()))
record={'apk':str(OUT),'sha256':sha(OUT.read_bytes()),'bytes':OUT.stat().st_size,'base_sha256':sha(BASE.read_bytes()),'native_module_sha256':sha((P/'libturbo_carousel.so').read_bytes()),'official_version':'PPSSPP 1.20.4','upstream_engine_rebuilt':False,'integration_compiled':True,'installed':False,'runtime_verified':False,'promoted_to_stable':False,'built_at':datetime.datetime.now().isoformat(),'removed':sorted(removed),'changed':changed,'added':added,'preserved_classes':'classes2.dex through classes16.dex','other_engines_byte_identical':True}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['changed','added']},ensure_ascii=False,indent=2))
