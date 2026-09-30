import pathlib,zipfile,subprocess,os,re,hashlib,sys
p=pathlib.Path(__file__).parent
full='--full' in sys.argv
if any(a in sys.argv for a in ['--engine-manifest','--loading-manifest']):
 raise RuntimeError('Active profile is stable with design only. Experimental engine/loading requires a new explicit maintainer request.')
base=pathlib.Path('E:\\ESTUDO APK\\work\\native-carousel\\implementation\\stable-reference-audit\\original-1.0.8-alignment-preserved.apk') if full else p.parent.parent/'TurboramaStation-baseline-phone-signed.apk'
apk=p/('TurboramaStation-ESTAVEL-6727ab7-design.apk' if full else 'TurboramaStation-carrossel-nativo-teste.apk')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='5cd234d0ac57aa6f1b260db6278087b7d961c671385ecf47871570bc00e78814', 'Wrong stable reference'
with zipfile.ZipFile(base) as baseline:
 assert hashlib.sha256(baseline.read('lib/arm64-v8a/libmain.so')).hexdigest()=='a1ae357dc29caac52d47386a71a0a9a685ecffb9c01d536f5af50b5ba658cda8'
 assert hashlib.sha256(baseline.read('classes5.dex')).hexdigest()=='e8717570af37f536e53e63ac52918c6bec714e0c03a6e180ff5207724feb1fc8' 
java=r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe'
apktool=r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar'
bt=pathlib.Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['JAVA_HOME']=str(pathlib.Path(java).parent.parent);os.environ['TEMP']=str(p/'tmp');os.environ['TMP']=str(p/'tmp')
def run(args):subprocess.run([str(x) for x in args],check=True)
decode=p/'stable-loader-decode'
if not decode.exists():
 with zipfile.ZipFile(base) as z,zipfile.ZipFile(p/'loader-input.apk','w') as out:
  for name in ['AndroidManifest.xml','resources.arsc']:out.writestr(name,z.read(name))
  out.writestr('classes.dex',z.read('classes5.dex'))
 run([java,'-Djava.io.tmpdir='+str(p/'tmp'),'-jar',apktool,'d','-r','-f','-p',p/'framework','-o',decode,p/'loader-input.apk'])
 sm=decode/'smali/org/emulationstation/frontend/ESActivity.smali';txt=sm.read_text(encoding='utf-8')
 start=txt.index('.method protected getLibraries()');end=txt.index('.end method',start)+len('.end method')
 method='''.method protected getLibraries()[Ljava/lang/String;
    .locals 3
    const/4 v0, 0x3
    new-array v0, v0, [Ljava/lang/String;
    const/4 v1, 0x0
    const-string v2, "SDL2"
    aput-object v2, v0, v1
    const/4 v1, 0x1
    const-string v2, "main"
    aput-object v2, v0, v1
    const/4 v1, 0x2
    const-string v2, "turbo_carousel"
    aput-object v2, v0, v1
    return-object v0
.end method

.method protected getMainSharedObject()Ljava/lang/String;
    .locals 1
    const-string v0, "libmain.so"
    return-object v0
.end method'''
 assert 'getMainSharedObject()' not in txt
 sm.write_text(txt[:start]+method+txt[end:],encoding='utf-8')
sm=decode/'smali/org/emulationstation/frontend/ESActivity.smali'
txt=sm.read_text(encoding='utf-8')
loader_changed='.method public dispatchKeyEvent(' not in txt
if loader_changed:
 sm.write_text(txt+'\n'+(p/'android_back_bridge.smali').read_text(encoding='utf-8'),encoding='utf-8')
backclass=decode/'smali/org/emulationstation/frontend/NativeCarouselBack.smali'
backtext=(p/'NativeCarouselBack.smali').read_text(encoding='utf-8-sig')
if not backclass.exists() or backclass.read_text(encoding='utf-8')!=backtext:
 backclass.write_text(backtext,encoding='utf-8');loader_changed=True
txt=sm.read_text(encoding='utf-8')
if 'NativeCarouselBack;->install' not in txt:
 needle='invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onResume()V'
 assert txt.count(needle)==1
 txt=txt.replace(needle,needle+'\n\n    invoke-static {p0}, Lorg/emulationstation/frontend/NativeCarouselBack;->install(Landroid/app/Activity;)V')
 sm.write_text(txt,encoding='utf-8');loader_changed=True
