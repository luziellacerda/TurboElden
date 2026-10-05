import os
from pathlib import Path
import zipfile,struct,shutil,hashlib,subprocess,json,os,copy,datetime
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=Path(os.environ['STATION_EMULATORS_WORK']);N=Path(os.environ['STATION_N64_WORK'])
B=Path(os.environ['STATION_BASE_APK']);O=W/'TurboStations-NeoGeo-N64-R15-20261005.apk';U=W/'unsigned.apk'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(W)
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
 with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def sig(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def run(args,name):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/(name+'.log')).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(r.stdout+r.stderr)[-4000:];return r.stdout+r.stderr
bh='661a8738faf2e598d448017bcb87f09e7d39ac7d2984a653fac4e9a642a9742f';assert sha(B)==bh
assert not U.exists() and not O.exists();assert shutil.disk_usage(W).free>B.stat().st_size*2+120*1024*1024
repl={'classes.dex':N/'classes.dex','classes30.dex':W/'classes30.dex','classes38.dex':N/'classes38.dex','lib/arm64-v8a/libturbo_carousel.so':N/'frontend-native/libturbo_carousel.so'}
repl.update({'lib/arm64-v8a/'+p.name:p for p in (N/'native-libs').glob('*.so')})
memory={}
with zipfile.ZipFile(B) as old,zipfile.ZipFile(N/'n64-resources-dex.apk') as new:
 assert zsha(old,'classes.dex')==json.loads((N/'application/receipt.json').read_text())['baseDexSHA256']
 for name in ('AndroidManifest.xml','resources.arsc','classes36.dex','classes37.dex'):memory[name]=new.read(name)
 for name in new.namelist():
  if (name.startswith('res/') and name not in old.namelist()) or name.startswith('assets/mupen64plus_data/'):
   assert name not in old.namelist();memory[name]=new.read(name)
 # Donor baseline profiles reference its original dex partition; do not overwrite Station profiles.
 assert not any(k.startswith('assets/dexopt/') for k in memory)
 def put(out,name,info=None):
  data=memory.get(name);path=repl.get(name);size=len(data) if data is not None else path.stat().st_size if path else info.file_size
  item=copy.copy(info) if info else zipfile.ZipInfo(name);item.extra=b'';item.file_size=size
  if not info:item.compress_type=zipfile.ZIP_STORED if name.endswith(('.so','.dex','.arsc')) else zipfile.ZIP_DEFLATED
  if item.compress_type==zipfile.ZIP_STORED:
   alignment=16384 if name.endswith('.so') else 4;off=out.fp.tell()+30+len(name.encode())
   if off%alignment:pad=(-(off+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
  with out.open(item,'w') as dst:
   if data is not None:dst.write(data)
   elif path:
    with path.open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
   else:
    with old.open(info) as src:shutil.copyfileobj(src,dst,1024*1024)
 print('Packaging verified R14B + Neo Geo correction + complete N64',flush=True)
 with zipfile.ZipFile(U,'w',allowZip64=True) as out:
  seen=set()
  for info in old.infolist():
   if sig(info.filename):continue
   put(out,info.filename,info);seen.add(info.filename)
  for name in sorted(set(memory)|set(repl)):
   if name not in seen:put(out,name)
run([BT/'zipalign.exe','-c','-P','16','4',U],'unsigned-alignment')
print('Aligned at write time; signing with original certificate',flush=True)
run([J/'java.exe','-Djava.io.tmpdir='+str(W),'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',O,U],'sign')
cert='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert cert in run([J/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',O],'signature')
run([BT/'zipalign.exe','-c','-P','16','4',O],'alignment')
preserved=0;changes=[];added=[]
print('Signed; checking every entry against base and compiled inputs',flush=True)
with zipfile.ZipFile(B) as a,zipfile.ZipFile(O) as b:
 assert len(b.namelist())==len(set(b.namelist()));before={x for x in a.namelist() if not sig(x)};after={x for x in b.namelist() if not sig(x)};assert before<=after
 for name in sorted(after):
  got=zsha(b,name)
  if name in repl:assert got==sha(repl[name]),name
  elif name in memory:assert got==hashlib.sha256(memory[name]).hexdigest(),name
  else:assert got==zsha(a,name),name
  if name not in before:added.append(name)
  elif got!=zsha(a,name):changes.append(name)
  else:preserved+=1
 check_rooms=zsha(b,'classes35.dex');assert check_rooms=='8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae'
 assert set(changes)=={'classes.dex','classes30.dex','AndroidManifest.xml','resources.arsc','lib/arm64-v8a/libturbo_carousel.so'},changes
result={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':str(B),'baseSHA256':bh,'baseArchivedFrom':str(R/B.name),'apk':str(O),'sha256':sha(O),'bytes':O.stat().st_size,'certificateSHA256':cert,'changed':changes,'added':added,'preservedEntries':preserved,'roomsDexSHA256':check_rooms,'allEntriesVerified':True,'alignment16KiB':True,'installed':False,'gameplayVerified':False,'stable':False}
(W/'build-result.json').write_text(json.dumps(result,indent=2),'utf8')
assert U.resolve().parent==W.resolve() and U.name=='unsigned.apk';U.unlink()
print(json.dumps({k:v for k,v in result.items() if k!='added'},indent=2));print('Added entries',len(added))
