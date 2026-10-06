#pragma once
#include "station_online_robot_state.h"
static StationOnlineRobotPlayback stationOnlineRobotPlayback;
static void drawOnlineRobot(void*p,void*matrix){
 static bool wasVisible=false;static void*owner;
 bool visible=!systemsMode&&!folderMode&&!modal(p)&&at<int>(p,0x370)>=2;
 if(!visible){wasVisible=false;stationOnlineRobotPlayback.hide();return;}
 unsigned now=fn<unsigned(*)()>(0x39e240)();
 if(!wasVisible||owner!=p){wasVisible=true;owner=p;stationOnlineRobotPlayback.press(now);}
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 auto r=stationOnlineRobotRect(w,h,(float)stationLottie_online_width/stationLottie_online_height);
 fn<void(*)(const void*)>(0x2e5640)(matrix);
 drawStationLottie(3,stationOnlineRobotPlayback.frame(now),{r.x,r.y,r.w,r.h});
}
