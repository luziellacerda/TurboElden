"""Reproduce R152 and compile the corrected R153 carousel presentation overlay."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE.parent / "native"
R145 = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/reconstrucao-atual/sky-blue-waves-r145-20261013/build/native/final")
R151 = Path("E:/StationVisualR151-20261014/native-final")
R152_SHA = "9d5c1f75e2d0f780358e7673ec132dee9ef1c0eb43992f5fb2dcf5fa673de4c3"
R151_SPACE_SHA = "88147d7971bfea5fd6a4533e9fd7c9efd93ce01fb6c2a71807217b9906fb4b8c"
R151_SETTINGS_SHA = "8d24f927d3aae4f78248f15d57566f3430d19d7a8bac1cacb6b9b7761a4dcf1b"
R151_PALETTE_SHA = "21565ada7a678e3d21a75fd7e669d9d0220de4e97873224b1b37d9634a879914"
R145_SKIN_SHA = "0db3942ca17c58f5ae118707be3c978fd9e7faf0e47262b2abd7316574b8ddbf"
R145_SPACE_SHA = "2ac9e649e27f8ed4259f01cf5116186f76b4481019f5181c36c3956ed4eb7f65"
R145_COMMANDS_SHA = "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def native_waves(source: str) -> str:
    start = source.index("static void drawNativeWaves(float w,float h,float t){")
    end = source.index("\n}\n", start) + 2
    return source[start:end]


def theme_wave_gradient(source: str) -> tuple[str, str]:
    return tuple(next(line for line in source.splitlines() if line.startswith("static unsigned " + name + "()"))
                 for name in ("stationWaveTop", "stationWaveBottom"))


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Pinned helper missing: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compile_one(command: list[str], overlays: list[Path], out: Path, label: str, labels,
                dependency_file: Path | None = None) -> bytes:
    actual = list(command)
    if dependency_file is not None:
        actual[1:1] = ["-MMD", "-MF", str(dependency_file)]
    first_include = actual.index("-I")
    for overlay in reversed(overlays):
        actual[first_include:first_include] = ["-I", str(overlay)]
    raw = out / (label + "-unlabelled.so")
    actual[actual.index("-o") + 1] = str(raw)
    environment = {**os.environ, "TEMP": str(out / "temp"), "TMP": str(out / "temp")}
    process = subprocess.run(actual, capture_output=True, cwd=out, env=environment, timeout=1800)
    (out / (label + ".log")).write_bytes(process.stdout + process.stderr)
    if process.returncode:
        raise ValueError("Native compile failed: " + label)
    binary, _ = labels.patch_labels(raw.read_bytes())
    return binary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    if sha(R151 / "overlay/native_space.h") != R151_SPACE_SHA:
        raise ValueError("R151 native donor differs")
    prior_settings = Path("G:/StationNormalOwnersR127/local-sony-demos/payloads-next/native/native_settings.h")
    if sha(prior_settings) != R151_SETTINGS_SHA:
        raise ValueError("Settings donor differs")
    prior_skin = R145 / "overlay/native_skin.h"
    if sha(prior_skin) != R145_SKIN_SHA:
        raise ValueError("R145 native skin donor differs")
    prior_space = R145 / "overlay/native_space.h"
    if sha(prior_space) != R145_SPACE_SHA:
        raise ValueError("Effective R151 wave donor differs")
    prior_palette = R151 / "overlay/station_wave_palette.h"
    if sha(prior_palette) != R151_PALETTE_SHA:
        raise ValueError("Effective R152 wave palette differs")
    paths = [SOURCE / "native_space.h", SOURCE / "native_settings.h"]
    if not all(path.is_file() for path in paths):
        raise ValueError("R152 overlay missing")
    # The R151 APK actually compiled R145's sibling native_space.h through
    # native_skin.h's quoted include; preserve the installed wave implementation.
    effective = prior_space.read_text("utf-8")
    proposed = paths[0].read_text("utf-8")
    if native_waves(effective) != native_waves(proposed) or theme_wave_gradient(effective) != theme_wave_gradient(proposed):
        raise ValueError("Installed animated wave mode changed")
    command_file = R145 / "commands.json"
    if sha(command_file) != R145_COMMANDS_SHA:
        raise ValueError("R145 native command receipt differs")
    commands = json.loads(command_file.read_text("utf-8"))
    found = [row["command"] for row in commands if row["label"] == "sky-blue-bands-r145"]
    if len(found) != 1:
        raise ValueError("Pinned native command missing")
    old_r145_overlay = str(Path("E:/StationSkyBlueWavesR145-20261013/native/final/overlay")).lower()
    command = [str(R145 / "overlay") if str(value).lower() == old_r145_overlay else value for value in found[0]]
    if not Path(command[0]).is_file() or not all(Path(command[i + 1]).is_dir() for i, value in enumerate(command[:-1]) if value == "-I"):
        raise ValueError("Pinned native tool or include missing")
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r152_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r152_elf")
    out.mkdir(parents=True)
    (out / "temp").mkdir()
    baseline = compile_one(command, [SOURCE, R151 / "overlay"], out, "baseline-r152", labels)
    if hashlib.sha256(baseline).hexdigest() != R152_SHA:
        raise ValueError("R152 native baseline did not reproduce byte for byte")
    # native_skin.h includes "native_space.h" with quote search. Without this
    # sibling copy, Clang picks R145's native_space.h before any -I overlay.
    route = out / "routed-native-space"
    route.mkdir()
    (route / "native_skin.h").write_bytes(prior_skin.read_bytes())
    (route / "native_space.h").write_bytes(paths[0].read_bytes())
    if sha(route / "native_skin.h") != R145_SKIN_SHA or sha(route / "native_space.h") != sha(paths[0]):
        raise ValueError("R152 native-space routing differs")
    dependencies = out / "visual-r152.d"
    current = compile_one(command, [route, SOURCE, R151 / "overlay"], out,
                          "visual-r152", labels, dependencies)
    if not dependencies.is_file():
        raise ValueError("R152 native include proof missing")
    dependency_text = dependencies.read_text("utf-8", errors="replace").replace("\\\n", "")
    dependency_text = dependency_text.replace("\\ ", " ").replace("\\", "/").lower()
    routed_space = str(route / "native_space.h").replace("\\", "/").lower()
    old_space = str(R145 / "overlay/native_space.h").replace("\\", "/").lower()
    installed_palette = str(prior_palette).replace("\\", "/").lower()
    if routed_space not in dependency_text or old_space in dependency_text or installed_palette not in dependency_text:
        raise ValueError("R152 native-space header was shadowed by R145")
    target = out / "libturbo_carousel.so"
    target.write_bytes(current)
    old, new = elf.elf_contract(baseline), elf.elf_contract(current)
    if old["exports"] != new["exports"] or old["needed"] != new["needed"] or old["soname"] != new["soname"] or new["minimumLoadAlignment"] < 16384:
        raise ValueError("Native ABI or alignment changed")
    receipt = {
        "schema": "station.r153.visual.native.v1",
        "passed": True,
        "r152Reproduced": True,
        "baseSha256": R152_SHA,
        "outputSha256": sha(target),
        "sourceSha256": {path.name: sha(path) for path in paths},
        "nativeSpaceInclude": str(route / "native_space.h"),
        "r145NativeSpaceExcluded": True,
        "installedWavePaletteSha256": R151_PALETTE_SHA,
        "originalWavesChanged": False,
        "installedAnimatedWavesPreserved": True,
        "backgroundModes": ["sky", "animated-waves", "off", "static-online-waves"],
        "staticOnlineWaveVertices": 270,
        "staticOnlineWaveDrawCallsPerFrame": 1,
        "staticOnlineWaveTimersAdded": 0,
        "fadeAppliesToAllActiveBackgroundModes": True,
        "compiled": True,
        "installed": False,
    }
    (out / "native-receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
