from pathlib import Path
import subprocess, shutil, os, hashlib, json, zipfile, copy, re, datetime, sys
ROOT=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-controller-ui-r97-20261009')
PREV=Path(r'E:\ESTUDO APK\work\station-bluetooth-controls-r96-20261009')
BASE=PREV/'package/TurboStations-Premium-R96-20261009.apk'
BASE_SHA='64a71268b77196ef2f3c064eb0a1d24e1ef75cc3be9f4bcd9cfcb064ce6d5f24'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
def sha(p):
 with Path('\\\\?\\'+str(Path(p).resolve())).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def zsha(z,n):
 with z.open(n) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def sig(n):return n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC'))
def main():
 assert sha(BASE)==BASE_SHA
 resume='--resume-native' in sys.argv
 out=WORK/'compiled';out.mkdir(exist_ok=resume);(out/'temp').mkdir(exist_ok=resume)
 env=dict(os.environ,TEMP=str(out/'temp'),TMP=str(out/'temp'))
 def run(cmd,name):
  r=subprocess.run(list(map(str,cmd)),capture_output=True,env=env)
  (out/(name+'.log')).write_bytes(r.stdout+r.stderr)
  assert r.returncode==0,(name,r.stderr.decode('utf8','replace')[-3000:])
  return r.stdout
 source=ROOT/'native/d0/native_carousel.cpp'
 if resume:assert sha(source)==sha(WORK/'carousel-inputs/d0/native_carousel.cpp') and (out/'libturbo_carousel.so').is_file() and (out/'carousel.log').is_file()
 else:shutil.copyfile(source,WORK/'carousel-inputs/d0/native_carousel.cpp')
 nr=json.loads((ROOT.parent/'station-snes-light-maps-r95-20261009/evidence/native-build.json').read_text())
 nh={p.relative_to(WORK/'carousel-inputs').as_posix():sha(p) for p in (WORK/'carousel-inputs').rglob('*') if p.is_file()}
 assert nh.keys()==nr['sourceHashes'].keys()
 assert [n for n in nh if nh[n]!=nr['sourceHashes'][n]]==['d0/native_carousel.cpp']
 spec=json.loads(Path(r'E:\ESTUDO APK\work\station-snes-light-maps-r95-20261009\carousel-command.json').read_text())
 assert sha(spec['command'][0])==spec['compilerSHA256']
 with zipfile.ZipFile(BASE) as z:assert zsha(z,'lib/arm64-v8a/libturbo_carousel.so')==nr['carouselSHA256']
 cmd=[a.replace('{BACKUP}/test-up-to-4-players-r95',str(WORK)).replace('{OUTPUT}',str(out/'libturbo_carousel.so')) for a in spec['command']]
 if not resume:run(cmd,'carousel')
 print('Native compile OK',flush=True)
 rel='netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java'
 shutil.copyfile(ROOT/'java'/rel,WORK/'java'/rel)
 before={p.relative_to(PREV/'java').as_posix():sha(p) for p in (PREV/'java').rglob('*.java')}
 after={p.relative_to(WORK/'java').as_posix():sha(p) for p in (WORK/'java').rglob('*.java')}
 assert before.keys()==after.keys() and [n for n in after if before[n]!=after[n]]==[rel]
 assert after=={p.relative_to(ROOT/'java').as_posix():sha(p) for p in (ROOT/'java').rglob('*.java')}
 jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
 android=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
 d8=Path(r'G:\Android\Sdk\build-tools\34.0.0\lib\d8.jar')
 classes=out/'classes';classes.mkdir()
 cp=str(android)+';'+str(PREV/'compiled-final/client.jar')
 args=['-encoding','UTF-8','--release','8','-proc:none','-cp',cp,'-d',str(classes)]
 args += [str(WORK/'java'/n) for n in sorted(after) if n.startswith(('netplay-src/','dependency-src/'))]
 argfile=out/'rooms.args';argfile.write_text('\n'.join('"'+a.replace('\\','/')+'"' for a in args),'utf8')
 run([jdk/'javac.exe','@'+str(argfile)],'javac')
 jar=out/'rooms.jar'
 with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(classes.rglob('*.class')):
   info=zipfile.ZipInfo(p.relative_to(classes).as_posix(),(2026,10,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 dex=out/'dex';dex.mkdir()
 run([jdk/'java.exe','-cp',d8,'com.android.tools.r8.D8','--min-api','26','--lib',android,'--classpath',PREV/'compiled-final/client.jar','--output',dex,jar],'d8')
 print('Java compile OK',flush=True)
 (ROOT/'JAVA-SOURCE-MANIFEST.json').write_text(json.dumps({'version':'R97','sources':after},indent=2)+'\n','utf8')
 receipt={'version':'R97','baseSHA256':BASE_SHA,'nativeSourceHashes':nh,'changedNativeSources':['d0/native_carousel.cpp'],'changedJavaSources':[rel],'javaSourceCount':len(after),'compilerSHA256':spec['compilerSHA256'],'carouselSHA256':sha(out/'libturbo_carousel.so'),'roomsDexSHA256':sha(dex/'classes.dex'),'compiled':True}
 (ROOT/'evidence/build.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
 tools=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
 key=Path(r'C:\Users\Admin\.android\debug.keystore')
 # Android's standard debug key password; certificate identity is enforced before signing.
 env['STATION_KS_PASS']=env.get('STATION_KS_PASS','android')
 env['STATION_KEY_PASS']=env.get('STATION_KEY_PASS','android')
 cert=run([jdk/'keytool.exe','-exportcert','-keystore',key,'-alias','androiddebugkey','-storepass:env','STATION_KS_PASS'],'certificate')
 assert hashlib.sha256(cert).hexdigest()==CERT
 pkg=WORK/'package';pkg.mkdir()
 payloads={'classes35.dex':dex/'classes.dex','lib/arm64-v8a/libturbo_carousel.so':out/'libturbo_carousel.so'}
 unsigned=pkg/'unsigned.apk';aligned=pkg/'aligned.apk';final=pkg/'TurboStations-Premium-R97-20261009.apk'
 with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(unsigned,'w',allowZip64=True) as new:
  for info in old.infolist():
   if sig(info.filename):continue
   item=copy.copy(info);item.extra=b''
   with new.open(item,'w') as target,(payloads[item.filename].open('rb') if item.filename in payloads else old.open(info)) as src:shutil.copyfileobj(src,target,1024*1024)
 run([tools/'zipalign.exe','-P','16','-f','4',unsigned,aligned],'zipalign')
 run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','sign','--v4-signing-enabled','false','--ks',key,'--ks-key-alias','androiddebugkey','--ks-pass','env:STATION_KS_PASS','--key-pass','env:STATION_KEY_PASS','--out',final,aligned],'sign')
 verified=run([jdk/'java.exe','-jar',tools/'lib/apksigner.jar','verify','--print-certs',final],'verify').decode()
 assert re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([a-f0-9]{64})\s*$',verified,re.M)==[CERT]
 run([tools/'zipalign.exe','-c','-P','16','4',final],'alignment')
 with zipfile.ZipFile(BASE) as old,zipfile.ZipFile(final) as new:
  names=[n for n in old.namelist() if not sig(n)]
  assert set(names)=={n for n in new.namelist() if not sig(n)}
  changes=[]
  for n in names:
   original=zsha(old,n);actual=zsha(new,n)
   assert actual==(sha(payloads[n]) if n in payloads else original),n
   if original!=actual:changes.append(n)
  assert set(changes)==set(payloads)
 receipt={'version':'R97','baseSHA256':BASE_SHA,'sha256':sha(final),'bytes':final.stat().st_size,'certificateSHA256':CERT,'changes':changes,'allEntriesVerified':True,'entries':len(names),'installed':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (ROOT/'evidence/package.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
 print(json.dumps(receipt),flush=True)
 # Only the two temporary APKs created by this recipe, under this package directory.
 for p in (unsigned,aligned):
  assert p.resolve().parent==pkg.resolve();p.unlink()
if __name__=='__main__':main()
