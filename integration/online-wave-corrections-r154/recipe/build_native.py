"""Reproduce R153 exactly, then compile only the corrected R154 carousel visual."""

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
R153 = REPO / "integration/online-wave-corrections-r153/native"
R153_SHA = "70526c14a9ccdb9c7f1fc3048fb8f7f5ecc55fe8103d5d2c0c855a73bf375416"
R153_SPACE_SHA = "1b4c81395da6dc54e843344e841c28421d3fbab69fda061e34eb6a0f48df6a0f"
R153_SETTINGS_SHA = "ed7a2a045e390b0801b1c153f5b0275c047653c4afcf363c0be1034b82b45ad4"
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


def function(source: str, signature: str) -> str:
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise ValueError("Unclosed native function: " + signature)


def visual_guards(effective: str, proposed: str, old_settings: Path, new_settings: Path) -> None:
    if native_waves(effective) != native_waves(proposed) or theme_wave_gradient(effective) != theme_wave_gradient(proposed):
        raise ValueError("Installed animated Ondas mode changed")
    if sha(old_settings) != R153_SETTINGS_SHA or sha(new_settings) != R153_SETTINGS_SHA:
        raise ValueError("Graphics settings changed outside visual scope")
    backdrop = function(proposed, "static void drawCarouselDiagonalBackdrop(float w,float h){")
    old_backdrop = function(effective, "static void drawCarouselDiagonalBackdrop(float w,float h){")
    required_backdrop = (
        "stationCarouselGeometry::neighborCount(stationCarouselStyle(),stationGraphicsEnabled(16))",
        "if(lastSlot!=10)lastSlot=6;",
        "auto first=coverSlot(gui,1.f),last=coverSlot(gui,(float)lastSlot);",
        "lastSlot!=previousLastSlot",
        "float rowY[15]", "for(int row=0;row<14;row++)", "for(int col=0;col<=26;col++)",
        "float regularT=col==0?0:col==26?1.f:(col-1)/24.f;",
        "if(col==25){", "x=bandRight<minimum?minimum:bandRight;if(x>w)x=w;",
        "255.f*(1.f-gameBackdropEase(t))", "maskX", "maskY", "bandTop", "bandBottom",
        "baseAlpha>bandAlpha?baseAlpha:bandAlpha", "Vertex strip[782]",
    )
    if not all(fragment in backdrop for fragment in required_backdrop):
        raise ValueError("Upper-cell fade did not preserve the original diagonal mesh")
    draw_call = "fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);"
    if backdrop.count(draw_call) != 1 or old_backdrop.count(draw_call) != 1:
        raise ValueError("Backdrop draw-call count changed")
    if "1.f-.25f*gameBackdropEase(t)" in backdrop:
        raise ValueError("Full-screen R153 dimmer remains")
    space = function(proposed, "static void drawNativeSpace(float w,float h){")
    required_route = (
        "background==1?stationWaveTop():stationSkyTop()",
        "background==1?stationWaveBottom():stationSkyBottom()",
        "if(background==1)drawNativeWaves(w,h,t);",
        "drawNativeClouds(w,h,t);",
        "if(background==3)drawNativeOnlineWaves(w,h);",
    )
    if not all(fragment in space for fragment in required_route):
        raise ValueError("R152 sky and cloud path was not restored for Online")
    if space.count("fn<unsigned(*)()>(0x39e240)()") != 1:
        raise ValueError("Online mode added or removed a frame timer")
    online = function(proposed, "static void drawNativeOnlineWaves(float w,float h){")
    required_online = (
        "static Vertex strip[270]", "static const float centers[4]={.48f,.54f,.60f,.66f}",
        "static const float amplitudes[4]={.055f,.075f,.095f,.070f}",
        "static const float strokes[4]={14.f,7.f,2.2f,1.3f}",
        "stationWaveCurrentPalette()", "stationOnlineBezier(",
        "fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);",
    )
    if not all(fragment in online for fragment in required_online):
        raise ValueError("Online curves diverged from the room geometry")
    if "fn<unsigned(*)()>(0x39e240)()" in online or "drawNativeClouds" in online:
        raise ValueError("Online curves gained an independent timer or cloud pass")


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
    if sha(R153 / "native_space.h") != R153_SPACE_SHA or sha(R153 / "native_settings.h") != R153_SETTINGS_SHA:
        raise ValueError("Exact R153 source donor required")
    prior_skin = R145 / "overlay/native_skin.h"
    if sha(prior_skin) != R145_SKIN_SHA:
        raise ValueError("R145 native skin donor differs")
    prior_space = R145 / "overlay/native_space.h"
    if sha(prior_space) != R145_SPACE_SHA:
        raise ValueError("Effective installed Ondas donor differs")
    prior_palette = R151 / "overlay/station_wave_palette.h"
    if sha(prior_palette) != R151_PALETTE_SHA:
        raise ValueError("Effective R152 wave palette differs")
    paths = [SOURCE / "native_space.h", SOURCE / "native_settings.h"]
    if not all(path.is_file() for path in paths):
        raise ValueError("R154 overlay missing")
    # R152's installed Online choice displayed the sky/cloud path because its
    # visual header was shadowed. R154 restores that path and limits dimming
    # to the upper cover row while retaining the room's four-curve geometry.
    effective = prior_space.read_text("utf-8")
    proposed = paths[0].read_text("utf-8")
    visual_guards(effective, proposed, R153 / "native_settings.h", paths[1])
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
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r154_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r154_elf")
    out.mkdir(parents=True)
    (out / "temp").mkdir()
    # Quoted include in native_skin.h outranks -I. Put the pinned skin and each
    # intended native_space.h side by side, then prove both dependency chains.
    def routed(directory: Path, space: Path) -> Path:
        directory.mkdir()
        (directory / "native_skin.h").write_bytes(prior_skin.read_bytes())
        (directory / "native_space.h").write_bytes(space.read_bytes())
        if sha(directory / "native_skin.h") != R145_SKIN_SHA or sha(directory / "native_space.h") != sha(space):
            raise ValueError("Native header route differs")
        return directory

    baseline_route = routed(out / "routed-r153", R153 / "native_space.h")
    baseline_deps = out / "baseline-r153.d"
    baseline = compile_one(command, [baseline_route, R153, R151 / "overlay"],
                           out, "baseline-r153", labels, baseline_deps)
    if hashlib.sha256(baseline).hexdigest() != R153_SHA:
        raise ValueError("R153 native baseline did not reproduce byte for byte")
    visual_route = routed(out / "routed-r154", paths[0])
    visual_deps = out / "visual-r154.d"
    current = compile_one(command, [visual_route, SOURCE, R151 / "overlay"],
                          out, "visual-r154", labels, visual_deps)
    old_space = str(R145 / "overlay/native_space.h").replace("\\", "/").lower()
    installed_palette = str(prior_palette).replace("\\", "/").lower()
    for dependencies, route in ((baseline_deps, baseline_route), (visual_deps, visual_route)):
        if not dependencies.is_file():
            raise ValueError("Native include proof missing: " + str(dependencies))
        dependency_text = dependencies.read_text("utf-8", errors="replace").replace("\\\n", "")
        dependency_text = dependency_text.replace("\\ ", " ").replace("\\", "/").lower()
        routed_space = str(route / "native_space.h").replace("\\", "/").lower()
        if routed_space not in dependency_text or old_space in dependency_text or installed_palette not in dependency_text:
            raise ValueError("Native visual header or installed palette was shadowed")
    target = out / "libturbo_carousel.so"
    target.write_bytes(current)
    old, new = elf.elf_contract(baseline), elf.elf_contract(current)
    if old["exports"] != new["exports"] or old["needed"] != new["needed"] or old["soname"] != new["soname"] or old["minimumLoadAlignment"] < 16384 or new["minimumLoadAlignment"] < 16384:
        raise ValueError("Native ABI or alignment changed")
    receipt = {
        "schema": "station.r154.visual.native.v1",
        "passed": True,
        "r153Reproduced": True,
        "baseSha256": R153_SHA,
        "outputSha256": sha(target),
        "sourceSha256": {path.name: sha(path) for path in paths},
        "nativeSpaceInclude": str(visual_route / "native_space.h"),
        "r145NativeSpaceExcluded": True,
        "installedWavePaletteSha256": R151_PALETTE_SHA,
        "originalWavesChanged": False,
        "installedAnimatedWavesPreserved": True,
        "backgroundPreservedFromR152": True,
        "backgroundModes": ["sky", "animated-waves", "off", "online-curves-over-sky-clouds"],
        "staticOnlineWaveVertices": 270,
        "staticOnlineWaveDrawCallsPerFrame": 1,
        "staticOnlineWaveTimersAdded": 0,
        "fadeLimitedToUpperCells": True,
        "backdropVertices": 782,
        "originalBackdropSamplesPreserved": True,
        "backdropDrawCallsPerFrame": 1,
        "compiled": True,
        "installed": False,
    }
    (out / "native-receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
