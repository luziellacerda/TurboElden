#pragma once
struct StationLottieOnce {
 bool playing=false;unsigned started=0;
 void press(unsigned now){playing=true;started=now;}
 unsigned frame(unsigned now){
  if(!playing)return 0;
  unsigned elapsed=now-started;
  if(elapsed>=3003u){playing=false;return 0;}
  return elapsed*90u/3003u;
 }
};
