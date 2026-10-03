from pathlib import Path
import subprocess,os,json,hashlib,urllib.request,tarfile
r=Path(__file__).resolve().parent
out=Path(os.environ.get('STATION_BUILD_DIR',r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build'))/'archive'
out.mkdir(parents=True,exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(out)
ndk=Path(os.environ.get('STATION_NDK',r'E:\TurboEdenEngine\android-ndk-r28c'))
cmake=r'C:\Program Files\CMake\bin\cmake.exe'
ninja=r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Ninja-build.Ninja_Microsoft.Winget.Source_8wekyb3d8bbwe\ninja.exe'
packages=[('xz','5.8.3','https://github.com/tukaani-project/xz/releases/download/v5.8.3/xz-5.8.3.tar.gz','3d3a1b973af218114f4f889bbaa2f4c037deaae0c8e815eec381c3d546b974a0'),('libarchive','3.8.9','https://github.com/libarchive/libarchive/releases/download/v3.8.9/libarchive-3.8.9.tar.gz','f5a6539059cf5e597dbeda37bfa4874b1e8dea063c8d93bf85a2b44af90a5bd4')]
for name,version,url,digest in packages:
    target=out/(name+'-'+version+'.tar.gz')
    if not target.exists():
        with urllib.request.urlopen(url,timeout=60) as response:target.write_bytes(response.read())
    if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise RuntimeError('Dependency digest mismatch: '+name)
    source=out/(name+'-'+version)
    if not source.exists():
        with tarfile.open(target) as archive:archive.extractall(out,filter='data')
common=['-G','Ninja','-DCMAKE_MAKE_PROGRAM='+ninja,'-DCMAKE_TOOLCHAIN_FILE='+str(ndk/'build/cmake/android.toolchain.cmake'),'-DANDROID_ABI=arm64-v8a','-DANDROID_PLATFORM=android-26','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DBUILD_SHARED_LIBS=OFF']
log=out/'build.log'
with log.open('w',encoding='utf-8') as stream:
 def run(args):
    print('Building '+str(args[1:4]),flush=True)
    subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT,check=True)
 run([cmake,'-S',str(out/'xz-5.8.3'),'-B',str(out/'xz-build')]+common+['-DBUILD_TESTING=OFF','-DXZ_TOOL_XZ=OFF','-DXZ_TOOL_XZDEC=OFF','-DXZ_TOOL_LZMADEC=OFF','-DXZ_TOOL_LZMAINFO=OFF','-DXZ_DOC=OFF','-DXZ_NLS=OFF'])
 run([cmake,'--build',str(out/'xz-build'),'--target','liblzma','-j','4'])
 lzma=out/'xz-build/liblzma.a'
 if not lzma.exists():raise RuntimeError('Missing built liblzma')
 disabled=['BZip2','LZ4','ZSTD','LZO','OPENSSL','MBEDTLS','NETTLE','LIBB2','LIBXML2','EXPAT','PCREPOSIX','PCRE2POSIX','ICONV','ACL','XATTR','TEST','TAR','CPIO','CAT','UNZIP']
 options=['-DENABLE_'+v+'=OFF' for v in disabled]+['-DENABLE_LZMA=ON','-DENABLE_ZLIB=ON','-DLIBLZMA_LIBRARY='+str(lzma),'-DLIBLZMA_INCLUDE_DIR='+str(out/'xz-5.8.3/src/liblzma/api')]
 run([cmake,'-S',str(out/'libarchive-3.8.9'),'-B',str(out/'archive-build')]+common+options)
 run([cmake,'--build',str(out/'archive-build'),'--target','archive_static','-j','4'])
 cc=ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
 output=out.parent/'native/arm64-v8a/libstation_archive.so';output.parent.mkdir(parents=True,exist_ok=True)
 run([str(cc),'--target=aarch64-linux-android26','-shared','-fPIC','-O2','-fvisibility=hidden','-Wall','-Wextra','-Werror','-I'+str(out/'libarchive-3.8.9/libarchive'),str(r/'src/native/station_archive.c'),str(out/'archive-build/libarchive/libarchive.a'),str(lzma),'-lz','-Wl,--no-undefined','-Wl,-z,max-page-size=16384','-Wl,--exclude-libs,ALL','-o',str(output)])
report={'packages':[{'name':n,'version':v,'url':u,'sha256':h} for n,v,u,h in packages],'library':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'size':output.stat().st_size}
(out/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
