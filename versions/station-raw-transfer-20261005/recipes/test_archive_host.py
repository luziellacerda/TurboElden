#!/usr/bin/env python3
"""Host JNI regression; Android library is built and verified separately."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--java-build',required=True,type=Path);p.add_argument('--headers',required=True,type=Path);p.add_argument('--json-jar',required=True,type=Path);p.add_argument('--jdk',required=True,type=Path);a=p.parse_args()
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
r=Path(__file__).resolve().parents[1];base=r.parent/'station-performance-offline-r16-20261005/client/src/native/station_archive.c'
cp=str(a.java_build/'host')+os.pathsep+str(a.json_jar);classes=out/'classes';classes.mkdir()
subprocess.run(['javac','--release','11','-encoding','UTF-8','-cp',cp,'-d',str(classes),str(r/'tests/StationArchivePolicyTest.java')],check=True)
results=[]
for policy,source in [('original',base),('skip',r/'native/station_archive.c')]:
 library=out/policy/'libstation_archive.so';library.parent.mkdir()
 subprocess.run(['gcc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-I'+str(a.jdk/'include'),'-I'+str(a.jdk/'include/linux'),'-I'+str(a.headers),str(source),'-Wl,--no-undefined','-l:libarchive.so.13','-o',str(library)],check=True)
 run=subprocess.run(['java','-Djava.library.path='+str(library.parent),'-cp',str(classes)+os.pathsep+cp,'org.emulationstation.frontend.station.StationArchivePolicyTest',str(out/'fixtures'/policy),policy],capture_output=True,text=True,check=True)
 print(run.stdout.strip(),flush=True);results.append({'policy':policy,'output':run.stdout.strip()})
(out/'result.json').write_text(json.dumps({'tests':results,'hostDecoder':'Ubuntu libarchive.so.13.7.2','androidExecution':False},indent=2)+'\n')
