from pathlib import Path
import shutil,json

P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-media-refresh';B=R/'before'
for name in ['native_system_video720.h','native_space3d.h']:
    assert not (B/name).exists()
    shutil.copy2(P/name,B/name)
f=P/'native_carousel.cpp';s=f.read_text(encoding='utf-8')
old='||strcmp(key,"Odyssey 2")==0)continue;'
assert s.count(old)==1
s=s.replace(old,'||strcmp(key,"Odyssey 2")==0||presentationKeyEqual(key,"atari7800")||presentationKeyEqual(key,"supergrafx"))continue;')
anchor='#include "native_xbox360.h"'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n#include "native_menu_power.h"')
s=s.replace('static void renderHook(void*p,void*matrix){','static void renderHook(void*p,void*matrix){\n paceStoreMenu(p);')
s=s.replace('static bool inputHook(void*p,void*cfg,const void*in){\n gui=p;', 'static bool inputHook(void*p,void*cfg,const void*in){\n noteStoreInteraction();gui=p;')
s=s.replace('static bool touchHook(void*p,const void*event){gui=p;', 'static bool touchHook(void*p,const void*event){noteStoreInteraction();gui=p;')
f.write_text(s,encoding='utf-8')
shutil.copy2(Path(__file__).parent/'native_menu_power.h',P/'native_menu_power.h')
f=P/'system_video720_assets.h';s=f.read_text(encoding='utf-8')
for key,slug in [('Pc Engine','pcengine'),('Pc Engine cd','pcenginecd')]:
    assert '"'+key+'"' not in s
    s=s.replace('\n};','\n{"'+key+'","turbo-system-videos/720-'+slug+'.mp4"},\n};')
f.write_text(s,encoding='utf-8')
f=P/'native_system_video720.h';s=f.read_text(encoding='utf-8')
s=s.replace('unsigned texture,retryAt;','unsigned texture,retryAt,lastPollAt;')
old='  result[i]=0;auto&v=video720Slots[i];if(!v.texture)continue;'
assert s.count(old)==1
s=s.replace(old,old+'''
  // A parked preview retains its GPU frame. Poll only a heartbeat, not every GUI frame.
  // This remains below the Java lifecycle watchdog's three-second retirement timeout.
  if(v.ready&&!v.visible&&(unsigned)(now-v.lastPollAt)<1000)continue;
  v.lastPollAt=now;''')
f.write_text(s,encoding='utf-8')
f=P/'native_space3d.h';s=f.read_text(encoding='utf-8')
assert '(int)(t*30)' in s and 'frame/30.f' in s
s=s.replace('320x180 at 30Hz','320x180 at 15Hz').replace('(int)(t*30)','(int)(t*15)').replace('frame/30.f','frame/15.f')
f.write_text(s,encoding='utf-8')
shutil.copy2(Path(__file__),R/'apply.py')
policy={'scope':'native GuiStore only, emulator loops and speed settings unchanged',
        'idle_platform_with_video_fps':30,'idle_other_menu_fps':15,
        'interaction_and_transition_fps':60,'interaction_boost_ms':650,
        'clouds_fps':15,'paused_video_poll_interval_ms':1000,
        'focus_video':{'resolution':[720,720],'fps':30,'speed':1,'loop':True},
        'sources':['https://developer.android.com/games/optimize/power','https://wiki.libsdl.org/SDL2/SDL_Delay','https://wiki.libsdl.org/SDL2/SDL_GetPerformanceCounter'],
        'verified_on_device':False}
(R/'power-policy.json').write_text(json.dumps(policy,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Applied platform exclusions, exact video mappings and native menu power policy.')
