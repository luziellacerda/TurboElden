from pathlib import Path
import json,re,shutil,os,subprocess,zipfile,xml.etree.ElementTree as ET,hashlib
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-xbox-pce-refresh';M=R/'merged';D=M/'smali_classes26'
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
# Every donor Context directory is isolated from the host and other emulators.
for p in D.rglob('*.smali'):
 s=p.read_text(encoding='utf-8');t=s
 for method,args,target in [('getFilesDir','','files'),('getExternalFilesDir','Ljava/lang/String;','userFiles'),('getCacheDir','','cache')]:
  t=re.sub(r'invoke-virtual(.*?)L(?:android/content/Context|android/app/Activity|com/izzy2lost/x1box/[^;]+);->'+method+r'\('+args+r'\)Ljava/io/File;',r'invoke-static\1Lorg/emulationstation/frontend/XboxBootstrap;->'+target+'(Landroid/content/Context;'+args+')Ljava/io/File;',t)
 if t!=s:p.write_text(t,encoding='utf-8')
for folder in ['smali','smali_classes8']:
 shutil.copytree(R/'modules-decoded'/folder,M/folder,dirs_exist_ok=True)
p=M/'smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=p.read_text(encoding='utf-8')
needle='    invoke-super {p0}, Landroid/app/Application;->onCreate()V';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    invoke-static {p0}, Lorg/emulationstation/frontend/XboxBootstrap;->initProcess(Landroid/app/Application;)Z\n    move-result v7\n    if-eqz v7, :turbo_not_xbox_classic\n    return-void\n    :turbo_not_xbox_classic\n')
# Covers install only in the main frontend process, after all emulator guards.
needle='    invoke-static {p0}, Lorg/yuzu/yuzu_emu/bootstrap/BootstrapAssets;->installKeys(Landroid/content/Context;)V'
assert s.count(needle)==1;s=s.replace(needle,'    invoke-static {p0}, Lorg/emulationstation/frontend/PlatformAssets;->install(Landroid/content/Context;)V\n'+needle);p.write_text(s,encoding='utf-8')
# Existing native exit finishes its own process. Redirect its UI destination to the host.
p=D/'com/izzy2lost/x1box/MainActivity.smali';s=p.read_text(encoding='utf-8')
assert s.count('const-class v3, Lcom/izzy2lost/x1box/GameLibraryActivity;')==1
s=s.replace('const-class v3, Lcom/izzy2lost/x1box/GameLibraryActivity;','const-class v3, Lorg/emulationstation/frontend/ESActivity;')
s=s.replace('    invoke-direct {p0, v2}, Lcom/izzy2lost/x1box/MainActivity;->nativeSetReturnToLibraryOnExit(Z)V','    const/4 v2, 0x0\n    invoke-direct {p0, v2}, Lcom/izzy2lost/x1box/MainActivity;->nativeSetReturnToLibraryOnExit(Z)V')
p.write_text(s,encoding='utf-8')
# Label the official exit accurately inside the host; all rendering/settings stay native to X1 BOX.
for p in (M/'res').glob('values*/xc_strings.xml'):
 t=ET.parse(p);changed=False
 for e in t.getroot():
  if e.get('name')=='xc_in_game_menu_exit_to_library':e.text='Voltar à TurboramaStation';changed=True
 if changed:t.write(p,encoding='utf-8',xml_declaration=True)
A='{http://schemas.android.com/apk/res/android}';ET.register_namespace('android',A[1:-1]);p=M/'AndroidManifest.xml';t=ET.parse(p);app=t.getroot().find('application')
ET.SubElement(app,'activity',{A+'name':'org.emulationstation.frontend.XboxEntryActivity',A+'process':':xbox',A+'exported':'false',A+'screenOrientation':'userLandscape',A+'theme':'@android:style/Theme.Material.NoActionBar',A+'taskAffinity':'org.emulationstation.frontend'})
t.write(p,encoding='utf-8',xml_declaration=True)
src=Path(r'G:\ESTUDOS MONTAR SISTEMA\SAMBOX-Vfull\sistema\bios');setup=M/'assets/xbox-classic/setup';setup.mkdir(parents=True,exist_ok=True)
record=[]
for n in ['mcpx_1.0.bin','Complex_4627.bin','xbox_hdd.qcow2']:
 shutil.copy2(src/n,setup/n);record.append({'source':str(src/n),'asset':'xbox-classic/setup/'+n,'sha256':hashlib.sha256((src/n).read_bytes()).hexdigest(),'bytes':(src/n).stat().st_size})
data=(src/'syscard3.pce').read_bytes();raw=data[512:] if len(data)==262656 else data
assert len(raw)==262144 and hashlib.md5(raw).hexdigest()=='38179df8f4ac870017db21ebcbf53114'
setup=M/'assets/platform-refresh/setup';setup.mkdir(parents=True,exist_ok=True);(setup/'syscard3.pce').write_bytes(raw)
record.append({'source':str(src/'syscard3.pce'),'asset':'platform-refresh/setup/syscard3.pce','removed_copier_header':len(data)-len(raw),'md5':hashlib.md5(raw).hexdigest(),'sha256':hashlib.sha256(raw).hexdigest()})
(R/'local-setup-provenance.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
srcdir=R/'java/org/emulationstation/frontend';srcdir.mkdir(parents=True,exist_ok=True)
for n in ['XboxBootstrap.java','XboxEntryActivity.java','PlatformAssets.java']:shutil.copy2(Path(__file__).parent/n,srcdir/n)
classes=R/'java-classes';classes.mkdir(exist_ok=True)
subprocess.run([str(J/'javac.exe'),'-encoding','UTF-8','-source','8','-target','8','-classpath',r'G:\Android\Sdk\platforms\android-34\android.jar','-d',str(classes),*map(str,srcdir.glob('*.java'))],check=True)
with zipfile.ZipFile(R/'bridge.jar','w') as z:
 for p in classes.rglob('*.class'):z.write(p,p.relative_to(classes).as_posix())
(R/'bridge-dex').mkdir(exist_ok=True)
subprocess.run([str(J/'java.exe'),'-cp',str(BT/'lib/d8.jar'),'com.android.tools.r8.D8','--min-api','26','--lib',r'G:\Android\Sdk\platforms\android-34\android.jar','--output',str(R/'bridge-dex'),str(R/'bridge.jar')],check=True)
print('X1 BOX isolated bridge and local setup prepared')
