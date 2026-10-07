#include "collection_video_policy.h"
#include <cassert>
#include <cstring>
#include <cstdio>
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
 {const auto*v=collectionVideoFor("snes","## SUPER MARIO ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-mario.mp4")==0);}
 {const auto*v=collectionVideoFor("snes","parent/## SUPER MARIO ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-mario.mp4")==0);}
 assert(!collectionVideoFor("neogeo","## SUPER MARIO ##",false));
 assert(!collectionVideoFor("megadrive","## SUPER MARIO ##",false));
 {const auto*v=collectionVideoFor("snes","## TOP GEAR ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-topgear.mp4")==0);}
 {const auto*v=collectionVideoFor("snes","parent/## TOP GEAR ##",false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,"turbo-system-videos/720-collection-snes-topgear.mp4")==0);}
 assert(!collectionVideoFor("neogeo","## TOP GEAR ##",false));
 assert(!collectionVideoFor("megadrive","## TOP GEAR ##",false));
 assert(!collectionVideoFor(nullptr,"",false));
 assert(!collectionVideoFor("snes",nullptr,false));
 assert(!collectionVideoFor("snes","SUPER MARIO WORLD",false));
 assert(!collectionVideoFor("snes","TOP GEAR 2",false));
 assert(!collectionVideoFor("neogeocd","# 5 - HACKS #",false));
 std::puts("PASS collection video routes");
 return 0;
}
