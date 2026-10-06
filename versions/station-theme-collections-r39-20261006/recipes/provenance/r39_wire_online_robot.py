from pathlib import Path
import shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
shutil.copy2('r39_online_robot_state.h',N/'station_online_robot_state.h');shutil.copy2('r39_online_robot_native.h',N/'native_online_robot.h')
p=N/'native_theme_switch.h';s=p.read_text('utf8').replace('stationLottieTextures[3]','stationLottieTextures[4]').replace('asset>2','asset>3');p.write_text(s,'utf8')
p=N/'native_carousel.cpp';s=p.read_text('utf8').replace('#include "native_lottie_gear.h"','#include "native_lottie_gear.h"\n#include "native_online_robot.h"').replace('drawThemeSwitch(p,&formationMatrix,false);','drawThemeSwitch(p,&formationMatrix,false);drawOnlineRobot(p,matrix);');p.write_text(s,'utf8')
p=N/'native_netplay.h';s=p.read_text('utf8').replace('if(type==0){pressed=inside;finger=id;return pressed;}','if(type==0){pressed=inside;finger=id;if(pressed)stationOnlineRobotPlayback.press(fn<unsigned(*)()>(0x39e240)());return pressed;}');p.write_text(s,'utf8')
print('Small original online robot centered above the existing button; no hit-area or routing change.')
