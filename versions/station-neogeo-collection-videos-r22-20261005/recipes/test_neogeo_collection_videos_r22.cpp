#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>
#include <string>
#include "collection_video_policy.h"

static int checks;
static void require(bool pass,const char*what){++checks;if(!pass){std::fprintf(stderr,"FAIL %s\n",what);std::exit(1);}}
int main(){
 require(sizeof(collectionVideoDefinitions)/sizeof(collectionVideoDefinitions[0])==8,"eight assets");
 const char*snes[]={"Super Nintendo","Super Nintendo - BR","snes","snesbr"};
 const char*neo[]={"Neo Geo","neogeo","neo-geo"};
 const char*prefix[]={"","games/","colecoes/sub/"};
 const char*before[]={"","## "," #"};
 const char*after[]={""," ##","# "};
 for(int index=0;index<8;index++){
  const auto&v=collectionVideoDefinitions[index];
  for(auto pre:prefix)for(auto left:before)for(auto right:after){
   std::string path=std::string(pre)+left+v.name+right;
   for(auto platform:snes)require(collectionVideoFor(platform,path.c_str(),false)==(index<5?&v:nullptr),"SNES isolated");
   for(auto platform:neo)require(collectionVideoFor(platform,path.c_str(),false)==(index>=5?&v:nullptr),"Neo Geo isolated");
   for(auto platform:{"Neo Geo CD","neogeocd","MegaDrive","naomi","", "Neo Geo - Extra"})
    require(!collectionVideoFor(platform,path.c_str(),false),"other platforms unaffected");
   for(auto platform:{"Neo Geo","Super Nintendo"})require(!collectionVideoFor(platform,path.c_str(),true),"All games uses platform video");
  }
  for(auto suffix:{" 2"," EXTRA","/child","BR"}){
   std::string bad=std::string(v.name)+suffix;
   require(!collectionVideoFor(index<5?"Super Nintendo":"Neo Geo",bad.c_str(),false),"no partial or parent matches");
  }
  require(!collectionVideoFor(nullptr,v.name,false),"null platform");
 }
 for(auto platform:{"Neo Geo","Super Nintendo","neogeo","snes"}){
  require(!collectionVideoFor(platform,nullptr,false),"null path");
  for(auto path:{"","/","#","###  ","Unknown","FATAL","SLUG","SAMURAI"})
   require(!collectionVideoFor(platform,path,false),"unknown leaves unchanged");
 }
 std::printf("%d collection video routing checks passed\n",checks);
}
