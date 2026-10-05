#include "collection_presentation.h"
#include "collection_video_policy.h"
// Presentation-only folders. Games keep their original CatalogService indices/IDs.
// Metadata is committed with the signed catalog by libstation_frontend on SDL's thread.
static bool foldersEnabled,folderMode,folderAllGames;
static char folderPlatform[512],folderPath[2049],folderReturnPath[2049];
alignas(16) static B folderFacade[0x138];static bool folderFacadeReady;
struct FolderMeta {alignas(8) B path[24];U count;int kind;int pad;};
static B*folderItems;static FolderMeta*folderMeta;static int folderCount,folderCapacity;
static U folderRevision;
static const CollectionVideoDef*folderVideo(void*p,int index){
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
 if(index<0||!visible||visible+index>=end||visible[index]>=(U)folderCount)return nullptr;
 const auto&m=folderMeta[visible[index]];
 return collectionVideoFor(folderPlatform,strData(m.path),m.kind==2);
}
static float folderVideoAspect(void*p,int index){const auto*v=folderVideo(p,index);return v?v->aspect:1.f;}
using FolderVisitor=void(*)(void*,const char*,const char*,U,const char*);
static int(*visitFolders)(const char*,const char*,U*,FolderVisitor,void*);
static const char*(*itemFolderPath)(const char*);
static U(*foldersRevision)();
static void showSystems(void*);
static bool folderCopy(char*dst,U size,const char*src){U n=strlen(src);if(n>=size)return false;memcpy(dst,src,n+1);return true;}
static bool folderBridge(){
 if(visitFolders&&itemFolderPath&&foldersRevision)return true;
 void*lib=dlopen("libstation_frontend.so",2);if(!lib)return false;
 visitFolders=(decltype(visitFolders))dlsym(lib,"StationCatalog_visitFolders");
 itemFolderPath=(decltype(itemFolderPath))dlsym(lib,"StationCatalog_itemFolderPath");
 foldersRevision=(decltype(foldersRevision))dlsym(lib,"StationCatalog_folderRevision");
 return visitFolders&&itemFolderPath&&foldersRevision;
}
static void folderFreeString(void*p){if(at<B>(p,0)&1)fn<V>(0x39d820)(at<void*>(p,16));}
static void releaseFolderListing(){
 const U offsets[]={0,0x18,0x60,0xc8};
 for(int i=0;i<folderCount;i++){for(int j=0;j<4;j++)folderFreeString(folderItems+i*0xe8+offsets[j]);folderFreeString(folderMeta[i].path);}
 if(folderItems)fn<V>(0x39d820)(folderItems);if(folderMeta)fn<V>(0x39d820)(folderMeta);
 folderItems=nullptr;folderMeta=nullptr;folderCount=folderCapacity=0;
 if(folderFacadeReady){at<void*>(folderFacade,0x88)=nullptr;at<void*>(folderFacade,0x90)=nullptr;at<void*>(folderFacade,0x98)=nullptr;}
}
static void resetFolderNavigation(){foldersEnabled=folderMode=folderAllGames=false;folderPlatform[0]=folderPath[0]=folderReturnPath[0]=0;releaseFolderListing();}
static const char*folderArt(){for(int i=0;i<NSYSTEMS;i++)if(strcmp(systems[i].key,folderPlatform)==0)return systems[i].path;return "";}
static void folderNumber(char*dst,U n){char reversed[24];int count=0;do{reversed[count++]=(char)('0'+n%10);n/=10;}while(n);int j=0;while(count)dst[j++]=reversed[--count];dst[j]=0;}
static void appendFolder(const char*path,const char*name,U count,const char*cover,int kind){
 if(folderCount>=folderCapacity)return;
 B*item=folderItems+folderCount*0xe8;char id[40]="collection_";folderNumber(id+11,(U)folderCount);
 strAssign(item,id);strAssign(item+0x18,name);strAssign(item+0x60,folderPlatform);
 strAssign(item+0xc8,cover&&*cover?cover:folderArt());
 strAssign(folderMeta[folderCount].path,path);folderMeta[folderCount].count=count;folderMeta[folderCount].kind=kind;folderCount++;
}
static void describeFolder(U index,char*body,U size){
 if(index>=(U)folderCount){if(size)body[0]=0;return;}
 const FolderMeta&meta=folderMeta[index];const char*path=strData(meta.path);
 const char*examples[3]={};unsigned count=0;
 void*real=fn<void*(*)()>(0x1887dc)();B*end=at<B*>(real,0x90);
 for(B*it=at<B*>(real,0x88);it&&it<end&&count<3;it+=0xe8){
  if(strcmp(strData(it+0x60),folderPlatform)!=0)continue;
  const char*itemPath=itemFolderPath?itemFolderPath(strData(it)):"";
  if(!collectionHasPath(path,itemPath?itemPath:"",meta.kind==2,meta.kind==1))continue;
  const char*name=strData(it+0x18);if(!*name)continue;
  bool duplicate=false;for(unsigned j=0;j<count;j++)if(strcmp(examples[j],name)==0)duplicate=true;
  if(!duplicate)examples[count++]=name;
 }
 collectionSynopsis(body,size,strData(folderItems+index*0xe8+0x18),folderPlatform,meta.count,meta.kind,examples,count);
}
static void appendFolderVisitor(void*,const char*path,const char*name,U count,const char*cover){appendFolder(path,name,count,cover,0);}
static void showFolderMenu(void*p,const char*path){
 char next[2049];if(!folderCopy(next,sizeof(next),path)||!folderBridge())return;
 U direct=0;int children=visitFolders(folderPlatform,next,&direct,nullptr,nullptr);
 clearTextures(p);releaseFolderListing();
 if(!folderFacadeReady){fn<V>(0x18876c)(folderFacade);folderFacadeReady=true;}
 folderCapacity=children+2;folderItems=(B*)fn<void*(*)(U)>(0x39d9c0)((U)folderCapacity*0xe8);folderMeta=(FolderMeta*)fn<void*(*)(U)>(0x39d9c0)((U)folderCapacity*sizeof(FolderMeta));
 memset(folderItems,0,(U)folderCapacity*0xe8);memset(folderMeta,0,(U)folderCapacity*sizeof(FolderMeta));
 folderCopy(folderPath,sizeof(folderPath),next);folderMode=true;systemsMode=true;folderAllGames=false;
 if(!*next){void*real=fn<void*(*)()>(0x1887dc)();U total=0;for(B*it=at<B*>(real,0x88);it<at<B*>(real,0x90);it+=0xe8)if(strcmp(strData(it+0x60),folderPlatform)==0)total++;appendFolder("","Todos os jogos",total,folderArt(),2);}
 if(direct&&*next&&children)appendFolder(next,collectionLeafName(next),direct,folderArt(),1);
 visitFolders(folderPlatform,next,nullptr,appendFolderVisitor,nullptr);
 at<void*>(folderFacade,0x88)=folderItems;at<void*>(folderFacade,0x90)=folderItems+(U)folderCount*0xe8;at<void*>(folderFacade,0x98)=folderItems+(U)folderCount*0xe8;
 at<int>(folderFacade,0x50)=2;at<int>(folderFacade,0xa8)++;
 strAssign((B*)p+0x150,"");strAssign((B*)p+0x650,"");at<B>(p,0x148)=0;
 invalidate(p);rebuildHook(p);refreshHook(p);folderRevision=foldersRevision();
 __android_log_print(4,"TurboCarousel","FOLDERS menu platform=%s depth-path=%s children=%d direct=%lu",folderPlatform,folderPath,children,direct);
}
static bool enterFolderRoot(void*p,const char*platform,int index){
 if(!folderBridge())return false;
 if(!folderCopy(folderPlatform,sizeof(folderPlatform),platform))return false;
 lastSystem=index;foldersEnabled=true;showFolderMenu(p,"");return true;
}
static void enterFolderGames(void*p,const char*path,bool all,const char*returnPath){
 char next[2049],back[2049];if(!folderCopy(next,sizeof(next),path)||!folderCopy(back,sizeof(back),returnPath))return;
 clearTextures(p);folderMode=false;systemsMode=false;folderAllGames=all;folderCopy(folderPath,sizeof(folderPath),next);folderCopy(folderReturnPath,sizeof(folderReturnPath),back);
 strAssign((B*)p+0x150,folderPlatform);strAssign((B*)p+0x650,"");at<B>(p,0x148)=0;
 at<int>(fn<void*(*)()>(0x1887dc)(),0x11c)=0;
 invalidate(p);rebuildHook(p);refreshHook(p);
 coverCheckAt=fn<unsigned(*)()>(0x39e240)();coverCheckPending=true;
 __android_log_print(4,"TurboCarousel","FOLDERS games platform=%s path=%s all=%d visible=%lu",folderPlatform,folderPath,all,(at<U>(p,0x100)-at<U>(p,0xf8))/8);
}
static void openSelectedFolder(void*p){
 int cursor=at<int>(p,0xf0);U*begin=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
 if(!begin||cursor<0||begin+cursor>=end||begin[cursor]>=(U)folderCount)return;
 FolderMeta&meta=folderMeta[begin[cursor]];char target[2049],back[2049];folderCopy(target,sizeof(target),strData(meta.path));folderCopy(back,sizeof(back),folderPath);
 if(meta.kind==2){enterFolderGames(p,"",true,back);return;}
 if(meta.kind==1){enterFolderGames(p,target,false,back);return;}
 U direct=0;if(visitFolders(folderPlatform,target,&direct,nullptr,nullptr)>0)showFolderMenu(p,target);
 else enterFolderGames(p,target,false,back);
}
static bool backFromFolder(void*p){
 if(!foldersEnabled)return false;
 if(!systemsMode){showFolderMenu(p,folderReturnPath);return true;}
 if(folderMode&&*folderPath){char parent[2049];folderCopy(parent,sizeof(parent),folderPath);int n=(int)strlen(parent);while(n>0&&parent[n-1]!='/')--n;parent[n>0?n-1:0]=0;showFolderMenu(p,parent);return true;}
 showSystems(p);return true;
}
static void filterFolderGames(void*p){
 if(!foldersEnabled||systemsMode||folderAllGames||!itemFolderPath)return;
 void*catalog=fn<void*(*)()>(0x1887dc)();B*first=at<B*>(catalog,0x88),*last=at<B*>(catalog,0x90);U count=first&&last>=first?(U)(last-first)/0xe8:0;
 U*begin=at<U*>(p,0xf8),*end=at<U*>(p,0x100),*out=begin;
 for(U*it=begin;it&&it<end;it++)if(*it<count&&strcmp(itemFolderPath(strData(first+*it*0xe8)),folderPath)==0)*out++=*it;
 at<U*>(p,0x100)=out;int visible=begin&&out?(int)(out-begin):0;
 if(at<int>(p,0xf0)>=visible){at<int>(p,0xf0)=visible?visible-1:0;at<float>(p,0xf4)=(float)at<int>(p,0xf0);}
 if(out!=end){at<int>(p,0x220)=-1;at<U>(p,0x228)=~0UL;}
}
static void refreshFolderNavigation(void*p){
 if(!foldersEnabled||!foldersRevision||folderRevision==foldersRevision())return;
 folderRevision=foldersRevision();
 if(folderMode){char current[2049];folderCopy(current,sizeof(current),folderPath);showFolderMenu(p,current);}
 else{rebuildHook(p);refreshHook(p);}
}