txt=sm.read_text(encoding='utf-8')
if ':native_back_done' not in txt:
 a=txt.index('.method protected onResume()V');b=txt.index('.end method',a)
 method=txt[a:b].replace('.locals 0','.locals 2')
 call='invoke-static {p0}, Lorg/emulationstation/frontend/NativeCarouselBack;->install(Landroid/app/Activity;)V'
 method=method.replace(call,'sget v0, Landroid/os/Build$VERSION;->SDK_INT:I\n    const/16 v1, 0x21\n    if-lt v0, v1, :native_back_done\n    '+call+'\n    :native_back_done')
 sm.write_text(txt[:a]+method+txt[b:],encoding='utf-8');loader_changed=True
if loader_changed or not (p/'stable-loader-built.apk').exists():
 run([java,'-Djava.io.tmpdir='+str(p/'tmp'),'-jar',apktool,'b','-p',p/'framework','-o',p/'stable-loader-built.apk',decode])
with zipfile.ZipFile(p/'stable-loader-built.apk') as l: dex=l.read('classes.dex')
with zipfile.ZipFile(base) as z,zipfile.ZipFile(p/'carousel-unsigned.apk','w',allowZip64=True) as out:
 for info in z.infolist():
  if info.filename.startswith('META-INF/'):continue
  out.writestr(info,dex if info.filename=='classes5.dex' else z.read(info.filename))
 out.write(p/'libturbo_carousel.so','lib/arm64-v8a/libturbo_carousel.so',compress_type=zipfile.ZIP_STORED)
 for name in ['premium-selection-laser.glsl','premium-selection-laser-android.glsl','premium-selection-glow.svg','laser-system-colors.json']:out.write(p/name,'assets/turbo-carousel/'+name,compress_type=zipfile.ZIP_DEFLATED)
 for asset in [p/'premium-spacecraft-rear-v2.png',p/'game-info-coverage-final.json',p/'game-info-unmatched-final.json',p/'game-title-aliases.json',p/'turborama-palette.json']:out.write(asset,'assets/turbo-carousel/'+asset.name,compress_type=zipfile.ZIP_DEFLATED)
 for name in ['USO-E-ACESSO.md','NOTICE-TURBORAMA.txt','ai-access-policy.json','AGENTS.md','CLAUDE.md','GEMINI.md']:out.write(p/name,'assets/turborama-policy/'+name,compress_type=zipfile.ZIP_DEFLATED)
 for name in __import__('json').loads((p/'space3d/license-assets.json').read_text()):out.write(p/'space3d'/name,'assets/turbo-space3d/'+name,compress_type=zipfile.ZIP_DEFLATED)
 for info in sorted((p/'game-info-xml').glob('*.xml')):out.write(info,'assets/turbo-game-info/'+info.name,compress_type=zipfile.ZIP_DEFLATED)
 for info in sorted((p/'theme-infos').glob('*.xml')):out.write(info,'assets/turbo-system-info/xml/'+info.name,compress_type=zipfile.ZIP_DEFLATED)
 out.write(p/'theme-infos-index.json','assets/turbo-system-info/index.json',compress_type=zipfile.ZIP_DEFLATED)
 out.write(p/'theme-infos-mapping.json','assets/turbo-system-info/mapping.json',compress_type=zipfile.ZIP_DEFLATED)
run([bt/'zipalign.exe','-f','-P','16','4',p/'carousel-unsigned.apk',p/'carousel-aligned.apk'])
run([str(bt/'apksigner.bat'),'sign','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',apk,p/'carousel-aligned.apk'])
run([str(bt/'apksigner.bat'),'verify','--verbose','--print-certs',apk])
print('APK',apk,'bytes',apk.stat().st_size,'sha256',hashlib.sha256(apk.read_bytes()).hexdigest())
# Active branding requested after the stable rollback. The intermediate design APK
# remains a separate artifact; the deliverable includes the login and launcher icon.
if full:
 run([sys.executable,p/'brand-login/build_brand_login.py','--base-apk',apk,'--base-sha256',hashlib.sha256(apk.read_bytes()).hexdigest()])
 video_base=p/'TurboramaStation-design-base-videos.apk'
 run([sys.executable,p/'system-videos/build_videos.py','--base-apk',video_base,'--base-sha256',hashlib.sha256(video_base.read_bytes()).hexdigest()])
