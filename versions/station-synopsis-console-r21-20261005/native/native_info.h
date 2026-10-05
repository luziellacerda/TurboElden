// Native synopsis viewport: complete text, measured by the original font renderer.
#include "system_infos.h"
#include "game_infos.h"
#include "station_game_infos.h"
#include "station_info_layout.h"
#include "station_synopsis_scroll.h"
static bool stationConsoleAvailable(const char*);
static void drawStationConsole(void*,const char*,const StationInfoRect&);
#include "station_game_lookup.h"
struct Vec3{float x,y,z;};struct Vec2{float x,y;};
static void setLongText(void*t,const char*value){
 alignas(8) B s[24]={};strAssign(s,value);fn<void(*)(void*,const void*)>(0x2d2c70)(t,s);
 if(s[0]&1)fn<V>(0x39d820)(at<void*>(s,16));
}
static void*createInfoText(void*p,unsigned color){
 void*t=fn<void*(*)(U)>(0x39d9c0)(0x130);alignas(8) B empty[24]={};
 fn<void(*)(void*,void*,const void*,const void*,unsigned,int,Vec3,Vec2,unsigned)>(0x2d2a04)(t,at<void*>(p,0x10),empty,(B*)p+0x928+0xe8,color,0,Vec3{0,0,0},Vec2{0,0},0);
 fn<void(*)(void*,void*)>(0x2772c8)(p,t);return t;
}
static void*infoTitle;static void*infoDescription;
static const char*infoConsoleKey;static StationInfoLayout infoGameLayout;
static StationInfoRect infoViewport{},infoTrack{};
static StationSynopsisScroll infoScroll{};
alignas(8) static B infoSourceText[24]={};
static bool setSynopsisText(void*text,const char*raw,bool force){
 if(!raw)raw="";
 bool changed=force||strcmp(strData(infoSourceText),raw)!=0;
 if(!changed)return false;
 strAssign(infoSourceText,raw);
 // Keep every UTF-8 byte; old form-feed page separators become line breaks.
 alignas(8) B normalized[24]={};strAssign(normalized,raw);
 char*s=(char*)strData(normalized);for(char*p=s;*p;p++)if(*p=='\f')*p='\n';
 fn<void(*)(void*,const void*)>(0x2d2c70)(text,normalized);
 if(normalized[0]&1)fn<V>(0x39d820)(at<void*>(normalized,16));
 return true;
}
static void updateSystemInfo(void*p){
 static void*owner;static int oldIndex=-2,oldRevision;
 static bool wasSystems,wasFolder;static U oldMappedIndex=~(U)0;static float oldW,oldH;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 bool newOwner=owner!=p;
 if(newOwner){owner=p;infoTitle=createInfoText(p,0xF3FFF6ff);infoDescription=createInfoText(p,0xD1DED5ff);oldIndex=-2;}
 int cursor=at<int>(p,0xf0),rev=at<int>(systemsMode?(folderMode?(void*)folderFacade:(void*)facade):fn<void*(*)()>(0x1887dc)(),0xa8);
 U*visible=at<U*>(p,0xf8),*end=at<U*>(p,0x100);
 bool valid=visible&&end&&cursor>=0&&(U)cursor<(U)(end-visible);
 U index=valid?visible[cursor]:~(U)0;
 bool selectionChanged=newOwner||oldIndex!=cursor||oldMappedIndex!=index||wasSystems!=systemsMode||wasFolder!=folderMode;
 bool changed=selectionChanged||oldRevision!=rev||oldW!=w||oldH!=h;
 if(!changed)return;
 oldIndex=cursor;oldMappedIndex=index;wasSystems=systemsMode;wasFolder=folderMode;oldRevision=rev;oldW=w;oldH=h;
 infoConsoleKey=nullptr;
 fn<void(*)(void*,bool)>(0x277228)(infoTitle,valid);fn<void(*)(void*,bool)>(0x277228)(infoDescription,valid);
 if(!valid){infoViewport={};infoTrack={};stationSynopsisMeasure(infoScroll,0,0,true);return;}
 const char*heading="";const char*body="";char folderText[2048]={};
 if(folderMode){
  if(index>=(U)folderCount){infoViewport={};infoTrack={};stationSynopsisMeasure(infoScroll,0,0,true);return;}
  heading=strData(folderItems+index*0xe8+0x18);describeFolder(index,folderText,sizeof(folderText));body=folderText;
 }else if(systemsMode){
  if(index>=(U)systemCount){infoViewport={};infoTrack={};stationSynopsisMeasure(infoScroll,0,0,true);return;}
  const char*key=strData(items+index*0xe8+0x60);const SystemInfo*info=nullptr;
  for(int i=0;i<NINFOS;i++)if(strcmp(systemInfos[i].key,key)==0){info=&systemInfos[i];break;}
  heading=info?info->title:key;body=info?info->description:"";
 }else{
  void*catalog=fn<void*(*)()>(0x1887dc)();B*item=at<B*>(catalog,0x88)+index*0xe8;
  if(item>=at<B*>(catalog,0x90)){infoViewport={};infoTrack={};stationSynopsisMeasure(infoScroll,0,0,true);return;}
  const char*key=strData(item+0x60),*id=strData(item);heading=strData(item+0x18);infoConsoleKey=key;
  const char*serverDescription=strData(item+0x30);
  const GameInfo*gameInfo=findStationGameInfo(key,id);
  if(!gameInfo&&!starts(id,"station_"))for(int i=0;i<NGAMEINFOS;i++)if(strcmp(gameInfos[i].system,key)==0&&strcmp(gameInfos[i].id,id)==0){gameInfo=&gameInfos[i];break;}
  body=*serverDescription?serverDescription:gameInfo?gameInfo->pages:"Sinopse ainda não localizada para esta edição.";
 }
 setLongText(infoTitle,heading);bool bodyChanged=setSynopsisText(infoDescription,body,newOwner);
 float titleY=systemsMode?.873f:.851f,left=contentLeft(p),width=w*.965f-left;
 infoGameLayout=stationInfoLayout(w,h,left,infoConsoleKey&&stationConsoleAvailable(infoConsoleKey),systemsMode);
 infoViewport=infoGameLayout.text;infoTrack={};
 place(infoTitle,left,h*titleY,width,h*.045f,systemsMode?1.05f:.96f,0);
 // Height zero enables the original TextComponent's auto-height/wrapped layout.
 constexpr float scale=.82f;
 place(infoDescription,infoViewport.x,infoViewport.y,infoViewport.w,0,scale,0);
 fn<void(*)(void*,int)>(0x2d38e8)(infoDescription,3);
 float contentHeight=at<float>(infoDescription,0x58)*scale;
 if(contentHeight>infoViewport.h){
  float gutter=w*.014f;if(gutter<20.f)gutter=20.f;
  if(gutter<infoViewport.w*.2f){
   infoTrack={infoViewport.x+infoViewport.w-gutter,infoViewport.y,gutter,infoViewport.h};
   place(infoDescription,infoViewport.x,infoViewport.y,infoViewport.w-gutter,0,scale,0);
   fn<void(*)(void*,int)>(0x2d38e8)(infoDescription,3);
   contentHeight=at<float>(infoDescription,0x58)*scale;
  }
 }
 stationSynopsisMeasure(infoScroll,infoViewport.h,contentHeight,selectionChanged||bodyChanged);
 __android_log_print(4,"TurboCarousel","SYNOPSIS mode=%s content=%.1f viewport=%.1f scroll=%d bytes=%lu",folderMode?"collections":systemsMode?"platforms":"games",contentHeight,infoViewport.h,contentHeight>infoViewport.h,strlen(body));
}
static bool isSystemInfoText(void*t){return t==infoTitle||t==infoDescription;}
static void clipSynopsis(const StationInfoRect&r){
 Vec3 local[4]={{r.x,r.y,0},{r.x+r.w,r.y,0},{r.x,r.y+r.h,0},{r.x+r.w,r.y+r.h,0}};
 Vec3 point=fn<Vec3(*)(const void*,const void*)>(0x2e1274)(&formationMatrix,local);
 float l=point.x,t=point.y,right=l,bottom=t;
 for(int i=1;i<4;i++){point=fn<Vec3(*)(const void*,const void*)>(0x2e1274)(&formationMatrix,local+i);if(point.x<l)l=point.x;if(point.y<t)t=point.y;if(point.x>right)right=point.x;if(point.y>bottom)bottom=point.y;}
 Int2 pos{(int)l,(int)t};if(pos.x>l)pos.x--;if(pos.y>t)pos.y--;
 int x2=(int)right,y2=(int)bottom;if(x2<right)x2++;if(y2<bottom)y2++;
 Int2 size{x2-pos.x,y2-pos.y};fn<void(*)(const Int2*,const Int2*)>(0x2e2800)(&pos,&size);
}
static void drawSynopsisScrollbar(){
 if(infoTrack.w<=0||infoScroll.contentHeight<=infoScroll.viewportHeight)return;
 auto thumb=stationSynopsisThumb(infoScroll,infoTrack);
 float line=infoTrack.w*.16f;if(line<2)line=2;
 float x=infoTrack.x+(infoTrack.w-line)*.5f;
 rect(x,infoTrack.y,line,infoTrack.h,0x8BC7A038u);
 float thumbWidth=line*1.8f;
 rect(infoTrack.x+(infoTrack.w-thumbWidth)*.5f,thumb.y,thumbWidth,thumb.h,infoScroll.dragging?0xB4FFD0ffu:0x53DD8Cddu);
}
static void drawSystemInfoLayer(void*p){
 updateSystemInfo(p);drawSystemInfoPanel(p);
 if(infoTitle)fn<void(*)(void*,void*)>(0x2d2dc4)(infoTitle,&formationMatrix);
 if(infoDescription&&infoViewport.w>0&&infoViewport.h>0){
  fn<void(*)(void*,float,float,float)>(0x277194)(infoDescription,infoViewport.x,infoViewport.y-infoScroll.offset,0);
  clipSynopsis(infoViewport);
  fn<void(*)(void*,void*)>(0x2d2dc4)(infoDescription,&formationMatrix);
  fn<void(*)()>(0x2e2aac)();
 }
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
 if(!modal(p))drawSynopsisScrollbar();
 if(!systemsMode&&!folderMode&&infoConsoleKey&&infoGameLayout.photo)drawStationConsole(p,infoConsoleKey,infoGameLayout.console);
}
static bool touchSynopsis(void*p,const void*event){
 bool enabled=!modal(p)&&!at<B>(p,0x16d0)&&!at<B>(p,0x1d99)&&at<int>(p,0x370)>=2&&infoViewport.w>0&&infoViewport.h>0;
 if(at<int>((void*)event,0)==0&&hitCover(at<float>((void*)event,0x10),at<float>((void*)event,0x14))>=0)return false;
 return stationSynopsisTouch(infoScroll,at<int>((void*)event,0),at<U>((void*)event,8),at<float>((void*)event,0x10),at<float>((void*)event,0x14),infoViewport,infoTrack,enabled);
}
