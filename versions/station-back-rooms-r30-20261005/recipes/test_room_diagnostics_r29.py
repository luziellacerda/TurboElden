from pathlib import Path
import subprocess,json,hashlib,shutil,os
W=Path(r'E:\ESTUDO APK\work\station-room-diagnostics-r29-20261005')
S=W/'netplay-src/org/emulationstation/frontend/netplay';T=W/'tests';stub=T/'stubs';out=T/'classes';out.mkdir(exist_ok=True)
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');JSON=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
os.environ['TEMP']=os.environ['TMP']=str(T)
stubs={
'android/content/Context.java':'package android.content; public class Context {public android.content.res.AssetManager getAssets(){return null;} public android.content.pm.ApplicationInfo getApplicationInfo(){return null;}}',
'android/content/res/AssetManager.java':'package android.content.res; public class AssetManager {public java.io.InputStream open(String name)throws java.io.IOException {throw new java.io.IOException("unused");}}',
'android/content/pm/ApplicationInfo.java':'package android.content.pm; public class ApplicationInfo {public String nativeLibraryDir;}',
'org/emulationstation/frontend/station/StationApi.java':'package org.emulationstation.frontend.station; public class StationApi {public static class Cancellation {public void check()throws java.io.IOException{}}}',
'org/emulationstation/frontend/station/StationFrontend.java':'package org.emulationstation.frontend.station; public class StationFrontend {public static java.io.IOException failure;public static String path;public static String installedPathForItem(String id)throws java.io.IOException{if(failure!=null)throw failure;return path;}}',
'org/emulationstation/frontend/station/StationPlatforms.java':'package org.emulationstation.frontend.station; public class StationPlatforms {public String folder;public static StationPlatforms resolve(String raw){StationPlatforms p=new StationPlatforms();p.folder=raw;return p;}}',
'org/emulationstation/frontend/station/StationCatalog.java':'package org.emulationstation.frontend.station; public class StationCatalog {public static class Item {public String name,platform;}}',
'org/emulationstation/frontend/netplay/StationOnlineClient.java':'package org.emulationstation.frontend.netplay; class StationOnlineClient {org.emulationstation.frontend.station.StationCatalog.Item item(String id){return null;}}'
}
for name,source in stubs.items():
 p=stub/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(source,'utf8')
shutil.copyfile(Path(__file__).parent/'room-r29/StationRoomsRegressionTest.java',T/'StationRoomsRegressionTest.java')
shutil.copyfile(Path(__file__).parent/'lobby-r27/StationCompactLobbyTest.java',T/'StationCompactLobbyTest.java')
production=[S/n for n in ['StationRoomStartState.java','StationRoomFeedback.java','StationOnlineGame.java','StationInvitationCode.java','StationPlayerModel.java','StationRoomState.java']]
sources=production+list(stub.rglob('*.java'))+[T/'StationRoomsRegressionTest.java',T/'StationCompactLobbyTest.java']
subprocess.run([str(J/'javac.exe'),'-encoding','UTF-8','--release','8','-cp',str(JSON),'-d',str(out),*[str(p) for p in sources]],check=True)
logs=[]
for name in ['StationRoomsRegressionTest','StationCompactLobbyTest']:
 r=subprocess.run([str(J/'java.exe'),'-cp',str(out)+';'+str(JSON),'org.emulationstation.frontend.netplay.'+name,str(T)],capture_output=True,text=True,encoding='utf8')
 (W/'evidence'/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');print(r.stdout+r.stderr);r.check_returncode();logs.append(r.stdout.strip())
baseline=json.loads((W/'evidence/baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[Path(n).name for n,h in baseline.items() if sha(W/n)!=h]
assert set(changed)=={'StationOnlineGame.java','StationRoomsActivity.java'},changed
code=(S/'StationRoomsActivity.java').read_text('utf8')
assert 'feedback.text(snapshot,busy)' in code and 'feedback.fail(StationOnlineClient.message(error))' in code
assert 'updateStartState();peerScroll.post' in code and 'String changed=StationRoomStartState.reason(state.get())' in code
record={'passed':True,'logs':logs,'changedProductionFiles':changed,'sourceHashes':{str(p.relative_to(W)):sha(p) for p in production},'scope':'Real Java readiness/feedback/game-file boundary with Android/frontend stubs; UI and real-server Android actions recorded separately.'}
(W/'evidence/tests.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
