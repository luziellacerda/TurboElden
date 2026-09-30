from pathlib import Path
import hashlib,json,os,subprocess,zipfile
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'search-download-ui'
BASE=P/'TurboramaStation-loading-progresso.apk';OUT=P/'TurboramaStation-pesquisa-downloads.apk'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())=='0d5a0dccfa1a404759b93d9a32623a102b85e03dca240af0083a9bf04637226b'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
(R/'tmp').mkdir(exist_ok=True);os.environ['TMP']=os.environ['TEMP']=str(R/'tmp')
module='lib/arm64-v8a/libturbo_carousel.so';lib=(P/'libturbo_carousel.so').read_bytes()
unsigned=R/'ui-unsigned.apk';aligned=R/'ui-aligned.apk'
def run(*args):subprocess.run(list(map(str,args)),check=True)
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
    for info in z.infolist():
        if info.filename.startswith('META-INF/'):continue
        out.writestr(info,lib if info.filename==module else z.read(info.filename))
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink()
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
    names={n for n in a.namelist() if not n.startswith('META-INF/')}
    assert names=={n for n in b.namelist() if not n.startswith('META-INF/')}
    changed=sorted(n for n in names if sha(a.read(n))!=sha(b.read(n)))
    assert changed==[module],changed
aligned.unlink()
report=dict(apk=str(OUT),sha256=sha(OUT.read_bytes()),bytes=OUT.stat().st_size,
    base=str(BASE),base_sha256=sha(BASE.read_bytes()),changed=changed,
    reference='User request: native search and ALL download notices',reference_component='GuiStore search, keyboard, messages, toast and transfer progress',
    native_module_sha256=sha(lib),session_dex_identical=True,all_other_dex_identical=True,
    emulator_engines_identical=True,media_identical=True,installed=False,visual_check_performed=False,
    promoted_to_stable=False)
(R/'build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
profile_path=P/'stable-design/active-profile.json'
profile=json.loads(profile_path.read_text(encoding='utf-8'))
profile.update(latest_built_apk=str(OUT),latest_built_apk_sha256=report['sha256'],installation_pending=True,current_revision_promoted_to_stable=False)
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
