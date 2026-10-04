from pathlib import Path
import subprocess,zipfile,hashlib,json,os
r=Path(__file__).resolve().parent;jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
out=Path(os.environ.get('STATION_BUILD_DIR',str(r/'build')));classes=out/'android-classes';package=out/'station-client.jar'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(classes.rglob('*.class')):z.write(p,p.relative_to(classes).as_posix())
dex=out/'dex';dex.mkdir(exist_ok=True)
subprocess.run([str(jdk/'java.exe'),'-cp',r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',str(dex),str(package)],check=True)
manifest='<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.emulationstation.frontend.station"><uses-sdk android:minSdkVersion="26"/><uses-permission android:name="android.permission.INTERNET"/></manifest>'
with zipfile.ZipFile(out/'station-client.aar','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('AndroidManifest.xml',manifest);z.write(package,'classes.jar');z.writestr('R.txt','')
with zipfile.ZipFile(out/'station-client-sources.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted((r/'src').rglob('*')):
  if p.is_file():z.write(p,p.relative_to(r).as_posix())
 for p in sorted((r/'tests').glob('*')):
  if p.is_file():z.write(p,p.relative_to(r).as_posix())
 for name in ['run_tests.py','build_module.py','prepare_test_dependency.py','tools/json-dependency.json','platform-evidence.json','HANDOFF-RECONSTRUCAO-TURBOSTATIONS.md','HANDOFF-SERVIDOR-CONEXAO-E-INSTALACAO.md','HANDOFF-CAPAS-20261003.md']:
  if (r/name).is_file():z.write(r/name,name)
report={}
for file in [package,out/'station-client.aar',dex/'classes.dex',out/'station-client-sources.zip']:
 data=file.read_bytes();report['build/'+file.relative_to(out).as_posix()]={'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
(out/'module-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
