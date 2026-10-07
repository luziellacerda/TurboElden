from pathlib import Path
import argparse,hashlib,json,os,subprocess,zipfile
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True)
p.add_argument('--apk',type=Path,default=Path('G:/BAKUP SISTEMA APP 03-10-2026/apks-candidatos-visuais/TurboStations-Premium-R65-20261007.apk'))
a=p.parse_args();root=Path(__file__).resolve().parents[1];w=a.work.resolve()
assert w.drive.lower()=='e:' and not w.exists()
w.mkdir(parents=True);(w/'classes').mkdir();os.environ['TEMP']=os.environ['TMP']=str(w)
j=Path('C:/Program Files/Eclipse Adoptium/jdk-17.0.20.101-hotspot/bin')
bootstrap=(root/'java/org/emulationstation/frontend/MameBootstrap.java').read_text('utf8')
def extract(signature):
 start=bootstrap.index(signature);i=bootstrap.index('{',start)+1;depth=1
 while depth:
  if bootstrap[i]=='{':depth+=1
  elif bootstrap[i]=='}':depth-=1
  i+=1
 return bootstrap[start:i]
(w/'MameBootstrap.java').write_text('package org.emulationstation.frontend;import java.io.*;public class MameBootstrap{'+extract('static String quoteCliPath(')+extract('static String cliParamsFor(')+'}','utf8')
source=root/'java/org/emulationstation/frontend/NeoCdSupport.java'
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace')
 if r.returncode:print(r.stdout+r.stderr)
 r.check_returncode();return r.stdout+r.stderr
run([j/'javac.exe','-encoding','UTF-8','-d',w/'classes',source,w/'MameBootstrap.java',*sorted((root/'tests').glob('*.java'))])
prior=run([j/'java.exe','-Djava.io.tmpdir='+str(w),'-cp',w/'classes','org.emulationstation.frontend.NeoCdSupportTest',w/'synthetic-fixtures'])
assert 'PASS 37 ' in prior
actual=run([j/'java.exe','-Djava.io.tmpdir='+str(w),'-cp',w/'classes','org.emulationstation.frontend.NeoCdBundledTest',a.apk,w/'existing-apk-fixtures'])
assert 'PASS 29 ' in actual,actual
with zipfile.ZipFile(a.apk) as apk:
 assets={n:{'bytes':len(apk.read(n)),'sha256':hashlib.sha256(apk.read(n)).hexdigest()} for n in apk.namelist() if n.startswith('assets/bios/neocd/') and not n.endswith('/')}
result={'passed':True,'syntheticHelperChecks':37,'existingAPKBIOSChecks':29,'totalChecks':66,'output':prior+actual,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'existingAPKAssets':assets,'newFirmwareDownloaded':False,'newFirmwareAddedToAPK':False,'androidGameplayVerified':False}
(w/'host-tests.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))
