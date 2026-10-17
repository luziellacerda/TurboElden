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
// Room reference: StationWaveBackground fills three sinusoidal ribbons from
// their moving upper edge to the bottom with a vertical gradient. The main
// screen uses that same geometry with the requested fourth ribbon. Colors come
// from the current console; palettes shorter than four wrap instead of
// repeating their last color. This mode adds no timer, heap work or cloud pass.
static unsigned stationOnlineRibbonMix(unsigned a,unsigned b,float t){
 if(t<=0)return a;if(t>=1)return b;
 unsigned rgba=0;
 for(int shift=0;shift<=24;shift+=8){
  float first=(float)((a>>shift)&255u),last=(float)((b>>shift)&255u);
  rgba|=(unsigned)(first+(last-first)*t+.5f)<<shift;
 }
 return rgba;
}
static unsigned stationOnlineRibbonDim(unsigned rgba,unsigned alpha){
 unsigned red=((rgba>>24)&255u)*55u/100u;
 unsigned green=((rgba>>16)&255u)*55u/100u;
 unsigned blue=((rgba>>8)&255u)*55u/100u;
 return red<<24|green<<16|blue<<8|alpha;
}
static void drawNativeOnlineRibbons(float w,float h,float t){
 const StationWavePalette*palette=stationWaveCurrentPalette();
 static const unsigned blueTop[4]={0x29ACFF60u,0x5782FF58u,0x38D9E850u,0x4BA7DC48u};
 static const unsigned blueBottom[4]={0x33509B28u,0x23357324u,0x2087A720u,0x2757751Cu};
 static const unsigned darkTop[4]={0x3B4B5960u,0x38455058u,0x616B7450u,0x55636C48u};
 static const unsigned darkBottom[4]={0x1A212828u,0x1A202724u,0x30384020u,0x27333D1Cu};
 static const unsigned topAlpha[4]={0x60u,0x58u,0x50u,0x48u};
 static const unsigned bottomAlpha[4]={0x28u,0x24u,0x20u,0x1Cu};
 static Vertex strip[206];unsigned count=0;
 float phase=t*.35f;
 for(unsigned layer=0;layer<4;layer++){
  unsigned top=stationThemeId==1?blueTop[layer]:darkTop[layer];
  unsigned bottom=stationThemeId==1?blueBottom[layer]:darkBottom[layer];
  if(palette&&palette->count){
   unsigned source=palette->colors[layer%palette->count];
   top=(source&0xFFFFFF00u)|topAlpha[layer];
   bottom=stationOnlineRibbonDim(source,bottomAlpha[layer]);
  }
  unsigned bottomColor=fn<unsigned(*)(unsigned)>(3029376)(bottom);
  for(int point=0;point<=24;point++){
   float u=point/24.f;
   float curve=flightSin(u*6.2831853f+phase+layer*1.15f)*.055f+
               flightSin(u*3.14159265f+phase*.7f+layer*.6f)*.035f;
   float x=w*u,y=h*(.59f+layer*.055f+curve);
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
