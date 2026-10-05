#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <vector>
#include <cstring>
using U=uintptr_t;using B=unsigned char;
struct Vertex{float x,y,u,v;unsigned color;};
static unsigned ticks;static bool record;static FILE*out;static float left,top,width,height;static int draws;
static unsigned clockTick(){return ticks;}static unsigned packed(unsigned c){return c;}
static void bind(unsigned){}
static void draw(const Vertex*v,unsigned n,int,int){
 assert(n>0&&n<=382);draws++;
 if(record)fprintf(out,"%u",n);
 for(unsigned i=0;i<n;i++){
  assert(std::isfinite(v[i].x)&&std::isfinite(v[i].y));
  assert(v[i].x>=left-.02f&&v[i].x<=left+width+.02f&&v[i].y>=top-.02f&&v[i].y<=top+height+.02f);
  assert((v[i].color&255)==255);
  if(record)fprintf(out," %.4f %.4f %u",v[i].x,v[i].y,v[i].color);
 }
 if(record)fprintf(out,"\n");
}
template<class T>static T fn(U p){if(p==0x39e240)return (T)clockTick;if(p==0x2e3980)return (T)packed;if(p==0x2e52e8)return (T)bind;assert(p==0x2e5470);return (T)draw;}
template<class T>static T& at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
static float absolute(float n){return n<0?-n:n;}
static float squareRoot(float value){
 if(value<=0)return 0;float root=value>1?value:1;
 for(int i=0;i<12;i++)root=(root+value/root)*.5f;return root;
}
static unsigned blendColor(unsigned a,unsigned b,float t){
 unsigned result=0;for(int shift=0;shift<32;shift+=8){float av=(a>>shift)&255,bv=(b>>shift)&255;result|=((unsigned)(av+(bv-av)*t+.5f))<<shift;}return result;
}
static float actionClamp(float v){return v<0?0:v>1?1:v;}
static float actionEase(float v){v=actionClamp(v);return v*v*(3-2*v);}
static void openButtonFill(float x,float y,float w,float h,unsigned top,unsigned bottom){
 float r=h*.24f;Vertex strip[36];unsigned count=0;
 fn<void(*)(unsigned)>(3035880)(0);
 for(int half=0;half<2;half++)for(int i=0;i<=8;i++){
  float local=r*i/8,yy=half?h-r+local:local,dy=half?local:r-local;
  float inset=r-squareRoot(r*r-dy*dy);
  unsigned c=fn<unsigned(*)(unsigned)>(3029376)(blendColor(top,bottom,yy/h));
  strip[count++]={x+inset,y+yy,0,0,c};strip[count++]={x+w-inset,y+yy,0,0,c};
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);
}

#include "native_game_actions.h"
struct CoverRect{float x,y,w,h;int index;}; static bool systemsMode=true;
static CoverRect coverSlot(void*p,float d){
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 float bigH=h*(systemsMode?.665f:.740f),bigW=systemsMode?bigH:bigH*.72f,bigX=w*(systemsMode?.035f:.025f),top=h*(systemsMode?.135f:.115f);
 float stripX=systemsMode?w*.365f:bigX+bigW+w*.022f,gap=w*.012f,smallW=(w*.965f-stripX-5*gap)/6,smallH=systemsMode?smallW:smallW/.72f;
 CoverRect result{};result.y=top;
 if(d<0){result.x=bigX+d*(bigW+w*.06f);result.w=bigW;result.h=bigH;}
 else if(d<1){float t=d*d*(3-2*d);result.x=bigX+(stripX-bigX)*t;result.w=bigW+(smallW-bigW)*t;result.h=bigH+(smallH-bigH)*t;}
 else {result.x=stripX+(d-1)*(smallW+gap);result.w=smallW;result.h=smallH;}
 return result;
}

int main(int argc,char**argv){
 unsigned frames[]={0,300,800,1900,3600,4199,4200,0xfffffff0u};int cases=0;
 for(float w:{180.f,288.f,351.f,600.f})for(float h:{32.f,44.f,70.f,102.f})for(unsigned t:frames)for(int slot=0;slot<8;slot++)for(bool disabled:{false,true})for(bool confirm:{false,true}){
  left=10;top=20;width=w;height=h;ticks=t;drawGameAction(left,top,w,h,slot,disabled,false,confirm);cases++;
 }
 int before=draws;drawGameAction(0,0,0,50,0,false,false,false);assert(before==draws);
 for(int i=0;i<6;i++)for(int j=i+1;j<6;j++)assert(gameActionPalette(i,false,false).accent!=gameActionPalette(j,false,false).accent);
 alignas(8) B ui[256]={};int geometry=0;
 for(float sw:{1280.f,1920.f,2340.f,2560.f})for(float sh:{720.f,1080.f,1440.f}){
  at<float>(ui,0x54)=sw;at<float>(ui,0x58)=sh;
  for(int i=-20;i<=132;i++){auto r=coverSlot(ui,i/20.f);assert(std::abs(r.w-r.h)<.01);geometry++;}
 }
 printf("PASS %d action meshes: all vertices inside, 8 icons, 6 distinct colors, disabled/confirming states; %d square carousel slots\n",cases,geometry);
 if(argc>1){out=fopen(argv[1],"w");assert(out);record=true;
  for(int i=0;i<8;i++){left=24+(i%4)*374;top=24+(i/4)*140;width=350;height=90;ticks=1400;drawGameAction(left,top,width,height,i,false,false,i==3);}
  fclose(out);
 }
}
