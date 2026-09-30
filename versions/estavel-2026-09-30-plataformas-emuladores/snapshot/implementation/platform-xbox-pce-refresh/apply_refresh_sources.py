from pathlib import Path
import json,hashlib,urllib.request,urllib.parse,re,shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-xbox-pce-refresh';M=R/'merged'
manifest=json.loads((R/'covers-manifest.json').read_text(encoding='utf-8'))
missing=json.loads((R/'covers-missing.json').read_text(encoding='utf-8'))
for f in missing:
 assert f['normalized']=='sensiblesoccerinternationaledition'
 tree=json.loads((R/'jaguar-cover-tree.json').read_text(encoding='utf-8'));opts=[x['path'] for x in tree['tree'] if x['path'].startswith('Named_Boxarts/International Sensible Soccer')];print('Sensible candidates',opts)
 chosen=next(x for x in opts if '(World)' in x and 'Beta' not in x)
 url='https://raw.githubusercontent.com/libretro-thumbnails/Atari_-_Jaguar/'+tree['sha']+'/'+urllib.parse.quote(chosen)
 data=urllib.request.urlopen(url,timeout=20).read();assert data.startswith(b'\x89PNG');name=f['id']+'.png';(M/'assets/platform-refresh/covers'/name).write_bytes(data)
 manifest.append({**{k:f[k] for k in ['category','id','name']},'source':url,'asset':'platform-refresh/covers/'+name,'local':'/data/data/org.emulationstation.frontend/files/turbo-game-covers/'+name,'sha256':hashlib.sha256(data).hexdigest()})
