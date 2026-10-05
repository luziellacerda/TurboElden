from pathlib import Path
import subprocess,json,hashlib,shutil,datetime,os
W=Path(r'E:\ESTUDO APK\work\station-compact-lobby-r27-20261005');S=W/'netplay-src/org/emulationstation/frontend/netplay';T=W/'tests';out=T/'host';out.mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(W)
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');JSON=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
shutil.copyfile(Path(__file__).resolve().parent.parent/'tests/StationCompactLobbyTest.java',T/'StationCompactLobbyTest.java')
sources=[S/n for n in ['StationInvitationCode.java','StationPlayerModel.java','StationRoomState.java']]+[T/'StationCompactLobbyTest.java']
subprocess.run([str(J/'javac.exe'),'-encoding','UTF-8','--release','8','-cp',str(JSON),'-d',str(out),*[str(p) for p in sources]],check=True)
result=subprocess.check_output([str(J/'java.exe'),'-cp',str(out)+';'+str(JSON),'org.emulationstation.frontend.netplay.StationCompactLobbyTest'],text=True,encoding='utf8')
checks=[]
def check(name,v):checks.append({'name':name,'passed':bool(v)});assert v,name
baseline=json.loads((W/'evidence/baseline.json').read_text())['files'];changed=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,h in baseline.items():
 if sha(W/path)!=h:changed.append(Path(path).name)
check('only rooms presentation and actionable error messages changed',set(changed)=={'StationRoomsActivity.java','StationOnlineClient.java'})
current={str(p.relative_to(W)) for d in ['netplay-src','dependency-src'] for p in (W/d).rglob('*.java')}
check('only three new production classes',{Path(p).name for p in current-set(baseline)}=={'StationInvitationCode.java','StationPlayerModel.java','StationPlayerSheet.java'})
code=(S/'StationRoomsActivity.java').read_text('utf8');start=code.index('private void renderPlayers(');end=code.index('private void closeSheets(',start);rows=code[start:end]
check('no cards or avatar in contact rows','card(' not in rows and 'avatar' not in rows)
check('whole row opens profile','line.setOnClickListener(v->showPlayer(id,name))' in rows)
check('48dp row touch target','new LinearLayout.LayoutParams(-1,dp(48))' in rows)
check('no invite button on rows','"invite"' not in rows and 'Convidar' not in rows)
check('search page scope explicit','Filtrar nomes desta página' in code)
check('callbacks tied to current lifecycle','if(active&&generation==epoch)' in code and 'closeSheets();super.onStop()' in code)
check('no stale room state protection removed','snapshot.optLong("revision")<latest.optLong("revision")' in code)
check('created room comes from actual response','own=current.optJSONObject("room")' in code and 'client.call(prepared.fields(StationOnlineClient.command("create"))' in code)
check('invites use existing signed client command','StationOnlineClient.command("invite").put("roomId",own.getString("roomId")).put("peerId",id)' in code)
check('codes use existing join preparation','join(parsed.roomId,parsed.itemId)' in code and 'StationOnlineGame.prepare(this,client,itemId,state.get(),cancel)' in code)
check('server restart invalidates old locator','parsed.instance.equals(snapshot.optString("instance"))' in code)
check('on stop cancels requests', 'epoch++;cancelAll();closeSheets()' in code)
check('no production fake peers','new JSONObject().put("peerId"' not in code)
check('code dialog scrollable','body.addView(outer,new ScrollView.LayoutParams(-1,-2))' in code)
check('profile dialog scrollable','scroll.addView(content' in (S/'StationPlayerSheet.java').read_text('utf8'))
check('baseline reproduces installed DEX',json.loads((W/'build/baseline/result.json').read_text())['dexSHA256']=='8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae')
record={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'javaOutput':result.strip(),'checks':checks,'baselineChanged':changed,'sourceHashes':{str(p.relative_to(W)):sha(p) for p in sources},'scope':'Executable JVM model/code tests and source preservation. Not Android visual or two-device gameplay validation.','passed':True}
(W/'evidence/tests.json').write_text(json.dumps(record,indent=2)+'\n','utf8');print(result.strip());print(str(len(checks))+' preservation/policy checks passed')
