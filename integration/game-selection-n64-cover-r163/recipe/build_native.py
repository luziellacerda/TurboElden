"""Build the scoped game-selection/N64 artwork carousel from the R162 native base.

The ten source headers are copied from the byte-pinned R158/R162 overlay.  The
two local patches edit that copy only.  The original overlay and the signed APK
are never modified in place.
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
SOURCE = Path("E:/StationVisualR158UnifiedPsxFinal-20261014/combined-native-v8")
COMMANDS = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/"
                "reconstrucao-atual/sky-blue-waves-r145-20261013/build/native/final/commands.json")
SOURCE_LIBRARY_SHA = "7d2f2be22083c3fb2a27df9fd43c3b92cf63bc74f87e1f64955753910b00c025"
COMMANDS_SHA = "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671"
HEADERS = {
    "magazine_shader.h": "b8821da12ca401b1288685a91a80bc9e91eb069b461b3be28a3cfdcc3a5870ae",
    "native_formation.h": "06e3916afd8af22a1e3969863339b739efb25dfbec592b44e93008693db091b4",
    "native_magazine_field.h": "00fb3ab72b245e705874820e0b89c3ca1ec79abef8e6ca6c51789b1038a512af",
    "native_magazine.h": "c706102382f61996104505eb32582d69c7c50f75c44ce7f8c9756033616c0829",
    "native_settings.h": "ed7a2a045e390b0801b1c153f5b0275c047653c4afcf363c0be1034b82b45ad4",
    "native_skin.h": "0db3942ca17c58f5ae118707be3c978fd9e7faf0e47262b2abd7316574b8ddbf",
    "native_space.h": "1b93e7564a9f5b5db3dd440f9f368dc9bd4f6bbdf99291349e45b163d6a0da3e",
    "r132_native_info.h": "af31da6851bb2ce6742aca553b361fdb5beccab87c68a4874a6c6febbb89b0b6",
    "station_theme_palette.h": "eb525207bb42abf4299f640a4dc046d74948db9797804e3e689bca2b699497bf",
    "station_wave_palette.h": "21565ada7a678e3d21a75fd7e669d9d0220de4e97873224b1b37d9634a879914",
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Missing scoped build helper: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(out: Path) -> dict:
    if out.exists():
        raise FileExistsError(out)
    source_overlay = SOURCE / "overlay"
    if sha(SOURCE / "libturbo_carousel.so") != SOURCE_LIBRARY_SHA or \
       {path.name: sha(path) for path in source_overlay.iterdir() if path.is_file()} != HEADERS:
        raise ValueError("R162 visual source is not the pinned ten-header overlay")
    if sha(COMMANDS) != COMMANDS_SHA:
        raise ValueError("Pinned native compiler command changed")
    out.mkdir(parents=True)
    overlay = out / "overlay"
    shutil.copytree(source_overlay, overlay)
    (out / "temp").mkdir()
    layout = load(HERE / "patch_layout.py", "r163_layout")
    cover = load(HERE / "patch_n64_cover.py", "r163_cover")
    layout_receipt = layout.patch(overlay)
    cover_receipt = cover.patch(overlay)
    added = {"station_bottom_action_layout.h", "native_search_download.h",
             "station_collection_settings_layout.h"}
    if {path.name for path in overlay.iterdir() if path.is_file()} != set(HEADERS) | added:
        raise ValueError("Unexpected native overlay source added")
    changed = sorted(name for name in HEADERS if sha(overlay / name) != HEADERS[name])
    if not changed or any(name not in {"magazine_shader.h", "native_magazine_field.h",
                                         "native_formation.h", "native_skin.h"} for name in changed):
        raise ValueError("Native change escaped the visual/layout scope")
    rows = json.loads(COMMANDS.read_text("utf-8"))
    commands = [row["command"] for row in rows if row["label"] == "sky-blue-bands-r145"]
    if len(commands) != 1:
        raise ValueError("Native compiler command is ambiguous")
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
        raise ValueError("Scoped native carousel compilation failed; inspect " + str(log))
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py",
                  "r163_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py",
               "r163_elf")
    binary, _ = labels.patch_labels(raw.read_bytes())
    final = out / "libturbo_carousel.so"
    final.write_bytes(binary)
    old_abi = elf.elf_contract((SOURCE / "libturbo_carousel.so").read_bytes())
    new_abi = elf.elf_contract(binary)
    if (old_abi["exports"], old_abi["needed"], old_abi["soname"]) != \
       (new_abi["exports"], new_abi["needed"], new_abi["soname"]) or \
       new_abi["minimumLoadAlignment"] < 16384:
        raise ValueError("Carousel ABI or Android page alignment changed")
    warnings = lambda p: sorted(line for line in p.read_text("utf-8", errors="replace").splitlines()
                                if "warning:" in line)
    if warnings(SOURCE / "combined.log") != warnings(log):
        raise ValueError("Native compiler emitted new warnings")
    receipt = {
        "schema": "station.r163.selection-n64-cover.native.v1", "passed": True,
        "sourceLibrarySha256": SOURCE_LIBRARY_SHA, "outputSha256": sha(final),
        "changedHeaders": changed, "addedHeaders": sorted(added),
        "headerSha256": {name: sha(overlay / name) for name in sorted(set(HEADERS) | added)},
        "layout": layout_receipt, "cover": cover_receipt,
        "extraPerFrameDrawCalls": 0, "newTimersThreadsHeapAllocations": 0,
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
