from pathlib import Path
import shutil,subprocess,sys
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'saturn-leds'
assert not (P/'native_saturn.h').exists()
shutil.copy2(Path(__file__).parent/'saturn-addition/native_saturn.h',P/'native_saturn.h')
file=P/'native_carousel.cpp';text=file.read_text(encoding='utf-8');assert text.count('#include "native_psvita.h"')==1
text=text.replace('#include "native_psvita.h"','#include "native_psvita.h"\n#include "native_saturn.h"')
assert text.count('{0x2a5720,(void*)vitaKnownCoresHook}'),text.count('{0x2a5720,(void*)vitaKnownCoresHook}')
text=text.replace('{0x2a5720,(void*)vitaKnownCoresHook}','{0x2a5720,(void*)saturnKnownCoresHook}');file.write_text(text,encoding='utf-8')
with (R/'build-native-final.log').open('w',encoding='utf-8') as log:
 subprocess.run([sys.executable,str(P/'build_native.py')],check=True,stdout=log,stderr=subprocess.STDOUT)
shutil.copy2(Path(__file__),R/'finish_saturn_native.py')
print('Native Saturn settings and carousel compiled.')
