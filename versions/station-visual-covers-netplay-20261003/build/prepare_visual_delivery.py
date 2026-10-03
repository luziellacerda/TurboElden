from pathlib import Path
import hashlib,json,shutil

ROOT=Path(r'E:\ESTUDO APK\work\station-visual-covers-20261003')
OLD=Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003')
NATIVE=ROOT/'native'
def replace_once(text, old, new):
    if text.count(old)!=1: raise RuntimeError('Expected one source marker: '+old[:90])
    return text.replace(old,new)

def main():
    original={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OLD/'native').iterdir() if p.suffix in ('.h','.cpp')}
    (ROOT/'native-base-hashes.json').write_text(json.dumps(original,indent=2)+'\n')
    p=NATIVE/'native_carousel.cpp';s=p.read_text('utf-8')
    s=replace_once(s,'#include "native_laser.h"','#include "native_laser.h"\n#include "native_magazine.h"')
    s=replace_once(s,'#include "native_system_video720.h"','#include "native_system_video720.h"\n#include "native_console.h"')
    s=replace_once(s,'#include "native_settings.h"','static bool openStationNetplay();\n#include "native_settings.h"')
    s=replace_once(s,'#include "native_mega.h"','#include "native_mega.h"\n#include "native_netplay.h"')
    p.write_text(s,encoding='utf-8')
    p=NATIVE/'native_settings.h';s=p.read_text('utf-8')
    s=replace_once(s,'static void*settingsBackText;static void*settingsBackOwner;',
        'static void*settingsBackText;static void*settingsBackOwner;\nstatic void*settingsNetplayText;')
    s=replace_once(s,'w*.052f,h*.064f,w*.70f,h*.075f','w*.052f,h*.064f,w*.48f,h*.075f')
    s=replace_once(s,'setLongText(settingsBackText,"VOLTAR");}',
        'setLongText(settingsBackText,"VOLTAR");settingsNetplayText=createInfoText(p,0xF3FFF6ff);setLongText(settingsNetplayText,"JOGAR EM REDE");}')
    s=replace_once(s,'place(settingsBackText,w*.825f,h*.064f,w*.128f,h*.065f,.85f,1);',
        'place(settingsBackText,w*.825f,h*.064f,w*.128f,h*.065f,.85f,1);\n place(settingsNetplayText,w*.585f,h*.064f,w*.221f,h*.065f,.75f,1);')
    s=replace_once(s,'rounded(w*.825f,h*.064f,w*.128f,h*.065f,0x147D32ff);',
        'rounded(w*.585f,h*.064f,w*.221f,h*.065f,0x183C26ff);\n if(settingsNetplayText)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsNetplayText,matrix);\n rounded(w*.825f,h*.064f,w*.128f,h*.065f,0x147D32ff);')
    s=replace_once(s,'static bool pressed;static U finger;', 'static bool pressed;static U finger;static int pressedAction;')
    s=replace_once(s,'if(type==0){pressed=inside;finger=id;if(inside)return true;}\n if(pressed&&id==finger){if(type==2){pressed=false;if(inside)requestSettingsClose(p);}return true;}',
        '''bool network=x>=w*.585f&&x<=w*.806f&&y>=h*.064f&&y<=h*.129f;
 if(type==0){pressed=inside||network;pressedAction=network?2:1;finger=id;if(pressed)return true;}
 if(pressed&&id==finger){if(type==2){pressed=false;if(pressedAction==1&&inside)requestSettingsClose(p);else if(pressedAction==2&&network&&openStationNetplay())requestSettingsClose(p);}return true;}''')
    p.write_text(s,encoding='utf-8')
    project=ROOT/'manifest-project';project.mkdir(exist_ok=True)
    for directory in ('res',):shutil.copytree(OLD/'manifest-decoded'/directory,project/directory,dirs_exist_ok=True)
    shutil.copy2(OLD/'manifest-decoded/apktool.yml',project/'apktool.yml')
    source=(OLD/'manifest-decoded/AndroidManifest.xml').read_text('utf-8')
    added='''        <activity android:name="org.emulationstation.frontend.netplay.StationNetplayActivity" android:exported="false"
            android:enableOnBackInvokedCallback="false" android:screenOrientation="userLandscape"
            android:configChanges="keyboardHidden|orientation|screenSize" android:theme="@android:style/Theme.Material.NoActionBar"/>
        <activity android:name="org.emulationstation.frontend.netplay.StationDolphinNetplayActivity" android:exported="false" android:process=":dolphin"
            android:enableOnBackInvokedCallback="false" android:screenOrientation="userLandscape"
            android:configChanges="keyboardHidden|orientation|screenSize" android:theme="@style/td_Theme.Dolphin"/>
'''
    # Verify the embedded upstream Dolphin theme rather than inventing a resource.
    import xml.etree.ElementTree as ET
    tree=ET.fromstring(source);ns='{http://schemas.android.com/apk/res/android}'
    dolphin=next(a for a in tree.find('application').findall('activity') if a.get(ns+'name')=='org.dolphinemu.dolphinemu.features.netplay.ui.NetplaySetupActivity')
    theme=dolphin.get(ns+'theme')
    if not theme: raise RuntimeError('Dolphin Netplay theme must be explicit in base manifest')
    added=added.replace('@style/td_Theme.Dolphin','@android:style/Theme.Material.NoActionBar')
    (project/'AndroidManifest.xml').write_text(replace_once(source,'    </application>',added+'    </application>'),'utf-8')
    (ROOT/'manifest-additions.json').write_text(json.dumps({'addedActivities':['org.emulationstation.frontend.netplay.StationNetplayActivity','org.emulationstation.frontend.netplay.StationDolphinNetplayActivity'],'dolphinTheme':theme},indent=2)+'\n')
    print('Prepared native menu entry and manifest; existing engine declarations retained.')

if __name__=='__main__':main()
