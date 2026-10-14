// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Clouds-only background. Aircraft and stars have no rendering or update work.
static void drawNativeClouds(float,float,float);
static float flightSin(float);
// One continuous shade across the carousel. The lower-right corner remains the
// light source while the top/left gradually darken behind the small covers.
// Artwork and text are drawn later; no cover-shaped or horizontal dark band.
static float gameBackdropEase(float t){
 if(t<=0)return 0;if(t>=1)return 1;return t*t*(3.f-2.f*t);
}
static void drawCarouselDiagonalBackdrop(float w,float h){
 auto cover=coverSlot(gui,0);
 float anchorX=cover.x+cover.w*.44f,anchorY=cover.y+cover.h*.075f;
 static Vertex strip[754];static unsigned count=0;
 static float lastW=-1,lastH=-1,lastLeft=-1,lastX=-1,lastY=-1;
 if(w!=lastW||h!=lastH||cover.x!=lastLeft||anchorX!=lastX||anchorY!=lastY){
  lastW=w;lastH=h;lastLeft=cover.x;lastX=anchorX;lastY=anchorY;count=0;
  // Restore the original 14x26 mesh and diagonal black plateau. A second
  // smooth diagonal term darkens the top without introducing a row boundary.
  for(int row=0;row<14;row++){
   if(row){strip[count]=strip[count-1];count++;}
   for(int col=0;col<=25;col++){
    float t=col==0?0:(col-1)/24.f;
    for(int edge=0;edge<2;edge++){
     float y=h*(row+edge)/14.f,line=anchorX*(h-y)/(h-anchorY);
     if(line<cover.x)line=cover.x; // Entire left lateral space remains black.
     float x=col==0?0:line+(w-line)*t;
     float original=1.f-gameBackdropEase(t);
     float away=(w-x)/w*.22f+(h-y)/h*.78f;
     float ambient=.74f*gameBackdropEase(away);
     unsigned alpha=(unsigned)(255.f*(original+(1.f-original)*ambient)+.5f);
     unsigned color=fn<unsigned(*)(unsigned)>(3029376)(alpha);
     Vertex v={x,y,0,0,color};
     if(row&&col==0&&edge==0)strip[count++]=v;
     strip[count++]=v;
    }
   }
  }
 }
 fn<void(*)(unsigned)>(3035880)(0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);
}
// The existing appearance theme drives both backdrop choices and the Lottie switch.
// Blue uses the requested sky-blue gradient; black backdrop branches stay exact.
static unsigned stationWaveTop(){return stationThemeId==1?0x287EB5ffu:0x000000ffu;}
static unsigned stationWaveBottom(){return stationThemeId==1?0x5DAEDEffu:0x07090Dffu;}
#include "station_wave_palette.h"
// Read the already selected platform without JNI/catalog callbacks or allocation.
// Game lists retain their exact platform filter; folders retain folderPlatform.
static const char* stationWaveSystemKey(){
 if(!gui||at<int>(gui,0x370)!=3)return nullptr;
 if(folderMode)return folderPlatform;
 if(!systemsMode)return strData((B*)gui+0x150);
 int cursor=at<int>(gui,0xf0);U*begin=at<U*>(gui,0xf8),*end=at<U*>(gui,0x100);
 if(!items||!begin||!end||end<begin||cursor<0||(U)cursor>=(U)(end-begin))return nullptr;
 U index=begin[cursor];if(index>=(U)systemCount)return nullptr;
 return strData(items+index*0xe8+0x60);
}
static const StationWavePalette* stationWaveCurrentPalette(){
 // Cache only the exact short key and palette pointer; aliases are evaluated
 // on platform changes. Theme fallback stays live, independent of this cache.
 static char previous[64]={};static const StationWavePalette*remembered;
 const char*key=stationWaveSystemKey();if(!key)key="";
 unsigned length=0;while(length<sizeof(previous)&&key[length])length++;
 const StationWavePalette*palette=nullptr;
 if(length<sizeof(previous)){
  if(strcmp(previous,key)!=0){memcpy(previous,key,length+1);remembered=stationWavePalette(key);}
  palette=remembered;
 }
 // A longer unknown key never truncates or reuses a different family's palette.
 return palette;
}
static unsigned stationWaveColor(int wave,const StationWavePalette*palette){
 if(palette)return palette->colors[wave];
 // Unlisted systems/welcome retain their theme RGB with the same legible alpha.
 return stationThemeId==1?(wave==0?0x65BFF0B0u:wave==1?0x6587DEA0u:0x9DCBDD90u):(wave==0?0x8193A6B0u:wave==1?0x596775A0u:0x9DA8B190u);
}
// Requested palettes use three to five strips; other families keep three.
// One fixed 66-vertex stack buffer is reused, with the same 32 segments.
static void drawNativeWaves(float w,float h,float t){
 fn<void(*)(unsigned)>(3035880)(0);
 const auto*palette=stationWaveCurrentPalette();unsigned bands=palette?palette->count:3u;
 Vertex strip[66];
 for(unsigned wave=0;wave<bands;wave++){
  unsigned color=fn<unsigned(*)(unsigned)>(3029376)(stationWaveColor((int)wave,palette));
  for(int i=0;i<=32;i++){
   float u=i/32.f,x=w*u,y=h*(.47f+wave*.065f+flightSin(u*5.5f+t*.32f+wave*.7f)*.075f+flightSin(u*2.1f-t*.19f)*.025f);
   float half=h*(.007f+wave*.002f)*(palette?palette->widthMultipliers[wave]:1.f);strip[i*2]={x,y-half,0,0,color};strip[i*2+1]={x,y+half,0,0,color};
  }
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,66,4,5);
 }
}
// Match the online room's three wide, filled, sinusoidal ribbons. The main
// screen keeps their vertical gradients and uses a dark-to-light blue spectrum
// in every console and both themes. This adds no timer, heap or cloud pass.
static unsigned stationOnlineRibbonMix(unsigned a,unsigned b,float t){
 if(t<=0)return a;if(t>=1)return b;
 unsigned rgba=0;
 for(int shift=0;shift<=24;shift+=8){
  float first=(float)((a>>shift)&255u),last=(float)((b>>shift)&255u);
  rgba|=(unsigned)(first+(last-first)*t+.5f)<<shift;
 }
 return rgba;
}
static void drawNativeOnlineRibbons(float w,float h,float t){
 static const unsigned blueTop[3]={0x18447760u,0x327DBD58u,0x89D2F250u};
 static const unsigned blueBottom[3]={0x102C5328u,0x20588424u,0x5B98B520u};
 static const unsigned darkTop[3]={0x2B65AE60u,0x4A9CD958u,0xA1DCF550u};
 static const unsigned darkBottom[3]={0x1B416F28u,0x316B9824u,0x6F9FB520u};
 static const float phaseSpeed[3]={.68f,.84f,.76f};
 static Vertex strip[154];unsigned count=0;
 for(unsigned layer=0;layer<3;layer++){
  unsigned top=stationThemeId==1?blueTop[layer]:darkTop[layer];
  unsigned bottom=stationThemeId==1?blueBottom[layer]:darkBottom[layer];
  unsigned bottomColor=fn<unsigned(*)(unsigned)>(3029376)(bottom);
  // Different deterministic tempos keep the three broad ribbons from drifting
  // in lockstep. The small envelope and vertical bob use the existing clock.
  float drift=.25f*flightSin(t*(.067f+.013f*layer)+layer*1.73f);
  float primary=t*phaseSpeed[layer]+drift+layer*1.15f;
  float secondary=t*phaseSpeed[layer]*.73f+drift*.55f+layer*.6f;
  float envelope=1.f+.20f*flightSin(t*(.11f+.023f*layer)+layer*2.07f);
  float bob=.014f*flightSin(t*(.19f+.027f*layer)+layer*1.41f);
  for(int point=0;point<=24;point++){
   float u=point/24.f;
   float curve=envelope*(flightSin(u*6.2831853f+primary)*.055f+
                         flightSin(u*3.14159265f+secondary)*.035f);
   float x=w*u,y=h*(.59f+layer*.055f+bob+curve);
   float gradient=(y/h-.40f)/.50f;
   unsigned upper=stationOnlineRibbonMix(top,bottom,gradient);
   Vertex a={x,y,0,0,fn<unsigned(*)(unsigned)>(3029376)(upper)};
   Vertex b={x,h,0,0,bottomColor};
   if(layer&&point==0){strip[count]=strip[count-1];count++;strip[count++]=a;}
   strip[count++]=a;strip[count++]=b;
  }
 }
 fn<void(*)(unsigned)>(3035880)(0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);
}
static void drawNativeSpace(float w,float h){
 if(w<=0||h<=0)return;
 // Initial preparation has no background work: return before timing,
 // preference lookup, vertex generation or any cloud shader initialization.
 if(gui&&at<int>(gui,0x370)==0){fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,0x000000ffu,0x000000ffu,false,4,5);return;}
 int background=stationGraphicsBackground();
 if(background==2){fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,0x000000ffu,0x000000ffu,false,4,5);return;}
 unsigned top=background==1?stationWaveTop():background==3?(stationThemeId==1?0x287EB5ffu:0x000000ffu):stationSkyTop();
 unsigned bottom=background==1?stationWaveBottom():background==3?top:stationSkyBottom();
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,top,bottom,false,4,5);
 static unsigned started;unsigned now=fn<unsigned(*)()>(0x39e240)();if(!started)started=now;float t=(unsigned)(now-started)*.001f;
 if(background==1)drawNativeWaves(w,h,t);
 else if(background==0)drawNativeClouds(w,h,t); // The installed R152 sky route.
 // GuiStore phases: 0 loading, 1 welcome, 2 entering, 3 open carousel.
 // Welcome/entry use the selected background; darken only the open UI.
 if(gui&&at<int>(gui,0x370)==3)drawCarouselDiagonalBackdrop(w,h);
 if(background==3)drawNativeOnlineRibbons(w,h,t);
}
