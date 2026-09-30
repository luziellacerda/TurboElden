from pathlib import Path
import re,subprocess,os,zipfile
R=Path(r'\\?\E:\ESTUDO APK\work\native-carousel\implementation\flycast-integration');M=R/'merged';P=R.parent
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')[4:]
def run(*args):subprocess.run([str(x)[4:] if str(x).startswith(chr(92)*2+'?') else str(x) for x in args],check=True)
p=M/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=p.read_text('utf-8')
if 'FlycastBootstrap;->initProcess' not in s:
 needle='    invoke-super {p0}, Landroid/app/Application;->onCreate()V'
 assert s.count(needle)==1
 s=s.replace(needle,needle+"\n    invoke-static {p0}, Lorg/emulationstation/frontend/FlycastBootstrap;->initProcess(Landroid/app/Application;)Z\n    move-result v7\n    if-eqz v7, :turbo_not_flycast\n    return-void\n    :turbo_not_flycast\n")
 p.write_text(s,'utf-8')
D=M/'smali_classes13'
# Keep Flycast preferences separate from the original application.
for p in D.rglob('*.smali'):
 s=p.read_text('utf-8')
 t=s.replace('Landroid/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;', 'Lorg/emulationstation/frontend/FlycastBootstrap;->preferences(Landroid/content/Context;)Landroid/content/SharedPreferences;')
 t=t.replace('"com.flycast.emulator.provider"','"org.emulationstation.frontend.flycast.provider"')
 if t!=s:p.write_text(t,'utf-8')
p=D/'com/flycast/emulator/Emulator.smali';s=p.read_text('utf-8')
if 'initEmbedded' not in s:
 s+='''
.method public static initEmbedded(Landroid/app/Application;)Landroid/content/Context;
    .locals 1
    new-instance v0, Lcom/flycast/emulator/Emulator;
    invoke-direct {v0}, Lcom/flycast/emulator/Emulator;-><init>()V
    invoke-virtual {v0, p0}, Lcom/flycast/emulator/Emulator;->attachBaseContext(Landroid/content/Context;)V
    invoke-virtual {v0}, Lcom/flycast/emulator/Emulator;->onCreate()V
    return-object v0
.end method
.method public getApplicationContext()Landroid/content/Context;
    .locals 0
    return-object p0
.end method
'''
 p.write_text(s,'utf-8')
# Files exported/imported by the official menus are confined to this emulator.
for rel in ['com/flycast/emulator/Emulator.smali','com/flycast/emulator/BaseGLActivity.smali']:
 p=D/rel;s=p.read_text('utf-8')
 if 'FlycastBootstrap;->internalDirectory' not in s:
  for name,args,target in [('getFilesDir','','internalDirectory'),('getExternalFilesDir','Ljava/lang/String;','userDirectory'),('getCacheDir','','cacheDirectory')]:
   s+='\n.method public '+name+'('+args+')Ljava/io/File;\n    .locals 1\n    invoke-static {}, Lorg/emulationstation/frontend/FlycastBootstrap;->'+target+'()Ljava/io/File;\n    move-result-object v0\n    return-object v0\n.end method\n'
 p.write_text(s,'utf-8')
p=D/'com/flycast/emulator/BaseGLActivity.smali';s=p.read_text('utf-8')
if 'FlycastBootstrap;->applicationContext' not in s:
 s+='''
.method public getApplicationContext()Landroid/content/Context;
    .locals 1
    invoke-static {}, Lorg/emulationstation/frontend/FlycastBootstrap;->applicationContext()Landroid/content/Context;
    move-result-object v0
    return-object v0
.end method
.method public finishAffinity()V
    .locals 0
    invoke-static {p0}, Lorg/emulationstation/frontend/FlycastBootstrap;->finishActivity(Landroid/app/Activity;)V
    return-void
.end method
'''
 s=s.replace('.method public onGameStateChange(Z)V\n    .locals 1','.method public onGameStateChange(Z)V\n    .locals 1\n    invoke-static {p1}, Lorg/emulationstation/frontend/FlycastBootstrap;->gameState(Z)V')
 p.write_text(s,'utf-8')
p=D/'com/flycast/emulator/NativeGLActivity.smali';s=p.read_text('utf-8')
if 'FlycastBootstrap;->activityReady' not in s:
 needle='    invoke-super {p0, p1}, Lcom/flycast/emulator/BaseGLActivity;->onCreate(Landroid/os/Bundle;)V'
 assert s.count(needle)==1
 s=s.replace(needle,needle+'\n    invoke-static {p0}, Lorg/emulationstation/frontend/FlycastBootstrap;->activityReady(Landroid/app/Activity;)V')
 p.write_text(s,'utf-8')
# Native navigation offsets are pinned to this integrated official binary.
import hashlib,json
abi=json.loads((R/'navigation-abi.json').read_text('utf-8'))
assert hashlib.sha256((M/'lib/arm64-v8a/libflycast.so').read_bytes()).hexdigest()==abi['integrated_engine_sha256']
classes=R/'java-classes';classes.mkdir(exist_ok=True)
run(JAVA/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',r'G:\Android\Sdk\platforms\android-34\android.jar','-d',classes,*list((R/'java').rglob('*.java')))
jar=R/'bridge.jar'
with zipfile.ZipFile(jar,'w') as out:
 for f in classes.rglob('*.class'):out.write(f,f.relative_to(classes).as_posix())
dex=R/'bridge-dex';dex.mkdir(exist_ok=True)
run(JAVA/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',dex,jar)
run(r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-fno-stack-protector','-mno-outline-atomics','-Wl,-z,max-page-size=16384','-Wl,-z,defs','-Wl,-soname,libturbo_flycast.so',R/'native_bridge.c','-L'+str(P)[4:],'-ldl','-lc','-llog','-o',M/'lib/arm64-v8a/libturbo_flycast.so')
print('Flycast process, storage and official settings entry integrated.')
