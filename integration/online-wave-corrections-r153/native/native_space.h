// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Clouds-only background. Aircraft and stars have no rendering or update work.
static void drawNativeClouds(float,float,float);
static float flightSin(float);
// Shared carousel backdrop: solid black up to the focused cover, then a
// deeper, longer fade behind every carousel cell in every background mode.
// Only the background is shaded; artwork and text are drawn afterward.
static float gameBackdropEase(float t){
 if(t<=.18f)return 0;
 if(t>=1)return 1;
 t=(t-.18f)/.82f;return t*t*(3.f-2.f*t);
}
static void drawCarouselDiagonalBackdrop(float w,float h){
 auto cover=coverSlot(gui,0);
 float anchorX=cover.x+cover.w*.44f,anchorY=cover.y+cover.h*.075f;
 static Vertex strip[754];static unsigned count=0;
 static float lastW=-1,lastH=-1,lastLeft=-1,lastX=-1,lastY=-1;
 if(w!=lastW||h!=lastH||cover.x!=lastLeft||anchorX!=lastX||anchorY!=lastY){
  lastW=w;lastH=h;lastLeft=cover.x;lastX=anchorX;lastY=anchorY;count=0;
  for(int row=0;row<14;row++){
   if(row){strip[count]=strip[count-1];count++;}
   for(int col=0;col<=25;col++){
    float t=col==0?0:(col-1)/24.f;
    // Retain at least 75% black at the right edge, so later cells stand out.
    unsigned color=fn<unsigned(*)(unsigned)>(3029376)((unsigned)(255.f*(1.f-.25f*gameBackdropEase(t))+.5f));
    for(int edge=0;edge<2;edge++){
     float y=h*(row+edge)/14.f,line=anchorX*(h-y)/(h-anchorY);
     if(line<cover.x)line=cover.x; // Entire left lateral space remains black.
     float x=col==0?0:line+(w-line)*t;
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
static unsigned stationOnlineTop(){return stationThemeId==1?0x226FA7ffu:0x000000ffu;}
static unsigned stationOnlineBottom(){return stationThemeId==1?0x509ACCffu:0x07090Dffu;}
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
// The online room's four cubic curves, sampled once per size/theme/system.
// This is a separate selectable mode; the existing animated waves above stay exact.
static float stationOnlineBezier(float a,float b,float c,float d,float t){
 float q=1.f-t;return q*q*q*a+3.f*q*q*t*b+3.f*q*t*t*c+t*t*t*d;
}
static void drawNativeOnlineWaves(float w,float h){
 const StationWavePalette*palette=stationThemeId==1?stationWaveCurrentPalette():nullptr;
 static Vertex strip[270];static unsigned count=0;
 static float lastW=-1,lastH=-1;static int lastTheme=-1;
 static const StationWavePalette*lastPalette=nullptr;
 if(w!=lastW||h!=lastH||stationThemeId!=lastTheme||palette!=lastPalette){
  lastW=w;lastH=h;lastTheme=stationThemeId;lastPalette=palette;count=0;
  static const float centers[4]={.48f,.54f,.60f,.66f};
  static const float amplitudes[4]={.055f,.075f,.095f,.070f};
  static const float strokes[4]={14.f,7.f,2.2f,1.3f};
  static const unsigned darkColors[4]={0x8D969F50u,0x7A858F62u,0xB0B8C08Au,0x8A949D65u};
  static const unsigned lightAlpha[4]={0x5Cu,0x70u,0x9Au,0x72u};
  for(unsigned wave=0;wave<4;wave++){
   unsigned rgba=darkColors[wave];
   if(stationThemeId==1){
    unsigned source=palette&&palette->count?palette->colors[wave<palette->count?wave:palette->count-1]:stationWaveColor((int)wave,nullptr);
    rgba=(source&0xFFFFFF00u)|lightAlpha[wave];
   }
   unsigned color=fn<unsigned(*)(unsigned)>(3029376)(rgba);
   float y=centers[wave]*h,a=amplitudes[wave]*h,half=strokes[wave]*h/1440.f;
   for(int i=0;i<=32;i++){
    float u=i<=16?i/16.f:(i-16)/16.f;
    float x,curve;
    if(i<=16){
     x=stationOnlineBezier(-.05f,.16f,.34f,.52f,u)*w;
     curve=stationOnlineBezier(y+a*.45f,y-a,y-a,y,u);
    }else{
     x=stationOnlineBezier(.52f,.70f,.86f,1.05f,u)*w;
     curve=stationOnlineBezier(y,y+a,y+a*.72f,y-a*.28f,u);
    }
    Vertex top={x,curve-half,0,0,color},bottom={x,curve+half,0,0,color};
    if(wave&&i==0){strip[count]=strip[count-1];count++;strip[count++]=top;}
    strip[count++]=top;strip[count++]=bottom;
   }
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
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,background==3?stationOnlineTop():background==1?stationWaveTop():stationSkyTop(),background==3?stationOnlineBottom():background==1?stationWaveBottom():stationSkyBottom(),false,4,5);
 if(background==3)drawNativeOnlineWaves(w,h);
 else{
  static unsigned started;unsigned now=fn<unsigned(*)()>(0x39e240)();if(!started)started=now;float t=(unsigned)(now-started)*.001f;
  if(background==1)drawNativeWaves(w,h,t);else drawNativeClouds(w,h,t);
 }
 // GuiStore phases: 0 loading, 1 welcome, 2 entering, 3 open carousel.
 // Welcome/entry use the selected background; darken only the open UI.
 if(!gui||at<int>(gui,0x370)!=3)return;
 drawCarouselDiagonalBackdrop(w,h);
}
