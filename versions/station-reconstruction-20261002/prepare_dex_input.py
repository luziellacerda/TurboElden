from pathlib import Path
import zipfile,hashlib,subprocess,os
r=Path(__file__).resolve().parent
apk=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk')
with apk.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b'
work=r/'build/dex-integration';work.mkdir(parents=True,exist_ok=True)
(r/'input').mkdir(exist_ok=True);(r/'temp').mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(r/'temp')
java=r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe'
tool=r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar'
with zipfile.ZipFile(apk) as z:
 for lib in ['main','SDL2','turbo_carousel','c++_shared']:(r/'input'/('lib'+lib+'.so')).write_bytes(z.read('lib/arm64-v8a/lib'+lib+'.so'))
 for dex in ['classes5.dex','classes6.dex','classes8.dex','classes28.dex']:
  mini=work/(dex+'.apk')
  with zipfile.ZipFile(mini,'w') as out:
   for name in ['AndroidManifest.xml','resources.arsc']:out.writestr(name,z.read(name))
   out.writestr('classes.dex',z.read(dex))
  subprocess.run([java,'-Djava.io.tmpdir='+str(r/'temp'),'-jar',tool,'d','-f','-r','-p',str(work/'framework'),'-o',str(work/(dex+'-decoded')),str(mini)],check=True)
print('Exact APK native inputs and DEX trees prepared')
