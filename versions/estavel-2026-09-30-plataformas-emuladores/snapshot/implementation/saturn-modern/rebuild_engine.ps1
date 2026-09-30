$ErrorActionPreference = 'Stop'
$SaturnRoot = $PSScriptRoot
$env:TEMP = Join-Path $SaturnRoot 'tmp'
$env:TMP = $env:TEMP
$SaturnSource = Join-Path $SaturnRoot 'source/yabasanshiro-1.20.46/yabause'
$SaturnBuild = Join-Path $SaturnRoot 'build'
& 'C:/Program Files/CMake/bin/cmake.exe' -S $SaturnSource -B $SaturnBuild -G Ninja '-DCMAKE_TOOLCHAIN_FILE=E:/TurboEdenEngine/android-ndk-r28c/build/cmake/android.toolchain.cmake' '-DANDROID_ABI=arm64-v8a' '-DANDROID_PLATFORM=android-26' '-DANDROID_STL=c++_static' '-DCMAKE_BUILD_TYPE=Release' '-DCMAKE_POLICY_VERSION_MINIMUM=3.5' '-DYAB_PORTS=android' '-DYAB_WANT_OPENGL=OFF' '-DYAB_WANT_SDL=OFF' '-DYAB_WANT_OPENAL=OFF' '-DYAB_WANT_VULKAN=OFF' '-DYAB_WANT_DYNAREC_DEVMIYAX=ON' '-DHAVE_RETROACHIEVEMENTS=OFF' '-DYAB_TESTS=OFF' '-DSH2_TRACE=ON' '-DSH2_DYNAREC=OFF' '-DYAB_WANT_SH2_CACHE=ON' '-DYAB_EXEC_FROM_CACHE=ON' '-DCMAKE_POSITION_INDEPENDENT_CODE=ON' '-DCMAKE_C_FLAGS=-DHAVE_LIBGL=1 -Wno-error=int-conversion -Wno-error=incompatible-function-pointer-types' '-DCMAKE_CXX_FLAGS=-DHAVE_LIBGL=1'
if ($LASTEXITCODE -ne 0) { throw 'Saturn configuration failed' }
& 'C:/Program Files/CMake/bin/cmake.exe' --build $SaturnBuild --target turbo_saturn -j 6
if ($LASTEXITCODE -ne 0) { throw 'Saturn build failed' }
& 'E:/TurboEdenEngine/android-ndk-r28c/toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-strip.exe' --strip-unneeded -o (Join-Path $SaturnRoot 'libturbo_saturn.so') (Join-Path $SaturnBuild 'src/android/libturbo_saturn.so')
if ($LASTEXITCODE -ne 0) { throw 'Saturn strip failed' }
