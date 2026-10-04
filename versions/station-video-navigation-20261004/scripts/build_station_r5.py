from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,subprocess,sys,zipfile
ROOT=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
BASE=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003\TurboStations-Capas4-Sinopses-LED-Netplay-R4-20261003.apk')
OUT=ROOT/'TurboStations-Videos-Sem-Espera-SNES-Roxo-R5-20261004.apk'
BASE_SHA='17e9b87bf268c2349874d1767d5ab315862eb09fb2705f9b79a7e307c0c63c77'
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(ROOT)
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
 with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.RSA','.DSA','.EC','.SF'))
def run(args,name):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf-8',errors='replace')
 (ROOT/'evidence'/name).write_text(r.stdout+r.stderr,encoding='utf-8')
 assert r.returncode==0,(name,(r.stdout+r.stderr)[-5000:])
 return r.stdout+r.stderr
def native():
 n=ROOT/'native'
 run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',n/'native_carousel.cpp',n/'video720_posters.o','-L',n,'-lc','-ldl','-llog','-o',n/'libturbo_carousel.so'],'native-build.log')
 print('Native rebuilt',sha(n/'libturbo_carousel.so'))
def package():
 assert sha(BASE)==BASE_SHA and not OUT.exists()
 assert shutil.disk_usage(ROOT).free>2*BASE.stat().st_size+200*1024*1024,'Build space'
 replacements={'lib/arm64-v8a/libturbo_carousel.so':ROOT/'native/libturbo_carousel.so'}
 notice={'base':str(BASE),'baseSha256':BASE_SHA,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'videoStartDelayMs':0,'previewTexturesMax':8,'previewGpuBytesMax':8294400,'videoFrameSources':44,'snesLed':'A855F7FF','engineChanges':False,'serverChanges':False,'installed':False,'phonePerformanceVerified':False,'netplayNewEnginesIntegrated':False,'stable':False}
 receipt=ROOT/'evidence/BUILD-NOTICE.json';receipt.write_text(json.dumps(notice,indent=2)+'\n')
 additions={'assets/station-video-navigation-r5/BUILD-NOTICE.json':receipt}
 unsigned=ROOT/'unsigned-r5.apk';aligned=ROOT/'aligned-r5.apk'
 assert not unsigned.exists() and not aligned.exists()
 with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(unsigned,'w',allowZip64=True) as b:
  for info in a.infolist():
   if signature(info.filename):continue
   oi=copy.copy(info);oi.extra=b''
   if info.filename in replacements:
    with replacements[info.filename].open('rb') as src,b.open(oi,'w') as dst:shutil.copyfileobj(src,dst,1024*1024)
   else:
    with a.open(info) as src,b.open(oi,'w') as dst:shutil.copyfileobj(src,dst,1024*1024)
  for name,p in additions.items():b.write(p,name,compress_type=zipfile.ZIP_DEFLATED)
 run([BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned],'align.log');unsigned.unlink()
 run([JDK/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--v4-signing-enabled','false','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned],'sign.log')
 assert '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825' in run([JDK/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',OUT],'signature.log')
 run([BT/'zipalign.exe','-c','-P','16','4',OUT],'alignment-check.log')
 preserved=0;changed=[]
 with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
  before={n for n in a.namelist() if not signature(n)};after={n for n in b.namelist() if not signature(n)}
  assert len(b.namelist())==len(set(b.namelist())) and after-before==set(additions) and not before-after
  for name in sorted(before):
   old,new=zsha(a,name),zsha(b,name)
   if old!=new:
    assert name in replacements and sha(replacements[name])==new,name
    changed.append(name)
   else:preserved+=1
  assert set(changed)==set(replacements)
  for i in b.infolist():
   if i.filename.startswith('assets/turbo-system-videos/') and i.filename.endswith('.mp4'):assert i.compress_type==0
 aligned.unlink()
 result={**notice,'apk':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,'changed':changed,'preservedEntries':preserved,'fullPayloadIntegrityPassed':True}
 (ROOT/'evidence/build-result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':{'native':native,'package':package}[sys.argv[1]]()
