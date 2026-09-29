from pathlib import Path
import hashlib,json,os,subprocess,zipfile
R=Path(__file__).resolve().parent;P=R.parent
BASE=P/'TurboramaStation-ESTAVEL-6727ab7-sobrevoo.apk'
APK=P/'TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
sha=lambda data:hashlib.sha256(data).hexdigest()
assert sha(BASE.read_bytes())=='e00b0e941907bbe646f1829806c266cada3e53394fd3636da52a473b5cf39174'
lib=P/'libturbo_carousel.so';module='lib/arm64-v8a/libturbo_carousel.so'
assert sha(lib.read_bytes())!=sha((R/'before/libturbo_carousel.so').read_bytes())
unsigned=R/'motion-unsigned.apk';aligned=R/'motion-aligned.apk'
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
 for info in z.infolist():
  if info.filename.startswith('META-INF/'):continue
  out.writestr(info,lib.read_bytes() if info.filename==module else z.read(info.filename))
def run(*args):subprocess.run(list(map(str,args)),check=True)
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',APK,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',APK)
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(APK) as b:
 names={n for n in a.namelist() if not n.startswith('META-INF/')}
 assert names=={n for n in b.namelist() if not n.startswith('META-INF/')}
 changed=sorted(n for n in names if a.read(n)!=b.read(n))
 assert changed==[module],changed
report=dict(apk=str(APK),sha256=sha(APK.read_bytes()),bytes=APK.stat().st_size,
 base=str(BASE),base_sha256=sha(BASE.read_bytes()),stable_commit='6727ab7',
 changed=changed,added=[],removed=[],all_emulator_engines_identical=True,
 all_dex_identical=True,icon_and_approved_login_identical=True,
 catalog_and_download_code_unchanged=True,installed=False,
 native_module_sha256=sha(lib.read_bytes()),visual_check_performed=False)
(R/'build-result.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
