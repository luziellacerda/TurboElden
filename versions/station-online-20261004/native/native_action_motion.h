// Turborama adaptation of the animated apk-download-cta reference, not the static login submit.
// Existing native render loop only: no Java overlay, textures, FBO, decoder or background timer.
static float actionClamp(float v){return v<0?0:v>1?1:v;}
static float actionEase(float v){v=actionClamp(v);return v*v*(3-2*v);}
static float actionCycle(unsigned now,unsigned period,unsigned offset=0){
 float t=((now+offset)%period)/(float)period;return actionEase(t<.5f?t*2:(1-t)*2);
}
struct ActionMotion {float shift,center,sweep,pulse;};
static ActionMotion actionMotion(unsigned now){
 (void)now;
 // Static face: no traveling sheen, no color wave, no pulse.
 return {.28f,0.f,0.f,0.f};
}
static unsigned animatedActionColor(float nx,float ny,float aspect,const ActionMotion&m,bool pause,bool exit){
 unsigned color;
 if(pause){
  unsigned a=exit?0x652135ff:0x0D442Eff,b=exit?0xA33349ff:0x147C4Fff;
  color=blendColor(a,b,actionClamp(nx*.6f+ny*.15f+m.shift*.25f));
 }else{
  const unsigned colors[]={0x075139ff,0x12BD80ff,0x65FF79ff,0xB4FF55ff,0xD5FFB6ff};
  const float stops[]={0,.27f,.52f,.78f,1};
  float t=actionClamp((nx+1.3f*m.shift)/2.3f);int index=0;
  while(index<3&&t>stops[index+1])index++;
  color=blendColor(colors[index],colors[index+1],(t-stops[index])/(stops[index+1]-stops[index]));
 }
 float diagonal=nx+(ny-.5f)*aspect*.325f;
 float light=actionClamp(1-absolute(diagonal-m.center)/.17f);
 light=actionEase(light)*m.sweep*(pause?.22f:1.f);
 return blendColor(color,0xF5FFF2ff,light);
}
static float actionInset(float yy,float h,float radius){
 float d=yy<radius?radius-yy:yy>h-radius?yy-(h-radius):0;
 return d>0?radius-squareRoot(radius*radius-d*d):0;
}
static void animatedActionFace(float x,float y,float w,float h,const ActionMotion&m,bool pause,bool exit){
 if(w<=0||h<=0)return;
 // Eight bands sample the tilted moving shine and clip it to the rounded face.
 // Degenerate joins keep this a single native triangle-strip draw.
 Vertex v[670];unsigned count=0;float radius=h*.20f;
 fn<void(*)(unsigned)>(3035880)(0);
 for(int row=0;row<8;row++){
  float yy[2]={h*row/8,h*(row+1)/8};
  float inset[2]={actionInset(yy[0],h,radius),actionInset(yy[1],h,radius)};
  if(row){v[count]=v[count-1];count++;v[count++]={x+inset[0],y+yy[0],0,0,0};}
  for(int col=0;col<=40;col++)for(int side=0;side<2;side++){
   float xx=inset[side]+(w-2*inset[side])*col/40;
   unsigned rgba=animatedActionColor(xx/w,yy[side]/h,h/w,m,pause,exit);
   v[count++]={x+xx,y+yy[side],0,0,fn<unsigned(*)(unsigned)>(3029376)(rgba)};
  }
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(v,count,4,5);
}
static void actionSpark(float x,float y,float h,float level){
 unsigned a=(unsigned)(80+175*level);float size=h*(.025f+.018f*level);
 openButtonFill(x-size*2,y-size*2,size*4,size*4,0xB7FFB522,0xB7FFB522);
 rect(x-size*1.5f,y-size*.18f,size*3,size*.36f,0xF4FFDB00|a);
 rect(x-size*.18f,y-size*1.5f,size*.36f,size*3,0xF4FFDB00|a);
}
static void drawPrimaryOpen(void*p,float x,float y,float w,float h){
 ActionMotion m=actionMotion(0);
 bool focused=at<float>(p,0x1c4)>.08f;
 float pad=h*.035f,edge=h*.016f;
 openButtonFill(x-pad,y-pad,w+2*pad,h+2*pad,0x45F26B28,0x45F26B28);
 openButtonFill(x-edge,y-edge,w+2*edge,h+2*edge,focused?0xF0FFE0ff:0xBDFFBDdd,0x34D399bb);
 animatedActionFace(x,y,w,h,m,false,false);
 openButtonChevron(x+w-h*.61f,y+h*.50f,h*.135f,0x06361Dff);
}
#include "native_pause_menu.h"
