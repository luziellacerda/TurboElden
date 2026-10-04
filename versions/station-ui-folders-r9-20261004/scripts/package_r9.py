from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,subprocess,zipfile
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
W=R/'ui-r9'
B=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Online-Candidato-R7-20261004.apk')
OUT=R/'TurboStations-Salas-Subpastas-R9-20261004.apk'
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
assert sha(B)=='827723436ac618d3b1745a873813c7781ff10e043abc6033de416c01d774703d'
assert not OUT.exists() and shutil.disk_usage(R).free>2*B.stat().st_size+200*1024*1024
replacements={'lib/arm64-v8a/libturbo_carousel.so':R/'native/libturbo_carousel.so','classes35.dex':R/'netplay/build-r8/dex/classes.dex','classes28.dex':R/'folders/build/dex/classes.dex','lib/arm64-v8a/libstation_frontend.so':R/'folders/build/native/arm64-v8a/libstation_frontend.so'}
notice={'builtAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseApk':str(B),'baseSha256':sha(B),'scope':['uniform native game action buttons','animated green sheen','room hero, vector symbols and adaptive columns','native folder navigation','optional signed folderPath metadata'],'nativeGameButtonVertices':286,'nativeExtraThreads':0,'nativeExtraTextures':0,'roomContinuousAnimationsMax':2,'heroLightingFps':15.625,'folderServerDeploymentRequired':True,'roomAnimationOnlyVisibleEnabledFocused':True,'routesChanged':False,'authChanged':False,'offlineEnginesChanged':False,'serverDeployed':False,'installed':False,'deviceVisualVerified':False,'stable':False}
(W/'BUILD-NOTICE.json').write_text(json.dumps(notice,indent=2)+'\n','utf8')
additions={'assets/station-ui-r9/BUILD-NOTICE.json':W/'BUILD-NOTICE.json'}
unsigned=W/'unsigned.apk';aligned=W/'aligned.apk';assert not unsigned.exists() and not aligned.exists()
with zipfile.ZipFile(B) as a,zipfile.ZipFile(unsigned,'w',allowZip64=True) as b:
 for info in a.infolist():
  if signature(info.filename):continue
  oi=copy.copy(info);oi.extra=b''
  with b.open(oi,'w') as dst:
   if info.filename in replacements:
    with replacements[info.filename].open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
   else:
    with a.open(info) as src:shutil.copyfileobj(src,dst,1024*1024)
 for name,p in additions.items():b.write(p,name,compress_type=zipfile.ZIP_DEFLATED)
run([BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned],'align.log');unsigned.unlink()
run([J/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned],'sign.log')
assert '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825' in run([J/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',OUT],'signature.log')
run([BT/'zipalign.exe','-c','-P','16','4',OUT],'alignment-check.log')
preserved=0;changed=[]
with zipfile.ZipFile(B) as a,zipfile.ZipFile(OUT) as b:
 before={n for n in a.namelist() if not signature(n)};after={n for n in b.namelist() if not signature(n)}
 assert len(b.namelist())==len(set(b.namelist())) and after-before==set(additions) and not before-after
 for name in sorted(before):
  old,new=zsha(a,name),zsha(b,name)
  if old!=new:
   assert name in replacements and sha(replacements[name])==new,name
   changed.append(name)
  else:preserved+=1
 assert set(changed)==set(replacements)
 for name,p in additions.items():assert zsha(b,name)==sha(p)
 for info in b.infolist():
  if info.filename.startswith('assets/turbo-system-videos/') and info.filename.endswith('.mp4'):assert info.compress_type==0
aligned.unlink()
result={**notice,'apk':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,'changed':changed,'added':list(additions),'preservedEntries':preserved,'fullPayloadIntegrityPassed':True}
(W/'build-result.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result,indent=2))
