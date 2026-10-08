from pathlib import Path
import json,hashlib,subprocess,re,sys,datetime
SNAPSHOT=Path(__file__).resolve().parents[2]
ROOT=SNAPSHOT/'java'
TEST=Path(__file__).resolve().parent
OUTPUT=Path(r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\session-tests-final')
OUTPUT.mkdir(parents=True,exist_ok=True)
(OUTPUT/'temp').mkdir(exist_ok=True)
BASE=Path(r'E:\ESTUDO APK\work\station-recovery-handshake-r73-20261007-build\java')
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
HELPER=Path(r'C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git\versions\station-collection-videos-r67-20261007\tests\MemoryCompile.java')
JSON=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
ANDROID=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
PROD=ROOT/'netplay-src/org/emulationstation/frontend/netplay'
checks=[]
def check(name,value):
    if not value: raise AssertionError(name)
    checks.append(name)
def between(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
def compile(name,sources,cp,tests=()):
    args=[str(JAVA),'-Djava.io.tmpdir='+str(OUTPUT/'temp'),str(HELPER),cp]+list(tests)
    r=subprocess.run(args,input='\n'.join(map(str,sources)),text=True,encoding='utf-8',capture_output=True,timeout=40)
    out=r.stdout+r.stderr;(OUTPUT/(name+'.log')).write_text(out,encoding='utf-8')
    print(out)
    if r.returncode:raise RuntimeError(name+' failed')
    return out
s={f.stem:f.read_text(encoding='utf-8') for f in PROD.glob('*.java')}
a=s['StationRetroActivity'];l=s['StationSessionLink'];v=s['StationSessionService'];o=s['StationGameSession'];r=s['StationSessionRegistry'];rooms=s['StationRoomsActivity']
check('real Messenger IPC', 'new Messenger(binder)' in l and 'new Messenger(handler)' in v)
check('important bound dependency', 'Context.BIND_AUTO_CREATE|Context.BIND_IMPORTANT' in l)
check('explicit private service target', 'new Intent(activity,StationSessionService.class)' in l)
for forbidden in ['startService(', 'startForeground(', 'START_STICKY','WakeLock','ESActivity','GuiStore','setWebViewClient']:
    check('service does not '+forbidden,forbidden not in v+l)
check('sender UID server','message.sendingUid!=android.os.Process.myUid()' in v)
check('sender UID client','message.sendingUid!=android.os.Process.myUid()' in l)
check('exact session registry','anchors.find(key,room,generation)' in o)
check('single outstanding launch','!entries.isEmpty()' in r)
check('registry uses private nonce','UUID.randomUUID().toString()' in o)
check('new attach starts before startActivity',rooms.index('StationGameSession.attach(this,room')<rooms.index('startActivityForResult(nativeIntent'))
check('native return identity saved','out.putBundle("station.nativeReturn",nativeReturn.save())' in rooms)
check('native return identity restored','nativeReturn.restore(saved==null?null:saved.getBundle("station.nativeReturn"))' in rooms)
check('callback exact local completion','if(nativeReturn.completed(requestCode))' in rooms)
check('result code never remote leave','command(' not in between(rooms,'@Override protected void onActivityResult','private int dp('))
check('pending native result blocks second launch','if(launching||nativeReturn.pending()||key.equals(launchKey))return;' in rooms)
check('failed launch cleanup','StationGameSession.discardLaunch(nativeIntent' in rooms)
check('all transports behind owner ack','if(!ownerReady||!visible||sessionFinished)return;' in a)
check('one transport worker set','if(!transportStarted){transportStarted=true;if(recovery!=null)recovery.start();if(relay!=null)relay.start();}' in a)
check('not started during create','recovery.start()' not in between(a,'@Override public void onCreate','@Override protected void onStart'))
check('keep bind while stopped','sessionLink.close()' not in between(a,'@Override protected void onStop','private boolean notified'))
check('retain v2 presence on stop','if(!recovery)pause();' in o)
check('human quit sent before native quit',a.index('closeSession();',a.index('private void requestHumanExit'))<a.index('stationRequestQuit()',a.index('private void requestHumanExit')))
check('JNI true waits normal native exit','if(stationRequestQuit())return;' in a)
check('destroy releases link','sessionLink.close();sessionLink=null;' in a)
check('callback guarded after close','if(sessionFinished||isFinishing()||isDestroyed())return;ownerReady=true' in a)
check('callbacks ignored once link closed','if(closed||connection==null||!connection.bound||service==null' in l)
check('binding failure cleans resources','connection=null;unbind(next);listener.unavailable("BIND_UNAVAILABLE")' in l)
check('binding exception cleans resources','connection=null;unbind(next);listener.unavailable("BIND_FAILED")' in l)
check('disconnect is not unbind','unbind(' not in between(l,'@Override public void onServiceDisconnected','@Override public void onBindingDied'))
check('death listener registered','peer.linkToDeath(claim,0)' in v)
check('no remote terminal on local release','event(6' not in between(o,'synchronized void anchorEnded','private static ResultReceiver createOwner'))
check('explicit human allowed after cleanup',o.index('if(event==4)')<o.index('if(closed||failed)return'))
check('explicit terminal allowed after cleanup',o.index('if(event==6')<o.index('if(closed||failed)return'))
check('grant coalescing','ticketScheduled.compareAndSet(false,true)' in o and 'finally{ticketScheduled.set(false);}' in o)
check('native status/tunnel unchanged', not (PROD/'StationRecoveryTunnel.java').exists())
check('no global device settings', all(x not in a+l+v+o for x in ['Settings.Global','Settings.System','force-stop','killProcess','setThreadPriority']))
full={str(f.relative_to(BASE)).lower():f for f in BASE.rglob('*.java')}
for f in (ROOT/'netplay-src').rglob('*.java'):full[str(f.relative_to(ROOT)).lower()]=f
production=compile('production-api34-compile',list(full.values()),str(ANDROID)+';'+str(JSON))
fixtures=list((TEST/'fixture-src').rglob('*.java'))+[PROD/(x+'.java') for x in ['StationSessionRegistry','StationSessionService','StationSessionLink','StationGameSession']]+[TEST/'StationSessionRegistryTest.java',TEST/'StationSessionLifecycleTest.java']
local=compile('lifecycle-fixture',fixtures,str(JSON),('org.emulationstation.frontend.netplay.StationSessionRegistryTest','org.emulationstation.frontend.netplay.StationSessionLifecycleTest'))
receipt={'sourceGuards':checks,'sourceGuardCount':len(checks),'productionSourceCount':len(full),'localChecks':sum(map(int,re.findall(r': (\d+) checks passed',local))),'scope':'API34 compilation and JVM fixtures; no Android freezer, phone, network, APK or gameplay test','sha256':{str(f.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'netplay-src').rglob('*.java'))}}
receipt['createdUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt['baseSha256']={str(f.relative_to(ROOT)).replace('\\','/'):(hashlib.sha256((BASE/f.relative_to(ROOT)).read_bytes()).hexdigest() if (BASE/f.relative_to(ROOT)).exists() else None) for f in sorted((ROOT/'netplay-src').rglob('*.java'))}
(OUTPUT/'test-receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('source guards:',len(checks),'local checks:',receipt['localChecks'])
