"""Compile the composed R57 client and rooms together, Java8/API34, DEX28/35 min26."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,zipfile
win=os.name=='nt';sdk=Path(r'G:\Android\Sdk');jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
p=argparse.ArgumentParser()
p.add_argument('--output',default=r'E:\ESTUDO APK\work\station-security-r57-20261007')
p.add_argument('--android-jar',default=str(sdk/'platforms/android-34/android.jar'))
p.add_argument('--station-jar',default=r'E:\ESTUDO APK\work\station-download-performance-20261005\client\build-final\station-client.jar')
p.add_argument('--d8-jar',default=str(sdk/'build-tools/34.0.0/lib/d8.jar'))
p.add_argument('--java',default=str(jdk/'java.exe') if win else 'java')
p.add_argument('--javac',default=str(jdk/'javac.exe') if win else 'javac')
p.add_argument('--api-check-only',action='store_true')
a=p.parse_args();snapshot=Path(__file__).resolve().parent.parent;versions=snapshot.parent
out=Path(a.output).resolve();base=versions/'station-current-r55-20261006'
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(ok,message):
    if not ok:raise SystemExit(message)
require(not out.exists(),'Use a new output directory; existing builds are preserved')
expected={'androidJar':'6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
          'stationJar':'e41854977e9c2dab786f431449c95afb759e80c653e02cbc990434f74a2c39a2',
          'd8Jar':'d43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0'}
inputs={'androidJar':sha(a.android_jar),'stationJar':sha(a.station_jar)}
require(inputs['androidJar']==expected['androidJar'],'Verified Android34 SDK is required')
if not a.api_check_only:
    inputs['d8Jar']=sha(a.d8_jar);require(inputs==expected,'Exact original R55 classpath and D8 are required')
require(sha(base/'SOURCE-MANIFEST.json')=='a106b5b5676acd1f8d6e2eaf7833b3cebd2bae7d48a85c96391ac06749620ca9','Frozen R55 manifest differs')
base_manifest=json.loads((base/'SOURCE-MANIFEST.json').read_text('utf8'))
source_prefixes=('client/src/java/','netplay-src/','dependency-src/')
for name,entry in base_manifest['files'].items():
    if name.startswith(source_prefixes):require(sha(base/name)==entry['sha256'],'Frozen R55 source changed: '+name)
visual=versions/'station-layout-r57-20261006';auto=versions/'station-auto-room-access-r57-20261006'
require(sha(visual/'SOURCE-MANIFEST.json')=='a294d2ef860035c957e352f22c262ca9194c52391cc6aefdb10ed79191a6253c','R57 visual manifest differs')
require(sha(auto/'SOURCE-MANIFEST.json')=='ae01012d59544c5e479c012483a51994bd1df264ab66c9eabbc40d1d4699db24','Automatic room access manifest differs')
os.umask(0o077);out.mkdir(parents=True)
for name in source_prefixes:shutil.copytree(base/name,out/name)
for name,entry in json.loads((visual/'SOURCE-MANIFEST.json').read_text('utf8'))['overlay'].items():
    require(sha(visual/name)==entry['sha256'],'Visual source changed: '+name)
    if name.startswith('netplay-src/'):shutil.copyfile(visual/name,out/name)
auto_manifest=json.loads((auto/'SOURCE-MANIFEST.json').read_text('utf8'))
for f in (auto/'netplay-src').rglob('*.java'):
    rel=f.relative_to(auto);require(sha(f)==auto_manifest['files'][rel.as_posix()]['sha256'],'Automatic room access source changed: '+str(rel))
    shutil.copyfile(f,out/rel)
for prefix in ('client/src/java','netplay-src'):
    for f in (snapshot/prefix).rglob('*.java'):
        target=out/f.relative_to(snapshot);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)
source_hashes={f.relative_to(out).as_posix():sha(f) for prefix in source_prefixes for f in (out/prefix).rglob('*.java')}
require(len(source_hashes)==190,'Unexpected composed source count')
build=out/'build/final';build.mkdir(parents=True);env=dict(os.environ,TEMP=str(out),TMP=str(out))
def run(args,name):
    r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace',env=env)
    (build/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
    print((r.stdout+r.stderr)[-2000:],flush=True);r.check_returncode()
def compile_module(prefixes,module,classpath):
    classes=build/(module+'-classes');classes.mkdir()
    sources=sorted(f for prefix in prefixes for f in (out/prefix).rglob('*.java'))
    args=['-encoding','UTF-8','--release','8','-cp',classpath,'-d',str(classes)]+list(map(str,sources))
    argfile=build/(module+'-javac.args');argfile.write_text('\n'.join('"'+v.replace('\\','/')+'"' for v in args),encoding='utf8')
    run([a.javac,'@'+str(argfile)],module+'-javac')
    jar=build/(module+'.jar')
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(classes.rglob('*.class')):z.write(f,f.relative_to(classes).as_posix())
    return jar
client=compile_module(['client/src/java'],'station-client',a.android_jar)
netplay=compile_module(['netplay-src','dependency-src'],'netplay',str(Path(a.android_jar))+os.pathsep+str(client))
result={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled':True,
    'sourceBase':'R57','securityOverlay':'request-proof-v1','baseCommit':'8980cd422d63068299b5e9946c120f81a9c94f29',
    'previousHandoffCommit':'029612b06205ff66cc1c7dcb2a2dd1a4c47aa1f9','inputs':inputs,
    'sourceFiles':len(source_hashes),'sourceHashes':source_hashes,'apiCheckOnly':a.api_check_only,'java8API34':True,'minAPI':26,
    'clientJarSHA256':sha(client),'netplayJarSHA256':sha(netplay),'apkBuilt':False,'installed':False,'hardwareAttestationVerified':False,'twoDeviceGameplayVerified':False}
if not a.api_check_only:
    for jar,module in [(client,'client'),(netplay,'netplay')]:
        dex=build/(module+'-dex');dex.mkdir()
        args=[a.java,'-cp',a.d8_jar,'com.android.tools.r8.D8','--min-api','26','--lib',a.android_jar,'--output',dex]
        if module=='netplay':args+=['--classpath',client]
        run(args+[jar],module+'-d8')
        require([f.name for f in dex.iterdir()]==['classes.dex'],'Unexpected split DEX output')
        result[module+'DexSHA256']=sha(dex/'classes.dex')
(build/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ['compiled','sourceFiles','apiCheckOnly','apkBuilt','installed','hardwareAttestationVerified']}))
