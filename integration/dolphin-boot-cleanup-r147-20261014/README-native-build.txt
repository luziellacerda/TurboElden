R147 native draft — full donor reproduction followed by one-line boot cleanup

Do not execute this private draft. Copy into a fresh committed scope
work/publication-app/integration/dolphin-boot-cleanup-r147-20261014 and freeze it
with the final/intermediate source commit before executing. Original R126 stage,
build24, final-native, R145 and R146 are not modified.

Productive source_map() has exactly four files:
 native/Source/Android/jni/MainAndroid.cpp
 recipe/build_native.py
 recipe/StationDolphinMainAndroidOverride.cmake
 evidence/native-scope.json

Additional source/evidence files in this scope are also required to equal the
frozen Git commit. Baseline-only verifies its own complete tracked source map;
it does not need final Java/packaging/common.py. Productive final compilation
must validate common.verify_commit() and record the global final source map.
Baseline and patched host fixtures concern boot-flag ownership
only; they do not claim Android gameplay or device performance.

CLI common inputs, using the actual qualified R146 APK:
 --base-apk F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R146-relay-direto-online-20261014.apk
 --source-stage G:/StationDolphinR126/stage
 --original-build G:/StationDolphinR126/build24
 --parent-native G:/StationDolphinR126/final-native
 --build-closure <workspace>/work/r146-audit-private/dolphin-build-closure/closed-build-inputs-and-plan.json
 --source-closure <workspace>/work/r146-audit-private/dolphin-build-closure/source-tree-inputs.json
 --graph-closure <workspace>/work/r146-audit-private/dolphin-build-closure/actual-build-graph-final/graph-inputs-private.json
 --ndk E:/TurboEdenEngine/android-ndk-r28c
 --source-commit <40-character frozen final or native-intermediate commit>
 --jobs 4

Run only the original full baseline while Java ownership remains in preparation:
 --baseline-only
 --out E:/StationDolphinBootCleanupR147-20261014/native-baseline-<fresh-name>

This emits native-baseline-receipt.json after all original hashes pass. The full
main target and four dependencies are rebuilt in a fresh directory. Compiler
cache is OFF, object reuse is absent. Both the complete unstripped original
92b1951facb9fca6aad644026c47adcc62e09c9b5aca61629aab7e1515a270fe
and the actual APK motor
f7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d
must reproduce byte exactly. Four Adrenotools hooks must also match byte exactly.
SONAME, dynamic symbols, dependency lists and 16KiB loads must remain identical.
All 94 generated files must match their original hashes in the baseline:
46 archives (.a), 34 objects (.o), 11 headers (.h), 2 sources (.c), 1 hook (.so).
In the productive phase, exactly the MainAndroid.cpp.o compiled from the frozen
overlay is allowed to change; the other 93 files must still be byte exact. The
object is a direct main link input, not an archive member. The only generated
.so is hook_impl, which remains byte exact. The resulting core is qualified
separately against the original ELF contract. Source file-set and hashes are
verified before and after compile. Do not relax these gates if a path/build-ID issue
appears. Retain failed output and resolve reproducibility first.

After the complete R147 source, including any approved Java ownership methods,
is frozen, compile the productive motor in a different fresh output directory:
 --qualified-baseline <exact prior native-baseline-receipt.json>
 --out E:/StationDolphinBootCleanupR147-20261014/native-final-<fresh-name>

Reuse is permitted only if the native four-file map and every private source,
tool/dependency/graph receipt are identical, the old native-intermediate commit
is an ancestor of the new source freeze and the qualified baseline files still
have their hashes. Otherwise build the full baseline again in a fresh directory.

The original source stage is used read-only. Static review scanned all CMake
files, including the 140 parsed by original configure, and reviewed 15 process
statements plus the 3 reachable build-time CMake scripts. Install, network,
formatting and documentation targets are not executed by the main target.
mbedtls source-link creation is disabled by retained ENABLE_TESTING=OFF. The two
zlib source headers that would trigger source renames remain absent; unexpected
source mutations fail closed. The frozen CMake include restores
the original names solely in C/C++ macro/debug paths and defers a main-target
source-list substitution for exactly one MainAndroid.cpp. It preserves every
other source path and all original feature/runtime/optimization flags, including
Core settings, GPU, JIT/caches and DataDir. The original four assets packaging
commands are redirected to the fresh phase packaging-assets directory. Exact
source scmrev.h removal is a no-op only while the original file is absent;
no deletion in the original G source is delegated. All other direct file and
configure/custom-command output writes must stay in fresh outputs. Eight host
CMake safety fixtures passed without configuring or compiling the real stage.
There is no byte patch of a .so.

Productive native-receipt.json schema:
 station.r147.dolphin.boot-cleanup.native.v1
 baselineNativeSha256 = f7ebe048...
 outputNativeSha256 = actual new qualified core
 baselineReproduced = {dolphinCore:true, allFourHooks:true}
 passed/compiled true only after actual productive target completion
 sourceCommit/sourceSha256/completeFrozenSourceFiles, full private closure pins
 inverseWholeFilePassed and originalSourceStageExactlyPreserved
 exportedSymbolsExactlyPreserved/dependenciesExactlyPreserved/sonameExactlyPreserved
 nativeLoadAlignment16384, baselinePayloads/payloads
 baselineGeneratedInputSha256 / generatedInputSha256 (same original94keys)
 approvedGeneratedObjectDelta = {originalRelativePath,productiveRelativePath,
   baselineSha256,productiveSha256,compiledSourceSha256}; unchangedGeneratedInputs93
 originalPackagingAssetsRedirected:true, inTreeScmrevAbsencePreserved:true
 frontendChanged:false, dexChanged:false, cpuJitCacheOptionsControllersProfilesNetworkChanged:false
 androidExecuted:false, physicalGameplayVerified:false

New core hash requires the current final identity fingerprints, engine descriptor
and server kit, including all actual core/dependency and DEX hashes. This builder
does not assemble/sign/install an APK, update Git, change profile approval,
operate USB, contact the server or apply a registry/deployment.
