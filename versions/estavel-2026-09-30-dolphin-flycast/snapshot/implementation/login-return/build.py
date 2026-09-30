from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
R=Path(__file__).resolve().parent;P=R.parent
ap=argparse.ArgumentParser()
ap.add_argument('--base-apk',type=Path,default=P/'TurboramaStation-abrir-destaque.apk')
ap.add_argument('--base-sha256',default='437e5ad3690e8318194e5bda9dcec197910dfd2245f522da9007a3a07f71682d')
a=ap.parse_args();BASE=a.base_apk;OUT=P/'TurboramaStation-retorno-logado.apk'
assert BASE.resolve()!=OUT.resolve()
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
SDK=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
APKTOOL=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
os.environ['TMP']=os.environ['TEMP']=str(R/'tmp')
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):subprocess.run(list(map(str,args)),check=True)
def apktool(*args):run(JAVA,'-Djava.io.tmpdir='+str(R/'tmp'),'-jar',APKTOOL,*args)
def wrapper(path,dex):
    with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(path,'w') as out:
        for n in ['AndroidManifest.xml','resources.arsc']:out.writestr(n,z.read(n))
        out.writestr('classes.dex',dex)
assert sha(BASE.read_bytes())==a.base_sha256
for folder in ['tmp','classes','dex']:(R/folder).mkdir(exist_ok=True)
with zipfile.ZipFile(BASE) as z: wrapper(R/'original-login.apk',z.read('classes8.dex'))
apktool('d','-r','-f','-p',R/'framework','-o',R/'decoded',R/'original-login.apk')
PACKAGE=Path('org/emulationstation/frontend/auth')
original=R/'decoded/smali'/PACKAGE
original_files={p.relative_to(R/'decoded/smali').as_posix():p.read_bytes() for p in (R/'decoded/smali').rglob('*.smali')}
# Keep the existing password verifier private and unchanged. Only its fingerprint is used.
revision=sha((original/'LocalPassword.smali').read_bytes())
template=R/'java'/PACKAGE/'AuthSession.java.template'
source=R/'java'/PACKAGE/'AuthSession.java'
source.write_text(template.read_text(encoding='utf-8').replace('__PASSWORD_REVISION__','authenticated-v1:'+revision),encoding='utf-8')
run(JAVA.with_name('javac.exe'),'-encoding','UTF-8','-source','8','-target','8','-cp',SDK,'-d',R/'classes',source,R/'compile-stubs'/PACKAGE/'LocalPassword.java')
run(JAVA,'-Djava.io.tmpdir='+str(R/'tmp'),'-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',SDK,'--output',R/'dex',R/'classes'/PACKAGE/'AuthSession.class')
wrapper(R/'session-only.apk',(R/'dex/classes.dex').read_bytes())
apktool('d','-r','-f','-p',R/'framework','-o',R/'session-decoded',R/'session-only.apk')
shutil.copy2(R/'session-decoded/smali'/PACKAGE/'AuthSession.smali',original/'AuthSession.smali')
login=original/'LoginActivity.smali';s=login.read_text(encoding='utf-8')
assert '->attach(Landroid/content/Context;)V' not in s, 'Already patched: select unpatched visual base'
for method in ['ensureAuthorized(Landroid/app/Activity;)V','onCreate(Landroid/os/Bundle;)V']:
    pattern=r'(?m)^\.method [^\n]*'+re.escape(method)+r'\n[\s\S]*?^\.end method'
    match=re.search(pattern,s);assert match,method
    text=match.group()
    if method.startswith('ensureAuthorized'):
        anchor='    invoke-static {}, Lorg/emulationstation/frontend/auth/AuthSession;->isAuthorized()Z'
        assert text.count(anchor)==1
        text=text.replace(anchor,'    invoke-static {p0}, Lorg/emulationstation/frontend/auth/AuthSession;->attach(Landroid/content/Context;)V\n\n'+anchor,1)
    else:
        anchor='    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V'
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+'\n\n    invoke-static {p0}, Lorg/emulationstation/frontend/auth/AuthSession;->attach(Landroid/content/Context;)V',1)
    s=s[:match.start()]+text+s[match.end():]
login.write_text(s,encoding='utf-8')
changed_smali=[]
for rel,data in original_files.items():
    now=(R/'decoded/smali'/rel).read_bytes()
    if data!=now:changed_smali.append(rel)
assert sorted(changed_smali)==sorted([(PACKAGE/'AuthSession.smali').as_posix(),(PACKAGE/'LoginActivity.smali').as_posix()])
apktool('b','-p',R/'framework','-o',R/'patched-login.apk',R/'decoded')
with zipfile.ZipFile(R/'patched-login.apk') as z:dex=z.read('classes.dex')
unsigned=R/'return-unsigned.apk';aligned=R/'return-aligned.apk'
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
    for info in z.infolist():
        if info.filename.startswith('META-INF/'):continue
        out.writestr(info,dex if info.filename=='classes8.dex' else z.read(info.filename))
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink()
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
with zipfile.ZipFile(BASE) as before,zipfile.ZipFile(OUT) as after:
    names={n for n in before.namelist() if not n.startswith('META-INF/')}
    assert names=={n for n in after.namelist() if not n.startswith('META-INF/')}
    changed=sorted(n for n in names if sha(before.read(n))!=sha(after.read(n)))
    assert changed==['classes8.dex'],changed
aligned.unlink()
report=dict(apk=str(OUT),sha256=sha(OUT.read_bytes()),bytes=OUT.stat().st_size,
    base=str(BASE),base_sha256=a.base_sha256,changed=changed,changed_auth_classes=changed_smali,
    password_validator_unchanged=True,engines_unchanged=True,native_button_and_media_preserved=True,
    persistence='AES-256-GCM; AndroidKeyStore; noBackupFilesDir; only after existing LocalPassword.matches accepts',
    first_login_required=True,installed=False,runtime_return_verified=False,
    stable_tag_preserved='estavel-2026-09-29-playlist-retro',promoted_to_stable=False)
(R/'build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
