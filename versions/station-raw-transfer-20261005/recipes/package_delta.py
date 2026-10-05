#!/usr/bin/env python3
"""Unsigned candidate over verified R20, replacing only the client and ZIP bridge."""
import argparse,copy,hashlib,json,re,shutil,zipfile
from pathlib import Path
BASE_SHA='64eae3ab4dd253e25ee826dd23bf02c947e5cbd1db70e6b07f759d988d465904'
CLIENT_SHA='ba3bf581a02a32484b4bed4de64cb78ae9e790b9ffe4030f93012703d8578c21'
MAME_SHA='0d76beace3c7c427c670dc4cc59d60200d14b11f96b907fe79c8abc3e25d973f'
ROOMS_SHA='8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae'
def sha(stream):
 h=hashlib.sha256()
 for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def digest(p):
 with p.open('rb') as f:return sha(f)
def signature(n):return bool(re.fullmatch(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))',n,re.I))
p=argparse.ArgumentParser();p.add_argument('--base-apk',type=Path,required=True);p.add_argument('--dex',type=Path,required=True);p.add_argument('--java-report',type=Path,required=True);p.add_argument('--archive-so',type=Path,required=True);p.add_argument('--archive-report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert not a.output.exists() and not a.output.with_suffix('.json').exists(),'Do not overwrite a candidate or receipt'
assert digest(a.base_apk)==BASE_SHA,'Use the verified R20; newer builds need their receipt reconciled first'
java=json.loads(a.java_report.read_text());native=json.loads(a.archive_report.read_text())
assert digest(a.dex)==java['dexSha256'] and java['gameBodyHashEnabled'] is False
assert len(java['tests'])==18 and all(t['result'].startswith('PASS ') for t in java['tests'])
assert digest(a.archive_so)==native['sha256'] and native['zipBodyCRC32Enabled'] is False
r=Path(__file__).resolve().parents[1]
assert native['sourceSha256']==digest(r/'native/station_archive.c')
for s in (r/'java').rglob('*.java'):assert java['sources'][s.relative_to(r/'java').as_posix()]==digest(s)
replace={'classes28.dex':a.dex,'lib/arm64-v8a/libstation_archive.so':a.archive_so}
assert shutil.disk_usage(a.output.resolve().parent).free>a.base_apk.stat().st_size+100*1024*1024
with zipfile.ZipFile(a.base_apk) as old:
 assert len(old.namelist())==len(set(old.namelist()))
 assert hashlib.sha256(old.read('classes28.dex')).hexdigest()==CLIENT_SHA
 assert hashlib.sha256(old.read('classes30.dex')).hexdigest()==MAME_SHA
 assert hashlib.sha256(old.read('classes35.dex')).hexdigest()==ROOMS_SHA
 assert all(n in old.namelist() for n in replace)
 expected={}
 try:
  with zipfile.ZipFile(a.output,'x') as out:
   for info in old.infolist():
    if signature(info.filename):continue
    copied=copy.copy(info);copied.extra=b''
    with out.open(copied,'w') as target:
     with (replace[info.filename].open('rb') if info.filename in replace else old.open(info)) as source:shutil.copyfileobj(source,target,1024*1024)
    with old.open(info) as source:expected[info.filename]=(sha(source),info.compress_type)
  with zipfile.ZipFile(a.output) as out:
   assert set(out.namelist())==set(expected) and len(out.namelist())==len(expected)
   for name,(prior,compression) in expected.items():
    with out.open(name) as source:assert sha(source)==(digest(replace[name]) if name in replace else prior),name
    assert out.getinfo(name).compress_type==compression,name
 except Exception:
  a.output.unlink(missing_ok=True);raise
result={'baseApkSha256':BASE_SHA,'changedEntries':list(replace),'preservedEntries':len(expected)-len(replace),'allOtherBytesCompressionNamesPreserved':True,'gameBodyHashEnabled':False,'zipBodyCRC32Enabled':False,'signed':False,'installed':False,'needsAlignment16KiBAndOriginalCertificate':True}
a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
