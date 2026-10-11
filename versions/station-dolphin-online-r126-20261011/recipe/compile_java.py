"""Compile R124 rooms/dependencies with the explicit R125 and R126 deltas.

The unchanged client DEX is kept from the exact R124 APK. Its verified compiled
JAR is required as the classpath for the rooms module.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, zipfile, shutil, os

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'station-video-room-footer-r124-20261011'
CLIENT_JAR_SHA='011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313'
def native(path):return Path('\\\\?\\'+str(path.resolve())) if os.name=='nt' else path
def sha(path):return hashlib.sha256(native(path).read_bytes()).hexdigest()
def run(command,out,name):
    result=subprocess.run([str(x) for x in command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    (out/(name+'.log')).write_text(result.stdout,encoding='utf-8')
    if result.returncode:raise RuntimeError(name+' failed; see '+str(out/(name+'.log')))

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--jdk',type=Path,required=True);p.add_argument('--android-jar',type=Path,required=True);p.add_argument('--d8-jar',type=Path,required=True);p.add_argument('--client-jar',type=Path,required=True);a=p.parse_args()
    assert not a.out.exists();a.out.mkdir(parents=True)
    manifest=json.loads((PARENT/'JAVA-SOURCE-MANIFEST.json').read_text(encoding='utf-8'))
    assert sha(a.client_jar)==CLIENT_JAR_SHA, 'R124 client classpath changed'
    base={}
    for name,digest in manifest.items():
        path=PARENT/'java'/name;assert sha(path)==digest,'R124 source changed: '+name
        if name.startswith(('netplay-src/','dependency-src/')):base[name]=path
    for revision in (ROOT.parent/'station-mupen-online-r125-20261011',ROOT):
        delta={p.relative_to(revision/'java').as_posix():p for p in (revision/'java').rglob('*.java')}
        for name,path in delta.items():base['netplay-src/'+name]=path
    classes=a.out/'classes';classes.mkdir();alias=a.out/'source-alias';source_paths=[]
    for i,(name,path) in enumerate(sorted(base.items())):
        target=alias/str(i)/path.name;target.parent.mkdir(parents=True);shutil.copyfile(native(path),target);source_paths.append(target)
    args=['-encoding','UTF-8','--release','8','-proc:none','-cp',str(a.android_jar)+';'+str(a.client_jar),'-d',str(classes)]+[str(x) for x in source_paths]
    argfile=a.out/'javac.args';argfile.write_text('\n'.join('"'+x.replace('\\','/')+'"' for x in args)+'\n',encoding='utf-8')
    run([a.jdk/'javac.exe','@'+str(argfile)],a.out,'javac')
    jar=a.out/'rooms.jar'
    with zipfile.ZipFile(jar,'w',zipfile.ZIP_STORED) as archive:
        for path in sorted(classes.rglob('*.class')):
            info=zipfile.ZipInfo(path.relative_to(classes).as_posix(),(1980,1,1,0,0,0));archive.writestr(info,path.read_bytes())
    dex=a.out/'dex';dex.mkdir()
    run([a.jdk/'java.exe','-cp',a.d8_jar,'com.android.tools.r8.D8','--release','--min-api','28','--lib',a.android_jar,'--classpath',a.client_jar,'--output',dex,jar],a.out,'d8')
    files=list(dex.glob('*.dex'));assert len(files)==1
    final=a.out/'classes35.dex';shutil.copyfile(files[0],final)
    sources={name:sha(path) for name,path in sorted(base.items())}
    (a.out/'compile-java.json').write_text(json.dumps({'sourceCount':len(sources),'sources':sources,'clientClasspathJarSHA256':sha(a.client_jar),'classes35SHA256':sha(final),'nativeUIChanged':False,'physicalGameplayValidated':False},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sourceCount':len(sources),'classes35SHA256':sha(final)}))
if __name__=='__main__':main()
