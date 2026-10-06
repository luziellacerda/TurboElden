#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
using U=uintptr_t;
template<class T> T& at(void*p,U offset){return *reinterpret_cast<T*>(static_cast<unsigned char*>(p)+offset);}
static bool skinTop;
static void*skinTopOwner;
static void*gui;
static bool modal(void*){return false;}
static unsigned ticks(){return 1234;}
static int fallbackCalls,drawCalls,cloudCalls,rectCalls;
static void* fallbackArg;
static void fallback(void*p,float,float,float,unsigned){++fallbackCalls;fallbackArg=p;}
struct R {float x,y,w,h;};
static R lastDraw;
static constexpr float stationLottie_chatbot_height=100,stationLottie_chatbot_width=120;
static void drawStationLottie(int id,unsigned frame,R r){assert(id==2&&frame<86);lastDraw=r;++drawCalls;}
static unsigned stationSkyTop(){return 0x030805ff;}
static unsigned stationSkyBottom(){return 0x010201ff;}
static R coverSlot(void*,int){return {30,10,300,500};}
struct RectCall {float x,y,w,h;unsigned a,b;bool horizontal;};
static RectCall rects[8];
static void rect(float x,float y,float w,float h,unsigned a,unsigned b,bool hor,int src,int dst){assert(src==4&&dst==5);rects[rectCalls++]={x,y,w,h,a,b,hor};}
static void drawNativeClouds(float,float,float){++cloudCalls;}
template<class F> F fn(U address){
 if(address==0x39e240)return reinterpret_cast<F>(&ticks);
 if(address==0x221854)return reinterpret_cast<F>(&fallback);
 if(address==0x2e2c38)return reinterpret_cast<F>(&rect);
 assert(false);return nullptr;
}
#include "native_lottie_gear.h"
#include "native_space.h"
#include "station_rating_animation.h"

int main(){
 alignas(16) unsigned char owner[0x1500]={};
 at<float>(owner,0x58)=1080;
 skinTop=true;skinTopOwner=owner;
 // Exact crash reproducer: the hook's incoming x0 is null. Draw with real owner.
 drawSettingsLottieHook(nullptr,100,60,20,0xffffffff);
 assert(drawCalls==1&&fallbackCalls==0);
 float expected=1080*.059f*.34f*6.54f;
 assert(std::fabs(lastDraw.w-expected)<.001f);
 assert(std::fabs(lastDraw.x-(100-expected*.5f))<.001f);
 // Garbage x0 is equally irrelevant; no read through it is permitted.
 drawSettingsLottieHook(reinterpret_cast<void*>(uintptr_t(1)),100,60,20,0xffffffff);
 assert(drawCalls==2);
 skinTopOwner=nullptr;
 drawSettingsLottieHook(nullptr,100,60,20,0xffffffff);
 assert(drawCalls==2&&fallbackCalls==1&&fallbackArg==nullptr);
 skinTop=false;skinTopOwner=owner;
 drawSettingsLottieHook(owner,100,60,20,0xffffffff);
 assert(drawCalls==2&&fallbackCalls==2&&fallbackArg==owner);
 // No gradient before a GUI exists or during any loading/intro phase.
 gui=nullptr;rectCalls=cloudCalls=0;drawNativeSpace(2340,1080);
 assert(rectCalls==1&&cloudCalls==1&&!rects[0].horizontal);
 gui=owner;
 for(int phase=0;phase<=4;++phase){
  at<int>(owner,0x370)=phase;rectCalls=cloudCalls=0;drawNativeSpace(2340,1080);
  assert(cloudCalls==1&&rectCalls==(phase==3?3:1));
  if(phase==3){
   assert(!rects[1].horizontal&&!rects[2].horizontal);
   assert(rects[1].a==0x000000cc&&rects[1].b==0x000000b3);
   assert(rects[2].a==0x000000b3&&rects[2].b==0);
   assert(rects[1].x==0&&rects[1].w==330&&rects[2].x==330&&rects[2].w==2010);
  }
 }
 rectCalls=cloudCalls=0;drawNativeSpace(0,1080);drawNativeSpace(2340,0);
 assert(rectCalls==0&&cloudCalls==0);
 // Match native assembly: bool=true assigns B to bottom-left and A to top-right.
 // false must keep each vertical edge uniform, blending continuously along x.
 auto alphaAt=[](const RectCall&r,float x,float y){
  float fraction=r.horizontal?(y-r.y)/r.h:(x-r.x)/r.w;
  return (r.a&255)*(1-fraction)+(r.b&255)*fraction;
 };
 at<int>(owner,0x370)=3;rectCalls=0;drawNativeSpace(2340,1080);
 assert(alphaAt(rects[1],0,0)==204);
 assert(alphaAt(rects[1],330,0)==179);
 assert(alphaAt(rects[2],330,0)==179);
 assert(alphaAt(rects[2],2340,0)==0);
 for(int y=0;y<=1080;y+=120){
  assert(std::fabs(alphaAt(rects[1],330,y)-alphaAt(rects[2],330,y))<.001f);
  assert(std::fabs(alphaAt(rects[1],180,y)-alphaAt(rects[1],180,0))<.001f);
  float prior=205;
  for(int x=0;x<=2340;++x){float a=alphaAt(rects[x<=330?1:2],(float)x,(float)y);assert(a<=prior+.0001f);prior=a;}
 }
 // Original Favourite timing, continued well past the first animation cycle.
 for(unsigned time=0;time<30000;++time)assert(stationRatingLoopFrame(time)==(time*60u/1000u)%80u);
 assert(stationRatingLoopFrame(0xffffffffu)<80);
 puts("PASS: original crash regression, startup gates, correct native gradient axis, continuous 80/70/0 opacity without seam, and Favourite loops at original 60fps.");
}
