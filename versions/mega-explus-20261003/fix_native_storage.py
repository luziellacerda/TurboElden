"""Correct NativeActivity internalDataPath for both complete emulators.
Do not import shared files/config: its owner/layout cannot safely be inferred.
"""
from pathlib import Path
import os,shutil,subprocess,zipfile
P=Path(__file__).resolve().parent.parent
S=Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003')
M=Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003')
J=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
SDK=Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
AT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar')
os.environ['TEMP']=os.environ['TMP']=str(M)
def run(*a):subprocess.run(list(map(str,a)),check=True)
from native_activity_storage import overrides

if __name__=='__main__':
    for root,folder,bridge,output in [(S,'snes-explus-20261003','SnesBootstrap','snes-storage-module.apk'),(M,'mega-explus-20261003','MegaBootstrap','mega-storage-module.apk')]:
        project=root/'donor-merged'
        activity=project/'smali/com/imagine/BaseActivity.smali'
        text=activity.read_text('utf-8')
        if '.method public getFilesDir()Ljava/io/File;' not in text:
            text+=overrides(bridge)
            activity.write_text(text,'utf-8')
        # Keep regeneration recipes consistent with these required overrides.
        java=root/'java';shutil.copytree(P/folder/'java',java,dirs_exist_ok=True)
        classes=root/'java-classes'
        run(J/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-classpath',SDK,'-d',classes,*java.rglob('*.java'))
        with zipfile.ZipFile(root/'bridge.jar','w') as z:
            for f in classes.rglob('*.class'):z.write(f,f.relative_to(classes).as_posix())
        run(J/'java.exe','-cp',BT/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',SDK,'--output',root/'bridge-dex',root/'bridge.jar')
        run(J/'java.exe','-jar',AT,'b','-p',S/'framework','-o',root/output,project)
    print('Both NativeActivity storage paths rebuilt. Shared configuration left untouched.')
