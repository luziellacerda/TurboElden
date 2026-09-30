from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,zipfile
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'saturn-leds';R.mkdir(exist_ok=True)
for part in ['before','media','tmp']:(R/part).mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
APK=P/'TurboramaStation-Plataformas-Organizadas.apk';EXPECTED='33e84a20049b832bfba68992d7e054826fc996455865abc5b4658d11746a6477'
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(APK)==EXPECTED
assert not (R/'before/source-manifest.json').exists(),'Already prepared; inspect current sources and backup first.'
frozen=Path(r'F:\Turborama-build-archive\TurboramaStation-psvita-rar-33e84a20.apk')
if not frozen.exists():shutil.copy2(APK,frozen)
assert sha(frozen)==EXPECTED
names=['native_carousel.cpp','system_video720_assets.h','system_infos.h','theme-infos-mapping.json','laser-user-overrides.json','prepare_laser.py','laser-system-colors.json','laser_assets.h','libturbo_carousel.so']
for name in names:shutil.copy2(P/name,R/'before'/name)
shutil.copy2(P/'stable-design/active-profile.json',R/'before/active-profile.json')
with zipfile.ZipFile(APK) as z:
 (R/'before/entry-hashes.json').write_text(json.dumps({n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.startswith('META-INF/')},indent=2),encoding='utf-8')
(R/'before/source-manifest.json').write_text(json.dumps({'base_sha256':EXPECTED,'frozen_base':str(frozen),'source_files':{n:sha(P/n) for n in names}},indent=2),encoding='utf-8')
palette={'Gameboy Color':['923BFFFF'],'GameCube':['923BFFFF'],'wiiu':['0070FFFF'],'Psvita':['FFFFFFFF'],'sega32x':['FF6A00FF'],'xbox360':['39EF32FF'],'Pc Engine':['FF6A00FF'],'Pc Engine cd':['0070FFFF']}
file=P/'laser-user-overrides.json';data=json.loads(file.read_text(encoding='utf-8'));data['colors'].update(palette);data['latest_instruction']='Explicit owner palette 2026-09-30: GBC/GC purple; WiiU/PCECD blue; Vita white; 32X/PCE orange; Xbox green.'
file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
file=P/'prepare_laser.py';text=file.read_text(encoding='utf-8');text=text.replace("origin='explicit user palette 2026-09-29'","origin='explicit user palette; laser-user-overrides.json'");file.write_text(text,encoding='utf-8')
file=P/'theme-infos-mapping.json';mapping=json.loads(file.read_text(encoding='utf-8'));assert not any(x['key']=='saturn' for x in mapping)
info=json.loads((P/'theme-infos-index.json').read_text(encoding='utf-8'))['saturn']
mapping.append({'key':'saturn','folder':'saturn','file':info['file'],'language':info['language'],'has_description':bool(info['description'])});file.write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
desc=re.split(r'\n\n(?:Italiano:|Ingl[eê]s:|English:)',info['description'])[0]
if len(desc)>600:desc=desc[:597].rsplit(' ',1)[0]+'…'
file=P/'system_infos.h';text=file.read_text(encoding='utf-8');assert '{"saturn",' not in text
row='{'+','.join(json.dumps(x,ensure_ascii=False) for x in ['saturn',info['name'],desc,info['file']])+'},\n'
text=text.replace('};\nstatic constexpr int NINFOS=',row+'};\nstatic constexpr int NINFOS=');file.write_text(text,encoding='utf-8')
file=P/'system_video720_assets.h';text=file.read_text(encoding='utf-8');assert '{"saturn",' not in text
text=text.replace('\n};','\n{"saturn","turbo-system-videos/720-saturn.mp4"},\n};');file.write_text(text,encoding='utf-8')
file=P/'native_carousel.cpp';text=file.read_text(encoding='utf-8')
old='art?art->title:(strcmp(key,"xbox360")==0?"Xbox 360":key)';assert text.count(old)==1
text=text.replace(old,'art?art->title:(strcmp(key,"saturn")==0?"Sega Saturn":(strcmp(key,"xbox360")==0?"Xbox 360":key))')
# Exact Saturn command is added after the existing native route has been audited.
file.write_text(text,encoding='utf-8')
sys.path.insert(0,str(P/'system-videos/tools'));import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();src=Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas\saturno.mp4');dest=R/'media/720-saturn.mp4'
subprocess.run([ff,'-hide_banner','-loglevel','error','-nostdin','-y','-i',str(src),'-vf','scale=720:720:force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','19','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',str(dest)],check=True)
reader=imageio_ffmpeg.read_frames(str(src));before=next(reader);reader.close();reader=imageio_ffmpeg.read_frames(str(dest));after=next(reader);reader.close()
assert tuple(after['size'])==(720,720) and abs(after['fps']-30)<.01 and abs(before['duration']-after['duration'])<.08
media={'key':'saturn','source':str(src),'source_sha256':sha(src),'source_fps':before['fps'],'source_duration':before['duration'],'asset':'assets/turbo-system-videos/'+dest.name,'sha256':sha(dest),'width':720,'height':720,'fps':30,'duration':after['duration'],'speed':1.0,'loop':True,'focus_only':True}
(R/'media-manifest.json').write_text(json.dumps(media,indent=2)+'\n',encoding='utf-8');(R/'requested-leds.json').write_text(json.dumps(palette,indent=2)+'\n',encoding='utf-8')
shutil.copy2(Path(__file__),R/'prepare_saturn_leds.py')
print(json.dumps({'media':media,'leds':palette,'backup':str(frozen)},ensure_ascii=False))
