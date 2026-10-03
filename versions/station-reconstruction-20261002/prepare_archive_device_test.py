from pathlib import Path
import zipfile,subprocess,binascii,shutil,json,hashlib
r=Path(__file__).resolve().parent;out=r/'build/device-archive';out.mkdir(parents=True,exist_ok=True)
(out/'fixture.bin').write_bytes(bytes(range(256))*16)
with zipfile.ZipFile(out/'valid.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(out/'fixture.bin','fixture.bin')
with zipfile.ZipFile(out/'traversal.zip','w') as z:z.writestr('../outside.bin',b'abc')
with zipfile.ZipFile(out/'symlink.zip','w') as z:
 i=zipfile.ZipInfo('link');i.create_system=3;i.external_attr=(0o120777<<16);z.writestr(i,'target')
with zipfile.ZipFile(out/'duplicate.zip','w') as z:z.writestr('Game.bin',b'abc');z.writestr('game.bin',b'def')
(out/'truncated.zip').write_bytes((out/'valid.zip').read_bytes()[:50])
lines=(r/'build/archive/libarchive-3.8.9/libarchive/test/test_read_format_rar5_stored.rar.uu').read_bytes().splitlines()
start=next(i for i,line in enumerate(lines) if line.startswith(b'begin '))+1
data=b''.join(binascii.a2b_uu(line) for line in lines[start:] if line!=b'end')
(out/'stored.rar').write_bytes(data)
subprocess.run([r'C:\Program Files\7-Zip\7z.exe','a','-t7z',str(out/'valid.7z'),str(out/'fixture.bin')],check=True,capture_output=True)
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');android=r'G:\Android\Sdk\platforms\android-34\android.jar'
classes=out/'classes';classes.mkdir(exist_ok=True)
sources=[str(p) for p in (r/'src/java/org/emulationstation/frontend/station').glob('*.java') if 'import android.' not in p.read_text()]+[str(r/'tests/StationArchiveDeviceTest.java')]
subprocess.run([str(jdk/'javac.exe'),'-encoding','UTF-8','--release','8','-cp',android,'-d',str(classes)]+sources,check=True)
jar=out/'test.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 for p in classes.rglob('*.class'):z.write(p,p.relative_to(classes).as_posix())
dex=out/'dex';dex.mkdir(exist_ok=True)
subprocess.run([str(jdk/'java.exe'),'-cp',r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',str(dex),str(jar)],check=True)
with zipfile.ZipFile(out/'archive-test.jar','w') as z:z.write(dex/'classes.dex','classes.dex')
shutil.copy2(r/'build/native/arm64-v8a/libstation_archive.so',out/'libstation_archive.so')
print('Device archive fixture build ready: '+str(out))
