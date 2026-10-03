from pathlib import Path
import shutil, json, hashlib

BASE = Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
UPSTREAM = Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003\source\emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943')
SRC = BASE / 'source'
BASE.mkdir(parents=True, exist_ok=True)
for name in ['imagine', 'EmuFramework', 'Snes9x', 'MD.emu']:
    if not (SRC/name).exists():
        shutil.copytree(UPSTREAM/name, SRC/name, ignore=shutil.ignore_patterns('bundle', 'build', '.git'))

cfg = SRC/'imagine/cmake/config.cmake'
s = (UPSTREAM/'imagine/cmake/config.cmake').read_text()
s = s.replace('451f2fe2-a8a2-47c3-bc32-94786d8fc91b', 'f35a9ac6-8463-4d38-8eec-5d6008153e7d')
start = s.index('\texecute_process(', s.index('function(generateConfigHeader'))
end = s.index('\ttarget_include_directories', start)
s = s[:start] + '''\tfile(MAKE_DIRECTORY "${genDir}")
\tset(configText "#pragma once\\n")
\tgetProp(defs ${target} configEnable)
\tforeach(def IN LISTS defs)
\t\tstring(REPLACE "=" " " def "${def}")
\t\tstring(APPEND configText "#define ${def} 1\\n")
\tendforeach()
\tgetProp(defs ${target} configDisable)
\tforeach(def IN LISTS defs)
\t\tstring(APPEND configText "#define ${def} 0\\n")
\tendforeach()
\tgetProp(incs ${target} configInc)
\tforeach(inc IN LISTS incs)
\t\tstring(APPEND configText "#include ${inc}\\n")
\tendforeach()
\tstring(APPEND configText "#define IMAGINE_VERSION_BASE \\"${PROJECT_VERSION}\\"\\n")
\tif(EXISTS "${configFilePath}")
\t\tfile(READ "${configFilePath}" oldConfigText)
\tendif()
\tif(NOT "${oldConfigText}" STREQUAL "${configText}")
\t\tfile(WRITE "${configFilePath}" "${configText}")
\tendif()
''' + s[end:]
s = s.replace('COMMAND pkg-config ', 'COMMAND C:/Python314/python.exe "${IMAGINE_PATH}/cmake/station_pkgconfig.py" ')
s = s.replace('string(REPLACE " " ";" pkgConfigCFlagsOutput "${pkgConfigCFlagsOutput}")', 'separate_arguments(pkgConfigCFlagsOutput UNIX_COMMAND "${pkgConfigCFlagsOutput}")')
s = s.replace('string(REPLACE " " ";" pkgConfigLibsOutput "${pkgConfigLibsOutput}")', 'separate_arguments(pkgConfigLibsOutput UNIX_COMMAND "${pkgConfigLibsOutput}")')
s = s.replace('target_link_libraries(${target} PRIVATE $<$<CONFIG:${config}>:${pkgConfigLibsOutput}>)', '''foreach(flag IN LISTS pkgConfigLibsOutput)
                        if(flag MATCHES "^-L(.+)")
                            target_link_directories(${target} PRIVATE "${CMAKE_MATCH_1}")
                        else()
                            target_link_libraries(${target} PRIVATE "$<$<CONFIG:${config}>:${flag}>")
                        endif()
                    endforeach()''')
s = s.replace('${CMAKE_BINARY_DIR}/../android${GEN_TARGET_EXT}/src/main/jniLibs/',
              '${CMAKE_BINARY_DIR}/android${GEN_TARGET_EXT}/src/main/jniLibs/')
cfg.write_text(s)
shutil.copy2(Path(__file__).with_name('station_pkgconfig.py'), cfg.with_name('station_pkgconfig.py'))

