"""Rebuild only UI sources, with output and logs on E:. Does not install or deploy."""
from pathlib import Path
import subprocess,sys
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');N=R/'native';W=R/'ui-r8'
def run(args,log):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/log).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,p.stdout+p.stderr
run([r'C:\Program Files\LLVM\bin\clang.exe','--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384','-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',N/'native_carousel.cpp',N/'video720_posters.o','-L',N,'-lc','-ldl','-llog','-o',N/'libturbo_carousel.so'],'native-build.log')
run([sys.executable,R/'netplay/build_ui_r8.py'],'java-build.log')
print('Native and Java UI modules compiled on E:. Package separately.')
