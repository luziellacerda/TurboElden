R147 final — recipe correction after a rejected baseline, no gameplay change

New publication scope:
 integration/dolphin-boot-cleanup-r147-20261014-final
New productive output namespace:
 E:/StationDolphinBootCleanupR147Final-20261014

The failed preliminary frozen6b4eab scope/output remains intact and must not be
used as a qualified baseline. No final APK or repaired motor was produced there.

Four native source pins are MainAndroid.cpp, build_native.py, the CMake override
and native-scope.json. MainAndroid retains the same approved single boot-flag
clear in null BootSessionData early return. Its whole-file inverse still restores
the original272bd5a... Main; successful Run/Stop/Surface/CPU/options are intact.

Two concrete recipe defects prevented the original baseline byte reproduction:
 - CMake bracket argument forwarding discarded an initial newline, removing
   all37 blank lines (74CRLF bytes) from generated zconf.h. Quoted original ARGV
   references now forward file/add_custom_command arguments without parsing
   their content again. Original Windows WRITE/APPEND text semantics remain.
 - mGBA overwrites target COMPILE_OPTIONS with its existing FEATURE_FLAGS,
   dropping the inherited compiler metadata path map. A deferred PRIVATE map
   is appended solely to that target after the original override. Original
   feature/CPU/compiler optimization flags are retained.

The old94 generated inputs had90 identical bytes; the only differences were
zconf.h and three dependent archives. Runtime.text/rodata were identical, while
DWARF/build-id differed. The new recipes preserve94/92b/f7 gates, without changing
runtime bytes by patch or allowing a merely equivalent baseline.

Evidence includes the inverse to the frozen6b CMake file, eight isolated
leading-newline/semicolon/quote/backslash/literal-variable and source-guard
fixtures, plus the actual closed Android configure/single mGBA version object
qualification. The latter verifies the original zconf hash63a4b8f... and the
original object byte exactly, without building the whole motor or the approved
productive MainAndroid source.

Mandatory original full baseline:
 unstripped92b1951facb9fca6aad644026c47adcc62e09c9b5aca61629aab7e1515a270fe
 strippedf7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d
 all four Adrenotools hooks byte exact; all94 generated files byte exact.
94 means46.a,34.o,11.h,2.c,1.so, not merely headers. The productive phase may
change only MainAndroid.cpp.o among these94 (other93 exact); it is a direct main
link input, not an archive member. The only generated.so is hook_impl, retained.
The productive core must preserve exports/deps/SONAME/16KiB and inverse/source
closure while differing by the authorized source insertion.

CLI after root copies/freezes the full final source:
 python -B <finalscope>/recipe/build_native.py
 --base-apk F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R146-relay-direto-online-20261014.apk
 --source-stage G:/StationDolphinR126/stage
 --original-build G:/StationDolphinR126/build24
 --parent-native G:/StationDolphinR126/final-native
 --build-closure <workspace>/work/r146-audit-private/dolphin-build-closure/closed-build-inputs-and-plan.json
 --source-closure <workspace>/work/r146-audit-private/dolphin-build-closure/source-tree-inputs.json
 --graph-closure <workspace>/work/r146-audit-private/dolphin-build-closure/actual-build-graph-final/graph-inputs-private.json
 --ndk E:/TurboEdenEngine/android-ndk-r28c
 --source-commit <actual40hex full-final freeze>
 --out E:/StationDolphinBootCleanupR147Final-20261014/native-baseline-final2
 --jobs 4 --baseline-only

The above output must be absent. Compiler
cache remains OFF; original archived objects serve comparison, not recompilation.
Productive build uses a distinct fresh output and --qualified-baseline only from
this exact final recipe/source map/closures after all original hashes pass.

Baseline-only validates its own complete tracked final bytes; productive requires
common.verify_commit() global pins. Enable PYTHONDONTWRITEBYTECODE=1. Original
Gstage file-set/hashes/absences are checked before/after, assets go to fresh
packaging-assets, source scmrev.h removal is a checked absent no-op. No other
source-stage write/remove is allowed. This builder never assembles/signs/installs
an APK, contacts server/USB, updates Git or promotes stable R143/ATUAL.
