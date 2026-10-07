#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <string>
#include <vector>
#include <map>
#include "../../station-theme-collections-r39-20261006/tests/station_collections.hpp"
using U=uintptr_t;using B=unsigned char;using V=void(*)(void*);
template<class T>T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
static bool systemsMode=true;static int lastSystem;static unsigned coverCheckAt;static bool coverCheckPending;
struct Sys {const char*key;const char*path;};static Sys systems[]={{"Super Nintendo","snes.png"}};static int NSYSTEMS=1;
static B realCatalog[0x138],ui[0x2100];static U visible[4096];static unsigned revision=1;
struct Item {std::string id,platform,coverPath;};static std::vector<Item> realItems;static std::map<std::string,std::string> paths;
static const char*strData(const void*p){auto*b=(const B*)p;return b[0]&1?*(const char*const*)(b+16):(const char*)b+1;}
static void strAssign(void*p,const char*s){if(at<B>(p,0)&1)free(at<void*>(p,16));memset(p,0,24);size_t n=strlen(s);if(n<=22){at<B>(p,0)=(B)(n*2);memcpy((B*)p+1,s,n+1);}else{at<B>(p,0)=1;at<U>(p,8)=n;at<void*>(p,16)=malloc(n+1);memcpy(at<void*>(p,16),s,n+1);}}
static void*alloc(U n){return malloc(n);}static void release(void*p){free(p);}static void ctor(void*p){memset(p,0,0x138);}static void*catalog(){return realCatalog;}static unsigned tick(){return 100;}
static void closeSearch(void*p,bool clear){at<B>(p,0x648)=0;at<B>(p,0x598)=0;if(clear)strAssign((B*)p+0x650,"");}
template<class T>T fn(U p){switch(p){case 0x39d9c0:return (T)alloc;case 0x39d820:return (T)release;case 0x18876c:return (T)ctor;case 0x1887dc:return (T)catalog;case 0x39e240:return (T)tick;case 0x219570:return (T)closeSearch;default:assert(false);return nullptr;}}
static void*dlopen(const char*,int){return (void*)1;}static void*dlsym(void*,const char*){return nullptr;}
static int __android_log_print(int,const char*,const char*,...){return 0;}
static int refreshedCursor;static void clearTextures(void*){}static void pauseSystemVideo720(){}static void refreshHook(void*p){refreshedCursor=at<int>(p,0xf0);}
static void invalidate(void*p){at<int>(p,0xf0)=0;at<U*>(p,0xf8)=visible;at<U*>(p,0x100)=visible;}
static void rebuildHook(void*);
#include "native_search_state.h"
#include "native_folders.h"
static void showSystems(void*p){clearTextures(p);resetFolderNavigation();systemsMode=true;invalidate(p);}
static void rebuildHook(void*p){
 // Model original rebuildVisible: remember the selected catalog index, expand
 // the vector, then locate that index in the broader native result.
 int oldCursor=at<int>(p,0xf0);U*oldBegin=at<U*>(p,0xf8),*oldEnd=at<U*>(p,0x100);
 bool hadSelection=oldBegin&&oldEnd&&oldCursor>=0&&(U)oldCursor<(U)(oldEnd-oldBegin);
 U selected=hadSelection?oldBegin[oldCursor]:0,n=0;
 if(folderMode){for(int i=0;i<folderCount;i++)visible[n++]=(U)i;}
 else{
  const char*plat=strData((B*)p+0x150);bool search=*strData((B*)p+0x650)!=0;
  for(size_t i=0;i<realItems.size();i++)if(search||realItems[i].platform==plat)visible[n++]=(U)i;
 }
 at<U*>(p,0xf8)=visible;at<U*>(p,0x100)=visible+n;
 int cursor=oldCursor<0?0:oldCursor;if((U)cursor>=n)cursor=n?(int)n-1:0;
 if(hadSelection)for(U i=0;i<n;i++)if(visible[i]==selected){cursor=(int)i;break;}
 at<int>(p,0xf0)=cursor;at<float>(p,0xf4)=(float)cursor;refreshHook(p);
 if(!systemsMode)stationSearchScope(p,realCatalog);
 filterFolderGames(p);refreshHook(p);
}
static U rev(){return revision;}static const char*path(const char*id){return paths[id].c_str();}
static int visit(const char*platform,const char*parent,U*direct,FolderVisitor cb,void*ctx){auto listing=station::collectionListing(realItems,paths,platform,parent);if(direct)*direct=listing.direct;if(cb)for(auto&pair:listing.children){auto&c=pair.second;cb(ctx,c.path.c_str(),c.name.c_str(),c.count,c.cover.c_str());}return (int)listing.children.size();}
static int select(const char*name){for(int i=0;i<folderCount;i++)if(!strcmp(strData(folderItems+i*0xe8+0x18),name)){at<int>(ui,0xf0)=i;return i;}assert(false);return -1;}
int main(){
 int checks=0;auto check=[&](bool ok){if(!ok){fprintf(stderr,"Failed navigation check %d\n",checks+1);std::exit(1);}checks++;};
 realItems={{"id_root","Super Nintendo",""},{"id_rpg","Super Nintendo","a.png"},{"id_deep","Super Nintendo","b.png"},{"id_other","MegaDrive","c.png"},{"id_rpg2","Super Nintendo","d.png"}};
 paths={{"id_rpg","RPG"},{"id_deep","RPG/Traduções"},{"id_other","RPG"},{"id_rpg2","RPG2"}};
 B*storage=(B*)calloc(realItems.size(),0xe8);at<B*>(realCatalog,0x88)=storage;at<B*>(realCatalog,0x90)=storage+realItems.size()*0xe8;
 for(size_t i=0;i<realItems.size();i++){strAssign(storage+i*0xe8,realItems[i].id.c_str());strAssign(storage+i*0xe8+0x18,realItems[i].id.c_str());strAssign(storage+i*0xe8+0x60,realItems[i].platform.c_str());}
 visitFolders=visit;itemFolderPath=path;foldersRevision=rev;
 check(enterFolderRoot(ui,"Super Nintendo",2));check(folderMode&&systemsMode&&foldersEnabled);check(folderCount==3);check(folderMeta[select("Todos os jogos")].count==4);
 openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode&&!folderMode&&folderAllGames);check(at<U*>(ui,0x100)-visible==4);check(visible[3]==4);check(backFromFolder(ui));check(folderMode);
 select("RPG");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(folderMode);check(!strcmp(folderPath,"RPG"));check(folderCount==2);
 select("RPG");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode);check(at<U*>(ui,0x100)-visible==1&&visible[0]==1);check(backFromFolder(ui));check(!strcmp(folderPath,"RPG"));
 select("Traduções");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode);check(at<U*>(ui,0x100)-visible==1&&visible[0]==2);check(!strcmp(strData(storage+visible[0]*0xe8),"id_deep"));
 check(backFromFolder(ui));check(!strcmp(folderPath,"RPG"));check(backFromFolder(ui));check(folderMode&&!*folderPath);check(backFromFolder(ui));check(systemsMode&&!foldersEnabled&&!folderMode);
 check(enterFolderRoot(ui,"Absent platform",3));check(!folderMode&&!systemsMode);check(at<U*>(ui,0x100)==visible);check(backFromFolder(ui));check(!foldersEnabled);
 check(enterFolderRoot(ui,"Super Nintendo",2));for(int i=0;i<folderCount;i++)check(strcmp(strData(folderItems+i*0xe8+0x18),"Jogos sem subpasta")!=0);
 select("Todos os jogos");char synopsis[6144];describeFolder((U)select("Todos os jogos"),synopsis,sizeof(synopsis));
 check(strstr(synopsis,"Toda a biblioteca")!=nullptr);check(strstr(synopsis,"id_root")!=nullptr);check(strstr(synopsis,"id_other")==nullptr);
 describeFolder((U)select("RPG"),synopsis,sizeof(synopsis));check(strstr(synopsis,"RPG —")!=nullptr);check(strstr(synopsis,"id_rpg")!=nullptr);check(strstr(synopsis,"id_deep")!=nullptr);check(strstr(synopsis,"id_root")==nullptr);check(strstr(synopsis,"id_rpg2")==nullptr);
 select("Todos os jogos");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(at<U*>(ui,0x100)-visible==4&&visible[0]==0);
 // Repeat enter/leave across refreshes; no synthetic IDs can reach game lists.
 for(int i=0;i<200;i++){backFromFolder(ui);select("RPG2");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(at<U*>(ui,0x100)-visible==1&&visible[0]==4);revision++;refreshFolderNavigation(ui);check(at<U*>(ui,0x100)-visible==1&&visible[0]==4);}

 // Return remembers stable path AND row kind, not a positional index.
 auto selectedName=[&](){int i=at<int>(ui,0xf0);check(i>=0&&i<folderCount);check(at<float>(ui,0xf4)==(float)i);return strData(folderItems+visible[i]*0xe8+0x18);};
 check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG2"));
 // Server inserts a folder before the selected entry: the visible index shifts.
 int previous=at<int>(ui,0xf0);paths["id_root"]="AAA";revision++;refreshFolderNavigation(ui);
 check(!strcmp(selectedName(),"RPG2"));check(at<int>(ui,0xf0)==previous+1);
 select("RPG");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(folderMode&&!strcmp(folderPath,"RPG"));
 select("Traduções");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode);check(backFromFolder(ui));
 check(!strcmp(selectedName(),"Traduções"));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==0);
 check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG"));
 // Same parent-path direct-games row must not be confused with its child row.
 openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}select("RPG");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode);check(backFromFolder(ui));
 check(!strcmp(selectedName(),"RPG"));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==1);
 check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG"));
 select("Todos os jogos");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(backFromFolder(ui));
 check(!strcmp(selectedName(),"Todos os jogos"));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==2);
 select("RPG2");paths.erase("id_rpg2");revision++;refreshFolderNavigation(ui);
 check(!strcmp(selectedName(),"Todos os jogos")); // Removed selection: explicit safe first row.
 // Restore a leaf then repeat return/refresh with exact selection 200 times.
 paths["id_rpg2"]="RPG2";revision++;refreshFolderNavigation(ui);
 for(int i=0;i<200;i++){select("RPG2");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode);check(backFromFolder(ui));check(!strcmp(selectedName(),"RPG2"));revision++;refreshFolderNavigation(ui);check(!strcmp(selectedName(),"RPG2"));}

 // Flat platforms bypass the synthetic one-cell "Todos os jogos" screen.
 showSystems(ui);paths.clear();revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));check(!systemsMode&&!folderMode&&folderAllGames);
 check(at<U*>(ui,0x100)-visible==4);check(folderHistoryCount==0);
 check(backFromFolder(ui));check(systemsMode&&!foldersEnabled&&lastSystem==2);
 // A root with one real child and no direct games has no meaningful choice.
 for(auto&it:realItems)paths[it.id]="Coleção única/Traduções/Seleção";
 revision++;check(enterFolderRoot(ui,"Super Nintendo",2));check(!systemsMode&&!folderMode);
 check(!strcmp(folderPath,"Coleção única/Traduções/Seleção"));check(at<U*>(ui,0x100)-visible==4);
 check(backFromFolder(ui));check(systemsMode&&!foldersEnabled); // Never re-enter a hidden chain.
 // Keep the menu when direct games coexist with one child.
 paths["id_root"]="";revision++;check(enterFolderRoot(ui,"Super Nintendo",2));check(folderMode&&folderCount==2);
 select("Coleção única");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode);check(at<U*>(ui,0x100)-visible==3);
 check(backFromFolder(ui));check(folderMode&&!*folderPath);check(!strcmp(selectedName(),"Coleção única"));
 select("Todos os jogos");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(at<U*>(ui,0x100)-visible==4);check(backFromFolder(ui));
 // A single-child chain can end at a genuine two-way menu.
 paths["id_rpg"]="Coleção única/Traduções/A";paths["id_rpg2"]="Coleção única/Traduções/B";
 paths["id_deep"]="Coleção única/Traduções/B";revision++;refreshFolderNavigation(ui);
 select("Coleção única");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(folderMode&&!strcmp(folderPath,"Coleção única/Traduções"));check(folderCount==2);
 select("B");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode&&at<U*>(ui,0x100)-visible==2);
 check(backFromFolder(ui));check(!strcmp(folderPath,"Coleção única/Traduções"));check(!strcmp(selectedName(),"B"));
 check(backFromFolder(ui));check(!*folderPath&&!strcmp(selectedName(),"Coleção única"));
 check(backFromFolder(ui));check(!foldersEnabled);
 // An automatically opened root branch returns directly to platforms.
 paths["id_root"]="Coleção única/Traduções/A";revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));check(folderMode&&!strcmp(folderPath,"Coleção única/Traduções"));
 check(backFromFolder(ui));check(!foldersEnabled&&systemsMode);
 // Mixed direct+child games inside a collection must not be hidden.
 paths["id_root"]="";paths["id_rpg"]="Coleção única/Traduções";revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));select("Coleção única");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}
 check(folderMode&&!strcmp(folderPath,"Coleção única/Traduções")&&folderCount==2);
 select("Traduções");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}check(!systemsMode&&at<U*>(ui,0x100)-visible==1);
 check(backFromFolder(ui));check(folderMeta[visible[at<int>(ui,0xf0)]].kind==1);
 check(backFromFolder(ui));check(!strcmp(selectedName(),"Coleção única"));
 // Stable original selection survives refresh and sibling insertion after auto-forward.
 for(int round=0;round<100;round++){
  select("Coleção única");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}select("B");openSelectedFolder(ui);if(!systemsMode){check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);}
  check(at<U*>(ui,0x100)-visible==2);revision++;refreshFolderNavigation(ui);
  check(backFromFolder(ui));check(!strcmp(selectedName(),"B"));
  check(backFromFolder(ui));check(!strcmp(selectedName(),"Coleção única"));
 }
 showSystems(ui);
 // Reproduce R69's actual failure after entering: native rebuild expands the
 // collection to the platform list and restores the same catalog index there.
 paths={{"id_rpg","Other"},{"id_deep","Collection"},{"id_rpg2","Collection"}};revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));select("Collection");openSelectedFolder(ui);
 check(at<int>(ui,0xf0)==0&&visible[0]==2&&at<U*>(ui,0x100)==visible+2);
 // Native [0,1,2,4], cursor 2 -> collection [2,4]. R69 clamps to 1 (last).
 rebuildHook(ui);check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0&&visible[0]==2);
 showSystems(ui);
 paths={{"id_rpg","Collection"},{"id_deep","Collection"},{"id_rpg2","Collection"}};revision++;
 check(enterFolderRoot(ui,"Super Nintendo",2));select("Collection");openSelectedFolder(ui);
 check(!folderMode&&!systemsMode&&at<int>(ui,0xf0)==0&&visible[0]==1);
 rebuildHook(ui);check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0&&visible[0]==1);check(refreshedCursor==0);
 // User movement remains valid through repeated rebuilds; never force the user
 // back to the first game after they deliberately selected another game.
 at<int>(ui,0xf0)=1;at<float>(ui,0xf4)=1;
 for(int i=0;i<20;i++){rebuildHook(ui);check(at<int>(ui,0xf0)==1&&at<float>(ui,0xf4)==1&&visible[1]==2);}
 at<int>(ui,0xf0)=2;at<float>(ui,0xf4)=2;
 rebuildHook(ui);check(at<int>(ui,0xf0)==2&&visible[2]==4);
 // Full-text native results also contain the other platform. The scope filter
 // must remap ID 4 before the collection filter remaps it a second time.
 strAssign(ui+0x650,"match");rebuildHook(ui);check(at<int>(ui,0xf0)==2&&at<float>(ui,0xf4)==2&&visible[2]==4);
 // No compacting means no animation snap during normal carousel movement.
 at<float>(ui,0xf4)=1.25f;stationSearchScope(ui,realCatalog);filterFolderGames(ui);
 check(at<int>(ui,0xf0)==2&&at<float>(ui,0xf4)==1.25f);
 // Back keeps the selected collection; a fresh entry starts at its first game.
 check(backFromFolder(ui));check(!strcmp(selectedName(),"Collection"));check(!*strData(ui+0x650));
 openSelectedFolder(ui);check(at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0&&visible[0]==1);
 revision++;refreshFolderNavigation(ui);check(at<int>(ui,0xf0)==0&&visible[0]==1);
 // A selected item removed by either filter falls back to the first remaining
 // item. Invalid or empty selections are safe and never choose the final item.
 visible[0]=0;visible[1]=1;visible[2]=2;visible[3]=4;at<U*>(ui,0x100)=visible+4;
 at<int>(ui,0xf0)=0;filterFolderGames(ui);check(at<int>(ui,0xf0)==0&&visible[0]==1);
 for(int i=0;i<5;i++)visible[i]=(U)i;at<U*>(ui,0x100)=visible+5;at<int>(ui,0xf0)=3;
 stationSearchScope(ui,realCatalog);check(at<int>(ui,0xf0)==0&&visible[0]==0);
 for(int i=0;i<5;i++)at<B>(storage+i*0xe8,0xa8)=i==2||i==4?1:0;
 at<B>(ui,0x148)=1;at<int>(ui,0xf0)=3;stationSearchScope(ui,realCatalog);
 check(at<int>(ui,0xf0)==1&&visible[1]==4&&at<U*>(ui,0x100)==visible+2);
 at<int>(ui,0xf0)=-1;stationSearchScope(ui,realCatalog);check(at<int>(ui,0xf0)==0);
 at<int>(ui,0xf0)=200;filterFolderGames(ui);check(at<int>(ui,0xf0)==0);
 folderCopy(folderPath,sizeof(folderPath),"Removed");filterFolderGames(ui);
 check(at<U*>(ui,0x100)==visible&&at<int>(ui,0xf0)==0&&at<float>(ui,0xf4)==0);
 showSystems(ui);for(size_t i=0;i<realItems.size();i++){folderFreeString(storage+i*0xe8);folderFreeString(storage+i*0xe8+0x60);folderFreeString(storage+i*0xe8+0x18);}free(storage);folderFreeString(ui+0x150);folderFreeString(ui+0x650);
 printf("PASS %d native navigation checks; original IDs/indices, All, direct, nested, Back, flat catalogs and 200 refresh cycles\n",checks);
}
