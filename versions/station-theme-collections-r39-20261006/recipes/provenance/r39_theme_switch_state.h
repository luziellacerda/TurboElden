#pragma once
static StationThemeRect stationThemeToggleRect(float w,float h,bool settings){return settings?StationThemeRect{w*.323f,h*.147f,w*.205f,h*.075f}:StationThemeRect{w*.035f,h*.949f,w*.245f,h*.048f};}
struct StationThemeToggleGesture {
 bool pressed=false,cancelled=false;unsigned long finger=0;
 int touch(int type,unsigned long id,float x,float y,StationThemeRect r){
  if(type==0){if(pressed)return 0;if(!stationThemeContains(r,x,y))return -1;pressed=true;cancelled=false;finger=id;return 0;}
  if(!pressed)return -1;if(id!=finger)return 0;
  if(type!=1&&type!=2){pressed=false;return 0;}
  if(!stationThemeContains(r,x,y))cancelled=true;
  if(type==2){pressed=false;return cancelled?0:1;}return 0;
 }
};
struct StationThemeTransition {
 bool ready=false;int target=-1;float origin=0,current=0;unsigned started=0;
 unsigned frame(int theme,unsigned now){
  int end=theme==1?0:85;
  if(!ready){ready=true;target=end;origin=current=(float)end;started=now;return end;}
  float elapsed=(now-started)*.060f;
  current=origin<target?((origin+elapsed)<target?origin+elapsed:(float)target):((origin-elapsed)>target?origin-elapsed:(float)target);
  if(end!=target){origin=current;target=end;started=now;}
  return (unsigned)(current+.5f);
 }
};
