// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Hyperspace is procedural geometry rendered by the existing native OpenGL renderer.
// A true 3D spacecraft is rendered by native_space3d.h; the rejected PNG animation is retired.
#include "native_flight.h"
static void drawSpace3D(float,float,float);
static void drawNativeClouds(float,float,float);
static unsigned spaceRandom(unsigned&state){state=state*1664525u+1013904223u;return state;}
static float spaceUnit(unsigned&state){return (spaceRandom(state)>>8)*(1.f/16777216.f);}
static float spaceSin(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"sinf");return f?f(x):0;}
static float spaceCos(float x){static float(*f)(float);if(!f)f=(float(*)(float))dlsym(dlopen("libm.so",2),"cosf");return f?f(x):1;}
static void drawNativeSpace(float w,float h){
 if(w<=0||h<=0)return;
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,0x020604ff,0x060A08ff,false,4,5);
 static unsigned started;unsigned now=fn<unsigned(*)()>(0x39e240)();if(!started)started=now;float t=(unsigned)(now-started)*.001f;
 drawNativeClouds(w,h,t);
 NativeFlight flight=nativeFlight(t,w/h);
 float diagonalC=flightCos(flightDiagonal),diagonalS=flightSin(flightDiagonal);
 float vx=w*flightVanishingX,vy=h*flightVanishingY;
 Vertex stars[1200];unsigned count=0,seed=0x54555242;
 // Stars move away from the vanishing point, the visual motion of forward flight.
 for(int i=0;i<180;i++){
  float worldX=(spaceUnit(seed)*2-1)*10.f,worldY=(spaceUnit(seed)*2-1)*6.f;
  constexpr float nearZ=1.2f,farZ=20.f,span=farZ-nearZ;
  float progress=spaceUnit(seed)+flight.travel/span;progress-=(int)progress;
  float depth=farZ-progress*span,previousDepth=depth+.9f*.42f;
  // Match the clouds: focal length 2.9, the same forward world travel, and
  // the same diagonal pixel basis. Depth never runs backwards or reverses.
  float dx=(diagonalC*worldX-diagonalS*worldY)*h*1.45f;
  float dy=(diagonalS*worldX+diagonalC*worldY)*h*1.45f;
  float length=squareRoot(dx*dx+dy*dy);if(length<1)continue;
  float x=vx+dx/depth,y=vy+dy/depth;
  if(x<0||x>w||y<0||y>h)continue;
  float tx=vx+dx/previousDepth,ty=vy+dy/previousDepth;
  float z=progress,half=(.4f+z*1.05f)*h/1080.f,nx=-dy/length*half,ny=dx/length*half;
  float fade=flightClamp(progress/.06f)*flightClamp((1.f-progress)/.025f);
  unsigned alpha=(unsigned)((24+z*105)*fade);if(y>h*.43f&&y<h*.81f&&x>w*.33f)alpha=alpha/2;
  unsigned head=fn<unsigned(*)(unsigned)>(3029376)(0xb9efd000|alpha),end=fn<unsigned(*)(unsigned)>(3029376)(0x25894A00|(alpha/5));
  Vertex q[4]={{tx+nx,ty+ny,0,0,end},{tx-nx,ty-ny,0,0,end},{x+nx,y+ny,0,0,head},{x-nx,y-ny,0,0,head}};
  if(count){stars[count]=stars[count-1];count++;stars[count++]=q[0];}
  for(int j=0;j<4;j++)stars[count++]=q[j];
 }
 fn<void(*)(unsigned)>(3035880)(0);
 if(count)fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(stars,count,4,5);
 drawSpace3D(w,h,t);
}
