#!/usr/bin/env python3
"""Compile the frozen updater and hooks using actual current private dependencies.

The output DEX is an overlay for the existing scoped assembler, NEVER an APK
partition to append with duplicate classes. No signing or installation occurs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

MODULE=Path(__file__).resolve().parents[1]
def run(args,cwd=None):
    result=subprocess.run(list(map(str,args)),cwd=cwd,check=True,capture_output=True,text=True)
    return result.stdout+result.stderr
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',required=True,type=Path)
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--classpath',required=True)
    parser.add_argument('--android-jar',required=True,type=Path)
    parser.add_argument('--d8-jar',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    repository=Path(run(['git','rev-parse','--show-toplevel'],MODULE).strip())
    commit=run(['git','rev-parse','HEAD'],repository).strip()
    if len(args.source_commit)!=40 or commit!=args.source_commit:raise ValueError('Use the frozen full source commit')
    executable=sorted((MODULE/'java').rglob('*.java'))+sorted((MODULE/'recipe').glob('*.py'))+[MODULE/'SCOPED-TYPES.json',MODULE/'manifest-fragment.xml']
    for source in executable:
        expected=subprocess.run(['git','show',commit+':'+source.relative_to(repository).as_posix()],cwd=repository,check=True,capture_output=True).stdout
        if expected!=source.read_bytes():raise ValueError('Executable source differs from frozen commit')
    dependencies=[Path(p) for p in args.classpath.split(os.pathsep)]
    if any(not p.is_file() for p in dependencies):raise ValueError('Use current private classpath JARs, not test fixtures or directories')
    args.out.mkdir(parents=True,exist_ok=False)
    patched=args.out/'patched'
    run([sys.executable,MODULE/'recipe/patch_sources.py','--source-dir',args.source_dir,'--out',patched])
    sources=sorted((MODULE/'java').rglob('*.java'))+sorted(patched.glob('*.java'))
    classes=args.out/'classes';classes.mkdir()
    compile_log=run(['javac','--release','8','-encoding','UTF-8','-Xlint:-options','-sourcepath','',
        '-cp',os.pathsep.join([str(args.android_jar),args.classpath]),'-d',classes,*sources])
    (args.out/'compile.log').write_text(compile_log)
    jar=args.out/'update-overlay.jar'
    with zipfile.ZipFile(jar,'w') as output:
        for path in sorted(classes.rglob('*.class')):output.write(path,path.relative_to(classes).as_posix())
    dex=args.out/'overlay-dex';dex.mkdir()
    command=['java','-cp',args.d8_jar,'com.android.tools.r8.D8','--release','--min-api','28','--lib',args.android_jar,'--output',dex]
    for dependency in dependencies:command+=['--classpath',dependency]
    run([*command,jar])
    receipt=dict(schema='station.app-update.overlay.v1',sourceCommit=commit,apkBuiltSignedOrInstalled=False,
        fixturesPackaged=False,overlayOnly=True,sourceHashes={str(p.relative_to(repository)):sha(p) for p in executable},
        patchedHashes={p.name:sha(p) for p in patched.glob('*.java')},
        dependencyHashes=[dict(name=p.name,sha256=sha(p)) for p in [args.android_jar,args.d8_jar,*dependencies]],
        overlayDexSha256=sha(dex/'classes.dex'))
    (args.out/'overlay-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'compiled':True,'overlayOnly':True,'sourceCommit':commit,'overlayDexSha256':receipt['overlayDexSha256'],'apkBuiltSignedOrInstalled':False}))

if __name__=='__main__':main()
