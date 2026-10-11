"""Actual native slot/flow/priority bodies, isolated from phone/GPU/catalog assets."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
from datetime import datetime, timezone

def raw(path):
    return Path("\\\\?\\" + str(path.resolve())).read_bytes()

def text(path):
    return raw(path).decode("utf-8").replace("\r\n", "\n")

def body(source, name):
    match=re.search(r"static [^\n;]*\b"+re.escape(name)+r"\([^\n]*?\)\{",source)
    assert match,name
    start=source.index("{",match.start());end=start+1;depth=1
    while depth:
        depth+=(source[end]=="{")-(source[end]=="}");end+=1
    return source[match.start():end]

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--work",type=Path,required=True)
    parser.add_argument("--clang",type=Path,default=Path(r"C:\Program Files\LLVM\bin\clang++.exe"))
    args=parser.parse_args();args.work.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parent.parent;base=root.parent/"station-theme-room-download-r122-20261011"
    formation=text(root/"native/d0/native_formation.h");prior=text(base/"native/d0/native_formation.h")
    native=text(root/"native/d0/native_carousel.cpp");oldnative=text(base/"native/d0/native_carousel.cpp")
    # Only the shared pure-header include and the visible-priority method may change here.
    normalized=native.replace('#include "station_carousel_geometry.h"\n','')
    normalized=normalized.replace(body(native,"prioritizeHook"),body(oldnative,"prioritizeHook"))
    assert normalized==oldnative
    assert "distance<0?-1:1" in body(formation,"coverFormationHook")
    assert "distance>stationCarouselGeometry::neighborCount(style,stationGraphicsEnabled(16))+.6f" in formation
    (args.work/"station_carousel_geometry.h").write_bytes(raw(root/"native/d0/station_carousel_geometry.h"))
    fixture=r'''
#include <cassert>
#include <cmath>
#include <cstring>
#include <iostream>
#include <vector>
#include "station_carousel_geometry.h"
using U=unsigned long long;using B=unsigned char;using V=void(*)(void*);
template<class T>static T&at(void*p,U offset){return *reinterpret_cast<T*>((B*)p+offset);}
struct CoverRect {float x,y,w,h;int index;bool allGames=false;stationCarouselGeometry::Transform projection{};};
struct NativeVector {B*begin;B*end;B*capacity;};
static bool systemsMode=false;static int selectedStyle=0;static unsigned effects=127;
static int stationCarouselStyle(){return selectedStyle;}
static bool stationGraphicsEnabled(unsigned bit){return (effects&bit)!=0;}
static CoverRect painted[20];static int paintedCount;static B gui[0x400],catalog[0x140];
static std::vector<U> visible,priority;static int flowCalls,priorityCalls,layerCalls,videoCalls;
static void drawSystemInfoLayer(void*){layerCalls++;}
static void drawSystemVideo720(void*){videoCalls++;}
static void*catalogGetter(){return catalog;}
static void publishPriority(void*,const NativeVector&v){priority.assign((U*)v.begin,(U*)v.end);at<U>(catalog,0x100)=(U)priority.data();at<U>(catalog,0x108)=(U)(priority.data()+priority.size());priorityCalls++;}
static void coverFormationHook(void*,U,float);
// Preserved ELF traversal: descending offsets, negative then positive, hero once.
// The boundary fixture models the sixth offset with collapse displacement zero;
// it does not reproduce the native collapse timer/trajectory.
static void originalFlow(void*p){
 flowCalls++;int anchor=(int)at<float>(p,0xf4),last=at<int>(p,0x364)<0?5:6;
 for(int offset=last;offset>=0;offset--){
  int negative=anchor-offset,positive=anchor+offset;
  if(negative>=0&&(U)negative<visible.size())coverFormationHook(p,visible[negative],negative-at<float>(p,0xf4));
  if(offset&&positive>=0&&(U)positive<visible.size())coverFormationHook(p,visible[positive],positive-at<float>(p,0xf4));
 }
}
template<class T>static T fn(U a){if(a==0x22a154)return reinterpret_cast<T>(originalFlow);if(a==0x1887dc)return reinterpret_cast<T>(catalogGetter);return reinterpret_cast<T>(publishPriority);}
__SLOT__
namespace baseline {__BASE_SLOT__}
static void coverFormationHook(void*p,U index,float distance){
 int style=stationCarouselStyle(),neighbors=stationCarouselGeometry::neighborCount(style,stationGraphicsEnabled(16));
 if(distance < -1.01f || distance > neighbors+.6f)return;
 int position=-1;for(size_t i=0;i<visible.size();i++)if(visible[i]==index){position=(int)i;break;}
 auto r=coverSlot(p,distance,style);r.index=position;
 r.projection=stationCarouselGeometry::make(r.x,r.y,r.w,r.h,position,at<int>(p,0xf0),style,stationGraphicsEnabled(16),distance<0?-1:1);
 if(position>=0&&paintedCount<20&&r.x+r.w>0&&r.x<at<float>(p,0x54))painted[paintedCount++]=r;
}
__FLOW__
__PRIORITY__
static float cornerRadius(float,float,bool){return 0;}
__HIT__
static long long checks,cases;
static void check(bool v){assert(v);checks++;}
static void configure(int size,int selected,float animated,float width=960,float height=432){
 std::memset(gui,0,sizeof(gui));visible.clear();for(int i=0;i<size;i++)visible.push_back(200+(U)i);
 at<float>(gui,0x54)=width;at<float>(gui,0x58)=height;at<int>(gui,0xf0)=selected;at<float>(gui,0xf4)=animated;
 at<int>(gui,0x364)=-1;
 at<U>(gui,0xf8)=(U)visible.data();at<U>(gui,0x100)=(U)(visible.data()+visible.size());
 at<U>(catalog,0x88)=0x100000;at<U>(catalog,0x90)=0x100000+(200+size)*0xe8;
}
static void sameRect(const CoverRect&a,const CoverRect&b){check(a.x==b.x&&a.y==b.y&&a.w==b.w&&a.h==b.h);}
int main(){
 for(bool system:{false,true})for(float width:{640.f,960.f,1280.f,1920.f})for(float aspect:{1.5f,2.f,2.222222f,2.5f}){
  systemsMode=system;configure(23,17,17,width,width/aspect);
  for(int style:{0,1,2})for(bool enabled:{false,true}){
   selectedStyle=style;effects=enabled?127:111;
   if(style!=2||!enabled)for(float distance:{-1.f,0.f,.2f,.8f,1.f,2.f,5.f,6.f,6.6f}){sameRect(coverSlot(gui,distance),baseline::coverSlot(gui,distance));cases++;}
   else {
    sameRect(coverSlot(gui,0),baseline::coverSlot(gui,0));
    float previousRight=-1;
    for(int offset=1;offset<=10;offset++){
     auto r=coverSlot(gui,(float)offset);int position=(17+offset)%23;
     auto t=stationCarouselGeometry::make(r.x,r.y,r.w,r.h,position,17,2,true,1);auto b=t.bounds(r.x,r.y,r.w,r.h);
     check(t.depth<0);check(b.w>0&&b.h>0);check(b.x>=previousRight-.003f);check(b.x+b.w<=width*.965f+.004f);
     float stripX=system?width*.365f:baseline::coverSlot(gui,0).x+baseline::coverSlot(gui,0).w+width*.022f;
     if(offset==1)check(std::fabs(b.x-stripX)<.004f);
     if(offset==10)check(std::fabs(b.x+b.w-width*.965f)<.004f);
     previousRight=b.x+b.w;
     auto center=t.map(r.x+r.w*.5f,r.y+r.h*.5f),back=t.inverse(center.x,center.y);check(std::fabs(back.x-r.x-r.w*.5f)<.004f);
     cases++;
    }
   }
  }
 }
 systemsMode=false;
 for(int size:{1,2,3,5,6,7,10,11,12,23,64,100})for(int selected=0;selected<size;selected++)for(int style:{0,1,2})for(unsigned mask:{127u,111u,95u,0u})for(float fraction:{0.f,.25f,.75f})for(bool collapseBoundary:{false,true}){
  selectedStyle=style;effects=mask;float animated=selected+fraction;if(animated>=size)animated=selected;
  configure(size,selected,animated);int beforeFlow=flowCalls,beforeLayer=layerCalls,beforeVideo=videoCalls;
  at<int>(gui,0x364)=collapseBoundary?0:-1;
  flowFormationHook(gui);check(flowCalls==beforeFlow+1&&layerCalls==beforeLayer+1&&videoCalls==beforeVideo+1);check(at<float>(gui,0xf4)==animated);
  int neighbors=stationCarouselGeometry::neighborCount(style,(mask&16u)!=0);
  check(paintedCount<=neighbors+3);std::vector<bool>seen(size,false);
  for(int i=0;i<paintedCount;i++){auto&r=painted[i];check(r.index>=0&&r.index<size);
   // Old Reta/Diagonal can repaint offset six at this native collapse boundary.
   if(neighbors==10||!collapseBoundary)check(!seen[r.index]);seen[r.index]=true;
   if(r.index!=selected&&style==2&&(mask&16u))check(r.projection.depth<0);
   if(neighbors==10&&(fraction==0||!(mask&32u))){auto center=r.projection.map(r.x+r.w*.5f,r.y+r.h*.5f);check(hitCover(center.x,center.y)==r.index);}
  }
  if((fraction==0||!(mask&32u))&&neighbors==10){int expected=size<11?size:11;check(paintedCount==expected);for(int offset=0;offset<expected;offset++)check(seen[(selected+offset)%size]);}
  prioritizeHook(gui);check(priority.size()<=(size_t)(neighbors+3));check(!priority.empty()&&priority[0]==visible[selected]);
  std::vector<bool>prioritySeen(size,false);for(U index:priority){int position=(int)(index-200);check(position>=0&&position<size&&!prioritySeen[position]);prioritySeen[position]=true;}
  if(neighbors==10){int anchor=(mask&32u)?(int)animated:selected;for(int offset=0;offset<=10;offset++)check(prioritySeen[(anchor+offset)%size]);}
  int before=priorityCalls;prioritizeHook(gui);check(priorityCalls==before);cases++;
 }
 // Same short indices still publish once on a mode/budget transition.
 configure(3,0,0);selectedStyle=0;effects=127;prioritizeHook(gui);int before=priorityCalls;
 selectedStyle=2;prioritizeHook(gui);check(priorityCalls==before+1);before=priorityCalls;effects=111;prioritizeHook(gui);check(priorityCalls==before+1);
 selectedStyle=2;effects=127;configure(23,17,17);flowFormationHook(gui);check(paintedCount==11);
 const int expected[11]={17,18,19,20,21,22,0,1,2,3,4};for(int position:expected){bool found=false;for(int i=0;i<paintedCount;i++)if(painted[i].index==position)found=true;check(found);}
 std::cout<<cases<<" "<<checks;
}
'''
    fixture=fixture.replace("__SLOT__",body(formation,"coverSlot")).replace("__BASE_SLOT__",body(prior,"coverSlot"))
    fixture=fixture.replace("__FLOW__",body(formation,"flowFormationHook")).replace("__PRIORITY__",body(native,"prioritizeHook"))
    fixture=fixture.replace("__HIT__",body(formation,"hitCover"))
    source=args.work/"ten-covers.cpp";source.write_text(fixture,encoding="utf-8")
    exe=args.work/"ten-covers.exe"
    for command in ([args.clang,"-std=c++17","-O2",source,"-o",exe],[exe]):
        result=subprocess.run([str(x) for x in command],capture_output=True,text=True,encoding="utf-8")
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    cases,checks=map(int,result.stdout.split())
    receipt={"version":"R123","utc":datetime.now(timezone.utc).isoformat(),"passed":True,"scope":"isolated host actual native coverSlot/flowFormationHook/prioritizeHook/hitCover; original renderer stub follows preserved ELF descending offsets five or six, negative then positive, hero once; sixth-offset boundary uses collapse displacement zero, not native collapse trajectory; no real phone/GPU/thermal measurement","cases":cases,"checks":checks,"visible":{"sideNeighbors":10,"flatDiagonalNeighbors":6,"example17of23Content":[17,18,19,20,21,22,0,1,2,3,4],"exampleOrder":"logical forward display slots; does not assert native paint order","wrap":"De lado forward display only, each catalog position at most once","sideBudget":13,"otherBudget":9},"preservation":{"defaultSlotFieldsExactR122":True,"originalFlowCalledOnce":True,"animationRestoredAfterSnap":True,"legacySixthOffsetRepaintAtCollapseBoundaryPreserved":True,"wrappedCenterPickingActualHitCover":True,"priorityChangesOnlyWhenIndicesOrBudgetOrCatalogChange":True,"noNewShaderDecoderQueueWorkerOrFrameLoop":True},"sources":{str(path.relative_to(root)).replace("\\","/"):hashlib.sha256(raw(path)).hexdigest() for path in [root/"native/d0/native_carousel.cpp",root/"native/d0/native_formation.h",root/"native/d0/station_carousel_geometry.h",Path(__file__).resolve()]}}
    (root/"evidence/carousel-ten-covers-r123.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":cases,"checks":checks}))

if __name__=="__main__":main()
