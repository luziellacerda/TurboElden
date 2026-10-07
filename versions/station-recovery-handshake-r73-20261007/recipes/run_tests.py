"""Repeat all R71 executable fixtures on the final R73 sources, plus room-profile regressions."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys
from build_candidate import verified_sources,sha,require,SNAPSHOT,DEFAULT_WORK

p=argparse.ArgumentParser();p.add_argument('--workspace',default=DEFAULT_WORK);args=p.parse_args()
w=Path(args.workspace);require(w.drive.upper()=='E:','E: workspace required')
repo=SNAPSHOT.parent.parent;r71=SNAPSHOT.parent/'station-online-layout-r71-20261007'
previous=json.loads((r71/'evidence/local-tests.json').read_text('utf8'))
baseline,overlay,sources,manifest=verified_sources()
source_hashes={n:sha(f) for n,f in sorted(sources.items())}
build=json.loads((w/'evidence/build.json').read_text('utf8'))
require(build['sourceHashes']==source_hashes and build['sourceCount']==198,'Tests must bind all compiled R72 sources')
for module in ['client','rooms']:
    require(sha(w/'java/build'/f'{module}-dex/classes.dex')==build[module+'DexSHA256'],'DEX mismatch')
tests=[]
for name,digest in previous['testSourceHashes'].items():
    f=repo/name;require(sha(f)==digest,'Frozen fixture changed '+name);tests.append(f)
new=SNAPSHOT.parent/'station-native-registration-r72-20261007/tests/StationOwnRoomProfilesTest.java';tests.append(new)
tests.append(SNAPSHOT/'tests/wait_DiagnosticsTest.java')
classes=previous['testClasses']+['org.emulationstation.frontend.netplay.StationOwnRoomProfilesTest','org.emulationstation.frontend.netplay.wait_DiagnosticsTest']
helper=SNAPSHOT.parent/'station-collection-videos-r67-20261007/tests/MemoryCompile.java'
require(sha(helper)==previous['memoryCompilerSHA256'],'Memory test compiler changed')
java=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
android=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
jsonjar=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
require(sha(java)==previous['javaExecutableSHA256'],'JDK changed')
require(sha(android)==previous['inputs']['androidJar'] and sha(jsonjar)==previous['inputs']['jsonJar'],'Dependencies changed')
scratch=w/'tests';scratch.mkdir(exist_ok=True)
temp=scratch/'temp';temp.mkdir(exist_ok=True)
vectors=SNAPSHOT.parent/'station-online-recovery-r67-20261007/tests/contract-vectors.json'
env=dict(os.environ,TEMP=str(temp),TMP=str(temp))
cmd=[str(java),'-Djava.io.tmpdir='+str(temp),'-Dstation.recovery.vectors='+str(vectors),str(helper),os.pathsep.join(map(str,[jsonjar,android])),*classes]
run=subprocess.run(cmd,input='\n'.join(map(str,list(sources.values())+tests))+'\n',text=True,encoding='utf8',capture_output=True,env=env)
(scratch/'suite-private.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf8')
expected=[s for s in previous['stdout'].splitlines() if s and not s.startswith('success=')]
require(run.returncode==0,'JVM suite failed; see private log')
for line in expected:require(line in run.stdout,'Existing fixture result missing: '+line)
require('StationOwnRoomProfilesTest: 29 checks passed' in run.stdout,'Own-room regression fixture failed')
require(source_hashes=={n:sha(f) for n,f in sources.items()},'Sources changed during tests')
oldhashes=json.loads((SNAPSHOT.parent/'station-native-registration-r72-20261007/evidence/java-dex-build.json').read_text('utf8'))['sourceHashes']
changes=sorted(n for n in sources if source_hashes[n]!=oldhashes[n])
prefix='netplay-src/org/emulationstation/frontend/netplay/'
require(changes==[prefix+'StationRecoveryTunnel.java',prefix+'StationRetroActivity.java'],'Unexpected production delta')
activity=sources[prefix+'StationRetroActivity.java'].read_text('utf8')
register=activity.index('System.loadLibrary("station_retroarch")')
require(activity.rfind('super.onCreate(state)',0,register)>=0 and register<activity.index('nativeLoaded=true;'),'JNI registration order')
require('stationRecoveryStatus();stationRecoveryStalled();' in activity,'Read-only JNI probes missing')
receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),success=True,
 sourceHashes=source_hashes,productionSourceCount=198,changedSources=changes,preservedSources=196,
 testSourceHashes={f.relative_to(repo).as_posix():sha(f) for f in tests},testClasses=classes,
 previousSuiteChecks=1152,addedProfileChecks=29,countedChecks=1206,addedDiagnosticChecks=25,
 sourceBinding='exact compiled R73 production sources',buildReceiptSHA256=sha(w/'evidence/build.json'),
 clientDexSHA256=build['clientDexSHA256'],roomsDexSHA256=build['roomsDexSHA256'],
 nativeRegistrationPreserved=True,jniRegistrationAndroidVerified=False,
 androidGameplay=False,stdout=run.stdout,recipeSHA256=sha(__file__))
(w/'evidence/local-tests.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:receipt[k] for k in ['success','productionSourceCount','countedChecks','preservedSources','androidGameplay']},indent=2))
