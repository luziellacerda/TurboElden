"""Restore R55 + R57 visual overlay plus the reconciled readiness delta, compile Java8/API34 and DEX/min26."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,zipfile

win=os.name=='nt'
sdk=Path(r'G:\Android\Sdk')
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
p=argparse.ArgumentParser()
p.add_argument('--output',default=r'E:\ESTUDO APK\work\station-relay-readiness-r57-20261006')
p.add_argument('--android-jar',default=str(sdk/'platforms/android-34/android.jar'))
p.add_argument('--station-jar',default=r'E:\ESTUDO APK\work\station-download-performance-20261005\client\build-final\station-client.jar')
p.add_argument('--d8-jar',default=str(sdk/'build-tools/34.0.0/lib/d8.jar'))
p.add_argument('--java',default=str(jdk/'java.exe') if win else 'java')
p.add_argument('--javac',default=str(jdk/'javac.exe') if win else 'javac')
p.add_argument('--api-check-only',action='store_true',help='Only compile against the provided API classpath; no DEX or publishable APK')
a=p.parse_args();snapshot=Path(__file__).resolve().parent.parent
base=snapshot.parent/'station-current-r55-20261006'
out=Path(a.output).resolve()
if out.exists():raise SystemExit('Use a new output directory; existing source/build/APK is preserved')
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
expected={'androidJar':'6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
          'stationJar':'e41854977e9c2dab786f431449c95afb759e80c653e02cbc990434f74a2c39a2',
          'd8Jar':'d43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0'}
inputs={'androidJar':sha(a.android_jar),'stationJar':sha(a.station_jar)}
if inputs['androidJar']!=expected['androidJar']:raise SystemExit('The verified R55 Android34 SDK is required')
if not a.api_check_only:
    inputs['d8Jar']=sha(a.d8_jar)
    if inputs!=expected:raise SystemExit('Exact R55 station-client.jar / SDK / D8 are required for a candidate')
if sha(base/'SOURCE-MANIFEST.json')!='a106b5b5676acd1f8d6e2eaf7833b3cebd2bae7d48a85c96391ac06749620ca9':raise SystemExit('Exact received R55 source manifest required')
manifest=json.loads((base/'SOURCE-MANIFEST.json').read_text('utf8'))
for name,entry in manifest['files'].items():
    want=entry['sha256']
    if name.startswith(('netplay-src/','dependency-src/')) and sha(base/name)!=want:
        raise SystemExit('Frozen R55 source changed: '+name)
os.umask(0o077);out.mkdir(parents=True)
for name in ('netplay-src','dependency-src'):shutil.copytree(base/name,out/name)
visual=snapshot.parent/'station-layout-r57-20261006'
if sha(visual/'SOURCE-MANIFEST.json')!='a294d2ef860035c957e352f22c262ca9194c52391cc6aefdb10ed79191a6253c':raise SystemExit('Exact R57 overlay manifest required')
visualManifest=json.loads((visual/'SOURCE-MANIFEST.json').read_text('utf8'))
for name,entry in visualManifest['overlay'].items():
    if sha(visual/name)!=entry['sha256']:raise SystemExit('R57 overlay source changed: '+name)
    if name.startswith('netplay-src/'):
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(visual/name,target)
delta={}
for f in (snapshot/'netplay-src').rglob('*.java'):
    rel=f.relative_to(snapshot);shutil.copyfile(f,out/rel);delta[rel.as_posix()]=sha(f)
build=out/'build/final';classes=build/'classes';classes.mkdir(parents=True)
env=dict(os.environ,TEMP=str(out),TMP=str(out))
def run(args,name):
    r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace',env=env)
    (build/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf8');print((r.stdout+r.stderr)[-3000:],flush=True)
    r.check_returncode()
sources=sorted((out/'netplay-src').rglob('*.java'))+sorted((out/'dependency-src').rglob('*.java'))
args=['-encoding','UTF-8','--release','8','-cp',str(Path(a.android_jar))+os.pathsep+str(Path(a.station_jar)),'-d',str(classes)]+[str(f) for f in sources]
argfile=build/'javac.args';argfile.write_text('\n'.join('"'+v.replace('\\','/')+'"' for v in args),encoding='utf8')
run([a.javac,'@'+str(argfile)],'javac')
jar=build/'netplay.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(classes.rglob('*.class')):z.write(f,f.relative_to(classes).as_posix())
result={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled':True,
        'sourceBase':'R57','baseCommit':'8980cd422d63068299b5e9946c120f81a9c94f29','functionalBaseCommit':'9d3d45f048aa44bb2ee9c41f567e985901628daa','sourceFiles':len(sources),'delta':delta,'inputs':inputs,
        'apiCheckOnly':a.api_check_only,'java8API34':True,'minAPI':26,
        'apkBuilt':False,'installed':False,'twoDeviceGameplayVerified':False}
if not a.api_check_only:
    dex=build/'dex';dex.mkdir()
    run([a.java,'-cp',a.d8_jar,'com.android.tools.r8.D8','--min-api','26','--lib',a.android_jar,'--classpath',a.station_jar,'--output',dex,jar],'d8')
    result.update(dex=str(dex/'classes.dex'),dexSHA256=sha(dex/'classes.dex'),dexBytes=(dex/'classes.dex').stat().st_size)
(build/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ['compiled','sourceFiles','apiCheckOnly','apkBuilt','installed','twoDeviceGameplayVerified']}))
