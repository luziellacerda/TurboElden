from pathlib import Path
import shutil,json,xml.etree.ElementTree as ET,subprocess,os,hashlib
W=Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
U=Path(r'E:\ESTUDO APK\work\station-n64-complete-20261005')
P=W/'resource-project';P.mkdir(exist_ok=False)
shutil.copytree(U/'merged/res',P/'res')
for n in ('AndroidManifest.xml','apktool.yml'):shutil.copy2(U/'merged'/n,P/n)
mapping=json.loads((U/'resource-map.json').read_text('utf8'))['classes']
dots={k.replace('/','.'):v.replace('/','.') for k,v in mapping.items()}
changes=[]
for f in (P/'res').rglob('n6_*.xml'):
 tree=ET.parse(f);dirty=False
 for e in tree.getroot().iter():
  if e.text and e.text.strip() in dots:
   value=e.text.strip();dest=dots[value]
   if value!=dest:
    changes.append({'file':str(f.relative_to(P)),'resource':e.attrib.get('name',''),'from':value,'to':dest})
    e.text=e.text.replace(value,dest);dirty=True
  for key,val in list(e.attrib.items()):
   if val in dots and dots[val]!=val:
    changes.append({'file':str(f.relative_to(P)),'attribute':key,'from':val,'to':dots[val]});e.set(key,dots[val]);dirty=True
 if dirty:
  before=W/'before-resources'/f.relative_to(P);before.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(U/'merged'/f.relative_to(P),before)
  tree.write(f,encoding='utf-8',xml_declaration=True)
assert len(changes)==11,changes
# Correct the reusable import algorithm as well, not just generated XML.
merge=(U/'merge_resources.py').read_text('utf8')
merge=merge.replace('            val = refs(val)\n','            val = refs(val)\n            val = dot_map.get(val, val)\n')
merge=merge.replace('            e.text = refs(e.text)\n','            e.text = refs(e.text)\n            if e.text.strip() in dot_map:\n                value = e.text.strip()\n                e.text = e.text.replace(value, dot_map[value])\n')
(W/'merge_resources.py').write_text(merge,'utf8')
checks=0
for f in (P/'res').rglob('*.xml'):
 src=U/'merged'/f.relative_to(P)
 if not f.name.startswith('n6_'):
  assert f.read_bytes()==src.read_bytes(),str(f);checks+=1;continue
 for e in ET.parse(f).getroot().iter():
  vals=list(e.attrib.values())+([e.text.strip()] if e.text else [])
  for v in vals:
   assert v not in dots or dots[v]==v,(str(f),v)
   checks+=1
(W/'resource-tests.json').write_text(json.dumps({'changes':changes,'resourceChecks':checks,'nonN64XmlByteIdentical':True,'classReferencesMatchRelocatedDex':True},indent=2),'utf8')
for c in changes:print(c['resource'],c['to'])
print('PASS',checks,'resource checks')
os.environ['TEMP']=os.environ['TMP']=str(W)
args=[r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe','-Xmx2300m','-Djava.io.tmpdir='+str(W),'-jar',r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar','b','-p',str(U/'framework'),'-o',str(W/'n64-resources-r19b.apk'),str(P)]
p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace');(W/'resources-build.log').write_text(p.stdout+p.stderr,'utf8');print((p.stdout+p.stderr)[-2500:]);assert p.returncode==0
import zipfile
with zipfile.ZipFile(W/'n64-resources-r19b.apk') as z:
 (W/'resources.arsc').write_bytes(z.read('resources.arsc'))
print('resourcesSHA256',hashlib.sha256((W/'resources.arsc').read_bytes()).hexdigest())
