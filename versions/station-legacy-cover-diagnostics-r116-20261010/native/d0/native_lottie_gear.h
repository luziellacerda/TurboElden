// Live chatbot, Abdul Latif. Original frames loop only when this visible icon is drawn.
// Existing settings button action and hit rectangle stay owned by GuiStore.
#include "station_chatbot_state.h"
static StationChatbotPlayback settingsChatbotPlayback;
static void settingsChatbotPress(void*p,const void*event){
 if(modal(p)||at<int>((void*)event,0)!=0)return;
 float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);
 float bx=at<float>(p,0x1410),by=at<float>(p,0x1414),bw=at<float>(p,0x1418),bh=at<float>(p,0x141c);
 if(x>=bx&&x<=bx+bw&&y>=by&&y<=by+bh)settingsChatbotPlayback.press(fn<unsigned(*)()>(0x39e240)());
}
static void drawSettingsLottieHook(void*p,float cx,float cy,float radius,unsigned color){
 if(!skinTop||!skinTopOwner){fn<void(*)(void*,float,float,float,unsigned)>(0x221854)(p,cx,cy,radius,color);return;}
 // No independent timer: hidden/background menus make no calls or texture uploads.
 unsigned frame=settingsChatbotPlayback.frame(fn<unsigned(*)()>(0x39e240)());
 // Original GuiStore::drawTopButtons uses radius = button height * .34.
 // Keep the requested prior scale, then enlarge the original artwork another 50%.
 // p is ABI baggage here, not a valid object: x0 can be null at 0x22ee5c.
 // Only the owner bound by topSkinHook may be dereferenced.
 float oldRadius=at<float>(skinTopOwner,0x58)*.059f*.34f;
 float w=systemsMode?oldRadius*6.54f:at<float>(skinTopOwner,0x1418),h=w*stationLottie_chatbot_height/stationLottie_chatbot_width;
 drawStationLottie(2,frame,{cx-w*.5f,cy-h*.5f,w,h});
}
