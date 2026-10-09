from pathlib import Path
import subprocess, os, hashlib, json, zipfile, shutil, copy, re, datetime
# APK uses classic ZIP uint32 offsets; Python's conservative 2 GiB ZIP64
# threshold would unnecessarily emit ZIP64 records rejected by Android tools.
zipfile.ZIP64_LIMIT=(1<<32)-1
W=Path(r'E:\ESTUDO APK\work\station-server-integration-r99-20261009')
S=Path(__file__).resolve().parent;IN=W/'incoming/versions/station-all-platforms-online-20261009'
BASE=Path(r'E:\ESTUDO APK\work\station-online-input-r98-20261009\package\TurboStations-Premium-R98-20261009.apk')
BASE_SHA='556fc80a4f5d403ac16a31a18390b156b99cbddce1d2e1a9c5540d0cd0538a77'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
FINAL=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R99-20261009.apk')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
    with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def sig(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def main():
    assert sha(BASE)==BASE_SHA
    out=W/'compiled';out.mkdir(exist_ok=True);(out/'temp').mkdir(exist_ok=True)
    env=dict(os.environ,TEMP=str(out/'temp'),TMP=str(out/'temp'))
    def run(cmd,name):
        r=subprocess.run(list(map(str,cmd)),capture_output=True,env=env)
        (out/(name+'.log')).write_bytes(r.stdout+r.stderr)
        assert r.returncode==0,(name,r.stderr.decode('utf8','replace')[-3000:])
        return r.stdout
    jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
    android=Path(r'G:\Android\Sdk\platforms\android-34\android.jar');d8=Path(r'G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar')
    sources={p.relative_to(S/'java').as_posix():sha(p) for p in sorted((S/'java').rglob('*.java'))};assert len(sources)==224
    jars={};dexes={}
    for module,prefixes in [('client',('client/src/java/',)),('rooms',('netplay-src/','dependency-src/'))]:
        classes=out/(module+'-classes');classes.mkdir(exist_ok=True)
        cp=str(android)+(os.pathsep+str(jars['client']) if module=='rooms' else '')
        args=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]
        args += [str(S/'java'/n) for n in sources if n.startswith(prefixes)]
        argfile=out/(module+'.args');argfile.write_text('\n'.join('"'+a.replace('\\','/')+'"' for a in args),'utf8')
        run([jdk/'javac.exe','@'+str(argfile)],module+'-javac')
        jar=out/(module+'.jar')
        with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(classes.rglob('*.class')):
                info=zipfile.ZipInfo(p.relative_to(classes).as_posix(),(2026,10,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
        jars[module]=jar;dex=out/(module+'-dex');dex.mkdir(exist_ok=True)
        command=[jdk/'java.exe','-cp',d8,'com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',dex]
        if module=='rooms':command+=['--classpath',jars['client']]
        run(command+[jar],module+'-d8');dexes[module]=dex/'classes.dex'
        print(module+' Java/DEX compiled',flush=True)
    (W/'evidence/java-sources.json').write_text(json.dumps(sources,indent=2)+'\n','utf8')
    payloads={'classes28.dex':dexes['client'],'classes35.dex':dexes['rooms']}
    for p in (IN/'native').glob('*.so'):payloads['lib/arm64-v8a/'+p.name]=p
    for p in (IN/'assets').rglob('*'):
        if p.is_file():payloads[p.relative_to(IN).as_posix()]=p
    # Validate shipped engines against actual old/new APK members before packaging.
    engines=json.loads((IN/'assets/station-online/engines.json').read_text())['engines']
    with zipfile.ZipFile(BASE) as z:
        for e in engines:
            name='lib/arm64-v8a/'+e['library'];actual=sha(payloads[name]) if name in payloads else zsha(z,name)
            assert actual==e['coreSha256'],e['engineId']
            assert sha(payloads['lib/arm64-v8a/libstation_retroarch.so'])==e['runtimeSha256']
    tools=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
    key=Path(r'C:\Users\Admin\.android\debug.keystore')
    env['STATION_KS_PASS']=env.get('STATION_KS_PASS','android');env['STATION_KEY_PASS']=env.get('STATION_KEY_PASS','android')
    cert=run([jdk/'keytool.exe','-exportcert','-keystore',key,'-alias','androiddebugkey','-storepass:env','STATION_KS_PASS'],'certificate')
    assert hashlib.sha256(cert).hexdigest()==CERT
    pkg=W/'package';pkg.mkdir(exist_ok=True);FINAL.parent.mkdir(exist_ok=True)
    unsigned=pkg/'unsigned.apk';aligned=pkg/'aligned.apk'
    assert not FINAL.exists()
    with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
        for info in old.infolist():
            if sig(info.filename):continue
            item=copy.copy(info);item.extra=b''
            with new.open(item,'w') as dst,(payloads[item.filename].open('rb') if item.filename in payloads else old.open(info)) as src:shutil.copyfileobj(src,dst,1024*1024)
        for name in sorted(set(payloads)-set(old.namelist())):
            info=zipfile.ZipInfo(name,(2026,10,9,0,0,0));info.compress_type=zipfile.ZIP_STORED if name.endswith('.so') else zipfile.ZIP_DEFLATED
            with new.open(info,'w') as dst,payloads[name].open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
    print('APK assembled',flush=True)
    run([tools/'zipalign.exe','-P','16','-f','4',unsigned,aligned],'zipalign')
    # The aligned copy is verified before removing only this run's unsigned temporary.
    with zipfile.ZipFile(aligned) as z:assert z.testzip() is None
    assert unsigned.resolve().parent==pkg.resolve();unsigned.unlink()
    run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','sign','--v4-signing-enabled','false','--ks',key,'--ks-key-alias','androiddebugkey','--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',FINAL,aligned],'sign')
    verified=run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',FINAL],'verify').decode()
    assert re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([a-f0-9]{64})\s*$',verified,re.M)==[CERT]
    run([tools/'zipalign.exe','-c','-P','16','4',FINAL],'alignment')
    changes=[];added=[]
    with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(FINAL) as new:
        names={n for n in old.namelist() if not sig(n)};newnames={n for n in new.namelist() if not sig(n)}
        assert newnames==names|set(payloads)
        for name in sorted(newnames):
            actual=zsha(new,name);original=zsha(old,name) if name in names else None
            assert actual==(sha(payloads[name]) if name in payloads else original),name
            if original is None:added.append(name)
            elif actual!=original:changes.append(name)
        # Preserve every offline engine, carousel, all original touch layouts and 219 gamepad profiles.
        preserved=[n for n in names if n.startswith(('assets/station-online/autoconfig/','assets/station-online/overlays/station-local/')) or n=='lib/arm64-v8a/libturbo_carousel.so']
        assert all(zsha(old,n)==zsha(new,n) for n in preserved)
    receipt=dict(version='R99',baseSHA256=BASE_SHA,sha256=sha(FINAL),bytes=FINAL.stat().st_size,certificateSHA256=CERT,
        changes=changes,added=added,entries=len(newnames),allEntriesVerified=True,javaSourceCount=len(sources),installed=False,gameplayVerified=False,
        runtimeSHA256=sha(payloads['lib/arm64-v8a/libstation_retroarch.so']),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (W/'evidence/package.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    assert aligned.resolve().parent==pkg.resolve();aligned.unlink()
    print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
