#!/usr/bin/env python3
"""Validate update sources against API/HTTP/Android inputs supplied by the caller.

All outputs are isolated tests, never a final APK or a replacement base DEX.
The optional panel fixture is compiled into a separate classpath directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

HERE=Path(__file__).resolve().parent
MODULE=HERE.parent

def run(args,cwd=None):
    p=subprocess.run(list(map(str,args)),cwd=cwd,capture_output=True,text=True)
    if p.returncode:
        raise RuntimeError(p.stdout+p.stderr)
    return p.stdout+p.stderr

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',required=True,type=Path)
    p.add_argument('--classpath',required=True)
    p.add_argument('--android-jar',required=True,type=Path)
    p.add_argument('--json-jar',required=True,type=Path)
    p.add_argument('--media-source',type=Path)
    p.add_argument('--origin-source',type=Path)
    p.add_argument('--fixture-panel',action='store_true')
    p.add_argument('--d8-jar',type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    patched=args.out/'patched'
    run([sys.executable,MODULE/'recipe/patch_sources.py','--source-dir',args.source_dir,'--out',patched])
    dependencies=args.out/'dependency-classes';dependencies.mkdir()
    classpath=os.pathsep.join([str(args.android_jar),str(args.json_jar),args.classpath])
    sources=[]
    if args.fixture_panel:sources.append(HERE/'fixtures/StationDownloadPanel.java')
    sources.extend(s for s in (args.media_source,args.origin_source) if s)
    if sources:run(['javac','--release','8','-Xlint:-options','-sourcepath','','-cp',classpath,'-d',dependencies,*sources])
    classes=args.out/'classes';classes.mkdir()
    cp=os.pathsep.join([str(dependencies),classpath])
    production=sorted((MODULE/'java').rglob('*.java'))+sorted(patched.glob('*.java'))
    compile_log=run(['javac','--release','8','-Xlint:-options','-sourcepath','','-cp',cp,'-d',classes,*production])
    (args.out/'compile.log').write_text(compile_log)
    tests=args.out/'test-classes';tests.mkdir()
    run(['javac','--release','8','-Xlint:-options','-sourcepath','','-cp',os.pathsep.join([str(classes),cp]),'-d',tests,HERE/'StationAppUpdateProbe.java'])
    output=run(['java','-cp',os.pathsep.join([str(tests),str(classes),str(dependencies),str(args.json_jar),args.classpath]),'org.emulationstation.frontend.station.StationAppUpdateProbe'])
    (args.out/'probe.log').write_text(output)
    classes_jar=args.out/'isolated-module-classes.jar'
    with zipfile.ZipFile(classes_jar,'w') as jar:
        for path in sorted(classes.rglob('*.class')):jar.write(path,path.relative_to(classes).as_posix())
    dex_sha=None
    if args.d8_jar:
        dex=args.out/'isolated-dex';dex.mkdir()
        run(['java','-cp',args.d8_jar,'com.android.tools.r8.D8','--release','--min-api','28','--lib',args.android_jar,'--output',dex,classes_jar])
        dex_sha=hashlib.sha256((dex/'classes.dex').read_bytes()).hexdigest()
    receipt=dict(status='passed',probe=output.strip(),androidInstallerOrUiValidated=False,apkBuiltSignedOrInstalled=False,
        compileUsesPanelFixture=args.fixture_panel,fixturesIncludedInModuleJar=False,
        moduleClassCount=len(list(classes.rglob('*.class'))),isolatedDexSha256=dex_sha,
        sourceHashes={str(s.relative_to(MODULE)) if s.is_relative_to(MODULE) else s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in production},
        dependencyHashes={str(s):hashlib.sha256(s.read_bytes()).hexdigest() for s in (args.android_jar,args.json_jar)},
        inputSourceHashes={s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in args.source_dir.glob('*.java')})
    (args.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('sourceHashes','dependencyHashes','inputSourceHashes')},ensure_ascii=False))

if __name__=='__main__':main()
