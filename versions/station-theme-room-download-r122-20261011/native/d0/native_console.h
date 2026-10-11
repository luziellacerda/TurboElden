// One local console texture per hardware family; reused by its regional lists.
// Included after native_system_video720.h to reuse GL context/state utilities.
#include "console_assets.h"
#include "station_console_fit.h"
struct StationConsoleTexture {unsigned id;void*context;StationConsoleCrop crop;};
static StationConsoleTexture stationConsoleTextures[sizeof(stationConsoleAssets)/sizeof(stationConsoleAssets[0])];
static unsigned stationConsoleProgram;static int stationConsoleMVP,stationConsoleSampler;static void*stationConsoleProgramContext;static bool stationConsoleProgramFailed;
static bool ensureStationConsoleProgram(){
 void*context=videoGLContext();if(!context)return false;
 if(stationConsoleProgramContext!=context){stationConsoleProgramContext=context;stationConsoleProgram=0;stationConsoleProgramFailed=false;}
 if(stationConsoleProgramFailed)return false;
 if(stationConsoleProgram&&laserGL.IsProgram(stationConsoleProgram))return true;
 const char*vertex="#version 100\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}";
 const char*fragment="#version 100\nprecision mediump float;uniform sampler2D consoleArt;varying vec2 uv;void main(){gl_FragColor=texture2D(consoleArt,uv);}";
 stationConsoleProgram=compileSpaceProgram(vertex,fragment,true);
 if(!stationConsoleProgram){stationConsoleProgramFailed=true;return false;}
 stationConsoleMVP=laserGL.GetUniformLocation(stationConsoleProgram,"MVPMatrix");
 stationConsoleSampler=laserGL.GetUniformLocation(stationConsoleProgram,"consoleArt");
 return true;
}
#include "station_console_keys.h"
static int stationConsoleIndex(const char*key){
 const char*canonical=stationConsoleKey(key);if(!canonical)return -1;
 for(unsigned i=0;i<sizeof(stationConsoleAssets)/sizeof(stationConsoleAssets[0]);i++)
  if(strcmp(stationConsoleAssets[i].key,canonical)==0)return (int)i;
 return -1;
}
static bool stationConsoleAvailable(const char*key){return stationConsoleIndex(key)>=0;}
static void drawStationConsole(void*p,const char*key,const StationInfoRect&slot){
 if(modal(p)||slot.w<=0||slot.h<=0)return;
 int index=stationConsoleIndex(key);if(index<0||!loadSpaceGL())return;
 auto&asset=stationConsoleAssets[index];auto&texture=stationConsoleTextures[index];
 void*context=videoGLContext();if(!context)return;
 if(texture.context!=context){texture.id=0;texture.context=context;}
 auto&g=laserGL;auto&s=spaceGL;
 int originalProgram=0;g.GetIntegerv(0x8b8d,&originalProgram);if(!originalProgram||!ensureStationConsoleProgram())return;
 float matrix[16];g.GetUniformfv((unsigned)originalProgram,at<int>((void*)base,0x3cf4c8),matrix);
 int originalActive=0,originalTexture=0,originalUnpack=0;
 g.GetIntegerv(0x84e0,&originalActive);s.ActiveTexture(0x84c0);g.GetIntegerv(0x8069,&originalTexture);
 if(!texture.id){
  texture.crop=stationConsoleBounds(asset.rgba,asset.width,asset.height);
  s.GenTextures(1,&texture.id);s.BindTexture(0x0de1,texture.id);
  s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);
  s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);
  // RGBA rows are width*4: valid under all standard unpack alignments up to4.
  // The original renderer uses alignment4, explicitly preserve actual state.
  static void(*pixelStore)(unsigned,int);if(!pixelStore)pixelStore=(void(*)(unsigned,int))dlsym(dlopen("libGLESv2.so",2),"glPixelStorei");
  if(pixelStore){g.GetIntegerv(0x0cf5,&originalUnpack);pixelStore(0x0cf5,1);}
  s.TexImage2D(0x0de1,0,0x1908,asset.width,asset.height,0,0x1908,0x1401,asset.rgba);
  if(pixelStore)pixelStore(0x0cf5,originalUnpack);
  __android_log_print(4,"TurboCarousel","CONSOLE texture prepared %s %ux%u",asset.key,asset.width,asset.height);
 }else s.BindTexture(0x0de1,texture.id);
 // Fit actual visible hardware, not the transparent 512-square padding.
 auto fitted=stationConsoleFit(slot,texture.crop,asset.width,asset.height);
 unsigned color=fn<unsigned(*)(unsigned)>(0x2e3980)(0xffffffffu);
 Vertex q[4]={{fitted.x,fitted.y,fitted.u0,fitted.v0,color},
              {fitted.x,fitted.y+fitted.h,fitted.u0,fitted.v1,color},
              {fitted.x+fitted.w,fitted.y,fitted.u1,fitted.v0,color},
              {fitted.x+fitted.w,fitted.y+fitted.h,fitted.u1,fitted.v1,color}};
 g.UseProgram(stationConsoleProgram);g.UniformMatrix4fv(stationConsoleMVP,1,0,matrix);
 s.Uniform1i(stationConsoleSampler,0);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);
 s.BindTexture(0x0de1,(unsigned)originalTexture);s.ActiveTexture((unsigned)originalActive);g.UseProgram((unsigned)originalProgram);
}
