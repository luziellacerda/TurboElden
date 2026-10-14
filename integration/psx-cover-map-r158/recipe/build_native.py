"""Rebuild R157's carousel exactly, then change only the PSX artwork map."""

from __future__ import annotations

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
R145 = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/reconstrucao-atual/sky-blue-waves-r145-20261013/build/native/final")
R145_INPUT = R145.parents[2] / "native-inputs"
BASE_SHA = "52aa5e3e32e0664c829a68ffed41e883aacb9992481b96becebb8a3b26867309"
R157_APK = Path("F:/TurboStations-Estavel-R157-20261014/apk/TurboStations-Premium-R157-visual-20261014.apk")
R157_APK_SHA = "563625c40bfce77def6770a67448f83e2206e67a07023c58359ad2a0de4eee34"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Pinned helper unavailable: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(output: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    if sha(R157_APK) != R157_APK_SHA:
        raise ValueError("Exact owner-approved R157 APK required")
    output.mkdir(parents=True)
    (output / "temp").mkdir()
    r150 = load(REPO / "integration/online-wave-visual-r150/recipe/prepare_native_overlay.py", "r158_r150")
    r151 = load(REPO / "integration/snes-border-gap-r151/recipe/prepare_snes_cover_overlay.py", "r158_r151")
    r148 = load(REPO / "integration/system-synopsis-removal-r148/recipe/prepare_overlay.py", "r158_r148")
    psx = load(HERE / "prepare_overlay.py", "r158_psx")
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r158_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r158_elf")
    r150.prepare(R145 / "overlay", output / "r150")
    r151.prepare(R145_INPUT / "native/d0", output / "r151")
    r148.prepare(R145_INPUT / "parent-overlay/r132_native_info.h", output / "r148")
    expected = {
        "station_wave_palette.h": "21565ada7a678e3d21a75fd7e669d9d0220de4e97873224b1b37d9634a879914",
        "station_theme_palette.h": "eb525207bb42abf4299f640a4dc046d74948db9797804e3e689bca2b699497bf",
        "native_formation.h": "f37992fd3dced2f2eee0eb014a526be417d02264825ffc0677e26dc06351453f",
        "native_magazine.h": "c706102382f61996104505eb32582d69c7c50f75c44ce7f8c9756033616c0829",
        "native_magazine_field.h": "f223caed4bad8af65b9d3db993b4f56f688045c86cd8e2d18c870b9f415a9f72",
        "magazine_shader.h": "969e422a57e544da7b12ee3855ab9be67169e876357ebe74bddbaa4b3f48da99",
        "r132_native_info.h": "af31da6851bb2ce6742aca553b361fdb5beccab87c68a4874a6c6febbb89b0b6",
        "native_skin.h": "0db3942ca17c58f5ae118707be3c978fd9e7faf0e47262b2abd7316574b8ddbf",
        "native_space.h": "1b93e7564a9f5b5db3dd440f9f368dc9bd4f6bbdf99291349e45b163d6a0da3e",
        "native_settings.h": "ed7a2a045e390b0801b1c153f5b0275c047653c4afcf363c0be1034b82b45ad4",
    }
    source = {
        **{name: output / "r150" / name for name in ("station_wave_palette.h", "station_theme_palette.h")},
        **{name: output / "r151" / name for name in ("native_formation.h", "native_magazine.h", "native_magazine_field.h", "magazine_shader.h")},
        "r132_native_info.h": output / "r148/r132_native_info.h",
        "native_skin.h": R145 / "overlay/native_skin.h",
        "native_space.h": REPO / "integration/online-wave-corrections-r156/native/native_space.h",
        "native_settings.h": REPO / "integration/online-wave-corrections-r156/native/native_settings.h",
    }
    if set(source) != set(expected) or any(sha(path) != expected[name] for name, path in source.items()):
        raise ValueError("Reconstructed installed R157 native sources differ")
    old = output / "baseline-overlay"
    new = output / "psx-overlay"
    old.mkdir()
    new.mkdir()
    for name, path in source.items():
        shutil.copyfile(path, old / name)
        shutil.copyfile(path, new / name)
    changed = psx.patch(source["magazine_shader.h"].read_bytes())
    (new / "magazine_shader.h").write_bytes(changed)
    field = psx.patch_field(source["native_magazine_field.h"].read_bytes())
    (new / "native_magazine_field.h").write_bytes(field)
    if any(sha(old / name) != sha(new / name) for name in source
           if name not in ("magazine_shader.h", "native_magazine_field.h")):
        raise ValueError("Unrelated native header changed")
    command_file = R145 / "commands.json"
    if sha(command_file) != "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671":
        raise ValueError("Pinned native compiler command changed")
    rows = json.loads(command_file.read_text("utf-8"))
    commands = [row["command"] for row in rows if row["label"] == "sky-blue-bands-r145"]
    if len(commands) != 1:
        raise ValueError("Native compiler command ambiguous")
    command = list(commands[0])
    historic = "E:/StationSkyBlueWavesR145-20261013/native/final/overlay"
    command = [str(R145 / "overlay") if str(arg).replace("\\", "/").lower() == historic.lower() else arg for arg in command]
    if not Path(command[0]).is_file() or any(not Path(command[i+1]).is_dir() for i, value in enumerate(command[:-1]) if value == "-I"):
        raise ValueError("Compiler or retained include path missing")

    def compile_one(overlay: Path, stem: str) -> bytes:
        args = list(command)
        args[args.index("-I"):args.index("-I")] = ["-I", str(overlay)]
        raw = output / (stem + "-unlabelled.so")
        args[args.index("-o") + 1] = str(raw)
        result = subprocess.run(args, cwd=output, env={**os.environ, "TEMP": str(output / "temp"), "TMP": str(output / "temp")},
                                capture_output=True, timeout=1800)
        (output / (stem + ".log")).write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError("Native compilation failed: " + stem)
        binary, _ = labels.patch_labels(raw.read_bytes())
        return binary

    baseline = compile_one(old, "baseline-r157")
    if hashlib.sha256(baseline).hexdigest() != BASE_SHA:
        raise ValueError("R157 carousel did not reproduce byte for byte")
    candidate = compile_one(new, "psx-r158")
    target = output / "libturbo_carousel.so"
    target.write_bytes(candidate)
    if elf.elf_contract(baseline) != elf.elf_contract(candidate):
        raise ValueError("Native ABI, dependencies or page alignment changed")
    warnings = lambda stem: sorted(line for line in (output / (stem + ".log")).read_text("utf-8", errors="replace").splitlines() if "warning:" in line)
    if warnings("baseline-r157") != warnings("psx-r158"):
        raise ValueError("Native compiler warnings changed")
    receipt = {"schema": "station.r158.psx-cover.native.v1", "passed": True,
               "r157Reproduced": True, "baseSha256": BASE_SHA,
               "outputSha256": sha(target), "shaderSha256": sha(new / "magazine_shader.h"),
               "sourceArtDimensions": [1024, 1536],
               "changedHeaders": ["magazine_shader.h", "native_magazine_field.h"],
               "otherNativeHeadersChanged": False, "psxUsesSnesInstantFieldBake": True,
               "extraPerFrameDrawCalls": 0, "newTimersThreadsHeapAllocations": 0,
               "legacyPsxOverlayRemoved": True, "sharedPsxFrameMap": True,
               "snesProfilePreserved": True}
    (output / "native-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return receipt


if __name__ == "__main__":
    import argparse
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", type=Path, required=True)
    print(json.dumps(build(cli.parse_args().out.resolve()), ensure_ascii=False))
