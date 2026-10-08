"""Reproduce R74 DEX, then compile the reviewed R76 Java overlay on the same sources."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, os, shutil, subprocess, sys, zipfile
sys.dont_write_bytecode=True
SNAPSHOT=Path(__file__).resolve().parent.parent
PREVIOUS=SNAPSHOT.parent/'station-session-lifecycle-r74-20261007'
DEFAULT_WORK=r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008\compiled-final'
CLIENT_DEX='1a04582a02804ecbe4b075dd487118a171b0b0f305dbb8884015bbede09b25d7'
ROOMS_DEX='e8c57484aa2e566edf6226a02e1f5f8ba7f9c25c7f6b050b890a092637370d3c'
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def base_sources():
    spec=importlib.util.spec_from_file_location('frozen_r74',PREVIOUS/'recipes/build_candidate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    baseline,overlay,sources,_=module.verified_sources()
    receipt=json.loads((PREVIOUS/'evidence/java-dex-build.json').read_text('utf8'))
    require({n:sha(p) for n,p in sources.items()}==receipt['sourceHashes'],'Exact R74 source composition required')
    return baseline,overlay,sources
def verified_sources():
    baseline,overlay,sources=base_sources()
    manifest_path=SNAPSHOT/'JAVA-OVERLAY-MANIFEST.json'
    manifest=json.loads(manifest_path.read_text('utf8'))
    require(manifest['base']=='R74' and manifest['baseSourceReceiptSHA256']==sha(PREVIOUS/'evidence/java-dex-build.json'),'Wrong overlay base')
    names={p.relative_to(SNAPSHOT/'java').as_posix() for p in (SNAPSHOT/'java').rglob('*.java')}
    require(names==set(manifest['files'])==set(manifest['reviewedFiles']),'Unreviewed Java delta')
    require(names=={'netplay-src/org/emulationstation/frontend/netplay/StationRecoveryTunnel.java'},'Only the reviewed tunnel may change')
    for n,h in manifest['files'].items():
        p=SNAPSHOT/'java'/n;require(sha(p)==h and sha(sources[n])!=h,'Invalid overlay '+n)
        sources[n]=p;overlay[n]=p
    require(len(sources)==manifest['sourceCount']==201,'Source count differs')
    return baseline,overlay,sources,manifest_path
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default=DEFAULT_WORK);p.add_argument('--baseline',action='store_true');a=p.parse_args()
    work=Path(a.output).resolve();require(work.drive.upper()=='E:' and not work.exists(),'New E: build directory required')
    if a.baseline:
        _,_,sources=base_sources();manifest=None
    else:
        _,_,sources,manifest=verified_sources()
        proof=json.loads((work.parent/'baseline/evidence/build.json').read_text('utf8'))
        require(proof['baselineReproduced'] and proof['roomsDexSHA256']==ROOMS_DEX and proof['clientDexSHA256']==CLIENT_DEX,'Reproduce baseline first')
    source_hashes={n:sha(f) for n,f in sorted(sources.items())}
    for d in ('temp','evidence','java/build'):(work/d).mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,TEMP=str(work/'temp'),TMP=str(work/'temp'))
    for n,f in sources.items():
        dest=work/'java'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
        require(sha(dest)==source_hashes[n],'Staging mismatch')
    jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
    android=Path(r'G:\Android\Sdk\platforms/android-34/android.jar');d8=Path(r'G:\Android\Sdk\build-tools/34.0.0/lib/d8.jar')
    inputs={'androidJar':sha(android),'d8Jar':sha(d8)}
    require(inputs=={'androidJar':'6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad','d8Jar':'d43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0'},'SDK identity changed')
    def run(command,label):
        r=subprocess.run(list(map(str,command)),capture_output=True,env=env,timeout=180)
        (work/'evidence'/(label+'.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0,'Failed '+label)
    def compile_module(name,prefixes,cp):
        classes=work/'java/build'/(name+'-classes');classes.mkdir()
        paths=sorted(work/'java'/n for n in sources if n.startswith(prefixes))
        options=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]+list(map(str,paths))
        args=work/'java/build'/(name+'.args');args.write_text('\n'.join('"'+v.replace('\\','/')+'"' for v in options),'utf8')
        run([jdk/'javac.exe','-J-Djava.io.tmpdir='+str(work/'temp'),'@'+str(args)],name+'-javac')
        jar=work/'java/build'/(name+'.jar')
        with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(classes.rglob('*.class')):
                info=zipfile.ZipInfo(f.relative_to(classes).as_posix(),(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
        return jar
    client=compile_module('client',('client/src/java/',),str(android));rooms=compile_module('rooms',('netplay-src/','dependency-src/'),str(android)+os.pathsep+str(client))
    hashes={}
    for name,jar in [('client',client),('rooms',rooms)]:
        dest=work/'java/build'/(name+'-dex');dest.mkdir()
        command=[jdk/'java.exe','-Djava.io.tmpdir='+str(work/'temp'),'-cp',d8,'com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',dest]
        if name=='rooms':command+=['--classpath',client]
        run(command+[jar],name+'-d8');require([f.name for f in dest.iterdir()]==['classes.dex'],'Unexpected DEX split');hashes[name+'DexSHA256']=sha(dest/'classes.dex')
    require(hashes['clientDexSHA256']==CLIENT_DEX,'Client DEX must remain identical')
    require((hashes['roomsDexSHA256']==ROOMS_DEX)==a.baseline,'Unexpected rooms DEX identity')
    require({n:sha(f) for n,f in sources.items()}==source_hashes=={n:sha(work/'java'/n) for n in sources},'Source drift')
    old=json.loads((PREVIOUS/'evidence/java-dex-build.json').read_text('utf8'))['sourceHashes']
    receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base='R74',compiled=True,baselineReproduced=a.baseline,sourceHashes=source_hashes,sourceCount=len(sources),changedSources=[n for n in sources if old.get(n)!=source_hashes[n]],preservedSources=sum(old.get(n)==h for n,h in source_hashes.items()),inputs=inputs,clientJarSHA256=sha(client),roomsJarSHA256=sha(rooms),**hashes,baseRoomsDexSHA256=ROOMS_DEX,baseClientDexSHA256=CLIENT_DEX,clientDexUnchanged=True,overlayManifestSHA256=sha(manifest) if manifest else None,buildRecipeSHA256=sha(__file__),changedDexSlots=[] if a.baseline else ['classes35.dex'],apkBuilt=False,installed=False)
    (work/'evidence/build.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='sourceHashes'},indent=2))
if __name__=='__main__':main()
