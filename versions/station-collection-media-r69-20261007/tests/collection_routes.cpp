#include "collection_video_policy.h"
#include <cassert>
#include <cstdio>
#include <cstring>
int main(){
 const char* snes[]={"Super Nintendo","Super Nintendo - BR","snes","snesbr"};
 const char* neo[]={"Neo Geo","neogeo","neo-geo"};
 assert(sizeof(collectionVideoDefinitions)/sizeof(collectionVideoDefinitions[0])==13);
 for(const auto&def:collectionVideoDefinitions){
  const char*const*aliases=def.family==0?snes:neo;int count=def.family==0?4:3;
  for(int i=0;i<count;i++){
   const auto*actual=collectionVideoFor(aliases[i],def.name,false);
   assert(actual==&def&&std::strcmp(actual->asset,def.asset)==0);
   assert(!collectionVideoFor(aliases[i],def.name,true));
  }
 }
 {const auto*v=collectionVideoFor("snes","## FINAL FIGHT ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-finalfight.mp4")==0);}
 {const auto*v=collectionVideoFor("snes","parent/## FINAL FIGHT ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-finalfight.mp4")==0);}
 assert(!collectionVideoFor("neogeo","## FINAL FIGHT ##",false));
 assert(!collectionVideoFor("megadrive","## FINAL FIGHT ##",false));
 {const auto*v=collectionVideoFor("snes","## MEGA MAN ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-megaman.mp4")==0);}
 {const auto*v=collectionVideoFor("snes","parent/## MEGA MAN ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-megaman.mp4")==0);}
 assert(!collectionVideoFor("neogeo","## MEGA MAN ##",false));
 assert(!collectionVideoFor("megadrive","## MEGA MAN ##",false));
 {const auto*v=collectionVideoFor("snes","## TOP GEAR ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-topgear.mp4")==0);}
 {const auto*v=collectionVideoFor("snes","parent/## TOP GEAR ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-topgear.mp4")==0);}
 assert(!collectionVideoFor("neogeo","## TOP GEAR ##",false));
 assert(!collectionVideoFor("megadrive","## TOP GEAR ##",false));
 assert(!collectionVideoFor(nullptr,"",false));
 assert(!collectionVideoFor("snes",nullptr,false));
 assert(!collectionVideoFor("snes","MEGA MAN X",false));
 assert(!collectionVideoFor("snes","FINAL FIGHT 2",false));
 assert(!collectionVideoFor("snes","TOP GEAR 2",false));
 assert(!collectionVideoFor("neogeocd","# 5 - HACKS #",false));
 std::puts("PASS collection routes: 13 definitions, platform aliases, nested folders and negative cases");
 return 0;
}
