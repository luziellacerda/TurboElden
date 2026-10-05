
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include "station_info_layout.h"
static int checks=0;
static void check(bool value,const char* what){checks++;if(!value){std::fprintf(stderr,"FAIL %s at check %d\n",what,checks);std::exit(1);}}
static bool close(float a,float b){return std::fabs(a-b)<.02f;}
static void rectangle(const StationInfoRect&r,float width,float height){
 check(std::isfinite(r.x)&&std::isfinite(r.y)&&std::isfinite(r.w)&&std::isfinite(r.h),"finite rectangle");
 check(r.x>=0&&r.y>=0&&r.w>=0&&r.h>=0,"nonnegative rectangle");
 check(r.x+r.w<=width+.02f&&r.y+r.h<=height+.02f,"rectangle stays on screen");
}
static void sample(float w,float h,float left,bool art,bool systems){
 auto p=stationInfoLayout(w,h,left,art,systems);
 rectangle(p.text,w,h);rectangle(p.console,w,h);
 float expectedLeft=left<0?0:left>w*.965f?w*.965f:left;
 check(close(p.text.x,expectedLeft),"clamped left edge");
 check(close(p.text.y,h*(systems?.422f:.454f)),"original text top");
 check(close(p.text.y+p.text.h,h*(systems?.812f:.830f)),"original text bottom");
 check(close(p.console.y,p.text.y)&&close(p.console.h,p.text.h),"shared vertical band");
 if(p.photo){
  check(art&&w>=h*1.25f,"photo only for available landscape art");
  check(p.text.w>=w*.22f-.02f,"minimum readable text width");
  check(close(p.console.w,w*.175f),"existing photo width");
  check(close(p.console.x-p.text.x-p.text.w,w*.018f),"text-photo gap without overlap");
  check(close(p.console.x+p.console.w,w*.965f),"right photo edge");
 }else{
  check(close(p.console.w,0),"no image area when hidden");
  check(close(p.text.w,w*.965f-expectedLeft),"full text width when hidden");
 }
 if(!art||w<h*1.25f)check(!p.photo,"no photo in portrait or without art");
}
int main(){
 constexpr auto landscape=stationInfoLayout(1920,1080,100,true,true);
 static_assert(landscape.photo,"system photo is available at compile time");
 constexpr auto portrait=stationInfoLayout(1080,1920,100,true,true);
 static_assert(!portrait.photo,"portrait must preserve text width");
 const float sizes[][2]={{1920,1080},{1280,720},{2560,1440},{2400,1080},{800,600},{1000,800},{999,800},{1080,1920},{720,1280},{400,400},{320,240},{3840,2160}};
 const float origins[]={-.1f,0.f,.02f,.18f,.33f,.55f,.60f,.77f,.965f,1.f,1.25f};
 for(auto &size:sizes)for(float origin:origins)for(int art=0;art<2;art++)for(int mode=0;mode<2;mode++)
  sample(size[0],size[1],origin*size[0],art!=0,mode!=0);
 for(int w=200;w<=2600;w+=137)for(int h=200;h<=1600;h+=173)for(int mode=0;mode<2;mode++)
  sample((float)w,(float)h,w*.31f,true,mode!=0);
 for(int mode=0;mode<2;mode++){
  auto empty=stationInfoLayout(0,1080,200,true,mode!=0);
  check(!empty.photo&&empty.text.w==0&&empty.text.h==0,"zero width");
  empty=stationInfoLayout(1920,-1,200,true,mode!=0);
  check(!empty.photo&&empty.text.w==0&&empty.text.h==0,"negative height");
  empty=stationInfoLayout(std::numeric_limits<float>::quiet_NaN(),1080,200,true,mode!=0);
  check(!empty.photo&&empty.text.w==0&&empty.text.h==0,"NaN width");
  auto nanleft=stationInfoLayout(1920,1080,std::numeric_limits<float>::quiet_NaN(),true,mode!=0);
  check(nanleft.text.x==0,"NaN origin clamps to screen");
  rectangle(nanleft.text,1920,1080);rectangle(nanleft.console,1920,1080);
 }
 // Four-argument legacy callers retain the games band exactly.
 auto previous=stationInfoLayout(1920,1080,100,true);
 auto games=stationInfoLayout(1920,1080,100,true,false);
 check(close(previous.text.y,games.text.y)&&close(previous.text.h,games.text.h),"legacy call retains games layout");
 std::printf("PASS %d checks: systems and games bands, landscape and portrait, no artwork, narrow text, offscreen origins, no overlap\n",checks);
}
