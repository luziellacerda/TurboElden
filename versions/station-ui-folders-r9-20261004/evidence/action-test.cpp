#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <vector>
using U=uintptr_t;struct Vertex{float x,y,u,v;unsigned color;};
static unsigned ticks;static std::vector<Vertex> captured;static int draws;
static unsigned clockTick(){return ticks;}static unsigned packed(unsigned c){return c;}
static void bind(unsigned){}static void draw(const Vertex*v,unsigned n,int,int){assert(n==286);captured.assign(v,v+n);draws++;}
template<class T>static T fn(U p){if(p==0x39e240)return (T)clockTick;if(p==0x2e3980)return (T)packed;if(p==0x2e52e8)return (T)bind;assert(p==0x2e5470);return (T)draw;}
static void openButtonFill(float,float,float w,float h,unsigned,unsigned){assert(w>0&&h>0);}
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
static float actionCycle(unsigned now,unsigned period,unsigned offset=0){
 float t=((now+offset)%period)/(float)period;return actionEase(t<.5f?t*2:(1-t)*2);
}
static float actionInset(float yy,float h,float radius){
 float d=yy<radius?radius-yy:yy>h-radius?yy-(h-radius):0;
 return d>0?radius-squareRoot(radius*radius-d*d):0;
}

#include "native_game_actions.h"

int main(){
 unsigned frames[]={0,100,170,420,800,1200,2000,3399,3400,0xfffffff0u};int cases=0;
 for(float width:{120.f,200.f,351.f,600.f})for(float height:{32.f,44.f,70.f})for(unsigned t:frames)for(int slot=0;slot<6;slot++)for(bool disabled:{false,true}){
  ticks=t;drawGameAction(10,20,width,height,slot,disabled,false,false);assert(captured.size()==286);
  for(const auto&v:captured){assert(std::isfinite(v.x)&&std::isfinite(v.y));assert(v.x>=9.99&&v.x<=10+width+.01);assert(v.y>=19.99&&v.y<=20+height+.01);assert((v.color&255)==255);}
  cases++;
 }
 int before=draws;drawGameAction(0,0,0,50,0,false,false,false);assert(before==draws);
 assert(gameActionColor(.3,.4,0,0,false)!=gameActionColor(.3,.4,1300,0,false));
 assert(gameActionColor(.3,.4,0,0,true)==gameActionColor(.3,.4,1300,0,true));
 printf("PASS %d native meshes; clipping, animation, disabled state and zero dimensions\n",cases);
}
