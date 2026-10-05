#!/usr/bin/env python3
"""Build only the three MAME bridge classes; output remains an unsigned DEX."""
import argparse,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--android-jar',type=Path,required=True);p.add_argument('--d8',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--javac',default='javac');a=p.parse_args()
root=Path(__file__).resolve().parents[1];sources=sorted((root/'java').rglob('*.java'))
assert len(sources)==3 and a.android_jar.is_file() and not a.output.exists()
a.output.mkdir(parents=True)
with tempfile.TemporaryDirectory() as t:
 classes=Path(t)/'classes';classes.mkdir()
 subprocess.run([a.javac,'-encoding','UTF-8','-source','8','-target','8','-classpath',str(a.android_jar),'-d',str(classes),*map(str,sources)],check=True)
 command=[str(a.d8),'--min-api','26','--lib',str(a.android_jar),'--output',str(a.output),*map(str,sorted(classes.rglob('*.class')))]
 if a.d8.suffix.lower()=='.bat':command=['cmd','/c',*command]
 subprocess.run(command,check=True)
 produced=a.output/'classes.dex';assert produced.is_file() and not (a.output/'classes2.dex').exists()
 digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 result={'compiled':True,'androidJarSha256':digest(a.android_jar),'minApi':26,'dexSha256':digest(produced),'sources':{str(f.relative_to(root)):digest(f) for f in sources},'apkSignedOrInstalled':False}
 (a.output/'build.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
