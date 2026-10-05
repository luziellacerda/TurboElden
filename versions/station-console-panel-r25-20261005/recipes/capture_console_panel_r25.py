from pathlib import Path
import subprocess,os,json,datetime
W=Path(r'E:\ESTUDO APK\work\station-console-panel-r25-20261005\device-evidence');W.mkdir(exist_ok=True)
os.environ['ANDROID_USER_HOME']=r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
a=[r'G:\Android\Sdk\platform-tools\adb.exe','-s',os.environ.get('STATION_ADB_SERIAL','RQCY30751WY')]
def run(args):
 r=subprocess.run(a+args,capture_output=True);assert r.returncode==0,r.stderr.decode(errors='replace');return r.stdout
stamp=datetime.datetime.now().strftime('%H%M%S')
pid=run(['shell','pidof','org.turboramastation.frontend']).decode().strip();assert pid.isdigit()
png=run(['exec-out','screencap','-p']);assert png.startswith(b'\x89PNG');image=W/('screen-'+stamp+'.png');image.write_bytes(png)
log=W/('video-'+stamp+'.log')
log.write_bytes(run(['logcat','-d','--pid='+pid,'-v','threadtime','TurboCarousel:I','SystemCardVideo720:V','TurboVideo720:V','AndroidRuntime:E','*:S']))
record={'image':str(image),'log':str(log),'pid':pid}
(W/'latest-capture.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
print(json.dumps(record))
