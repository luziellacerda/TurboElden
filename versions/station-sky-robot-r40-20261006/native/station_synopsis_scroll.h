// Pure touch scrolling for a bounded synopsis. Include station_info_layout.h first.
#pragma once

struct StationSynopsisScroll {
 float offset=0,viewportHeight=0,contentHeight=0;
 bool dragging=false,barDrag=false,swallowing=false;
 unsigned long finger=0;
 float lastY=0,grab=0;
};
static inline bool stationSynopsisFinite(float value){return value>=-3.402823466e+38F&&value<=3.402823466e+38F;}
static inline float stationSynopsisMaximum(const StationSynopsisScroll&s){
 return s.viewportHeight>0&&s.contentHeight>s.viewportHeight?s.contentHeight-s.viewportHeight:0;
}
static inline float stationSynopsisClamp(float value,float maximum){
 if(!(value>=0))return 0;return value>maximum?maximum:value;
}
static inline void stationSynopsisRelease(StationSynopsisScroll&s){
 s.dragging=false;s.barDrag=false;s.swallowing=false;s.finger=0;s.lastY=0;s.grab=0;
}
static inline void stationSynopsisCancel(StationSynopsisScroll&s){
 // A cancelled gesture still owns its remaining events. Preserve the finger so
 // its release cannot reach native buttons or the carousel without its down.
 if(s.dragging||s.swallowing){s.dragging=false;s.barDrag=false;s.swallowing=true;s.lastY=0;s.grab=0;}
 else stationSynopsisRelease(s);
}
static inline void stationSynopsisMeasure(StationSynopsisScroll&s,float viewH,float contentH,bool reset){
 if(!stationSynopsisFinite(viewH)||viewH<0)viewH=0;
 if(!stationSynopsisFinite(contentH)||contentH<0)contentH=0;
 bool resized=s.viewportHeight!=viewH||s.contentHeight!=contentH;
 s.viewportHeight=viewH;s.contentHeight=contentH;
 float maximum=stationSynopsisMaximum(s);
 s.offset=reset?0:stationSynopsisClamp(s.offset,maximum);
 if(reset||resized||maximum<=0)stationSynopsisCancel(s);
}
static inline bool stationSynopsisInside(float x,float y,const StationInfoRect&r){
 return stationSynopsisFinite(x)&&stationSynopsisFinite(y)&&stationSynopsisFinite(r.x)&&
  stationSynopsisFinite(r.y)&&stationSynopsisFinite(r.w)&&stationSynopsisFinite(r.h)&&
  r.w>0&&r.h>0&&x>=r.x&&x<=r.x+r.w&&y>=r.y&&y<=r.y+r.h;
}
static inline StationInfoRect stationSynopsisThumb(const StationSynopsisScroll&s,StationInfoRect track){
 if(!stationSynopsisFinite(track.x)||!stationSynopsisFinite(track.y)||!stationSynopsisFinite(track.w)||
    !stationSynopsisFinite(track.h)||track.w<=0||track.h<=0)return {track.x,track.y,0,0};
 float maximum=stationSynopsisMaximum(s);
 if(maximum<=0)return track;
 float height=track.h*(s.viewportHeight/s.contentHeight);
 if(height<24)height=24;
 if(height>track.h)height=track.h;
 return {track.x,track.y+(track.h-height)*(stationSynopsisClamp(s.offset,maximum)/maximum),track.w,height};
}
static inline void stationSynopsisMoveBar(StationSynopsisScroll&s,float y,const StationInfoRect&track){
 StationInfoRect thumb=stationSynopsisThumb(s,track);
 float travel=track.h-thumb.h;
 if(travel>0)s.offset=stationSynopsisClamp((y-track.y-s.grab)/travel,1)*stationSynopsisMaximum(s);
}
static inline bool stationSynopsisTouch(StationSynopsisScroll&s,int type,unsigned long id,float x,float y,
                                      const StationInfoRect&area,const StationInfoRect&track,bool enabled){
 bool available=enabled&&stationSynopsisMaximum(s)>0;
 if(!available)stationSynopsisCancel(s);
 if(s.swallowing){
  if(id!=s.finger)return false;
  // A fresh down starts a new lifecycle, including reuse of an ID after a lost
  // up. Only that new down may decide whether to acquire this finger again.
  if(type==0)stationSynopsisRelease(s);
  else {if(type==2)stationSynopsisRelease(s);return true;}
 }
 if(!available)return false;
 if(type==0){
  // A second finger cannot replace the finger that owns the current gesture.
  if(s.dragging)return id==s.finger;
  bool onTrack=stationSynopsisInside(x,y,track);
  if(!onTrack&&!stationSynopsisInside(x,y,area))return false;
  s.dragging=true;s.barDrag=onTrack;s.finger=id;s.lastY=y;
  if(onTrack){
   StationInfoRect thumb=stationSynopsisThumb(s,track);
   s.grab=stationSynopsisInside(x,y,thumb)?y-thumb.y:thumb.h*.5f;
   stationSynopsisMoveBar(s,y,track);
  }
  return true;
 }
 if(!s.dragging||id!=s.finger)return false;
 // Once captured, the whole gesture belongs to the synopsis, including releases
 // outside its rectangle. This prevents a drag from activating a nearby button.
 if(type==1&&stationSynopsisFinite(y)){
  if(s.barDrag)stationSynopsisMoveBar(s,y,track);
  else s.offset=stationSynopsisClamp(s.offset+s.lastY-y,stationSynopsisMaximum(s));
  s.lastY=y;
 }else if(type==2){stationSynopsisRelease(s);}
 return true;
}
