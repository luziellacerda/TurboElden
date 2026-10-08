// Regression: R71 transcoded five COLEÇÃO literals to mojibake. Comparing
// collectionVideoFor(..., def.name) to that same definition missed the bug.
// These UTF-8 paths come from the independent server catalog fixture, not defs.
#include "collection_video_policy.h"
#include "system_video720_assets.h"
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>

struct Expected {const char*key;const char*path;const char*asset;};
static const Expected neo[]={
 {"neogeo-artoffighting","# 0 - ART OF FIGTHERS COLEÇÃO #","turbo-system-videos/720-collection-neogeo-artoffighting.mp4"},
 {"neogeo-metalslug","# 1 - METAL SLUG COLEÇÃO #","turbo-system-videos/720-collection-neogeo-metalslug.mp4"},
 {"neogeo-samuraishodown","# 2 - SAMURAI SHODOWN COLEÇÃO #","turbo-system-videos/720-collection-neogeo-samuraishodown.mp4"},
 {"neogeo-kof","# 3 - THE KING OF FIGTHERS COLEÇÃO #","turbo-system-videos/720-collection-neogeo-kof.mp4"},
 {"neogeo-fatalfury","# 4 - FATAL FURY COLEÇÃO #","turbo-system-videos/720-collection-neogeo-fatalfury.mp4"},
 {"neogeo-kofhacks","# 5 - HACKS #","turbo-system-videos/720-collection-neogeo-kofhacks.mp4"},
};

// Minimal data layout adapter; routing functions below are extracted verbatim
// from the actual R71 native_folders.h/native_system_video720.h by run_tests.py.
using U=std::uint64_t;using B=unsigned char;
template<class T>static T&at(void*p,U n){return *reinterpret_cast<T*>(static_cast<B*>(p)+n);}
static const char*strData(const void*p){return static_cast<const char*>(p);}
struct FolderMeta{const char*path;int kind;};
static bool folderMode=true;
static char folderPlatform[512];
static FolderMeta metas[8];static FolderMeta*folderMeta=metas;static int folderCount;
static B*items;static int systemCount;
#include "production_video_routes.h"

static unsigned checks,failures,neoFailures,otherFailures;
static void check(bool ok,const char*label,bool neoCase=false){
 ++checks;if(ok)return;++failures;if(neoCase)++neoFailures;else++otherFailures;
 std::fprintf(stderr,"FAIL %s\n",label);
}
static bool equal(const char*a,const char*b){return a&&b&&std::strcmp(a,b)==0;}
static bool maps(const char*platform,const char*path,const char*asset,bool all=false){
 const auto*v=collectionVideoFor(platform,path,all);return v&&equal(v->asset,asset)&&v->aspect==1.f;
}

