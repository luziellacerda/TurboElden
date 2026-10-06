// Installed state belongs to the catalog item, not the selected cursor.
// Called immediately after each visible original card, preserving its z order.
// Reuse one text layout at the hero reference width and scale it with the card.
#include "station_installed_ribbon.h"
static void*installedTagText;
static void drawInstalledCover(void*p,U index,const CoverRect&cover){
 if(systemsMode||folderMode||modal(p)||at<int>(p,0x370)<2||cover.w<=0||cover.h<=0)return;
 void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);
 if(!begin||!end||end<begin||index>=(U)(end-begin)/0xe8||!begin[index*0xe8+0xa8])return;
 float reference=coverSlot(p,0).w;if(reference<=0)return;
 float scale=cover.w/reference;
 StationRibbonMesh<Vertex> ribbon;
 stationBuildInstalledRibbon(ribbon,reference,fn<unsigned(*)()>(0x39e240)());
 if(!ribbon.count)return;
 NativeMatrix faceLocal{{scale,0,0,0,0,scale,0,0,0,0,1,0,cover.x,cover.y,0,1}};
 NativeMatrix faceMatrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(&formationMatrix,&faceLocal);
 fn<void(*)(const void*)>(0x2e5640)(&faceMatrix);fn<void(*)(unsigned)>(0x2e52e8)(0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(ribbon.vertices,ribbon.count,4,5);
 float c=.707106781f*scale;
 NativeMatrix textLocal{{c,-c,0,0,c,c,0,0,0,0,1,0,cover.x,cover.y+ribbon.reach*scale,0,1}};
 NativeMatrix textMatrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(&formationMatrix,&textLocal);
 static void*owner;static float oldLength,oldHalf;
 if(owner!=p){owner=p;installedTagText=createInfoText(p,0xF5FFF9ffu);setLongText(installedTagText,"INSTALADO");oldLength=0;}
 if(oldLength!=ribbon.length||oldHalf!=ribbon.half){
  oldLength=ribbon.length;oldHalf=ribbon.half;
  fitInfoText(installedTagText,{ribbon.half*1.55f,-ribbon.half*.82f,ribbon.length-ribbon.half*3.10f,ribbon.half*1.64f},1.22f,1);
 }
 fn<void(*)(void*,void*)>(0x2d2dc4)(installedTagText,&textMatrix);
 fn<void(*)(const void*)>(0x2e5640)(&formationMatrix);
}
