#pragma once
struct StationSearchBox {float x,y,w,h;};
static StationSearchBox stationSearchActionBox(float w,float h,bool editor,int action){
 if(editor)return action==1?StationSearchBox{w*.18f,h*.382f,w*.28f,h*.061f}:StationSearchBox{w*.50f,h*.382f,w*.32f,h*.061f};
 return action==1?StationSearchBox{w*.375f,h*.54f,w*.25f,h*.082f}:StationSearchBox{w*.655f,h*.54f,w*.25f,h*.082f};
}
struct StationSearchGesture {
 int armed=0;U finger=0;bool editor=false;float startX=0,startY=0;
 int touch(unsigned type,U id,float x,float y,float w,float h,bool editing,bool enabled){
  if(!enabled){armed=0;return -1;}
  auto hit=[&](int a){auto b=stationSearchActionBox(w,h,editing,a);return x>=b.x&&x<=b.x+b.w&&y>=b.y&&y<=b.y+b.h;};
  if(type==0){if(armed)return 0;armed=hit(1)?1:hit(2)?2:0;if(!armed)return -1;finger=id;editor=editing;startX=x;startY=y;return 0;}
  if(!armed)return -1;if(finger!=id)return 0;
  if(editing!=editor||(type!=1&&type!=2)||(type==1&&(x-startX>h*.02f||startX-x>h*.02f||y-startY>h*.02f||startY-y>h*.02f))){armed=0;return 0;}
  if(type==2){int result=hit(armed)?armed:0;armed=0;return result;}
  return 0;
 }
};
