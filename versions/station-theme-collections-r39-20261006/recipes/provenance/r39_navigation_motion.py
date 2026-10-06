from pathlib import Path
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
def edit(n,a,b):
 p=N/n;s=p.read_text('utf8');assert a in s,(n,a[:70]);p.write_text(s.replace(a,b),'utf8')
edit('native_folders.h','static void enterFolderGames(void*p', '''// A fresh list must not inherit the native rebuild's remembered selection.
// Back restores its stable folder path separately in showFolderMenu.
static void firstFolderGame(void*p){
 at<int>(p,0xf0)=0;at<float>(p,0xf4)=0;
 at<int>(p,0x220)=-1;at<U>(p,0x228)=~0UL;
}
static void enterFolderGames(void*p''')
edit('native_folders.h','invalidate(p);rebuildHook(p);refreshHook(p);','invalidate(p);rebuildHook(p);firstFolderGame(p);refreshHook(p);folderRevision=foldersRevision();')
edit('native_folders.h','invalidate(p);rebuildHook(p);\n if(selectedKind>=0){','invalidate(p);rebuildHook(p);\n at<int>(p,0xf0)=0;at<float>(p,0xf4)=0;\n if(selectedKind>=0){')
edit('native_carousel.cpp','invalidate(p);rebuildHook(p);refreshHook(p);\n coverCheckAt=','invalidate(p);rebuildHook(p);firstFolderGame(p);refreshHook(p);\n coverCheckAt=')
edit('native_info.h','owner=t;oldW=w;oldH=h;strAssign(previous,label);','owner=t;oldW=w;oldH=h;gameStatusNeedsLayout=false;strAssign(previous,label);')
edit('native_info.h','infoPlayStars={layout.label.x+used+layout.gap,layout.stars.y,layout.stars.w,layout.stars.h};','infoPlayStars={layout.label.x+used+layout.gap,layout.stars.y,layout.stars.w,layout.stars.h};\n strAssign(previous,strData((B*)t+0xd0));')
edit('native_settings.h','i?0x123251ff:0x080C09ff','i?0x123251ff:0x090D12ff')
(N/'station_lottie_once.h').write_text('''#pragma once
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
''','utf8')
edit('native_lottie_gear.h','#include "lottie_gear3_data.h"','#include "lottie_gear3_data.h"\n#include "station_lottie_once.h"\nstatic StationLottieOnce gear3Playback;\nstatic void gear3Press(void*p,const void*event){\n if(modal(p)||at<int>((void*)event,0)!=0)return;\n float x=at<float>((void*)event,0x10),y=at<float>((void*)event,0x14);\n float bx=at<float>(p,0x1410),by=at<float>(p,0x1414),bw=at<float>(p,0x1418),bh=at<float>(p,0x141c);\n if(x>=bx&&x<=bx+bw&&y>=by&&y<=by+bh)gear3Playback.press(fn<unsigned(*)()>(0x39e240)());\n}')
edit('native_lottie_gear.h','unsigned frame=(tick%3003u)*90u/3003u;','unsigned frame=gear3Playback.frame(tick);')
edit('native_carousel.cpp','static bool touchHook(void*p,const void*event){noteStoreInteraction();gui=p;','static bool touchHook(void*p,const void*event){noteStoreInteraction();gui=p;gear3Press(p,event);')
print('Fresh folder selection reset after rebuild; stable Back preserved; gear Lottie runs once on press')
