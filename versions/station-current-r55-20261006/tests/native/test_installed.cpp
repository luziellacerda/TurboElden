#include <cassert>
#include <cstdio>
#include <cstdint>
#include <cmath>
using U=uintptr_t;using B=unsigned char;
template<class T>T&at(void*p,U o){return *reinterpret_cast<T*>((B*)p+o);}
struct StationInfoRect{float x,y,w,h;};using CoverRect=StationInfoRect;
struct NativeMatrix{float v[16];};static NativeMatrix formationMatrix;
static bool systemsMode,folderMode,modalOpen;static bool modal(void*){return modalOpen;}
static B catalog[0x100],items[0xe8*3];static int draws;static StationInfoRect last;
static void*getCatalog(){return catalog;}static void matrix(const void*){}static void texture(unsigned){}
template<class F>F fn(U a){if(a==0x1887dc)return reinterpret_cast<F>(getCatalog);if(a==0x2e5640)return reinterpret_cast<F>(matrix);if(a==0x2e52e8)return reinterpret_cast<F>(texture);assert(false);return nullptr;}
#include "native_installed_tag.h"
static void drawInstalledArtwork(StationInfoRect r){last=r;draws++;}
static bool eq(float a,float b){return std::fabs(a-b)<.01f;}
int main(){
 B gui[0x400]={};at<int>(gui,0x370)=3;at<B*>(catalog,0x88)=items;at<B*>(catalog,0x90)=items+sizeof(items);items[0xa8]=1;items[0xe8*2+0xa8]=1;
 drawInstalledCover(gui,0,{100,120,500,700});assert(draws==1);
 assert(eq(last.w,340)&&eq(last.x+last.w*stationRibbonCreaseX,100)&&eq(last.y+last.h*stationRibbonCreaseY,120)&&eq(last.w,last.h));
 drawInstalledCover(gui,2,{700,120,160,225});assert(draws==2&&eq(last.w,108.8f)&&eq(last.h,108.8f));
 for(int i: {1,3})drawInstalledCover(gui,i,{100,120,500,700});assert(draws==2);
 systemsMode=true;drawInstalledCover(gui,0,{100,120,500,700});systemsMode=false;
 folderMode=true;drawInstalledCover(gui,0,{100,120,500,700});folderMode=false;
 modalOpen=true;drawInstalledCover(gui,0,{100,120,500,700});modalOpen=false;
 at<int>(gui,0x370)=1;drawInstalledCover(gui,0,{100,120,500,700});assert(draws==2);
 at<int>(gui,0x370)=3;drawInstalledCover(gui,0,{100,120,0,700});assert(draws==2);
 int checks=0;
 for(int width=24;width<=900;width+=3)for(int y=32;y<=500;y+=13){
  float x=width*.3f,h=width/0.72f;
  auto p=stationPlaceRibbon(x,y,width,h);
  assert(eq(p.w,p.h)&&eq(p.w,width*.68f));
  assert(eq(p.x+p.w*stationRibbonCreaseX,x)&&eq(p.y+p.h*stationRibbonCreaseY,y));
  // Entire return lies outside the image; front face starts at the exact edge.
  assert(p.x<x&&p.y<y);checks++;
 }
 assert(stationPlaceRibbon(1,1,-1,100).w==0&&stationPlaceRibbon(1,1,100,0).w==0);
 std::printf("PASS %d ribbon placement cases\n",checks);
 puts("PASS R55: per-item flag, all visibility gates, R50 size restored, R51 integrated lettering, integrated lettering, no text component/layout/rotation per cover.");
}
