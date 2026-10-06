#pragma once
static StationActionRect stationOnlineRobotRect(float w,float h,float aspect){
 auto b=stationBottomGameAction(w,h,1);if(b.w<=0||aspect<=0)return {};
 float height=h*.066f,width=height*aspect;if(width>b.w*.8f){width=b.w*.8f;height=width/aspect;}
 return {b.x+(b.w-width)*.5f,b.y-h*.008f-height,width,height};
}
struct StationOnlineRobotPlayback {
 bool playing=false;unsigned last=0,phase=0;
 void press(unsigned now){playing=true;last=now;phase=0;}
 void hide(){playing=false;phase=0;}
 unsigned frame(unsigned now){
  if(!playing)return 0;
  // Accumulate milliseconds modulo the complete original 242-frame cycle.
  // 30 uploads/s samples every other 60fps source frame at normal speed.
  // Small integer state remains bounded even after days or clock rollover.
  unsigned elapsed=now-last;last=now;phase=(phase+(elapsed%12100u)*3u)%12100u;
  unsigned source=phase/50u;return source&~1u;
 }
};
