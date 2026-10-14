"""Reproduce the R149 carousel and compile the single-pass R150 visual overlay.

The two historical baselines must match byte for byte before the seven visual
headers replace their R149 counterparts in one native library. No APK is edited.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
R145 = Path("E:/StationSkyBlueWavesR145-20261013/native/final")
R148 = Path("E:/StationSystemSynopsisR148-20261014")
R149_APK = Path("E:/StationDolphinOnPauseR149-20261014/TurboStations-Premium-R149-dolphin-onpause-20261014.apk")
R145_COMMAND_SHA = "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671"
R145_RECEIPT_SHA = "3a9b84e7f141cdfee26901e1cc5fc496097aaeef87db9b03b5dc1314d523ec0d"
R145_UNLABELLED_SHA = "5022403c9f8c16993a781c3249893a34f8ca1d4d848a90d7eb5c45f38cdcdf77"
R145_CAROUSEL_SHA = "2e15a9a330c2562c71574921f5558d6142e3051bba64a315434e5714f38908a9"
R148_HEADER_SHA = "af31da6851bb2ce6742aca553b361fdb5beccab87c68a4874a6c6febbb89b0b6"
R149_CAROUSEL_SHA = "313de078f8c300b6c7944de2ce03292de697532bc1a493b7406fdbb8260fbd28"
R149_APK_SHA = "698e8a7914cc7be2facc00e6701ff1f3533fa13f763358b51578a35d25c2741e"
CLANG_SHA = "1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3"
EXPECTED_COVER_SHA = "c40505b7a848a2c9ebcb21e17782b6b3f1c257756a514cadaeac0ac87ca6523d"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Pinned helper missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compile_command(command: list[str], output: Path, directory: Path, label: str) -> str:
    command = list(command)
    command[command.index("-o") + 1] = str(output)
    env = {**os.environ, "TEMP": str(directory / "temp"), "TMP": str(directory / "temp")}
    result = subprocess.run(command, cwd=directory, env=env, capture_output=True, timeout=1800)
    (directory / f"{label}.log").write_bytes(result.stdout + result.stderr)
    need(result.returncode == 0, f"Native compile failed: {label}; inspect its log")
    return sha(output)


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--native-overlay", type=Path, required=True)
    cli.add_argument("--cover-overlay", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    args = cli.parse_args()
    native_overlay, cover_overlay = args.native_overlay.resolve(strict=True), args.cover_overlay.resolve(strict=True)
    out = args.out.resolve()
    need(not out.exists(), "Fresh R150 native output directory required")
    need(sha(R149_APK) == R149_APK_SHA and sha(R148 / "native/libturbo_carousel.so") == R149_CAROUSEL_SHA,
         "Exact signed R149 APK and its inherited carousel required")
    need(sha(R145 / "commands.json") == R145_COMMAND_SHA and
         sha(R145 / "native-receipt.json") == R145_RECEIPT_SHA and
         sha(R145 / "unlabelled-r145.so") == R145_UNLABELLED_SHA and
         sha(R145 / "libturbo_carousel.so") == R145_CAROUSEL_SHA,
         "Pinned R145 replay inputs changed")
    r148_header = R148 / "overlay/r132_native_info.h"
    need(sha(r148_header) == R148_HEADER_SHA, "Exact R148 synopsis header required")

    native_receipt_path = native_overlay / "overlay-receipt.json"
    cover_receipt_path = cover_overlay / "overlay-receipt.json"
    native_receipt = json.loads(native_receipt_path.read_text("utf-8"))
    cover_receipt = json.loads(cover_receipt_path.read_text("utf-8"))
    need(native_receipt.get("schema") == "station.r150.visual.native-overlay.v1" and
         native_receipt.get("inverseByteExact") is True and
         native_receipt.get("newTimersThreadsHeapAllocations") == 0 and
         native_receipt.get("waveBands", {}).get("SNES") == 4 and
         cover_receipt.get("schema") == "station.r150.snes-cover-geometry-led.v1" and
         cover_receipt.get("fullInversePassed") is True and
         cover_receipt.get("drawCallsAddedPerFrame") == 0 and
         cover_receipt.get("snesLegacyAndMegaClassifiersSkipped") is True and
         cover_receipt.get("snesLegacyAndMegaSupportSkipped") is True and
         cover_receipt.get("outputSha256", {}).get("magazine_shader.h") == EXPECTED_COVER_SHA,
         "Reviewed R150 single-pass overlays required")
    for root, receipt in ((native_overlay, native_receipt), (cover_overlay, cover_receipt)):
        need(all(sha(root / name) == checksum for name, checksum in receipt["outputSha256"].items()),
             f"Overlay header changed: {root}")
    shader = (cover_overlay / "magazine_shader.h").read_text("utf-8")
    need("if(model>0.125) return snesNewSupport(p);" in shader and
         "return (model>0.125?snesNewSupport(p):snesSupport(p))||megaSupport(p);" not in shader,
         "SNES must not evaluate the legacy or Mega support map")

    prior = json.loads((R145 / "native-receipt.json").read_text("utf-8"))
    paths = {name: Path(value) for name, value in prior["retainedInputPaths"].items()}
    need(len(paths) == 158 and set(paths) == set(prior["retainedInputSha256"]) and
         all(path.is_file() and sha(path) == prior["retainedInputSha256"][name]
             for name, path in paths.items()), "Original 158 native inputs changed")
    commands = json.loads((R145 / "commands.json").read_text("utf-8"))
    matches = [row["command"] for row in commands if row["label"] == "sky-blue-bands-r145"]
    need(len(matches) == 1, "Unique historical carousel command required")
    command = matches[0]
    need(sha(Path(command[0])) == CLANG_SHA and command.count("-o") == 1 and
         command[command.index("-o") + 1] == str(R145 / "unlabelled-r145.so") and
         str(paths["r133-overlay:native_carousel.cpp"]) in command,
         "Pinned native tool or compile command changed")
    r132_parent = str(paths["parent-overlay:r132_native_info.h"].parent)
    need(r132_parent in command and command[command.index(r132_parent) - 1] == "-I",
         "R132 include position changed")

    out.mkdir(parents=True)
    (out / "temp").mkdir()
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r150_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r150_elf")

    baseline_unlabelled = out / "baseline-r145-unlabelled.so"
    need(compile_command(command, baseline_unlabelled, out, "baseline-r145") == R145_UNLABELLED_SHA,
         "R145 unlabelled baseline did not reproduce")
    baseline, base_labels = labels.patch_labels(baseline_unlabelled.read_bytes())
    need(hashlib.sha256(baseline).hexdigest() == R145_CAROUSEL_SHA,
         "R145 labelled baseline did not reproduce")

    r149_command = list(command)
    at = r149_command.index(r132_parent) - 1
    r149_command[at:at] = ["-I", str((R148 / "overlay").resolve())]
    r149_unlabelled = out / "baseline-r149-unlabelled.so"
    compile_command(r149_command, r149_unlabelled, out, "baseline-r149")
    r149_binary, r149_labels = labels.patch_labels(r149_unlabelled.read_bytes())
    need(hashlib.sha256(r149_binary).hexdigest() == R149_CAROUSEL_SHA and
         r149_binary == (R148 / "native/libturbo_carousel.so").read_bytes() and
         base_labels == r149_labels, "R149 carousel did not reproduce byte for byte")

    combined = out / "overlay"
    combined.mkdir()
    shutil.copyfile(r148_header, combined / r148_header.name)
    for root, receipt in ((native_overlay, native_receipt), (cover_overlay, cover_receipt)):
        for name in receipt["outputSha256"]:
            need(not (combined / name).exists(), "Duplicate R150 header: " + name)
            shutil.copyfile(root / name, combined / name)
    r150_command = list(command)
    r150_command[r150_command.index("-I"):r150_command.index("-I")] = ["-I", str(combined)]
    r150_unlabelled = out / "r150-unlabelled.so"
    compile_command(r150_command, r150_unlabelled, out, "r150-visual")
    r150_binary, r150_labels = labels.patch_labels(r150_unlabelled.read_bytes())
    final = out / "libturbo_carousel.so"
    final.write_bytes(r150_binary)
    label_contract = lambda rows: [(row["bytes"], row["fromText"], row["toText"]) for row in rows]
    need(label_contract(base_labels) == label_contract(r150_labels) and sha(final) != R149_CAROUSEL_SHA,
         "R150 changed retained labels or did not change the visual library")
    old_abi, new_abi = elf.elf_contract(r149_binary), elf.elf_contract(r150_binary)
    need(old_abi["exports"] == new_abi["exports"] and
         old_abi["needed"] == new_abi["needed"] and
         old_abi["soname"] == new_abi["soname"] == ["libturbo_carousel.so"] and
         new_abi["minimumLoadAlignment"] >= 16384,
         "Native ABI or alignment changed")
    need(all(sha(path) == prior["retainedInputSha256"][name] for name, path in paths.items()),
         "Original native input changed during R150 compilation")
    receipt = {"schema": "station.r150.native.single-pass.v1", "revision": "R150",
               "passed": True, "compiled": True, "r145Reproduced": True, "r149Reproduced": True,
               "r149ApkSha256": R149_APK_SHA, "r149CarouselSha256": R149_CAROUSEL_SHA,
               "outputNativeSha256": sha(final), "outputNativeBytes": final.stat().st_size,
               "nativeOverlayReceiptSha256": sha(native_receipt_path),
               "coverOverlayReceiptSha256": sha(cover_receipt_path),
               "snesLegacyAndMegaClassifiersSkipped": True,
               "coverDrawCallsAddedPerFrame": 0, "newTimersThreadsHeapAllocations": 0,
               "nativeAbi": new_abi, "installed": False}
    (out / "native-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({"passed": True, "r149Reproduced": True,
                      "outputNativeSha256": receipt["outputNativeSha256"]}))


if __name__ == "__main__":
    main()
