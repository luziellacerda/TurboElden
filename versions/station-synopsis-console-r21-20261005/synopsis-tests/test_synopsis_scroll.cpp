#include <cmath>
#include <cstdio>
#include <limits>
#include "../native/station_info_layout.h"
#include "../native/station_synopsis_scroll.h"
static int checks=0,failures=0;
#define CHECK(condition) do { ++checks; if(!(condition)){++failures;std::printf("FAIL line %d: %s\n",__LINE__,#condition);} } while(0)
static bool near(float a,float b){return std::fabs(a-b)<.002f;}
int main(){
 const StationInfoRect area{100,200,280,100},track{390,200,10,100};
 StationSynopsisScroll s;
 stationSynopsisMeasure(s,100,80,true);
 CHECK(!stationSynopsisTouch(s,0,7,200,240,area,track,true));
 CHECK(!s.dragging&&s.offset==0);
 stationSynopsisMeasure(s,100,100,false);
 CHECK(stationSynopsisMaximum(s)==0);
 stationSynopsisMeasure(s,100,500,true);
 CHECK(stationSynopsisMaximum(s)==400);
 CHECK(!stationSynopsisTouch(s,0,7,50,230,area,track,true));
 CHECK(!stationSynopsisTouch(s,1,7,200,230,area,track,true));
 CHECK(!stationSynopsisTouch(s,2,7,200,230,area,track,true));
 CHECK(!s.dragging);
 CHECK(stationSynopsisTouch(s,0,7,200,280,area,track,true));
 CHECK(s.dragging&&!s.barDrag&&s.finger==7);
 CHECK(stationSynopsisTouch(s,1,7,200,230,area,track,true));
 CHECK(near(s.offset,50));
 CHECK(stationSynopsisTouch(s,1,7,200,250,area,track,true));
 CHECK(near(s.offset,30));
 // Cross the visible bounds: text stays clamped and the gesture stays captured.
 CHECK(stationSynopsisTouch(s,1,7,10,-1000,area,track,true));
 CHECK(near(s.offset,400));
 CHECK(stationSynopsisTouch(s,1,7,10,3000,area,track,true));
 CHECK(s.offset==0);
 CHECK(stationSynopsisTouch(s,2,7,600,600,area,track,true));
 CHECK(!s.dragging);
 CHECK(!stationSynopsisTouch(s,1,7,200,230,area,track,true));
 // A second finger cannot alter, cancel or replace the captured stream.
 CHECK(stationSynopsisTouch(s,0,11,200,280,area,track,true));
 CHECK(!stationSynopsisTouch(s,0,12,395,260,area,track,true));
 CHECK(!stationSynopsisTouch(s,1,12,395,210,area,track,true));
 CHECK(!stationSynopsisTouch(s,2,12,395,210,area,track,true));
 CHECK(s.dragging&&s.finger==11&&s.offset==0&&!s.barDrag);
 CHECK(stationSynopsisTouch(s,1,11,200,230,area,track,true));
 CHECK(near(s.offset,50));
 CHECK(stationSynopsisTouch(s,2,11,200,230,area,track,true));
 // Modals and selecting another item cancel a gesture and prevent stale drags.
 CHECK(stationSynopsisTouch(s,0,13,200,280,area,track,true));
 CHECK(stationSynopsisTouch(s,1,13,200,210,area,track,false));
 CHECK(!s.dragging&&s.swallowing&&s.finger==13&&near(s.offset,50));
 CHECK(stationSynopsisTouch(s,1,13,200,200,area,track,true));
 CHECK(near(s.offset,50));
 CHECK(stationSynopsisTouch(s,2,13,600,600,area,track,false));
 CHECK(!s.swallowing&&!s.dragging);
 CHECK(!stationSynopsisTouch(s,2,13,200,240,area,track,true));
 CHECK(stationSynopsisTouch(s,0,14,200,250,area,track,true));
 stationSynopsisMeasure(s,100,500,true);
 CHECK(!s.dragging&&s.offset==0);
 CHECK(s.swallowing&&s.finger==14);
 CHECK(stationSynopsisTouch(s,1,14,200,200,area,track,true));
 CHECK(s.offset==0);
 CHECK(stationSynopsisTouch(s,2,14,600,600,area,track,true));
 CHECK(!s.swallowing);
 // A metadata refresh with unchanged dimensions preserves position and capture.
 CHECK(stationSynopsisTouch(s,0,15,200,280,area,track,true));
 CHECK(stationSynopsisTouch(s,1,15,200,210,area,track,true));
 stationSynopsisMeasure(s,100,500,false);
 CHECK(s.dragging&&near(s.offset,70));
 stationSynopsisMeasure(s,150,200,false);
 CHECK(!s.dragging&&s.swallowing&&near(s.offset,50));
 CHECK(stationSynopsisTouch(s,1,15,200,100,area,track,true));
 CHECK(near(s.offset,50));
 stationSynopsisMeasure(s,200,200,false);
 CHECK(s.swallowing&&s.finger==15);
 CHECK(stationSynopsisTouch(s,2,15,600,600,area,track,true));
 CHECK(!s.swallowing);
 CHECK(s.offset==0&&!stationSynopsisTouch(s,0,1,200,240,area,track,true));
 // Proportional thumb, minimum size, bottom alignment and a short track.
 stationSynopsisMeasure(s,100,500,true);
 StationInfoRect thumb=stationSynopsisThumb(s,track);
 CHECK(near(thumb.h,24)&&near(thumb.y,200));
 s.offset=400;thumb=stationSynopsisThumb(s,track);
 CHECK(near(thumb.y+thumb.h,300));
 StationInfoRect tiny=stationSynopsisThumb(s,{390,200,10,12});
 CHECK(near(tiny.h,12)&&near(tiny.y,200));
 stationSynopsisMeasure(s,100,200,true);thumb=stationSynopsisThumb(s,track);
 CHECK(near(thumb.h,50));
 // Grabbing a thumb keeps the exact initial position; movement is proportional.
 s.offset=40;thumb=stationSynopsisThumb(s,track);
 CHECK(stationSynopsisTouch(s,0,17,395,thumb.y+10,area,track,true));
 CHECK(s.barDrag&&near(s.offset,40));
 CHECK(stationSynopsisTouch(s,1,17,395,thumb.y+25,area,track,true));
 CHECK(near(s.offset,70));
 CHECK(stationSynopsisTouch(s,1,17,1000,10000,area,track,true));
 CHECK(near(s.offset,100));
 CHECK(stationSynopsisTouch(s,2,17,1000,10000,area,track,true));
 // Tapping an empty track moves the thumb toward that point, then permits dragging.
 stationSynopsisMeasure(s,100,500,true);
 CHECK(stationSynopsisTouch(s,0,19,395,280,area,track,true));
 CHECK(s.barDrag&&s.offset>300&&s.offset<400);
 CHECK(stationSynopsisTouch(s,1,19,395,200,area,track,true));
 CHECK(s.offset==0);
 CHECK(stationSynopsisTouch(s,2,19,395,200,area,track,true));
 // Left and right screen regions remain separate in platform and game layouts.
 for(int mode=0;mode<2;++mode){
  StationInfoLayout layout=stationInfoLayout(1920,1080,700,true,mode!=0);
  StationInfoRect view=layout.text,bar{view.x+view.w-12,view.y,12,view.h};view.w-=20;
  stationSynopsisMeasure(s,view.h,view.h*4,true);
  CHECK(!stationSynopsisTouch(s,0,21,100,200,view,bar,true));
  CHECK(!stationSynopsisTouch(s,0,21,900,1080*.93f,view,bar,true));
  CHECK(!stationSynopsisTouch(s,0,21,900,1080*.88f,view,bar,true));
  CHECK(stationSynopsisTouch(s,0,21,view.x+10,view.y+view.h*.75f,view,bar,true));
  CHECK(stationSynopsisTouch(s,1,21,view.x+10,view.y+view.h*.25f,view,bar,true));
  CHECK(near(s.offset,view.h*.5f));
  CHECK(stationSynopsisTouch(s,2,21,view.x+10,view.y+view.h*.25f,view,bar,true));
 }
 // Invalid dimensions or pointer coordinates cannot poison offsets with NaN/Inf.
 float nan=std::numeric_limits<float>::quiet_NaN(),inf=std::numeric_limits<float>::infinity();
 stationSynopsisMeasure(s,nan,500,false);CHECK(s.viewportHeight==0&&s.offset==0);
 stationSynopsisMeasure(s,100,inf,false);CHECK(s.contentHeight==0&&s.offset==0);
 stationSynopsisMeasure(s,-10,-1,false);CHECK(s.viewportHeight==0&&s.contentHeight==0);
 stationSynopsisMeasure(s,100,500,true);
 CHECK(!stationSynopsisTouch(s,0,23,nan,250,area,track,true));
 CHECK(!stationSynopsisTouch(s,0,23,200,inf,area,track,true));
 CHECK(stationSynopsisTouch(s,0,23,200,250,area,track,true));
 CHECK(stationSynopsisTouch(s,1,23,200,nan,area,track,true));
 CHECK(s.offset==0&&s.lastY==250);
 CHECK(stationSynopsisTouch(s,2,23,200,nan,area,track,true));
 CHECK(!s.dragging);
 // Cancellation remains owned across repeated layout resets and other fingers.
 stationSynopsisMeasure(s,100,500,true);
 CHECK(stationSynopsisTouch(s,0,25,200,280,area,track,true));
 CHECK(stationSynopsisTouch(s,1,25,200,260,area,track,true));
 stationSynopsisMeasure(s,0,0,true);
 stationSynopsisMeasure(s,100,500,true);
 CHECK(s.swallowing&&!s.dragging&&s.finger==25&&s.offset==0);
 CHECK(!stationSynopsisTouch(s,0,26,200,280,area,track,true));
 CHECK(!stationSynopsisTouch(s,1,26,200,200,area,track,true));
 CHECK(!stationSynopsisTouch(s,2,26,600,600,area,track,true));
 CHECK(s.swallowing&&s.finger==25);
 CHECK(stationSynopsisTouch(s,1,25,200,200,area,track,true));
 CHECK(s.offset==0);
 CHECK(stationSynopsisTouch(s,2,25,600,600,area,track,true));
 CHECK(!s.swallowing);
 // After the swallowed up, the same ID works normally on the next gesture.
 CHECK(stationSynopsisTouch(s,0,25,200,280,area,track,true));
 CHECK(stationSynopsisTouch(s,1,25,200,250,area,track,true));
 CHECK(near(s.offset,30));
 CHECK(stationSynopsisTouch(s,2,25,200,250,area,track,true));
 // A lost up followed by a reused ID starts a new lifecycle inside or outside.
 CHECK(stationSynopsisTouch(s,0,27,200,280,area,track,true));
 stationSynopsisMeasure(s,100,500,true);
 CHECK(s.swallowing);
 CHECK(!stationSynopsisTouch(s,0,27,600,600,area,track,true));
 CHECK(!s.swallowing&&!s.dragging);
 CHECK(!stationSynopsisTouch(s,2,27,600,600,area,track,true));
 CHECK(stationSynopsisTouch(s,0,27,200,280,area,track,true));
 stationSynopsisMeasure(s,100,500,true);
 CHECK(stationSynopsisTouch(s,0,27,200,260,area,track,true));
 CHECK(s.dragging&&!s.swallowing&&s.finger==27);
 CHECK(stationSynopsisTouch(s,1,27,200,240,area,track,true));
 CHECK(near(s.offset,20));
 CHECK(stationSynopsisTouch(s,2,27,600,600,area,track,true));
 // No gesture started here: modal/layout changes must not acquire any events.
 CHECK(!stationSynopsisTouch(s,0,29,600,600,area,track,true));
 stationSynopsisMeasure(s,150,500,true);
 CHECK(!stationSynopsisTouch(s,1,29,200,240,area,track,false));
 CHECK(!stationSynopsisTouch(s,2,29,200,240,area,track,true));
 CHECK(!s.swallowing&&!s.dragging);
 // Cancelling on UP itself must swallow it, even with no intermediate move.
 stationSynopsisMeasure(s,100,500,true);
 CHECK(stationSynopsisTouch(s,0,31,200,280,area,track,true));
 CHECK(stationSynopsisTouch(s,2,31,600,600,area,track,false));
 CHECK(!s.swallowing&&!s.dragging&&s.offset==0);
 // A thumb gesture obeys the same cancel contract and cannot move after reset.
 CHECK(stationSynopsisTouch(s,0,33,395,280,area,track,true));
 CHECK(s.barDrag&&s.offset>0);
 stationSynopsisMeasure(s,100,500,true);
 CHECK(s.swallowing&&!s.barDrag&&s.offset==0);
 CHECK(stationSynopsisTouch(s,1,33,395,280,area,track,true));
 CHECK(s.offset==0);
 CHECK(stationSynopsisTouch(s,2,33,600,600,area,track,true));
 CHECK(!s.swallowing);
 // Same ID starts a fresh native gesture while unavailable; do not swallow it.
 CHECK(stationSynopsisTouch(s,0,35,200,280,area,track,true));
 CHECK(stationSynopsisTouch(s,1,35,200,260,area,track,false));
 CHECK(s.swallowing);
 CHECK(!stationSynopsisTouch(s,0,35,200,260,area,track,false));
 CHECK(!s.swallowing&&!s.dragging);
 CHECK(!stationSynopsisTouch(s,2,35,200,240,area,track,false));
 std::printf("%d checks; %d failures\n",checks,failures);
 return failures?1:0;
}
