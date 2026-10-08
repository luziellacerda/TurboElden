"""Reproduce the binary manifest delta and parse it with Android's aapt2."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,zipfile
SNAP=Path(__file__).resolve().parent.parent
WORK=Path(r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\manifest-tests-final')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R73-20261007.apk')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
patcher=module('patch_service',SNAP/'recipes/patch_session_manifest.py')
parser=module('read_manifest',SNAP.parent/'station-online-layout-r71-20261007/recipes/patch_navigation_manifest.py')
WORK.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(BASE) as z:old=z.read('AndroidManifest.xml')
new,receipt=patcher.patch(old,parser)
before=parser.attributes(old);after=parser.attributes(new)
assert len(after)==len(before)+1
def semantic(nodes):return [(tag,[{k:v for k,v in attr.items() if k!='dataOffset'} for attr in attrs]) for tag,attrs in nodes]
assert semantic([node for node in after if not any(v['value']==patcher.SERVICE for v in node[1])])==semantic(before)
rejected=0
for invalid in (b'',old[:-1],new):
    try:patcher.patch(invalid,parser)
    except (ValueError,AssertionError,IndexError):rejected+=1
assert rejected==3
apk=WORK/'manifest-only.apk'
with zipfile.ZipFile(apk,'w') as z:z.writestr('AndroidManifest.xml',new)
r=subprocess.run([r'G:\Android\Sdk\build-tools\34.0.0\aapt2.exe','dump','xmltree',str(apk),'--file','AndroidManifest.xml'],capture_output=True)
(WORK/'aapt2-private.log').write_bytes(r.stdout+r.stderr)
assert r.returncode==0 and patcher.SERVICE.encode() in r.stdout
report=dict(success=True,unchangedExistingXmlElements=len(before),newServiceElements=1,
            malformedInputsRejected=rejected,aapt2Parsed=True,serviceExported=False,permissionsAdded=0,
            manifestSHA256=hashlib.sha256(new).hexdigest(),recipeSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(WORK/'manifest-tests.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report,indent=2))
