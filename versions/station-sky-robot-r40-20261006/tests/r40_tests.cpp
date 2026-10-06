#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <set>
using U=uintptr_t;using B=unsigned char;
template<class T>T&at(void*p,U n){return *reinterpret_cast<T*>((B*)p+n);}
static unsigned checks=0,now=0,draws=0,lastFrame=0;static bool systemsMode=false,folderMode=false,covered=false;
static bool modal(void*){return covered;}
static unsigned tick(){return now;}static void matrix(const void*){}
template<class T>T fn(U a){if(a==0x39e240)return (T)tick;if(a==0x2e5640)return (T)matrix;abort();}
#include "station_theme_palette.h"
#include "station_theme_switch_state.h"
#include "station_bottom_action_layout.h"
static const unsigned stationLottie_online_width=138,stationLottie_online_height=150;
static void drawStationLottie(int id,unsigned frame,StationActionRect r){if(id!=3||frame>=242||r.w<=0||r.h<=0)abort();draws++;lastFrame=frame;}
#include "native_online_robot.h"
static void check(bool b){checks++;if(!b){printf("FAILED %u\n",checks);abort();}}
int main(){
 unsigned seed=13;
 for(int theme:{0,1}){stationThemeId=theme;for(int i=0;i<20000;i++){seed=seed*1664525u+1013904223u;check(stationThemeColor(seed)==seed);}}
 stationThemeId=0;check(stationSkyTop()==0x020604ff&&stationSkyBottom()==0x060A08ff);stationThemeId=1;check(stationSkyTop()==0x0B4B83ff&&stationSkyBottom()==0x267CBBff);
 for(float w:{640.f,1280.f,1920.f,2340.f})for(float h:{360.f,720.f,1080.f}){
  auto r=stationThemeToggleRect(w,h,false);check(r.x>w*.7f&&r.x+r.w<=w*.976f&&r.y+r.h<=h);
  StationThemeToggleGesture gesture;check(gesture.touch(0,1,w*.05f,h*.97f,r)==-1);float x=r.x+r.w*.9f,y=r.y+r.h*.5f;check(gesture.touch(0,1,x,y,r)==0);check(gesture.touch(2,1,x,y,r)==1);
  auto settings=stationThemeToggleRect(w,h,true);check(settings.x==w*.323f&&settings.y==h*.147f);
 }
 StationOnlineRobotPlayback clock;clock.press(0);std::set<unsigned> frames;unsigned changes=0,previous=~0u;
 for(unsigned ms=0;ms<600000;ms+=8){unsigned f=clock.frame(ms);check(f<242&&f%2==0&&clock.playing);frames.insert(f);if(f!=previous){changes++;previous=f;}}
 check(frames.size()==121&&changes>17000&&changes<18100);clock.hide();check(clock.frame(700000)==0&&!clock.playing);
 clock.press(0xfffffff0u);check(clock.frame(0x00000020u)==2);clock.hide();clock.press(123);check(clock.frame(123)==0&&clock.frame(1123)==60&&clock.frame(4123)==240&&clock.frame(4157)==0);
 alignas(16) B gui[0x2100]={};at<float>(gui,0x54)=2340;at<float>(gui,0x58)=1080;at<int>(gui,0x370)=3;
 now=0;drawOnlineRobot(gui,nullptr);check(draws==1&&lastFrame==0);
 now=6000;drawOnlineRobot(gui,nullptr);check(draws==2&&lastFrame!=0&&stationOnlineRobotPlayback.playing);
 unsigned before=draws;covered=true;drawOnlineRobot(gui,nullptr);check(draws==before&&!stationOnlineRobotPlayback.playing);covered=false;
 now=9000;drawOnlineRobot(gui,nullptr);check(draws==before+1&&lastFrame==0);systemsMode=true;drawOnlineRobot(gui,nullptr);check(!stationOnlineRobotPlayback.playing);systemsMode=false;folderMode=true;before=draws;drawOnlineRobot(gui,nullptr);check(draws==before);
 printf("PASS %u checks: UI colors unchanged in both choices; sky colors; right selector/shared hitbox; continuous robot at normal speed, bounded 30fps frame changes, timer wrap and hidden/modal reset.\n",checks);
}
