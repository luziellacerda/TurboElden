"""Two human Sony launcher actions in the existing native settings footer.

No native ABI/export or emulator core change. Original tabs and their dispatch
are preserved. Reserve one row of the options viewport for two static actions;
JNI runs only after a completed human tap, never during layout or rendering.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json

SOURCE_SHA='7d7e4d388319594d7bfc934105d1d09c75af09a3887f4b1f8bb1dcf14d9b3abb'

BRIDGE='''// Human settings hand-off only. No game path, online command or frame polling.
static bool openStationSonySettings(const char*platform){
 if(!platform||(strcmp(platform,"ps3")!=0&&strcmp(platform,"ps4")!=0))return false;
 JNIEnv*env=videoEnv();if(!env)return false;
 jobject activity=videoActivity();if(!activity)return false;
 jclass activityClass=nullptr,loaderClass=nullptr,bridge=nullptr;
 jobject loader=nullptr;jstring className=nullptr,system=nullptr;bool accepted=false;
 do{
  activityClass=env->GetObjectClass(activity);if(!activityClass||env->ExceptionCheck())break;
  jmethodID getLoader=env->GetMethodID(activityClass,"getClassLoader","()Ljava/lang/ClassLoader;");
  if(!getLoader||env->ExceptionCheck())break;
  loader=env->CallObjectMethod(activity,getLoader);if(!loader||env->ExceptionCheck())break;
  loaderClass=env->GetObjectClass(loader);if(!loaderClass||env->ExceptionCheck())break;
  jmethodID load=env->GetMethodID(loaderClass,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;");
  if(!load||env->ExceptionCheck())break;
  className=env->NewStringUTF("org.emulationstation.frontend.offline.StationSonyOfflineActivity");
  if(!className||env->ExceptionCheck())break;
  bridge=(jclass)env->CallObjectMethod(loader,load,className);if(!bridge||env->ExceptionCheck())break;
  jmethodID open=env->GetStaticMethodID(bridge,"openSettings","(Landroid/app/Activity;Ljava/lang/String;)Z");
  if(!open||env->ExceptionCheck())break;
  system=env->NewStringUTF(platform);if(!system||env->ExceptionCheck())break;
  accepted=env->CallStaticBooleanMethod(bridge,open,activity,system)==JNI_TRUE;
 }while(false);
 if(env->ExceptionCheck()){env->ExceptionClear();accepted=false;log("Sony settings bridge unavailable");}
 if(system)env->DeleteLocalRef(system);if(bridge)env->DeleteLocalRef(bridge);
 if(className)env->DeleteLocalRef(className);if(loaderClass)env->DeleteLocalRef(loaderClass);
 if(loader)env->DeleteLocalRef(loader);if(activityClass)env->DeleteLocalRef(activityClass);
 env->DeleteLocalRef(activity);
 if(accepted){stopSystemVideo();pauseRetroMusicForGame();log("Sony settings request dispatched");}
 return accepted;
}
'''

REPLACEMENTS=(
 ('static void*settingsEffectsLabel;\n',
  'static void*settingsEffectsLabel;\nstatic void*settingsSonyPs3Text;static void*settingsSonyPs4Text;\n'),
 ('static StationThemeRect settingsEffectsRect,settingsBackRect,settingsNetworkRect,settingsSkyRect;\n',
  'static StationThemeRect settingsEffectsRect,settingsBackRect,settingsNetworkRect,settingsSkyRect;\nstatic StationThemeRect settingsSonyPs3Rect,settingsSonyPs4Rect;\nstatic float settingsRowsClipHeight;\n'),
 ('static void requestSettingsClose(void*p){\n',
  BRIDGE+'static void requestSettingsClose(void*p){\n'),
 (' settingsTabClipHeight=settingsContentHeight-tap-gap;\n',
  ''' settingsTabClipHeight=settingsContentHeight-tap-gap;
 settingsRowsClipHeight=settingsContentHeight-tap-gap;
 float sonyY=settingsContentY+settingsRowsClipHeight+gap,sonyWidth=(w*.63f-gap)*.5f;
 settingsSonyPs3Rect={w*.323f,sonyY,sonyWidth,tap};
 settingsSonyPs4Rect={w*.323f+sonyWidth+gap,sonyY,sonyWidth,tap};
'''),
 (' bounds(p,0x2064,w*.323f,settingsContentY,w*.63f,settingsContentHeight);\n',
  ' bounds(p,0x2064,w*.323f,settingsContentY,w*.63f,settingsRowsClipHeight);\n'),
 (' float content=nr*rowStep;if(content<settingsContentHeight)content=settingsContentHeight;at<float>(p,0x2130)=content;\n float maxRows=content-settingsContentHeight;',
  ' float content=nr*rowStep;if(content<settingsRowsClipHeight)content=settingsRowsClipHeight;at<float>(p,0x2130)=content;\n float maxRows=content-settingsRowsClipHeight;'),
 ('  settingsEffectsLabel=createInfoText(p,0xEFF5FFff);setLongText(settingsEffectsLabel,"EFEITOS GRÁFICOS");\n',
  '''  settingsEffectsLabel=createInfoText(p,0xEFF5FFff);setLongText(settingsEffectsLabel,"EFEITOS GRÁFICOS");
  settingsSonyPs3Text=createInfoText(p,0xEFF5FFff);setLongText(settingsSonyPs3Text,"PS3 — Configurar emulador");
  settingsSonyPs4Text=createInfoText(p,0xEFF5FFff);setLongText(settingsSonyPs4Text,"PS4 — Configurar emulador");
'''),
 (' place(settingsEffectsLabel,settingsEffectsRect.x+w*.013f,settingsEffectsRect.y+settingsTextInset,settingsEffectsRect.w-w*.026f,tap*.68f,.67f,0);\n',
  ''' place(settingsEffectsLabel,settingsEffectsRect.x+w*.013f,settingsEffectsRect.y+settingsTextInset,settingsEffectsRect.w-w*.026f,tap*.68f,.67f,0);
 place(settingsSonyPs3Text,settingsSonyPs3Rect.x+w*.013f,settingsSonyPs3Rect.y+settingsTextInset,settingsSonyPs3Rect.w-w*.026f,tap*.68f,.67f,0);
 place(settingsSonyPs4Text,settingsSonyPs4Rect.x+w*.013f,settingsSonyPs4Rect.y+settingsTextInset,settingsSonyPs4Rect.w-w*.026f,tap*.68f,.67f,0);
'''),
 (' if(settingsEffectsLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsEffectsLabel,matrix);\n',
  ''' if(settingsEffectsLabel)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsEffectsLabel,matrix);
 auto s3=settingsSonyPs3Rect;bool ps3Pressed=settingsActionPressed&&settingsPressedAction==3;
 settingsConsoleCard(s3.x,s3.y,s3.w,s3.h,ps3Pressed?0x244EB3ff:0x151F2Eff,ps3Pressed?0xEFF5FFff:0x334153ff);
 if(settingsSonyPs3Text)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsSonyPs3Text,matrix);
 auto s4=settingsSonyPs4Rect;bool ps4Pressed=settingsActionPressed&&settingsPressedAction==4;
 settingsConsoleCard(s4.x,s4.y,s4.w,s4.h,ps4Pressed?0x244EB3ff:0x151F2Eff,ps4Pressed?0xEFF5FFff:0x334153ff);
 if(settingsSonyPs4Text)fn<void(*)(void*,void*)>(0x2d2dc4)(settingsSonyPs4Text,matrix);
'''),
 (' bool inside=stationThemeContains(settingsBackRect,x,y),network=stationThemeContains(settingsNetworkRect,x,y);\n if(type==0){settingsActionPressed=inside||network;settingsPressedAction=network?2:1;',
  ''' bool inside=stationThemeContains(settingsBackRect,x,y),network=stationThemeContains(settingsNetworkRect,x,y);
 bool ps3=stationThemeContains(settingsSonyPs3Rect,x,y),ps4=stationThemeContains(settingsSonyPs4Rect,x,y);
 if(type==0){settingsActionPressed=inside||network||ps3||ps4;settingsPressedAction=ps4?4:ps3?3:network?2:1;'''),
 ('else if(settingsPressedAction==2&&network&&openStationNetplay())requestSettingsClose(p);}return true;\n',
  'else if(settingsPressedAction==2&&network&&openStationNetplay())requestSettingsClose(p);else if(settingsPressedAction==3&&ps3&&openStationSonySettings("ps3"))requestSettingsClose(p);else if(settingsPressedAction==4&&ps4&&openStationSonySettings("ps4"))requestSettingsClose(p);}return true;\n'),
)

def patch(original:bytes)->bytes:
    if hashlib.sha256(original).hexdigest()!=SOURCE_SHA:
        raise ValueError('Exact current R124 native_settings.h required')
    text=original.decode('utf-8')
    for old,new in REPLACEMENTS:
        if text.count(old)!=1:
            raise ValueError('Native settings anchor changed: '+old[:80])
        text=text.replace(old,new,1)
    result=text.encode('utf-8')
    verify(original,result)
    return result

def verify(original:bytes,patched:bytes)->dict:
    if hashlib.sha256(original).hexdigest()!=SOURCE_SHA:
        raise ValueError('Settings source identity mismatch')
    text=patched.decode('utf-8')
    for old,new in reversed(REPLACEMENTS):
        if text.count(new)!=1:
            raise ValueError('Settings patch must be unique and exact')
        text=text.replace(new,old,1)
    if text.encode('utf-8')!=original:
        raise ValueError('An unrelated settings byte changed')
    return {
        'sourceSha256':SOURCE_SHA,
        'patchedSha256':hashlib.sha256(patched).hexdigest(),
        'exactInverse':True,
        'changedMethods':['layoutSettingsSkin','drawSettingsSkinHook','touchSettingsSkinHook'],
        'addedMethods':['openStationSonySettings'],
        'originalTabsAndEmulatorDispatchUnchanged':True,
        'originalOptionValueActionsUnchanged':True,
        'oneOptionsRowReservedForSonySettings':True,
        'externalSettingsLauncherOnly':True,
        'humanTapOnly':True,
        'jniPerFrameAdded':False,
        'backgroundLoopsAdded':False,
        'gameLaunchRoutesChanged':False,
        'onlineMethodsChanged':False,
        'nativePublicExportsAdded':False,
        'physicalValidation':False,
    }

def patch_settings(native_source:bytes,original_header:bytes)->tuple[bytes,bytes,dict]:
    """Build adapter: owned text guard, local override header and flags.

    Write the header beside the generated .cpp only after the exact R128
    baseline was compiled and compared. Quoted includes select that local
    header for the final compilation; the baseline input stays untouched.
    """
    if native_source.count(b'#include "native_settings.h"')!=1:
        raise ValueError('The native source must use its single quoted settings include')
    patched=patch(original_header)
    flags=verify(original_header,patched)
    old=b'p==settingsEffectsLabel||isStoreUiLabel(p)'
    new=b'p==settingsEffectsLabel||p==settingsSonyPs3Text||p==settingsSonyPs4Text||isStoreUiLabel(p)'
    if native_source.count(old)!=1 or new in native_source:
        raise ValueError('Exact settings owned-label rendering guard required')
    changed=native_source.replace(old,new,1)
    if changed.replace(new,old,1)!=native_source:
        raise ValueError('Unrelated native rendering byte changed')
    flags['nativeCppByteIdentical']=False
    flags['nativeCppChange']='two-owned-settings-labels-in-existing-textRenderHook-exclusion'
    flags['nativeCppExactInverse']=True
    flags['sonyLabelsDrawnOnlyByOpenSettingsModal']=True
    return changed,patched,flags

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('source','out','receipt'):
        parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    original=args.source.read_bytes();patched=patch(original)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(patched)
    args.receipt.write_text(json.dumps(verify(original,patched),indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
