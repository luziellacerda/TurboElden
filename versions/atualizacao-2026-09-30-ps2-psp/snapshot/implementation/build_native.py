import pathlib,subprocess,os
p=pathlib.Path(__file__).parent
clang=r'C:\Program Files\LLVM\bin\clang.exe'
os.environ['TEMP']=str(p/'tmp');os.environ['TMP']=str(p/'tmp');(p/'tmp').mkdir(exist_ok=True)
import sys
subprocess.run([sys.executable,str(p/'prepare_laser.py')],check=True)
subprocess.run([sys.executable,str(p/'space3d/prepare_shaders.py')],check=True)
model_inputs=[p/'space3d/f16-turborama/prepare_f16.py',p/'space3d/f16-source/f16-exterior-original.glb',p/'space3d/f16-turborama/f16-graphite-albedo-v1.png']
if not (p/'space3d_assets.h').exists() or max(x.stat().st_mtime for x in model_inputs)>(p/'space3d_assets.h').stat().st_mtime:
 subprocess.run([sys.executable,str(p/'space3d/f16-turborama/prepare_f16.py')],check=True)
common=[clang,'--target=aarch64-linux-android26','--sysroot=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot','-fuse-ld=lld','-shared','-fPIC','-nostdlib','-Wl,-z,max-page-size=16384']
# Import-only linker stubs; these are NOT packaged. Android provides the real system libraries.
libs={'c':['memcpy','memset','strlen','strcmp','mkdir','fopen','fwrite','fclose','mprotect','sysconf'], 'dl':['dlopen','dlsym','dladdr'],'log':['__android_log_print']}
for lib,syms in libs.items():
 src=p/(lib+'_imports.c');src.write_text('\n'.join('void '+s+'(void){}' for s in syms))
 subprocess.run(common+['-Wno-incompatible-library-redeclaration',str(src),'-Wl,-soname,lib'+lib+'.so','-o',str(p/('lib'+lib+'.so'))],check=True)
subprocess.run(common+['-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-stack-protector','-fno-builtin','-Wl,-z,defs','-Wl,-soname,libturbo_carousel.so',str(p/'native_carousel.cpp'),'-L'+str(p),'-lc','-ldl','-llog','-o',str(p/'libturbo_carousel.so')],check=True)
print('Built native module', (p/'libturbo_carousel.so').stat().st_size)
