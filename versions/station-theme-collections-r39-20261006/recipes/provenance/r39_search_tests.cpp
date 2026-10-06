#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <string>
#include <vector>
#include <chrono>
using U=uintptr_t;using B=unsigned char;
template<class T>T&at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
static const char*strData(const void*p){auto*b=(const B*)p;return b[0]&1?*(const char*const*)(b+16):(const char*)b+1;}
static void strAssign(void*p,const char*s){if(at<B>(p,0)&1)free(at<void*>(p,16));memset(p,0,24);size_t n=strlen(s);if(n<=22){at<B>(p,0)=(B)(n*2);memcpy((B*)p+1,s,n+1);}else{at<B>(p,0)=1;at<U>(p,8)=n;at<void*>(p,16)=malloc(n+1);memcpy(at<void*>(p,16),s,n+1);}}
static B ui[0x2100],catalog[0x138];static std::vector<B> records;static std::vector<U> list;static std::string token;static unsigned closes=0,rebuilds=0;static bool cleared;
static void rebuild();
static void query(const char*q){if(!strcmp(q,strData(ui+0x650)))return;strAssign(ui+0x650,q);token=q;at<U>(ui,0x688)=at<U>(ui,0x680);at<int>(ui,0xf0)=0;rebuild();}
static void closeSearch(void*,bool clear){closes++;cleared=clear;at<B>(ui,0x648)=at<B>(ui,0x598)=0;if(clear)query("");}
template<class T>T fn(U addr){assert(addr==0x219570);return (T)closeSearch;}
#include "native_search_state.h"
#include "station_search_actions.h"
struct StationInfoRect{float x,y,w,h;};
#include "station_root_label.h"
static unsigned checks=0;
static void check(bool b){checks++;if(!b){printf("Failed check %u\n",checks);abort();}}
static void rebuild(){
 if(stationEmptySearchCache.reuse(ui,catalog))return;
 rebuilds++;list.clear();
 for(U i=0;i<records.size()/0xe8;i++){
  const char*name=strData(records.data()+i*0xe8+0x18);
  if(token.empty()||std::string(name).find(token)!=std::string::npos)list.push_back(i);
 }
 at<U*>(ui,0xf8)=list.data();at<U*>(ui,0x100)=list.data()+list.size();
 at<int>(ui,0x110)=at<int>(catalog,0xa8);at<B>(ui,0x114)=at<B>(ui,0x148);
 strAssign(ui+0x118,strData(ui+0x150));strAssign(ui+0x130,strData(ui+0x650));
 stationSearchScope(ui,catalog);stationEmptySearchCache.remember(ui,catalog);
}
static U size(){return (at<U>(ui,0x100)-at<U>(ui,0xf8))/sizeof(U);}
static void scope(const char*platform){clearSearchForNavigation(ui);strAssign(ui+0x150,platform);stationEmptySearchCache.invalidate();rebuild();}
int main(){
 records.resize(40000*0xe8);list.reserve(40000);at<int>(ui,0x370)=2;
 at<B*>(catalog,0x88)=records.data();at<B*>(catalog,0x90)=records.data()+records.size();at<int>(catalog,0xa8)=14;
 for(U i=0;i<40000;i++){B*r=records.data()+i*0xe8;strAssign(r+0x18,i%3==0?"Mario":i%3==1?"Sonic":"Tradução Especial");strAssign(r+0x60,i%2?"MegaDrive":"Super Nintendo");r[0xa8]=i%5==0?1:0;}
 scope("Super Nintendo");check(size()==20000);
 query("zzzz-not-found");check(size()==0&&stationSearchEmpty(ui));unsigned before=rebuilds;
 auto start=std::chrono::steady_clock::now();for(int i=0;i<10000;i++){rebuild();check(size()==0);}check(rebuilds==before);
 auto elapsed=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
 query("Mario");check(size()==6667&&!stationSearchEmpty(ui));
 at<B>(ui,0x648)=1;check(stationSearchCanBack(ui));stationSearchBack(ui);check(!at<B>(ui,0x648)&&!cleared&&size()==6667);
 stationSearchBack(ui);check(cleared&&size()==20000&&!stationSearchCanBack(ui));
 query("Sonic");scope("MegaDrive");check(token.empty()&&!*strData(ui+0x650)&&size()==20000);
 // Demonstrate the previous direct-string clear leaves an active filter.
 query("zzzz-not-found");strAssign(ui+0x650,"");stationEmptySearchCache.invalidate();rebuild();check(size()==0&&!token.empty());
 query("Mario");clearSearchForNavigation(ui);check(token.empty()&&size()==20000);
 // Same state machine is used by the platform/collection presentation catalogs.
 for(int pass=0;pass<100;pass++){
  scope("");check(size()==40000);query("zzzz-not-found");check(stationSearchEmpty(ui));
  at<B>(ui,0x648)=1;at<B>(ui,0x598)=pass%2;stationSearchBack(ui);check(!at<B>(ui,0x648)&&!at<B>(ui,0x598));stationSearchBack(ui);check(size()==40000);
  query("Tradução");check(size()==13333);scope("Super Nintendo");check(size()==20000);
 }
 at<B>(ui,0x148)=1;query("Mario");check(size()==1334);for(U*it=at<U*>(ui,0xf8);it<at<U*>(ui,0x100);it++){check(records[*it*0xe8+0xa8]==1);check(!strcmp(strData(records.data()+*it*0xe8+0x60),"Super Nintendo"));}
 query("zzzz");check(size()==0);before=rebuilds;rebuild();check(rebuilds==before);
 at<int>(catalog,0xa8)++;rebuild();check(rebuilds==before+1);
 at<B>(ui,0x148)=0;rebuild();check(rebuilds==before+2);
 strAssign(ui+0x150,"MegaDrive");rebuild();check(rebuilds==before+3);
 stationEmptySearchCache.invalidate();rebuild();check(rebuilds==before+4);
 at<B>(ui,0x2050)=1;check(!stationSearchEmpty(ui)&&!stationSearchCanBack(ui));at<B>(ui,0x2050)=0;check(stationSearchEmpty(ui));
 for(float w:{640.f,1280.f,1920.f,2340.f})for(float h:{360.f,720.f,1080.f})for(bool editing:{false,true})for(int a:{1,2}){
  auto r=stationSearchActionBox(w,h,editing,a);check(r.x>=0&&r.y>=0&&r.x+r.w<=w&&r.y+r.h<=h);
  StationSearchGesture g;float x=r.x+r.w/2,y=r.y+r.h/2;
  check(g.touch(0,7,x,y,w,h,editing,true)==0);check(g.touch(2,8,x,y,w,h,editing,true)==0);check(g.touch(2,7,x,y,w,h,editing,true)==a);
  check(g.touch(0,7,x,y,w,h,editing,true)==0);check(g.touch(1,7,x+h*.04f,y,w,h,editing,true)==0);check(g.touch(2,7,x,y,w,h,editing,true)==-1);
  check(g.touch(0,7,x,y,w,h,editing,true)==0);check(g.touch(2,7,x,y,w,h,editing,false)==-1);
  check(g.touch(0,7,0,0,w,h,editing,true)==-1);
 }
 for(float width:{100.f,200.f,500.f})for(float label:{10.f,80.f,99.f,150.f})for(float spaces:{3.f,15.f,40.f}){
  auto r=stationMainButtonText({10,20,width,40},label,spaces);check(r.x>=10&&r.x+r.w==10+width);float expected=(width-label)*.5f-spaces;if(expected<0)expected=0;check(r.x==10+expected);
 }
 printf("%u search/Back/scope/cache/touch/root-label checks passed; 40,000 entries, 10,000 unchanged empty frames: %.3f ms on host (not Android).\n",checks,elapsed);
}
