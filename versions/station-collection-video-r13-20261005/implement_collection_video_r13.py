from pathlib import Path
import shutil,subprocess,json,hashlib,imageio_ffmpeg
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=R/'native';W=R/'collection-video-r13';B=W/'before';B.mkdir(exist_ok=False)
names=['native_folders.h','native_info.h','native_formation.h','native_system_video720.h','native_carousel.cpp','video720_posters.h','video720_posters.o']
for n in names:shutil.copyfile(N/n,B/n)
shutil.copyfile('collection_video_policy.h',N/'collection_video_policy.h')
def edit(n,a,b):
 p=N/n;s=p.read_text('utf8');assert a in s,n;p.write_text(s.replace(a,b),'utf8',newline='\n')
edit('native_folders.h','#include "collection_presentation.h"','#include "collection_presentation.h"\n#include "collection_video_policy.h"')
edit('native_folders.h','static U folderRevision;', '''static U folderRevision;
static const CollectionVideoDef*folderVideo(void*p,int index){
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
 if(index<0||!visible||visible+index>=end||visible[index]>=(U)folderCount)return nullptr;
 const auto&m=folderMeta[visible[index]];
 return collectionVideoFor(folderPlatform,strData(m.path),m.kind==2);
}
static float folderVideoAspect(void*p,int index){const auto*v=folderVideo(p,index);return v?v->aspect:1.f;}''')
edit('native_folders.h','if(!folderBridge())return false;U direct=0;if(visitFolders(platform,"",&direct,nullptr,nullptr)==0)return false;','if(!folderBridge())return false;')
edit('native_folders.h',' pauseSystemVideo720();lastSystem=index;foldersEnabled=true;',' lastSystem=index;foldersEnabled=true;')
edit('native_info.h',(N/'native_info.h').read_text('utf8').split('static void*folderLabels[20];')[1].split('static void drawSystemInfoLayer')[0].join(['static void*folderLabels[20];','']), 'static bool isSystemInfoText(void*t){return t==infoTitle||t==infoDescription;}\n')
edit('native_formation.h','static void drawFolderLabels(void*);\n','')
edit('native_formation.h',' drawFolderLabels(p);\n','')
edit('native_formation.h',' return result;\n}', ''' if(folderMode){int index=(int)(at<float>(p,0xf4)+d+.5f);result.h=result.w/folderVideoAspect(p,index);}
 return result;
}''')
edit('native_formation.h','if(systemsMode&&!folderMode){','if(systemsMode){')
edit('native_system_video720.h','sizeof(systemVideo720Definitions)/sizeof(systemVideo720Definitions[0]);','sizeof(systemVideo720Definitions)/sizeof(systemVideo720Definitions[0])+sizeof(collectionVideoDefinitions)/sizeof(collectionVideoDefinitions[0]);')
edit('native_system_video720.h',' if(folderMode)return nullptr;',''' if(folderMode){
  U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
  if(index<0||!visible||visible+index>=end||visible[index]>=(U)folderCount)return nullptr;
  if(const auto*v=folderVideo(p,index))return v->asset;
  for(const auto&v:systemVideo720Definitions)if(strcmp(folderPlatform,v.key)==0)return v.asset;
  return nullptr;
 }''')
edit('native_system_video720.h','if(!systemsMode||folderMode||modal(p)||','if(!systemsMode||modal(p)||')
edit('native_carousel.cpp','if(!systemsMode||folderMode||modal(p))pauseSystemVideo720();','if(!systemsMode||modal(p))pauseSystemVideo720();')
source=Path(r'C:\Users\Admin\Videos\New folder');out=W/'media';out.mkdir();pre=W/'previews';pre.mkdir()
mapping=[('## BOMBER MAN ##.mp4','bomberman',16/9),('## DONKEY KONG ##.mp4','donkeykong',16/9),('## SUPER MARIO ##.mp4','mario',1),('## TOP GEAR ##.mp4','topgear',16/9),('1 -PT-BR.mp4','ptbr',16/9)]
ff=imageio_ffmpeg.get_ffmpeg_exe();rows=[];asm=['.section .rodata.station_collection_previews,"a",%progbits'];decl=[];entries=[]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for index,(name,key,aspect) in enumerate(mapping):
 src=source/name;dst=out/('720-collection-snes-'+key+'.mp4');asset='turbo-system-videos/'+dst.name
 # Square sampling matches the existing decoder/cache; native geometry restores the source aspect.
 args=[ff,'-nostdin','-hide_banner','-loglevel','error','-i',str(src),'-map','0:V:0','-vf','scale=720:720,setsar=1,fps=30','-an','-sn','-dn','-c:v','libx264','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','20','-maxrate','3500k','-bufsize','7000k','-threads','2','-g','60','-bf','0','-movflags','+faststart',str(dst)]
 subprocess.run(args,check=True);raw=pre/(key+'.rgb565')
 subprocess.run([ff,'-nostdin','-hide_banner','-loglevel','error','-i',str(dst),'-frames:v','1','-vf','vflip','-pix_fmt','rgb565le','-f','rawvideo',str(raw)],check=True)
 assert raw.stat().st_size==720*720*2
 symbol='station_collection_video_'+str(index);decl.append('extern const unsigned char '+symbol+'[];');entries.append('{"'+asset+'",'+symbol+'},')
 asm+=['.balign 16','.global '+symbol,'.hidden '+symbol,'.type '+symbol+',%object',symbol+':','.incbin "'+raw.as_posix()+'"','.size '+symbol+',.-'+symbol]
 rows.append({'source':str(src),'sourceSha256':sha(src),'asset':'assets/'+asset,'sha256':sha(dst),'previewSha256':sha(raw),'displayAspect':aspect,'fps':30,'speed':1,'audio':False,'onlyFocusedPlays':True});print('Prepared',name,flush=True)
p=N/'video720_posters.h';s=p.read_text('utf8');s=s.replace('extern "C" {','extern "C" {\n'+'\n'.join(decl));s=s.replace('static const Video720Poster video720Posters[]={','static const Video720Poster video720Posters[]={\n'+'\n'.join(entries));p.write_text(s,'utf8',newline='\n')
(W/'collection_previews.S').write_text('\n'.join(asm)+'\n','utf8',newline='\n')
subprocess.run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','-c',str(W/'collection_previews.S'),'-o',str(W/'collection_previews.o')],check=True)
subprocess.run([r'C:\Program Files\LLVM\bin\ld.lld.exe','-r',str(B/'video720_posters.o'),str(W/'collection_previews.o'),'-o',str(N/'video720_posters.o')],check=True)
(W/'media-manifest.json').write_text(json.dumps({'videos':rows,'sourceFolder':str(source),'allGamesUsesPlatformVideo':True,'cellLabelsRemoved':True},indent=2)+'\n','utf8')
