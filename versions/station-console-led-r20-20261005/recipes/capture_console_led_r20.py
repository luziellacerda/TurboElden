from pathlib import Path
import subprocess,datetime,os,json
W=Path(r'E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005\device-evidence');W.mkdir(exist_ok=True)
adb=r'G:\Android\Sdk\platform-tools\adb.exe';serial=os.environ['STATION_ADB_SERIAL']
os.environ['ANDROID_USER_HOME']=r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
stamp=datetime.datetime.now().strftime('%H%M%S')
def run(*args):
 p=subprocess.run([adb,'-s',serial,*args],capture_output=True);assert p.returncode==0,p.stderr.decode(errors='replace');return p.stdout
png=run('exec-out','screencap','-p');assert png.startswith(b'\x89PNG');(W/('screen-'+stamp+'.png')).write_bytes(png)
pid=run('shell','pidof','org.turboramastation.frontend').decode().strip()
assert pid.isdigit(),pid
log=run('logcat','-d','--pid='+pid,'-v','threadtime','TurboCarousel:I','AndroidRuntime:E','*:S')
(W/('visual-'+stamp+'.log')).write_bytes(log)
record={'image':str(W/('screen-'+stamp+'.png')),'log':str(W/('visual-'+stamp+'.log')),'pid':pid}
(W/'latest-capture.json').write_text(json.dumps(record,indent=2),'utf-8')
print(json.dumps(record))
