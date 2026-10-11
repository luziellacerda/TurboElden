"""Host-only regression using real R123 geometry/draw/hit/preference bodies.

No phone, server, ROM, decoder or GPU is used. Generated fixtures stay outside Git.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone


def raw(path):
    return Path("\\\\?\\" + str(path.resolve())).read_bytes()


def text(path):
    return raw(path).decode("utf-8").replace("\r\n", "\n")


def body(source, name):
    match = re.search(r"static [^\n;]*\b" + re.escape(name) + r"\([^\n]*?\)\{", source)
    assert match, name
    start = source.index("{", match.start())
    depth = 1
    end = start + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


def run(args):
    completed = subprocess.run([str(x) for x in args], capture_output=True, text=True, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return completed.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--clang", type=Path, default=Path(r"C:\Program Files\LLVM\bin\clang++.exe"))
    parser.add_argument("--jdk", type=Path, default=Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin"))
    parser.add_argument("--ndk", type=Path, default=Path(r"E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    base = root.parent / "station-theme-room-download-r122-20261011"
    args.work.mkdir(parents=True, exist_ok=True)
    formation = text(root / "native/d0/native_formation.h")
    prior = text(base / "native/d0/native_formation.h")
    assert 'String[] styleNames={"Reta","Diagonal","De lado"};' in text(root / "java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPanel.java")
    guards = 0
    for name in ("contentLeft", "cornerRadius", "squareRoot", "blendColor", "blendVertex", "formationTouch"):
        assert body(formation, name) == body(prior, name), name
        guards += 1
    for f in ("native/d0/native_magazine.h", "native/d0/native_magazine_field.h", "native/d0/magazine_shader.h", "native/d0/native_space.h", "native/d0/native_theme_switch.h", "native/d0/station_ribbon_placement.h", "java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java"):
        assert raw(root/f) == raw(base/f), f
        guards += 1
    f = "native/d0/native_system_video720.h"
    assert raw(root/f).replace(b"roundedCoverQuad(q,4,5,r);", b"roundedQuad(q,4,5,r.allGames);") == raw(base/f)
    guards += 1
    f = "native/d0/installed_art_r48.h"
    assert raw(root/f).replace(b"drawFormationStrip(q,4,4,5);", b"fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);") == raw(base/f)
    guards += 1
    bridge = text(root/"frontend/station_frontend.cpp")
    old_bridge = text(base/"frontend/station_frontend.cpp")
    added = 'std::atomic<int> carouselStyle{0}; // Separate UI-only field; existing graphics snapshot stays identical.\n'
    assert bridge.count(added) == 1
    bridge = bridge.replace(added, "")
    start = bridge.index("API int StationCarousel_style()")
    end = bridge.index("API uint64_t StationGraphics_snapshot()", start)
    bridge = bridge[:start] + bridge[end:]
    assert bridge.count("size_t coverPlanBudget=9;") == 1
    bridge = bridge.replace("size_t coverPlanBudget=9;", "")
    start = bridge.index("API void StationCatalog_prioritize(")
    end = bridge.index("API bool StationCatalog_start(", start)
    prior_start = old_bridge.index("API void StationCatalog_prioritize(")
    prior_end = old_bridge.index("API bool StationCatalog_start(", prior_start)
    # This one visible-window budget method has its own actual-body host proof.
    bridge = bridge[:start] + old_bridge[prior_start:prior_end] + bridge[end:]
    assert bridge == old_bridge
    guards += 1
    for f in ("station_carousel_geometry.h", "collection_corner_policy.h"):
        (args.work/f).write_bytes(raw(root/"native/d0"/f))
    common = "\n".join(body(formation, name) for name in ("cornerRadius", "squareRoot", "blendColor", "blendVertex"))
    perspective = formation[formation.index("struct FormationPerspectiveGL"):formation.index("// Transform the final existing strip only:")]
    actual = perspective + "\n" + "\n".join(body(formation, name) for name in ("drawFormationStrip", "roundedQuad", "roundedCoverQuad", "hitCover", "clipFormationHook"))
    fixture = r'''
#include <cassert>
#include <cmath>
#include <cstring>
#include <iostream>
#include <vector>
#include "station_carousel_geometry.h"
#include "collection_corner_policy.h"
using U=unsigned long;using B=unsigned char;
static bool systemsMode=false,folderMode=false,mappingCover=false;
struct Vertex {float x,y,u,v;unsigned color;};
struct CoverRect {float x,y,w,h;int index;bool allGames=false;stationCarouselGeometry::Transform projection{};};
struct Int2{int x,y;};
static CoverRect painted[20];static int paintedCount;
static const stationCarouselGeometry::Transform*formationProjection;
static float sourceX,sourceY,scaleX=1,scaleY=1,targetX,targetY;
static std::vector<Vertex> captured;static int capturedSrc,capturedDst,draws;static Int2 clipPos,clipSize;
static float currentMVP[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1},drawMVP[16];
static int activeProgram=3,uniformLocation=7,uniformWrites,glQueries,glResolves,glOpens;
static void getInteger(unsigned,int*p){*p=activeProgram;glQueries++;}
static int getLocation(unsigned program,const char*name){glQueries++;if((program==3&&!std::strcmp(name,"u_mvp"))||(program==4&&!std::strcmp(name,"MVPMatrix")))return uniformLocation;return -1;}
static void getUniform(unsigned,int,float*p){std::memcpy(p,currentMVP,sizeof(currentMVP));glQueries++;}
static void setUniform(int,int,B,const float*p){std::memcpy(currentMVP,p,sizeof(currentMVP));uniformWrites++;}
static void* dlopen(const char*,int){glOpens++;return (void*)1;}
static void* dlsym(void*,const char*name){glResolves++;if(!std::strcmp(name,"glGetIntegerv"))return (void*)getInteger;if(!std::strcmp(name,"glGetUniformLocation"))return (void*)getLocation;if(!std::strcmp(name,"glGetUniformfv"))return (void*)getUniform;return (void*)setUniform;}
static void capture(const Vertex*v,unsigned n,int src,int dst){captured.assign(v,v+n);std::memcpy(drawMVP,currentMVP,sizeof(drawMVP));capturedSrc=src;capturedDst=dst;draws++;}
static void captureClip(const Int2*p,const Int2*s){clipPos=*p;clipSize=*s;}
template<class T>static T fn(U address){return address==0x2e5470?reinterpret_cast<T>(capture):reinterpret_cast<T>(captureClip);}
__COMMON__
namespace baseline {
__BASE_ROUNDED__
}
__ACTUAL__
static long long checks;static void check(bool value){assert(value);checks++;}
int main(){
 for(int kind=0;kind<3;kind++){
  systemsMode=kind!=0;folderMode=kind==2;
  for(float w:{24.f,64.f,96.f,180.f,400.f})for(float aspect:{.72f,1.f,1.5f})for(int sign:{-1,1}){
   float h=w/aspect,x=42.25f,y=27.125f;int index=3+sign,selected=3;
   Vertex q[4]={{x,y,.15f,.2f,0xa0b1c2d3},{x,y+h,.15f,.8f,0xa0b1c2d3},{x+w,y,.75f,.2f,0xfedcba98},{x+w,y+h,.75f,.8f,0xfedcba98}};
   for(int style:{0,1})for(bool effects:{false,true}){
    auto t=stationCarouselGeometry::make(x,y,w,h,index,selected,style,effects);
    formationProjection=&t;int before=draws;roundedQuad(q,4,5,kind==2);auto actual=captured;
    check(draws==before+1);check(capturedSrc==4&&capturedDst==5);
    formationProjection=nullptr;baseline::roundedQuad(q,4,5,kind==2);auto expected=captured;
    check(actual.size()==expected.size());
    for(size_t i=0;i<actual.size();i++){
     check(actual[i].u==expected[i].u&&actual[i].v==expected[i].v&&actual[i].color==expected[i].color);
     auto point=t.map(expected[i].x,expected[i].y);
     check(actual[i].x==point.x&&actual[i].y==point.y);
     if(!t.active)check(std::memcmp(&actual[i],&expected[i],sizeof(Vertex))==0);
    }
    if(!t.active){check(t.map(-0.f,y).x==0);continue;}
    check(std::fabs(std::atan2(t.s,t.c)*180/3.141592653589793)<7.5001);
    check(std::fabs(std::atan2(t.s,t.c)*180/3.141592653589793)>7.4999);
    check((t.s>0)==(sign<0));
    auto b=t.bounds(x,y,w,h);check(b.x>=x-.001f&&b.y>=y-.001f&&b.x+b.w<=x+w+.001f&&b.y+b.h<=y+h+.001f);
    for(int ix=0;ix<=10;ix++)for(int iy=0;iy<=10;iy++){
     float px=x+w*ix/10,py=y+h*iy/10;auto point=t.map(px,py),back=t.inverse(point.x,point.y);
     check(std::fabs(back.x-px)<.001f&&std::fabs(back.y-py)<.001f);
    }
    CoverRect r{x,y,w,h,index,kind==2,t};formationProjection=nullptr;roundedCoverQuad(q,4,5,r);check(formationProjection==nullptr);check(captured.size()==expected.size());
    paintedCount=1;painted[0]=r;auto center=t.map(x+w/2,y+h/2);check(hitCover(center.x,center.y)==index);
    auto outside=t.map(x-w*.1f,y+h/2);check(hitCover(outside.x,outside.y)==-1);
    mappingCover=true;sourceX=sourceY=targetX=targetY=0;scaleX=scaleY=1;formationProjection=&t;
    Int2 pos{(int)x,(int)y},size{(int)w,(int)h};clipFormationHook(&pos,&size);
    auto bounds=t.bounds((float)pos.x,(float)pos.y,(float)size.x,(float)size.y);
    check(clipPos.x<=bounds.x&&clipPos.y<=bounds.y&&clipPos.x+clipSize.x>=bounds.x+bounds.w&&clipPos.y+clipSize.y>=bounds.y+bounds.h);
    mappingCover=false;formationProjection=nullptr;
   }
   auto selectedTransform=stationCarouselGeometry::make(x,y,w,h,selected,selected,1,true);check(!selectedTransform.active);
   formationProjection=&selectedTransform;roundedQuad(q,4,5,kind==2);auto hero=captured;formationProjection=nullptr;baseline::roundedQuad(q,4,5,kind==2);check(hero.size()==captured.size()&&std::memcmp(hero.data(),captured.data(),hero.size()*sizeof(Vertex))==0);
  }
 }
 systemsMode=false;folderMode=false;paintedCount=7;
 for(int i=0;i<7;i++){painted[i]={20.f+i*110.f,15.f,100.f,140.f,i,false,stationCarouselGeometry::make(20.f+i*110.f,15.f,100.f,140.f,i,0,1,true)};auto&r=painted[i];auto point=r.projection.map(r.x+r.w/2,r.y+r.h/2);check(hitCover(point.x,point.y)==i);}
 for(int style:{-1,0,3})check(!stationCarouselGeometry::make(0,0,100,100,1,0,style,true).active);
 for(float zero:{0.f,-1.f})check(!stationCarouselGeometry::make(0,0,zero,100,1,0,1,true).active);
 check(glQueries==0&&uniformWrites==0&&glResolves==0&&glOpens==0); // Reta/Diagonal do not enter GL presentation.
 for(int kind=0;kind<3;kind++)for(float w:{24.f,96.f,180.f,400.f})for(float aspect:{.72f,1.f,1.5f})for(int sign:{-1,1}){
  systemsMode=kind!=0;folderMode=kind==2;float x=420.25f,y=27.125f,h=w/aspect;int index=3+sign,selected=3;
  activeProgram=kind%2?3:4;auto t=stationCarouselGeometry::make(x,y,w,h,index,selected,2,true);check(t.active&&t.projective);check((t.depth>0)==(sign<0));
  auto b=t.bounds(x,y,w,h);check(b.x>=x-.002f&&b.y>=y-.002f&&b.x+b.w<=x+w+.002f&&b.y+b.h<=y+h+.002f);
  for(int ix=0;ix<=12;ix++)for(int iy=0;iy<=12;iy++){
   float px=x+w*ix/12,py=y+h*iy/12;auto point=t.map(px,py),back=t.inverse(point.x,point.y);check(std::fabs(back.x-px)<.003f&&std::fabs(back.y-py)<.003f);
  }
  const float identity[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};std::memcpy(currentMVP,identity,sizeof(identity));
  Vertex q[4]={{x,y,0,0,0xa0b1c2d3},{x,y+h,0,1,0xa0b1c2d3},{x+w,y,1,0,0xfedcba98},{x+w,y+h,1,1,0xfedcba98}};
  formationProjection=nullptr;baseline::roundedQuad(q,4,5,kind==2);auto expected=captured;
  formationProjection=&t;int before=draws,writes=uniformWrites;roundedQuad(q,4,5,kind==2);check(draws==before+1&&uniformWrites==writes+2);
  check(captured.size()==expected.size()&&std::memcmp(captured.data(),expected.data(),captured.size()*sizeof(Vertex))==0);check(std::memcmp(currentMVP,identity,sizeof(identity))==0);
  for(const auto&v:captured){auto point=t.map(v.x,v.y);float W=drawMVP[3]*v.x+drawMVP[7]*v.y+drawMVP[15];check(W>.60f);check(std::fabs((drawMVP[0]*v.x+drawMVP[4]*v.y+drawMVP[12])/W-point.x)<.005f);check(std::fabs((drawMVP[1]*v.x+drawMVP[5]*v.y+drawMVP[13])/W-point.y)<.005f);}
  // Raster varyings use UV/W with clip-W; verify both triangle halves against the inverse homography.
  for(int iu=1;iu<10;iu++)for(int iv=1;iv<10;iv++){
   float u=iu/10.f,v=iv/10.f;int a=0,bv=1,c=2;if(u+v>1){a=1;bv=3;c=2;}
   auto A=t.map(q[a].x,q[a].y),Bq=t.map(q[bv].x,q[bv].y),C=t.map(q[c].x,q[c].y),P=t.map(x+w*u,y+h*v);
   float D=(Bq.y-C.y)*(A.x-C.x)+(C.x-Bq.x)*(A.y-C.y);
   float la=((Bq.y-C.y)*(P.x-C.x)+(C.x-Bq.x)*(P.y-C.y))/D,lb=((C.y-A.y)*(P.x-C.x)+(A.x-C.x)*(P.y-C.y))/D,lc=1-la-lb;
   float wa=1+t.depth*(q[a].x-t.cx),wb=1+t.depth*(q[bv].x-t.cx),wc=1+t.depth*(q[c].x-t.cx),weight=la/wa+lb/wb+lc/wc;
   check(std::fabs((la*q[a].u/wa+lb*q[bv].u/wb+lc*q[c].u/wc)/weight-u)<.00005f);check(std::fabs((la*q[a].v/wa+lb*q[bv].v/wb+lc*q[c].v/wc)/weight-v)<.00005f);
  }
  CoverRect r{x,y,w,h,index,kind==2,t};paintedCount=1;painted[0]=r;auto center=t.map(x+w/2,y+h/2);check(hitCover(center.x,center.y)==index);auto outside=t.map(x-w*.1f,y+h/2);check(hitCover(outside.x,outside.y)==-1);
  mappingCover=true;sourceX=sourceY=targetX=targetY=0;scaleX=scaleY=1;Int2 pos{(int)x,(int)y},size{(int)w,(int)h};clipFormationHook(&pos,&size);auto bounds=t.bounds((float)pos.x,(float)pos.y,(float)size.x,(float)size.y);check(clipPos.x<=bounds.x&&clipPos.y<=bounds.y&&clipPos.x+clipSize.x>=bounds.x+bounds.w&&clipPos.y+clipSize.y>=bounds.y+bounds.h);mappingCover=false;
  formationProjection=nullptr;roundedCoverQuad(q,4,5,r);check(formationProjection==nullptr&&std::memcmp(currentMVP,identity,sizeof(identity))==0);
  auto hero=stationCarouselGeometry::make(x,y,w,h,selected,selected,2,true);check(!hero.active&&!hero.projective);formationProjection=&hero;before=glQueries;drawFormationStrip(q,4,4,5);check(before==glQueries&&std::memcmp(captured.data(),q,sizeof(q))==0);
  check(!stationCarouselGeometry::make(x,y,w,h,index,selected,2,false).active);
 }
 check(glOpens==1&&glResolves==4);activeProgram=3;check(formationPerspectiveLocation(3)==7);activeProgram=4;check(formationPerspectiveLocation(4)==7);check(formationPerspectiveAvailable());activeProgram=3;int before=uniformWrites;activeProgram=0;check(!formationPerspectiveAvailable());check(!drawFormationPerspectiveStrip(captured.data(),4,4,5)&&uniformWrites==before);activeProgram=3;uniformLocation=-1;check(!formationPerspectiveAvailable());check(!drawFormationPerspectiveStrip(captured.data(),4,4,5)&&uniformWrites==before);uniformLocation=7;
 std::cout<<checks;
}
'''.replace("__COMMON__", common).replace("__BASE_ROUNDED__", body(prior,"roundedQuad")).replace("__ACTUAL__", actual)
    (args.work/"geometry.cpp").write_text(fixture, encoding="utf-8")
    run([args.clang,"-std=c++17","-O2",args.work/"geometry.cpp","-o",args.work/"geometry.exe"])
    geometry_checks = int(run([args.work/"geometry.exe"]))
    java_root = root/"java/client/src/java/org/emulationstation/frontend/station"
    preference = text(java_root/"StationCarouselStylePreferences.java")
    host = args.work/"java-host"
    files = {
        "android/os/Looper.java": "package android.os; public class Looper { public static final Looper MAIN=new Looper(); public static Looper getMainLooper(){return MAIN;} }",
        "android/os/Handler.java": "package android.os; import java.util.*; public class Handler {static final List<Runnable> jobs=new ArrayList<>();public Handler(Looper l){} public boolean post(Runnable r){jobs.add(r);return true;}public static void flush(){while(!jobs.isEmpty())jobs.remove(0).run();}}",
        "android/util/Log.java": "package android.util; public class Log {public static int w(String t,String m){return 0;}}",
        "android/content/SharedPreferences.java": "package android.content; public interface SharedPreferences {int getInt(String k,int d);Editor edit(); interface Editor {Editor putInt(String k,int v);void apply();}}",
        "android/content/Context.java": "package android.content; public abstract class Context {public static final int MODE_PRIVATE=0;public Context getApplicationContext(){return this;}public abstract SharedPreferences getSharedPreferences(String n,int m);}",
        "org/emulationstation/frontend/station/StationCarouselStylePreferences.java": preference,
        "org/emulationstation/frontend/station/StyleTest.java": r'''
package org.emulationstation.frontend.station;
import android.content.*;import android.os.Handler;import java.util.*;import java.util.concurrent.*;
public class StyleTest {
 static int checks;static boolean worker;static void check(boolean v){if(!v)throw new AssertionError("check "+checks);checks++;}
 static class Saved implements SharedPreferences {int value=1,reads,writes;public int getInt(String k,int d){check(worker);reads++;return value;}public Editor edit(){return new Editor(){int next;public Editor putInt(String k,int v){next=v;return this;}public void apply(){value=next;writes++;}};}}
 static class App extends Context {Saved saved=new Saved();int opens;public SharedPreferences getSharedPreferences(String n,int m){check(worker);opens++;return saved;}}
 static class Worker implements Executor {List<Runnable> jobs=new ArrayList<>();public void execute(Runnable r){jobs.add(r);}void flush(){worker=true;try{while(!jobs.isEmpty())jobs.remove(0).run();}finally{worker=false;}}}
 static void reset()throws Exception{java.lang.reflect.Field f=StationCarouselStylePreferences.class.getDeclaredField("instance");f.setAccessible(true);f.set(null,null);Handler.flush();}
 public static void main(String[]args)throws Exception{
  for(int saved:new int[]{-2,0,1,2}){
   reset();App app=new App();app.saved.value=saved;Worker executor=new Worker();StationCarouselStylePreferences p=StationCarouselStylePreferences.get(app);
   check(p.style()==0&&!p.loaded()&&app.opens==0);check(p==StationCarouselStylePreferences.get(app));int[] notifications={0};StationCarouselStylePreferences.Listener listener=s->{notifications[0]++;};p.addListener(listener);p.addListener(listener);
   p.initialize(executor);p.initialize(executor);check(executor.jobs.size()==1);executor.flush();Handler.flush();check(p.loaded()&&p.style()==(saved==1||saved==2?saved:0));check(app.opens==1&&app.saved.reads==1&&notifications[0]==1);
   int oldWrites=app.saved.writes;p.setStyle(p.style());Handler.flush();check(app.saved.writes==oldWrites&&notifications[0]==1);p.setStyle(1-p.style());Handler.flush();check(app.saved.writes==oldWrites+1&&notifications[0]==2);int expected=p.style();
   p.removeListener(listener);p.setStyle(1-p.style());Handler.flush();check(notifications[0]==2);p.setStyle(expected);Handler.flush();reset();StationCarouselStylePreferences restored=StationCarouselStylePreferences.get(app);restored.initialize(executor);executor.flush();Handler.flush();check(restored.style()==expected);
  }
  reset();App app=new App();Worker executor=new Worker();StationCarouselStylePreferences p=StationCarouselStylePreferences.get(app);p.initialize(executor);p.setStyle(0);executor.flush();Handler.flush();check(p.style()==0&&app.saved.value==0&&app.saved.writes==1);
  reset();app=new App();executor=new Worker();p=StationCarouselStylePreferences.get(app);p.initialize(r->{throw new RejectedExecutionException();});check(!p.loaded()&&app.opens==0);p.initialize(executor);executor.flush();Handler.flush();check(p.loaded());
  p.setStyle(999);Handler.flush();check(p.style()==0);p.setStyle(2);Handler.flush();check(p.style()==2&&app.saved.value==2);reset();p=StationCarouselStylePreferences.get(app);p.initialize(executor);executor.flush();Handler.flush();check(p.style()==2);System.out.println(checks);
 }
}
''',
    }
    java_sources=[]
    for relative, source in files.items():
        path=host/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(source,encoding="utf-8");java_sources.append(path)
    classes=args.work/"host-classes";classes.mkdir(exist_ok=True)
    run([args.jdk/"javac.exe","-encoding","UTF-8","--release","8","-d",classes,*java_sources])
    preference_checks=int(run([args.jdk/"java.exe","-cp",classes,"org.emulationstation.frontend.station.StyleTest"]))
    # The production carousel has -nostdlib. Dynamic local static initialization
    # must not introduce __cxa_guard_acquire/release merely to resolve the getter.
    (args.work/"native_graphics.h").write_bytes(raw(root/"native/d0/native_graphics.h"))
    probe='extern "C" {void* dlopen(const char*,int);void* dlsym(void*,const char*);}\n#include "native_graphics.h"\nextern "C" int styleProbe(){return stationCarouselStyle();}\n'
    stubs='extern "C" {int selectedStyle=1,opens=0,resolves=0,missing=0;int readStyle(){return selectedStyle;}void* dlopen(const char*,int){opens++;return (void*)1;}void* dlsym(void*,const char*){resolves++;return missing?nullptr:(void*)readStyle;}}\n'
    host_main='''#include <cassert>
#include <iostream>
extern "C" {int styleProbe();extern int selectedStyle,opens,resolves,missing;}
int main(int argc,char**){missing=argc>1;int checks=0;for(int i=0;i<128;i++){selectedStyle=i%3;assert(styleProbe()==(missing?0:selectedStyle));checks++;assert(opens==1&&resolves==1);checks++;}std::cout<<checks;}
'''
    for name,contents in (("style-probe.cpp",probe),("style-stubs.cpp",stubs),("style-probe-main.cpp",host_main)):(args.work/name).write_text(contents,encoding="utf-8")
    run([args.clang,"-std=c++17","-O2",args.work/"style-probe.cpp",args.work/"style-stubs.cpp",args.work/"style-probe-main.cpp","-o",args.work/"style-probe.exe"])
    bridge_checks=int(run([args.work/"style-probe.exe"]))+int(run([args.work/"style-probe.exe","missing-symbol"]))
    run([args.ndk/"clang++.exe","--target=aarch64-linux-android26","-std=c++17","-shared","-fPIC","-O2","-nostdlib","-fno-exceptions","-fno-rtti","-fno-stack-protector","-fno-builtin","-Wl,--no-undefined",args.work/"style-probe.cpp",args.work/"style-stubs.cpp","-o",args.work/"style-probe.so"])
    undefined=run([args.ndk/"llvm-nm.exe","--undefined-only",args.work/"style-probe.so"])
    assert not undefined,undefined
    symbols=run([args.ndk/"llvm-nm.exe",args.work/"style-probe.so"])
    assert "__cxa_guard" not in symbols
    receipt={"version":"R123","utc":datetime.now(timezone.utc).isoformat(),"passed":True,"scope":"isolated host geometry and actual preference class; no Android/GPU/gameplay/thermal measurement", "checks":{"geometry":geometry_checks,"preferences":preference_checks,"preservationGuards":guards,"oneTimeNativeBridge":bridge_checks},"nativeBridgeLink":{"aarch64Android26":True,"nostdlib":True,"noUndefinedSymbols":True,"noCxaGuardSymbols":True,"method":"real native_graphics.h plus independent dlopen/dlsym host stubs; resolved-once and missing-symbol fallback cases"},"model":{"type":"2D affine Diagonal plus homogeneous Y perspective","diagonalDegrees":7.5,"lateralDegrees":45,"lateralFocalWidth":1.2,"noNewShaders":True,"additionalSideNeighbors":4,"neighbors":{"Reta":6,"Diagonal":6,"De lado":10},"sidePriorityBudget":13,"fit":"projected bounds fill ten forward side slots; Reta/Diagonal exact previous geometry","default":"CURRENT=0","displayChoices":["Reta","Diagonal","De lado"],"maskGate":"CELL_EFFECTS=16 and master effective mask"},"sources":{str(path.relative_to(root)).replace("\\","/"):hashlib.sha256(raw(path)).hexdigest() for path in [root/"native/d0/station_carousel_geometry.h",root/"native/d0/native_formation.h",root/"native/d0/native_system_video720.h",root/"native/d0/installed_art_r48.h",root/"native/d0/native_graphics.h",root/"native/d0/native_carousel.cpp",root/"frontend/station_frontend.cpp",root/"frontend/station_cover_plan.hpp",java_root/"StationCarouselStylePreferences.java",java_root/"StationFrontend.java",java_root/"StationGraphicsPanel.java",Path(__file__).resolve()]}}
    destination=root/"evidence/carousel-geometry-r123.json";destination.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt["checks"]))


if __name__=="__main__":main()
