from pathlib import Path
import copy,datetime,hashlib,json,os,shutil,struct,subprocess,sys,zipfile

P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
R=P/'platform-videos-arcade-20260930'; D=R; D.mkdir(exist_ok=True); (D/'tmp').mkdir(exist_ok=True)
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk'
FROZEN=Path(r'F:\Turborama-build-archive\TurboramaStation-videos-br-544fdecb.apk')
EXPECTED='544fdecbc512a128827b392dcc96461573db9a16c09dc343bc3d958749980b81'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(*a):subprocess.run(list(map(str,a)),check=True)
assert sha(BASE)==EXPECTED
assert FROZEN.exists()
assert sha(FROZEN)==EXPECTED

shutil.copy2(P/'system_video720_assets.h',D/'system_video720_assets.before.h')
shutil.copy2(P/'native_system_video720.h',D/'native_system_video720.before.h')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
sys.path.insert(0,str(P/'system-videos/tools'));import imageio_ffmpeg
folder=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas')
media=[]
for key,name,slug in [('Arcade','ARCADE.mp4','arcade'),('fbneo','fbneo.mp4','fbneo'),('mame','mame.mp4','mame')]:
    src=folder/name;dst=D/('720-'+slug+'.mp4')
    run(imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-nostdin','-y','-i',src,'-vf','scale=720:720:force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','19','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',dst)
    a=imageio_ffmpeg.read_frames(str(src));before=next(a);a.close();a=imageio_ffmpeg.read_frames(str(dst));after=next(a);a.close()
    assert tuple(after['size'])==(720,720) and abs(after['fps']-30)<.01 and abs(before['duration']-after['duration'])<.08
    media.append({'key':key,'source':str(src),'source_sha256':sha(src),'asset':'assets/turbo-system-videos/'+dst.name,'sha256':sha(dst),'source_duration':before['duration'],'duration':after['duration'],'fps':30,'size':[720,720],'speed':1,'loop':True,'focus_only':True})
    print('Prepared '+name,flush=True)
(D/'media-manifest.json').write_text(json.dumps(media,indent=2,ensure_ascii=False),encoding='utf-8')
f=P/'system_video720_assets.h';s=(D/'system_video720_assets.before.h').read_text(encoding='utf-8')
assert '{"Arcade","turbo-system-videos/720-mame.mp4"}' in s
s=s.replace('{"Arcade","turbo-system-videos/720-mame.mp4"}','{"Arcade","turbo-system-videos/720-arcade.mp4"}')
v=P/'native_system_video720.h';t=v.read_text(encoding='utf-8')
assert 'static constexpr int video720FrameCount=40;' in t
t=t.replace('static constexpr int video720FrameCount=40;','static constexpr int video720FrameCount=sizeof(systemVideo720Definitions)/sizeof(systemVideo720Definitions[0]);')
v.write_text(t,encoding='utf-8')
f.write_text(s,encoding='utf-8')
run(r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',P/'native_carousel.cpp','-L'+str(P),'-lc','-ldl','-llog','-o',D/'libturbo_carousel.so')
changes={'lib/arm64-v8a/libturbo_carousel.so':(D/'libturbo_carousel.so').read_bytes(),'assets/platform-refresh/videos-arcade-20260930-manifest.json':(D/'media-manifest.json').read_bytes()}
for row in media:changes[row['asset']]=(D/Path(row['asset']).name).read_bytes()
with zipfile.ZipFile(FROZEN) as z:
    for n in z.namelist():
        if n.startswith('assets/') and Path(n).name=='system_video720_assets.h':changes[n]=f.read_bytes()
        if n.startswith('assets/') and Path(n).name=='native_system_video720.h':changes[n]=(P/'native_system_video720.h').read_bytes()
aligned=D/'aligned.apk';assert not aligned.exists()
def put(z,old,data):
    info=copy.copy(old) if isinstance(old,zipfile.ZipInfo) else zipfile.ZipInfo(old)
    if not isinstance(old,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if old.endswith(('.so','.mp4')) else zipfile.ZIP_DEFLATED
    info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
        align=16384 if info.filename.endswith('.so') else 4;off=z.fp.tell()+30+len(info.filename.encode())
        if off%align:pad=(-(off+4))%align;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
    z.writestr(info,data)
with zipfile.ZipFile(FROZEN) as z,zipfile.ZipFile(aligned,'w') as out:
    seen=set()
    for info in z.infolist():
        if info.filename.startswith('META-INF/'):continue
        put(out,info,changes.get(info.filename,z.read(info.filename)));seen.add(info.filename)
    for n,data in changes.items():
        if n not in seen:put(out,n,data)
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15');J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(J/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',os.environ['TURBORAMA_SIGNING_KEYSTORE'],'--ks-key-alias',os.environ['TURBORAMA_SIGNING_ALIAS'],'--ks-pass','env:TURBORAMA_SIGNING_PASSWORD','--key-pass','env:TURBORAMA_SIGNING_PASSWORD','--out',BASE,aligned)
run(J/'java.exe','-jar',BT/'lib/apksigner.jar','verify',BASE)
with zipfile.ZipFile(FROZEN) as old,zipfile.ZipFile(BASE) as new:
    for n in old.namelist():
        if n.startswith('META-INF/') or n in changes:continue
        assert hashlib.sha256(old.read(n)).digest()==hashlib.sha256(new.read(n)).digest(),n
    for n,data in changes.items():assert new.read(n)==data,n
aligned.unlink()
shutil.copy2(D/'libturbo_carousel.so',P/'libturbo_carousel.so')

record={'built_at':datetime.datetime.now().astimezone().isoformat(),'apk':str(BASE),'sha256':sha(BASE),'bytes':BASE.stat().st_size,'base_sha256':EXPECTED,'base_apk':str(FROZEN),'media':media,'all_non_video_logic_preserved':True,'preview_capacity':'derived from platform video definitions; no new active players','unchanged_entries_verified':True,'native_module_sha256':sha(P/'libturbo_carousel.so'),'installed':False,'git_published':False}
(D/'build-result.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
f=P/'stable-design/active-profile.json';v=json.loads(f.read_text(encoding='utf-8'));v.update({'pending_apk':str(BASE),'pending_apk_sha256':record['sha256'],'pending_build':str(D/'build-result.json'),'installation_pending':True,'latest_built_apk':str(BASE),'latest_built_apk_sha256':record['sha256'],'latest_build_record':str(D/'build-result.json')});f.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
if Path(__file__).resolve() != (D/'update_videos.py').resolve():shutil.copy2(__file__,D/'update_videos.py')
print(json.dumps(record,ensure_ascii=False))
