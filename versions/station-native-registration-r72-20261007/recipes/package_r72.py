"""Replace only DEX35 over exact R71, verify every other entry, sign with existing credentials."""
from pathlib import Path
import argparse,copy,datetime,hashlib,importlib.util,json,os,shutil,struct,subprocess,sys,zipfile
from build_candidate import SNAPSHOT,DEFAULT_WORK,BASE_APK,BASE_SHA256,CLIENT_DEX_SHA256,BASE_ROOMS_DEX_SHA256,verified_sources,sha,zsha,require,R67,R67_IDENTITIES
p=argparse.ArgumentParser();p.add_argument('--workspace',default=DEFAULT_WORK);p.add_argument('--output',default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R72-20261007.apk');a=p.parse_args()
w=Path(a.workspace);output=Path(a.output);require(w.drive.upper()=='E:' and output.drive.upper()=='G:','E build/G output required')
require(not output.exists(),'Never overwrite an existing APK')
base=BASE_APK;require(sha(base)==BASE_SHA256,'Exact R71 complete base required')
_,_,sources,manifest=verified_sources();source_hashes={n:sha(f) for n,f in sorted(sources.items())}
build_path=w/'evidence/build.json';build=json.loads(build_path.read_text('utf8'));tests_path=w/'evidence/local-tests.json';tests=json.loads(tests_path.read_text('utf8'))
require(build['sourceHashes']==source_hashes==tests['sourceHashes'],'Compiled/tested sources differ')
require(tests['success'] and tests['countedChecks']==1181 and tests['productionSourceCount']==198,'All R72 tests required')
require(tests['buildReceiptSHA256']==sha(build_path),'Tests target another build')
dex=w/'java/build/rooms-dex/classes.dex';require(sha(dex)==build['roomsDexSHA256']==tests['roomsDexSHA256'],'DEX35 mismatch')
require(build['clientDexSHA256']==tests['clientDexSHA256']==CLIENT_DEX_SHA256 and build['clientDexUnchanged'],'Client must remain R71')
require(build['changedDexSlots']==['classes35.dex'],'Only DEX35 may change')
tools=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');cert='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
env=dict(os.environ,TEMP=str(w/'temp'),TMP=str(w/'temp'))
for k in ['STATION_KEYSTORE','STATION_KEY_ALIAS','STATION_KS_PASS','STATION_KEY_PASS']:require(bool(env.get(k)),'Missing signing environment '+k)
def run(args,label):
 r=subprocess.run(list(map(str,args)),env=env,capture_output=True)
 (w/'evidence'/f'{label}.log').write_bytes(r.stdout+r.stderr)
 require(r.returncode==0,'Operation failed; inspect private log '+label)
 return (r.stdout+r.stderr).decode('utf8','replace')
cert_bytes=subprocess.check_output([str(jdk/'keytool.exe'),'-exportcert','-keystore',env['STATION_KEYSTORE'],'-alias',env['STATION_KEY_ALIAS'],'-storepass:env','STATION_KS_PASS'],env=env,stderr=subprocess.DEVNULL)
require(hashlib.sha256(cert_bytes).hexdigest()==cert,'Signing identity must equal existing APK certificate')
require(cert in run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',base],'base-cert'),'Base signer differs')
gpath=R67/'recipes/dex_gates.py';require(sha(gpath)==R67_IDENTITIES['recipes/dex_gates.py'],'DEX gate changed')
spec=importlib.util.spec_from_file_location('r72_dex_gates',gpath);gates=importlib.util.module_from_spec(spec);spec.loader.exec_module(gates)
def signature(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
unsigned=w/'unsigned.apk';require(not unsigned.exists(),'Unsigned candidate already exists')
require(shutil.disk_usage(w).free>base.stat().st_size+64*1024**2 and shutil.disk_usage(output.parent).free>base.stat().st_size+64*1024**2,'Packaging space insufficient')
with zipfile.ZipFile(base) as old:
 require(len(old.namelist())==len(set(old.namelist())),'Duplicate base entry')
 require(zsha(old,'classes35.dex')==BASE_ROOMS_DEX_SHA256 and zsha(old,'classes28.dex')==CLIENT_DEX_SHA256,'Base modules differ')
 gate=gates.verify_modules(old,{'classes35.dex':dex.read_bytes()})
 print('Packaging exact R71 plus DEX35; all native engines and media preserved',flush=True)
 with zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
  for info in old.infolist():
   if signature(info.filename):continue
   item=copy.copy(info);item.extra=b''
   if item.filename=='classes35.dex':item.file_size=dex.stat().st_size
   if item.compress_type==zipfile.ZIP_STORED:
    alignment=16384 if item.filename.endswith('.so') else 4
    offset=new.fp.tell()+30+len(item.filename.encode('utf8'))
    if offset%alignment:
     pad=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
   with new.open(item,'w') as dst:
    with (dex.open('rb') if item.filename=='classes35.dex' else old.open(info)) as src:shutil.copyfileobj(src,dst,1024*1024)
run([tools/'zipalign.exe','-c','-P','16','4',unsigned],'unsigned-align')
run([jdk/'java.exe','-Djava.io.tmpdir='+str(w/'temp'),'-jar',tools/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',env['STATION_KEYSTORE'],'--ks-key-alias',env['STATION_KEY_ALIAS'],'--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',output,unsigned],'sign')
require(cert in run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',output],'cert'),'Output signer differs')
run([tools/'zipalign.exe','-c','-P','16','4',output],'alignment')
changed=[];preserved=0
with zipfile.ZipFile(base) as old,zipfile.ZipFile(output) as new:
 names={n for n in old.namelist() if not signature(n)};require(names=={n for n in new.namelist() if not signature(n)},'APK entries added or removed')
 require(len(new.namelist())==len(set(new.namelist())),'Duplicate output entry')
 for n in sorted(names):
  prior=zsha(old,n);got=zsha(new,n);expected=sha(dex) if n=='classes35.dex' else prior
  require(got==expected and old.getinfo(n).compress_type==new.getinfo(n).compress_type,'Entry differs '+n)
  if got!=prior:changed.append(n)
  else:preserved+=1
 require(changed==['classes35.dex'],'Unexpected change list')
 require(gates.verify_modules(new,{})==gate,'Final DEX gate differs')
 runtime=zsha(new,'lib/arm64-v8a/libstation_retroarch.so');engines=zsha(new,'assets/station-online/engines.json')
 require(runtime=='d66267cd42507388f86034deb47e9f9670875784efb9afabfb8ffc64e3f3a856','Native runtime changed')
require({n:sha(f) for n,f in sources.items()}==source_hashes,'Sources changed during package')
receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),apk=str(output),sha256=sha(output),bytes=output.stat().st_size,baseSHA256=BASE_SHA256,changed=changed,added=[],preservedEntries=preserved,allPackageEntriesVerified=True,certificateSHA256=cert,alignment16KiB=True,classGate=gate,clientDexUnchanged=True,clientDexSHA256=CLIENT_DEX_SHA256,roomsDexSHA256=sha(dex),runtimeSHA256=runtime,engineManifestSHA256=engines,enginesUnchanged=True,allOtherDexAndNativeLibrariesPreserved=True,totalVideos=58,buildReceiptSHA256=sha(build_path),testReceiptSHA256=sha(tests_path),packageRecipeSHA256=sha(__file__),installed=False,androidGameplay=False,stable=False)
(w/'evidence/package.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
require(unsigned.resolve().parent==w.resolve() and unsigned.name=='unsigned.apk','Unexpected temp path');unsigned.unlink()
print(json.dumps(receipt,indent=2))
