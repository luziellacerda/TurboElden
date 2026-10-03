from pathlib import Path
import zipfile,hashlib,shutil,subprocess,json,os,re,struct,copy
r=Path(__file__).resolve().parent
base=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk')
out=r/'build/apk';out.mkdir(parents=True,exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(r/'temp')
java=r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe'
bt=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
key=Path(r'C:\Users\Admin\.android\debug.keystore')
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):
 result=subprocess.run([str(a) for a in args],check=True,capture_output=True,text=True,encoding='utf-8',errors='replace');return result.stdout
assert digest(base)=='d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b','Base changed'
replacements={f'classes{n}.dex':r/f'build/dex-integration/prepared/classes{n}.dex.rebuilt' for n in [5,6,8,28]}
for lib in ['main','station_frontend','station_archive']:replacements[f'lib/arm64-v8a/lib{lib}.so']=r/f'build/native/arm64-v8a/lib{lib}.so'
for name,path in [('libarchive-COPYING.txt',r/'build/archive/libarchive-3.8.9/COPYING'),('xz-COPYING.txt',r/'build/archive/xz-5.8.3/COPYING'),('xz-COPYING.0BSD.txt',r/'build/archive/xz-5.8.3/COPYING.0BSD')]:replacements['assets/station-notices/'+name]=path
for p in replacements.values():assert p.is_file(),p
unsigned=out/'station-unsigned.apk';aligned=out/'station-aligned.apk';signed=out/'TurboStations-Station-CANDIDATO-20261003.apk'
def signature(name):return name.upper()=='META-INF/MANIFEST.MF' or (name.upper().startswith('META-INF/') and name.upper().endswith(('.SF','.RSA','.DSA','.EC')))
removed=['assets/turboretro/catalog.json']
preserved={}
print('Packaging verified base, preserving engines and resources',flush=True)
with zipfile.ZipFile(base) as src,zipfile.ZipFile(unsigned,'w',allowZip64=False) as dst:
 assert len(src.namelist())==len(set(src.namelist()))
 for info in src.infolist():
  name=info.filename
  if signature(name) or name in removed:continue
  if name in replacements:
   payload=replacements.pop(name);updated=copy.copy(info);updated.extra=b''
   with payload.open('rb') as a,dst.open(updated,'w') as b:shutil.copyfileobj(a,b,1024*1024)
  else:
   h=hashlib.sha256()
   with src.open(info) as a,dst.open(copy.copy(info),'w') as b:
    while chunk:=a.read(1024*1024):h.update(chunk);b.write(chunk)
   preserved[name]=h.hexdigest()
 for name,p in replacements.items():
  info=zipfile.ZipInfo(name,(2026,10,3,0,0,0));info.compress_type=zipfile.ZIP_STORED if name.endswith('.so') else zipfile.ZIP_DEFLATED
  with p.open('rb') as a,dst.open(info,'w') as b:shutil.copyfileobj(a,b,1024*1024)
print('Aligning and signing candidate',flush=True)
run([bt/'zipalign.exe','-f','-P','16','4',unsigned,aligned])
run([java,'-jar',bt/'lib/apksigner.jar','sign','--ks',key,'--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--alignment-preserved','true','--out',signed,aligned])
base_sig=run([java,'-jar',bt/'lib/apksigner.jar','verify','--print-certs',base])
new_sig=run([java,'-jar',bt/'lib/apksigner.jar','verify','--verbose','--print-certs',signed])
pat=r'Signer #1 certificate SHA-256 digest: ([0-9a-f]+)'
assert re.search(pat,base_sig).group(1)==re.search(pat,new_sig).group(1),'Signer changed'
run([bt/'zipalign.exe','-c','-P','16','4',signed])
print('Verifying all preserved entries and DEX types',flush=True)
def dex_types(data):
 def u32(off):return struct.unpack_from('<I',data,off)[0]
 def string(off):
  while data[off]&128:off+=1
  off+=1;end=data.index(0,off);return data[off:end].decode('utf-8',errors='replace')
 strings=[string(u32(u32(60)+i*4)) for i in range(u32(56))]
 types=[strings[u32(u32(68)+i*4)] for i in range(u32(64))]
 classes=[types[u32(u32(100)+i*32)] for i in range(u32(96))]
 return types,classes
old_classes={};new_classes={};forbidden=['Lorg/emulationstation/frontend/'+v for v in ['HttpBridge','GameDownload','StationTransfer','auth/LocalPassword','auth/AuthSession','catalog/LocalCatalog']]
with zipfile.ZipFile(base) as src,zipfile.ZipFile(signed) as dst:
 assert len(dst.namelist())==len(set(dst.namelist()))
 for name,expected in preserved.items():
  with dst.open(name) as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
  assert actual==expected,('Preserved entry changed',name)
 for name in dst.namelist():
  if re.fullmatch(r'classes\d*\.dex',name):
   types,classes=dex_types(dst.read(name))
   assert not any(t.startswith(p) for t in types for p in forbidden),('Old client type',name)
   for cls in classes:new_classes.setdefault(cls,[]).append(name)
 for name in src.namelist():
  if re.fullmatch(r'classes\d*\.dex',name):
   for cls in dex_types(src.read(name))[1]:old_classes.setdefault(cls,[]).append(name)
 assert not {k:v for k,v in new_classes.items() if len(v)>1 and len(old_classes.get(k,[]))<len(v)},'New duplicate classes'
 for cls in ['auth/LoginActivity','auth/StationLogin','station/StationFrontend','station/StationApi','DownloadService']:assert len(new_classes.get('Lorg/emulationstation/frontend/'+cls+';',[]))==1,cls
 assert src.read('AndroidManifest.xml')==dst.read('AndroidManifest.xml')
 assert all(name not in dst.namelist() for name in removed)
 replaced=[name for name in dst.namelist() if name not in preserved and not signature(name)]
report={'status':'candidate-not-authenticated','package':'org.turboramastation.frontend','versionCode':11,'versionName':'1.0.8-turboeden-unico','base':str(base),'baseSha256':digest(base),'apk':str(signed),'sha256':digest(signed),'sizeBytes':signed.stat().st_size,'signerSha256':re.search(pat,new_sig).group(1),'preservedEntryCount':len(preserved),'changedOrAddedEntries':replaced,'removedEntries':removed,'manifestUnchanged':True,'newDuplicateClasses':False,'legacyJavaClientTypesRemoved':True,'nativeUnusedLegacyRoutinesStillPresent':True,'deviceInstalled':False,'authenticatedFlowVerified':False}
(out/'apk-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(out/'preserved-entry-hashes.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
(out/'apksigner-verification.txt').write_text(new_sig,encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
