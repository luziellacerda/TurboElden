#!/usr/bin/env python3
"""Create an unsigned R15 APK with only classes30.dex replaced; verify all other bytes."""
import argparse,copy,hashlib,json,re,shutil,zipfile
from pathlib import Path
BASE_SHA='d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b'
MAME_SHA='8748a125b1e59be70837f0e57993104802df81f4607a2d19d48fe77c0d82a32d'
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
assert digest(a.base_apk)==BASE_SHA,'Base must be the verified R15, preserving full N64/R14B/R12'
with zipfile.ZipFile(a.base_apk) as base:
 assert len(base.namelist())==len(set(base.namelist()))
 assert hashlib.sha256(base.read('classes30.dex')).hexdigest()==MAME_SHA
 assert hashlib.sha256(base.read('classes35.dex')).hexdigest()==ROOMS_SHA
 expected={};removed=[]
 try:
  with zipfile.ZipFile(a.output,'x') as out:
   for info in base.infolist():
    if old_signature(info.filename):removed.append(info.filename);continue
    with out.open(copy.copy(info),'w',force_zip64=True) as dest:
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
