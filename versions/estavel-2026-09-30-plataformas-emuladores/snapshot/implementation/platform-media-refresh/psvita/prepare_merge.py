from pathlib import Path
import json,zipfile,struct,subprocess,shutil,os,re,urllib.request
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-media-refresh/psvita';os.environ['TEMP']=os.environ['TMP']=str(R.parent/'tmp')
APK=P/'TurboramaStation-Plataformas-Organizadas.apk'
def strings_and_classes(d):
    count,off=struct.unpack_from('<II',d,56);strings=[]
    for i in range(count):
        pos=struct.unpack_from('<I',d,off+4*i)[0]
        while d[pos]&128:pos+=1
        pos+=1;end=d.index(0,pos);strings.append(d[pos:end].decode('utf-8',errors='replace'))
    count,off=struct.unpack_from('<II',d,64);types=[strings[struct.unpack_from('<I',d,off+4*i)[0]] for i in range(count)]
    count,off=struct.unpack_from('<II',d,96)
    return [types[struct.unpack_from('<I',d,off+32*i)[0]][1:-1] for i in range(count)]
with zipfile.ZipFile(APK) as z:
    names=z.namelist();classes=[]
    for name in names:
        if re.fullmatch(r'classes\d*\.dex',name):classes+=strings_and_classes(z.read(name))
    (R/'base-classes.json').write_text(json.dumps(classes),encoding='utf-8')
    with zipfile.ZipFile(R/'frontend-module.apk','w') as o:
        for name in names:
            if name in ['AndroidManifest.xml','resources.arsc','classes.dex'] or name.startswith('res/'):
                o.writestr(name,z.read(name))
    collisions=[]
    for f in (R/'donor-decoded/assets').rglob('*'):
        if f.is_file():
            name='assets/'+f.relative_to(R/'donor-decoded/assets').as_posix()
            if name.startswith('assets/dexopt/'):continue
            if name in names and z.read(name)!=f.read_bytes():collisions.append(name)
    assert not collisions, collisions
java=r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe';tool=r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar'
subprocess.run([java,'-jar',tool,'d','-f',str(R/'frontend-module.apk'),'-o',str(R/'frontend-decoded')],check=True)
# Adapt the already established resource/DEX isolation merger to the Vita donor.
s=(P/'xbox360-integration/prepare.py').read_text(encoding='utf-8')
s=re.sub(r"R=Path\(r'[^']+'\)",lambda _:"R=Path(r'"+str(R)+"')",s,count=1)
s=s.replace("D=R/'current-decoded'", "D=R/'donor-decoded'")
s=s.replace("'tx_'+", "'tv_'+").replace("'tx_'", "'tv_'")
s=s.replace('xendroid.compose','org.vita3k.emulator').replace('xendroid/compose/','org/vita3k/emulator/')
s=s.replace("old.startswith(('xendroid/',))", "old.startswith(('org/vita3k/',))")
s=s.replace('org/p2sdlx/','org/vtsdlx/').replace('tx360cor','tvita3kc')
s=s.replace('start=21','start=23').replace(':xbox360emu',':psvita').replace(':xbox360',':psvita')
s=s.replace('org.emulationstation.frontend.xbox360.','org.emulationstation.frontend.psvita.')
s=s.replace("'xsl_alloc_hook'","'vsl_alloc_hook'").replace("'xhok_impl'","'vhok_impl'").replace("'x360_hook'","'vita_hook'").replace("'xile_redirect_hook'","'vile_redirect_hook'").replace("'x3c_shared'","'v3c_shared'")
s=s.replace("if e.tag not in ['uses-library','service']:","if e.tag != 'uses-library':")
s=s.replace("if 'ShortcutActivity' in name or 'profileinstaller' in name:continue", "if 'shortcuts.' in name or 'ShortcutActivity' in name or 'profileinstaller' in name:continue")
s=s[:s.index("notice=M/'assets/xbox360-integration'")]
s+="\n(R/'class-map.json').write_text(json.dumps(class_map))\n(R/'resource-map.json').write_text(json.dumps(resource_map))\nprint('Prepared Vita classes:',len(class_map),'resources:',len(idmap))\n"
(R/'merge_resources.py').write_text(s,encoding='utf-8')
subprocess.run([str(Path(os.sys.executable)),str(R/'merge_resources.py')],check=True)
# Leave all donor startup code intact, but register the relocated SDL native methods before use.
f=R/'merged/smali_classes23/org/vita3k/emulator/Vita3KApplication.smali';s=f.read_text()
needle='    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    invoke-static {}, Lorg/emulationstation/frontend/VitaBootstrap;->registerSdl()V')
s+='''
.method public static initEmbedded(Landroid/app/Application;)V
 .locals 1
 new-instance v0, Lorg/vita3k/emulator/Vita3KApplication;
 invoke-direct {v0}, Lorg/vita3k/emulator/Vita3KApplication;-><init>()V
 invoke-virtual {v0, p0}, Lorg/vita3k/emulator/Vita3KApplication;->attachEmbedded(Landroid/content/Context;)V
 invoke-virtual {v0}, Lorg/vita3k/emulator/Vita3KApplication;->onCreate()V
 return-void
.end method
.method public attachEmbedded(Landroid/content/Context;)V
 .locals 0
 invoke-super {p0, p1}, Landroid/app/Application;->attachBaseContext(Landroid/content/Context;)V
 return-void
.end method
''';f.write_text(s,encoding='utf-8')
f=R/'merged/smali/org/yuzu/yuzu_emu/YuzuApplication.smali';s=f.read_text()
needle='    invoke-super {p0}, Landroid/app/Application;->onCreate()V';assert s.count(needle)==1
s=s.replace(needle,needle+'''
    invoke-static {p0}, Lorg/emulationstation/frontend/VitaBootstrap;->initProcess(Landroid/app/Application;)Z
    move-result v7
    if-eqz v7, :turbo_not_psvita
    return-void
    :turbo_not_psvita
''');f.write_text(s,encoding='utf-8')
# Storage isolation is applied to donor code only, including its shaded helpers.
for f in (R/'merged/smali_classes23').rglob('*.smali'):
    s=f.read_text();original=s
    for method,args,target in [('getFilesDir','','files'),('getExternalFilesDir','Ljava/lang/String;','userFiles'),('getCacheDir','','cache')]:
        s=re.sub(r'invoke-virtual(.*?)Landroid/content/Context;->'+method+r'\('+args+r'\)Ljava/io/File;',r'invoke-static\1Lorg/emulationstation/frontend/VitaBootstrap;->'+target+'(Landroid/content/Context;'+args+')Ljava/io/File;',s)
    s=re.sub(r'invoke-virtual(.*?)Landroid/content/Context;->getSharedPreferences\(Ljava/lang/String;I\)Landroid/content/SharedPreferences;',r'invoke-static\1Lorg/emulationstation/frontend/VitaBootstrap;->preferences(Landroid/content/Context;Ljava/lang/String;I)Landroid/content/SharedPreferences;',s)
    if s!=original:f.write_text(s,encoding='utf-8')
shutil.copy2(Path(__file__),R/'prepare_merge.py')
print('Vita resource merge and isolated startup prepared.',flush=True)
