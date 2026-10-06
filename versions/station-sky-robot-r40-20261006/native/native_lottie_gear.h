// Live chatbot, Abdul Latif. Original Lottie frames, one cycle on press only.
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
 if(!skinTop){fn<void(*)(void*,float,float,float,unsigned)>(0x221854)(p,cx,cy,radius,color);return;}
 unsigned frame=settingsChatbotPlayback.frame(fn<unsigned(*)()>(0x39e240)());
 float w=radius*2.18f,h=w*stationLottie_chatbot_height/stationLottie_chatbot_width;
 drawStationLottie(2,frame,{cx-w*.5f,cy-h*.5f,w,h});
}
