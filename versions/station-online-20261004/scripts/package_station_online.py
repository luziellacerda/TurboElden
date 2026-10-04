from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,subprocess,zipfile
from build_visual_delivery import classes
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
B=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Videos-Sem-Espera-SNES-Roxo-R5-20261004.apk')
OUT=R/'TurboStations-Online-Candidato-R7-20261004.apk'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R)
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,name):
 with z.open(name) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(name):return name.startswith('META-INF/') and name.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def run(args,log):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(R/'evidence'/log).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,(log,(p.stdout+p.stderr)[-3000:]);return p.stdout+p.stderr
assert sha(B)=='afa300d23dc57bb5b1973530dc83371fc892d6c37cf11ecc1750aed8ff22415b'
assert not OUT.exists() and shutil.disk_usage(R).free>2*B.stat().st_size+200*1024*1024
with zipfile.ZipFile(R/'manifest-module.apk') as z:(R/'AndroidManifest.online').write_bytes(z.read('AndroidManifest.xml'))
with zipfile.ZipFile(R/'application/module.apk') as z:(R/'application/classes.online.dex').write_bytes(z.read('classes.dex'))
replacements={'classes.dex':R/'application/classes.online.dex','classes28.dex':R/'station/build/dex/classes.dex','classes35.dex':R/'netplay/build/dex/classes.dex','AndroidManifest.xml':R/'AndroidManifest.online','lib/arm64-v8a/libturbo_carousel.so':R/'native/libturbo_carousel.so'}
additions={'lib/arm64-v8a/'+p.name:p for p in (R/'runtime').glob('*.so')}
for p in (R/'assets/station-online').rglob('*'):
 if p.is_file():additions['assets/station-online/'+p.relative_to(R/'assets/station-online').as_posix()]=p
notice={'schemaVersion':1,'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseApkSha256':sha(B),'installed':False,'androidGameVerified':False,'twoDeviceNetplayVerified':False,'serverDeployed':False,'stable':False,'serverCodeBase':'54bba11c52f35695fd47eabc7145f42af9990426','nativeOnlineAction':True,'nativeHostListeningGate':True,'mainProcessSessionBroker':True,'stationSignedRoomsClient':True,'candidateOnlinePlatforms':['snes','megadrive'],'neoGeoLaunchEnabled':False,'publicLobby':False,'publicRelay':False,'offlineEnginesModified':False,'existingVideoFilesModified':False}
(R/'evidence/ONLINE-BUILD-NOTICE.json').write_text(json.dumps(notice,indent=2),'utf8');additions['assets/station-online/BUILD-NOTICE.json']=R/'evidence/ONLINE-BUILD-NOTICE.json'
with zipfile.ZipFile(B) as z:
 old=set(z.namelist());assert set(replacements)<=old and not old.intersection(additions)
 definitions={}
 for name in old:
  if name.startswith('classes') and name.endswith('.dex'):
   d=replacements[name].read_bytes() if name in replacements else z.read(name)
   for c in classes(d):assert c not in definitions,(c,name);definitions[c]=name
 for c in ('StationRoomsActivity','StationRetroActivity','StationPresence','StationProcess'):assert definitions['Lorg/emulationstation/frontend/netplay/'+c+';']=='classes35.dex'
 for c in ('Lcom/imagine/BaseActivity;','Lcom/mdimagn/BaseActivity;'):assert c in definitions
unsigned=R/'online-unsigned.apk';aligned=R/'online-aligned.apk';assert not unsigned.exists() and not aligned.exists()
with zipfile.ZipFile(B) as a,zipfile.ZipFile(unsigned,'w',allowZip64=True) as b:
 for info in a.infolist():
  if signature(info.filename):continue
  oi=copy.copy(info);oi.extra=b''
  with b.open(oi,'w') as dst:
   if info.filename in replacements:
    with replacements[info.filename].open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
   else:
    with a.open(info) as src:shutil.copyfileobj(src,dst,1024*1024)
 for name,p in additions.items():b.write(p,name,compress_type=zipfile.ZIP_STORED if name.endswith('.so') else zipfile.ZIP_DEFLATED)
run([BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned],'online-align.log');unsigned.unlink()
run([J/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned],'online-sign.log')
assert '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825' in run([J/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',OUT],'online-signature.log')
run([BT/'zipalign.exe','-c','-P','16','4',OUT],'online-alignment-check.log')
preserved=0;changed=[]
with zipfile.ZipFile(B) as a,zipfile.ZipFile(OUT) as b:
 before={n for n in a.namelist() if not signature(n)};after={n for n in b.namelist() if not signature(n)}
 assert len(b.namelist())==len(set(b.namelist())) and not before-after and after-before==set(additions)
 for name in sorted(before):
  x,y=zsha(a,name),zsha(b,name)
  if x!=y:assert name in replacements and sha(replacements[name])==y,name;changed.append(name)
  else:preserved+=1
 assert set(changed)==set(replacements)
 for name,p in additions.items():assert zsha(b,name)==sha(p)
 for i in b.infolist():
  if i.filename.startswith('assets/turbo-system-videos/') and i.filename.endswith('.mp4'):assert i.compress_type==0
aligned.unlink()
result={**notice,'apk':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,'changed':changed,'added':sorted(additions),'preservedEntries':preserved,'fullZipIntegrityVerified':True,'uniqueClassDefinitions':len(definitions)}
(R/'evidence/online-build-result.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({k:result[k] for k in ('apk','sha256','bytes','changed','preservedEntries')},indent=2))
