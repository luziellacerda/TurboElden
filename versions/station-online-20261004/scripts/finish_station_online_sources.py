from pathlib import Path
import shutil,hashlib,zipfile,json,re
R=Path(r'E:\StationNetplayWork');P=Path(__file__).resolve().parent/'station-online-proposed';S=R/'station/src/java/org/emulationstation/frontend/station'
for p in P.glob('*.java'):shutil.copy2(p,R/'netplay/src/org/emulationstation/frontend/netplay'/p.name)
def patch(p,old,new):
 t=p.read_text('utf-8');assert t.count(old)==1,(p,t.count(old));p.write_text(t.replace(old,new),'utf-8',newline='\n')
patch(S/'StationAndroid.java','        coordinator=new StationCoordinator(api,sessions,catalogs,covers,privateFiles,clock);','''        coordinator=new StationCoordinator(api,sessions,catalogs,covers,privateFiles,clock);
        try{Class.forName("org.emulationstation.frontend.netplay.StationPresence").getMethod("install",Context.class).invoke(null,context);}
        catch(ReflectiveOperationException optional){android.util.Log.w("StationOnline","Presence module unavailable");}''')
patch(S/'StationFrontend.java','foreground=visible;images.setForeground(visible);publishForeground(visible);','''foreground=visible;images.setForeground(visible);publishForeground(visible);
  StationAndroid onlineApp=StationAndroid.current();if(onlineApp!=null)try{Class.forName("org.emulationstation.frontend.netplay.StationPresence").getMethod("foreground",Context.class,boolean.class).invoke(null,onlineApp.context,visible);}catch(ReflectiveOperationException optional){android.util.Log.w("StationOnline","Presence lifecycle unavailable");}''')
cached=Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003\host-merged');host=R/'application/module'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(cached/'build/apk/classes.dex')==sha(R/'application/classes.original.dex')
assert not host.exists();host.mkdir()
shutil.copytree(cached/'smali',host/'smali')
for name in ('AndroidManifest.xml','resources.arsc','apktool.yml'):shutil.copy2(cached/name,host/name)
app=host/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali'
patch(app,'    invoke-super {p0}, Landroid/app/Application;->onCreate()V','''    invoke-super {p0}, Landroid/app/Application;->onCreate()V
    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationProcess;->isNetplay()Z
    move-result v7
    if-eqz v7, :station_not_direct_netplay
    return-void
    :station_not_direct_netplay''')
changes=[p.relative_to(cached/'smali').as_posix() for p in (cached/'smali').rglob('*.smali') if p.read_bytes()!=(host/'smali'/p.relative_to(cached/'smali')).read_bytes()]
assert changes==['org/yuzu/yuzu_emu/YuzuApplication.smali'],changes
(R/'evidence/application-change.json').write_text(json.dumps({'baseDexSha256':sha(R/'application/classes.original.dex'),'cachedDexMatchedApk':True,'changedSmali':changes,'purpose':'Skip unrelated offline engine/application initialization only in :station_netplay process'},indent=2),'utf-8')
print('Application isolation and foreground presence integrated')
