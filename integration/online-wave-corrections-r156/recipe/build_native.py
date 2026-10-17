"""Reproduce R155 exactly, then compile only the corrected R156 online ribbons."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE.parent / "native"
R145 = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/reconstrucao-atual/sky-blue-waves-r145-20261013/build/native/final")
R151 = Path("E:/StationVisualR151-20261014/native-final")
R155 = REPO / "integration/online-wave-corrections-r155/native"
R155_SHA = "f0adaf5fdf9c1fe9ddb86bac2195599a441b69fe0fe9b222d911d6daa2c8f5b2"
R155_SPACE_SHA = "1ae740a12b1fddd3e4ba5c3f938e76cf8f82a901d4345354d32cc30ad60205a6"
R155_SETTINGS_SHA = "ed7a2a045e390b0801b1c153f5b0275c047653c4afcf363c0be1034b82b45ad4"
R156_SPACE_SHA = "1b93e7564a9f5b5db3dd440f9f368dc9bd4f6bbdf99291349e45b163d6a0da3e"
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
    if sha(old_settings) != R155_SETTINGS_SHA or sha(new_settings) != R155_SETTINGS_SHA:
        raise ValueError("Graphics settings changed outside online-ribbon scope")
    old_online_marker = "// Room reference:"
    online_marker = "// Match the online room"
    space_signature = "static void drawNativeSpace(float w,float h){"
    if old_online_marker not in effective or online_marker not in proposed or space_signature not in effective or space_signature not in proposed:
        raise ValueError("Online source boundary missing")
    old_start, new_start = effective.index(old_online_marker), proposed.index(online_marker)
    old_end, new_end = effective.index(space_signature), proposed.index(space_signature)
    if old_start >= old_end or new_start >= new_end:
        raise ValueError("Online source boundary order changed")
    if effective[:old_start] != proposed[:new_start]:
        raise ValueError("Backdrop, wave geometry, system palettes, or native setup changed")
    if effective[old_end:] != proposed[new_end:]:
        raise ValueError("Background routing, timer, or draw order changed")
    old_online, online = effective[old_start:old_end], proposed[new_start:new_end]
    if old_online == online:
        raise ValueError("R156 has no online-ribbon change")
    if "static void drawNativeOnlineRibbons(float w,float h,float t){" not in online:
        raise ValueError("Three-ribbon renderer missing")
    executable = re.sub(r"//[^\n]*", "", online)
    if any(fragment in executable for fragment in (
        "fn<unsigned(*)()>(0x39e240)()", "drawNativeClouds", "pthread_create", "std::thread",
        "std::async", "malloc(", "calloc(", "realloc(", "operator new", "new ",
    )):
        raise ValueError("Online change added a timer, thread, cloud pass, or heap allocation")
    draw = function(online, "static void drawNativeOnlineRibbons(float w,float h,float t){")
    draw_call = "fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(strip,count,4,5);"
    required = (
        "static Vertex strip[154];unsigned count=0;",
        "for(unsigned layer=0;layer<3;layer++)",
        "for(int point=0;point<=24;point++)",
        "if(layer&&point==0){strip[count]=strip[count-1];count++;strip[count++]=a;}",
        "strip[count++]=a;strip[count++]=b;",
        "Vertex b={x,h,0,0,bottomColor};",
        "stationOnlineRibbonMix(top,bottom,gradient)",
        "float primary=t*phaseSpeed[layer]+drift+layer*1.15f;",
        "float secondary=t*phaseSpeed[layer]*.73f+drift*.55f+layer*.6f;",
        "float envelope=1.f+.20f*flightSin(t*(.11f+.023f*layer)+layer*2.07f);",
        "float bob=.014f*flightSin(t*(.19f+.027f*layer)+layer*1.41f);",
        "float curve=envelope*(flightSin(u*6.2831853f+primary)*.055f+",
        "flightSin(u*3.14159265f+secondary)*.035f);",
    )
    if not all(fragment in draw for fragment in required) or draw.count(draw_call) != 1:
        raise ValueError("Three broad filled animated ribbons or one-draw mesh missing")
    # Three 25-point ribbons use 150 vertices plus two degenerate joins of two
    # vertices each. The bounded motion keeps the upper edge inside the screen:
    # 0.59..0.70 baseline +/-0.014 bob +/-1.20*(.055+.035) = 0.468..0.822.
    speeds = re.search(r"static const float phaseSpeed\[3\]=\{([^}]+)\};", draw)
    if not speeds:
        raise ValueError("Independent ribbon phase speeds missing")
    values = [float(token.strip().removesuffix("f")) for token in speeds.group(1).split(",")]
    if len(values) != 3 or len(set(values)) != 3 or any(not (.35 < speed <= 1.0) for speed in values):
        raise ValueError("Ribbon phase speeds are not distinct, faster, and bounded")
    if "stationWaveCurrentPalette" in online or "palette->" in online or "stationOnlineRibbonDim" in online:
        raise ValueError("Mode 3 still depends on console palette or orphan R155 color helper")
    helpers = re.findall(r"(?m)^static (?:unsigned|void|float) (stationOnline\w+|drawNativeOnlineRibbons)\(", online)
    if helpers != ["stationOnlineRibbonMix", "drawNativeOnlineRibbons"] or draw.count("stationOnlineRibbonMix(") != 1:
        raise ValueError("Online helper is unused or unexpected visual code was added")
    if function(proposed, space_signature).count("if(background==3)drawNativeOnlineRibbons(w,h,t);") != 1:
        raise ValueError("R156 online renderer is not linked to active mode 3")
    def colors(name: str) -> list[tuple[int, int, int]]:
        match = re.search(r"static const unsigned " + name + r"\[3\]=\{([^}]+)\};", draw)
        if not match:
            raise ValueError("Fixed blue ribbon palette missing: " + name)
        packed = [int(token.strip().removesuffix("u"), 16) for token in match.group(1).split(",")]
        if len(packed) != 3:
            raise ValueError("Blue palette count changed: " + name)
        return [((color >> 24) & 255, (color >> 16) & 255, (color >> 8) & 255) for color in packed]
    for suffix in ("Top", "Bottom"):
        for family in ("blue", "dark"):
            rgb = colors(family + suffix)
            brightness = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in rgb]
            if not all(rgb[i][2] > rgb[i][0] and brightness[i] < brightness[i + 1] for i in range(2)) or rgb[2][2] <= rgb[2][0]:
                raise ValueError("Three fixed blue layers are not dark-to-light")
    if "unsigned top=stationThemeId==1?blueTop[layer]:darkTop[layer];" not in draw or "unsigned bottom=stationThemeId==1?blueBottom[layer]:darkBottom[layer];" not in draw:
        raise ValueError("Blue ribbon palette does not cover both themes")


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
    if sha(R155 / "native_space.h") != R155_SPACE_SHA or sha(R155 / "native_settings.h") != R155_SETTINGS_SHA:
        raise ValueError("Exact R155 source donor required")
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
        raise ValueError("R156 overlay missing")
    if sha(paths[0]) != R156_SPACE_SHA or sha(paths[1]) != R155_SETTINGS_SHA:
        raise ValueError("Reviewed R156 source changed after freeze")
    effective = (R155 / "native_space.h").read_text("utf-8")
    proposed = paths[0].read_text("utf-8")
    visual_guards(effective, proposed, R155 / "native_settings.h", paths[1])
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
    labels = load(REPO / "integration/wave-palette-r144-20261013-final/recipe/build_native.py", "r156_labels")
    elf = load(REPO / "integration/sky-blue-waves-r145-20261013/recipe/common.py", "r156_elf")
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

    baseline_route = routed(out / "routed-r155", R155 / "native_space.h")
    baseline_deps = out / "baseline-r155.d"
    baseline = compile_one(command, [baseline_route, R155, R151 / "overlay"],
                           out, "baseline-r155", labels, baseline_deps)
    if hashlib.sha256(baseline).hexdigest() != R155_SHA:
        raise ValueError("R155 native baseline did not reproduce byte for byte")
    visual_route = routed(out / "routed-r156", paths[0])
    visual_deps = out / "visual-r156.d"
    current = compile_one(command, [visual_route, SOURCE, R151 / "overlay"],
                          out, "visual-r156", labels, visual_deps)
    def warning_lines(path: Path) -> list[str]:
        return sorted(line for line in path.read_text("utf-8", errors="replace").splitlines() if "warning:" in line)
    if warning_lines(out / "baseline-r155.log") != warning_lines(out / "visual-r156.log"):
        raise ValueError("R156 introduced a compiler warning")
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
        "schema": "station.r156.visual.native.v1",
        "passed": True,
        "r155Reproduced": True,
        "baseSha256": R155_SHA,
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
        "onlineWaveRibbonCount": 3,
        "onlineWaveVertices": 154,
        "onlineWaveRibbonsBroadFilled": True,
        "onlineRibbonMotionExpanded": True,
        "onlineRibbonBlueGradientDarkToLight": True,
        "onlineRibbonBlueForAllSystems": True,
        "backdropPreservedFromR155": True,
        "timerCountUnchanged": True,
        "onlyActiveMode3RoutineChanged": True,
        "noDeadVisualHelpersAdded": True,
        "noNewTimersThreadsHeapAllocations": True,
        "compilerWarningsUnchanged": True,
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
