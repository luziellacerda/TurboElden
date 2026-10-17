"""Actual PSX Session/Launch with explicit JVM Android/JNI/typed metadata fixtures."""
from pathlib import Path
import argparse,hashlib,json,subprocess,shutil,os
ap=argparse.ArgumentParser();ap.add_argument('--jdk',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();suffix='.exe' if os.name=='nt' else '';a.jdk=a.jdk if (a.jdk/('javac'+suffix)).exists() else a.jdk/'bin';module=Path(__file__).resolve().parent.parent;repo=module.parent.parent;a.out.mkdir(parents=True,exist_ok=True)
java=module/'java/org/emulationstation/frontend/netplay';files=[java/'StationPsxSession.java',java/'StationPsxWifiLatency.java',java/'StationPsxLaunch.java',java/'StationPsxPolicy.java',module/'tests/StationPsxSessionProbe.java',repo/'versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationContentIdentity.java']+sorted((module/'tests/session-fixtures').rglob('*.java'))
classes=a.out/'classes';classes.mkdir(exist_ok=True);aliases=a.out/'aliases';paths=[]
for i,p in enumerate(files):
 q=aliases/str(i)/p.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(Path('\\\\?\\'+str(p.resolve())).read_bytes() if os.name=='nt' else p.read_bytes());paths.append(q)
args=a.out/'javac.args';args.write_text('\n'.join('"'+str(x).replace('\\','/')+'"' for x in ['-encoding','UTF-8','-d',classes,*paths])+'\n',encoding='utf-8')
r=subprocess.run([str(a.jdk/('javac'+suffix)),'@'+str(args)],capture_output=True,text=True);(a.out/'javac.log').write_text(r.stdout+r.stderr,encoding='utf-8')
if r.returncode:print(r.stderr);raise SystemExit(r.returncode)
r=subprocess.run([str(a.jdk/('java'+suffix)),'-cp',str(classes),'org.emulationstation.frontend.netplay.StationPsxSessionProbe'],capture_output=True,text=True);(a.out/'probe.log').write_text(r.stdout+r.stderr,encoding='utf-8')
if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
receipt={'passed':True,'result':r.stdout.strip(),'fixtureOnly':True,'fixtureShipped':False,'physicalGameplay':False,'scope':'Actual Session/Launch/ContentIdentity with typed metadata fixtures and fake Android/JNI; no auth cryptography or real JSON parser claim','sources':[{'file':p.relative_to(repo).as_posix(),'sha256':hashlib.sha256((Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p).read_bytes()).hexdigest()} for p in files]};(a.out/'session-launch-probe.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'result':receipt['result']}))
