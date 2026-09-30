from pathlib import Path
import hashlib,json,os,subprocess,zipfile,datetime,copy,struct,shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'focus-video-30'
BASE=P/'TurboramaStation-Plataformas-Organizadas.apk';OUT=BASE
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe');BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
def file_sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
sha=lambda b:hashlib.sha256(b).hexdigest()
base_sha=file_sha(BASE);assert base_sha=='af9d76ba686a1e279b215ffd564946c1198d4258cd376f7f91505792f6c38053'
shutil.copy2(Path(__file__),R/'package.py')
media=json.loads((R/'media-manifest.json').read_text(encoding='utf-8'))
replacements={
 'lib/arm64-v8a/libturbo_carousel.so':P/'libturbo_carousel.so',
 'classes9.dex':R/'dex/classes.dex',
 'assets/idle-power-update/source/native_system_video720.h':P/'native_system_video720.h',
 'assets/focus-video-30/media-manifest.json':R/'media-manifest.json',
 'assets/focus-video-30/source/native_system_video720.h':P/'native_system_video720.h',
 'assets/focus-video-30/source/SystemCardVideo720.java':P/'system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java',
 'assets/focus-video-30/source/prepare.py':R/'prepare.py',
 'assets/focus-video-30/source/package.py':R/'package.py',
}
for video in media['videos']:
 source=R/'media'/Path(video['asset']).name;assert file_sha(source)==video['sha256'];replacements[video['asset']]=source
aligned=R/'focus30-aligned.apk'
def write_aligned(out,entry,data):
 info=copy.copy(entry) if isinstance(entry,zipfile.ZipInfo) else zipfile.ZipInfo(entry)
 if not isinstance(entry,zipfile.ZipInfo):info.compress_type=zipfile.ZIP_STORED if entry.endswith(('.so','.dex','.arsc','.mp4')) else zipfile.ZIP_DEFLATED
 if info.filename.startswith('assets/') and info.filename.endswith('.mp4'):info.compress_type=zipfile.ZIP_STORED
 info.extra=b''
 if info.compress_type==zipfile.ZIP_STORED:
  alignment=16384 if info.filename.endswith('.so') else 4
  offset=out.fp.tell()+30+len(info.filename.encode('utf-8'))
  if offset%alignment:
   pad=(-(offset+4))%alignment;info.extra=struct.pack('<HH',0xffff,pad)+bytes(pad)
 out.writestr(info,data)
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(aligned,'w',allowZip64=True) as out:
 seen=set()
 for info in z.infolist():
  name=info.filename
  if name.startswith('META-INF/'):continue
  write_aligned(out,info,replacements[name].read_bytes() if name in replacements else z.read(name));seen.add(name)
 for name,source in replacements.items():
  if name not in seen:write_aligned(out,name,source.read_bytes())
def run(*args):subprocess.run(list(map(str,args)),check=True)
run(BT/'zipalign.exe','-c','-P','16','4',aligned)
run(J,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',__import__('os').environ['TURBORAMA_KEYSTORE'],'--ks-key-alias',__import__('os').environ['TURBORAMA_KEY_ALIAS'],'--ks-pass','env:TURBORAMA_STORE_PASSWORD','--key-pass','env:TURBORAMA_KEY_PASSWORD','--out',OUT,aligned)
run(J,'-jar',BT/'lib/apksigner.jar','verify',OUT)
aligned.unlink()
previous=json.loads((R/'before/entry-hashes.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(OUT) as z:
 for name,digest in previous.items():
  if name in replacements:continue
  assert sha(z.read(name))==digest,'Unexpected change: '+name
 for name,source in replacements.items():assert sha(z.read(name))==file_sha(source),name
 for video in media['videos']:assert z.getinfo(video['asset']).compress_type==zipfile.ZIP_STORED
 assert z.read('classes9.dex').count(b'Lorg/emulationstation/frontend/SystemCardVideo720;')>=1
 changed=[n for n in previous if n in replacements and sha(z.read(n))!=previous[n]]
record={'apk':str(OUT),'sha256':file_sha(OUT),'bytes':OUT.stat().st_size,'base_sha256':base_sha,'native_module_sha256':file_sha(P/'libturbo_carousel.so'),'video_dex_sha256':file_sha(R/'dex/classes.dex'),'built_at':datetime.datetime.now().astimezone().isoformat(),'update':'Only focused system cell plays a 720p30 loop at speed1x; side cards use retained video frames; paused previews stay warm','videos':len(media['videos']),'fps':30,'playback_speed':1.0,'focus_only':True,'loop':True,'all_videos_stored':True,'other_dex_and_engines_identical':True,'changed':changed,'installed':False,'runtime_verified':False,'promoted_to_stable':False}
(R/'build-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='changed'},ensure_ascii=False,indent=2))
