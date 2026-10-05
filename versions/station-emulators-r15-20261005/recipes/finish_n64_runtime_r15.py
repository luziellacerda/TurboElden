import os
from pathlib import Path
import json,re,struct,shutil,subprocess,zipfile,os,hashlib
W=Path(os.environ['STATION_N64_WORK']);M=W/'merged';D=W/'donor'
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
TOOL=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
SDK=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
os.environ['TEMP']=os.environ['TMP']=str(W/'tmp')
def run(args,name):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,(name,(p.stdout+p.stderr)[-6000:]);print(name, 'OK',flush=True)
def apk(*args):return [J/'java.exe','-Xmx2300m','-Djava.io.tmpdir='+str(W/'tmp'),'-jar',TOOL,*args,'-p',W/'framework']
changes={};root=M/'smali_classes36'
assert not (W/'runtime-adaptations.json').exists(), 'Already adapted; do not reapply'
for p in root.rglob('*.smali'):
 s=p.read_text('utf8');t=re.sub(r'invoke-virtual(/range)? (\{[^}]+\}), Landroid/content/Context;->getSharedPreferences\(Ljava/lang/String;I\)Landroid/content/SharedPreferences;',r'invoke-static\1 \2, Lorg/emulationstation/frontend/N64Bootstrap;->sharedPrefs(Landroid/content/Context;Ljava/lang/String;I)Landroid/content/SharedPreferences;',s)
 t=t.replace('".filesprovider"','".n64.filesprovider"')
 # Keep receiver action scoped to the integrated runtime.
 t=t.replace('org.mupen64plusae.v3.alpha.USB_PERMISSION','org.turboramastation.frontend.n64.USB_PERMISSION')
 if t!=s:p.write_text(t,'utf8');changes[p.relative_to(M).as_posix()]='isolated preferences/provider/USB action'
p=root/'paulscode/android/mupen64plusae/SplashActivity.smali';s=p.read_text('utf8')
needle='.method public requestPermissions()V';a=s.index(needle);b=s.index('.end method',a)+len('.end method')
s=s[:a]+needle+'\n    .locals 0\n    invoke-direct {p0}, Lpaulscode/android/mupen64plusae/SplashActivity;->checkExtractAssetsOrCleanup()V\n    return-void\n.end method'+s[b:]
s=s.replace('    invoke-static {}, Lpaulscode/android/mupen64plusae/util/DeviceUtil;->clearLogCat()V','    # Station retains diagnostics across emulator launches.')
s=s.replace('    invoke-static {p0, v0, v1}, Lpaulscode/android/mupen64plusae/task/SyncProgramsJobService;->scheduleSyncingProgramsForChannel(Landroid/content/Context;J)V','    # TV channel background scanning is not used by the Station catalogue.')
s=s.replace('    invoke-direct {p0}, Lpaulscode/android/mupen64plusae/SplashActivity;->createChannel()V','    # Station uses its existing catalogue, not Android TV channels.')
p.write_text(s,'utf8');changes[p.relative_to(M).as_posix()]='direct app-private preparation; no startup folder picker, log clear or TV job'
# Retain the donor dex partition; avoid overflowing a single dex method table.
cm=json.loads((W/'resource-map.json').read_text('utf8'))['classes'];moved=0
for p in (D/'smali_classes2').rglob('*.smali'):
 old=p.relative_to(D/'smali_classes2').as_posix()[:-6];mapped=cm[old];a=root/(mapped+'.smali')
 if a.exists():
  b=M/'smali_classes37'/(mapped+'.smali');b.parent.mkdir(parents=True,exist_ok=True);shutil.move(a,b);moved+=1
# Rewrite DT_NEEDED / DT_SONAME only, retaining exports, relocations and symbol hash tables.
native=W/'native-libs';native.mkdir(exist_ok=True);elf_receipt=[]
for p in sorted((D/'lib/arm64-v8a').glob('*.so')):
 data=bytearray(p.read_bytes());assert data[:6]==b'\x7fELF\x02\x01'
 phoff=struct.unpack_from('<Q',data,32)[0];ents,count=struct.unpack_from('<HH',data,54);loads=[];dynamic=None
 for i in range(count):
  typ,flags,off,va,pa,fs,ms,align=struct.unpack_from('<IIQQQQQQ',data,phoff+i*ents)
  if typ==1:loads.append((va,off,fs))
  if typ==2:dynamic=(off,fs)
 assert dynamic,p
 entries=[];strva=None
 for off in range(dynamic[0],sum(dynamic),16):
  tag,val=struct.unpack_from('<qQ',data,off)
  if tag==0:break
  if tag==5:strva=val
  if tag in (1,14):entries.append((tag,val))
 assert strva is not None
 strbase=next(off+strva-va for va,off,fs in loads if va<=strva<va+fs);edits=[]
 for tag,index in entries:
  off=strbase+index;end=data.index(0,off);name=bytes(data[off:end])
  if name==b'libc++_shared.so':
   replacement=b'libn64cpp.so';data[off:end]=replacement+b'\0'*(end-off-len(replacement));edits.append({'offset':off,'tag':tag})
 target='libn64cpp.so' if p.name=='libc++_shared.so' else p.name
 (native/target).write_bytes(data);elf_receipt.append({'source':p.name,'target':target,'originalSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(data).hexdigest(),'dynamicEdits':edits})
# Compile the bridge independently of donor classes; it only calls public upstream APIs.
src=W/'java/org/emulationstation/frontend';src.mkdir(parents=True,exist_ok=True)
for name in ('N64Bootstrap.java','N64EntryActivity.java'):shutil.copy2(name,src/name)
cls=W/'bridge-classes';dex=W/'bridge-dex';cls.mkdir(exist_ok=True);dex.mkdir(exist_ok=True)
run([J/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-cp',SDK,'-d',cls,*src.glob('*.java')],'bridge-javac')
run([J/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','28','--lib',SDK,'--output',dex,*cls.rglob('*.class')],'bridge-d8')
shutil.copy2(dex/'classes.dex',W/'classes38.dex')
(W/'runtime-adaptations.json').write_text(json.dumps({'changes':changes,'donorSecondDexClasses':moved,'nativeLibraries':elf_receipt},indent=2),'utf8')
run(apk('b','-o',W/'n64-resources-dex.apk',M),'build-resources-dex')
print('Complete N64 resources, UI, plugins and bridge compiled',flush=True)
