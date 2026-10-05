using U=unsigned long;using B=unsigned char;
struct Vertex{float x,y,u,v;unsigned color;};
struct alignas(16) NativeMatrix{float values[16];};
struct CoverRect{float x,y,w,h;int index;};
struct StationInfoRect{float x,y,w,h;};
extern bool systemsMode,folderMode;
extern U base;
extern NativeMatrix formationMatrix;
template<class T> static T fn(U address){return reinterpret_cast<T>(base+address);}
template<class T> static T& at(void*p,U offset){return *reinterpret_cast<T*>((B*)p+offset);}
extern bool modal(void*);
extern CoverRect coverSlot(void*,float);
extern void*createInfoText(void*,unsigned);
extern void setLongText(void*,const char*);
extern void fitInfoText(void*,StationInfoRect,float,int);
static float absolute(float x){return x<0?-x:x;}
#include "native_installed_tag.h"
extern "C" void compileInstalledRibbon(void*p){drawInstalledTag(p);}
