from pathlib import Path
import json,re,subprocess,os,zipfile
R=Path(r'\\?\E:\ESTUDO APK\work\native-carousel\implementation\psp-integration');P=R.parent;M=R/'merged';D=M/'smali_classes17'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')[4:]
def run(*args):subprocess.run([str(x)[4:] if str(x).startswith(chr(92)*2+"?") else str(x) for x in args],check=True)
cm=json.loads((R/'class-map.json').read_text());typ=lambda n:'L'+cm.get(n,n)+';'
p=M/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=p.read_text()
if 'PspBootstrap;->initProcess' not in s:
 needle='    invoke-super {p0}, Landroid/app/Application;->onCreate()V';assert s.count(needle)==1
 s=s.replace(needle,needle+'\n    invoke-static {p0}, Lorg/emulationstation/frontend/PspBootstrap;->initProcess(Landroid/app/Application;)Z\n    move-result v7\n    if-eqz v7, :turbo_not_psp\n    return-void\n    :turbo_not_psp\n');p.write_text(s)
p=D/'org/ppsspp/ppsspp/PpssppActivity.smali';s=p.read_text()
if 'PspBootstrap;->internalDirectory' not in s:
 for name,args,target in [('getFilesDir','','internalDirectory'),('getExternalFilesDir','Ljava/lang/String;','userDirectory'),('getCacheDir','','cacheDirectory')]:
  s+='\n.method public '+name+'('+args+')Ljava/io/File;\n    .locals 1\n    invoke-static {}, Lorg/emulationstation/frontend/PspBootstrap;->'+target+'()Ljava/io/File;\n    move-result-object v0\n    return-object v0\n.end method\n'
 s+='\n.method public finish()V\n    .locals 0\n    invoke-static {}, Lorg/emulationstation/frontend/PspBootstrap;->finishing()V\n    invoke-super {p0}, Ltpspcore/appcompat/app/AppCompatActivity;->finish()V\n    return-void\n.end method\n'
 p.write_text(s,encoding='utf-8')
for p in D.rglob('*.smali'):
 s=p.read_text();t=s.replace('Landroid/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;', 'Lorg/emulationstation/frontend/PspBootstrap;->preferences(Landroid/content/Context;)Landroid/content/SharedPreferences;')
 if t!=s:p.write_text(t)
classes=R/'java-classes';classes.mkdir(exist_ok=True)
run(JAVA/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',r'G:\Android\Sdk\platforms\android-34\android.jar','-d',classes,*list((R/'java').rglob('*.java')))
jar=R/'bridge.jar'
with zipfile.ZipFile(jar,'w') as out:
 for f in classes.rglob('*.class'):out.write(f,f.relative_to(classes).as_posix())
dex=R/'bridge-dex';dex.mkdir(exist_ok=True)
run(JAVA/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',dex,jar)
print('PSP initialization, storage, settings and return bridge compiled.')
