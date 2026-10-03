"""Reproducible C dependencies for pinned Emu EX+ Alpha Android ARM64 build.

Only extracts/builds under --work/deps and installs into --work/sdk/android-arm64.
Upstream's libarchive CRC/UTF-8 patches and Android workarounds are preserved.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, tarfile

SOURCE = Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003\source\emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943\imagine\bundle\all\src')
WORK = Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
LLVM = Path(r'C:\Program Files\LLVM\bin')
NDK = Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64')
CMAKE = r'C:\Program Files\CMake\bin\cmake.exe'
PATCH = r'C:\Program Files\Git\usr\bin\patch.exe'
LIBS = [('libogg','1.3.6'),('libvorbis','1.3.7'),('flac','1.5.0'),('xz','5.8.3'),('libarchive','3.8.6')]
STATIC_LIBS = ['libogg.a','libvorbis.a','libvorbisfile.a','libvorbisenc.a','libFLAC.a','liblzma.a','libarchive.a']

def inspect_archive(path):
    data=path.read_bytes()
    if data[:8] != b'!<arch>\n': raise RuntimeError(f'Not an ar archive: {path}')
    pos=8; objects=0
    while pos < len(data):
        hdr=data[pos:pos+60]
        if hdr[58:60] != b'`\n': raise RuntimeError(f'Invalid member in {path}')
        name=hdr[:16].decode('ascii').strip(); size=int(hdr[48:58]); member=data[pos+60:pos+60+size]
        if name.startswith('#1/'): member=member[int(name[3:]):]
        if member.startswith(b'\x7fELF'):
            if member[4:6] != b'\x02\x01' or int.from_bytes(member[18:20],'little') != 183:
                raise RuntimeError(f'Non-ARM64 ELF member in {path}: {name}')
            objects+=1
        elif name not in ('/','//','/SYM64/') and not name.startswith('__.SYMDEF'):
            raise RuntimeError(f'Unexpected non-ELF member in {path}: {name}')
        pos += 60 + size + (size & 1)
    if not objects: raise RuntimeError(f'No ARM64 objects in {path}')
    return {'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'elf64_aarch64_objects':objects}

def run(cmd, logfile, **kwargs):
    with open(logfile, 'w', encoding='utf-8') as log:
        result = subprocess.run([str(x) for x in cmd], stdout=log, stderr=subprocess.STDOUT, **kwargs)
    if result.returncode:
        print(Path(logfile).read_text(encoding='utf-8', errors='replace')[-10000:])
        raise RuntimeError(f'Failed ({result.returncode}), see {logfile}')

def extract(name, version, deps):
    archive = SOURCE/name/f'{name}-{version}.tar.xz'
    dest = deps/'src'/f'{name}-{version}'
    if not dest.exists():
        with tarfile.open(archive) as tar:
            tar.extractall(deps/'src', filter='data')
    return dest

def main():
    p=argparse.ArgumentParser(); p.add_argument('--work',type=Path,default=WORK); p.add_argument('--prepare-only',action='store_true'); p.add_argument('--only',choices=[n for n,v in LIBS]); args=p.parse_args()
    deps=args.work/'deps'; sdk=args.work/'sdk'/'android-arm64'; deps.mkdir(parents=True,exist_ok=True); sdk.mkdir(parents=True,exist_ok=True)
    tc=deps/'android-arm64-clang22.cmake'
    # Generic Linux avoids CMake changing the selected compiler to the NDK's
    # clang19. Target and sysroot are explicit. NDK runtime builtins are used.
    tc.write_text(f'''set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER "{(LLVM/'clang.exe').as_posix()}")
set(CMAKE_CXX_COMPILER "{(LLVM/'clang++.exe').as_posix()}")
set(CMAKE_C_COMPILER_TARGET aarch64-linux-android26)
set(CMAKE_CXX_COMPILER_TARGET aarch64-linux-android26)
set(CMAKE_SYSROOT "{(NDK/'sysroot').as_posix()}")
set(CMAKE_AR "{(LLVM/'llvm-ar.exe').as_posix()}")
set(CMAKE_RANLIB "{(LLVM/'llvm-ranlib.exe').as_posix()}")
set(CMAKE_C_FLAGS_INIT "-fPIC")
set(CMAKE_CXX_FLAGS_INIT "-fPIC")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-fuse-ld=lld -resource-dir={NDK.as_posix()}/lib/clang/19")
set(CMAKE_SHARED_LINKER_FLAGS_INIT "-fuse-ld=lld -resource-dir={NDK.as_posix()}/lib/clang/19")
set(CMAKE_FIND_ROOT_PATH "{sdk.as_posix()}" "{(NDK/'sysroot').as_posix()}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
''',encoding='utf-8')
    for name,version in LIBS:
        if args.only and args.only != name: continue
        src=extract(name,version,deps)
        if name == 'libarchive' and not (src/'.station-upstream-patches').exists():
            for patch in ['libarchive-3.2.0-entry-crc32.patch','libarchive-3.2.1-force-utf8-charset.patch']:
                with open(SOURCE/name/patch,'rb') as stream:
                    run([PATCH,'--batch','--forward','-p1'],deps/f'{patch}.log',cwd=src,stdin=stream)
            shutil.copyfile(src/'contrib/android/include/android_lf.h',src/'libarchive/android_lf.h')
            (src/'.station-upstream-patches').write_text('CRC32 and force UTF-8 patches from pinned imagine bundle.\n')
        if args.prepare_only: continue
        build=deps/'build'/name
        flags=[f'-DCMAKE_TOOLCHAIN_FILE={tc}',f'-DCMAKE_INSTALL_PREFIX={sdk}',f'-DCMAKE_PREFIX_PATH={sdk}', '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DBUILD_SHARED_LIBS=OFF','-DBUILD_TESTING=OFF','-DCMAKE_POLICY_VERSION_MINIMUM=3.5']
        if name=='libogg': flags += ['-DINSTALL_DOCS=OFF','-DBUILD_DOCS=OFF']
        if name=='libvorbis': flags += ['-DBUILD_TESTING=OFF']
        if name=='flac': flags += ['-DBUILD_CXXLIBS=OFF','-DBUILD_PROGRAMS=OFF','-DBUILD_EXAMPLES=OFF','-DBUILD_TESTING=OFF','-DBUILD_DOCS=OFF','-DINSTALL_MANPAGES=OFF','-DWITH_OGG=ON','-DCMAKE_C_FLAGS=-fPIC -Dfseeko=fseek -Dftello=ftell']
        if name=='xz': flags += ['-DBUILD_TESTING=OFF','-DXZ_TOOL_XZ=OFF','-DXZ_TOOL_XZDEC=OFF','-DXZ_TOOL_LZMADEC=OFF','-DXZ_TOOL_LZMAINFO=OFF','-DXZ_TOOL_SCRIPTS=OFF','-DXZ_DOC=OFF','-DXZ_ENCODERS=lzma1;lzma2','-DXZ_DECODERS=lzma1;lzma2']
        if name=='libarchive': flags += ['-DENABLE_TEST=OFF','-DENABLE_TAR=OFF','-DENABLE_CPIO=OFF','-DENABLE_CAT=OFF','-DENABLE_UNZIP=OFF','-DENABLE_XATTR=OFF','-DENABLE_ACL=OFF','-DENABLE_BZip2=OFF','-DENABLE_ICONV=OFF','-DENABLE_LZ4=OFF','-DENABLE_ZSTD=OFF','-DENABLE_LZO=OFF','-DENABLE_NETTLE=OFF','-DENABLE_OPENSSL=OFF','-DENABLE_LIBXML2=OFF','-DENABLE_EXPAT=OFF','-DENABLE_LZMA=ON','-DENABLE_ZLIB=ON','-DCMAKE_C_FLAGS=-fPIC -Dset_statfs_transfer_size(a,b)=']
        print(f'Configuring {name}',flush=True)
        run([CMAKE,'--fresh','-S',src,'-B',build,'-G','Ninja',*flags],deps/f'{name}-configure.log')
        print(f'Building {name}',flush=True)
        run([CMAKE,'--build',build,'--parallel','4'],deps/f'{name}-build.log')
        run([CMAKE,'--install',build],deps/f'{name}-install.log')
        if name=='libarchive': (sdk/'include/android_lf.h').write_text('/* Upstream Android compatibility placeholder. */\n')
        print(f'Installed {name}',flush=True)
    report={
        'toolchain':'clang 22.1.8 headers/compiler, NDK r28c sysroot + linker builtins, aarch64-linux-android26',
        'source_commit':'1c12fac5ce49badaadff2e2f210dcc30b89f4943',
        'source_archives':{f'{name}-{version}.tar.xz':hashlib.sha256((SOURCE/name/f'{name}-{version}.tar.xz').read_bytes()).hexdigest() for name,version in LIBS},
        'patches':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (SOURCE/'libarchive').glob('*.patch')},
        'features':{
            'common':'static, PIC, Release, no programs/tests/docs',
            'vorbis':'Clang-incompatible -mno-ieee-fp is not used by CMake; original patch only changes autotools configure scripts',
            'flac':'native ARM64 NEON detection enabled; Ogg ON; no C++; upstream fseeko=fseek and ftello=ftell Android definitions',
            'xz':'LZMA1/LZMA2 encoders/decoders only, matching upstream configure selection',
            'libarchive':'upstream CRC32-entry and UTF-8 patches; ZLIB and LZMA; no xattr/ACL/BZip2/iconv/lz4/zstd/lzo/nettle/openssl/xml2/expat; upstream Android set_statfs_transfer_size definition'
        },
        'libraries':{name:inspect_archive(sdk/'lib'/name) for name in STATIC_LIBS if (sdk/'lib'/name).exists()}
    }
    (deps/'cdeps-build-report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
