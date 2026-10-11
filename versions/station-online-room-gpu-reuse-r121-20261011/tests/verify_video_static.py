"""Execute the production VIDEO-off admission/draw helpers under GL mocks.

This is an isolated renderer-path probe, not Android visual or thermal evidence.
The existing retained_draw_state test separately executes the actual GL-state
restoration wrapper. Every generated binary is kept in the ignored temp folder.
"""
from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/led-isolated'
OUT.mkdir(parents=True,exist_ok=True)
video=(ROOT/'native/d0/native_system_video720.h').read_text(encoding='utf-8')
baseline=(ROOT.parent/'station-legacy-cover-diagnostics-r116-20261010/native/d0/native_system_video720.h').read_text(encoding='utf-8')
start=video.index('static bool video720StaticPosterNeeded')
end=video.index('static r53VideoPolicy::Menu video720Menu',start)
helpers=video[start:end]
live=' int cursor=at<int>(p,0xf0);const char*focusedAsset=video720Asset(p,cursor);'
assert video[video.index(live):]==baseline[baseline.index(live):],'VIDEO-on preparation/playback changed'
for forbidden in ['CallStatic','ensureVideo720Jni','video720Start','video720Update','video720Capacity']:
    assert forbidden not in helpers,forbidden
assert helpers.count('seedVideo720Preview(pending)')==1
assert 'if(!videosEnabled){drawStaticSystemVideo720(p,context);return;}' in video
formation=(ROOT/'native/d0/native_formation.h').read_text(encoding='utf-8')
assert 'if(systemsMode&&stationGraphicsEnabled(2))' in formation

