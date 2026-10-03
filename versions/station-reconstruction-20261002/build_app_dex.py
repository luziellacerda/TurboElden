from pathlib import Path
import subprocess,shutil,zipfile,os,json,re
r=Path(__file__).resolve().parent;root=r/'build/dex-integration';os.environ['TEMP']=os.environ['TMP']=str(r/'temp')
java=r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe';tool=r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar'
prepared=root/'prepared';prepared.mkdir(exist_ok=True)
removed=[]
for dex in ['classes5.dex','classes6.dex','classes8.dex']:
 dest=prepared/dex;shutil.copytree(root/(dex+'-decoded'),dest,dirs_exist_ok=True)
 smali=dest/'smali'
 if dex=='classes5.dex':
  for p in smali.rglob('*.smali'):
   if p.name.startswith(('HttpBridge','StationTransfer','DownloadService')):
    if not p.resolve().is_relative_to(prepared.resolve()):raise RuntimeError('Unsafe prepared file')
    removed.append(str(p.relative_to(smali)));p.unlink()
  activity=smali/'org/emulationstation/frontend/ESActivity.smali';text=activity.read_text()
  old='''    invoke-static {}, Lorg/emulationstation/frontend/HttpBridge;->activeFileDownloads()Lorg/emulationstation/frontend/HttpBridge$DownloadSnapshot;

    move-result-object v0

    iget v0, v0, Lorg/emulationstation/frontend/HttpBridge$DownloadSnapshot;->count:I'''
  if text.count(old)!=1:raise RuntimeError('Expected old activity download owner')
  text=text.replace(old,'''    invoke-static {}, Lorg/emulationstation/frontend/station/StationFrontend;->activeCount()I

    move-result v0''')
  getlibs='''.method protected getLibraries()[Ljava/lang/String;
    .locals 3
    const/4 v0, 0x4
    new-array v0, v0, [Ljava/lang/String;
    const/4 v1, 0x0
    const-string v2, "SDL2"
    aput-object v2, v0, v1
    const/4 v1, 0x1
    const-string v2, "station_frontend"
    aput-object v2, v0, v1
    const/4 v1, 0x2
    const-string v2, "main"
    aput-object v2, v0, v1
    const/4 v1, 0x3
    const-string v2, "turbo_carousel"
    aput-object v2, v0, v1
    return-object v0
.end method'''
  text,n=re.subn(r'(?ms)^\.method protected getLibraries\(\)\[Ljava/lang/String;.*?^\.end method',lambda m:getlibs,text)
  if n!=1:raise RuntimeError('Library loading method missing')
  resume='    invoke-static {p0}, Lorg/emulationstation/frontend/auth/LoginActivity;->ensureAuthorized(Landroid/app/Activity;)V'
  if text.count(resume)!=1:raise RuntimeError('Authorization lifecycle missing')
  text=text.replace(resume,'''    const/4 v0, 0x1
    invoke-static {v0}, Lorg/emulationstation/frontend/station/StationFrontend;->setForeground(Z)V
'''+resume)
  if '.method protected onPause()V' in text:raise RuntimeError('Review existing pause behavior first')
  text+='''
.method protected onPause()V
    .locals 1
    const/4 v0, 0x0
    invoke-static {v0}, Lorg/emulationstation/frontend/station/StationFrontend;->setForeground(Z)V
    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onPause()V
    return-void
.end method
'''
  activity.write_text(text,encoding='utf-8')
 elif dex=='classes6.dex':
  activity=smali/'org/libsdl/app/SDLActivity.smali';text=activity.read_text()
  old='Lorg/emulationstation/frontend/auth/AuthSession;->isAuthorized()Z'
  if text.count(old)!=1:raise RuntimeError('Expected SDL auth gate')
  text=text.replace(old,'Lorg/emulationstation/frontend/auth/StationLogin;->ready()Z');activity.write_text(text,encoding='utf-8')
 elif dex=='classes8.dex':
  for directory in ['org/emulationstation/frontend/auth','org/emulationstation/frontend/catalog']:
   for p in (smali/directory).glob('*.smali'):
    if not p.resolve().is_relative_to(prepared.resolve()):raise RuntimeError('Unsafe prepared file')
    removed.append(str(p.relative_to(smali)));p.unlink()
 for p in smali.rglob('*.smali'):
  text=p.read_text()
  if any(v in text for v in ['Lorg/emulationstation/frontend/HttpBridge','Lorg/emulationstation/frontend/GameDownload','Lorg/emulationstation/frontend/StationTransfer','Lorg/emulationstation/frontend/auth/AuthSession','Lorg/emulationstation/frontend/auth/LocalPassword','Lorg/emulationstation/frontend/catalog/LocalCatalog']):raise RuntimeError('Legacy call retained: '+str(p))
 target=prepared/(dex+'.apk')
 subprocess.run([java,'-Djava.io.tmpdir='+str(r/'temp'),'-jar',tool,'b','-f','-p',str(root/'framework'),'-o',str(target),str(dest)],check=True)
 with zipfile.ZipFile(target) as z:(prepared/(dex+'.rebuilt')).write_bytes(z.read('classes.dex'))
# The former GameDownload DEX slot becomes the new client, with old auth removed above.
shutil.copy2(r/'build/dex/classes.dex',prepared/'classes28.dex.rebuilt')
(r/'build/dex-removal-manifest.json').write_text(json.dumps({'removedClasses':removed,'replacementDex':'classes28.dex','baseDexRebuilt':['classes5.dex','classes6.dex','classes8.dex'],'apkIntegrated':False},indent=2),encoding='utf-8')
print('Old frontend classes removed and four replacement DEX files prepared.')
