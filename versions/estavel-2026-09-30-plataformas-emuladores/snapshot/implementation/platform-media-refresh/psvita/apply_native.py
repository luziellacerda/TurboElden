from pathlib import Path
import shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'platform-media-refresh/psvita'
s=(P/'native_xbox360.h').read_text(encoding='utf-8')
s=s.replace('// XenDroid 0b11201 Android integration. Dedicated experimental Xbox 360 engine.','// Vita3K 0.2.1 Android integration; an isolated process is started only on explicit launch.')
s=s.replace('xbox360','vita').replace('Xbox360','Vita').replace('Xbox 360','PS Vita').replace('XenDroid','Vita3K')
s=s.replace('"xendroid"','"vita3k"')
# Fallback through the complete previous chain, including Xbox, Wii U and all earlier engines.
s=s.replace('return wiiu', 'return xbox360').replace(':wiiu', ':xbox360').replace('=wiiuKnownCoresHook()', '=xbox360KnownCoresHook()')
s=s.replace('wiiuSettingsHook(p,tab)', 'xbox360SettingsHook(p,tab)')
s=s.replace('static bool vitaCore(const void*id){return uiContains(strData(id),"vita3k")||uiContains(strData(id),"vita")||uiContains(strData(id),"PS Vita");}',
'''static bool vitaCore(const void*id){return uiContains(strData(id),"vita3k")||uiContains(strData(id),"psvita")||uiContains(strData(id),"Psvita")||uiContains(strData(id),"PS Vita");}''')
(P/'native_psvita.h').write_text(s,encoding='utf-8')
f=P/'native_carousel.cpp';s=f.read_text(encoding='utf-8');shutil.copy2(f,R/'native-before-vita.cpp')
anchor='#include "native_xbox360.h"';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n#include "native_psvita.h"')
for name in ['KnownCores','Run','Fresh','Bundled','Installed','Assets','Pack','Definitions','Settings']:
    old='(void*)xbox360'+name+'Hook';assert s.count(old)==1;s=s.replace(old,'(void*)vita'+name+'Hook')
anchor=' const char*key=strData(folder);';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n if(presentationKeyEqual(key,"psvita")||presentationKeyEqual(key,"PS Vita")){UiString result={};strAssign(&result,"libretro: core=vita3k_android.so");return result;}')
f.write_text(s,encoding='utf-8')
shutil.copy2(Path(__file__),R/'apply_native.py')
print('Native PS Vita launch/settings routes connected through the existing engine chain.')
