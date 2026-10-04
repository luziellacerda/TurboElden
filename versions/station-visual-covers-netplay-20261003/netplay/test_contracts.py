"""Static donor API contracts plus executable isolated file-handoff tests."""
from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parent
DONOR=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\dolphin-integration\merged\smali_classes10')
JDK=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')

def main():
    methods={
      'org/dolphinemu/dolphinemu/utils/DirectoryInitialization.smali':['.method public static final areDolphinDirectoriesReady()Z'],
      'org/dolphinemu/dolphinemu/model/GameFileCache.smali':['.method public static final native getIsoPaths()[Ljava/lang/String;','.method public static final native setIsoPaths([Ljava/lang/String;)V'],
      'org/dolphinemu/dolphinemu/features/settings/model/NativeConfig.smali':['.method public static final native save(I)V'],
      'org/dolphinemu/dolphinemu/services/GameFileCacheManager.smali':['.method public static final startLoad()V','.method public static final startRescan()V','.method public static final isLoadingOrRescanning()Z'],
      'org/dolphinemu/dolphinemu/features/netplay/ui/NetplaySetupActivity.smali':['.class public final Lorg/dolphinemu/dolphinemu/features/netplay/ui/NetplaySetupActivity;']}
    count=0
    for name,expected in methods.items():
        source=(DONOR/name).read_text(encoding='utf-8')
        for signature in expected:
            assert signature in source,(name,signature)
            count+=1
    frontend=(ROOT.parent/'station/src/java/org/emulationstation/frontend/station/StationFrontend.java').read_text(encoding='utf-8')
    assert 'String[] installedPathsFor(String platform)' in frontend
    native=(ROOT/'native_netplay.h').read_text(encoding='utf-8')
    assert 'static bool openStationNetplay()' in native
    source='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'src').rglob('*.java'))
    assert 'http://' not in source and 'https://' not in source # no invented lobby/API or secrets
    assert 'force-stop' not in source and 'pm clear' not in source
    assert source.index('Mega Drive e Super Nintendo • jogo local') < source.index('psp=ui.action(')
    assert 'MdEmuBootstrap' not in source and 'Snes9xBootstrap' not in source
    count+=6
    output=ROOT/'build/tests';output.mkdir(parents=True,exist_ok=True)
    subprocess.run([str(JDK/'javac.exe'),'-encoding','UTF-8','--release','8','-d',str(output),str(ROOT/'src/org/emulationstation/frontend/netplay/NetplayPaths.java'),str(ROOT/'NetplayPathsTest.java')],check=True)
    run=subprocess.run([str(JDK/'java.exe'),'-cp',str(output),'NetplayPathsTest',str(output)],check=True,capture_output=True,text=True)
    print(run.stdout,end='')
    result={'donorAndSourceContracts':count,'pathChecks':14,'runtime':'not run','output':run.stdout.strip()}
    (ROOT/'build/test-result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS donor/source contracts='+str(count))
if __name__=='__main__':main()
