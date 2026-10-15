"""Build one R165 carousel from the exact R164 width and Mega gate patches.

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
SOURCE = Path("E:/StationVisualR164SelectionActions-20261015/native")
SOURCE_LIBRARY_SHA = "bd3222558a43f8998d51b0b72010ecb8a94c7ae62a14d34b39863d13737a10d0"
SOURCE_RECEIPT_SHA = "c39fc9350cb643cd64bd227a874b9bee2d29bde914a963d6d5e153633e16c3eb"
COMMANDS = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/"
                "reconstrucao-atual/sky-blue-waves-r145-20261013/build/native/final/commands.json")
COMMANDS_SHA = "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671"
WIDTH_PATCH = REPO / "integration/game-selection-main-width-r165/recipe/patch_width.py"
MEGA_PATCH = REPO / "integration/mega-drive-cover-gate-r165/recipe/patch_mega_gate.py"
CHANGED = {"native_formation.h", "station_bottom_action_layout.h", "magazine_shader.h"}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        raise ValueError("Exact R164 carousel binary and receipt are required")
    source_receipt = json.loads((SOURCE / "native-receipt.json").read_text("utf-8"))
    expected = source_receipt.get("headerSha256")
    source_entries = list(source_overlay.iterdir())
    if source_receipt.get("schema") != "station.r164.selection-actions.native.v1" or \
       source_receipt.get("passed") is not True or \
       source_receipt.get("outputSha256") != SOURCE_LIBRARY_SHA or \
       not isinstance(expected, dict) or len(expected) != 14 or \
       len(source_entries) != len(expected) or not all(p.is_file() for p in source_entries) or \
       {p.name: sha(p) for p in source_entries} != expected:
        raise ValueError("R164 source overlay differs from its approved 14-header receipt")
    if sha(COMMANDS) != COMMANDS_SHA:
        raise ValueError("Pinned NDK command changed")
    if not WIDTH_PATCH.is_file() or not MEGA_PATCH.is_file():
        raise FileNotFoundError("Both scoped R165 visual patches are required")

    # Preflight the Mega patch before creating an output directory. Its pure
    # byte interface permits proof that only the intended shader can change.
    mega = load(MEGA_PATCH, "r165_mega_gate")
    old_shader = (source_overlay / "magazine_shader.h").read_bytes()
    new_shader, mega_receipt = mega.patch(old_shader)
    if not isinstance(new_shader, bytes) or not isinstance(mega_receipt, dict) or \
       new_shader == old_shader or \
       mega_receipt.get("schema") != "station.r165.mega-drive-cover-gate.patch.v1" or \
       mega_receipt.get("passed") is not True or \
       mega_receipt.get("sourceSha256") != expected["magazine_shader.h"] or \
       mega_receipt.get("outputSha256") != digest(new_shader) or \
       mega_receipt.get("changedFile") != "magazine_shader.h" or \
       mega_receipt.get("newTimersThreadsWorkersOrPerFrameDraws") != 0 or \
       mega_receipt.get("profile10LegacyPreserved") is not True or \
       mega_receipt.get("profile125MapPreserved") is not True:
        raise ValueError("Reviewed single-pass Mega shader patch receipt required")

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
    width = load(WIDTH_PATCH, "r165_main_width")
    width_receipt = width.patch(overlay)
    width_changes = {row["name"]: row["after"] for row in width_receipt.get("changedHeaders", [])}
    if width_receipt.get("schema") != "station.r165.selection-main-width.patch.v1" or \
       width_receipt.get("sourceCarouselSha256") != SOURCE_LIBRARY_SHA or \
       set(width_changes) != CHANGED - {"magazine_shader.h"} or \
       width_receipt.get("newTimersThreadsWorkersOrPerFrameDraws") != 0 or \
       any(sha(overlay / name) != value for name, value in width_changes.items()):
        raise ValueError("Reviewed width and action geometry patch receipt required")
    (overlay / "magazine_shader.h").write_bytes(new_shader)
    actual_entries = list(overlay.iterdir())
    actual = {p.name: sha(p) for p in actual_entries if p.is_file()}
    changed = {name for name in expected if actual.get(name) != expected[name]}
    if len(actual_entries) != 14 or set(actual) != set(expected) or changed != CHANGED or \
       actual["magazine_shader.h"] != mega_receipt["outputSha256"] or \
       actual["native_magazine_field.h"] != expected["native_magazine_field.h"] or \
       actual["native_netplay.h"] != expected["native_netplay.h"]:
        raise ValueError("Combined visual patch escaped the three-header scope")

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
        raise ValueError("Scoped R165 NDK build failed; inspect " + str(log))
    if warnings(log) != warnings(SOURCE / "carousel-build.log"):
        raise ValueError("R165 NDK build added or changed compiler warnings")

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
        raise ValueError("R165 carousel ABI, SONAME or 16 KiB alignment changed")
    receipt = {
        "schema": "station.r165.combined-visual.native.v1", "passed": True,
        "sourceLibrarySha256": SOURCE_LIBRARY_SHA,
        "sourceReceiptSha256": SOURCE_RECEIPT_SHA,
        "ndkCommandSha256": COMMANDS_SHA,
        "widthPatchSourceSha256": sha(WIDTH_PATCH),
        "megaPatchSourceSha256": sha(MEGA_PATCH),
        "changedHeaders": sorted(changed),
        "headerSha256": actual,
        "widthPatch": width_receipt,
        "megaPatch": mega_receipt,
        "outputSha256": sha(final),
        "abiPreserved": True,
        "soname": new_abi["soname"],
        "minimumLoadAlignment": new_abi["minimumLoadAlignment"],
        "compilerWarningsUnchanged": True,
        "extraPerFrameDrawCalls": 0,
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
