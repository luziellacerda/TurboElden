#pragma once
#include "station_lottie_assets.h"
#include "station_theme_switch_state.h"
struct StationLottieTexture {unsigned id=0;void*context=nullptr;int frame=-1;};
static StationLottieTexture stationLottieTextures[2];
static unsigned stationLottiePixels[384*216]; // Shared bounded scratch; never per frame allocation.
static bool stationLottieDecode(unsigned*dst,unsigned pixels,const unsigned*rle,unsigned begin,unsigned end){
 unsigned written=0;
 if(end<begin||(end-begin)%2)return false;
 for(unsigned i=begin;i<end;i+=2){unsigned run=rle[i],color=rle[i+1];if(!run||run>pixels-written)return false;for(unsigned j=0;j<run;j++)dst[written++]=color;}
 return written==pixels;
}
static void drawStationLottie(int asset,unsigned frame,StationInfoRect r){
 if(r.w<=0||r.h<=0||!loadSpaceGL()||!ensureStationConsoleProgram())return;
 auto&g=laserGL;auto&s=spaceGL;void*context=videoGLContext();if(!context)return;
 auto&t=stationLottieTextures[asset];if(t.context!=context){t.context=context;t.id=0;t.frame=-1;}
 unsigned width=asset?stationLottie_stars_width:stationLottie_switch_width,height=asset?stationLottie_stars_height:stationLottie_switch_height;
 unsigned frames=asset?stationLottie_stars_frames:stationLottie_switch_frames;if(frame>=frames)frame=frames-1;
 const unsigned*offsets=asset?stationLottie_stars_offsets:stationLottie_switch_offsets;
 const unsigned*data=asset?station_lottie_stars_rle:station_lottie_switch_rle;
 int program=0,active=0,texture=0,unpack=4;g.GetIntegerv(0x8b8d,&program);if(!program)return;
 float matrix[16];g.GetUniformfv(program,at<int>((void*)base,0x3cf4c8),matrix);
 g.GetIntegerv(0x84e0,&active);s.ActiveTexture(0x84c0);g.GetIntegerv(0x8069,&texture);
 static void(*pixelStore)(unsigned,int);static void(*upload)(unsigned,int,int,int,int,int,unsigned,unsigned,const void*);
 if(!pixelStore)pixelStore=(decltype(pixelStore))dlsym(dlopen("libGLESv2.so",2),"glPixelStorei");
 if(!upload)upload=(decltype(upload))dlsym(dlopen("libGLESv2.so",2),"glTexSubImage2D");
 if(t.frame!=(int)frame){
  if(!stationLottieDecode(stationLottiePixels,width*height,data,offsets[frame],offsets[frame+1])){s.ActiveTexture(active);return;}
  if(pixelStore){g.GetIntegerv(0x0cf5,&unpack);pixelStore(0x0cf5,1);}
  if(!t.id){s.GenTextures(1,&t.id);s.BindTexture(0x0de1,t.id);s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);s.TexImage2D(0x0de1,0,0x1908,width,height,0,0x1908,0x1401,stationLottiePixels);}
  else{s.BindTexture(0x0de1,t.id);if(upload)upload(0x0de1,0,0,0,width,height,0x1908,0x1401,stationLottiePixels);else s.TexImage2D(0x0de1,0,0x1908,width,height,0,0x1908,0x1401,stationLottiePixels);}
  if(pixelStore)pixelStore(0x0cf5,unpack);t.frame=(int)frame;
 }else s.BindTexture(0x0de1,t.id);
 unsigned color=fn<unsigned(*)(unsigned)>(0x2e3980)(0xffffffffu);
 Vertex q[4]={{r.x,r.y,0,0,color},{r.x,r.y+r.h,0,1,color},{r.x+r.w,r.y,1,0,color},{r.x+r.w,r.y+r.h,1,1,color}};
 g.UseProgram(stationConsoleProgram);g.UniformMatrix4fv(stationConsoleMVP,1,0,matrix);s.Uniform1i(stationConsoleSampler,0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);
 s.BindTexture(0x0de1,texture);s.ActiveTexture(active);g.UseProgram(program);
}
static StationThemeTransition stationThemeTransition;
static void*stationThemeMainText;static void*stationThemeMainOwner;
static void drawThemeSwitch(void*p,void*matrix,bool settings){
 if(!settings&&(!systemsMode||folderMode||modal(p)))return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);auto target=stationThemeToggleRect(w,h,settings);
 unsigned now=fn<unsigned(*)()>(0x39e240)();unsigned frame=stationThemeTransition.frame(stationThemeId,now);
 fn<void(*)(const void*)>(0x2e5640)(matrix);
 float bh=target.h*1.16f,bw=bh*384.f/216.f; // Transparent source padding keeps the pill inside its touch row.
 drawStationLottie(0,frame,{target.x,target.y+(target.h-bh)*.5f,bw,bh});
 if(!settings){
  if(stationThemeMainOwner!=p){stationThemeMainOwner=p;stationThemeMainText=createInfoText(p,0xE5F1FFff);}
  static int old=-1;static float oldW,oldH;
  if(old!=stationThemeId||oldW!=w||oldH!=h||!at<float>(stationThemeMainText,0x54)){
   old=stationThemeId;oldW=w;oldH=h;setLongText(stationThemeMainText,stationThemeId?"TEMA: AZUL":"TEMA: PRETO");
   place(stationThemeMainText,target.x+bw+h*.013f,target.y,target.w-bw-h*.02f,target.h,.48f,0);
  }
  fn<void(*)(void*,void*)>(0x2d2dc4)(stationThemeMainText,matrix);
 }
}
static StationThemeToggleGesture themeSwitchGesture;
static bool touchThemeSwitch(void*p,const void*event,bool settings){
 if(!settings&&(!systemsMode||folderMode||modal(p)))return false;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);auto r=stationThemeToggleRect(w,h,settings);
 int action=themeSwitchGesture.touch(at<int>((void*)event,0),at<U>((void*)event,8),at<float>((void*)event,0x10),at<float>((void*)event,0x14),r);
 if(action<0)return false;
 if(action==1){bool saved=stationThemeChoose(1-stationThemeId);log(saved?"THEME toggle accepted":"THEME toggle could not save");}
 return true;
}
