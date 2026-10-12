from pathlib import Path
import subprocess,json,hashlib,datetime,argparse
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PROD=HERE.parent/'java/org/emulationstation/frontend/netplay'
p=argparse.ArgumentParser(description='Compile exact app sources and deterministic offline JVM probes; no device/network access.')
for key in ('out','jdk-bin','android-jar','rooms-jar','client-jar','json-jar','input-hashes'):p.add_argument('--'+key,type=Path,required=True)
a=p.parse_args()
OUT,JDK,ANDROID,ROOMS,CLIENT,JSON=a.out,a.jdk_bin,a.android_jar,a.rooms_jar,a.client_jar,a.json_jar
inputs={'javac':JDK/'javac.exe','java':JDK/'java.exe','androidJar':ANDROID,'roomsJar':ROOMS,'clientJar':CLIENT,'jsonJar':JSON}
expected=json.loads(a.input_hashes.read_text(encoding='utf-8'))
trusted=json.loads((HERE.parent/'SOURCE-PINS.json').read_text(encoding='utf-8'))['inputsSha256']
if expected.get('clientJar')!='011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313':raise ValueError('Unchanged R124 client required')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for name,path in inputs.items():
 if name not in trusted or expected.get(name)!=trusted[name] or sha(path)!=trusted[name]:raise ValueError('Pinned tested R134/API34/JDK17 input required: '+name)
BASE=REPO/'versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay'
DOLPHIN=REPO/'versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay'
MP=REPO/'integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java'
frozen={p:sha(p) for p in [MP,DOLPHIN/'StationDolphinSession.java',BASE/'StationGameSession.java',*PROD.glob('*.java')]}
receipt={'scope':'API34/JDK17 compilation (production Java8 target) and deterministic JVM probes of actual production classes; Android/native/IO edges mocked; no phone, server, APK or gameplay validation','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputsSha256':expected,'results':[]}
def run(name,args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf-8',timeout=35)
 (OUT/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8')
 if r.returncode:raise RuntimeError(name+': '+r.stdout+r.stderr)
 if r.stdout.strip():print(r.stdout.strip())
 receipt['results'].append({'name':name,'exitCode':r.returncode,'stdout':r.stdout.strip()})
def compile(name,sources,dest,cp):
 dest.mkdir(parents=True,exist_ok=True)
 target=['--release','8'] if 'production' in name else []
 run(name,[JDK/'javac.exe','-encoding','UTF-8','-proc:none',*target,'-cp',';'.join(map(str,cp)),'-d',dest,*sources])
OUT.mkdir(parents=True,exist_ok=True)
for variant in ('baseline','fixed'):
 production=OUT/variant/'production'
 sources=[MP,(DOLPHIN if variant=='baseline' else PROD)/'StationDolphinSession.java',(BASE if variant=='baseline' else PROD)/'StationGameSession.java']
 # The helper is available to compile the shared adversarial probe in both runs;
 # the unchanged baseline event 4 never invokes it.
 sources.append(PROD/'StationHumanDeparture.java')
 compile(variant+'-production-api34',sources,production,[ANDROID,ROOMS,CLIENT])
 for kind,probe in [('deadlock','StationDolphinExitDeadlockProbe'),('departure','StationHumanDepartureProbe')]:
  fixtures=list((HERE/(kind+'-fixtures')).rglob('*.java'))
  if kind=='departure':fixtures.append(PROD/'StationHumanDeparture.java')
  fixtureout=OUT/variant/kind
  compile(variant+'-'+kind+'-fixtures',fixtures+[HERE/(probe+'.java')],fixtureout,[JSON,production,ROOMS,CLIENT,ANDROID])
  run(variant+'-'+kind,[JDK/'java.exe','-cp',';'.join(map(str,[fixtureout,JSON,production,ROOMS,CLIENT,ANDROID])),'org.emulationstation.frontend.netplay.'+probe,variant])
for path,digest in frozen.items():
 if sha(path)!=digest:raise ValueError('Source changed during test: '+path.name)
for name,path in inputs.items():
 if sha(path)!=expected[name]:raise ValueError('Input changed during test: '+name)
receipt['overlaySha256']={str(p.relative_to(HERE.parent)).replace('\\','/'):sha(p) for p in sorted(PROD.glob('*.java'))}
receipt['baselineSha256']={str(p.relative_to(REPO)).replace('\\','/'):sha(p) for p in [MP,DOLPHIN/'StationDolphinSession.java',BASE/'StationGameSession.java']}
(HERE.parent/'evidence').mkdir(exist_ok=True)
(HERE.parent/'evidence/test-receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('receipt='+str(HERE.parent/'evidence/test-receipt.json'))
