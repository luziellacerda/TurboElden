"""Compile only the R157 online-room View family for a scoped DEX35 overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "java/org/emulationstation/frontend/netplay/StationHyperspaceView.java"
PREFERENCES = ROOT.parent / "online-wave-mode-r152/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java"
PINS = {
    "android": "6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad",
    "d8": "305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5",
    "lambda_stubs": "c8a21e0e653227d1fce74bd547c9e7278e17c016c405aa8e1f6c313b192ade31",
    "client": "011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313",
    "rooms": "6b2929eb3621b208593a886b6f06a32de52af9c931663cb314e197af155f773d",
}
PREFERENCES_SHA = "307576547697920da23b8079332f1e2b4d4af05cc303834c9d81726ce8d21aa4"
VIEW = "org/emulationstation/frontend/netplay/StationHyperspaceView"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(command: list[str | Path], out: Path, label: str) -> None:
    environment = {**os.environ, "TEMP": str(out / "temp"), "TMP": str(out / "temp")}
    process = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                             encoding="utf-8", errors="replace", env=environment, timeout=1800)
    (out / (label + ".log")).write_text(process.stdout + process.stderr, "utf-8")
    if process.returncode:
        raise ValueError(label + " failed; inspect isolated log")


def archive_classes(classes: Path, target: Path, prefix: str) -> list[str]:
    root_name = Path(prefix).name
    selected = sorted(path for path in (classes / prefix).parent.glob(root_name + "*.class")
                      if path.stem == root_name or path.stem.startswith(root_name + "$"))
    if not selected or not (classes / (prefix + ".class")).is_file():
        raise ValueError("Expected online View class was not compiled")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_STORED) as archive:
        for path in selected:
            archive.write(path, path.relative_to(classes).as_posix())
    return [path.relative_to(classes).as_posix() for path in selected]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("jdk", "android", "d8", "lambda-stubs", "client", "rooms", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    for name, checksum in PINS.items():
        path = getattr(args, name)
        if sha(path) != checksum:
            raise ValueError("Pinned Java input differs: " + name)
    if not SOURCE.is_file() or not PREFERENCES.is_file() or sha(PREFERENCES) != PREFERENCES_SHA:
        raise ValueError("R157 View or pinned R152 graphics compile dependency differs")
    java, javac = args.jdk / "bin/java.exe", args.jdk / "bin/javac.exe"
    if not java.is_file() or not javac.is_file():
        raise ValueError("Pinned JDK missing")
    out.mkdir(parents=True)
    for name in ("temp", "classes", "empty", "d8"):
        (out / name).mkdir()
    classpath = os.pathsep.join(map(str, (args.client, args.rooms)))
    boot = os.pathsep.join(map(str, (args.lambda_stubs, args.android)))
    run([javac, "-encoding", "UTF-8", "-source", "8", "-target", "8",
         "-bootclasspath", boot, "-proc:none", "-implicit:none", "-sourcepath", out / "empty",
         "-cp", classpath, "-d", out / "classes", PREFERENCES, SOURCE], out, "javac")
    classes = out / "classes"
    netplay_dir = classes / "org/emulationstation/frontend/netplay"
    netplay_classes = sorted(netplay_dir.glob("*.class"))
    if {path.name for path in netplay_classes} != {"StationHyperspaceView.class"}:
        raise ValueError("R157 must compile exactly one online View class")
    overlay_classes = archive_classes(classes, out / "online-view.jar", VIEW)
    if overlay_classes != [VIEW + ".class"]:
        raise ValueError("R157 View overlay contains another class")
    graphics_dir = classes / "org/emulationstation/frontend/station"
    graphics_classes = sorted(graphics_dir.glob("StationGraphicsPreferences*.class"))
    if not graphics_classes:
        raise ValueError("Graphics compile dependency was not built")
    with zipfile.ZipFile(out / "graphics-compile-only.jar", "w", zipfile.ZIP_STORED) as archive:
        for path in graphics_classes:
            archive.write(path, path.relative_to(classes).as_posix())
    run([java, "-cp", args.d8, "com.android.tools.r8.D8", "--release", "--min-api", "28",
         "--lib", args.android, "--classpath", args.client, "--classpath", args.rooms,
         "--classpath", out / "graphics-compile-only.jar", "--output", out / "d8",
         out / "online-view.jar"], out, "d8")
    dex = out / "d8/classes.dex"
    if not dex.is_file():
        raise ValueError("D8 online View overlay missing")
    receipt = {
        "schema": "station.r157.online-wave.java.v1", "passed": True,
        "sourceSha256": sha(SOURCE), "graphicsCompileDependencySha256": sha(PREFERENCES),
        "overlayClassFiles": overlay_classes, "overlayDexSha256": sha(dex),
        "sourceFamily": VIEW, "otherJavaRuntimeChanged": False,
    }
    (out / "java-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", "utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
