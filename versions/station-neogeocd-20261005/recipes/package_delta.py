#!/usr/bin/env python3
"""Create an unsigned R18 APK with only classes30.dex replaced; verify all other bytes."""
import argparse,copy,hashlib,json,re,shutil,zipfile
from pathlib import Path
BASE_SHA='a29151da312830d826f6ea71ebb61cb8a39fe1c21786f719e26a61568b29b1c4'
MAME_SHA='0d76beace3c7c427c670dc4cc59d60200d14b11f96b907fe79c8abc3e25d973f'
ROOMS_SHA='8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae'
def sha(stream):
 h=hashlib.sha256()
 for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def digest(path):
 with path.open('rb') as f:return sha(f)
def old_signature(name):return bool(re.fullmatch(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))',name,re.I))
p=argparse.ArgumentParser();p.add_argument('--base-apk',type=Path,required=True);p.add_argument('--dex',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert not a.output.exists() and a.output.resolve()!=a.base_apk.resolve()
assert digest(a.base_apk)==BASE_SHA,'Base must be the verified R18, preserving filesystem/R17/offline/R16/N64/R12'
with zipfile.ZipFile(a.base_apk) as base:
 assert len(base.namelist())==len(set(base.namelist()))
 assert hashlib.sha256(base.read('classes30.dex')).hexdigest()==MAME_SHA
 assert hashlib.sha256(base.read('classes35.dex')).hexdigest()==ROOMS_SHA
 expected={};removed=[]
 try:
  with zipfile.ZipFile(a.output,'x') as out:
   for info in base.infolist():
    if old_signature(info.filename):removed.append(info.filename);continue
    copied=copy.copy(info);copied.extra=b''
    with out.open(copied,'w') as dest:
     if info.filename=='classes30.dex':
      with a.dex.open('rb') as source:shutil.copyfileobj(source,dest,1024*1024)
     else:
      with base.open(info) as source:shutil.copyfileobj(source,dest,1024*1024)
    with base.open(info) as source:expected[info.filename]=(sha(source),info.compress_type)
  with zipfile.ZipFile(a.output) as out:
   assert set(out.namelist())==set(expected)
   for name,(previous,compression) in expected.items():
    with out.open(name) as f:actual=sha(f)
    assert actual==(digest(a.dex) if name=='classes30.dex' else previous)
    assert out.getinfo(name).compress_type==compression
 except Exception:
  a.output.unlink(missing_ok=True);raise
report={'baseApkSha256':BASE_SHA,'changedEntries':['classes30.dex'],'dexSha256':digest(a.dex),'oldSignatureEntriesRemoved':removed,'preservedEntries':len(expected)-1,'roomsDexPreserved':True,'n64ResourcesNativeManifestPreserved':True,'signed':False,'installed':False}
a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
