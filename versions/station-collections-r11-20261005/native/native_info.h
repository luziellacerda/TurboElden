// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
#include "system_infos.h"
#include "game_infos.h"
#include "station_game_infos.h"
#include "station_info_layout.h"
static bool stationConsoleAvailable(const char*);
static void drawStationConsole(void*,const char*,const StationInfoRect&);
#include "station_game_lookup.h"
struct Vec3{float x,y,z;};struct Vec2{float x,y;};
static void setLongText(void*t,const char*value){
 alignas(8) B s[24]={};strAssign(s,value);fn<void(*)(void*,const void*)>(0x2d2c70)(t,s);
 if(s[0]&1)fn<V>(0x39d820)(at<void*>(s,16));
}
static void* createInfoText(void*p,unsigned color){
 void*t=fn<void*(*)(U)>(0x39d9c0)(0x130);alignas(8) B empty[24]={};
 fn<void(*)(void*,void*,const void*,const void*,unsigned,int,Vec3,Vec2,unsigned)>(0x2d2a04)(t,at<void*>(p,0x10),empty,(B*)p+0x928+0xe8,color,0,Vec3{0,0,0},Vec2{0,0},0);
 fn<void(*)(void*,void*)>(0x2772c8)(p,t);return t;
}
static void*infoTitle;static void*infoDescription;
static const char*infoConsoleKey;static StationInfoLayout infoGameLayout;
static void updateSystemInfo(void*p){
 static void*owner;void*&title=infoTitle;void*&description=infoDescription;static int oldIndex=-2;static bool wasSystems,wasFolder;
 static int oldRevision;static U oldMappedIndex=~(U)0;static float oldW,oldH;static const GameInfo*gameInfo;static unsigned pageStarted;static int oldPage=-1;static char serverPages[8032]={};static int serverPageCount;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);unsigned tick=fn<unsigned(*)()>(0x39e240)();
 if(owner!=p){owner=p;title=createInfoText(p,0xF3FFF6ff);description=createInfoText(p,0xD1DED5ff);oldIndex=-2;}
 int cursor=at<int>(p,0xf0),rev=at<int>(systemsMode?(folderMode?(void*)folderFacade:(void*)facade):fn<void*(*)()>(0x1887dc)(),0xa8);
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
 bool valid=visible&&end&&cursor>=0&&(U)cursor<(U)(end-visible);
 U index=valid?visible[cursor]:~(U)0;
 // Filtering may keep cursor=0 while selecting a completely different game.
 bool changed=oldIndex!=cursor||oldMappedIndex!=index||wasSystems!=systemsMode||wasFolder!=folderMode||oldRevision!=rev||oldW!=w||oldH!=h;
 if(!changed){
  int count=serverPageCount?serverPageCount:(gameInfo?gameInfo->pageCount:0);
  if(folderMode||systemsMode||count<2)return;
  int page=((tick-pageStarted)/9500)%count;if(page==oldPage)return;
 }else{oldPage=-1;}
 oldIndex=cursor;oldMappedIndex=index;wasSystems=systemsMode;wasFolder=folderMode;oldRevision=rev;oldW=w;oldH=h;
 fn<void(*)(void*,bool)>(0x277228)(title,valid);fn<void(*)(void*,bool)>(0x277228)(description,valid);
 if(!valid){infoConsoleKey=nullptr;return;}
 const char*heading="";const char*body="";char pageText[2048]={};
 if(folderMode){
  gameInfo=nullptr;serverPageCount=0;serverPages[0]=0;infoConsoleKey=nullptr;if(index>=(U)folderCount)return;
  heading=strData(folderItems+index*0xe8+0x18);
  describeFolder(index,pageText,sizeof(pageText));body=pageText;
 }else if(systemsMode){
  gameInfo=nullptr;serverPageCount=0;serverPages[0]=0;
  infoConsoleKey=nullptr;
  if(index>=(U)systemCount)return;
  const char*key=strData(items+index*0xe8+0x60);const SystemInfo*info=nullptr;
  for(int i=0;i<NINFOS;i++)if(strcmp(systemInfos[i].key,key)==0){info=&systemInfos[i];break;}
  heading=info?info->title:key;body=info?info->description:"";
  __android_log_print(4,"TurboCarousel","INFO filter=%s; source=%s; bytes=%lu",key,info?info->file:"",strlen(body));
 }else{
  void*catalog=fn<void*(*)()>(0x1887dc)();B*item=at<B*>(catalog,0x88)+index*0xe8;
  if(item>=at<B*>(catalog,0x90))return;
  const char*key=strData(item+0x60),*id=strData(item);heading=strData(item+0x18);
  const char*serverDescription=strData(item+0x30);
  infoConsoleKey=key;
  if(changed){
   if(strcmp(serverPages,serverDescription)!=0){
    unsigned n=0;while(serverDescription[n]&&n<sizeof(serverPages)-1){serverPages[n]=serverDescription[n];n++;}serverPages[n]=0;
    serverPageCount=n?1:0;for(unsigned i=0;i<n;i++)if(serverPages[i]=='\f')serverPageCount++;
    pageStarted=tick;oldPage=-1;
   }
   const GameInfo*nextInfo=findStationGameInfo(key,id);
   if(!nextInfo&&!starts(id,"station_"))for(int i=0;i<NGAMEINFOS;i++)if(strcmp(gameInfos[i].system,key)==0&&strcmp(gameInfos[i].id,id)==0){nextInfo=&gameInfos[i];break;}
   // Cover batches change the catalog revision while this game stays selected.
   // Keep synopsis paging time until the selected metadata really changes.
   if(nextInfo!=gameInfo){pageStarted=tick;oldPage=-1;}gameInfo=nextInfo;
   __android_log_print(4,"TurboCarousel","GAMEINFO filter=%s; id=%s; name=%s; found=%d",key,id,heading,gameInfo!=nullptr);
  }
  body="Sinopse ainda não localizada para esta edição.";
  if(serverPageCount){
   oldPage=((tick-pageStarted)/9500)%serverPageCount;const char*text=serverPages;
   for(int page=0;page<oldPage;page++){while(*text&&*text!='\f')text++;if(*text)text++;}
   int n=0;while(*text&&*text!='\f'&&n<(int)sizeof(pageText)-1)pageText[n++]=*text++;body=pageText;
  }else if(gameInfo){
   oldPage=((tick-pageStarted)/9500)%gameInfo->pageCount;const char*text=gameInfo->pages;
   for(int page=0;page<oldPage;page++){while(*text&&*text!='\f')text++;if(*text)text++;}
   int n=0;while(*text&&*text!='\f'&&n<(int)sizeof(pageText)-1)pageText[n++]=*text++;body=pageText;
  }
 }
 setLongText(title,heading);setLongText(description,body);
 float titleY=systemsMode?.873f:.851f,bodyY=systemsMode?.422f:.454f,left=contentLeft(p),width=w*.965f-left;
 infoGameLayout=stationInfoLayout(w,h,left,!systemsMode&&infoConsoleKey&&stationConsoleAvailable(infoConsoleKey));
 place(title,left,h*titleY,width,h*.045f,systemsMode?1.05f:.96f,0);
 if(systemsMode)place(description,left,h*bodyY,width,h*(.812f-bodyY),.82f,0);
 else place(description,infoGameLayout.text.x,infoGameLayout.text.y,infoGameLayout.text.w,infoGameLayout.text.h,.82f,0);
 // Alignment enum: LEFT=0, CENTER=1, RIGHT=2, TOP=3, BOTTOM=4.
 // LEFT in the vertical setter logged an error every rendered frame.
 fn<void(*)(void*,int)>(0x2d38e8)(description,3);
}

