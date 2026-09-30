from pathlib import Path
import shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'dolphin-integration'
backup=R/'before';backup.mkdir(exist_ok=True)
for name in ['native_carousel.cpp','libturbo_carousel.so']:
    if not (backup/name).exists():shutil.copy2(P/name,backup/name)
p=P/'native_carousel.cpp';s=p.read_text('utf-8')
if '#include "native_dolphin.h"' not in s:
    s=s.replace('#include "native_search_download.h"','#include "native_search_download.h"\n#include "native_dolphin.h"')
    s=s.replace('static Hook hooks[]={','''static Hook hooks[]={
 {0x2a9718,(void*)dolphinRunHook},{0x2a89a8,(void*)dolphinFreshHook},
 {0x2a87d8,(void*)dolphinBundledHook},{0x18b098,(void*)dolphinInstalledHook},
 {0x18aaf0,(void*)dolphinAssetsHook},{0x18a8a8,(void*)dolphinPackHook},
 {0x2a6850,(void*)dolphinDefinitionsHook},{0x2228f8,(void*)dolphinSettingsHook},''')
    p.write_text(s,'utf-8')
print('Native Dolphin routes registered; original frontend and other cores retained.')
