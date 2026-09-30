from pathlib import Path
import json,re,subprocess,os,zipfile
R=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\ps2-integration');P=R.parent;M=R/'merged';D=M/'smali_classes15'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def run(*args):subprocess.run(list(map(str,args)),check=True)
cm=json.loads((R/'class-map.json').read_text());typ=lambda n:'L'+cm.get(n,n)+';'
p=M/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=p.read_text()
if 'Ps2Bootstrap;->initProcess' not in s:
 needle='    invoke-super {p0}, Landroid/app/Application;->onCreate()V';assert s.count(needle)==1
 s=s.replace(needle,needle+'\n    invoke-static {p0}, Lorg/emulationstation/frontend/Ps2Bootstrap;->initProcess(Landroid/app/Application;)Z\n    move-result v7\n    if-eqz v7, :turbo_not_ps2\n    return-void\n    :turbo_not_ps2\n');p.write_text(s)
for rel in ['com/armsx2/Pasx2Application','com/armsx2/Main']:
 p=D/(rel+'.smali');s=p.read_text()
 if 'Ps2Bootstrap;->internalDirectory' not in s:
  for name,args,target in [('getFilesDir','','internalDirectory'),('getExternalFilesDir','Ljava/lang/String;','userDirectory'),('getCacheDir','','cacheDirectory'),('getDataDir','','internalDirectory')]:
   s+='\n.method public '+name+'('+args+')Ljava/io/File;\n    .locals 1\n    invoke-static {}, Lorg/emulationstation/frontend/Ps2Bootstrap;->'+target+'()Ljava/io/File;\n    move-result-object v0\n    return-object v0\n.end method\n'
  s+='\n.method public getApplicationContext()Landroid/content/Context;\n    .locals 1\n    invoke-static {}, Lorg/emulationstation/frontend/Ps2Bootstrap;->applicationContext()Landroid/content/Context;\n    move-result-object v0\n    return-object v0\n.end method\n'
 if rel.endswith('Pasx2Application') and 'initEmbedded' not in s:
  s+='''
.method public static initEmbedded(Landroid/app/Application;)Landroid/content/Context;
    .locals 1
    new-instance v0, Lcom/armsx2/Pasx2Application;
    invoke-direct {v0}, Lcom/armsx2/Pasx2Application;-><init>()V
    invoke-virtual {v0, p0}, Lcom/armsx2/Pasx2Application;->attachBaseContext(Landroid/content/Context;)V
    invoke-virtual {v0}, Lcom/armsx2/Pasx2Application;->onCreate()V
    return-object v0
.end method
'''
 if rel.endswith('/Main') and 'embeddedSettings' not in s:
  s+='''
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 0
    invoke-super {p0, p1}, SUPER->onCreate(Landroid/os/Bundle;)V
    invoke-static {p0}, Lorg/emulationstation/frontend/Ps2Bootstrap;->activityReady(Landroid/app/Activity;)V
    return-void
.end method
.method public finishAndRemoveTask()V
    .locals 0
    invoke-static {p0}, Lorg/emulationstation/frontend/Ps2Bootstrap;->finishActivity(Landroid/app/Activity;)V
    return-void
.end method
.method public finishAffinity()V
    .locals 0
    invoke-static {p0}, Lorg/emulationstation/frontend/Ps2Bootstrap;->finishActivity(Landroid/app/Activity;)V
    return-void
.end method
.method public static embeddedSettings()V
    .locals 3
    new-instance v0, ROUTE
    const/4 v1, 0x0
    const/4 v2, 0x2
    invoke-direct {v0, v1, v2}, ROUTE-><init>(GAMEI)V
    invoke-static {v0}, NAV->c(IFACE)V
    return-void
.end method
.method public static embeddedAtHome()Z
    .locals 1
    sget-object v0, NAV->b:STATE
    invoke-virtual {v0}, STATE->getValue()Ljava/lang/Object;
    move-result-object v0
    instance-of v0, v0, HOME
    return v0
.end method
'''.replace('SUPER',typ('kd2')).replace('ROUTE',typ('dm')).replace('GAME',typ('ab1')).replace('IFACE',typ('fm')).replace('NAV',typ('cl4')).replace('STATE',typ('v03')).replace('HOME',typ('xl'))
 p.write_text(s,encoding='utf-8')
classes=R/'java-classes';classes.mkdir(exist_ok=True)
run(JAVA/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',r'G:\Android\Sdk\platforms\android-34\android.jar','-d',classes,*list((R/'java').rglob('*.java')))
jar=R/'bridge.jar'
with zipfile.ZipFile(jar,'w') as out:
 for f in classes.rglob('*.class'):out.write(f,f.relative_to(classes).as_posix())
dex=R/'bridge-dex';dex.mkdir(exist_ok=True)
run(JAVA/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',dex,jar)
print('PS2 initialization, storage, settings and return bridge compiled.')
