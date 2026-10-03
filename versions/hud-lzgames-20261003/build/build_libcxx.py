"""Build the pinned upstream EX+ libc++ runtime for arm64 Android on Windows.

Replicates imagine/bundle/all/src/libcxx/common.mk without Unix Make/autoconf.
Only writes the HUD deps/libcxx-* trees and sdk/android-arm64 runtime files.
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
DEPS = ROOT / 'deps'
SRC_BASE = Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003\source\emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943\imagine\bundle\all\src\libcxx')
ARCHIVE = SRC_BASE / 'llvm-project-libcxx-22.1.0.src.tar.xz'
SOURCE = DEPS / 'libcxx-source' / 'llvm-project-22.1.0.src'
BUILD = DEPS / 'libcxx-build'
SDK = ROOT / 'sdk' / 'android-arm64'
LLVM = Path(r'C:\Program Files\LLVM\bin')
NDK = Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64')
SYSROOT = NDK / 'sysroot'
CMAKE = shutil.which('cmake')
NINJA = shutil.which('ninja')
TARGET = 'aarch64-none-linux-android26'

def run(argv, name):
    print(name, flush=True)
    p = subprocess.run([str(a) for a in argv], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (BUILD / (name + '.log')).write_text(p.stdout, encoding='utf-8')
    if p.returncode:
        print(p.stdout[-14000:], flush=True)
        raise RuntimeError(f'{name} failed: {p.returncode}')
    print(p.stdout[-1000:], flush=True)

def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    if not (SOURCE / 'libcxx' / 'CMakeLists.txt').exists():
        SOURCE.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(ARCHIVE) as tar:
            tar.extractall(SOURCE.parent, filter='data')
    # Exact upstream unwind patch; inactive on arm64, but retain source recipe.
    personality = SOURCE / 'libcxxabi/src/cxa_personality.cpp'
    data = personality.read_text(encoding='utf-8')
    needle = '#else\n\n// Helper function to unwind one frame.'
    replacement = '#else\n\nextern "C" _Unwind_Reason_Code __gnu_unwind_frame(_Unwind_Exception*,\n                                                  _Unwind_Context*);\n\n// Helper function to unwind one frame.'
    if needle in data:
        personality.write_text(data.replace(needle, replacement, 1), encoding='utf-8')
    elif replacement not in data:
        raise RuntimeError('Upstream unwind patch location missing')
    cflags = ['--target=' + TARGET, '--sysroot=' + SYSROOT.as_posix(), '-fPIC', '-fvisibility=hidden', '-ffunction-sections', '-fdata-sections', '-O3']
    cxxflags = cflags + ['-nostdinc++', '-I' + (SOURCE / 'libcxxabi/include').as_posix(), '-I' + (SOURCE / 'libc').as_posix(), '-Wno-user-defined-literals', '-U_LIBCPP_LINK_PTHREAD_LIB', '-U_LIBCPP_LINK_RT_LIB']
    # CMake cache flags need shell quoting independently of subprocess list args.
    quote_flags = lambda flags: ' '.join('"' + f + '"' if ' ' in f else f for f in flags)
    configure = [CMAKE, '-S', SOURCE / 'libcxx', '-B', BUILD, '-G', 'Ninja',
        '-DCMAKE_MAKE_PROGRAM=' + NINJA,
        '-DPython3_EXECUTABLE=' + Path(sys.executable).as_posix(),
        '-DCMAKE_SYSTEM_NAME=Linux', '-DCMAKE_SYSTEM_PROCESSOR=aarch64',
        '-DCMAKE_C_COMPILER=' + (LLVM/'clang.exe').as_posix(),
        '-DCMAKE_CXX_COMPILER=' + (LLVM/'clang++.exe').as_posix(),
        '-DCMAKE_C_COMPILER_TARGET=' + TARGET, '-DCMAKE_CXX_COMPILER_TARGET=' + TARGET,
        '-DCMAKE_AR=' + (LLVM/'llvm-ar.exe').as_posix(),
        '-DCMAKE_RANLIB=' + (LLVM/'llvm-ranlib.exe').as_posix(),
        '-DCMAKE_SYSROOT=' + SYSROOT.as_posix(),
        '-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY',
        '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_C_FLAGS=' + quote_flags(cflags),
        '-DCMAKE_CXX_FLAGS=' + quote_flags(cxxflags),
        '-DLIBCXX_ENABLE_SHARED=OFF', '-DLIBCXX_CXX_ABI=libcxxabi', '-DLLVM_INCLUDE_TESTS=OFF',
        '-DLIBCXX_INCLUDE_TESTS=OFF', '-DLIBCXX_ENABLE_EXPERIMENTAL_LIBRARY=OFF',
        '-DLIBCXX_ENABLE_DEBUG_MODE_SUPPORT=OFF', '-DLIBCXX_ABI_UNSTABLE=ON',
        '-DLIBCXX_ENABLE_INCOMPLETE_FEATURES=ON', '-DLIBCXX_HERMETIC_STATIC_LIBRARY=ON',
        '-DLIBCXX_INCLUDE_BENCHMARKS=OFF', '-DLIBCXX_ENABLE_TIME_ZONE_DATABASE=OFF',
        '-DLIBCXX_INSTALL_MODULES=ON', '-DLIBCXX_CXX_ABI_INCLUDE_PATHS=' + (SOURCE/'libcxxabi/include').as_posix()]
    run(configure, 'configure-libcxx')
    run([CMAKE, '--build', BUILD, '--parallel', '6'], 'build-libcxx')
    abi_names = '''abort_message cxa_aux_runtime cxa_default_handlers cxa_demangle cxa_exception cxa_exception_storage cxa_guard cxa_handlers cxa_personality cxa_thread_atexit cxa_vector cxa_virtual fallback_malloc private_typeinfo stdlib_exception stdlib_new_delete stdlib_stdexcept stdlib_typeinfo'''.split()
    abi_dir = BUILD / 'abi-objects'
    abi_dir.mkdir(exist_ok=True)
    abi_flags = cxxflags + ['-std=gnu++26', '-DHAVE___CXA_THREAD_ATEXIT_IMPL', '-D_LIBCPP_DISABLE_EXTERN_TEMPLATE', '-D_LIBCPP_BUILDING_LIBRARY', '-D_LIBCXXABI_BUILDING_LIBRARY', '-I'+(SOURCE/'libcxx/src').as_posix(), '-I'+(BUILD/'include/c++/v1').as_posix()]
    def compile_abi(name):
        argv = [LLVM/'clang++.exe', *abi_flags, '-c', SOURCE/'libcxxabi/src'/(name+'.cpp'), '-o', abi_dir/(name+'.o')]
        run(argv, 'abi-'+name)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(compile_abi, abi_names))
    run([LLVM/'llvm-ar.exe', 'rcs', BUILD/'lib/libc++abi.a', *[abi_dir/(n+'.o') for n in abi_names]], 'archive-libcxxabi')
    (SDK/'lib').mkdir(parents=True, exist_ok=True)
    for n in ('libc++.a','libc++abi.a','libc++experimental.a','libc++.modules.json'):
        shutil.copy2(BUILD/'lib'/n, SDK/'lib'/n)
    shutil.copytree(BUILD/'include/c++/v1', SDK/'include/c++/v1', dirs_exist_ok=True)
    shutil.copytree(BUILD/'modules/c++/v1', SDK/'share/libc++/v1', dirs_exist_ok=True)
    shutil.copytree(SOURCE/'libcxxabi/include', SDK/'include/c++/v1', dirs_exist_ok=True)
    for n in ('std', 'std.compat'):
        shutil.copytree(SRC_BASE/n, SDK/'share/libc++/v1'/n, dirs_exist_ok=True)
    result = {'archive_sha256': hashlib.file_digest(ARCHIVE.open('rb'), 'sha256').hexdigest(), 'target':TARGET,
              'libcxx_version':'22.1.0', 'abi_namespace':'__2', 'sdk':str(SDK),
              'configure_command':[str(x) for x in configure], 'runtime_c_flags':cflags,
              'runtime_cxx_flags':cxxflags, 'abi_cxx_flags':abi_flags,
              'runtime_codegen_note':'O3 PIC, hidden symbols and per-function/data sections. No fast-math, LTO, or upstream optional removal of stack/unwind/thread-static safeguards in the C++ runtime. Engine/framework codegen is configured separately.',
              'libraries':{n:hashlib.file_digest((SDK/'lib'/n).open('rb'),'sha256').hexdigest() for n in ('libc++.a','libc++abi.a','libc++experimental.a')}}
    (BUILD/'libcxx-build-receipt.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
