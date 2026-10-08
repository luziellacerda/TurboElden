"""Package the tested R76 transport DEX over the exact R75 visual APK."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, os, shutil, struct, subprocess, zipfile

SNAPSHOT = Path(__file__).resolve().parent.parent
BASE = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R75-20261007.apk')
BASE_SHA = '1ab4fa3770570832ea5ff2e9b0ce4f8a26e0e24e210ad7652f4c96647fecad32'
OLD_DEX = 'e8c57484aa2e566edf6226a02e1f5f8ba7f9c25c7f6b050b890a092637370d3c'
CERT = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
ENTRY = 'classes35.dex'
PRESERVED = {
 'lib/arm64-v8a/libstation_retroarch.so': '804b2acfea4c6d615bf40dba30e1777015098bf7375d0745db8d117555eb2516',
 'lib/arm64-v8a/libturbo_carousel.so': '3c2e22bc94f3432280e2b08c2f26ab33508cd1278ee9bd750b48d45c35105a8b',
 'classes28.dex': '1a04582a02804ecbe4b075dd487118a171b0b0f305dbb8884015bbede09b25d7',
 'AndroidManifest.xml': '3a821dccd8a9853acd345f106614ec955bbf66b681b7690f907348569e8bef0d',
 'assets/station-online/engines.json': 'd43d6af1581691fbf88d6a15f87bea66761ef2f4d8952857028c6541b908e985',
}

def sha(p):
 with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def zsha(z, n):
 with z.open(n) as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def require(ok, message):
 if not ok: raise RuntimeError(message)
def signature(n): return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--workspace',default=r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008')
 p.add_argument('--output',default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R76-20261008.apk')
 a=p.parse_args(); w=Path(a.workspace).resolve(); output=Path(a.output).resolve()
 require(w.drive.upper()=='E:' and output.drive.upper()=='G:', 'Build E:, final G: required')
 require(not output.exists(), 'Never overwrite a previous APK')
 require(sha(BASE)==BASE_SHA, 'Exact R75 required')
 native=w/'compiled-final'; build_file=native/'evidence/build.json'
 build=json.loads(build_file.read_text('utf8')); so=native/'java/build/rooms-dex/classes.dex'
 require(build['compiled'] and sha(so)==build['roomsDexSHA256']!=OLD_DEX,'DEX build identity')
 sources={n:sha(native/'java'/n) for n in build['sourceHashes']}
 require(sources==build['sourceHashes'],'Built source drift')
 require(build['changedSources']==['netplay-src/org/emulationstation/frontend/netplay/StationRecoveryTunnel.java'],'Unexpected production change')
 manifest=json.loads((SNAPSHOT/'JAVA-OVERLAY-MANIFEST.json').read_text('utf8'))
 require(all(sha(SNAPSHOT/'java'/n)==h==sources[n] for n,h in manifest['files'].items()),'Source overlay drift')
 test_file=native/'evidence/local-tests.json';tests=json.loads(test_file.read_text('utf8'))
 require(tests['success'] and tests['sourceHashes']==sources and tests['countedChecks']==1206,'Regression tests stale')
 session=json.loads((w/'session-tests/test-receipt.json').read_text('utf8'))
 require(session['localChecks']==101 and session['sourceGuardCount']==42 and session['buildReceiptSHA256']==sha(build_file),'Session tests stale')
 gates=json.loads((SNAPSHOT/'evidence/package-gates.json').read_text('utf8'))
 require(gates['reviewed'] and gates['buildReceiptSHA256']==sha(build_file),'Reviewed transport gates missing')
 for item in gates['receipts']:
  require(sha(Path(item['path']))==item['sha256'],'Qualification receipt changed')
 recipe_sha=sha(__file__)
 with zipfile.ZipFile(BASE) as z:
  require(zsha(z,ENTRY)==OLD_DEX,'R75 rooms DEX mismatch')
  for n,h in PRESERVED.items(): require(zsha(z,n)==h,'R75 protected entry differs: '+n)
  require(len(z.namelist())==len(set(z.namelist())),'Duplicate input entries')

 tools=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
 jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
 evidence=w/'evidence'; evidence.mkdir(exist_ok=True)
 temp=w/'temp';temp.mkdir(exist_ok=True);env=dict(os.environ,TEMP=str(temp),TMP=str(temp))
 for key in ('STATION_KEYSTORE','STATION_KEY_ALIAS','STATION_KS_PASS','STATION_KEY_PASS'):
  require(bool(env.get(key)), 'Existing signing environment required: '+key)
 def run(command,label):
  r=subprocess.run(list(map(str,command)),capture_output=True,env=env)
  (evidence/('package-'+label+'-private.log')).write_bytes(r.stdout+r.stderr)
  require(r.returncode==0,'See private package log: '+label)
  return (r.stdout+r.stderr).decode('utf8','replace')
 cert=subprocess.run([str(jdk/'keytool.exe'),'-exportcert','-keystore',env['STATION_KEYSTORE'],'-alias',env['STATION_KEY_ALIAS'],'-storepass:env','STATION_KS_PASS'],capture_output=True,env=env)
 require(cert.returncode==0 and hashlib.sha256(cert.stdout).hexdigest()==CERT,'Existing signing key must match installed certificate')
 require(CERT in run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',BASE],'base-cert'),'Base signer mismatch')
 unsigned=w/'unsigned-r76.apk';signed=w/'signed-r76.apk'
 require(not unsigned.exists() and not signed.exists(),'Packaging attempt files already exist')
 require(shutil.disk_usage(w).free>2*BASE.stat().st_size+128*1024**2 and shutil.disk_usage(output.parent).free>BASE.stat().st_size+64*1024**2,'Insufficient space')
 with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
  for info in old.infolist():
   if signature(info.filename):continue
   item=copy.copy(info);item.extra=b''
   if item.filename==ENTRY:item.file_size=so.stat().st_size
   if item.compress_type==zipfile.ZIP_STORED:
    alignment=16384 if item.filename.endswith('.so') else 4
    offset=new.fp.tell()+30+len(item.filename.encode('utf8'))
    if offset%alignment:
     pad=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
   with new.open(item,'w') as dst:
    with (so.open('rb') if item.filename==ENTRY else old.open(info)) as src:shutil.copyfileobj(src,dst,1024*1024)
 run([tools/'zipalign.exe','-c','-P','16','4',unsigned],'unsigned-alignment')
 run([jdk/'java.exe','-Djava.io.tmpdir='+str(temp),'-jar',tools/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',env['STATION_KEYSTORE'],'--ks-key-alias',env['STATION_KEY_ALIAS'],'--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',signed,unsigned],'sign')
 require(CERT in run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',signed],'signed-cert'),'Signed certificate mismatch')
 run([tools/'zipalign.exe','-c','-P','16','4',signed],'signed-alignment')
 changed=[];preserved=0;video_hashes={}
 with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(signed) as new:
  names={n for n in old.namelist() if not signature(n)}
  require(names=={n for n in new.namelist() if not signature(n)},'Entries added/removed')
  require(len(new.namelist())==len(set(new.namelist())),'Duplicate final entries')
  for n in sorted(names):
   before=zsha(old,n);after=zsha(new,n)
   require(after==(build['roomsDexSHA256'] if n==ENTRY else before),'Unexpected entry change: '+n)
   require(old.getinfo(n).compress_type==new.getinfo(n).compress_type,'Compression changed: '+n)
   if before!=after:changed.append(n)
   else:preserved+=1
   if n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4'):video_hashes[n]=after
  require(changed==[ENTRY] and len(video_hashes)==58,'Only the rooms DEX may change; 58 carousel MP4 required')
  require(sum(n.endswith('.mp4') for n in names)==59,'Total MP4 count mismatch')
 require(sha(so)==build['roomsDexSHA256'] and sha(__file__)==recipe_sha,'Package inputs changed')
 digest=sha(signed)
 with output.open('xb') as dst,signed.open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
 require(sha(output)==digest,'Final G: copy mismatch')
 record=dict(version='R76',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),apk=str(output),sha256=digest,bytes=output.stat().st_size,
  baseSHA256=BASE_SHA,changed=changed,added=[],preservedEntries=preserved,allPackageEntriesVerified=True,
  certificateSHA256=CERT,alignment16KiB=True,roomsDexSHA256=build['roomsDexSHA256'],protectedEntries=PRESERVED,
  allMediaPreserved=True,totalVideos=59,carouselVideos=58,carouselVideoHashes=video_hashes,
  runtimeOnlineUnchanged=True,serverRegistryChangeRequired=False,javaBuildReceiptSHA256=sha(build_file),
  testReceiptSHA256=sha(test_file),packageRecipeSHA256=recipe_sha,installed=False,visualPlaybackVerified=False)
 (evidence/'package.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
 for f in (unsigned,signed):
  require(f.resolve().parent==w and f.name in ('unsigned-r76.apk','signed-r76.apk'),'Unexpected cleanup path')
  f.unlink()
 print(json.dumps({k:v for k,v in record.items() if k!='carouselVideoHashes'},indent=2))

if __name__=='__main__':main()
