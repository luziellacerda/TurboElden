from pathlib import Path
import subprocess,sys,os,time
W=Path(r'E:\ESTUDO APK\work\station-actions-gear-r31-20261005\device-evidence');W.mkdir(exist_ok=True)
os.environ['ANDROID_USER_HOME']=r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
adb=[r'G:\Android\Sdk\platform-tools\adb.exe','-s','RQCY30751WY']
name=sys.argv[1];assert name.replace('-','').replace('_','').isalnum()
if len(sys.argv)>2:
 assert sys.argv[2] in ['tap','swipe','keyevent','text']
 subprocess.run(adb+['shell','input']+sys.argv[2:],check=True)
 time.sleep(1.5)
screen=subprocess.run(adb+['exec-out','screencap','-p'],capture_output=True,check=True)
(W/(name+'.png')).write_bytes(screen.stdout)
r=subprocess.run(adb+['logcat','-d','-v','threadtime','StationRooms:W','*:S'],capture_output=True)
(W/(name+'.log')).write_bytes(r.stdout)
print(str(W/(name+'.png')))
print(r.stdout.decode('utf8',errors='replace')[-4500:])
