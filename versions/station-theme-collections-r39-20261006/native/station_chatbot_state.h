#pragma once
struct StationChatbotPlayback {
 bool playing=false;unsigned started=0;
 void press(unsigned now){playing=true;started=now;}
 unsigned frame(unsigned now){if(!playing)return 0;unsigned elapsed=now-started;if(elapsed>=2867u){playing=false;return 0;}unsigned value=elapsed*30u/1000u;return value>85?85:value;}
};
