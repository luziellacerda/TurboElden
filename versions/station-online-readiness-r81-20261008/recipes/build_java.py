"""Compile all 209 canonical Java sources. No historical source overlays."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile,datetime,shutil,sys
ROOT=Path(__file__).resolve().parent.parent
WORK=Path(r'E:\ESTUDO APK\work\station-online-readiness-r81-20261008')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r79')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def freeze():
    receipt=json.loads((WORK/'java-build-receipt.json').read_text('utf8'))
    for module in ['client','rooms']:assert sha(WORK/'compiled-final'/(module+'-dex/classes.dex'))==receipt[module+'DexSHA256']
    for name,digest in receipt['sourceHashes'].items():
        src=WORK/'java'/name;assert sha(src)==digest
        dst=Path('\\\\?\\'+str((ROOT/'java'/name).resolve()))
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(dst)==digest
    shutil.copyfile(WORK/'JAVA-SOURCE-MANIFEST.json',ROOT/'JAVA-SOURCE-MANIFEST.json')
    print('Frozen complete source set: '+str(len(receipt['sourceHashes'])))
def main():
    sources={p.relative_to(WORK/'java').as_posix():sha(p) for p in sorted((WORK/'java').rglob('*.java'))}
    baseline=json.loads((BASE/'JAVA-SOURCE-MANIFEST.json').read_text('utf8'))['sources']
    assert len(sources)==209 and sources.keys()==baseline.keys()
    changes=[n for n in sources if sources[n]!=baseline[n]]
    expected=['StationOnlineClient.java','StationOnlineGame.java','StationRoomsActivity.java','StationMultiplayerProfile.java']
    assert sorted(Path(n).name for n in changes)==sorted(expected),changes
    for name,digest in baseline.items():assert sha(BASE/'java'/name)==digest,name
    jr=json.loads((BASE/'java-build-receipt.json').read_text('utf8'))
    jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
    android=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
    d8=Path(r'G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar')
    assert sha(android)==jr['inputs']['androidJar'] and sha(d8)==jr['inputs']['d8Jar']
    out=WORK/'compiled-final';assert not out.exists(),'Fresh build required';out.mkdir()
    temp=out/'temp';temp.mkdir();env=dict(os.environ,TEMP=str(temp),TMP=str(temp))
    def run(cmd,label):
        r=subprocess.run(list(map(str,cmd)),env=env,capture_output=True)
        (out/(label+'.log')).write_bytes(r.stdout+r.stderr)
        assert r.returncode==0,label
    jars={};hashes={}
    for module,prefix in [('client',('client/src/java/',)),('rooms',('netplay-src/','dependency-src/'))]:
        classes=out/(module+'-classes');classes.mkdir()
        cp=str(android)+(os.pathsep+str(jars['client']) if module=='rooms' else '')
        options=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]
        options += [str(WORK/'java'/name) for name in sorted(sources) if name.startswith(prefix)]
        args=out/(module+'.args');args.write_text('\n'.join('"'+v.replace('\\','/')+'"' for v in options),'utf8')
        run([jdk/'javac.exe','-J-Djava.io.tmpdir='+str(temp),'@'+str(args)],module+'-javac')
        jar=out/(module+'.jar')
        with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(classes.rglob('*.class')):
                info=zipfile.ZipInfo(f.relative_to(classes).as_posix(),(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
        jars[module]=jar;dex=out/(module+'-dex');dex.mkdir()
        command=[jdk/'java.exe','-Djava.io.tmpdir='+str(temp),'-cp',d8,'com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',dex]
        if module=='rooms':command+=['--classpath',jars['client']]
        run(command+[jar],module+'-d8');hashes[module+'DexSHA256']=sha(dex/'classes.dex')
    assert hashes['clientDexSHA256']==jr['clientDexSHA256'],'Unchanged client DEX must reproduce'
    assert hashes['roomsDexSHA256']!=jr['roomsDexSHA256'],'Expected rooms update'
    receipt=dict(version='R81',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compiled=True,sourceCount=len(sources),sourceHashes=sources,changedSources=changes,baseVersion='R79',inputs=jr['inputs'],baseClientDexSHA256=jr['clientDexSHA256'],baseRoomsDexSHA256=jr['roomsDexSHA256'],recipeSHA256=sha(__file__),**hashes)
    (WORK/'JAVA-SOURCE-MANIFEST.json').write_text(json.dumps({'version':'R81','sources':sources},indent=2)+'\n','utf8')
    (WORK/'java-build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    (ROOT/'evidence').mkdir(exist_ok=True);shutil.copyfile(WORK/'java-build-receipt.json',ROOT/'evidence/java-build.json')
    # Freeze the complete source set used for this build in Git, not an overlay recipe.
    freeze()
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['sourceHashes','inputs']},indent=2))
if __name__=='__main__':
    if '--freeze-only' in sys.argv:freeze()
    else:main()
