"""Reproduce R154 exactly, then compile only the corrected R155 carousel visual."""

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
R154 = REPO / "integration/online-wave-corrections-r154/native"
R154_SHA = "bfa8efd8b0f24d19bf5b8e08aa6464482ba18c8397cfcd8f9102825712de0452"
R154_SPACE_SHA = "39bfa18d49e381d6ef4a97f69e74a064ef4e3e34805bd46fa098f97408b7fabd"
R154_SETTINGS_SHA = "ed7a2a045e390b0801b1c153f5b0275c047653c4afcf363c0be1034b82b45ad4"
R155_SPACE_SHA = "1ae740a12b1fddd3e4ba5c3f938e76cf8f82a901d4345354d32cc30ad60205a6"
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
    if sha(old_settings) != R154_SETTINGS_SHA or sha(new_settings) != R154_SETTINGS_SHA:
        raise ValueError("Graphics settings changed outside visual scope")
    for signature in (
        "static float gameBackdropEase(float t){",
        "static const char* stationWaveSystemKey(){",
        "static const StationWavePalette* stationWaveCurrentPalette(){",
        "static unsigned stationWaveColor(int wave,const StationWavePalette*palette){",
    ):
        if function(effective, signature) != function(proposed, signature):
            raise ValueError("Unrequested carousel palette or gradient helper changed: " + signature)
    backdrop = function(proposed, "static void drawCarouselDiagonalBackdrop(float w,float h){")
    old_backdrop = function(effective, "static void drawCarouselDiagonalBackdrop(float w,float h){")
    required_backdrop = (
        "Vertex strip[754]", "for(int row=0;row<14;row++)",
        "for(int col=0;col<=25;col++)", "float t=col==0?0:(col-1)/24.f;",
        "float original=1.f-gameBackdropEase(t);",
        "float away=(w-x)/w*.22f+(h-y)/h*.78f;",
        "float ambient=.74f*gameBackdropEase(away);",
        "255.f*(original+(1.f-original)*ambient)",
    )
    if not all(fragment in backdrop for fragment in required_backdrop):
        raise ValueError("Continuous bottom-right diagonal backdrop or original samples missing")
    if any(fragment in backdrop for fragment in ("bandLeft", "bandRight", "bandTop", "bandBottom", "maskX", "maskY", "bandAlpha", "Vertex strip[782]")):
        raise ValueError("R154 horizontal cell band remains")
    draw_call = "fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);"
    if backdrop.count(draw_call) != 1 or old_backdrop.count(draw_call) != 1:
        raise ValueError("Backdrop draw-call count changed")
    space = function(proposed, "static void drawNativeSpace(float w,float h){")
    old_space = function(effective, "static void drawNativeSpace(float w,float h){")
    mode2 = "if(background==2){fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,0x000000ffu,0x000000ffu,false,4,5);return;}"
    loading = "if(gui&&at<int>(gui,0x370)==0){fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,0x000000ffu,0x000000ffu,false,4,5);return;}"
    if not all(fragment in space and fragment in old_space for fragment in (mode2, loading)):
        raise ValueError("Loading or off mode changed")
    required_route = (
        "background==1?stationWaveTop():background==3?(stationThemeId==1?0x287EB5ffu:0x000000ffu):stationSkyTop()",
        "background==1?stationWaveBottom():background==3?top:stationSkyBottom()",
        "if(background==1)drawNativeWaves(w,h,t);",
        "else if(background==0)drawNativeClouds(w,h,t);",
        "if(background==3)drawNativeOnlineRibbons(w,h,t);",
    )
    if not all(fragment in space for fragment in required_route):
        raise ValueError("Background modes diverged from R155 scope")
    if space.count("fn<unsigned(*)()>(0x39e240)()") != 1 or space.count("drawNativeClouds(w,h,t)") != 1:
        raise ValueError("Online mode added a timer or clouds leaked into it")
    online = function(proposed, "static void drawNativeOnlineRibbons(float w,float h,float t){")
    required_online = (
        "stationWaveCurrentPalette()", "static Vertex strip[206]",
        "float phase=t*.35f;", "for(unsigned layer=0;layer<4;layer++)",
        "for(int point=0;point<=24;point++)", "palette->colors[layer%palette->count]",
        "flightSin(u*6.2831853f+phase+layer*1.15f)*.055f",
        "flightSin(u*3.14159265f+phase*.7f+layer*.6f)*.035f",
        "Vertex b={x,h,0,0,bottomColor};",
        "stationOnlineRibbonMix(top,bottom,gradient)",
    )
    if not all(fragment in online for fragment in required_online) or online.count(draw_call) != 1:
        raise ValueError("Four broad filled room-style ribbons were not preserved")
    if "fn<unsigned(*)()>(0x39e240)()" in online or "drawNativeClouds" in online or "stationOnlineBezier" in proposed:
        raise ValueError("Online ribbons gained their own timer, clouds, or old thin curves")


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
    if sha(R154 / "native_space.h") != R154_SPACE_SHA or sha(R154 / "native_settings.h") != R154_SETTINGS_SHA:
        raise ValueError("Exact R154 source donor required")
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
        raise ValueError("R155 overlay missing")
    if sha(paths[0]) != R155_SPACE_SHA or sha(paths[1]) != R154_SETTINGS_SHA:
        raise ValueError("Reviewed R155 source changed after freeze")
    effective = (R154 / "native_space.h").read_text("utf-8")
    proposed = paths[0].read_text("utf-8")
    visual_guards(effective, proposed, R154 / "native_settings.h", paths[1])
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
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r155_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r155_elf")
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

    baseline_route = routed(out / "routed-r154", R154 / "native_space.h")
    baseline_deps = out / "baseline-r154.d"
    baseline = compile_one(command, [baseline_route, R154, R151 / "overlay"],
                           out, "baseline-r154", labels, baseline_deps)
    if hashlib.sha256(baseline).hexdigest() != R154_SHA:
        raise ValueError("R154 native baseline did not reproduce byte for byte")
    visual_route = routed(out / "routed-r155", paths[0])
    visual_deps = out / "visual-r155.d"
    current = compile_one(command, [visual_route, SOURCE, R151 / "overlay"],
                          out, "visual-r155", labels, visual_deps)
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
        "schema": "station.r155.visual.native.v1",
        "passed": True,
        "r154Reproduced": True,
        "baseSha256": R154_SHA,
        "outputSha256": sha(target),
        "sourceSha256": {path.name: sha(path) for path in paths},
        "nativeSpaceInclude": str(visual_route / "native_space.h"),
        "r145NativeSpaceExcluded": True,
        "installedWavePaletteSha256": R151_PALETTE_SHA,
        "originalWavesChanged": False,
        "installedAnimatedWavesPreserved": True,
        "mode0SkyCloudsPreserved": True,
        "mode3FlatBlueBase": True,
        "mode3CloudsRemoved": True,
        "mode1Mode2Preserved": True,
        "backgroundModes": ["sky-clouds", "animated-waves", "off", "room-style-ribbons-on-blue"],
        "onlineWaveRibbonCount": 4,
        "onlineWaveRibbonsBroadFilled": True,
        "onlineWaveTimersAdded": 0,
        "bottomRightDiagonalGradient": True,
        "horizontalBandRemoved": True,
        "backdropVertices": 754,
        "smoothDiagonalBackdrop": True,
        "upperCellBandRemoved": True,
        "backdropDrawCallsPerFrame": 1,
        "compiled": True,
        "installed": False,
    }
    (out / "native-receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
