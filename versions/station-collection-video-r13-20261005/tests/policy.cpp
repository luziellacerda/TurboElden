#include <cassert>
#include <cstdio>
#include <initializer_list>
#include <cstring>
#include "collection_video_policy.h"
int main(){int n=0;auto check=[&](bool x){assert(x);++n;};
 const char*platforms[]={"Super Nintendo","Super Nintendo - BR","snes","snesbr"};
 const char*paths[]={"## BOMBER MAN ##","## DONKEY KONG ##","## SUPER MARIO ##","## TOP GEAR ##","## 1 -PT-BR ##"};
 for(auto platform:platforms)for(int i=0;i<5;i++){
  auto*v=collectionVideoFor(platform,paths[i],false);check(v!=nullptr);check(v==&collectionVideoDefinitions[i]);check(v->aspect==(i==2?1.f:16.f/9.f));
  check(collectionVideoFor(platform,paths[i],true)==nullptr);
 }
 for(auto platform:{"MegaDrive","Nintendo 64","Neo Geo","Unknown"})for(auto path:paths)check(collectionVideoFor(platform,path,false)==nullptr);
 check(collectionVideoFor("snes","## MEGA MAN ##",false)==nullptr);check(collectionVideoFor("snes","## FINAL FIGHT ##",false)==nullptr);
 check(collectionVideoFor("snes","nested/## TOP GEAR ##",false)==&collectionVideoDefinitions[3]);
 check(collectionVideoFor("snes","## TOP GEAR ## sequel",false)==nullptr);check(collectionVideoFor(nullptr,"",false)==nullptr);
 printf("PASS %d exact collection video and source aspect checks\n",n);
}