assert len(manifest)==58
(R/'covers-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');(R/'covers-missing.json').write_text('[]',encoding='utf-8')
catalog=json.loads((R/'catalog-refresh.json').read_text(encoding='utf-8'))
owner=json.loads(Path(r'C:\Users\Admin\AppData\Roaming\SamboxManagerBase\drawers.json').read_text(encoding='utf-8-sig'))
c=next(c for c in owner if c['Name']=='Psp - BR');assert len(c['Files'])==59
(R/'pspbr-source.json').write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
c.update({'CatalogLabel':'roms','R2Pasta':'pspbr','Android':True,'AndroidPackage':c['RequiredPackage'],'AndroidDemo':c['Demo'],'AndroidMensal':c['Mensal'],'Oculta':False})
catalog.append(c);(R/'catalog-refresh.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Local, title-specific cover mapping avoids network requests for the repaired platforms.
h='// Exact catalog IDs; source/provenance: platform-xbox-pce-refresh/covers-manifest.json\nstruct LocalGameCover {const char*id;const char*path;};\nstatic const LocalGameCover localGameCovers[]={\n'
h+=''.join('{'+json.dumps(f['id'])+','+json.dumps(f['local'])+'},\n' for f in manifest)+'};\n'
(P/'local_game_covers.h').write_text(h,encoding='utf-8')
p=P/'native_carousel.cpp';s=p.read_text(encoding='utf-8');assert '#include "native_xboxclassic.h"' not in s
s=s.replace('#include "relocations.h"','#include "relocations.h"\n#include "local_game_covers.h"')
needle=' syncedRevision=rev;syncedItems=begin;syncedSize=size;'
s=s.replace(needle,needle+'''
 // Local covers exist before catalog startup. Never change IDs, download paths, or saves.
 for(B*it=at<B*>(real,0x88);it<at<B*>(real,0x90);it+=0xe8){
  const char*platform=strData(it+0x60);
  if(strcmp(platform,"jaguar")!=0&&strcmp(platform,"Pc Engine cd")!=0)continue;
  for(U j=0;j<sizeof(localGameCovers)/sizeof(localGameCovers[0]);j++)if(strcmp(strData(it),localGameCovers[j].id)==0){
   void*file=fopen(localGameCovers[j].path,"rb");if(file){fclose(file);strAssign(it+0xc8,localGameCovers[j].path);}break;
  }
 }
''')
s=s.replace('{"PSP",1,30}', '{"PSP",1,30},{"Psp - BR",1,30},{"pspbr",1,30}')
s=s.replace('if(strcmp(key,systems[j].key)==0){art=&systems[j];break;}','if(strcmp(key,systems[j].key)==0||(strcmp(key,"Psp - BR")==0&&strcmp(systems[j].key,"PSP")==0)){art=&systems[j];break;}')
s=s.replace('strAssign(item+0x18,art?art->title:', 'strAssign(item+0x18,strcmp(key,"Psp - BR")==0?"PSP - BR":art?art->title:')
s=s.replace('#include "native_saturn.h"','#include "native_saturn.h"\n#include "native_xboxclassic.h"\n#include "native_pcecd.h"')
needle=' const char*key=strData(folder);'
assert s.count(needle)==1
s=s.replace(needle,needle+'''
 if(presentationKeyEqual(key,"xbox")){UiString result={};strAssign(&result,"libretro: core=x1box_android.so");return result;}
 if(presentationKeyEqual(key,"Psp - BR")||presentationKeyEqual(key,"pspbr")){UiString result={};strAssign(&result,"libretro: core=ppsspp_libretro_android.so");return result;}
 if(presentationKeyEqual(key,"Pc Engine cd")||presentationKeyEqual(key,"pcenginecd")){UiString result={};strAssign(&result,"libretro: core=mednafen_pce_libretro_android.so");return result;}
 if(presentationKeyEqual(key,"naomi")||presentationKeyEqual(key,"naomi2")){UiString result={};strAssign(&result,"libretro: core=flycast_libretro_android.so");return result;}
''')
for name in ['Run','Fresh','Bundled','Installed','Assets','Pack','Definitions','Settings','KnownCores']:
 s=s.replace('(void*)saturn'+name+'Hook','(void*)refresh'+name+'Hook')
p.write_text(s,encoding='utf-8')
template=(P/'native_saturn.h').read_text(encoding='utf-8').replace('saturn','xboxClassic').replace('Saturn','Xbox').replace('vita','saturn').replace('Yaba Sanshiro 1.20.46','X1 BOX 1.2.8').replace('Sega Xbox','Xbox clássico').replace('XboxBootstrap','XboxBootstrap')
start=template.index('static bool xboxClassicCore');end=template.index('\n',start)
template=template[:start]+'static bool xboxClassicCore(const void*id){const char*s=strData(id);return uiContains(s,"x1box")||strcmp(s,"Xbox clássico")==0||strcmp(s,"xbox")==0;}'+template[end:]
(P/'native_xboxclassic.h').write_text(template,encoding='utf-8')
# Video assets: preserve existing clips and decoding policy. Only these mappings change.
p=P/'system_video720_assets.h';s=p.read_text(encoding='utf-8')
s=s.replace('{"MegaDrive - BR","turbo-system-videos/720-megadrive.mp4"}','{"MegaDrive - BR","turbo-system-videos/720-megadrivebr.mp4"}').replace('{"Super Nintendo - BR","turbo-system-videos/720-snes.mp4"}','{"Super Nintendo - BR","turbo-system-videos/720-snesbr.mp4"}')
for key,slug in [('xbox','xbox'),('Psp - BR','psp'),('naomi','naomi'),('naomi2','naomi2')]:
 if '{'+json.dumps(key)+',' not in s:s=s.replace('\n};','\n{'+json.dumps(key)+',"turbo-system-videos/720-'+slug+'.mp4"},\n};')
p.write_text(s,encoding='utf-8')
p=P/'system_infos.h';s=p.read_text(encoding='utf-8');infos=json.loads((P/'theme-infos-index.json').read_text(encoding='utf-8'))
for key,slug,title in [('xbox','xbox','Xbox clássico'),('Psp - BR','psp','PSP - BR'),('naomi','naomi','Sega Naomi'),('naomi2','naomi2','Sega Naomi 2')]:
 if '{'+json.dumps(key)+',' in s:continue
 info=infos[slug];desc=info['description'].split('\n\nItaliano:')[0][:600]
 row='{'+','.join(json.dumps(v,ensure_ascii=False) for v in [key,title,desc,info['file']])+'},\n'
 s=s.replace('};\nstatic constexpr int NINFOS=',row+'};\nstatic constexpr int NINFOS=')
p.write_text(s,encoding='utf-8')
# Only append palette rows; do not regenerate unrelated visual resources.
p=P/'laser_assets.h';s=p.read_text(encoding='utf-8')
needle='{"xbox360",0x39EF32FF'
assert needle in s
row=next(l for l in s.splitlines() if l.startswith('{"xbox360",'))
s=s.replace(row,row+'\n'+row.replace('"xbox360"','"xbox"'))
row=next(l for l in s.splitlines() if l.startswith('{"PSP",'));s=s.replace(row,row+'\n'+row.replace('"PSP"','"Psp - BR"'));p.write_text(s,encoding='utf-8')
newhash=hashlib.sha256((R/'catalog-refresh.json').read_bytes()).hexdigest();oldhash=hashlib.sha256((R/'catalog-before.json').read_bytes()).hexdigest()
p=M/'smali_classes8/org/emulationstation/frontend/catalog/CatalogData.smali';s=p.read_text(encoding='utf-8');assert s.count(oldhash)==2;p.write_text(s.replace(oldhash,newhash),encoding='utf-8')
print('Catalog',len(catalog),'categories;',sum(len(c['Files']) for c in catalog),'items;',newhash)
