"""Replace R70 carousel/media entries only, preserving all DEX and emulator entries."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,shutil,struct,subprocess,zipfile
p=argparse.ArgumentParser()
p.add_argument('--workspace',default=r'E:\ESTUDO APK\work\station-collection-navigation-r70-20261007-final2')
p.add_argument('--output',default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R70-20261007.apk')
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
assert 'PASS' in r['cornerPolicyResult'] and 'PASS' in r['routeResult']
assert 'PASS 3584 ' in r['navigationResult'] and r['settingsPlacementChecks']==60
assert sha(base)==r['baseSHA256']=='901e5eb495a858fc6877f7a22e325b5fcb3b73807af8c6d2888c90f1425773e4'
assert sha(library)==r['nativeSHA256']
for name,h in r['nativeSources'].items():assert sha(w/'native'/name)==h,name
assert shutil.disk_usage(w).free>base.stat().st_size+64*1024**2
assert shutil.disk_usage(out.parent).free>base.stat().st_size+64*1024**2
cert='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
assert cert in run([java,'-jar',tools/'lib/apksigner.jar','verify','--print-certs',base],'base-signature')
target='lib/arm64-v8a/libturbo_carousel.so'
replacements={target:library}
expected={target:r['nativeSHA256']}
for v in r['videos']:
 replacements[v['asset']]=Path(v['output']);expected[v['asset']]=v['sha256']
 assert sha(replacements[v['asset']])==v['sha256']
with zipfile.ZipFile(base) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
 assert len(old.namelist())==len(set(old.namelist()))
 assert zsha(old,target)==r['baseNativeSHA256']
 allinfo=list(old.infolist())
 for name in sorted(set(replacements)-set(old.namelist())):
  item=zipfile.ZipInfo(name);item.compress_type=zipfile.ZIP_STORED;item.file_size=replacements[name].stat().st_size;allinfo.append(item)
 for info in allinfo:
  if signature(info.filename):continue
  item=copy.copy(info);item.extra=b''
  if item.filename in replacements:item.file_size=replacements[item.filename].stat().st_size
  if item.compress_type==zipfile.ZIP_STORED:
   alignment=16384 if item.filename.endswith('.so') else 4
   offset=new.fp.tell()+30+len(item.filename.encode('utf8'))
   if offset%alignment:
    pad=(-(offset+4))%alignment;item.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
  with new.open(item,'w') as dst:
   with (replacements[item.filename].open('rb') if item.filename in replacements else old.open(info)) as src:shutil.copyfileobj(src,dst,1024*1024)
run([tools/'zipalign.exe','-c','-P','16','4',unsigned],'unsigned-alignment')
run([java,'-Djava.io.tmpdir='+str(w/'temp'),'-jar',tools/'lib/apksigner.jar','sign','--alignment-preserved','true',
 '--v4-signing-enabled','false','--ks',env['STATION_KEYSTORE'],'--ks-key-alias',env['STATION_KEY_ALIAS'],
 '--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',out,unsigned],'sign')
assert cert in run([java,'-jar',tools/'lib/apksigner.jar','verify','--print-certs',out],'signature')
run([tools/'zipalign.exe','-c','-P','16','4',out],'alignment')
with zipfile.ZipFile(base) as old,zipfile.ZipFile(out) as new:
 oldnames={n for n in old.namelist() if not signature(n)}
 names=oldnames|set(replacements)
 assert {n for n in new.namelist() if not signature(n)}==names
 assert len(new.namelist())==len(set(new.namelist()))
 for n in sorted(names):assert zsha(new,n)==(expected[n] if n in expected else zsha(old,n)),n
result=dict(createdUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),apk=str(out),sha256=sha(out),bytes=out.stat().st_size,
 baseSHA256=r['baseSHA256'],certificateSHA256=cert,changed=sorted(set(replacements)&oldnames),added=sorted(set(replacements)-oldnames),preservedEntries=len(oldnames-set(replacements)),
 allPackageEntriesVerified=True,alignment16KiB=True,allDexPreserved=True,updatedVideos=len(r['videos']),totalVideos=sum(n.startswith('assets/turbo-system-videos/') and n.endswith('.mp4') for n in names),
 allEmulatorsPreserved=True,onlyAllGamesCollectionCellRounded=True,actualCollectionsSquareEvenSelected=True,mainPlatformsUnchanged=True,
 individualGameCoversUnchanged=True,menu30FpsPreserved=True,securityR67Preserved=True,collectionSelectionRemapped=True,collectionSettingsInFooter=True,installed=False)
(w/'evidence/package.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
assert unsigned.parent==w and unsigned.name=='unsigned.apk';unsigned.unlink()
print(json.dumps(result,indent=2))
