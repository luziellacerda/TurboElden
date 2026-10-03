from native_activity_storage import overrides
"""MD.emu complete Android frontend; isolated from the existing complete SNES."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,zipfile
S=Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003')
R=Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003')
HERE=Path(__file__).resolve().parent
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
SDK=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
AT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
os.environ['TEMP']=os.environ['TMP']=str(R)
sys.path.insert(0,r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\python')
import lief
def run(*a):subprocess.run(list(map(str,a)),check=True)
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b)
def sha(b):return hashlib.sha256(b).hexdigest()
assert sha((R/'MdEmu.zip').read_bytes())=='64f65b91a4000d4c6a5c4cdd90c733f17d2dd1dc7cb6b4220e83fb66e127580f'
with zipfile.ZipFile(R/'MdEmu-1c12fac5.apk') as md,zipfile.ZipFile(S/'Snes9xEXPlus-1c12fac5.apk') as sn:
    assert md.read('classes.dex')==sn.read('classes.dex')
    lib=md.read('lib/arm64-v8a/libmain.so')
    binary=lief.parse(list(lib));changes=[]
    # Only read-only JNI descriptor strings and the controller atlas filename.
    # Equal-size relocation; never patch executable code or symbol/hash tables.
    for old,new,expected in [(b'com/imagine',b'com/mdimagn',8),(b'gpOverlay.png',b'mdOverlay.png',1)]:
        assert len(old)==len(new) and lib.count(old)==expected
        for match in re.finditer(re.escape(old),lib):
            offset=match.start()
            section=next(s for s in binary.sections if s.offset<=offset and offset+len(old)<=s.offset+s.size)
            assert section.name=='.rodata' and not (int(section.flags)&4)
            changes.append(dict(offset=offset,old=old.decode(),new=new.decode(),section=section.name))
    adapted=lib.replace(b'com/imagine',b'com/mdimagn').replace(b'gpOverlay.png',b'mdOverlay.png')
    assert len(adapted)==len(lib)
    allowed={x['offset']+i for x in changes for i in range(len(x['old']))}
    assert all(i in allowed for i,(a,b) in enumerate(zip(lib,adapted)) if a!=b)
    (R/'libmdemu_station.so').write_bytes(adapted)
    (R/'mdOverlay.png').write_bytes(md.read('assets/gpOverlay.png'))
    for n in md.namelist():
        if n.startswith('assets/') and n!='assets/gpOverlay.png':assert md.read(n)==sn.read(n),n
    (R/'native-relocations.json').write_text(json.dumps(dict(official_sha256=sha(lib),integrated_sha256=sha(adapted),changes=changes,executable_code_identical=True),indent=2)+'\n')

for original,target in [(S/'official-decoded',R/'donor-merged'),(S/'host-merged',R/'host-merged'),(S/'manifest-decoded',R/'manifest-decoded')]:
    if not target.exists():shutil.copytree(original,target)
M=R/'donor-merged';H=R/'host-merged'
original=S/'official-decoded/smali';mapping={}
for f in original.rglob('*.smali'):
    c=re.search(r'^\.class (?:.* )?(L[^;]+;)',f.read_text('utf-8'),re.M)[1]
    mapping[c]=c.replace('Lcom/imagine/','Lcom/mdimagn/') if c.startswith('Lcom/imagine/') else 'Ltsmd/'+c[1:]
for f in original.rglob('*.smali'):
    s=f.read_text('utf-8')
    for old,new in mapping.items():
        s=s.replace(old,new).replace('"'+old[1:-1].replace('/','.')+'"','"'+new[1:-1].replace('/','.')+'"')
    (M/'smali'/f.relative_to(original)).write_text(s,'utf-8')
(R/'shading.json').write_text(json.dumps(mapping,indent=2)+'\n')
p=M/'smali/com/imagine/BaseActivity.smali';s=p.read_text('utf-8');bridge='Lorg/emulationstation/frontend/MegaBootstrap;'
for name in ['filesDir','cacheDir']:
    s,count=re.subn(rf'\.method public {name}\(\)Ljava/lang/String;.*?\.end method',f'''.method public {name}()Ljava/lang/String;
    .locals 1
    invoke-static {{p0}}, {bridge}->{name}(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method''',s,flags=re.S);assert count==1
s=once(s,'.method public intentDataPath()Ljava/lang/String;\n    .locals 4',f'''.method public intentDataPath()Ljava/lang/String;
    .locals 4
    invoke-static {{p0}}, {bridge}->consumeGamePath(Landroid/app/Activity;)Ljava/lang/String;
    move-result-object v0
    if-eqz v0, :station_original_intent
    return-object v0
    :station_original_intent''')
s=once(s,'    invoke-super {p0}, Landroid/app/NativeActivity;->onDestroy()V',f'    invoke-static {{p0}}, {bridge}->beforeDestroy(Landroid/app/Activity;)V\n    invoke-super {{p0}}, Landroid/app/NativeActivity;->onDestroy()V')
s += overrides('MegaBootstrap')
p.write_text(s,'utf-8')
p=H/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=(S/'host-merged/smali/org/yuzu/yuzu_emu/YuzuApplication.smali').read_text('utf-8')
s=once(s,'    invoke-super {p0}, Landroid/app/Application;->onCreate()V',f'''    invoke-super {{p0}}, Landroid/app/Application;->onCreate()V
    invoke-static {{p0}}, {bridge}->initProcess(Landroid/app/Application;)Z
    move-result v7
    if-eqz v7, :station_not_mega
    return-void
    :station_not_mega''');p.write_text(s,'utf-8')
p=R/'manifest-decoded/AndroidManifest.xml';s=(S/'manifest-decoded/AndroidManifest.xml').read_text('utf-8')
s=once(s,'    </application>','''        <activity android:name="com.mdimagn.BaseActivity" android:label="MD.emu"
            android:exported="false" android:process=":megadrive" android:launchMode="singleInstance"
            android:excludeFromRecents="true" android:enableOnBackInvokedCallback="false" android:screenOrientation="sensorLandscape"
            android:configChanges="mcc|mnc|locale|touchscreen|keyboard|keyboardHidden|navigation|orientation|screenLayout|uiMode|screenSize|smallestScreenSize|fontScale"
            android:theme="@android:style/Theme.NoTitleBar">
            <meta-data android:name="android.app.lib_name" android:value="mdemu_station"/>
        </activity>
    </application>''');p.write_text(s,'utf-8')

n=R/'native';n.mkdir(exist_ok=True)
for f in (S/'native').iterdir():
    if f.suffix=='.h' or f.name in ['native_carousel.cpp','libc.so','libdl.so','liblog.so']:shutil.copy2(f,n/f.name)
source=(S/'native/native_snes.h').read_text('utf-8')
source=re.sub(r'static bool snesCore.*?(?=static jclass)', '''static bool snesCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"mdemu_station")||strcmp(s,"Mega Drive")==0||strcmp(s,"MegaDrive")==0||
        strcmp(s,"MegaDrive - BR")==0||strcmp(s,"megadrive")==0||strcmp(s,"megadrivebr")==0;
}
''',source,flags=re.S)
source=source.replace('snes','mega').replace('Snes','Mega').replace('SNES','MEGA')
source=source.replace('refreshRunHook','snesRunHook').replace('refreshDefinitionsHook','snesDefinitionsHook').replace('refreshSettingsHook','snesSettingsHook').replace('Mega9x EX+','MD.emu').replace(':mega process',':megadrive process')
source+='''
static UiString gamecubeCommandHook(const void*);
static UiString megaCommandHook(const void*folder){
 const char*key=strData(folder);
 if(presentationKeyEqual(key,"MegaDrive")||presentationKeyEqual(key,"MegaDrive - BR")||
    presentationKeyEqual(key,"Mega Drive")||presentationKeyEqual(key,"megadrive")||
    presentationKeyEqual(key,"megadrivebr")||presentationKeyEqual(key,"genesis")){
  UiString result={};strAssign(&result,"libretro: core=mdemu_station.so");return result;
 }
 return gamecubeCommandHook(folder);
}
static bool megaFreshHook(const void*c){return megaCore(c)?false:refreshFreshHook(c);}
static bool megaBundledHook(const void*c){return megaCore(c)?true:refreshBundledHook(c);}
static bool megaInstalledHook(void*p,const void*c){return megaCore(c)?true:refreshInstalledHook(p,c);}
static bool megaAssetsHook(void*p,const void*c){return megaCore(c)?true:refreshAssetsHook(p,c);}
static bool megaPackHook(const void*c,void*u,void*p){if(!megaCore(c))return refreshPackHook(c,u,p);strAssign(u,"");strAssign(p,"");return false;}
'''
(n/'native_mega.h').write_text(source,'utf-8')
p=n/'native_carousel.cpp';s=p.read_text('utf-8');s=once(s,'#include "native_snes.h"','#include "native_snes.h"\n#include "native_mega.h"')
for off,old,new in [('0x1888e0','gamecubeCommandHook','megaCommandHook'),('0x2a9718','snesRunHook','megaRunHook'),('0x2a6850','snesDefinitionsHook','megaDefinitionsHook'),('0x2228f8','snesSettingsHook','megaSettingsHook')]:s=once(s,f'{{{off},(void*){old}}}',f'{{{off},(void*){new}}}')
for off,name in [('0x2a89a8','Fresh'),('0x2a87d8','Bundled'),('0x18b098','Installed'),('0x18aaf0','Assets'),('0x18a8a8','Pack')]:s=once(s,f'{{{off},(void*)refresh{name}Hook}}',f'{{{off},(void*)mega{name}Hook}}')
p.write_text(s,'utf-8')

java=R/'java';shutil.copytree(HERE/'java',java,dirs_exist_ok=True);classes=R/'java-classes';classes.mkdir(exist_ok=True)
run(J/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',SDK,'-d',classes,*java.rglob('*.java'))
with zipfile.ZipFile(R/'bridge.jar','w') as z:
    for f in classes.rglob('*.class'):z.write(f,f.relative_to(classes).as_posix())
dex=R/'bridge-dex';dex.mkdir(exist_ok=True)
run(J/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',SDK,'--output',dex,R/'bridge.jar')
for project,output in [(H,'host-module.apk'),(M,'mega-module.apk'),(R/'manifest-decoded','manifest-module.apk')]:
    run(J/'java.exe','-jar',AT,'b','-p',S/'framework','-o',R/output,project)
run(r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26',
    '--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot',
    '-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2',
    '-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs',
    '-Wl,-soname,libturbo_carousel.so',n/'native_carousel.cpp','-L',n,'-lc','-ldl','-llog','-o',n/'libturbo_carousel.so')
print('MD.emu complete interface and native routing compiled.')
