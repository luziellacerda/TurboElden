"""Host tests of the real helper/CLI code, using synthetic firmware identities only."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, shutil
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True)
p.add_argument('--jdk-bin',type=Path,default=Path('C:/Program Files/Eclipse Adoptium/jdk-17.0.20.101-hotspot/bin'))
a=p.parse_args();root=Path(__file__).resolve().parents[1];w=a.work.resolve()
assert w.drive.lower()=='e:' and not w.exists(), 'Use a fresh output folder on E:'
w.mkdir(parents=True);(w/'classes').mkdir();os.environ['TEMP']=os.environ['TMP']=str(w)
source=root/'java/org/emulationstation/frontend/NeoCdSupport.java'
bootstrap=(root/'java/org/emulationstation/frontend/MameBootstrap.java').read_text('utf8')
def extract(signature):
    start=bootstrap.index(signature);i=bootstrap.index('{',start)+1;depth=1
    while depth:
        if bootstrap[i]=='{':depth+=1
        elif bootstrap[i]=='}':depth-=1
        i+=1
    return bootstrap[start:i]
(w/'MameBootstrap.java').write_text('package org.emulationstation.frontend;import java.io.*;public class MameBootstrap{'+extract('static String quoteCliPath(')+extract('static String cliParamsFor(')+'}','utf8')
shutil.copy2(root/'tests/NeoCdSupportTest.java',w/'NeoCdSupportTest.java')
commands=[['javac.exe','-encoding','UTF-8','-d',w/'classes',source,w/'MameBootstrap.java',w/'NeoCdSupportTest.java'],['java.exe','-Djava.io.tmpdir='+str(w),'-cp',w/'classes','org.emulationstation.frontend.NeoCdSupportTest',w/'fixtures']]
output=[]
for command in commands:
    command[0]=a.jdk_bin/command[0]
    r=subprocess.run(list(map(str,command)),capture_output=True,text=True,encoding='utf8',errors='replace')
    output.append(r.stdout+r.stderr);(w/'result.log').write_text('\n'.join(output),'utf8');r.check_returncode()
assert 'PASS 37 ' in output[-1]
receipt={'passed':True,'checks':37,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'syntheticBIOSOnly':True,'androidRuntimeTested':False,'result':output[-1]}
(w/'reproduction-tests.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8');print(json.dumps(receipt))
