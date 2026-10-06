// One immutable reference-based transparent artwork, shared by every installed cover.
#include "installed_art_asset.h"
static unsigned installedArtTexture,installedArtProgram;
static void*installedArtContext;
static int installedArtMVP,installedArtSampler,installedArtTime;
static void drawInstalledArtwork(StationInfoRect r){
 if(r.w<=0||r.h<=0||!loadSpaceGL())return;
 auto&g=laserGL;auto&s=spaceGL;void*context=videoGLContext();if(!context)return;
 if(installedArtContext!=context){installedArtContext=context;installedArtTexture=0;installedArtProgram=0;}
 int program=0;g.GetIntegerv(0x8b8d,&program);if(!program)return;
 float matrix[16];g.GetUniformfv(program,at<int>((void*)base,0x3cf4c8),matrix);
 if(!installedArtProgram){
  const char*v="#version 100\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}";
  const char*f="#version 100\nprecision mediump float;uniform sampler2D ribbon;uniform float phase;varying vec2 uv;void main(){vec4 c=texture2D(ribbon,uv);float d=abs((uv.x-uv.y)-(phase*2.8-1.4));float sheen=(1.0-smoothstep(0.0,0.13,d))*clamp(c.r-c.g,0.0,1.0)*0.15;c.rgb=mix(c.rgb,vec3(1.0,0.78,0.76),sheen);gl_FragColor=c;}";
  installedArtProgram=compileSpaceProgram(v,f,true);if(!installedArtProgram)return;
  installedArtMVP=g.GetUniformLocation(installedArtProgram,"MVPMatrix");installedArtSampler=g.GetUniformLocation(installedArtProgram,"ribbon");installedArtTime=g.GetUniformLocation(installedArtProgram,"phase");
 }
 int active=0,texture=0,unpack=4;g.GetIntegerv(0x84e0,&active);s.ActiveTexture(0x84c0);g.GetIntegerv(0x8069,&texture);
 if(!installedArtTexture){
  const U count=(U)installedArtWidth*installedArtHeight;
  unsigned*pixels=(unsigned*)fn<void*(*)(U)>(0x39d9c0)(count*4);
  if(!pixels){s.ActiveTexture(active);return;}
  bool decoded=stationLottieDecode(pixels,(unsigned)count,station_installed_art_rle,0,installedArtWords,installedArtWords);
  if(!decoded){fn<void(*)(void*)>(0x39d820)(pixels);s.ActiveTexture(active);return;}
  static void(*pixelStore)(unsigned,int);if(!pixelStore)pixelStore=(decltype(pixelStore))dlsym(dlopen("libGLESv2.so",2),"glPixelStorei");
  if(pixelStore){g.GetIntegerv(0x0cf5,&unpack);pixelStore(0x0cf5,1);}
  s.GenTextures(1,&installedArtTexture);s.BindTexture(0x0de1,installedArtTexture);
  s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);
  s.TexImage2D(0x0de1,0,0x1908,installedArtWidth,installedArtHeight,0,0x1908,0x1401,pixels);
  if(pixelStore)pixelStore(0x0cf5,unpack);
  fn<void(*)(void*)>(0x39d820)(pixels);
  __android_log_print(4,"StationRibbon","Reference artwork uploaded once %ux%u",installedArtWidth,installedArtHeight);
 }else s.BindTexture(0x0de1,installedArtTexture);
 unsigned color=fn<unsigned(*)(unsigned)>(0x2e3980)(0xffffffffu);
 Vertex q[4]={{r.x,r.y,0,0,color},{r.x,r.y+r.h,0,1,color},{r.x+r.w,r.y,1,0,color},{r.x+r.w,r.y+r.h,1,1,color}};
 g.UseProgram(installedArtProgram);g.UniformMatrix4fv(installedArtMVP,1,0,matrix);s.Uniform1i(installedArtSampler,0);
 g.Uniform1f(installedArtTime,(fn<unsigned(*)()>(0x39e240)()%3800u)/3800.f);
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(q,4,4,5);
 s.BindTexture(0x0de1,texture);s.ActiveTexture(active);g.UseProgram(program);
}
