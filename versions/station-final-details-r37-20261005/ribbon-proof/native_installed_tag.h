// Raised emerald corner ribbon. Original installed-state and visibility gates remain.
// One bounded native mesh draw plus the cached native text. No new assets or timers.
#include "station_installed_ribbon.h"
static void*installedTagText;
static void drawInstalledTag(void*p){
 if(systemsMode||folderMode||modal(p)||at<int>(p,0x370)<2)return;
 int selected=fn<int(*)(void*)>(0x21b0c8)(p);if(selected<0)return;
 void*cat=fn<void*(*)()>(0x1887dc)();B*begin=at<B*>(cat,0x88),*end=at<B*>(cat,0x90);
 if(!begin||!end||end<begin||(U)selected>=(U)(end-begin)/0xe8||!begin[(U)selected*0xe8+0xa8])return;
 float distance=at<int>(p,0xf0)-at<float>(p,0xf4);if(absolute(distance)>.30f)return;
 auto cover=coverSlot(p,distance);
 StationRibbonMesh<Vertex> ribbon;
 stationBuildInstalledRibbon(ribbon,cover.w,fn<unsigned(*)()>(0x39e240)());
 if(!ribbon.count)return;
 NativeMatrix faceLocal{{1,0,0,0,0,1,0,0,0,0,1,0,cover.x,cover.y,0,1}};
 NativeMatrix faceMatrix=fn<NativeMatrix(*)(const void*,const void*)>(3019156)(&formationMatrix,&faceLocal);
 fn<void(*)(const void*)>(0x2e5640)(&faceMatrix);fn<void(*)(unsigned)>(0x2e52e8)(0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(ribbon.vertices,ribbon.count,4,5);
 constexpr float c=.707106781f;
 NativeMatrix textLocal{{c,-c,0,0,c,c,0,0,0,0,1,0,cover.x,cover.y+ribbon.reach,0,1}};
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
