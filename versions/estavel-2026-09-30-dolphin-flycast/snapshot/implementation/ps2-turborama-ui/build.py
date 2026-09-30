from pathlib import Path
import hashlib,json,os,subprocess,zipfile,shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'ps2-turborama-ui'
BASE=P/'TurboramaStation-abrir-lzgames.apk';OUT=P/'TurboramaStation-ps2-visual-turborama.apk'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())=='d9518d5c6359e27ce8c31c287c78de3700d56d85efc801da37660f9575198f10'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
SDK=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
APKTOOL=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
for name in ['tmp','classes','dex']:(R/name).mkdir(exist_ok=True)
os.environ['TMP']=os.environ['TEMP']=str(R/'tmp')
def run(*args):subprocess.run(list(map(str,args)),check=True)
def apktool(*args):run(JAVA,'-Djava.io.tmpdir='+str(R/'tmp'),'-jar',APKTOOL,*args)
def wrapper(path,dex):
    with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(path,'w') as out:
        for n in ['AndroidManifest.xml','resources.arsc']:out.writestr(n,z.read(n))
        out.writestr('classes.dex',dex)
with zipfile.ZipFile(BASE) as z:wrapper(R/'original-loader.apk',z.read('classes5.dex'))
apktool('d','-r','-f','-p',R/'framework','-o',R/'decoded',R/'original-loader.apk')
PACKAGE=Path('org/emulationstation/frontend')
smali=R/'decoded/smali'
before={p.relative_to(smali).as_posix():p.read_bytes() for p in smali.rglob('*.smali')}
run(JAVA.with_name('javac.exe'),'-encoding','UTF-8','-source','8','-target','8','-cp',SDK,'-d',R/'classes',R/'java'/PACKAGE/'LoadingOverlay.java')
classes=sorted((R/'classes'/PACKAGE).glob('LoadingOverlay*.class'));assert classes
run(JAVA,'-Djava.io.tmpdir='+str(R/'tmp'),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',SDK,'--output',R/'dex',*classes)
wrapper(R/'loading-only.apk',(R/'dex/classes.dex').read_bytes())
apktool('d','-r','-f','-p',R/'framework','-o',R/'loading-decoded',R/'loading-only.apk')
for path in (smali/PACKAGE).glob('LoadingOverlay*.smali'):
    assert path.resolve().parent==(smali/PACKAGE).resolve()
    path.unlink()
for path in (R/'loading-decoded/smali'/PACKAGE).glob('LoadingOverlay*.smali'):shutil.copy2(path,smali/PACKAGE/path.name)
after={p.relative_to(smali).as_posix():p.read_bytes() for p in smali.rglob('*.smali')}
changed_classes=sorted(n for n in set(before)|set(after) if before.get(n)!=after.get(n))
assert changed_classes and all(n.startswith('org/emulationstation/frontend/LoadingOverlay') for n in changed_classes)
apktool('b','-p',R/'framework','-o',R/'patched-loader.apk',R/'decoded')
with zipfile.ZipFile(R/'patched-loader.apk') as z:dex=z.read('classes.dex')
module='lib/arm64-v8a/libturbo_carousel.so';lib=(P/'libturbo_carousel.so').read_bytes()
replacements={'classes5.dex':dex,module:lib}
unsigned=R/'ui-unsigned.apk';aligned=R/'ui-aligned.apk'
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
    for info in z.infolist():
        if info.filename.startswith('META-INF/'):continue
        out.writestr(info,replacements[info.filename] if info.filename in replacements else z.read(info.filename))
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned);unsigned.unlink()
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
    names={n for n in a.namelist() if not n.startswith('META-INF/')}
    assert names=={n for n in b.namelist() if not n.startswith('META-INF/')}
    changed=sorted(n for n in names if sha(a.read(n))!=sha(b.read(n)))
    assert changed==sorted(replacements),changed
aligned.unlink()
r=dict(apk=str(OUT),sha256=sha(OUT.read_bytes()),bytes=OUT.stat().st_size,base=str(BASE),base_sha256=sha(BASE.read_bytes()),
    changed=changed,changed_loader_classes=changed_classes,authentication_dex_identical=True,
    emulator_engines_identical=True,media_identical=True,native_module_sha256=sha(lib),installed=False,
    visual_check_performed=False,runtime_navigation_verified=False,promoted_to_stable=False,
    scope='Existing game loading view and native Libretro pause/exit menu; includes PS2; Switch-specific menu unchanged')
(R/'build-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,ensure_ascii=False,indent=2))
