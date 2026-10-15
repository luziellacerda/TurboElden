"""Run the actual presentation method against Android framework XML on USB.

Pushes only a small diagnostic DEX to its own /data/local/tmp directory and
removes it afterwards. Does not install, stop or invoke the Station app.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shlex,subprocess,uuid,zipfile
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--adb',type=Path,required=True)
    ap.add_argument('--android-jar',type=Path,required=True);ap.add_argument('--d8',type=Path,required=True)
    ap.add_argument('--javac',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--baseline',action='store_true');a=ap.parse_args()
    need(not a.out.exists(),'Use a fresh diagnostic output directory');a.out.mkdir(parents=True,mode=0o700)
    env=dict(os.environ)
    def command(parts,label,timeout=45):
        result=subprocess.run([str(p) for p in parts],capture_output=True,timeout=timeout,env=env)
        (a.out/(label+'.private.log')).write_bytes(result.stdout+result.stderr)
        need(result.returncode==0,label+' failed; see private diagnostic log')
        return result.stdout
    devices=command([a.adb,'devices'],'devices').decode().splitlines()[1:]
    ready=[line.split()[0] for line in devices if len(line.split())>1 and line.split()[1]=='device']
    need(len(ready)==1,'Exactly one authorized USB device required');base=[a.adb,'-s',ready[0]]
    # Independent host Expat oracle for the normal native settings fragment.
    # Values remain in private local/phone temporary files and are never printed.
    realpath='/sdcard/EmulationStation/.emulationstation/es_settings.cfg'
    real=subprocess.run([str(p) for p in base+['exec-out','cat',realpath]],capture_output=True,timeout=15)
    expected={}
    if real.returncode==0:
        raw=real.stdout;need(len(raw)<=1048576,'Normal settings exceed the existing bound')
        text=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
        need('<!DOCTYPE' not in text,'Do not parse declarations in the independent real-settings oracle')
        text=re.sub(r'\A<\?xml\s[^?]*\?>','',text,count=1)
        document=ET.fromstring('<oracle>'+text+'</oracle>')
        for element in document.iter():
            key=element.get('name')
            if (element.tag=='string' and key in ('Player1Controller','Player2Controller')) or (element.tag=='bool' and key=='LibretroStretch'):
                need(key not in expected,'Duplicate actual input setting');expected[key]=element.get('value','')
    oracle=a.out/'real-oracle.private.json';oracle.write_text(json.dumps(expected,ensure_ascii=False)+'\n')
    source=a.source.read_text();marker='    private static void copyPresentationSettings('
    need(source.count(marker)==1,'One exact presentation method required');method=source[source.index(marker):source.rfind('\n}')].strip()
    template=(HERE/'PresentationAndroidProbe.java.in').read_text();need(template.count('__PRODUCTION_METHOD__')==1,'Probe template differs')
    java=a.out/'PresentationAndroidProbe.java';java.write_text(template.replace('__PRODUCTION_METHOD__',method))
    classes=a.out/'classes';classes.mkdir();dex=a.out/'dex';dex.mkdir()
    command([a.javac,'--release','8','-encoding','UTF-8','-cp',a.android_jar,'-d',classes,java],'javac')
    command([a.d8,'--min-api','28','--lib',a.android_jar,'--output',dex,*sorted(classes.glob('*.class'))],'d8')
    archive=a.out/'probe.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:z.write(dex/'classes.dex','classes.dex')
    remote='/data/local/tmp/station-psx-xml-'+uuid.uuid4().hex
    need(re.fullmatch(r'/data/local/tmp/station-psx-xml-[0-9a-f]{32}',remote) is not None,'Diagnostic path guard')
    created=False;cleaned=False
    try:
        command(base+['shell','mkdir',remote],'mkdir');created=True
        command(base+['push',archive,remote+'/probe.zip'],'push')
        command(base+['push',oracle,remote+'/oracle.json'],'push-oracle')
        script=shlex.join(['env','CLASSPATH='+remote+'/probe.zip','app_process','/system/bin','PresentationAndroidProbe',remote+'/fixtures',
                          realpath,str(a.baseline).lower(),remote+'/oracle.json'])
        raw=command(base+['shell',script],'android-probe',timeout=60).decode('utf-8','replace')
        result=next((json.loads(line) for line in raw.splitlines() if line.startswith('{')),None)
        need(result is not None and result.get('passed') is True,'Android did not confirm passing result')
        result.update(sourceSha256=sha(a.source),productionMethodSha256=hashlib.sha256(method.encode()).hexdigest(),
            extractedActualProductionMethod=True,methodTextNormalizedLineEndingsOnly=True,diagnosticDexSha256=sha(dex/'classes.dex'),
            installedApkModified=False,stationAppInvokedOrStopped=False,apkRomSaveOrLicenseReceived=False,
            toolSha256={name:sha(path) for name,path in [('javac',a.javac),('androidJar',a.android_jar),('d8',a.d8)]})
    finally:
        if created:
            command(base+['shell','rm','-r',remote],'cleanup');cleaned=True
    result['ownPhoneDiagnosticFilesRemoved']=cleaned
    (a.out/'android-probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