int main(){
 const char*aliases[]={"Neo Geo","neogeo","neo-geo"};
 for(const auto&v:neo){
  for(const char*platform:aliases){
   check(maps(platform,v.path,v.asset),v.key,true);
   std::string nested=std::string("parent/")+v.path;
   check(maps(platform,nested.c_str(),v.asset),"neo.nested",true);
   std::string trimmed=v.path;trimmed=trimmed.substr(2,trimmed.size()-4);
   check(maps(platform,trimmed.c_str(),v.asset),"neo.trimmed",true);
   check(collectionVideoFor(platform,v.path,true)==nullptr,"neo.all uses system fallback");
  }
  check(collectionVideoFor("snes",v.path,false)==nullptr,"no cross-family SNES");
  check(collectionVideoFor("neogeocd",v.path,false)==nullptr,"CD mapping is deliberately unchanged");
 }
 const Expected snes[]={
  {"snes-bomberman","## BOMBER MAN ##","turbo-system-videos/720-collection-snes-bomberman.mp4"},
  {"snes-donkeykong","## DONKEY KONG ##","turbo-system-videos/720-collection-snes-donkeykong.mp4"},
  {"snes-finalfight","## FINAL FIGHT ##","turbo-system-videos/720-collection-snes-finalfight.mp4"},
  {"snes-megaman","## MEGA MAN ##","turbo-system-videos/720-collection-snes-megaman.mp4"},
  {"snes-mario","## SUPER MARIO ##","turbo-system-videos/720-collection-snes-mario.mp4"},
  {"snes-topgear","## TOP GEAR ##","turbo-system-videos/720-collection-snes-topgear.mp4"},
 };
 for(const char*platform:{"Super Nintendo","Super Nintendo - BR","snes","snesbr"}){
  for(const auto&v:snes)check(maps(platform,v.path,v.asset),v.key);
  const auto*ptbr=collectionVideoFor(platform,"# 1 -PT-BR #",false);
  check(ptbr&&equal(ptbr->asset,"turbo-system-videos/720-collection-snes-ptbr.mp4")&&ptbr->aspect==16.f/9.f,"SNES PT-BR unchanged");
 }
 for(const char*platform:{"Super Nintendo","snes"})
  for(const char*path:{"","## TOP GEAR ##","parent/anything"})
   check(maps(platform,path,"turbo-system-videos/720-collection-snes-all.mp4",true),"SNES all R71 unchanged");
 for(const char*platform:{"Super Nintendo - BR","snesbr","Neo Geo","Neo Geo CD","neogeocd","megadrive","SNES",""})
  check(collectionVideoFor(platform,"",true)==nullptr,"all-games scope unchanged");
 check(collectionVideoFor(nullptr,"",false)==nullptr,"null platform");
 check(collectionVideoFor("neogeo",nullptr,false)==nullptr,"null path");
 for(const char*path:{"","missing","# 5 - HACKS extra #","# 5 - hacks #","# 5 - HACKS #/child"})
  check(collectionVideoFor("neogeo",path,false)==nullptr,"exact leaf matching unchanged");

 // Execute the actual production route, including original visible-index
 // indirection and generic video fallback; no decoder or phone is instantiated.
 alignas(16) B gui[0x110]={};U visible[8]={0,1,2,3,4,5};
 at<U*>(gui,0xf8)=visible;at<U*>(gui,0x100)=visible+6;folderCount=6;
 std::memcpy(folderPlatform,"Neo Geo",sizeof("Neo Geo"));
 for(unsigned i=0;i<6;i++)metas[i]={neo[i].path,0};
 for(int i=0;i<6;i++)check(equal(video720Asset(gui,i),neo[i].asset),"route.neo.expected collection",true);
 visible[0]=4;check(equal(video720Asset(gui,0),neo[4].asset),"route.neo.filtered original index",true);visible[0]=0;
 metas[0]={"",2};check(equal(video720Asset(gui,0),"turbo-system-videos/720-neogeo.mp4"),"Neo all generic video");
 metas[0]={"not a known collection",0};check(equal(video720Asset(gui,0),"turbo-system-videos/720-neogeo.mp4"),"unknown Neo generic video");
 std::memcpy(folderPlatform,"Neo Geo CD",sizeof("Neo Geo CD"));metas[0]={neo[0].path,0};
 check(equal(video720Asset(gui,0),"turbo-system-videos/720-neogeocd.mp4"),"CD generic video unchanged");
 std::memcpy(folderPlatform,"Super Nintendo",sizeof("Super Nintendo"));metas[0]={"",2};
 check(equal(video720Asset(gui,0),"turbo-system-videos/720-collection-snes-all.mp4"),"SNES all route");
 std::memcpy(folderPlatform,"unknown",sizeof("unknown"));check(video720Asset(gui,0)==nullptr,"unknown platform fallback");
 check(video720Asset(gui,-1)==nullptr,"negative cursor");check(video720Asset(gui,6)==nullptr,"cursor past end");
 visible[0]=6;check(video720Asset(gui,0)==nullptr,"original index past folder count");visible[0]=0;
 at<U*>(gui,0xf8)=nullptr;check(video720Asset(gui,0)==nullptr,"missing visible list");at<U*>(gui,0xf8)=visible;
 // Main platform route also remains exact and independent of collection lookup.
 alignas(16) B platformItems[0xe8]={};items=platformItems;systemCount=1;visible[0]=0;at<U*>(gui,0x100)=visible+1;
 std::memcpy(platformItems+0x60,"Neo Geo",sizeof("Neo Geo"));folderMode=false;
 check(equal(video720Asset(gui,0),"turbo-system-videos/720-neogeo.mp4"),"main Neo platform unchanged");
 std::printf("{\"checks\":%u,\"failures\":%u,\"neoFailures\":%u,\"otherFailures\":%u}\n",checks,failures,neoFailures,otherFailures);
 return failures?1:0;
}
