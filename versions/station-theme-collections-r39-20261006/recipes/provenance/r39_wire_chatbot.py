from pathlib import Path
import shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
shutil.copy2('r39_chatbot_native.h',N/'native_lottie_gear.h');shutil.copy2('r39_chatbot_state.h',N/'station_chatbot_state.h')
p=N/'native_skin.h';s=p.read_text('utf8').replace('#include "native_lottie_gear.h"','');p.write_text(s,'utf8')
p=N/'native_carousel.cpp';s=p.read_text('utf8').replace('#include "native_theme_switch.h"','#include "native_theme_switch.h"\n#include "native_lottie_gear.h"').replace('gear3Press(p,event)','settingsChatbotPress(p,event)').replace('(void*)drawLottieGearHook','(void*)drawSettingsLottieHook');p.write_text(s,'utf8')
p=N/'native_settings.h';s=p.read_text('utf8').replace(' auto black=stationThemeChoice(w,h,0),blue=stationThemeChoice(w,h,1);','');p.write_text(s,'utf8')
p=N/'native_theme_switch.h';s=p.read_text('utf8').replace('stationLottieTextures[2]','stationLottieTextures[3]').replace('asset>1','asset>2');a=s.index(' unsigned width=');b=s.index(' int program=0',a);s=s[:a]+''' const auto&definition=stationLottieAssets[asset];
 unsigned width=definition.width,height=definition.height,frames=definition.frames;if(frame>=frames)frame=frames-1;
 const unsigned*offsets=definition.offsets,*data=definition.data;
'''+s[b:];p.write_text(s,'utf8')
print('Original chatbot replaces the top settings gear; idle static, tap 30fps once, original route preserved.')
