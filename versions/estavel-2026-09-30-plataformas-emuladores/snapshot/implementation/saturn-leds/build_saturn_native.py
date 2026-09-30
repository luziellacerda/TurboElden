from pathlib import Path
import os,subprocess,sys,shutil
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'saturn-leds'
file=P/'native_carousel.cpp';text=file.read_text(encoding='utf-8')
needle='static UiString gamecubeCommandHook(const void* folder){\n const char*key=strData(folder);'
assert text.count(needle)==1 and 'core=yabasanshiro_libretro_android.so' not in text
text=text.replace(needle,needle+'\n if(presentationKeyEqual(key,"saturn")||presentationKeyEqual(key,"Sega Saturn")||presentationKeyEqual(key,"saturno")){UiString result={};strAssign(&result,"libretro: core=yabasanshiro_libretro_android.so");return result;}')
file.write_text(text,encoding='utf-8')
os.environ['TEMP']=os.environ['TMP']=str(R/'tmp')
with (R/'build-native.log').open('w',encoding='utf-8') as log:
 subprocess.run([sys.executable,str(P/'build_native.py')],check=True,stdout=log,stderr=subprocess.STDOUT)
shutil.copy2(Path(__file__),R/'build_saturn_native.py')
print('Saturn native route and eight LED colors compiled.')
