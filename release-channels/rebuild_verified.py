"""Verify or reproduce one explicit frozen channel. Never searches older version folders."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, zipfile

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('channel',choices=['stable-2p','test-4p'])
    p.add_argument('--backup',type=Path,default=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008'))
    p.add_argument('--output',type=Path)
    p.add_argument('--build',choices=['java','carousel','both'])
    a=p.parse_args()
    channels=json.loads((Path(__file__).parent/'ACTIVE.json').read_text('utf8'))['channels']
    config=channels[a.channel];root=a.backup/config['directory']
    apk=root/config['apk']
    assert sha(apk)==config['apkSHA256'],'Wrong APK for selected channel'
    jr=json.loads((root/'java-build-receipt.json').read_text('utf8'))
    manifest=json.loads((root/'JAVA-SOURCE-MANIFEST.json').read_text('utf8'))
    assert manifest['sources']==jr['sourceHashes']
    assert len(manifest['sources'])==config['javaSourceCount']
    for name,digest in manifest['sources'].items():assert sha(root/'java'/name)==digest,name
    guard=json.loads((a.backup/'BUILD-INPUTS-VERIFIED.json').read_text('utf8'))
    for name,record in guard['files'].items():
        if name.startswith(config['directory']+'/carousel-inputs/'):
            assert sha(a.backup/name)==record['sha256'],name
    if not a.build:
        print(json.dumps({'channel':a.channel,'verified':True,'sourceCount':len(manifest['sources']),'apkSHA256':config['apkSHA256']}));return
    assert a.output and a.output.drive.upper()=='E:' and not a.output.exists(),'Use a fresh E: output directory'
    a.output.mkdir(parents=True);temp=a.output/'temp';temp.mkdir()
    env=dict(os.environ,TEMP=str(temp),TMP=str(temp))
    def run(cmd,label):
        r=subprocess.run(list(map(str,cmd)),env=env,capture_output=True)
        (a.output/(label+'.log')).write_bytes(r.stdout+r.stderr)
        assert r.returncode==0,label
    result={'channel':a.channel,'compiled':True,'apkChanged':False,'installed':False}
    if a.build in ('carousel','both'):
        nr=json.loads((root/'carousel-command.json').read_text('utf8'))
        assert sha(nr['command'][0])==nr['compilerSHA256'],'Compiler mismatch'
        output=a.output/'libturbo_carousel.so'
        command=[v.replace('{BACKUP}',str(a.backup)).replace('{OUTPUT}',str(output)) for v in nr['command']]
        run(command,'carousel');assert sha(output)==nr['expectedSHA256'],'Carousel reproduction differs'
        result['carouselReproduced']=True
    if a.build in ('java','both'):
        jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
        android=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
        d8=Path(r'G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar')
        assert sha(android)==jr['inputs']['androidJar'] and sha(d8)==jr['inputs']['d8Jar']
        jars={}
        for module,prefix in [('client',('client/src/java/',)),('rooms',('netplay-src/','dependency-src/'))]:
            classes=a.output/(module+'-classes');classes.mkdir()
            cp=str(android)+(os.pathsep+str(jars['client']) if module=='rooms' else '')
            options=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]
            options += [str(root/'java'/name) for name in sorted(manifest['sources']) if name.startswith(prefix)]
            args=a.output/(module+'.args');args.write_text('\n'.join('"'+v.replace('\\','/')+'"' for v in options),'utf8')
            run([jdk/'javac.exe','-J-Djava.io.tmpdir='+str(temp),'@'+str(args)],module+'-javac')
            jar=a.output/(module+'.jar')
            with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
                for f in sorted(classes.rglob('*.class')):
                    info=zipfile.ZipInfo(f.relative_to(classes).as_posix(),(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
            jars[module]=jar
            dex=a.output/(module+'-dex');dex.mkdir()
            command=[jdk/'java.exe','-Djava.io.tmpdir='+str(temp),'-cp',d8,'com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',dex]
            if module=='rooms':command+=['--classpath',jars['client']]
            run(command+[jar],module+'-d8')
            assert sha(dex/'classes.dex')==jr[module+'DexSHA256'],module+' DEX reproduction differs'
        result['javaReproduced']=True
    (a.output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))

if __name__=='__main__':main()
