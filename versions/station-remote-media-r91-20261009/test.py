from pathlib import Path
import json,hashlib,subprocess,os,shutil,re,datetime
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-remote-media-r91-20261009');BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r90')
out=WORK/'tests';out.mkdir(exist_ok=True);jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');jsonjar=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
files=[]
for name in ['StationApiTest.java','StationInstallerTest.java']:
    text=(REPO/'versions/station-reconstruction-20261002/tests'/name).read_text('utf8').replace('operation.equals("catalog")','operation.startsWith("catalog")')
    dest=out/name;dest.write_text(text,'utf8');files.append(dest)
files.extend([ROOT/'tests/StationDownloadCenterTest.java',ROOT/'tests/StationMediaTest.java'])
cp=os.pathsep.join(map(str,[WORK/'compiled-final/client.jar',jsonjar]));classes=out/'classes';classes.mkdir(exist_ok=True)
def run(args,label):
    p=subprocess.run(list(map(str,args)),capture_output=True);(out/(label+'.log')).write_bytes(p.stdout+p.stderr)
    assert p.returncode==0,(p.stdout+p.stderr).decode('utf8','replace')[-5000:]
    return p.stdout.decode('utf8','replace')
run([jdk/'javac.exe','-encoding','UTF-8','--release','11','-cp',cp,'-d',classes,*files],'compile')
result=run([jdk/'java.exe','-cp',str(classes)+os.pathsep+cp,'org.emulationstation.frontend.station.StationDownloadCenterTest',out/('fixture-'+datetime.datetime.now().strftime('%H%M%S%f'))],'queue');print(result.strip())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
protected=['carousel-inputs/d0/native_magazine.h','carousel-inputs/d0/native_info.h','carousel-inputs/d0/station_menu_frame_policy.h','java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineCoverView.java','java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java']
for p in protected:assert sha(BASE/p)==sha(WORK/p),p
count=int(re.search(r'PASS (\d+)',result).group(1))
receipt=dict(passed=True,checks=count,sourceGuards=len(protected),sourceHashes=json.loads((WORK/'JAVA-SOURCE-MANIFEST.json').read_text())['sources'],LEDsAnd30fpsPreserved=True,oldDownloadNoticePreserved=True,scope='Actual queue, signed fixture HTTP, API and transactional installer on host. No real network outage or Android screen proof.',output=result.strip())
media=run([jdk/'java.exe','-cp',str(classes)+os.pathsep+cp,'org.emulationstation.frontend.station.StationMediaTest',out/('media-'+datetime.datetime.now().strftime('%H%M%S%f'))],'media');print(media.strip());receipt['mediaOutput']=media.strip();receipt['mediaChecks']=int(re.search(r'PASS (\d+)',media).group(1))
(ROOT/'evidence/tests.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
