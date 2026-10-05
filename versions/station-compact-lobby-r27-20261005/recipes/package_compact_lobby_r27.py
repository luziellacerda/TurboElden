"""Assemble in E:, archive the final signed deliverable in G: to preserve disk headroom."""
from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile
W=Path(r'E:\ESTUDO APK\work\station-compact-lobby-r27-20261005')
B=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Layout-R26-20261005.apk')
O=B.parent/'TurboStations-Salas-Lista-R27-20261005.apk';U=W/'unsigned.apk'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(W)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
 with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def sig(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def run(args,name):
 r=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf8',errors='replace');(W/'evidence'/name).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-3000:];return r.stdout+r.stderr
basehash='1d4549da6a15a9a9b2e8c52491ecc4382e0b5e050900763aebf163d136a36e75'
assert sha(B)==basehash
assert not U.exists() and not O.exists()
assert shutil.disk_usage(W).free>B.stat().st_size+256*1024*1024
assert shutil.disk_usage(O.parent).free>B.stat().st_size*2+256*1024*1024
build=json.loads((W/'build/final/result.json').read_text('utf8'));tests=json.loads((W/'evidence/tests.json').read_text('utf8'));assert tests['passed']
for name,h in build['files'].items():assert sha(W/name)==h,name
for name,h in tests['sourceHashes'].items():assert sha(W/name)==h,name
dex=Path(build['dex']);assert sha(dex)==build['dexSHA256']
print('Packaging R26 + compact lobby; preserving native layout and every other payload',flush=True)
with zipfile.ZipFile(B) as old,zipfile.ZipFile(U,'w',allowZip64=True) as out:
 assert zsha(old,'classes35.dex')=='8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae'
 for info in old.infolist():
  if sig(info.filename):continue
  entry=copy.copy(info);entry.extra=b'';replace=info.filename=='classes35.dex';entry.file_size=dex.stat().st_size if replace else info.file_size
  if entry.compress_type==zipfile.ZIP_STORED:
   alignment=16384 if entry.filename.endswith('.so') else 4;offset=out.fp.tell()+30+len(entry.filename.encode())
   if offset%alignment:pad=(-(offset+4))%alignment;entry.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
  with out.open(entry,'w') as dst:
   with (dex.open('rb') if replace else old.open(info)) as src:shutil.copyfileobj(src,dst,1024*1024)
run([BT/'zipalign.exe','-c','-P','16','4',U],'unsigned-alignment.log')
print('Signing the new deliverable directly into the verified archive directory',flush=True)
run([J/'java.exe','-Djava.io.tmpdir='+str(W),'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',O,U],'sign.log')
cert='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert cert in run([J/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',O],'signature.log')
run([BT/'zipalign.exe','-c','-P','16','4',O],'alignment.log')
print('Verifying complete package payloads',flush=True)
changed=[];preserved=0
with zipfile.ZipFile(B) as old,zipfile.ZipFile(O) as new:
 names={n for n in old.namelist() if not sig(n)};assert names=={n for n in new.namelist() if not sig(n)};assert len(new.namelist())==len(set(new.namelist()))
 for name in sorted(names):
  before,after=zsha(old,name),zsha(new,name)
  if before==after:preserved+=1
  else:assert name=='classes35.dex' and after==sha(dex);changed.append(name)
  assert old.getinfo(name).compress_type==new.getinfo(name).compress_type,name
 assert changed==['classes35.dex']
 native=zsha(new,'lib/arm64-v8a/libturbo_carousel.so');assert native=='b2d706dc07d4423758798fe0d6d37ce01c8f395b344c685a7b796ce60d03dd70'
record={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':str(B),'baseSHA256':basehash,'apk':str(O),'sha256':sha(O),'bytes':O.stat().st_size,'changed':changed,'preservedEntries':preserved,'roomsDexSHA256':sha(dex),'carouselSO':native,'certificateSHA256':cert,'allPackageEntriesVerified':True,'alignment16KiB':True,'installed':False,'visualAndroidVerified':False,'twoDeviceGameplayVerified':False,'serverChanged':False,'stable':False}
(W/'build-result.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
# The only deletion is this revision's temporary unsigned package after the final checks.
assert U.resolve().parent==W.resolve() and U.name=='unsigned.apk';U.unlink()
print(json.dumps(record,indent=2))
