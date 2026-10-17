"""Replay the exact R145/R147 carousel build, then overlay one R132 header.

This consumes the previously pinned 158 native inputs and command, preserving
their original directories. It writes only to a fresh R148 E: output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BUILD_ROOT = Path("E:/StationSystemSynopsisR148-20261014")
PARENT = Path("E:/StationSkyBlueWavesR145-20261013/native/final")
PARENT_COMMAND_SHA = "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671"
PARENT_RECEIPT_SHA = "3a9b84e7f141cdfee26901e1cc5fc496097aaeef87db9b03b5dc1314d523ec0d"
PARENT_UNLABELLED_SHA = "5022403c9f8c16993a781c3249893a34f8ca1d4d848a90d7eb5c45f38cdcdf77"
BASELINE_SHA = "2e15a9a330c2562c71574921f5558d6142e3051bba64a315434e5714f38908a9"
R132_SHA = "e6c910b188018146a394ff2128f9f82144afcbe46d0bd3924d09b200661c5c75"
TOOL_SHA = "1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Native replay helper missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(command: list[str], directory: Path, label: str) -> str:
    env = {**os.environ, "TEMP": str(directory / "temp"), "TMP": str(directory / "temp")}
    result = subprocess.run(command, cwd=directory, env=env, capture_output=True, timeout=1800)
    (directory / (label + ".log")).write_bytes(result.stdout + result.stderr)
    need(result.returncode == 0, "Pinned R148 native compilation failed: " + label)
    return sha(Path(command[command.index("-o") + 1]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay", type=Path, required=True,
                        help="Fresh output of prepare_overlay.py containing r132_native_info.h")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    overlay = args.overlay.resolve(strict=True)
    output = args.out.resolve()
    need(output.parent == BUILD_ROOT.resolve() and not output.exists() and
         overlay.parent == BUILD_ROOT.resolve() and overlay.is_dir(),
         "Fresh native output and prepared overlay below the R148 E: namespace required")
    header = overlay / "r132_native_info.h"
    overlay_receipt_path = overlay / "overlay-receipt.json"
    overlay_receipt = json.loads(overlay_receipt_path.read_text("utf-8"))
    need(overlay_receipt.get("schema") == "station.r148.platform-synopsis-overlay.v1" and
         overlay_receipt.get("inputHeaderSha256") == R132_SHA and
         overlay_receipt.get("parentCarouselSha256") == BASELINE_SHA and
         overlay_receipt.get("outputHeaderSha256") == sha(header) and
         overlay_receipt.get("changedLines") == 1 and
         overlay_receipt.get("gameAndCollectionSynopsesPreserved") is True,
         "Exact one-line R132 overlay required")
    commands_path = PARENT / "commands.json"
    receipt_path = PARENT / "native-receipt.json"
    need(sha(commands_path) == PARENT_COMMAND_SHA and sha(receipt_path) == PARENT_RECEIPT_SHA,
         "Immutable R145 native replay inputs changed")
    prior = json.loads(receipt_path.read_text("utf-8"))
    need(prior.get("passed") is True and prior.get("compiled") is True and
         prior.get("outputNativeSha256") == BASELINE_SHA and
         prior.get("retainedInputSha256") and prior.get("retainedInputPaths") and
         set(prior["retainedInputSha256"]) == set(prior["retainedInputPaths"]) and
         len(prior["retainedInputSha256"]) == 158,
         "R145 final receipt or 158-input inventory differs")
    input_paths = {name: Path(path) for name, path in prior["retainedInputPaths"].items()}
    need(all(path.is_file() and sha(path) == prior["retainedInputSha256"][name]
             for name, path in input_paths.items()), "An original native input changed")
    original_r132 = input_paths["parent-overlay:r132_native_info.h"]
    need(sha(original_r132) == R132_SHA and original_r132.parent != overlay,
         "Exact preserved R132 source header required")
    commands = json.loads(commands_path.read_text("utf-8"))
    compile_commands = [row["command"] for row in commands if row["label"] == "sky-blue-bands-r145"]
    need(len(compile_commands) == 1, "Unique historical carousel compile command required")
    command = compile_commands[0]
    compiler = Path(command[0])
    need(sha(compiler) == TOOL_SHA and command.count("-o") == 1 and
         str(original_r132.parent) in command and
         str(PARENT / "overlay") in command and
         str(input_paths["r133-overlay:native_carousel.cpp"]) in command and
         str(PARENT / "unlabelled-r145.so") == command[command.index("-o") + 1] and
         sha(PARENT / "unlabelled-r145.so") == PARENT_UNLABELLED_SHA and
         sha(PARENT / "libturbo_carousel.so") == BASELINE_SHA,
         "Exact original R145/R147 compile command and ELF outputs required")
    output.mkdir(parents=True)
    (output / "temp").mkdir()
    baseline_command = list(command)
    baseline_unlabelled = output / "baseline-unlabelled.so"
    baseline_command[baseline_command.index("-o") + 1] = str(baseline_unlabelled)
    need(run(baseline_command, output, "baseline") == PARENT_UNLABELLED_SHA,
         "Complete carousel baseline did not reproduce byte for byte")
    label_helper = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r148_labels")
    baseline, baseline_labels = label_helper.patch_labels(baseline_unlabelled.read_bytes())
    need(hashlib.sha256(baseline).hexdigest() == BASELINE_SHA and
         baseline == (PARENT / "libturbo_carousel.so").read_bytes(),
         "Reproduced R147 carousel differs")
    patched_command = list(command)
    patched_unlabelled = output / "synopsis-unlabelled.so"
    patched_command[patched_command.index("-o") + 1] = str(patched_unlabelled)
    include_at = patched_command.index(str(original_r132.parent))
    need(include_at > 0 and patched_command[include_at - 1] == "-I",
         "R132 include position changed")
    patched_command[include_at - 1:include_at - 1] = ["-I", str(overlay)]
    run(patched_command, output, "synopsis")
    final_raw, changed_labels = label_helper.patch_labels(patched_unlabelled.read_bytes())
    final = output / "libturbo_carousel.so"
    final.write_bytes(final_raw)
    need(sha(final) != BASELINE_SHA and baseline_labels == changed_labels,
         "One-line overlay must change native bytes without changing retained labels")
    old_elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r148_native_elf")
    old_contract, new_contract = old_elf.elf_contract(baseline), old_elf.elf_contract(final_raw)
    need(old_contract["exports"] == new_contract["exports"] and
         old_contract["needed"] == new_contract["needed"] and
         old_contract["soname"] == new_contract["soname"] == ["libturbo_carousel.so"] and
         new_contract["minimumLoadAlignment"] >= 16384,
         "Native carousel ABI or load alignment changed")
    need(all(sha(path) == prior["retainedInputSha256"][name]
             for name, path in input_paths.items()), "Native inputs changed during R148 replay")
    receipt = {"schema": "station.r148.native.system-synopsis.v1", "revision": "R148",
               "passed": True, "compiled": True, "baselineReproduced": True,
               "scopeOnlySystemSynopsis": True, "baselineNativeSha256": BASELINE_SHA,
               "baselineUnlabelledSha256": PARENT_UNLABELLED_SHA,
               "outputNativeSha256": sha(final), "outputNativeBytes": final.stat().st_size,
               "overlayReceiptSha256": sha(overlay_receipt_path),
               "overlayHeaderSha256": sha(header),
               "retainedR145NativeReceiptSha256": PARENT_RECEIPT_SHA,
               "retainedR145CommandsSha256": PARENT_COMMAND_SHA,
               "retainedInputCount": 158, "originalInputHeaderSha256": R132_SHA,
               "nativeAbi": new_contract, "gameAndCollectionSynopsesPreserved": True,
               "installed": False, "serverApplied": False}
    with (output / "native-receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"revision": "R148", "passed": True,
                      "baselineNativeSha256": BASELINE_SHA,
                      "outputNativeSha256": receipt["outputNativeSha256"],
                      "gameAndCollectionSynopsesPreserved": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
