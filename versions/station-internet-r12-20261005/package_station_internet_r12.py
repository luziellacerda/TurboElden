from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,subprocess,zipfile
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=R/'internet-r12'
M=Path(r'E:\ESTUDO APK\work\station-library-r10-build-20261004')
B=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Colecoes-Nomes-Sinopses-R11-20261005.apk')
OLD=R/B.name;OUT=R/'TurboStations-Netplay-Internet-R12-20261005.apk'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(W)
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
 with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.RSA','.DSA','.EC','.SF'))
def run(args,log):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/log).write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,(log,(r.stdout+r.stderr)[-3000:]);return r.stdout+r.stderr
basehash='7c5096d58991a9724537036e18eb42555f290e2f6d673904524520da0d0146d5'
if not B.exists():
 assert sha(OLD)==basehash;shutil.copyfile(OLD,B)
assert sha(B)==basehash
if OLD.exists():
 assert OLD.resolve().parent==R.resolve() and sha(OLD)==basehash
 OLD.unlink() # Only the verified exact duplicate; the complete R10 remains on G:.
assert not OUT.exists() and shutil.disk_usage(R).free>2*B.stat().st_size+200*1024*1024
replacements={'classes35.dex':W/'app-build/dex/classes.dex'}
additions={'assets/licenses/station-relay-'+n:W/'dependencies'/n for n in ['websocket-LICENSE.txt','slf4j-LICENSE.txt','sources.json']}
for p in replacements.values():assert p.is_file()
unsigned=W/'unsigned.apk';aligned=W/'aligned.apk';assert not unsigned.exists() and not aligned.exists()
print('R11 archive verified; packaging internet relay',flush=True)
with zipfile.ZipFile(B) as a,zipfile.ZipFile(unsigned,'w',allowZip64=True) as b:
 for info in a.infolist():
  if signature(info.filename):continue
  oi=copy.copy(info);oi.extra=b''
  with b.open(oi,'w') as dst:
   if info.filename in replacements:
    with replacements[info.filename].open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
   else:
    with a.open(info) as src:shutil.copyfileobj(src,dst,1024*1024)
 for name,path in additions.items():b.write(path,name,compress_type=zipfile.ZIP_DEFLATED)
run([BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned],'align.log');unsigned.unlink()
run([J/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned],'sign.log')
cert='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert cert in run([J/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',OUT],'signature.log')
run([BT/'zipalign.exe','-c','-P','16','4',OUT],'alignment-check.log')
print('Signed; comparing every payload against R11',flush=True)
preserved=0;changed=[]
with zipfile.ZipFile(B) as a,zipfile.ZipFile(OUT) as b:
 before={n for n in a.namelist() if not signature(n)};after={n for n in b.namelist() if not signature(n)}
 assert len(b.namelist())==len(set(b.namelist())) and before|set(additions)==after
 for name in sorted(before):
  assert a.getinfo(name).compress_type==b.getinfo(name).compress_type,name
  old,new=zsha(a,name),zsha(b,name)
  if old!=new:
   assert name in replacements and sha(replacements[name])==new,name
   changed.append(name)
  else:preserved+=1
 assert set(changed)==set(replacements)
 for name,path in additions.items():assert zsha(b,name)==sha(path)
 rooms=zsha(b,'classes35.dex')
aligned.unlink()
result={'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseApk':str(B),'baseSha256':basehash,'apk':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,'changed':changed,'added':list(additions),'preservedEntries':preserved,'roomsDexSha256':rooms,'certificateSha256':cert,'fullPayloadIntegrityPassed':True,'compressionPreserved':True,'alignment16KiBPassed':True,'serverDeployed':False,'installed':False,'androidGameplayVerified':False,'stable':False}
(W/'build-result.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result,indent=2))
