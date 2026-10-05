#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <vector>
using U=uint64_t;using B=unsigned char;
static U micros=1000000;static bool dialog,video,systemsMode;static int target;static unsigned slept,calls;
static U count(){return micros;}static U freq(){return 1000000;}
static void delay(unsigned ms){assert(ms>0&&ms<=67);micros+=ms*1000;slept+=ms;calls++;}
static unsigned tick(){return (unsigned)(micros/1000);}
template<class T>static T fn(U addr){assert(addr==0x39e240);return (T)tick;}
template<class T>static T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
static void*dlopen(const char*,int){return (void*)1;}
static void*dlsym(void*,const char*n){if(!strcmp(n,"SDL_GetPerformanceCounter"))return (void*)count;if(!strcmp(n,"SDL_GetPerformanceFrequency"))return (void*)freq;if(!strcmp(n,"SDL_Delay"))return (void*)delay;return nullptr;}
static bool modal(void*){return dialog;}
static const char*video720Asset(void*,int){return video?"video":nullptr;}
static int __android_log_print(int,const char*,const char*,int fps,const char*){target=fps;return 0;}
#include "native_menu_power.h"
int main(){alignas(8) B ui[0x1000]={};int checks=0;
 for(bool d:{false,true})for(bool v:{false,true})for(bool sys:{false,true})for(bool load:{false,true})for(unsigned elapsed:{0u,649u,650u,5000u,60000u}){
  dialog=d;video=v;systemsMode=sys;at<int>(ui,0x370)=load?2:3;micros+=1000000;noteStoreInteraction();micros+=elapsed*1000;
  paceStoreMenu(ui);int expected=!d||elapsed<650||load?60:15;
  if(target!=expected){fprintf(stderr,"target=%d expected=%d dialog=%d elapsed=%u\n",target,expected,d,elapsed);return 2;}checks++;
 }
 dialog=false;systemsMode=true;video=true;at<int>(ui,0x370)=3;micros+=1000000;paceStoreMenu(ui);U start=micros;unsigned beginCalls=calls;
 for(int i=0;i<600;i++){micros+=2000;paceStoreMenu(ui);assert(target==60);}
 U duration=micros-start;assert(duration>=9990000&&duration<=10010000);assert(calls-beginCalls==600);
 micros+=500000;paceStoreMenu(ui);micros+=80000;paceStoreMenu(ui);assert(target==60);
 printf("PASS %d policy cases; 600 frames in %llu us with sleeping, stable foreground target and idle modal15; suspension/overrun recovery\n",checks,(unsigned long long)duration);
}
