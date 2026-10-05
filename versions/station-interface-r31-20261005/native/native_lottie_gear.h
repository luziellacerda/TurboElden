// Exact Gear 3 Lottie geometry and easing, sampled at the source frame rate.
#include "lottie_gear3_data.h"
static void drawLottieGearHook(void*p,float cx,float cy,float radius,unsigned color){
 if(!skinTop){fn<void(*)(void*,float,float,float,unsigned)>(0x221854)(p,cx,cy,radius,color);return;}
 unsigned tick=fn<unsigned(*)()>(0x39e240)();unsigned frame=(tick%3003u)*90u/3003u;
 float co=gear3Frames[frame][0],si=gear3Frames[frame][1];
 float scale=radius/24.729749435f;
 unsigned packed=fn<unsigned(*)(unsigned)>(0x2e3980)(0xB78E3100u|(color&255));
 Vertex vertices[sizeof(gear3Outer)/sizeof(gear3Outer[0])];
 fn<void(*)(unsigned)>(0x2e52e8)(0);
 for(int layer=0;layer<2;layer++){
  const float(*data)[2]=layer?gear3Inner:gear3Outer;
  unsigned count=layer?sizeof(gear3Inner)/sizeof(gear3Inner[0]):sizeof(gear3Outer)/sizeof(gear3Outer[0]);
  for(unsigned i=0;i<count;i++){
   float x=data[i][0],y=data[i][1];if(!layer){float xx=x*co-y*si;y=x*si+y*co;x=xx;}
   vertices[i]={cx+x*scale,cy+y*scale,0,0,packed};
  }
  fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(vertices,count,4,5);
 }
}
