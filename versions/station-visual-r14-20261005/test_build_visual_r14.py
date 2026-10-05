from pathlib import Path
import subprocess,json,re,hashlib,io,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=R/'native';W=R/'visual-r14';T=W/'tests';T.mkdir(exist_ok=True)
def method(s,name):
 p=s.index(name);a=s.index('{',p);i=a+1;depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 return s[p:i]
def run(args,name):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,(name,p.stdout+p.stderr);print((p.stdout+p.stderr)[-1200:],flush=True);return p.stdout
cpp=r'''#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <vector>
#include <cstring>
using U=uintptr_t;using B=unsigned char;
struct Vertex{float x,y,u,v;unsigned color;};
static unsigned ticks;static bool record;static FILE*out;static float left,top,width,height;static int draws;
static unsigned clockTick(){return ticks;}static unsigned packed(unsigned c){return c;}
static void bind(unsigned){}
static void draw(const Vertex*v,unsigned n,int,int){
 assert(n>0&&n<=382);draws++;
 if(record)fprintf(out,"%u",n);
 for(unsigned i=0;i<n;i++){
  assert(std::isfinite(v[i].x)&&std::isfinite(v[i].y));
  assert(v[i].x>=left-.02f&&v[i].x<=left+width+.02f&&v[i].y>=top-.02f&&v[i].y<=top+height+.02f);
  assert((v[i].color&255)==255);
  if(record)fprintf(out," %.4f %.4f %u",v[i].x,v[i].y,v[i].color);
 }
 if(record)fprintf(out,"\n");
}
template<class T>static T fn(U p){if(p==0x39e240)return (T)clockTick;if(p==0x2e3980)return (T)packed;if(p==0x2e52e8)return (T)bind;assert(p==0x2e5470);return (T)draw;}
template<class T>static T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
'''
formation=(N/'native_formation.h').read_text('utf8');motion=(N/'native_action_motion.h').read_text('utf8');skin=(N/'native_skin.h').read_text('utf8')
for src,sig in [(formation,'static float absolute('),(formation,'static float squareRoot('),(formation,'static unsigned blendColor('),(motion,'static float actionClamp('),(motion,'static float actionEase('),(skin,'static void openButtonFill(')]:cpp+=method(src,sig)+'\n'
cpp+='\n#include "native_game_actions.h"\n'
cpp+='struct CoverRect{float x,y,w,h;int index;}; static bool systemsMode=true;\n'+method(formation,'static CoverRect coverSlot(')+'\n'
cpp+=r'''
int main(int argc,char**argv){
 unsigned frames[]={0,300,800,1900,3600,4199,4200,0xfffffff0u};int cases=0;
 for(float w:{180.f,288.f,351.f,600.f})for(float h:{32.f,44.f,70.f,102.f})for(unsigned t:frames)for(int slot=0;slot<8;slot++)for(bool disabled:{false,true})for(bool confirm:{false,true}){
  left=10;top=20;width=w;height=h;ticks=t;drawGameAction(left,top,w,h,slot,disabled,false,confirm);cases++;
 }
 int before=draws;drawGameAction(0,0,0,50,0,false,false,false);assert(before==draws);
 for(int i=0;i<6;i++)for(int j=i+1;j<6;j++)assert(gameActionPalette(i,false,false).accent!=gameActionPalette(j,false,false).accent);
 alignas(8) B ui[256]={};int geometry=0;
 for(float sw:{1280.f,1920.f,2340.f,2560.f})for(float sh:{720.f,1080.f,1440.f}){
  at<float>(ui,0x54)=sw;at<float>(ui,0x58)=sh;
  for(int i=-20;i<=132;i++){auto r=coverSlot(ui,i/20.f);assert(std::abs(r.w-r.h)<.01);geometry++;}
 }
 printf("PASS %d action meshes: all vertices inside, 8 icons, 6 distinct colors, disabled/confirming states; %d square carousel slots\n",cases,geometry);
 if(argc>1){out=fopen(argv[1],"w");assert(out);record=true;
  for(int i=0;i<8;i++){left=24+(i%4)*374;top=24+(i/4)*140;width=350;height=90;ticks=1400;drawGameAction(left,top,width,height,i,false,false,i==3);}
  fclose(out);
 }
}'''
(T/'actions.cpp').write_text(cpp,'utf8')
run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-I'+str(N),T/'actions.cpp','-o',T/'actions.exe'],'actions-compile')
actions=run([T/'actions.exe',W/'mesh.txt'],'actions')
im=Image.new('RGB',(1544,310),(6,10,15));dr=ImageDraw.Draw(im)
for line in (W/'mesh.txt').read_text().splitlines():
 a=line.split();n=int(a[0]);v=[(float(a[i]),float(a[i+1]),int(a[i+2])) for i in range(1,len(a),3)];assert len(v)==n
 for i in range(2,n):
  tri=v[i-2:i+1];c=tri[-1][2];dr.polygon([(p[0],p[1]) for p in tri],fill=((c>>24)&255,(c>>16)&255,(c>>8)&255))
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',23)
for i,label in enumerate(['JOGAR','JOGAR ONLINE','SALVAR','APAGAR','ATUALIZAR','VOLTAR','ABRIR','BAIXAR']):
 x=24+(i%4)*374;y=24+(i//4)*140;dr.text((x+90+(350-90-14)/2,y+45),label,fill='#F3FFF6',font=font,anchor='mm')
im.save(W/'buttons-preview.png')
# Execute actual folder/navigation code; video aspect metadata no longer modifies layout.
nav=(R/'collection-video-r13/tests/navigation.cpp').read_text('utf8');(T/'navigation.cpp').write_text(nav,'utf8')
run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-I'+str(N),'-I'+str(R/'station/src/native'),T/'navigation.cpp','-o',T/'navigation.exe'],'navigation-compile');navigation=run([T/'navigation.exe'],'navigation')
checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
oldnet=(W/'before/native_netplay.h').read_text('utf8');net=(N/'native_netplay.h').read_text('utf8')
for sig in ['static bool touchOnlineAction(','static bool dispatchStationNetplay(']:check(sig+' unchanged',method(oldnet,sig)==method(net,sig))
check('native hit rectangles unchanged','bounds(buttons+i*20,4,x,h*(systemsMode?.851f:.908f),width,h*(systemsMode?.094f:.065f));' in skin)
check('square all folder/platform cells','folderVideoAspect' not in formation)
check('cell strips and labels remain removed','drawFolderLabels' not in formation+(N/'native_info.h').read_text('utf8'))
check('video lifecycle source unchanged',(N/'native_system_video720.h').read_bytes()==(R/'collection-video-r13/before/native_system_video720.h').read_bytes() or (N/'native_system_video720.h').read_bytes()==Path('work/TurboElden-git/versions/station-collection-video-r13-20261005/native/native_system_video720.h').read_bytes())
ff=imageio_ffmpeg.get_ffmpeg_exe();media=[]
for row in json.loads((W/'media-manifest.json').read_text('utf8'))['videos']:
 dst=W/'media'/Path(row['asset']).name
 p=subprocess.run([ff,'-hide_banner','-i',str(dst),'-f','null','-'],capture_output=True,text=True,errors='replace');assert p.returncode==0,p.stderr
 assert '720x720' in p.stderr and '30 fps' in p.stderr and 'Error' not in p.stderr
 duration=re.search(r'Duration: (\d+:\d+:\d+\.\d+)',p.stderr).group(1)
 result={'asset':row['asset'],'fullDecodePassed':True,'duration':duration,'frame':'720x720','fps':30}
 if row['sourceAspect']!=1:
  r=subprocess.run([ff,'-nostdin','-hide_banner','-loglevel','error','-i',row['source'],'-map','0:V:0','-vf','scale=720:-1','-frames:v','1','-f','image2pipe','-c:v','png','-'],capture_output=True);assert r.returncode==0
  src=Image.open(io.BytesIO(r.stdout)).convert('RGB');rendered=Image.open(W/(dst.stem.removeprefix('720-collection-snes-')+'.png')).convert('RGB');assert src.size==(720,405)
  from PIL import ImageChops,ImageStat
  offset,error=min(((y,sum(ImageStat.Stat(ImageChops.difference(src,rendered.crop((0,y,720,y+405)))).mean)/3) for y in [156,157,158]),key=lambda x:x[1]);assert error<9,(dst,error)
  result.update(fullForegroundMeanAbsoluteError=error,foregroundBounds=[0,offset,720,405],foregroundAspect=720/405)
 media.append(result)
run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',N/'native_carousel.cpp',N/'video720_posters.o','-L',N,'-lc','-ldl','-llog','-o',W/'libturbo_carousel.so'],'native-build')
(W/'tests.json').write_text(json.dumps({'passed':True,'actions':actions,'navigation':navigation,'checks':checks,'media':media,'compiledAndroid26':True,'deviceVisualVerified':False},indent=2)+'\n','utf8')
print('All PC checks passed; Android library built')
