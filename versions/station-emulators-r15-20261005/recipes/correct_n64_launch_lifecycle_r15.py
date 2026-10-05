import os
from pathlib import Path
import subprocess,json,shutil,os
W=Path(os.environ['STATION_N64_WORK']);M=W/'merged'
p=M/'smali_classes36/paulscode/android/mupen64plusae/GalleryActivity.smali';s=p.read_text('utf8')
a=s.index('.method private launchGameOnCreation(Ljava/lang/String;Z)V');b=s.index('.end method',a)
part=s[a:b];needle='    invoke-virtual {p0}, Landroid/app/Activity;->finishAffinity()V'
assert part.count(needle)==1
part=part.replace(needle,'    # Keep the result recipient alive; upstream result callback closes it after the game exits.')
p.write_text(s[:a]+part+s[b:],'utf8')
r=json.loads((W/'runtime-adaptations.json').read_text('utf8'));r['changes'][p.relative_to(M).as_posix()]='Preserve Gallery result recipient while game is active; original RESULT_OK callback returns to Station after exit'
(W/'runtime-adaptations.json').write_text(json.dumps(r,indent=2),'utf8')
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15');SDK=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
os.environ['TEMP']=os.environ['TMP']=str(W/'tmp')
def run(args,name):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,(p.stdout+p.stderr)[-4000:];print(name,'OK',flush=True)
src=W/'java/org/emulationstation/frontend'
for n in ('N64Bootstrap.java','N64EntryActivity.java'):shutil.copy2(n,src/n)
run([J/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-cp',SDK,'-d',W/'bridge-classes',*src.glob('*.java')],'bridge-final-javac')
run([J/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','28','--lib',SDK,'--output',W/'bridge-dex',*(W/'bridge-classes').rglob('*.class')],'bridge-final-d8')
shutil.copy2(W/'bridge-dex/classes.dex',W/'classes38.dex')
run([J/'java.exe','-Xmx2300m','-Djava.io.tmpdir='+str(W/'tmp'),'-jar',r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar','b','-p',W/'framework','-o',W/'n64-resources-dex.apk',M],'n64-resources-final')
