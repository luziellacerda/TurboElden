import os
from pathlib import Path
import subprocess,zipfile,os,json,re,hashlib
W=Path(os.environ['STATION_N64_WORK']);R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
base=Path(os.environ['STATION_BASE_APK'])
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');tool=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
Y=W/'application';Y.mkdir(exist_ok=True);os.environ['TEMP']=os.environ['TMP']=str(W/'tmp')
def run(args,stage):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(Y/(stage+'.log')).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,(p.stdout+p.stderr)[-4500:];print(stage,'OK',flush=True)
with zipfile.ZipFile(base) as src,zipfile.ZipFile(Y/'stub.apk','w') as dst:
 for n in ('AndroidManifest.xml','classes.dex'):dst.writestr(n,src.read(n))
 before=hashlib.sha256(src.read('classes.dex')).hexdigest()
cmd=[J/'java.exe','-Xmx1800m','-Djava.io.tmpdir='+str(W/'tmp'),'-jar',tool]
run(cmd+['d','-r','-p',W/'framework','-o',Y/'decoded',Y/'stub.apk'],'decode')
p=Y/'decoded/smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=p.read_text('utf8')
needle='    invoke-static {p0}, Lorg/emulationstation/frontend/MameBootstrap;->initProcess(Landroid/app/Application;)Z\n'
assert s.count(needle)==1 and 'N64Bootstrap' not in s
insert='''    invoke-static {p0}, Lorg/emulationstation/frontend/N64Bootstrap;->initProcess(Landroid/app/Application;)Z
    move-result v7
    if-eqz v7, :turbo_not_n64
    return-void
    :turbo_not_n64
'''
p.write_text(s.replace(needle,insert+needle),'utf8')
run(cmd+['b','-p',W/'framework','-o',Y/'built.apk',Y/'decoded'],'build')
with zipfile.ZipFile(Y/'built.apk') as z:data=z.read('classes.dex');(W/'classes.dex').write_bytes(data)
(Y/'receipt.json').write_text(json.dumps({'baseDexSHA256':before,'newDexSHA256':hashlib.sha256(data).hexdigest(),'modifiedClass':'org.yuzu.yuzu_emu.YuzuApplication','earlyInit':'N64Bootstrap.initProcess','processes':[':n64',':n64core']},indent=2),'utf8')
