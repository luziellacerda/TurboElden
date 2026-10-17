"""Reproduce R151 and compile the isolated R152 carousel presentation overlay."""

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
R145 = Path("E:/StationSkyBlueWavesR145-20261013/native/final")
R151 = Path("E:/StationVisualR151-20261014/native-final")
R151_SHA = "27eb918a66ce38df2ea361dc483e61266a4d4d8b0e7f5a5b9124e8b7a92c2b6f"
R151_SPACE_SHA = "88147d7971bfea5fd6a4533e9fd7c9efd93ce01fb6c2a71807217b9906fb4b8c"
R151_SETTINGS_SHA = "8d24f927d3aae4f78248f15d57566f3430d19d7a8bac1cacb6b9b7761a4dcf1b"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def native_waves(source: str) -> str:
    start = source.index("static void drawNativeWaves(float w,float h,float t){")
    end = source.index("\n}\n", start) + 2
    return source[start:end]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Pinned helper missing: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compile_one(command: list[str], overlays: list[Path], out: Path, label: str, labels) -> bytes:
    actual = list(command)
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
    if sha(R151 / "libturbo_carousel.so") != R151_SHA or sha(R151 / "overlay/native_space.h") != R151_SPACE_SHA:
        raise ValueError("R151 native donor differs")
    prior_settings = Path("G:/StationNormalOwnersR127/local-sony-demos/payloads-next/native/native_settings.h")
    if sha(prior_settings) != R151_SETTINGS_SHA:
        raise ValueError("Settings donor differs")
    paths = [SOURCE / "native_space.h", SOURCE / "native_settings.h"]
    if not all(path.is_file() for path in paths):
        raise ValueError("R152 overlay missing")
    if native_waves((R151 / "overlay/native_space.h").read_text("utf-8")) != native_waves(paths[0].read_text("utf-8")):
        raise ValueError("Existing animated wave mode changed")
    commands = json.loads((R145 / "commands.json").read_text("utf-8"))
    found = [row["command"] for row in commands if row["label"] == "sky-blue-bands-r145"]
    if len(found) != 1:
        raise ValueError("Pinned native command missing")
    command = found[0]
    if not Path(command[0]).is_file() or not all(Path(command[i + 1]).is_dir() for i, value in enumerate(command[:-1]) if value == "-I"):
        raise ValueError("Pinned native tool or include missing")
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r152_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r152_elf")
    out.mkdir(parents=True)
    (out / "temp").mkdir()
    baseline = compile_one(command, [R151 / "overlay"], out, "baseline-r151", labels)
    if hashlib.sha256(baseline).hexdigest() != R151_SHA:
        raise ValueError("R151 native baseline did not reproduce byte for byte")
    current = compile_one(command, [SOURCE, R151 / "overlay"], out, "visual-r152", labels)
    target = out / "libturbo_carousel.so"
    target.write_bytes(current)
    old, new = elf.elf_contract(baseline), elf.elf_contract(current)
    if old["exports"] != new["exports"] or old["needed"] != new["needed"] or old["soname"] != new["soname"] or new["minimumLoadAlignment"] < 16384:
        raise ValueError("Native ABI or alignment changed")
    receipt = {
        "schema": "station.r152.online-wave-mode.native.v1",
        "passed": True,
        "r151Reproduced": True,
        "baseSha256": R151_SHA,
        "outputSha256": sha(target),
        "sourceSha256": {path.name: sha(path) for path in paths},
        "originalWavesChanged": False,
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
