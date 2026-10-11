"""Scope/consumption guards supplement compiled preferences/row/cache tests."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'station-legacy-cover-diagnostics-r116-20261010'
checks=0
def require(condition,label):
 global checks
 checks+=1
 if not condition:raise AssertionError(label)
def source(path):return (ROOT/path).read_text(encoding='utf-8')
for path in (
 'java/client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java',
 'java/client/src/java/org/emulationstation/frontend/station/StationCoverStore.java',
 'java/client/src/java/org/emulationstation/frontend/station/StationCarouselMedia.java',
 'java/client/src/java/org/emulationstation/frontend/station/StationApi.java',
 'java/netplay-src/org/emulationstation/frontend/netplay/StationRoomArtwork.java',
 'java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java',
 'native/d0/magazine_shader.h', 'native/d0/premium-magazine-led-android.glsl',
 'frontend/station_cover_plan.hpp','frontend/station_cover_warmstart.hpp'):
 require((ROOT/path).read_bytes()==(BASE/path).read_bytes(),'preserved '+path)
g=source('native/d0/native_graphics.h')
require('StationGraphics_snapshot' in g and 'JNIEnv' not in g,'atomic bridge without per-frame JNI')
require('stationGraphicsSnapshot()&bit' in g,'effect mask')
s=source('native/d0/native_space.h')
require('if(background==2)' in s and 'return;}' in s,'off skips clouds and waves')
require('if(background==1)drawNativeWaves' in s,'explicit waves only')
require('Vertex strip[66]' in s and 'wave<3' in s and 'i<=32' in s,'bounded 198-vertex waves')
v=source('native/d0/native_system_video720.h')
require('if(!videosEnabled)pauseSystemVideo720();' in v,'video off retires decoders')
require('if(!videosEnabled){drawStaticSystemVideo720(p,context);return;}' in v,'video off paints static artwork before decoder path')
require('if(pending)seedVideo720Preview(pending);' in v,'video off admits at most one packaged poster per frame')
m=source('native/d0/native_magazine.h')
require('if(!stationGraphicsEnabled(1u))' in m and 'releaseMagazineFieldObjects()' in m,'LED off releases work')
c=source('native/d0/native_carousel.cpp')
require('if(stationGraphicsEnabled(1))prewarmMagazinePrograms()' in c,'disabled LEDs do not prewarm')
f=source('native/d0/native_formation.h')
require('if(snap)at<float>(p,0xf4)=retainedAnimation;' in f,'presentation snap restores update/input state')
ui=source('native/d0/native_graphics_ui.h')
require('theme.x-w*.20f-w*.012f' in ui,'button beside theme')
require('StationGraphicsPanel' in ui and 'Landroid/app/Activity;)Z' in ui,'panel JNI signature')
front=source('frontend/station_frontend.cpp')
require('graphicsState.store(value,std::memory_order_release)' in front,'atomic whole snapshot')
require('graphicsState.load(std::memory_order_acquire)' in front,'atomic read')
require('mask>63||background<0||background>2' in front,'native bounds')
prefs=source('java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java')
require('FILE = "station_graphics_r117"' in prefs,'fresh storage distinct rejected R100')
require('masterDisabled ? 0 : individualMask' in prefs,'master preserves individual selections')
settings=source('native/d0/native_settings.h')
require('setLongText(settingsEffectsLabel,"EFEITOS")' in settings,'settings tab')
require('effectsAction==1)openGraphicsPanel()' in settings,'settings touch launches panel')
require('themeSwitchGesture={};settingsEffectsGesture={};fn<V>(0x21dd24)' in settings,'physical close resets effect gesture')
require('themeSwitchGesture={};\n settingsEffectsGesture={};' in settings,'requested close resets effect gesture')
require('if(settingsBackOwner!=p){settingsEffectsGesture={};' in settings,'new owner resets effect gesture')
report={'passed':True,'checks':checks,'scope':'source guards; no physical thermal/gameplay claim'}
(ROOT/'evidence/graphics-integration-guards.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
