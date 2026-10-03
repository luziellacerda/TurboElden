from pathlib import Path
import os, subprocess, sys, shutil

BASE=Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
SRC=BASE/'source'
os.environ['IMAGINE_PATH']=(SRC/'imagine').as_posix()
os.environ['IMAGINE_SDK_PATH']=(BASE/'sdk').as_posix()
os.environ['EMUFRAMEWORK_PATH']=(SRC/'EmuFramework').as_posix()
os.environ['TEMP']=os.environ['TMP']=str(BASE)
(BASE/'logs').mkdir(exist_ok=True)

def run(args, log):
    with (BASE/'logs'/log).open('w',encoding='utf-8') as f:
        result=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT)
    if result.returncode:
        print((BASE/'logs'/log).read_text(errors='replace')[-13000:])
        raise SystemExit(result.returncode)
    print(log+' OK',flush=True)

for name in sys.argv[1:]:
    build=BASE/'native-build'/name
    run(['cmake','-S',SRC/name,'-B',build,'-G','Ninja Multi-Config',
         '-DCMAKE_CONFIGURATION_TYPES=Release', '-DCMAKE_DEFAULT_BUILD_TYPE=Release',
         '-DCMAKE_TOOLCHAIN_FILE='+str(BASE/'station-arm64.cmake'),
         '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'],name.replace('.','_')+'-configure.log')
    run(['cmake','--build',build,'--config','Release','--parallel','4'],name.replace('.','_')+'-build.log')
    if name in ('imagine','EmuFramework'):
        run(['cmake','--install',build,'--config','Release'],name+'-install.log')
    else:
        lib=build/'android/src/main/jniLibs/arm64-v8a/libmain.so'
        assert lib.exists(),lib
        out=BASE/('libsnes9x_explus.so' if name=='Snes9x' else 'libmdemu_station.so')
        shutil.copy2(lib,out)
        print('Built '+str(out),flush=True)
