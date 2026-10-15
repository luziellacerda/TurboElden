"""Build one R167 carousel from the exact R165 native overlay.

Only a fresh, isolated output directory is written. This does not create an
APK, update engine identities, sign a package, or install on a telephone.
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
SOURCE = Path("E:/StationVisualR165Combined-20261015/native")
SOURCE_LIBRARY_SHA = "3f20f862bed0d73668fdbc0fa06e7009011cbf8ea32c2cfff96029c2b8f23fc8"
SOURCE_RECEIPT_SHA = "3dd4cca1f17d0f7a6a438b2250f9b186b19548a2177362efd1315c1b75637c3b"
COMMANDS = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/"
                "reconstrucao-atual/sky-blue-waves-r145-20261013/build/native/final/commands.json")
COMMANDS_SHA = "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671"
NEIGHBOR_PATCH = REPO / "integration/game-selection-neighbor-width-r167/recipe/patch_neighbors.py"
CHANGED = {"native_formation.h"}
SOURCE_FILES = {
    "integration/game-selection-neighbor-width-r167/recipe/build_native.py": HERE / "build_native.py",
    "integration/game-selection-neighbor-width-r167/recipe/patch_neighbors.py": NEIGHBOR_PATCH,
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Missing native helper: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def warnings(path: Path) -> list[str]:
    return sorted(line for line in path.read_text("utf-8", errors="replace").splitlines()
                  if "warning:" in line)


def build(output: Path) -> dict:
    out = Path(output).resolve()
    if out.exists() or out == SOURCE.resolve() or SOURCE.resolve() in out.parents or \
       out == REPO.resolve() or REPO.resolve() in out.parents:
        raise ValueError("Fresh native output outside source and Git is required")

    source_overlay = SOURCE / "overlay"
    if sha(SOURCE / "libturbo_carousel.so") != SOURCE_LIBRARY_SHA or \
       sha(SOURCE / "native-receipt.json") != SOURCE_RECEIPT_SHA:
        raise ValueError("Exact R165 carousel binary and receipt are required")
    source_receipt = json.loads((SOURCE / "native-receipt.json").read_text("utf-8"))
    expected = source_receipt.get("headerSha256")
    source_entries = list(source_overlay.iterdir())
    if source_receipt.get("schema") != "station.r165.selection-native.v1" or \
       source_receipt.get("passed") is not True or \
       source_receipt.get("outputSha256") != SOURCE_LIBRARY_SHA or \
       not isinstance(expected, dict) or len(expected) != 14 or \
       len(source_entries) != len(expected) or not all(p.is_file() for p in source_entries) or \
       {p.name: sha(p) for p in source_entries} != expected:
        raise ValueError("R165 source overlay differs from its approved 14-header receipt")
    if sha(COMMANDS) != COMMANDS_SHA:
        raise ValueError("Pinned NDK command changed")
    if not NEIGHBOR_PATCH.is_file():
        raise FileNotFoundError("Scoped R167 neighbor patch is required")

    rows = json.loads(COMMANDS.read_text("utf-8"))
    native_commands = [row["command"] for row in rows if row["label"] == "sky-blue-bands-r145"]
    if len(native_commands) != 1 or not isinstance(native_commands[0], list):
        raise ValueError("Pinned NDK command is ambiguous")
    old_include = "e:/stationskybluewavesr145-20261013/native/final/overlay"
    if sum(str(value).replace("\\", "/").lower() == old_include
           for value in native_commands[0]) != 1 or \
       native_commands[0].count("-I") < 1 or native_commands[0].count("-o") != 1:
        raise ValueError("Pinned NDK command structure changed")

    out.mkdir(parents=True)
    overlay = out / "overlay"
    shutil.copytree(source_overlay, overlay)
    (out / "temp").mkdir()
    patcher = load(NEIGHBOR_PATCH, "r167_neighbor_width")
    patch_receipt = patcher.patch(overlay)
    if patch_receipt.get("schema") != "station.r167.selection-neighbor-width.patch.v1" or \
       patch_receipt.get("sourceCarouselSha256") != SOURCE_LIBRARY_SHA or \
       patch_receipt.get("changedHeader") != "native_formation.h" or \
       patch_receipt.get("beforeSha256") != expected["native_formation.h"] or \
       patch_receipt.get("afterSha256") != sha(overlay / "native_formation.h") or \
       patch_receipt.get("selectedCoverAndNeighborHeightUnchanged") is not True or \
       patch_receipt.get("newTimersThreadsWorkersAllocationsOrDraws") != 0:
        raise ValueError("Reviewed neighbor geometry patch receipt required")
    actual_entries = list(overlay.iterdir())
    actual = {p.name: sha(p) for p in actual_entries if p.is_file()}
    changed = {name for name in expected if actual.get(name) != expected[name]}
    if len(actual_entries) != 14 or set(actual) != set(expected) or changed != CHANGED or \
       actual["station_bottom_action_layout.h"] != expected["station_bottom_action_layout.h"] or \
       actual["magazine_shader.h"] != expected["magazine_shader.h"] or \
       actual["native_magazine_field.h"] != expected["native_magazine_field.h"] or \
       actual["native_netplay.h"] != expected["native_netplay.h"]:
        raise ValueError("Neighbor patch escaped the single-header scope")

    source_root = str(COMMANDS.parent / "overlay")
    args = [source_root if str(value).replace("\\", "/").lower() == old_include else value
            for value in native_commands[0]]
    args[args.index("-I"):args.index("-I")] = ["-I", str(overlay)]
    raw = out / "carousel-unlabelled.so"
    args[args.index("-o") + 1] = str(raw)
    env = {**os.environ, "TEMP": str(out / "temp"), "TMP": str(out / "temp"),
           "PYTHONDONTWRITEBYTECODE": "1"}
    compiled = subprocess.run(args, cwd=out, env=env, capture_output=True, timeout=1800)
    log = out / "carousel-build.log"
    log.write_bytes(compiled.stdout + compiled.stderr)
    if compiled.returncode:
        raise ValueError("Scoped R167 NDK build failed; inspect " + str(log))
    if warnings(log) != warnings(SOURCE / "carousel-build.log"):
        raise ValueError("R167 NDK build added or changed compiler warnings")

    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py",
                  "r165_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py",
               "r165_elf")
    binary, _ = labels.patch_labels(raw.read_bytes())
    final = out / "libturbo_carousel.so"
    final.write_bytes(binary)
    old_abi = elf.elf_contract((SOURCE / "libturbo_carousel.so").read_bytes())
    new_abi = elf.elf_contract(binary)
    if (old_abi["exports"], old_abi["needed"], old_abi["soname"]) != \
       (new_abi["exports"], new_abi["needed"], new_abi["soname"]) or \
       old_abi["minimumLoadAlignment"] < 16384 or new_abi["minimumLoadAlignment"] < 16384:
        raise ValueError("R167 carousel ABI, SONAME or 16 KiB alignment changed")
    receipt = {
        "schema": "station.r167.selection-neighbor-native.v1", "passed": True,
        "sourceLibrarySha256": SOURCE_LIBRARY_SHA,
        "sourceReceiptSha256": SOURCE_RECEIPT_SHA,
        "ndkCommandSha256": COMMANDS_SHA,
        "sourceFilesSha256": {name: sha(path) for name, path in SOURCE_FILES.items()},
        "neighborPatchSourceSha256": sha(NEIGHBOR_PATCH),
        "changedHeaders": sorted(changed),
        "headerSha256": actual,
        "neighborPatch": patch_receipt,
        "outputSha256": sha(final),
        "abiPreserved": True,
        "soname": new_abi["soname"],
        "minimumLoadAlignment": new_abi["minimumLoadAlignment"],
        "compilerWarningsUnchanged": True,
        "effectRoutingPreserved": True,
        "extraPerFrameDrawCalls": 0,
        "newTimersThreadsHeapAllocations": 0,
        "newTimersThreadsWorkersOrPerFrameDraws": 0,
    }
    (out / "native-receipt.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(build(arguments.out), ensure_ascii=False))
