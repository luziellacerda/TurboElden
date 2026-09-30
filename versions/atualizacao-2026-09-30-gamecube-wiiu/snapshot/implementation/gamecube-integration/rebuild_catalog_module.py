from pathlib import Path
import zipfile,hashlib,subprocess,os
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'gamecube-integration'
JAVA=r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe'
APKTOOL=r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar'
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
with zipfile.ZipFile(P/'TurboramaStation-PSP-PPSSPP-1.20.4.apk') as z,zipfile.ZipFile(R/'catalog-module.apk','w') as out:
 old=hashlib.sha256(z.read('assets/turboretro/catalog.json')).hexdigest()
 for n in ['AndroidManifest.xml','resources.arsc']:out.writestr(n,z.read(n))
 out.writestr('classes.dex',z.read('classes8.dex'))
subprocess.run([JAVA,'-jar',APKTOOL,'d','-r','-f',str(R/'catalog-module.apk'),'-o',str(R/'catalog-decoded')],check=True)
f=R/'catalog-decoded/smali/org/emulationstation/frontend/catalog/CatalogData.smali';s=f.read_text();assert old in s
f.write_text(s.replace(old,hashlib.sha256((R/'catalog-gamecube.json').read_bytes()).hexdigest()),encoding='utf-8')
subprocess.run([JAVA,'-jar',APKTOOL,'b',str(R/'catalog-decoded'),'-o',str(R/'catalog-module-built.apk')],check=True)
