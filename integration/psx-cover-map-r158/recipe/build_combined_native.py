"""Compile the PSX plus Mega Drive cover map on the verified R157 base."""

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
PSX_SHA = "b11aa69c95f0593980cc06311568a6ef7c82e0aad78ece442ae83b906dd78561"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Pinned helper missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(psx_build: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    previous = psx_build / "libturbo_carousel.so"
    receipt = json.loads((psx_build / "native-receipt.json").read_text("utf-8"))
    if receipt.get("passed") is not True or receipt.get("r157Reproduced") is not True or sha(previous) != PSX_SHA:
        raise ValueError("Completed PSX-only native build required")
    output.mkdir(parents=True)
    (output / "temp").mkdir()
    overlay = output / "overlay"
    shutil.copytree(psx_build / "psx-overlay", overlay)
    mega = load(HERE / "prepare_mega_overlay.py", "r158_mega")
    hero = load(HERE / "prepare_hero_overlay.py", "r158_hero")
    (overlay / "magazine_shader.h").write_bytes(mega.patch((overlay / "magazine_shader.h").read_bytes()))
    (overlay / "native_magazine_field.h").write_bytes(mega.patch_field((overlay / "native_magazine_field.h").read_bytes()))
    (overlay / "native_formation.h").write_bytes(hero.patch((overlay / "native_formation.h").read_bytes()))
    if any(sha(overlay / f.name) != sha(f) for f in (psx_build / "psx-overlay").iterdir()
           if f.name not in ("magazine_shader.h", "native_magazine_field.h", "native_formation.h")):
        raise ValueError("An unrelated native source changed")
    command_file = R145 / "commands.json"
    if sha(command_file) != "d49eeeda3810508683352cb5682512182be8b4436f11fdbbf14aba87d052f671":
        raise ValueError("Pinned native command changed")
    rows = json.loads(command_file.read_text("utf-8"))
    commands = [row["command"] for row in rows if row["label"] == "sky-blue-bands-r145"]
    if len(commands) != 1:
        raise ValueError("Native compiler command ambiguous")
    args = [str(R145 / "overlay") if str(x).replace("\\", "/").lower() ==
            "e:/stationskybluewavesr145-20261013/native/final/overlay" else x for x in commands[0]]
    args[args.index("-I"):args.index("-I")] = ["-I", str(overlay)]
    raw = output / "combined-unlabelled.so"
    args[args.index("-o") + 1] = str(raw)
    result = subprocess.run(args, cwd=output, env={**os.environ, "TEMP": str(output / "temp"), "TMP": str(output / "temp")},
                            capture_output=True, timeout=1800)
    log = output / "combined.log"
    log.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError("Combined PSX/Mega native compilation failed")
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r158_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r158_elf")
    binary, _ = labels.patch_labels(raw.read_bytes())
    final = output / "libturbo_carousel.so"
    final.write_bytes(binary)
    if elf.elf_contract(previous.read_bytes()) != elf.elf_contract(binary):
        raise ValueError("Native ABI or alignment changed")
    warnings = lambda path: sorted(line for line in path.read_text("utf-8", errors="replace").splitlines() if "warning:" in line)
    if warnings(psx_build / "psx-r158.log") != warnings(log):
        raise ValueError("Combined native compiler warnings changed")
    proof = {"schema": "station.r158.psx-mega-cover.native.v1", "passed": True,
             "r157Reproduced": True, "psxParentSha256": PSX_SHA,
             "outputSha256": sha(final), "shaderSha256": sha(overlay / "magazine_shader.h"),
             "sourceArtDimensions": {"psx": [1024, 1536], "megaDrive": [2560, 3840]},
             "otherNativeHeadersChanged": False, "extraPerFrameDrawCalls": 0,
             "newTimersThreadsHeapAllocations": 0,
             "changedHeaders": ["magazine_shader.h", "native_magazine_field.h", "native_formation.h"],
             "psxAndMegaUseSnesInstantFieldBake": True,
             "legacyPsxOverlayRemoved": True, "legacyMegaProfilePreserved": True,
             "snesProfilePreserved": True,
             "megaTitleUsesExistingBlueEmitter": True,
             "segaNameUsesExistingBlueEmitter": True,
             "selectedGameCornersReuseSingleDraw": True}
    (output / "native-receipt.json").write_text(json.dumps(proof, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return proof


if __name__ == "__main__":
    import argparse
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--psx-build", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.psx_build.resolve(), args.out.resolve()), ensure_ascii=False))