static void*folderLabels[20];static void*folderLabelOwner;
static bool isSystemInfoText(void*t){if(t==infoTitle||t==infoDescription)return true;for(int i=0;i<20;i++)if(t==folderLabels[i])return true;return false;}
static void drawFolderLabels(void*p){
 if(!folderMode)return;
 if(folderLabelOwner!=p){folderLabelOwner=p;for(int i=0;i<20;i++)folderLabels[i]=nullptr;}
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);if(!visible||!end)return;
 for(int k=0;k<paintedCount&&k<20;k++){
  const CoverRect&r=painted[k];if(r.index<0||visible+r.index>=end||visible[r.index]>=(U)folderCount)continue;
  if(!folderLabels[k])folderLabels[k]=createInfoText(p,0xF3FFF6ff);
  const char*name=strData(folderItems+visible[r.index]*0xe8+0x18);void*label=folderLabels[k];
  if(strcmp(strData((B*)label+0xd0),name)!=0)setLongText(label,name);
  const float band=r.h*.25f,scale=r.w/420.f;
  fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
  rect(r.x+r.w*.025f,r.y+r.h-band-r.h*.035f,r.w*.95f,band,0x031008ee);
  place(label,r.x+r.w*.065f,r.y+r.h-band-r.h*.025f,r.w*.87f,band,scale<.30f?.30f:scale>.90f?.90f:scale,1);
  fn<void(*)(void*,void*)>(0x2d2dc4)(label,&formationMatrix);
 }
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
}
static void drawSystemInfoLayer(void*p){
 updateSystemInfo(p);
 drawSystemInfoPanel(p);
 if(infoTitle)fn<void(*)(void*,void*)>(0x2d2dc4)(infoTitle,&formationMatrix);
 if(infoDescription)fn<void(*)(void*,void*)>(0x2d2dc4)(infoDescription,&formationMatrix);
 // Text rendering changes the active matrix. Restore the store transform before native cards.
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
 if(!systemsMode&&infoConsoleKey&&infoGameLayout.photo)drawStationConsole(p,infoConsoleKey,infoGameLayout.console);
}
