#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <string>
#include <vector>
#include <map>
#include "station_collections.hpp"
using U=uintptr_t;using B=unsigned char;using V=void(*)(void*);
template<class T>T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
static bool systemsMode=true;static int lastSystem;static unsigned coverCheckAt;static bool coverCheckPending;
struct Sys {const char*key;const char*path;};static Sys systems[]={{"Super Nintendo","snes.png"}};static int NSYSTEMS=1;
static B realCatalog[0x138],ui[0x2100];static U visible[4096];static unsigned revision=1;
struct Item {std::string id,platform,coverPath;};static std::vector<Item> realItems;static std::map<std::string,std::string> paths;
static const char*strData(const void*p){auto*b=(const B*)p;return b[0]&1?*(const char*const*)(b+16):(const char*)b+1;}
static void strAssign(void*p,const char*s){if(at<B>(p,0)&1)free(at<void*>(p,16));memset(p,0,24);size_t n=strlen(s);if(n<=22){at<B>(p,0)=(B)(n*2);memcpy((B*)p+1,s,n+1);}else{at<B>(p,0)=1;at<U>(p,8)=n;at<void*>(p,16)=malloc(n+1);memcpy(at<void*>(p,16),s,n+1);}}
static void*alloc(U n){return malloc(n);}static void release(void*p){free(p);}static void ctor(void*p){memset(p,0,0x138);}static void*catalog(){return realCatalog;}static unsigned tick(){return 100;}
template<class T>T fn(U p){switch(p){case 0x39d9c0:return (T)alloc;case 0x39d820:return (T)release;case 0x18876c:return (T)ctor;case 0x1887dc:return (T)catalog;case 0x39e240:return (T)tick;default:assert(false);return nullptr;}}
static void*dlopen(const char*,int){return (void*)1;}static void*dlsym(void*,const char*){return nullptr;}
static int __android_log_print(int,const char*,const char*,...){return 0;}
static void clearTextures(void*){}static void pauseSystemVideo720(){}static void refreshHook(void*){}
static void invalidate(void*p){at<int>(p,0xf0)=0;at<U*>(p,0xf8)=visible;at<U*>(p,0x100)=visible;}
static void rebuildHook(void*);
#include "native_folders.h"
static void showSystems(void*p){clearTextures(p);resetFolderNavigation();systemsMode=true;invalidate(p);}
static void rebuildHook(void*p){U n=0;if(folderMode){for(int i=0;i<folderCount;i++)visible[n++]=i;}else{const char*plat=strData((B*)p+0x150);for(size_t i=0;i<realItems.size();i++)if(realItems[i].platform==plat)visible[n++]=i;}at<U*>(p,0xf8)=visible;at<U*>(p,0x100)=visible+n;filterFolderGames(p);}
static U rev(){return revision;}static const char*path(const char*id){return paths[id].c_str();}
static int visit(const char*platform,const char*parent,U*direct,FolderVisitor cb,void*ctx){auto listing=station::collectionListing(realItems,paths,platform,parent);if(direct)*direct=listing.direct;if(cb)for(auto&pair:listing.children){auto&c=pair.second;cb(ctx,c.path.c_str(),c.name.c_str(),c.count,c.cover.c_str());}return (int)listing.children.size();}
static int select(const char*name){for(int i=0;i<folderCount;i++)if(!strcmp(strData(folderItems+i*0xe8+0x18),name)){at<int>(ui,0xf0)=i;return i;}assert(false);return -1;}
int main(){
 int checks=0;auto check=[&](bool ok){if(!ok){fprintf(stderr,"Failed navigation check %d\n",checks+1);abort();}checks++;};
 realItems={{"id_root","Super Nintendo",""},{"id_rpg","Super Nintendo","a.png"},{"id_deep","Super Nintendo","b.png"},{"id_other","MegaDrive","c.png"},{"id_rpg2","Super Nintendo","d.png"}};
 paths={{"id_rpg","RPG"},{"id_deep","RPG/Traduções"},{"id_other","RPG"},{"id_rpg2","RPG2"}};
 B*storage=(B*)calloc(realItems.size(),0xe8);at<B*>(realCatalog,0x88)=storage;at<B*>(realCatalog,0x90)=storage+realItems.size()*0xe8;
 for(size_t i=0;i<realItems.size();i++){strAssign(storage+i*0xe8,realItems[i].id.c_str());strAssign(storage+i*0xe8+0x18,realItems[i].id.c_str());strAssign(storage+i*0xe8+0x60,realItems[i].platform.c_str());}
 visitFolders=visit;itemFolderPath=path;foldersRevision=rev;
 check(enterFolderRoot(ui,"Super Nintendo",2));check(folderMode&&systemsMode&&foldersEnabled);check(folderCount==3);check(folderMeta[select("Todos os jogos")].count==4);
 openSelectedFolder(ui);check(!systemsMode&&!folderMode&&folderAllGames);check(at<U*>(ui,0x100)-visible==4);check(visible[3]==4);check(backFromFolder(ui));check(folderMode);
 select("RPG");openSelectedFolder(ui);check(folderMode);check(!strcmp(folderPath,"RPG"));check(folderCount==2);
 select("RPG");openSelectedFolder(ui);check(!systemsMode);check(at<U*>(ui,0x100)-visible==1&&visible[0]==1);check(backFromFolder(ui));check(!strcmp(folderPath,"RPG"));
 select("Traduções");openSelectedFolder(ui);check(!systemsMode);check(at<U*>(ui,0x100)-visible==1&&visible[0]==2);check(!strcmp(strData(storage+visible[0]*0xe8),"id_deep"));
 check(backFromFolder(ui));check(!strcmp(folderPath,"RPG"));check(backFromFolder(ui));check(folderMode&&!*folderPath);check(backFromFolder(ui));check(systemsMode&&!foldersEnabled&&!folderMode);
 check(!enterFolderRoot(ui,"Absent platform",3));check(!foldersEnabled);
 check(enterFolderRoot(ui,"Super Nintendo",2));for(int i=0;i<folderCount;i++)check(strcmp(strData(folderItems+i*0xe8+0x18),"Jogos sem subpasta")!=0);
 select("Todos os jogos");char synopsis[2048];describeFolder((U)select("Todos os jogos"),synopsis,sizeof(synopsis));
 check(strstr(synopsis,"biblioteca completa")!=nullptr);check(strstr(synopsis,"id_root")!=nullptr);check(strstr(synopsis,"id_other")==nullptr);
 describeFolder((U)select("RPG"),synopsis,sizeof(synopsis));check(strstr(synopsis,"Coleção RPG.")!=nullptr);check(strstr(synopsis,"id_rpg")!=nullptr);check(strstr(synopsis,"id_deep")!=nullptr);check(strstr(synopsis,"id_root")==nullptr);check(strstr(synopsis,"id_rpg2")==nullptr);
 select("Todos os jogos");openSelectedFolder(ui);check(at<U*>(ui,0x100)-visible==4&&visible[0]==0);
 // Repeat enter/leave across refreshes; no synthetic IDs can reach game lists.
 for(int i=0;i<200;i++){backFromFolder(ui);select("RPG2");openSelectedFolder(ui);check(at<U*>(ui,0x100)-visible==1&&visible[0]==4);revision++;refreshFolderNavigation(ui);check(at<U*>(ui,0x100)-visible==1&&visible[0]==4);}
 showSystems(ui);for(size_t i=0;i<realItems.size();i++){folderFreeString(storage+i*0xe8);folderFreeString(storage+i*0xe8+0x60);folderFreeString(storage+i*0xe8+0x18);}free(storage);folderFreeString(ui+0x150);folderFreeString(ui+0x650);
 printf("PASS %d native navigation checks; original IDs/indices, All, direct, nested, Back, flat catalogs and 200 refresh cycles\n",checks);
}
