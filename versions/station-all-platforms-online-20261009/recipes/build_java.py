"""Compile the complete platform source set; produce both Android DEX files.

Use explicit JDK17, API34 and D8 inputs. Output is private and must be fresh.
This builds Java/DEX, not a signed full APK or a phone installation.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent/'station-online-readiness-r81-20261008'

def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser()
    for name in ('work','jdk','android-jar','d8-jar'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    baseline=json.loads((BASE/'evidence/java-build.json').read_text())
    assert sha(args.android_jar)==baseline['inputs']['androidJar']
    assert sha(args.d8_jar)==baseline['inputs']['d8Jar']
    sources={p.relative_to(ROOT/'java').as_posix():sha(p) for p in sorted((ROOT/'java').rglob('*.java'))}
    assert len(sources)==212 and set(baseline['sourceHashes']).issubset(sources)
    args.work.mkdir(parents=True,exist_ok=False)
    suffix='.exe' if os.name=='nt' else ''
    tools={name:args.jdk/(name+suffix) for name in ('java','javac')}
    jars={};hashes={}
    def run(command,name):
        result=subprocess.run(list(map(str,command)),capture_output=True)
        (args.work/(name+'.log')).write_bytes(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError(name+' failed; inspect private build log')
    for module,prefixes in [('client',('client/src/java/',)),('rooms',('netplay-src/','dependency-src/'))]:
        classes=args.work/(module+'-classes');classes.mkdir()
        cp=str(args.android_jar)+(os.pathsep+str(jars['client']) if module=='rooms' else '')
        options=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]
        options+=[str(ROOT/'java'/name) for name in sorted(sources) if name.startswith(prefixes)]
        argfile=args.work/(module+'.args')
        argfile.write_text('\n'.join('"'+value.replace('\\','/')+'"' for value in options),encoding='utf8')
        run([tools['javac'],'@'+str(argfile)],module+'-javac')
        jar=args.work/(module+'.jar')
        with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(classes.rglob('*.class')):
                info=zipfile.ZipInfo(path.relative_to(classes).as_posix(),(2026,10,7,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())
        jars[module]=jar
        dex=args.work/(module+'-dex');dex.mkdir()
        command=[tools['java'],'-cp',args.d8_jar,'com.android.tools.r8.D8','--min-api','26','--lib',args.android_jar,'--output',dex]
        if module=='rooms':command+=['--classpath',jars['client']]
        run(command+[jar],module+'-d8')
        hashes[module+'DexSHA256']=sha(dex/'classes.dex')
    assert hashes['clientDexSHA256']==baseline['clientDexSHA256'],'Unchanged authentication/catalog/download DEX did not reproduce'
    assert hashes['roomsDexSHA256']!=baseline['roomsDexSHA256']
    receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compiled=True,sourceCount=len(sources),sourceHashes=sources,
        changedSources=[name for name in sources if sources[name]!=baseline['sourceHashes'].get(name)],
        inputs=baseline['inputs'],recipeSHA256=sha(__file__),baseVersion='R81',**hashes,
        apkBuilt=False,installed=False,fivePhoneGameplayVerified=False)
    (args.work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (ROOT/'JAVA-SOURCE-MANIFEST.json').write_text(json.dumps({'baseVersion':'R81','sources':sources},indent=2)+'\n')
    (ROOT/'evidence/java-build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:value for key,value in receipt.items() if key!='sourceHashes'}))

if __name__=='__main__':main()
