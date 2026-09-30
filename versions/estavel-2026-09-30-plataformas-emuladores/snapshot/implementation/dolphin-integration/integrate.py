from pathlib import Path
import re, shutil, subprocess, os, zipfile
R=Path(r'\\?\E:\ESTUDO APK\work\native-carousel\implementation\dolphin-integration');M=R/'merged'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')[4:]
def run(*args):subprocess.run([str(x)[4:] if str(x).startswith('\\\\?\\') else str(x) for x in args],check=True)

# The frontend Application remains unchanged in its own process.
p=M/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=p.read_text('utf-8')
if 'DolphinBootstrap;->initProcess' not in s:
    needle='    invoke-super {p0}, Landroid/app/Application;->onCreate()V'
    assert s.count(needle)==1
    s=s.replace(needle,needle+'''\n
    invoke-static {p0}, Lorg/emulationstation/frontend/DolphinBootstrap;->initProcess(Landroid/app/Application;)Z
    move-result v7
    if-eqz v7, :turbo_original_process
    return-void
    :turbo_original_process
''');p.write_text(s,'utf-8')

p=M/'smali_classes10/org/dolphinemu/dolphinemu/DolphinApplication.smali';s=p.read_text('utf-8')
if 'initEmbedded' not in s:
    s=s.replace('.method public final onCreate()V\n    .locals 1','.method public final onCreate()V\n    .locals 2')
    s=s.replace('    invoke-virtual {p0, v0}, Landroid/app/Application;->registerActivityLifecycleCallbacks(Landroid/app/Application$ActivityLifecycleCallbacks;)V','''    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;
    move-result-object v1
    check-cast v1, Landroid/app/Application;
    invoke-virtual {v1, v0}, Landroid/app/Application;->registerActivityLifecycleCallbacks(Landroid/app/Application$ActivityLifecycleCallbacks;)V''')
    s=s.replace('const-string v0, "main"','const-string v0, "dolp"')
    s+='''
.method public static initEmbedded(Landroid/app/Application;)V
    .locals 1
    new-instance v0, Lorg/dolphinemu/dolphinemu/DolphinApplication;
    invoke-direct {v0}, Lorg/dolphinemu/dolphinemu/DolphinApplication;-><init>()V
    invoke-virtual {v0, p0}, Lorg/dolphinemu/dolphinemu/DolphinApplication;->attachBaseContext(Landroid/content/Context;)V
    invoke-virtual {v0}, Lorg/dolphinemu/dolphinemu/DolphinApplication;->onCreate()V
    return-void
.end method
''';p.write_text(s,'utf-8')

p=M/'smali_classes10/org/dolphinemu/dolphinemu/utils/DirectoryInitialization.smali';s=p.read_text('utf-8')
if 'DolphinBootstrap;->userDirectory' not in s:
    s,n=re.subn(r'(?ms)^\.method public static final getUserDirectoryPath\(Landroid/content/Context;\)Ljava/io/File;.*?^\.end method','''.method public static final getUserDirectoryPath(Landroid/content/Context;)Ljava/io/File;
    .locals 1
    invoke-static {p0}, Lorg/emulationstation/frontend/DolphinBootstrap;->userDirectory(Landroid/content/Context;)Ljava/io/File;
    move-result-object v0
    return-object v0
.end method''',s);assert n==1
    for old,new in [('getFilesDir','internalDirectory'),('getExternalCacheDir','cacheDirectory'),('getCacheDir','cacheDirectory')]:
        s=re.sub(r'invoke-virtual \{(\w+)\}, Landroid/content/Context;->'+old+r'\(\)Ljava/io/File;',lambda m:'invoke-static {'+m[1]+'}, Lorg/emulationstation/frontend/DolphinBootstrap;->'+new+'(Landroid/content/Context;)Ljava/io/File;',s)
    needle='    invoke-static {}, Lorg/dolphinemu/dolphinemu/NativeLibrary;->Initialize()V'
    assert s.count(needle)==1
    s=s.replace(needle,'    invoke-static {p0}, Lorg/emulationstation/frontend/DolphinBootstrap;->migrateLegacySaves(Landroid/content/Context;)V\n\n'+needle)
    p.write_text(s,'utf-8')

J=R/'java/org/emulationstation/frontend';J.mkdir(parents=True,exist_ok=True)
stub=R/'compile-only/tdolphin/appcompat/app/AppCompatActivity.java';stub.parent.mkdir(parents=True,exist_ok=True)
stub.write_text('package tdolphin.appcompat.app; public class AppCompatActivity extends android.app.Activity {}','utf-8')
classes=R/'java-classes';classes.mkdir(exist_ok=True)
run(JAVA/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',r'G:\Android\Sdk\platforms\android-34\android.jar','-d',classes,stub,*J.glob('*.java'))
jar=R/'bridge.jar'
with zipfile.ZipFile(jar,'w') as out:
    for f in (classes/'org').rglob('*.class'):out.write(f,f.relative_to(classes).as_posix())
dex=R/'bridge-dex';dex.mkdir(exist_ok=True)
run(JAVA/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',dex,jar)
print('Bootstrap, isolated directories and upstream launch checks integrated; bridge DEX ready.')
