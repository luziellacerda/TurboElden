"""Compile only new Netplay classes; no APK, manifest, existing DEX or device mutation."""
from pathlib import Path
import hashlib, json, os, subprocess, zipfile

ROOT=Path(__file__).resolve().parent
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
ANDROID=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
TOOLS=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
OUT=ROOT/'build'

def run(args):
    completed=subprocess.run([str(x) for x in args],cwd=ROOT,env=os.environ.copy(),capture_output=True,text=True,encoding='utf-8',errors='replace')
    if completed.stdout: print(completed.stdout,end='')
    if completed.stderr: print(completed.stderr,end='')
    completed.check_returncode()

def main():
    classes=OUT/'classes'; dex=OUT/'dex'
    classes.mkdir(parents=True,exist_ok=True);dex.mkdir(parents=True,exist_ok=True)
    sources=sorted((ROOT/'src').rglob('*.java'))
    run([JDK/'javac.exe','-encoding','UTF-8','--release','8','-cp',ANDROID,'-d',classes,*sources])
    jar=OUT/'netplay.jar'
    run([JDK/'jar.exe','cf',jar,'-C',classes,'.'])
    run([JDK/'java.exe','-cp',TOOLS/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',ANDROID,'--output',dex,jar])
    result=dex/'classes.dex'
    receipt={'schemaVersion':1,'newDexOnly':True,'package':'org.emulationstation.frontend.netplay',
             'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
             'dexPath':str(result),'dexSha256':hashlib.sha256(result.read_bytes()).hexdigest(),'dexBytes':result.stat().st_size,
             'runtimeValidation':'pending; no device used','serverChanged':False}
    (OUT/'build-result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('dexPath','dexSha256','dexBytes')}))
if __name__=='__main__':main()
