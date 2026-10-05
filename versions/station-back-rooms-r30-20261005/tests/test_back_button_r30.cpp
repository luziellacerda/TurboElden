#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <initializer_list>
#include "station_bottom_action_layout.h"
static int checks;
static void check(bool ok){++checks;if(!ok){std::printf("FAIL %d\n",checks);std::exit(1);}}
int main(){
 for(float h:{360.f,480.f,720.f,1080.f,1440.f,2160.f})for(float ratio:{1.333333f,1.6f,1.777778f,2.f,2.166667f,2.4f}){
  float w=h*ratio,cw=h*.665f,bh=h*.094f;
  auto open=stationCollectionAction(w*.035f,h*.851f,cw,bh,false),back=stationCollectionAction(w*.035f,h*.851f,cw,bh,true);
  check(open.x+open.w<back.x);check(back.x+back.w<=w*.035f+cw+.01f);
  check(open.h==back.h&&open.y==back.y);check(back.y+back.h<h);
  // Native label reserves 0.98h for its icon and 0.16h trailing padding.
  check(back.w-bh*1.14f>bh*1.65f);check(open.w-bh*1.14f>bh*1.65f);
  check(back.w>stationCompactActionRect({0,0,cw*.31f,bh}).w);
 }
 std::printf("PASS %d collection button bounds, text space and nonoverlap\n",checks);
}
