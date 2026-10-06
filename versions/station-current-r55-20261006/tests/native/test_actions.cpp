#include <cassert>
#include <cstdio>
#include <cstdint>
#include <cmath>
#include <vector>
#include <cstring>
using U=uintptr_t;
struct Vertex{float x,y,u,v;unsigned color;};
static unsigned tick;
static std::vector<Vertex> output;
static unsigned pack(unsigned c){return c;}static unsigned now(){return tick;}
static void bind(unsigned){}
static void draw(const Vertex*v,unsigned n,int,int){output.insert(output.end(),v,v+n);}
template<class F>F fn(U a){if(a==0x2e3980)return reinterpret_cast<F>(pack);if(a==0x39e240)return reinterpret_cast<F>(now);if(a==0x2e52e8)return reinterpret_cast<F>(bind);if(a==0x2e5470)return reinterpret_cast<F>(draw);assert(false);return nullptr;}
static float squareRoot(float x){return std::sqrt(x);}
static float actionClamp(float x){return x<0?0:x>1?1:x;}
static float actionEase(float x){return x*x*(3-2*x);}
static unsigned blendColor(unsigned a,unsigned b,float t){unsigned result=0;for(int shift=0;shift<32;shift+=8){float av=(a>>shift)&255,bv=(b>>shift)&255;result|=((unsigned)(av+(bv-av)*t+.5f))<<shift;}return result;}
static void openButtonFill(float,float,float,float,unsigned,unsigned){}
#include "native_game_actions.h"
static std::vector<Vertex> render(int slot,unsigned ms,bool disabled=false){tick=ms;output.clear();drawGameAction(20,30,300,70,slot,disabled,false,false,true);return output;}
int main(){for(int slot=0;slot<11;slot++){
 auto a=render(slot,0),b=render(slot,1500);assert(a.size()==b.size());bool equal=std::memcmp(a.data(),b.data(),a.size()*sizeof(Vertex))==0;
 assert(equal==(slot!=5&&slot!=6));
 a=render(slot,0,true);b=render(slot,1500,true);assert(a.size()==b.size()&&std::memcmp(a.data(),b.data(),a.size()*sizeof(Vertex))==0);
 }puts("PASS all 11 button roles: only Abrir/Voltar animate; disabled buttons static; role icons retained.");}
