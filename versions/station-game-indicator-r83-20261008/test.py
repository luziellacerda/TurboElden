from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-game-indicator-r83-20261008')
src=WORK/'java/client/src/java/org/emulationstation/frontend/station/StationGamePlayerFacts.java'
out=WORK/'tests';out.mkdir(exist_ok=True)
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
cmd=[str(jdk/'javac.exe'),'-encoding','UTF-8','--release','8','-d',str(out),str(ROOT/'tests/StationCatalog.java'),str(ROOT/'tests/PlayerFactsTest.java'),str(ROOT/'tests/Log.java'),str(src)]
r=subprocess.run(cmd,capture_output=True);assert r.returncode==0,r.stderr.decode('utf8','replace')
r=subprocess.run([str(jdk/'java.exe'),'-cp',str(out),'org.emulationstation.frontend.station.PlayerFactsTest'],capture_output=True);assert r.returncode==0,r.stderr.decode('utf8','replace');print(r.stdout.decode())
room=(WORK/'java/netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java').read_text()
assert 'heroFactDetail+"\\n\\n"' in room and 'heroOnlineDetail=StationOnlineClient.message(unavailable);renderHeroPlayerInfo();' in room
assert 'heroOnlinePlayers=b;heroOnlineDetail=d;renderHeroPlayerInfo();' in room
# No descriptive helper is imported/referenced by admission/transport code.
allowed={'StationGamePlayerFacts.java','StationCatalogPlayerEvidence.java','StationCatalogPlayerEvidenceLoader.java','StationRoomsActivity.java'}
for p in (WORK/'java').rglob('*.java'):
 if 'StationGamePlayerFacts' in p.read_text(encoding='utf8'):assert p.name in allowed,p
records=json.loads((ROOT.parents[1]/'audits/player-counts-20261008/manual-review.json').read_text())['records']
for row in records:
 if row['itemId'] in src.read_text():assert row['name'] in src.read_text()
result={'passed':True,'checks':int(r.stdout.decode().strip().split('=')[-1]),'integrationGuards':4,'scope':'descriptive facts, bindings, immutable publication, source-only UI guards; no Android gameplay',
 'factsSHA256':hashlib.sha256(src.read_bytes()).hexdigest()}
(ROOT/'evidence/tests.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