code=r'''
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>
using U=unsigned long long;
static U base=1;
static int focus;
template<class T>static T at(void*,U){return (T)focus;}
struct Vertex{float x,y,u,v;unsigned color;};
struct Rect{float x,y,w,h;int index;bool allGames;};
static Rect painted[4];static int paintedCount;
static const char*assets[]={"a","b","c","no-poster"};
struct Poster{const char*asset;};
static const Poster video720Posters[]={{"a"},{"b"},{"c"}};
struct Frame{bool ready;unsigned texture;};
static Frame frames[4];static bool idle=true,supported=true;
static void*video720Context=(void*)1;
static unsigned video720PreviewProgram;static int video720PreviewMVP=9;
static unsigned uploads,draws;static std::vector<int>paintedIds;
static const char*video720Asset(void*,int i){return i>=0&&i<4?assets[i]:nullptr;}
static bool video720Same(const char*a,const char*b){return a&&b&&!strcmp(a,b);}
static Frame*video720Retained(const char*asset){for(int i=0;i<4;i++)if(video720Same(asset,assets[i]))return &frames[i];return nullptr;}
static bool video720SlotsIdle(){return idle;}
struct GLState{int program=33,active=0x84c2;unsigned texture=55;};
static GLState state;
static bool same(GLState a,GLState b){return a.program==b.program&&a.active==b.active&&a.texture==b.texture;}
static void getInteger(unsigned name,int*p){assert(name==0x8b8d);*p=state.program;}
static bool isProgram(unsigned p){return p==77&&supported;}
static void getUniform(unsigned program,int,float*m){assert((int)program==state.program);for(int i=0;i<16;i++)m[i]=(float)i;}
static void useProgram(unsigned p){state.program=(int)p;}
static void matrix(int location,int n,int transpose,const float*m){assert(location==9&&n==1&&transpose==0);for(int i=0;i<16;i++)assert(m[i]==(float)i);}
static void active(unsigned x){state.active=(int)x;}
static void bind(unsigned target,unsigned x){assert(target==0x0de1);state.texture=x;}
struct Laser{decltype(&getInteger)GetIntegerv=getInteger;decltype(&isProgram)IsProgram=isProgram;decltype(&getUniform)GetUniformfv=getUniform;decltype(&useProgram)UseProgram=useProgram;decltype(&matrix)UniformMatrix4fv=matrix;}laserGL;
struct Space{decltype(&active)ActiveTexture=active;decltype(&bind)BindTexture=bind;}spaceGL;
struct SpaceState{GLState old=state;~SpaceState(){state=old;}};
struct Video720RetainedDrawState{GLState old=state;explicit Video720RetainedDrawState(int p){assert(p==state.program);}~Video720RetainedDrawState(){state=old;}};
struct VideoExternalBinding{};
static bool ensureVideo720PreviewProgram(){if(!supported)return false;video720PreviewProgram=77;state.program=77;return true;}
static void seedVideo720Preview(const char*a){uploads++;Frame*f=video720Retained(a);assert(f);f->ready=true;f->texture=101+(unsigned)(f-frames);state.texture=f->texture;}
static void roundedQuad(const Vertex*q,int src,int dst,bool allGames){
 assert(src==4&&dst==5);assert(state.program==77&&state.active==0x84c0);
 int id=(int)(state.texture-101);assert(id>=0&&id<3&&frames[id].ready);
 const Rect&r=painted[id];assert(q[0].x==r.x&&q[0].y==r.y&&q[3].x==r.x+r.w&&q[3].y==r.y+r.h);
 assert(q[0].u==.00138889f&&q[0].v==.99861111f&&q[3].u==.99861111f&&q[3].v==.00138889f);
 assert(allGames==r.allGames);draws++;paintedIds.push_back(id);state.texture=999; // native draw mutates bindings
}
'''+helpers+r'''
static unsigned checks;
static void check(bool x){checks++;assert(x);}
static void reset(){for(auto&f:frames)f={};video720PreviewProgram=0;uploads=draws=0;paintedIds.clear();idle=supported=true;state={};}
int main(){
 paintedCount=4;for(int i=0;i<4;i++)painted[i]={1.f+i*21.f,2.f,20.f,30.f,i,i==0};
 // Every focus is admitted first, all other packaged posters follow one per
 // call, and unsupported/missing artwork remains the original JPG below.
 for(int selected=0;selected<4;selected++){
  reset();focus=selected;
  for(unsigned frame=0;frame<12;frame++){
   unsigned before=uploads;GLState old=state;drawStaticSystemVideo720((void*)2,video720Context);
   check(uploads-before<=1);check(same(old,state));
   if(frame==0)check(paintedIds.front()==(selected==3?0:selected));
   if(frame>=2)check(uploads==3);
  }
  check(!frames[3].ready);check(video720NextStaticPoster((void*)2)==nullptr);
 }
 // Existing retained frame is not uploaded/redecoded, including when it was
 // captured before videos were disabled.
 reset();focus=1;frames[1]={true,102};GLState old=state;
 drawStaticSystemVideo720((void*)2,video720Context);check(uploads==1);check(frames[1].texture==102);check(same(old,state));
 // Lost context, pending decoder retirement, invalid caller program, and an
 // unsupported preview shader do not draw through unproved GL state.
 reset();drawStaticSystemVideo720((void*)2,(void*)3);check(uploads==0&&draws==0);
 idle=false;drawStaticSystemVideo720((void*)2,video720Context);check(uploads==0&&draws==0);
 idle=true;state.program=0;drawStaticSystemVideo720((void*)2,video720Context);check(uploads==0&&draws==0);
 state.program=33;supported=false;old=state;drawStaticSystemVideo720((void*)2,video720Context);check(uploads==0&&draws==0);check(same(old,state));
 std::printf("PASS %u executed static-video admission/draw checks\n",checks);
}
'''
source=OUT/'video_static_probe.cpp';source.write_text(code,encoding='utf-8')
exe=OUT/'video_static_probe.exe'
subprocess.run([r'C:\Program Files\LLVM\bin\clang++.exe','-std=c++17','-O2','-Wall','-Wextra',str(source),'-o',str(exe)],check=True,capture_output=True,text=True)
result=subprocess.run([str(exe)],check=True,capture_output=True,text=True).stdout.strip()
assert result.startswith('PASS ')
record={'productionHelperResult':result,'maxPackagedPosterUploadsPerMenuFrame':1,
        'steadyStatePosterUploads':0,'mediaJniInDisabledPath':False,'originalJpgFallback':True,
        'videoOnPathUnchanged':True,'physicalValidation':False,'thermalClaim':False}
(ROOT/'evidence/video-static-checks.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(result)
