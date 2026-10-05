"""Package final R21 plus isolated W22 native routing and three collection clips."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, os, shutil, struct, subprocess, zipfile
parser=argparse.ArgumentParser();parser.add_argument('--base-apk',required=True);parser.add_argument('--native-so');args=parser.parse_args()
W=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005')
B=Path(args.base_apk);U=W/'unsigned.apk';O=W/'TurboStations-NeoGeo-Colecoes-R22-20261005.apk'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(W/'temp')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,name):
 with z.open(name) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(name):return name.startswith('META-INF/') and name.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def run(name,cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace')
 (W/'evidence'/(name+'.log')).write_text(r.stdout+r.stderr,'utf8')
 assert r.returncode==0,(r.stdout+r.stderr)[-4000:]
 return r.stdout+r.stderr
integration=json.loads((W/'evidence/integration.json').read_text('utf8'))
media=json.loads((W/'media-manifest.json').read_text('utf8'))
assert sha(B)==integration['baseSha256']
native=Path(args.native_so) if args.native_so else W/'libturbo_carousel.so'
assert sha(native)==integration['soSHA256']
assert not U.exists() and not O.exists()
delta={'lib/arm64-v8a/libturbo_carousel.so':native}
for item in media['videos']:
 path=Path(item['output']);assert sha(path)==item['sha256'];delta[item['asset']]=path
assert len(delta)==4
with zipfile.ZipFile(B) as old:
 added_bytes=sum(p.stat().st_size for name,p in delta.items() if name not in old.namelist())
 native_growth=max(0,native.stat().st_size-old.getinfo('lib/arm64-v8a/libturbo_carousel.so').file_size)
 # Both unsigned and signed APKs coexist; add 32 MiB for ZIP padding/signing/temp.
 assert shutil.disk_usage(W).free>2*(B.stat().st_size+added_bytes+native_growth)+32*1024*1024
 old_names=set(old.namelist())
 assert sum(name in old_names for name in delta)==1
 def put(out,info):
  name=info.filename;path=delta.get(name);item=copy.copy(info);item.extra=b''
  item.file_size=path.stat().st_size if path else info.file_size
  if item.compress_type==zipfile.ZIP_STORED:
   alignment=16384 if name.endswith('.so') else 4
   offset=out.fp.tell()+30+len(name.encode())
   if offset%alignment:
    pad=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
  with out.open(item,'w') as dst:
   with (path.open('rb') if path else old.open(info)) as src:shutil.copyfileobj(src,dst,1024*1024)
 with zipfile.ZipFile(U,'w',allowZip64=True) as out:
  for info in old.infolist():
   if not signature(info.filename):put(out,info)
  for name in sorted(set(delta)-old_names):
   info=zipfile.ZipInfo(name,(2026,10,5,0,0,0));info.compress_type=zipfile.ZIP_STORED;put(out,info)
print('Unsigned R22 prepared',flush=True)
run('unsigned-alignment',[BT/'zipalign.exe','-c','-P','16','4',U])
run('sign',[J/'java.exe','-Djava.io.tmpdir='+str(W/'temp'),'-jar',BT/'lib/apksigner.jar','sign',
 '--alignment-preserved','true','--v4-signing-enabled','false','--ks',r'C:\Users\Admin\.android\debug.keystore',
 '--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',O,U])
certificate='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert certificate in run('signature',[J/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',O])
run('alignment',[BT/'zipalign.exe','-c','-P','16','4',O])
print('Verifying every APK entry',flush=True)
changed=[];preserved=0
with zipfile.ZipFile(B) as old,zipfile.ZipFile(O) as new:
 old_names={name for name in old.namelist() if not signature(name)}
 new_names={name for name in new.namelist() if not signature(name)}
 assert new_names==old_names|set(delta) and len(new.namelist())==len(set(new.namelist()))
 added=sorted(new_names-old_names)
 for name in sorted(new_names):
  expected=sha(delta[name]) if name in delta else zsha(old,name)
  assert zsha(new,name)==expected,name
  if name in old_names:
   if name in delta:changed.append(name)
   else:preserved+=1
 assert changed==['lib/arm64-v8a/libturbo_carousel.so'] and len(added)==3
 assert zsha(new,'resources.arsc')=='1e33730bf8fc2b7bd4c6994c2254b2dffb3e44fff8b359e22a51627dde9103dd'
 assert zsha(new,'classes30.dex')=='0d76beace3c7c427c670dc4cc59d60200d14b11f96b907fe79c8abc3e25d973f'
 assert zsha(new,'classes35.dex')=='8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae'
result={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':str(B),'baseSHA256':sha(B),
 'apk':str(O),'sha256':sha(O),'bytes':O.stat().st_size,'certificateSHA256':certificate,
 'changed':changed,'added':added,'preservedEntries':preserved,'allPackageEntriesVerified':True,'alignment16KiB':True,
 'r21NativeSourcesPreserved':True,'sourceRouteEvidence':'evidence/integration.json','installed':False,'stable':False}
(W/'build-result.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
assert U.resolve().parent==W.resolve() and U.name=='unsigned.apk';U.unlink()
print(json.dumps(result,indent=2))
