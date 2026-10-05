import os
from pathlib import Path
import zipfile,subprocess,shutil,os,importlib.util,inspect,json,re,xml.etree.ElementTree as ET
W=Path(os.environ['STATION_N64_WORK']);D=W/'donor';M=W/'merged';R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');B=Path(os.environ['STATION_BASE_APK'])
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');APKTOOL=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
os.environ['TEMP']=os.environ['TMP']=str(W/'tmp')
stub=W/'base-resources.apk'
if not stub.exists():
 with zipfile.ZipFile(B) as a,zipfile.ZipFile(stub,'w') as b:
  for i in a.infolist():
   if i.filename in ('AndroidManifest.xml','resources.arsc') or i.filename.startswith('res/'):b.writestr(i,a.read(i))
if not (W/'base').exists():
 p=subprocess.run([str(J/'java.exe'),'-Djava.io.tmpdir='+str(W/'tmp'),'-jar',str(APKTOOL),'d','-s','-p',str(W/'framework'),'-o',str(W/'base'),str(stub)],capture_output=True,text=True,encoding='utf8');(W/'base-decode.log').write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,p.stdout+p.stderr
assert not M.exists();M.mkdir();shutil.copytree(W/'base/res',M/'res');shutil.copyfile(W/'base/AndroidManifest.xml',M/'AndroidManifest.xml');shutil.copyfile(W/'base/apktool.yml',M/'apktool.yml')
p=M/'smali/org/emulationstation/frontend/N64MergeKeep.smali';p.parent.mkdir(parents=True);p.write_text('.class public Lorg/emulationstation/frontend/N64MergeKeep;\n.super Ljava/lang/Object;\n','utf8')
shutil.copy2(Path(__file__).with_name('merge_resources.py'),W/'merge_resources.py')
spec=importlib.util.spec_from_file_location('n64_resources',W/'merge_resources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names,ids,classes,natives=m.merge_donor(D,M)
(W/'resource-map.json').write_text(json.dumps({'names':{'/'.join(k):v for k,v in names.items()},'ids':{str(k):v for k,v in ids.items()},'classes':classes,'nativeClasses':sorted(natives)},indent=2),'utf8')
A=m.A;tree=ET.parse(M/'AndroidManifest.xml');app=tree.getroot().find('application');donor=ET.parse(D/'AndroidManifest.xml').getroot();da=donor.find('application');dot={k.replace('/','.'):v.replace('/','.') for k,v in classes.items()}
def ref(v):
 if v.startswith('@') and '/' in v:
  t,n=v[1:].split('/',1);return '@'+t+'/'+names.get((t,n),n)
 return v
def convert(e):
 for key,value in list(e.attrib.items()):
  if key==A+'name':value=dot.get(value,value)
  e.set(key,ref(value).replace('org.mupen64plusae.v3.alpha.filesprovider','org.turboramastation.frontend.n64.filesprovider').replace('org.mupen64plusae.v3.alpha.androidx-startup','org.turboramastation.frontend.n64.androidx-startup'))
 for c in list(e):convert(c)
for original in da:
 if original.tag not in ('activity','service','provider','receiver'):continue
 name=original.get(A+'name','')
 if 'StartupIntentReceiver' in name or 'ProfileInstallReceiver' in name or 'RetroAchievementsHostOverrideReceiver' in name:continue
 e=ET.fromstring(ET.tostring(original));convert(e);e.set(A+'process',':n64core' if original.get(A+'process') else ':n64')
 e.set(A+'exported','false')
 if e.tag=='activity':
  e.set(A+'taskAffinity','org.turboramastation.frontend.n64');e.set(A+'enableOnBackInvokedCallback','false');e.set(A+'theme',ref(original.get(A+'theme',da.get(A+'theme'))))
  for c in list(e):
   if c.tag=='intent-filter':e.remove(c)
 app.append(e)
ET.SubElement(app,'activity',{A+'name':'org.emulationstation.frontend.N64EntryActivity',A+'process':':n64',A+'exported':'false',A+'screenOrientation':'userLandscape',A+'theme':'@android:style/Theme.Material.NoActionBar',A+'taskAffinity':'org.turboramastation.frontend.n64'})
permissions={e.get(A+'name') for e in tree.getroot().findall('uses-permission')}
for e in donor.findall('uses-permission'):
 name=e.get(A+'name','')
 if name in permissions or name.startswith(('org.mupen64','com.android.providers.tv.')) or name=='android.permission.RECEIVE_BOOT_COMPLETED':continue
 tree.getroot().append(ET.fromstring(ET.tostring(e)))
ET.register_namespace('android',A[1:-1]);tree.write(M/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
print('Merged N64 resources and complete Android components:',len(ids),len(classes),'native',len(natives),flush=True)
