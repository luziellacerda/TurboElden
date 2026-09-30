from pathlib import Path
p=Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
f=p/'native_carousel.cpp';s=f.read_text('utf-8')
if '#include "native_flycast.h"' not in s:
 s=s.replace('#include "native_dolphin.h"','#include "native_dolphin.h"\n#include "native_flycast.h"')
 for name in ['Run','Fresh','Bundled','Installed','Assets','Pack','Definitions','Settings']:
  s=s.replace('(void*)dolphin'+name+'Hook','(void*)flycast'+name+'Hook')
 f.write_text(s,'utf-8')
print('Flycast routes chained to preserved Dolphin and other engines.')
