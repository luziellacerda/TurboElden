R145 native build — reviewed draft; do not execute from this private preparation

Stage the complete scope as integration/sky-blue-waves-r145-20261013 and freeze
every productive source and consumed evidence in a new full Git commit. The
common.verify_commit guard rejects this private directory and any unfrozen file.
The native source subset is exactly three headers plus recipe/build_native.py;
the full common guard also pins the palette/scope/inverse/key evidence.

Use the existing tools and original closed native inputs. The first example
must be run from the restored/current publication-app checkout after freeze:

python -B integration/sky-blue-waves-r145-20261013/recipe/build_native.py ^
  --base-apk F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R144-ondas-paletas-20261013.apk ^
  --r133-native G:/StationNormalOwnersR127/console-panel-r133/native ^
  --native-inputs F:/TurboStations-Backup-Completo-20261011/reconstrucao/native-inputs ^
  --generated-native G:/StationNormalOwnersR127/local-sony-demos/payloads-next/native ^
  --media-inputs G:/StationNormalOwnersR127/local-sony-demos/media-inputs ^
  --ndk F:/TurboStations-Backup-Completo-20261011/ferramentas/ndk-r28c ^
  --parent-r144-native-receipt E:/StationWavePaletteR144-20261013/native/final/native-receipt.json ^
  --parent-r144-final-proof E:/StationWavePaletteR144-20261013/assembly/final-apk-proof.json ^
  --source-commit FULL_NEW_R145_SOURCE_COMMIT ^
  --out E:/StationSkyBlueWavesR145-20261013/native/final

The caret syntax above is for cmd.exe. In PowerShell use a single line or its
normal argument continuation syntax. No shell is invoked by the Python recipe.
--parent-native is an exact alias of --r133-native; it always means the original
R133 native directory, not the R144 receipt directory. Both R144 receipt flags
are required and their exact hashes are checked before any compilation.

For relocated recovery inputs, --input-map accepts the original R133 logical
153-input/path mapping. All original SHA pins remain mandatory; four generated
R133 overlay files and the unchanged Sony offline route complete the 158-input
parent closure. Point --r133-native to the copied parent receipt/overlay tree.

Stages:
1. Check the exact signed R144 APK, frozen R144 14-source map at commit 1ac3f7d2,
   native receipt a885ba6b, final proof 24092e44, and every original input pin.
2. Recompile R133 baf0f07c byte exactly; replay two retained R134 settings labels
   to recover R143 867d86a5 byte exactly.
3. Recompile the frozen R144 headers; replay labels and require whole native bytes
   67180bdd to equal the actual R144 APK before applying any R145 overlay.
4. Validate inverses of all three proposed headers, the four blue RGB literals,
   requested three/four/five-band designs, widths and unchanged family/alias rows.
5. Compile the R145 override. Preserve all 33 exports, dependencies, SONAME and
   LOAD 16 KiB. Recheck every frozen source, tool, receipt and input afterward.

Output includes native-receipt.json, commands.json, private compiler/ELF logs,
the complete reproduced baselines, header overlays and libturbo_carousel.so.
Receipt schema is station.r145.native.sky-blue-bands.v1, matching build_identity.
Only native carousel is produced here; no APK, DEX, wrapper, phone or API mutation.

Settings/modal neutral backgrounds, black theme/OFF/loading, curves, clocks,
diagonal mask, clouds, media, LEDs, controls and gameplay stay in their original
paths. New band counts are visual, with a fixed 66-vertex reused stack buffer;
five-band profiles intentionally perform five draws/330 generated vertices
instead of three/198. No heap/JNI/worker/timer is added. Actual Android visual,
CPU, temperature and readability tests remain separate from compile proofs.

Keep all earlier sources and outputs intact. Output must be fresh and below the
fixed E:/StationSkyBlueWavesR145-20261013 namespace. Do not weaken SHA/freeze,
inverse, original-signature or identity-registration guards for a failed build.
