"""Build the reconciled R66 successor, with protected DEX28/35 together, on E:."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys, zipfile
sys.dont_write_bytecode = True
from source_composition import verified_composition, sha

parser = argparse.ArgumentParser()
parser.add_argument('--output', default=r'E:\ESTUDO APK\work\station-collection-videos-r67-20261007\java')
args = parser.parse_args()
out = Path(args.output).resolve()
assert out.drive.upper() == 'E:' and not out.exists(), 'Use a new E: build folder'
sources = verified_composition()
assert len(sources) == 193
sdk = Path(r'G:\Android\Sdk')
jdk = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
android = sdk / 'platforms/android-34/android.jar'
d8 = sdk / 'build-tools/34.0.0/lib/d8.jar'
inputs = {'androidJar':sha(android), 'd8Jar':sha(d8)}
assert inputs == {'androidJar':'6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
                  'd8Jar':'d43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0'}
out.mkdir(parents=True)
for folder in ('temp','evidence','build'):(out / folder).mkdir()
env = dict(os.environ, TEMP=str(out / 'temp'), TMP=str(out / 'temp'))
for name, source in sources.items():
    destination = out / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

def run(command, label):
    result = subprocess.run(list(map(str,command)), capture_output=True, env=env)
    (out / 'evidence' / (label+'.log')).write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(label+' failed; see private build log')

def compile_module(name, prefixes, classpath):
    classes = out / 'build' / (name+'-classes');classes.mkdir()
    paths = sorted(out / rel for rel in sources if rel.startswith(prefixes))
    options = ['-encoding','UTF-8','--release','8','-proc:none','-cp',classpath,'-d',str(classes)]+list(map(str,paths))
    argfile = out / 'build' / (name+'.args')
    argfile.write_text('\n'.join('"'+s.replace('\\','/')+'"' for s in options), 'utf8')
    run([jdk/'javac.exe','-J-Djava.io.tmpdir='+str(out/'temp'),'@'+str(argfile)],name+'-javac')
    jar = out / 'build' / (name+'.jar')
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(classes.rglob('*.class')):
            info=zipfile.ZipInfo(source.relative_to(classes).as_posix(),(2026,10,7,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,source.read_bytes())
    return jar

client = compile_module('client',('client/src/java/',),str(android))
rooms = compile_module('rooms',('netplay-src/','dependency-src/'),str(android)+os.pathsep+str(client))
receipt = {'base':'R66','baseAPK':'e4397fd743c410ea060f17446706d9475b5568caad379e1a6df37672c60398d1',
           'serverReturn':'b37c873b70bf361388b3a18fd58eed3b5452565a','inputs':inputs,
           'sourceHashes':{name:sha(source) for name,source in sorted(sources.items())},
           'clientJarSHA256':sha(client),'roomsJarSHA256':sha(rooms),
           'java8API34':True,'requestProofIntegrated':True,'compiled':True,
           'apkBuilt':False,'installed':False,'hardwareAttestationVerified':False}
for name, jar in [('client',client),('rooms',rooms)]:
    dex=out/'build'/(name+'-dex');dex.mkdir()
    command=[jdk/'java.exe','-Djava.io.tmpdir='+str(out/'temp'),'-cp',d8,'com.android.tools.r8.D8',
             '--min-api','26','--lib',android,'--output',dex]
    if name=='rooms':command+=['--classpath',client]
    run(command+[jar],name+'-d8')
    assert sorted(p.name for p in dex.iterdir())==['classes.dex']
    receipt[name+'DexSHA256']=sha(dex/'classes.dex')
receipt['createdAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'evidence/build.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
print('Protected client and current rooms compiled together; packaging and device tests pending.')
