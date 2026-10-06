#pragma once
static StationActionRect stationOnlineRobotRect(float w,float h,float aspect){
 auto b=stationBottomGameAction(w,h,1);if(b.w<=0||aspect<=0)return {};
 float height=h*.066f,width=height*aspect;if(width>b.w*.8f){width=b.w*.8f;height=width/aspect;}
 return {b.x+(b.w-width)*.5f,b.y-h*.008f-height,width,height};
}
struct StationOnlineRobotPlayback {
 bool playing=false;unsigned started=0;
 void press(unsigned now){playing=true;started=now;}
 unsigned frame(unsigned now){if(!playing)return 0;unsigned elapsed=now-started;if(elapsed>=4034u){playing=false;return 0;}unsigned value=elapsed*60u/1000u;return value>241?241:value;}
};
