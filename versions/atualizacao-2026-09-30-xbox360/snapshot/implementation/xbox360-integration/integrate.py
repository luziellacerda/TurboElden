from pathlib import Path
import json,re,subprocess,os,zipfile
R=Path(r'\\?\E:\ESTUDO APK\work\native-carousel\implementation\xbox360-integration');P=R.parent;M=R/'merged';D=M/'smali_classes21'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')[4:]
def run(*args):subprocess.run([str(x)[4:] if str(x).startswith(chr(92)*2+"?") else str(x) for x in args],check=True)
cm=json.loads((R/'class-map.json').read_text())
p=M/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=p.read_text()
needle='    invoke-super {p0}, Landroid/app/Application;->onCreate()V';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    invoke-static {p0}, Lorg/emulationstation/frontend/Xbox360Bootstrap;->initProcess(Landroid/app/Application;)Z\n    move-result v7\n    if-eqz v7, :turbo_not_xbox360\n    return-void\n    :turbo_not_xbox360\n');p.write_text(s)
p=D/'xendroid/compose/Application.smali';s=p.read_text().replace('"compose"','"Xbox360"')
s+='\n.method public static initEmbedded(Landroid/app/Application;)V\n .locals 1\n new-instance v0, Lxendroid/compose/Application;\n invoke-direct {v0}, Lxendroid/compose/Application;-><init>()V\n invoke-virtual {v0, p0}, Lxendroid/compose/Application;->attachEmbedded(Landroid/content/Context;)V\n invoke-virtual {v0}, Lxendroid/compose/Application;->onCreate()V\n return-void\n.end method\n.method public attachEmbedded(Landroid/content/Context;)V\n .locals 0\n invoke-super {p0, p1}, Landroid/app/Application;->attachBaseContext(Landroid/content/Context;)V\n return-void\n.end method\n'
p.write_text(s)
# Isolate XenDroid data files and preferences from all other engines.
for p in D.rglob('*.smali'):
 s=p.read_text();t=s.replace('"'+':emu'+'"','"'+':xbox360emu'+'"')
 for method,args,target in [('getFilesDir','','files'),('getExternalFilesDir','Ljava/lang/String;','userFiles'),('getCacheDir','','cache')]:
  t=re.sub(r'invoke-virtual(.*?)Landroid/content/Context;->'+method+r'\('+args+r'\)Ljava/io/File;',r'invoke-static\1Lorg/emulationstation/frontend/Xbox360Bootstrap;->'+target+'(Landroid/content/Context;'+args+')Ljava/io/File;',t)
 t=re.sub(r'invoke-virtual(.*?)Landroid/content/Context;->getSharedPreferences\(Ljava/lang/String;I\)Landroid/content/SharedPreferences;',r'invoke-static\1Lorg/emulationstation/frontend/Xbox360Bootstrap;->preferences(Landroid/content/Context;Ljava/lang/String;I)Landroid/content/SharedPreferences;',t)
 if t!=s:p.write_text(t)
import xml.etree.ElementTree as ET
A='{http://schemas.android.com/apk/res/android}'
p=M/'AndroidManifest.xml';tree=ET.parse(p);app=tree.getroot().find('application')
ET.SubElement(app,'activity',{A+'name':'org.emulationstation.frontend.Xbox360EntryActivity',A+'process':':xbox360',A+'exported':'false',A+'screenOrientation':'userLandscape',A+'theme':'@android:style/Theme.Material.NoActionBar',A+'taskAffinity':'org.emulationstation.frontend'})
ET.SubElement(app,'activity',{A+'name':'org.emulationstation.frontend.Xbox360GameEntryActivity',A+'process':':xbox360emu',A+'exported':'false',A+'screenOrientation':'userLandscape',A+'theme':'@android:style/Theme.Material.NoActionBar',A+'taskAffinity':'org.emulationstation.frontend'})
tree.write(p,encoding='utf-8',xml_declaration=True)
import hashlib
p=M/'smali_classes8/org/emulationstation/frontend/catalog/CatalogData.smali';s=p.read_text();old=hashlib.sha256((R/'catalog-before.json').read_bytes()).hexdigest();new=hashlib.sha256((R/'catalog-xbox360.json').read_bytes()).hexdigest();assert old in s;p.write_text(s.replace(old,new))
classes=R/'java-classes';classes.mkdir(exist_ok=True)
run(JAVA/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',r'G:\Android\Sdk\platforms\android-34\android.jar','-d',classes,*list((R/'java').rglob('*.java')))
jar=R/'bridge.jar'
with zipfile.ZipFile(jar,'w') as out:
 for f in classes.rglob('*.class'):out.write(f,f.relative_to(classes).as_posix())
dex=R/'bridge-dex';dex.mkdir(exist_ok=True)
run(JAVA/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',dex,jar)
print('Xbox 360 initialization, isolated storage and return bridge compiled.')
