"""Package one reviewed DEX over the canonical R79 APK. No phone or deployment actions."""
from pathlib import Path
import copy,datetime,hashlib,json,os,re,shutil,struct,subprocess,zipfile
ROOT=Path(__file__).resolve().parent.parent
WORK=Path(r'E:\ESTUDO APK\work\station-online-readiness-r81-20261008')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r79\TurboStations-Premium-R79-20261008.apk')
BASE_SHA='c2aeee4443dedc2862b29dde1f972574bc25464d6993abf01f34d43531558f0a'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
KEY=Path(r'C:\Users\Admin\.android\debug.keystore')
def need(ok,message):
    if not ok:raise RuntimeError(message)
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,name):
    with z.open(name) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def main():
    need(sha(BASE)==BASE_SHA,'Canonical R79 base required')
    jr=json.loads((WORK/'java-build-receipt.json').read_text('utf8'))
    need(jr['compiled'] and jr['sourceCount']==209,'Complete compiled source required')
    need(jr['recipeSHA256']==sha(ROOT/'recipes/build_java.py'),'Build recipe drift')
    for name,digest in jr['sourceHashes'].items():
        need(sha(WORK/'java'/name)==digest,'Work source drift '+name)
        need(sha(Path('\\\\?\\'+str((ROOT/'java'/name).resolve())))==digest,'Snapshot source drift '+name)
    for test in ['readiness-tests','profile-classification-tests']:
        record=json.loads((ROOT/'evidence'/(test+'.json')).read_text('utf8'));need(record['passed'],'Tests required')
        for name,digest in record.get('sourceHashes',record.get('correctedSources',{})).items():
            need(sha(WORK/'java/netplay-src/org/emulationstation/frontend/netplay'/name)==digest,'Test source drift')
    payload=WORK/'compiled-final/rooms-dex/classes.dex';need(sha(payload)==jr['roomsDexSHA256'],'Compiled DEX drift')
    need(sha(WORK/'compiled-final/client-dex/classes.dex')==jr['baseClientDexSHA256'],'Client DEX must remain identical')
    work=WORK/'package';need(not work.exists(),'Fresh package directory required')
    need(shutil.disk_usage(WORK).free>2*BASE.stat().st_size+256*1024**2,'Free space required')
    (work/'temp').mkdir(parents=True);(work/'evidence').mkdir()
    env=dict(os.environ,TEMP=str(work/'temp'),TMP=str(work/'temp'))
    for name in ['STATION_KS_PASS','STATION_KEY_PASS']:need(bool(env.get(name)),'Authorized original signing environment required')
    jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
    tools=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
    cert=subprocess.run([str(jdk/'keytool.exe'),'-exportcert','-keystore',str(KEY),'-alias','androiddebugkey','-storepass:env','STATION_KS_PASS'],env=env,capture_output=True)
    need(cert.returncode==0 and hashlib.sha256(cert.stdout).hexdigest()==CERT,'Original certificate required')
    def run(command,label):
        r=subprocess.run(list(map(str,command)),env=env,capture_output=True)
        (work/'evidence'/(label+'.private.log')).write_bytes(r.stdout+r.stderr);need(r.returncode==0,label)
        return (r.stdout+r.stderr).decode('utf8','replace')
    def signer(path,label):
        text=run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',path],label)
        need(re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([a-f0-9]{64})\s*$',text,re.M)==[CERT],'Certificate mismatch')
    signer(BASE,'base-certificate')
    unsigned=work/'unsigned-r81.apk';signed=work/'TurboStations-Premium-R81-20261008.apk'
    with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
        names=[n for n in old.namelist() if not signature(n)];need(len(names)==len(set(names))==13226,'Frozen inventory')
        need(zsha(old,'classes28.dex')==jr['clientDexSHA256'],'Base client mismatch')
        need(zsha(old,'classes35.dex')==jr['baseRoomsDexSHA256'],'Base rooms mismatch')
        for info in old.infolist():
            if signature(info.filename):continue
            item=copy.copy(info);item.extra=b''
            if item.filename=='classes35.dex':item.file_size=payload.stat().st_size
            if item.compress_type==zipfile.ZIP_STORED:
                align=16384 if item.filename.endswith('.so') else 4;offset=new.fp.tell()+30+len(item.filename.encode())
                if offset%align:pad=(-(offset+4))%align;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
            with new.open(item,'w') as output,(payload.open('rb') if item.filename=='classes35.dex' else old.open(info)) as input:
                shutil.copyfileobj(input,output,1024*1024)
    run([tools/'zipalign.exe','-c','-P','16','4',unsigned],'align-unsigned')
    run([jdk/'java.exe','-Djava.io.tmpdir='+str(work/'temp'),'-jar',tools/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',KEY,'--ks-key-alias','androiddebugkey','--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',signed,unsigned],'sign')
    signer(signed,'signed-certificate');run([tools/'zipalign.exe','-c','-P','16','4',signed],'align-signed')
    changes=[];videos={};preserved=0;protected={}
    with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(signed) as new:
        final=[n for n in new.namelist() if not signature(n)];need(len(final)==len(set(final)) and set(final)==set(names),'Entry set drift')
        for name in names:
            before,after=zsha(old,name),zsha(new,name)
            need(after==(jr['roomsDexSHA256'] if name=='classes35.dex' else before),'Unexpected change '+name)
            need(old.getinfo(name).compress_type==new.getinfo(name).compress_type,'Compression drift')
            if before==after:preserved+=1
            else:changes.append(name)
            if name.endswith('.mp4'):videos[name]=after
            if name in ['AndroidManifest.xml','assets/station-online/engines.json','lib/arm64-v8a/libstation_retroarch.so','lib/arm64-v8a/libstation_bsnes.so','lib/arm64-v8a/libstation_clownmdemu.so','lib/arm64-v8a/libturbo_carousel.so']:protected[name]=after
    need(changes==['classes35.dex'] and preserved==13225 and len(videos)==59,'Scope mismatch')
    receipt=dict(version='R81',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),temporaryApk=str(signed),sha256=sha(signed),bytes=signed.stat().st_size,baseSHA256=BASE_SHA,certificateSHA256=CERT,changes=changes,changedEntrySHA256={'classes35.dex':jr['roomsDexSHA256']},preservedEntries=preserved,totalVideos=len(videos),videoHashes=videos,protectedEntries=protected,allPackageEntriesVerified=True,alignment16KiB=True,javaReceiptSHA256=sha(WORK/'java-build-receipt.json'),recipeSHA256=sha(__file__),runtimeCoresEnginesUnchangedFromR79=True,archivedDreamcastEffectIncluded=False,serverV3ActivationStillRequired=True,installed=False)
    for p in [work/'evidence/package.json',ROOT/'evidence/package.json']:p.write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    need(unsigned.resolve().parent==work.resolve() and unsigned.name=='unsigned-r81.apk','Cleanup boundary');unsigned.unlink()
    print(json.dumps({k:v for k,v in receipt.items() if k!='videoHashes'},indent=2))
if __name__=='__main__':main()
