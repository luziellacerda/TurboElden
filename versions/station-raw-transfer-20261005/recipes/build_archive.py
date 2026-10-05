#!/usr/bin/env python3
"""Same pinned libarchive/xz as R16; only ZIP body CRC policy changes."""
import argparse,hashlib,json,platform,subprocess,tarfile,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--ndk',required=True,type=Path)
p.add_argument('--generator',default='Unix Makefiles');p.add_argument('--make-program');p.add_argument('--cmake',default='cmake');a=p.parse_args()
out=a.output.resolve();assert not out.exists(),'Use a new output directory';out.mkdir(parents=True)
root=Path(__file__).resolve().parents[1]
packages=[('xz','5.8.3','https://github.com/tukaani-project/xz/releases/download/v5.8.3/xz-5.8.3.tar.gz','3d3a1b973af218114f4f889bbaa2f4c037deaae0c8e815eec381c3d546b974a0'),('libarchive','3.8.9','https://github.com/libarchive/libarchive/releases/download/v3.8.9/libarchive-3.8.9.tar.gz','f5a6539059cf5e597dbeda37bfa4874b1e8dea063c8d93bf85a2b44af90a5bd4')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,version,url,digest in packages:
 print('Fetching pinned '+name+' '+version,flush=True)
 path=out/(name+'-'+version+'.tar.gz')
 with urllib.request.urlopen(url,timeout=45) as response:data=response.read(32*1024*1024+1)
 assert len(data)<=32*1024*1024 and hashlib.sha256(data).hexdigest()==digest,'Dependency differs'
 path.write_bytes(data)
 with tarfile.open(path) as source:source.extractall(out,filter='data')
common=['-G',a.generator,'-DCMAKE_TOOLCHAIN_FILE='+str(a.ndk/'build/cmake/android.toolchain.cmake'),'-DANDROID_ABI=arm64-v8a','-DANDROID_PLATFORM=android-26','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DBUILD_SHARED_LIBS=OFF']
if a.make_program:common.append('-DCMAKE_MAKE_PROGRAM='+a.make_program)
def run(args,label):
 print(label,flush=True)
 with (out/(label+'.log')).open('w') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
run([a.cmake,'-S',str(out/'xz-5.8.3'),'-B',str(out/'xz-build'),*common,'-DBUILD_TESTING=OFF','-DXZ_TOOL_XZ=OFF','-DXZ_TOOL_XZDEC=OFF','-DXZ_TOOL_LZMADEC=OFF','-DXZ_TOOL_LZMAINFO=OFF','-DXZ_DOC=OFF','-DXZ_NLS=OFF'],'configure-xz')
run([a.cmake,'--build',str(out/'xz-build'),'--target','liblzma','--parallel','4'],'build-xz')
lzma=out/'xz-build/liblzma.a';assert lzma.is_file()
disabled=['BZip2','LZ4','ZSTD','LZO','OPENSSL','MBEDTLS','NETTLE','LIBB2','LIBXML2','EXPAT','PCREPOSIX','PCRE2POSIX','ICONV','ACL','XATTR','TEST','TAR','CPIO','CAT','UNZIP']
run([a.cmake,'-S',str(out/'libarchive-3.8.9'),'-B',str(out/'archive-build'),*common,*['-DENABLE_'+n+'=OFF' for n in disabled],'-DENABLE_LZMA=ON','-DENABLE_ZLIB=ON','-DLIBLZMA_LIBRARY='+str(lzma),'-DLIBLZMA_INCLUDE_DIR='+str(out/'xz-5.8.3/src/liblzma/api')],'configure-archive')
run([a.cmake,'--build',str(out/'archive-build'),'--target','archive_static','--parallel','4'],'build-archive')
host='windows-x86_64' if platform.system()=='Windows' else 'linux-x86_64'
cc=a.ndk/'toolchains/llvm/prebuilt'/host/'bin'/('clang.exe' if platform.system()=='Windows' else 'clang')
library=out/'libstation_archive.so'
run([str(cc),'--target=aarch64-linux-android26','-shared','-fPIC','-O2','-fvisibility=hidden','-Wall','-Wextra','-Werror','-I'+str(out/'libarchive-3.8.9/libarchive'),str(root/'native/station_archive.c'),str(out/'archive-build/libarchive/libarchive.a'),str(lzma),'-lz','-Wl,--no-undefined','-Wl,-z,max-page-size=16384','-Wl,--exclude-libs,ALL','-o',str(library)],'link-jni')
report={'packages':[{'name':n,'version':v,'url':u,'sha256':h} for n,v,u,h in packages],'sha256':sha(library),'bytes':library.stat().st_size,'sourceSha256':sha(root/'native/station_archive.c'),'target':'Android arm64 API26; 16KiB max page size','zipBodyCRC32Enabled':False,'apkSignedOrInstalled':False}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
