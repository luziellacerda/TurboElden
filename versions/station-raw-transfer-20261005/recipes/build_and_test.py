#!/usr/bin/env python3
"""Build in a fresh directory from the frozen R16 Java snapshot plus two deltas."""
import argparse,hashlib,json,os,shutil,subprocess,zipfile
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--output',required=True,type=Path)
p.add_argument('--json-jar',required=True,type=Path)
p.add_argument('--android-jar',required=True,type=Path)
p.add_argument('--d8-jar',required=True,type=Path)
p.add_argument('--java',default='java');p.add_argument('--javac',default='javac')
a=p.parse_args();r=Path(__file__).resolve().parents[1]
base=r.parent/'station-performance-offline-r16-20261005';out=a.output.resolve()
names=['StationOfflineTest','StationDownloadPerformanceTest','StationCatalogPollTest','StationAutomaticCatalogTest','StationFoldersTest','StationFilesTest','StationApiTest','StationOnlineApiTest','StationStorageTest','StationCoordinatorTest','StationInstallerTest','StationClosureTest','StationBootstrapTest','StationCoverConcurrencyTest','StationTransferReuseTest','StationCoverPublicationTest']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert not out.exists(),'Use a fresh build directory'
manifest=json.loads((base/'SOURCE-MANIFEST.json').read_text())['files']
for name,digest in manifest.items():
 if name.endswith('.java') and (name.startswith('client\\src\\java\\') or
    name.startswith('client\\tests\\') and name.split('\\')[-1][:-5] in names):
  assert sha(base.joinpath(*name.split('\\')))==digest,'Frozen R16 source differs: '+name
out.mkdir(parents=True);shutil.copytree(base/'client/src/java',out/'src')
tests=out/'tests';tests.mkdir()
for name in names:shutil.copy2(base/'client/tests'/f'{name}.java',tests)
# Adapt only the expected RAW total; the historical R16 tests stay frozen.
perf=tests/'StationDownloadPerformanceTest.java';old='transition.total==(long)server.artifact.length+data.length'
text=perf.read_text();assert text.count(old)==1
perf.write_text(text.replace(old,'transition.total==(long)server.artifact.length+(archive?data.length:0)'))
for path in (r/'java').rglob('*.java'):shutil.copy2(path,out/'src'/path.relative_to(r/'java'))
for name in ['StationRawTransferTest','StationDownloadStartTest']:
 shutil.copy2(r/'tests'/f'{name}.java',tests);names.append(name)
sources=sorted((out/'src').rglob('*.java'));host=out/'host';host.mkdir()
pure=[s for s in sources if 'import android.' not in s.read_text(encoding='utf-8-sig')]
subprocess.run([a.javac,'-encoding','UTF-8','--release','11','-cp',str(a.json_jar),'-d',str(host),*map(str,pure),*map(str,tests.glob('*.java'))],check=True)
results=[]
for name in names:
 run=subprocess.run([a.java,'-cp',str(host)+os.pathsep+str(a.json_jar),'org.emulationstation.frontend.station.'+name,str(out/'fixtures'/name)],capture_output=True,text=True,check=True,timeout=90)
 print(run.stdout.strip(),flush=True);results.append({'test':name,'result':run.stdout.strip()})
android=out/'android';android.mkdir()
subprocess.run([a.javac,'-encoding','UTF-8','--release','8','-cp',str(a.android_jar),'-d',str(android),*map(str,sources)],check=True)
jar=out/'station-client.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(android.rglob('*.class')):z.write(path,path.relative_to(android).as_posix())
dex=out/'dex';dex.mkdir()
subprocess.run([a.java,'-cp',str(a.d8_jar),'com.android.tools.r8.D8','--min-api','26','--lib',str(a.android_jar),'--output',str(dex),str(jar)],check=True)
report={'tests':results,'androidCompile':'API36 Java8, D8 min26','dexSha256':sha(dex/'classes.dex'),'dexBytes':(dex/'classes.dex').stat().st_size,'gameBodyHashEnabled':False,'apkSignedOrInstalled':False,'sources':{s.relative_to(out/'src').as_posix():sha(s) for s in sources},'jsonJarSha256':sha(a.json_jar),'androidJarSha256':sha(a.android_jar)}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS Android compilation and DEX; no APK installed',flush=True)
