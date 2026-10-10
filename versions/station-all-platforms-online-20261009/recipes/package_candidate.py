"""Make the complete signed platform candidate from the exact private R81 APK.

Replace rooms DEX, native runtime and engine manifest; add uniquely named cores
and platform overlays. Preserve all previous offline cores, games,
media, other cores, identity and resources. Signing credentials stay on the APK
production PC; this recipe never installs, clears data or selects a latest file.
"""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, os, re, shutil, struct, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='85fac8f51daa3a370eabb14d98832f75c2f30ff81422c549538ee715627032c6'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'

def need(ok,message):
    if not ok:raise RuntimeError(message)
def sha(path):
    with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def zsha(archive,name):
    with archive.open(name) as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def signature(name):return name.startswith('META-INF/') and name.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base-apk','work','jdk','build-tools','keystore'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--key-alias',default='androiddebugkey')
    args=parser.parse_args()
    need(sha(args.base_apk)==BASE_SHA,'Exact R81 complete base required; no historical overlay')
    need(args.work.is_absolute() and not args.work.exists(),'Fresh absolute package directory required')
    if os.name=='nt':need(args.work.drive.upper()=='E:','Use E: for production build output')
    java=json.loads((ROOT/'evidence/java-build.json').read_text())
    native=json.loads((ROOT/'evidence/native-build.json').read_text())
    need(java['compiled'] and java['sourceCount']==212 and native['compiled'],'Complete compiled inputs required')
    for name,digest in java['sourceHashes'].items():need(sha(ROOT/'java'/name)==digest,'Source drift: '+name)
    changes={'classes35.dex':ROOT/'compiled/rooms.dex',
        'lib/arm64-v8a/libstation_retroarch.so':ROOT/'native/libstation_retroarch.so',
        'assets/station-online/engines.json':ROOT/'assets/station-online/engines.json'}
    core_builds=json.loads((ROOT/'evidence/core-builds.json').read_text())
    for core in core_builds['cores']:
        source=ROOT/'native'/core['library']
        need(core['compiled'] and sha(source)==core['sha256'],'Compiled core drift')
        need(core['elfLoadAlignmentMinimum']>=16384,'16 KiB core alignment required')
        need(sha(ROOT/core['sourceArchive'])==core['sourceArchiveSHA256'],'Corresponding source drift')
        for patch in core.get('patches',[]):need(sha(ROOT/patch['path'])==patch['sha256'],'Corresponding source patch drift')
        changes['lib/arm64-v8a/'+core['library']]=source
    for source in sorted((ROOT/'assets/station-online').rglob('*')):
        if source.is_file():changes['assets/'+source.relative_to(ROOT/'assets').as_posix()]=source
    need(sha(changes['classes35.dex'])==java['roomsDexSHA256'],'Rooms DEX drift')
    need(sha(ROOT/'compiled/client.dex')==java['clientDexSHA256'],'Client DEX drift')
    need(sha(changes['lib/arm64-v8a/libstation_retroarch.so'])==native['runtimeSHA256'],'Runtime drift')
    engines=json.loads(changes['assets/station-online/engines.json'].read_text())
    need(engines['maximumPlayers']==5 and all(e['runtimeSha256']==native['runtimeSHA256'] for e in engines['engines']),'Engine/runtime binding drift')
    need(json.loads((ROOT/'evidence/profile-tests.json').read_text())['passed'],'Player classification checks required')
    lobby=json.loads((ROOT/'evidence/lobby-recovery-tests.json').read_text())
    need(lobby['passed'] and lobby['checks']==36 and lobby['sourceHashes']==java['sourceHashes'],'Lobby recovery checks must match the complete compiled source set')
    need(lobby['fixtureSHA256']==sha(ROOT/'tests/StationLobbyRecoveryTest.java.in') and lobby['recipeSHA256']==sha(ROOT/'recipes/test_lobby_recovery.py'),'Lobby recovery test inputs changed')
    need(json.loads((ROOT.parent/'station-five-player-support-20261009/native/tests/native-result.json').read_text())['passed'],'Unchanged runtime ownership checks required')
    need(json.loads((ROOT/'evidence/bios-tests.json').read_text())['passed'],'Firmware isolation checks required')
    identity=json.loads((ROOT/'evidence/content-identity-tests.json').read_text())
    need(identity['passed'] and identity['sourceSHA256']==sha(ROOT/'java/netplay-src/org/emulationstation/frontend/netplay/StationContentIdentity.java'),'Portable CUE identity checks required')
    env=dict(os.environ)
    for name in ('STATION_KS_PASS','STATION_KEY_PASS'):need(bool(env.get(name)),'Original private signing environment required')
    need(shutil.disk_usage(args.work.parent).free>args.base_apk.stat().st_size*3+268435456,'Package/alignment/signing free space required')
    (args.work/'temp').mkdir(parents=True);(args.work/'evidence').mkdir()
    env.update(TEMP=str(args.work/'temp'),TMP=str(args.work/'temp'))
    suffix='.exe' if os.name=='nt' else ''
    java_bin=args.jdk/('java'+suffix);zipalign=args.build_tools/('zipalign'+suffix)
    signer=args.build_tools/'lib/apksigner.jar'
    def run(command,label):
        result=subprocess.run(list(map(str,command)),env=env,capture_output=True)
        (args.work/'evidence'/(label+'.private.log')).write_bytes(result.stdout+result.stderr)
        need(result.returncode==0,label+' failed; inspect local private log')
        return (result.stdout+result.stderr).decode('utf8','replace')
    def certificate(path,label):
        value=run([java_bin,'-jar',signer,'verify','--print-certs',path],label)
        need(re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([a-f0-9]{64})\s*$',value,re.M)==[CERT],'Original certificate required')
    certificate(args.base_apk,'base-certificate')
    unsigned=args.work/'unsigned-platforms.apk';aligned=args.work/'aligned-platforms.apk';signed=args.work/'TurboStations-Premium-Platforms-Candidate-20261009.apk'
    with zipfile.ZipFile(args.base_apk) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
        names=[n for n in old.namelist() if not signature(n)]
        need(len(names)==len(set(names))==13226,'Frozen R81 inventory required')
        need(zsha(old,'classes28.dex')==java['clientDexSHA256'],'Preserved client DEX mismatch')
        for engine in engines['engines']:
            entry='lib/arm64-v8a/'+engine['library']
            need((sha(changes[entry]) if entry in changes else zsha(old,entry))==engine['coreSha256'],'Core hash mismatch')
        additions={name:path for name,path in changes.items() if name not in names}
        need(all(name.startswith(('lib/arm64-v8a/libstation_online_','assets/station-online/overlays/station-platforms/','assets/station-online/licenses/')) for name in additions),'Unexpected new namespace')
        for entry in old.infolist():
            if signature(entry.filename):continue
            item=copy.copy(entry);item.extra=b''
            replacement=changes.get(item.filename)
            if replacement:item.file_size=replacement.stat().st_size
            if item.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if item.filename.endswith('.so') else 4
                offset=new.fp.tell()+30+len(item.filename.encode())
                if offset%alignment:padding=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,padding)+bytes(padding)
            with new.open(item,'w') as output,(replacement.open('rb') if replacement else old.open(entry)) as source:shutil.copyfileobj(source,output,1048576)
        for name,source in additions.items():
            item=zipfile.ZipInfo(name,(2026,10,9,0,0,0));item.compress_type=zipfile.ZIP_STORED if name.endswith('.so') else zipfile.ZIP_DEFLATED
            item.file_size=source.stat().st_size
            with new.open(item,'w') as output,source.open('rb') as input:shutil.copyfileobj(input,output,1048576)
    # zipalign also checks deflated/unusual legacy entries in the full base.
    run([zipalign,'-P','16','4',unsigned,aligned],'align')
    run([java_bin,'-jar',signer,'sign','--alignment-preserved','true','--v4-signing-enabled','false',
        '--ks',args.keystore,'--ks-key-alias',args.key_alias,'--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',signed,aligned],'sign')
    certificate(signed,'signed-certificate');run([zipalign,'-c','-P','16','4',signed],'aligned-signed-check')
    preserved=0
    with zipfile.ZipFile(args.base_apk) as old,zipfile.ZipFile(signed) as new:
        final=[n for n in new.namelist() if not signature(n)]
        need(len(final)==len(set(final)) and set(final)==set(names)|set(additions),'Entry set drift')
        for name in names:
            before=zsha(old,name);after=zsha(new,name)
            need(after==(sha(changes[name]) if name in changes else before),'Unexpected changed bytes: '+name)
            need(old.getinfo(name).compress_type==new.getinfo(name).compress_type,'Compression changed: '+name)
            if before==after:preserved+=1
        for name,path in additions.items():need(zsha(new,name)==sha(path),'New entry drift: '+name)
    receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),apkBuilt=True,installed=False,fivePhoneGameplayVerified=False,
        apkSHA256=sha(signed),apkBytes=signed.stat().st_size,baseSHA256=BASE_SHA,signingCertificateSHA256=CERT,
        changedEntries={name:sha(path) for name,path in changes.items()},preservedEntries=preserved,
        originalEntrySetPreserved=True,addedEntries={name:sha(path) for name,path in additions.items()},compressionPreserved=True,alignment16KiB=True,allOtherCoresGamesMediaManifestAndLicenseCodePreserved=True,
        sourceReceiptSHA256=sha(ROOT/'evidence/java-build.json'),nativeReceiptSHA256=sha(ROOT/'evidence/native-build.json'),recipeSHA256=sha(__file__))
    (args.work/'evidence/package.json').write_text(json.dumps(receipt,indent=2)+'\n')
    unsigned.unlink();aligned.unlink()
    print(json.dumps(receipt))

if __name__=='__main__':main()
