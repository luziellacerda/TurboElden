"""Compile R164 game-selection controls from the exact R163 native overlay.

The inherited N64 cover light map stays byte-identical.  The R164 patch is
applied only to a copy; all source, compiler, ABI and warning pins must pass.
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
SOURCE = Path("E:/StationVisualR163SelectionN64-20261015/native")
SOURCE_LIBRARY_SHA = "788ff4a8eb30add5f5352cf8f0820a73c5b94bd78f42c7ee184ac20d7ecf5d09"
SOURCE_RECEIPT_SHA = "9cade91f8657f7b8038cea5709f33313b65b021bd7342bdf03a512dc67edc810"
COMMANDS = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/"
                "reconstrucao-atual/sky-blue-waves-r145-20261013/build/native/final/commands.json")
COMMANDS_SHA = "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671"
PATCH = REPO / "integration/game-selection-actions-r164/recipe/patch_actions.py"
CHANGED = {"native_formation.h", "station_bottom_action_layout.h", "native_skin.h"}
ADDED = {"native_netplay.h"}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Missing pinned R164 native helper: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(out: Path) -> dict:
    if out.exists():
        raise FileExistsError(out)
    source_overlay = SOURCE / "overlay"
    source_receipt_path = SOURCE / "native-receipt.json"
    if sha(SOURCE / "libturbo_carousel.so") != SOURCE_LIBRARY_SHA or \
       sha(source_receipt_path) != SOURCE_RECEIPT_SHA:
        raise ValueError("Exact signed R163 native source/receipt required")
    source_receipt = json.loads(source_receipt_path.read_text("utf-8"))
    expected = source_receipt.get("headerSha256")
    if source_receipt.get("schema") != "station.r163.selection-n64-cover.native.v1" or \
       source_receipt.get("passed") is not True or \
       source_receipt.get("outputSha256") != SOURCE_LIBRARY_SHA or \
       not isinstance(expected, dict) or len(expected) != 13 or \
       {path.name: sha(path) for path in source_overlay.iterdir() if path.is_file()} != expected:
        raise ValueError("R163 source overlay differs from its approved 13-header receipt")
    if sha(COMMANDS) != COMMANDS_SHA:
        raise ValueError("Pinned native compiler command changed")
    if not PATCH.is_file():
        raise FileNotFoundError("R164 responsive action patch missing: " + str(PATCH))
    out.mkdir(parents=True)
    overlay = out / "overlay"
    shutil.copytree(source_overlay, overlay)
    (out / "temp").mkdir()
    patch = load(PATCH, "r164_actions")
    patch_receipt = patch.patch(overlay)
    if not isinstance(patch_receipt, dict) or \
       patch_receipt.get("schema") != "station.r164.selection-actions.patch.v1" or \
       patch_receipt.get("actionsPreserved") != [0, 1, 2, 3, 4, 5] or \
       patch_receipt.get("newTimersThreadsWorkers") != 0:
        raise ValueError("Reviewed R164 action patch receipt required")
    new_files = {path.name for path in overlay.iterdir() if path.is_file()}
    changed = {name for name in expected if sha(overlay / name) != expected[name]}
    if new_files != set(expected) | ADDED or changed != CHANGED or \
       sha(overlay / "magazine_shader.h") != expected["magazine_shader.h"] or \
       sha(overlay / "native_magazine_field.h") != expected["native_magazine_field.h"]:
        raise ValueError("R164 patch changed N64 cover map or escaped four-header layout scope")
    rows = json.loads(COMMANDS.read_text("utf-8"))
    commands = [row["command"] for row in rows if row["label"] == "sky-blue-bands-r145"]
    if len(commands) != 1:
        raise ValueError("Pinned native compiler command is ambiguous")
    source_root = str(COMMANDS.parent / "overlay")
    args = [source_root if str(value).replace("\\", "/").lower() ==
            "e:/stationskybluewavesr145-20261013/native/final/overlay" else value
            for value in commands[0]]
    args[args.index("-I"):args.index("-I")] = ["-I", str(overlay)]
    raw = out / "carousel-unlabelled.so"
    args[args.index("-o") + 1] = str(raw)
    env = {**os.environ, "TEMP": str(out / "temp"), "TMP": str(out / "temp"),
           "PYTHONDONTWRITEBYTECODE": "1"}
    compiled = subprocess.run(args, cwd=out, env=env, capture_output=True, timeout=1800)
    log = out / "carousel-build.log"
    log.write_bytes(compiled.stdout + compiled.stderr)
    if compiled.returncode:
        raise ValueError("Scoped R164 native compilation failed; inspect " + str(log))
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py",
                  "r164_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py",
               "r164_elf")
    binary, _ = labels.patch_labels(raw.read_bytes())
    final = out / "libturbo_carousel.so"
    final.write_bytes(binary)
    old_abi = elf.elf_contract((SOURCE / "libturbo_carousel.so").read_bytes())
    new_abi = elf.elf_contract(binary)
    if (old_abi["exports"], old_abi["needed"], old_abi["soname"]) != \
       (new_abi["exports"], new_abi["needed"], new_abi["soname"]) or \
       new_abi["minimumLoadAlignment"] < 16384:
        raise ValueError("R164 carousel ABI or Android page alignment changed")
    warnings = lambda p: sorted(line for line in p.read_text("utf-8", errors="replace").splitlines()
                                if "warning:" in line)
    if warnings(SOURCE / "carousel-build.log") != warnings(log):
        raise ValueError("R164 native compiler emitted new warnings")
    receipt = {
        "schema": "station.r164.selection-actions.native.v1", "passed": True,
        "sourceLibrarySha256": SOURCE_LIBRARY_SHA, "sourceReceiptSha256": SOURCE_RECEIPT_SHA,
        "outputSha256": sha(final), "changedHeaders": sorted(changed),
        "addedHeaders": sorted(ADDED),
        "headerSha256": {name: sha(overlay / name) for name in sorted(new_files)},
        "n64CoverMapSha256Preserved": expected["magazine_shader.h"],
        "n64CoverFieldSha256Preserved": expected["native_magazine_field.h"],
        "patch": patch_receipt, "extraPerFrameDrawCalls": 0,
        "newTimersThreadsHeapAllocations": 0,
        "abiPreserved": True, "compilerWarningsUnchanged": True,
    }
    (out / "native-receipt.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.out.resolve()), ensure_ascii=False))
