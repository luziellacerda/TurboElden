from native_activity_storage import overrides
"""Build complete EX+ integration against the frozen 3b355b02 Station APK.
Inputs are private/local; never run old whole-application packaging recipes.
"""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, zipfile

R = Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003')
HERE = Path(__file__).resolve().parent
JDK = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
APKTOOL = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
SDK = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
os.environ['TMP'] = os.environ['TEMP'] = str(R)
def run(*args): subprocess.run(list(map(str, args)), check=True)
def sha(path):
    with open(path, 'rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)

assert sha(R/'Snes9xEXPlus.zip') == 'dac0074094b37ba92743a894893f7ca8a5ee0e941e569e93dffdde24f4f783fe'
assert sha(R/'native/recovered-stable.so') == '523eb3b3c87c53834ea172091aa2c9826874e7a3956077b1269069901283da24'

# Working copies keep donor and recovered baseline available for comparison.
M = R/'donor-merged'
if not M.exists(): shutil.copytree(R/'official-decoded', M)
H = R/'host-merged'
if not H.exists(): shutil.copytree(R/'host-decoded', H)

# Shade every obfuscated helper, avoiding duplicate definitions in existing DEX.
original = R/'official-decoded/smali'
mapping = {}
for f in original.rglob('*.smali'):
    descriptor = re.search(r'^\.class (?:.* )?(L[^;]+;)', f.read_text('utf-8'), re.M)[1]
    if descriptor.startswith(('La/', 'Lb/', 'Lc/', 'Landroid/support/')):
        mapping[descriptor] = 'Ltsnes/' + descriptor[1:]
for f in original.rglob('*.smali'):
    text = f.read_text('utf-8')
    for old, new in mapping.items():
        text = text.replace(old, new)
        text = text.replace('"'+old[1:-1].replace('/', '.')+'"', '"'+new[1:-1].replace('/', '.')+'"')
    target = M/'smali'/f.relative_to(original)
    target.write_text(text, 'utf-8')
(R/'shading.json').write_text(json.dumps(mapping, indent=2))

p = M/'smali/com/imagine/BaseActivity.smali'
s = p.read_text('utf-8')
bridge = 'Lorg/emulationstation/frontend/SnesBootstrap;'
for name in ('filesDir', 'cacheDir'):
    pattern = rf'\.method public {name}\(\)Ljava/lang/String;.*?\.end method'
    replacement = f'''.method public {name}()Ljava/lang/String;
    .locals 1
    invoke-static {{p0}}, {bridge}->{name}(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method'''
    s, count = re.subn(pattern, replacement, s, flags=re.S)
    assert count == 1
s = once(s, '.method public intentDataPath()Ljava/lang/String;\n    .locals 4',
    f'''.method public intentDataPath()Ljava/lang/String;
    .locals 4
    invoke-static {{p0}}, {bridge}->consumeGamePath(Landroid/app/Activity;)Ljava/lang/String;
    move-result-object v0
    if-eqz v0, :station_original_intent
    return-object v0
    :station_original_intent''')
s = once(s, '    invoke-super {p0}, Landroid/app/NativeActivity;->onDestroy()V',
    f'    invoke-static {{p0}}, {bridge}->beforeDestroy(Landroid/app/Activity;)V\n'
    '    invoke-super {p0}, Landroid/app/NativeActivity;->onDestroy()V')
s += overrides('SnesBootstrap')
p.write_text(s, 'utf-8')

p = H/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali'
s = (R/'host-decoded/smali/org/yuzu/yuzu_emu/YuzuApplication.smali').read_text('utf-8')
s = once(s, '    invoke-super {p0}, Landroid/app/Application;->onCreate()V',
    f'''    invoke-super {{p0}}, Landroid/app/Application;->onCreate()V
    invoke-static {{p0}}, {bridge}->initProcess(Landroid/app/Application;)Z
    move-result v7
    if-eqz v7, :station_not_snes
    return-void
    :station_not_snes''')
p.write_text(s, 'utf-8')

p = R/'manifest-decoded/AndroidManifest.xml'
s = p.read_text('utf-8')
if 'com.imagine.BaseActivity' not in s:
    s = once(s, '    </application>', '''        <activity android:name="com.imagine.BaseActivity"
            android:label="Snes9x EX+" android:exported="false" android:process=":snes"
            android:launchMode="singleInstance" android:excludeFromRecents="true"
            android:enableOnBackInvokedCallback="false" android:screenOrientation="sensorLandscape"
            android:configChanges="mcc|mnc|locale|touchscreen|keyboard|keyboardHidden|navigation|orientation|screenLayout|uiMode|screenSize|smallestScreenSize|fontScale"
            android:theme="@android:style/Theme.NoTitleBar">
            <meta-data android:name="android.app.lib_name" android:value="snes9x_explus"/>
        </activity>
    </application>''')
    p.write_text(s, 'utf-8')

# Native routing: inherited helper implementation, chained into verified stable hooks.
n = R/'native'
source = (n/'native_flycast.h').read_text('utf-8')
source = source[source.index('static bool flycastCore'):]
source = re.sub(r'static bool flycastCore\(.*?\n\}', '''static bool flycastCore(const void*id){
 const char*s=strData(id);
 return uiContains(s,"snes9x")||strcmp(s,"Super Nintendo")==0||
        strcmp(s,"Super Nintendo - BR")==0||strcmp(s,"snes")==0||strcmp(s,"snesbr")==0;
}''', source, count=1, flags=re.S)
source = re.sub(r'static bool flycastFreshHook.*?(?=static bool flycastDefinitionsHook)', '', source, flags=re.S)
source = source.replace('flycast', 'snes').replace('Flycast', 'Snes').replace('FLYCAST', 'SNES')
source = source.replace('dolphinRunHook', 'refreshRunHook').replace('dolphinSettingsHook', 'refreshSettingsHook').replace('dolphinDefinitionsHook', 'refreshDefinitionsHook')
source = source.replace('Snes v2.7-44', 'Snes9x EX+ 1.5.85').replace('Snes integrado', 'Snes9x EX+ integrado')
(n/'native_snes.h').write_text('// Official EX+ UI/controls, own :snes process. No Libretro SNES launch.\n'+source, 'utf-8')
p = n/'native_carousel.cpp'
s = p.read_text('utf-8')
if '#include "native_snes.h"' not in s:
    s = once(s, '#include "native_pcecd.h"', '#include "native_pcecd.h"\n#include "native_snes.h"')
    for offset, name in [('0x2a9718','Run'), ('0x2a6850','Definitions'), ('0x2228f8','Settings')]:
        s = once(s, f'{{{offset},(void*)refresh{name}Hook}}', f'{{{offset},(void*)snes{name}Hook}}')
    p.write_text(s, 'utf-8')

classes = R/'java-classes'; classes.mkdir(exist_ok=True)
java = R/'java'; shutil.copytree(HERE/'java', java, dirs_exist_ok=True)
run(JDK/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',SDK,'-d',classes,*java.rglob('*.java'))
with zipfile.ZipFile(R/'bridge.jar','w') as out:
    for f in classes.rglob('*.class'):out.write(f,f.relative_to(classes).as_posix())
dex = R/'bridge-dex'; dex.mkdir(exist_ok=True)
run(JDK/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',SDK,'--output',dex,R/'bridge.jar')
for project, output in [(H,'host-module.apk'),(M,'snes-module.apk'),(R/'manifest-decoded','manifest-module.apk')]:
    run(JDK/'java.exe','-jar',APKTOOL,'b','-p',R/'framework','-o',R/output,project)
run(r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26',
    '--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot',
    '-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2',
    '-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs',
    '-Wl,-soname,libturbo_carousel.so',n/'native_carousel.cpp','-L',n,'-lc','-ldl','-llog','-o',n/'libturbo_carousel.so')
print('SNES bridge, complete upstream UI, manifest and native routing built.')