# Common upstream configuration, using a Windows-host compiler and Android target.
sdk = (BASE/'sdk/android-arm64').as_posix()
sysroot = 'E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/sysroot'
ndkbin = 'E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/bin'
toolchain = f'''include("{(SRC/'imagine/cmake/config.cmake').as_posix()}")
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_ANDROID_ARCH_ABI arm64-v8a)
set(ENV android)
set(ENV_KERNEL linux)
set(ARCH aarch64)
set(SUBARCH arm64)
set(CTARGET aarch64-linux-android)
set(ANDROID_CTARGET aarch64-none-linux-android26)
set(ANDROID_NDK_SDK 26)
set(CMAKE_C_COMPILER "C:/Program Files/LLVM/bin/clang.exe")
set(CMAKE_CXX_COMPILER "C:/Program Files/LLVM/bin/clang++.exe")
set(CMAKE_C_COMPILER_TARGET aarch64-linux-android26)
set(CMAKE_CXX_COMPILER_TARGET aarch64-linux-android26)
set(CMAKE_CXX_STANDARD_LIBRARY libc++)
set(CMAKE_SYSROOT "{sysroot}")
set(CMAKE_AR "C:/Program Files/LLVM/bin/llvm-ar.exe")
set(CMAKE_RANLIB "C:/Program Files/LLVM/bin/llvm-ranlib.exe")
set(CMAKE_STRIP "C:/Program Files/LLVM/bin/llvm-strip.exe")
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_SKIP_RPATH ON)
set(USE_EXTERNAL_LIBCXX 1)
set(CMAKE_CXX_STDLIB_MODULES_JSON "{sdk}/lib/libc++.modules.json")
set(CFLAGS_CODEGEN "-target aarch64-linux-android26 -no-canonical-prefixes")
set(CFLAGS_COMMON "-DANDROID -Wno-error=deprecated-declarations")
set(LDFLAGS "-fuse-ld=lld -Wl,-z,max-page-size=16384 -Wl,-z,noexecstack,-z,relro,-z,now,--warn-shared-textrel,--fatal-warnings -Wl,-O3,--gc-sections,--icf=all,--as-needed,--lto-whole-program-visibility,--exclude-libs=ALL -L\\"{sdk}/lib\\" -L\\"{sysroot}/usr/lib/aarch64-linux-android/26\\" -L\\"{sysroot}/usr/lib/aarch64-linux-android\\" -resource-dir=E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/lib/clang/19")
include("{(SRC/'imagine/cmake/clang.cmake').as_posix()}")
'''
(BASE/'station-arm64.cmake').write_text(toolchain)
compiler = SRC/'imagine/cmake/compiler-common.cmake'
s = (UPSTREAM/'imagine/cmake/compiler-common.cmake').read_text().replace('${IMAGINE_SDK_PLATFORM_PATH}/lib/pkgconfig:${PKG_CONFIG_PATH}', '${IMAGINE_SDK_PLATFORM_PATH}/lib/pkgconfig')
s = s.replace('-isystem ${IMAGINE_SDK_PLATFORM_PATH}/include/c++/v1', '-isystem \\"${IMAGINE_SDK_PLATFORM_PATH}/include/c++/v1\\"')
s = s.replace('set(CMAKE_CXX_COMPILER_ID_ARG1 -B "${IMAGINE_SDK_PLATFORM_PATH}/lib")', '# modules json passed explicitly by the Windows toolchain')
compiler.write_text(s)
s = s.replace(' -gz ', ' ')
compiler.write_text(s)
app = SRC/'imagine/src/base/android/Application.cc'
s = app.read_text(encoding='utf-8')
# NDK28 JNINativeMethod.fnPtr is void*: C++ constant evaluation rejects its
# function-pointer cast. A static const table retains the same JNI callbacks.
s = s.replace('static constexpr JNINativeMethod method[]', 'static const JNINativeMethod method[]')
app.write_text(s,encoding='utf-8',newline='\n')
# ZIP extraction on Windows materializes this upstream symlink as link text.
(SRC/'MD.emu/emuFrameworkUtils.cmake').write_text('include("${CMAKE_CURRENT_LIST_DIR}/../EmuFramework/emuFrameworkUtils.cmake")\n')
# Source headers must win over a previous engine's installed SDK headers.
for rel in ('imagine/CMakeLists.txt', 'EmuFramework/CMakeLists.txt'):
    p=SRC/rel
    s=p.read_text().replace('target_include_directories(imagine PRIVATE include)',
        'target_include_directories(imagine BEFORE PRIVATE include)').replace(
        'target_include_directories(emuframework PRIVATE include)',
        'target_include_directories(emuframework BEFORE PRIVATE include)')
    p.write_text(s)
print(json.dumps({'source':str(SRC), 'sdk':sdk, 'toolchain':str(BASE/'station-arm64.cmake')}))
