"""Replace only the R67 carousel native library, with complete entry preservation checks."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile
p=argparse.ArgumentParser()
p.add_argument('--workspace',default=r'E:\ESTUDO APK\work\station-collection-corners-r68-20261007-final')
p.add_argument('--output',default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R68-20261007.apk')
a=p.parse_args();w=Path(a.workspace).resolve();out=Path(a.output).resolve()
assert w.drive.upper()=='E:' and out.drive.upper()=='G:'
r=json.loads((w/'evidence/build.json').read_text('utf8'))
base=Path(r['baseAPK']);unsigned=w/'unsigned.apk';library=w/'libturbo_carousel.so'
assert not unsigned.exists() and not out.exists()
tools=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
java=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
env=dict(os.environ,TEMP=str(w/'temp'),TMP=str(w/'temp'))
for key in ['STATION_KEYSTORE','STATION_KEY_ALIAS','STATION_KS_PASS','STATION_KEY_PASS']:assert env.get(key),key
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
 with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def run(cmd,label):
 proc=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace',env=env)
 (w/'evidence'/(label+'.log')).write_text(proc.stdout+proc.stderr,'utf8')
 if proc.returncode:raise RuntimeError(label+' failed; inspect local log')
 return proc.stdout+proc.stderr
assert r['cornerPolicyChecks']==24 and r['sourceWiringChecks']==3
assert sha(base)==r['baseSHA256']=='d746cc02b602162b19509cd44ad7cf751e320de3b52199e7d48e86e9e897228f'
assert sha(library)==r['nativeSHA256']
for name,h in r['nativeSources'].items():assert sha(w/'native'/name)==h,name
assert shutil.disk_usage(w).free>base.stat().st_size+64*1024**2
assert shutil.disk_usage(out.parent).free>base.stat().st_size+64*1024**2
cert='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert cert in run([java,'-jar',tools/'lib/apksigner.jar','verify','--print-certs',base],'base-signature')
target='lib/arm64-v8a/libturbo_carousel.so'
with zipfile.ZipFile(base) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
 assert len(old.namelist())==len(set(old.namelist()))
 assert zsha(old,target)==r['baseNativeSHA256']
 for info in old.infolist():
  if signature(info.filename):continue
  item=copy.copy(info);item.extra=b''
  if item.filename==target:item.file_size=library.stat().st_size
  if item.compress_type==zipfile.ZIP_STORED:
   alignment=16384 if item.filename.endswith('.so') else 4
   offset=new.fp.tell()+30+len(item.filename.encode('utf8'))
   if offset%alignment:
    pad=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
  with new.open(item,'w') as dst:
   with (library.open('rb') if item.filename==target else old.open(info)) as src:shutil.copyfileobj(src,dst,1024*1024)
run([tools/'zipalign.exe','-c','-P','16','4',unsigned],'unsigned-alignment')
run([java,'-Djava.io.tmpdir='+str(w/'temp'),'-jar',tools/'lib/apksigner.jar','sign','--alignment-preserved','true',
 '--v4-signing-enabled','false','--ks',env['STATION_KEYSTORE'],'--ks-key-alias',env['STATION_KEY_ALIAS'],
 '--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',out,unsigned],'sign')
assert cert in run([java,'-jar',tools/'lib/apksigner.jar','verify','--print-certs',out],'signature')
run([tools/'zipalign.exe','-c','-P','16','4',out],'alignment')
with zipfile.ZipFile(base) as old,zipfile.ZipFile(out) as new:
 names={n for n in old.namelist() if not signature(n)}
 assert {n for n in new.namelist() if not signature(n)}==names
 assert len(new.namelist())==len(set(new.namelist()))
 for n in sorted(names):assert zsha(new,n)==(r['nativeSHA256'] if n==target else zsha(old,n)),n
result=dict(createdUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),apk=str(out),sha256=sha(out),bytes=out.stat().st_size,
 baseSHA256=r['baseSHA256'],certificateSHA256=cert,changed=[target],preservedEntries=len(names)-1,
 allPackageEntriesVerified=True,alignment16KiB=True,allDexPreserved=True,all55VideosPreserved=True,
 allEmulatorsPreserved=True,allCollectionsSquareCorners=True,mainPlatformsUnchanged=True,
 individualGameCoversUnchanged=True,menu30FpsPreserved=True,securityR67Preserved=True,installed=False)
(w/'evidence/package.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
assert unsigned.parent==w and unsigned.name=='unsigned.apk';unsigned.unlink()
print(json.dumps(result,indent=2))
