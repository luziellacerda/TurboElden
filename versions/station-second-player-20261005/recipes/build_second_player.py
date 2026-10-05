"""Restore exact R30 Java inputs, overlay this delta and compile only classes35.

No APK installation, signing material or production server mutation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def restore(delta, destination):
    versions=delta.parent
    expected=json.loads((versions/'station-back-rooms-r30-20261005/SOURCE-MANIFEST.json').read_text())
    for group in ('netplay-src','dependency-src'):
        shutil.copytree(versions/'station-compact-lobby-r27-20261005'/group,destination/group)
        previous=versions/'station-back-rooms-r30-20261005'/group
        if previous.exists():shutil.copytree(previous,destination/group,dirs_exist_ok=True)
        if hashes(destination/group)!=expected[group]:raise RuntimeError('R30 source bytes differ: '+group)
    for source in (delta/'netplay-src').rglob('*.java'):
        shutil.copyfile(source,destination/'netplay-src'/source.relative_to(delta/'netplay-src'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('android-jar','client-jar','r8-jar','output'):p.add_argument('--'+key,required=True)
    for key in ('java','javac','jar'):p.add_argument('--'+key,default=key)
    a=p.parse_args();delta=Path(__file__).resolve().parent.parent
    out=Path(a.output).resolve()
    if out.exists():raise RuntimeError('Output must be a new directory')
    inputs=[Path(getattr(a,k)).resolve() for k in ('android_jar','client_jar','r8_jar')]
    if not all(x.is_file() for x in inputs):raise RuntimeError('Required build input missing')
    out.mkdir(parents=True);restore(delta,out/'src')
    classes=out/'classes';classes.mkdir();dex=out/'dex';dex.mkdir()
    sources=sorted((out/'src').rglob('*.java'))
    # An argfile handles both the Windows source paths and the full dependency set.
    argfile=out/'javac.args'
    args=['--release','8','-encoding','UTF-8','-classpath',os.pathsep.join(map(str,inputs[:2])),'-d',str(classes)]+list(map(str,sources))
    argfile.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in args)+'\n',encoding='utf-8')
    subprocess.run([a.javac,'@'+str(argfile)],check=True)
    jar=out/'netplay-second-player.jar'
    subprocess.run([a.jar,'cf',str(jar),'-C',str(classes),'.'],check=True)
    subprocess.run([a.java,'-cp',str(inputs[2]),'com.android.tools.r8.D8','--min-api','26',
                    '--lib',str(inputs[0]),'--classpath',str(inputs[1]),'--output',str(dex),str(jar)],check=True)
    if sorted(x.name for x in dex.glob('*.dex'))!=['classes.dex']:raise RuntimeError('Unexpected multidex result')
    source={group:hashes(out/'src'/group) for group in ('netplay-src','dependency-src')}
    (out/'SOURCE-MANIFEST.json').write_text(json.dumps(source,indent=2)+'\n')
    report={'compiled':True,'javaSources':len(sources),'sourceBase':'R30','javaRelease':8,'minApi':26,
            'originalApkSha256':'1768b7df440dcdf99efbd2e8ff93181eae06edaab5bb9be85e073afeb639027b',
            'replaceOnly':'classes35.dex','dexSha256':hashlib.sha256((dex/'classes.dex').read_bytes()).hexdigest(),
            'dexBytes':(dex/'classes.dex').stat().st_size,'installed':False,'twoAndroidGameplayVerified':False}
    (out/'build-result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
