param(
  [Parameter(Mandatory=$true)][string]$Stage,
  [Parameter(Mandatory=$true)][string]$Build,
  [string]$Ndk='E:\TurboEdenEngine\android-ndk-r28c',
  [string]$CMake='C:\Program Files\CMake\bin\cmake.exe',
  [ValidateSet(24,28)][int]$Api=24,
  [int]$Jobs=4
)
$ErrorActionPreference='Stop'
$stageRoot=[IO.Path]::GetFullPath($Stage)
$buildRoot=[IO.Path]::GetFullPath($Build)
if($stageRoot -eq $buildRoot -or !$stageRoot.StartsWith('G:\') -or !$buildRoot.StartsWith('G:\')) { throw 'Use separate new G: stage/build directories' }
$sourceReceipt=Get-Content -LiteralPath (Join-Path $stageRoot 'station-r126-source-receipt.json') -Raw | ConvertFrom-Json
$dependencyReceipt=Get-Content -LiteralPath (Join-Path $stageRoot 'station-r126-dependency-receipt.json') -Raw | ConvertFrom-Json
$hookReceipt=Get-Content -LiteralPath (Join-Path $stageRoot 'station-r126-hook-receipt.json') -Raw | ConvertFrom-Json
if($sourceReceipt.upstream -ne '5102a0339c2177575378107b76541e47cc52122d' -or !$dependencyReceipt.complete -or $hookReceipt.commit -ne '8fae8ce254dfc1344527e05301e43f37dea2df80') { throw 'Pinned source/dependencies/hooks are not complete' }
$toolchain=Join-Path $Ndk 'build\cmake\android.toolchain.cmake'
if(!(Test-Path -LiteralPath $toolchain)) { throw 'NDK toolchain missing' }
$ninja=(Get-Command ninja -ErrorAction Stop).Source
$cacheFile=Join-Path $buildRoot 'CMakeCache.txt'
if(Test-Path -LiteralPath $cacheFile) {
  $cachedApi=Select-String -LiteralPath $cacheFile -Pattern '^ANDROID_PLATFORM:STRING=(.+)$'
  if($cachedApi -and $cachedApi.Matches[0].Groups[1].Value -ne "android-$Api") { throw 'Use a fresh build directory when changing Android API; cached feature probes are API-dependent' }
}
$env:SOURCE_DATE_EPOCH='1790576668'
& $CMake -S $stageRoot -B $buildRoot -G Ninja "-DCMAKE_MAKE_PROGRAM=$ninja" "-DCMAKE_TOOLCHAIN_FILE=$toolchain" -DANDROID_ABI=arm64-v8a "-DANDROID_PLATFORM=android-$Api" -DANDROID_STL=c++_static -DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON -DCMAKE_BUILD_TYPE=Release -DENABLE_QT=OFF -DENABLE_SDL=OFF -DENABLE_TESTS=OFF -DENABLE_DISCORD_PRESENCE=OFF -DENABLE_ANALYTICS=OFF -DENABLE_AUTOUPDATE=OFF -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF -DUSE_UPNP=ON -DUSE_MGBA=ON -DUSE_RETRO_ACHIEVEMENTS=ON -DENABLE_CUBEB=ON -DENABLE_VULKAN=ON
if($LASTEXITCODE -ne 0) { throw 'Dolphin CMake configure failed; no binary is ready' }
& $CMake --build $buildRoot --target main --parallel $Jobs
if($LASTEXITCODE -ne 0) { throw 'Dolphin native build failed; no binary is ready' }
$library=Get-ChildItem -LiteralPath $buildRoot -Recurse -Filter libstation_dolphin_online.so | Select-Object -First 1
if(!$library) { throw 'Online-only target library not found' }
Get-FileHash -LiteralPath $library.FullName -Algorithm SHA256
