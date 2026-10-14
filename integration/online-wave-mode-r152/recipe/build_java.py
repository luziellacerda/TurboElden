"""Compile R152 menu and online-view source for the two scoped DEX overlays."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "java/org/emulationstation/frontend"
PINS = {
    "android": "6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad",
    "d8": "305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5",
    "lambda": "c8a21e0e653227d1fce74bd547c9e7278e17c016c405aa8e1f6c313b192ade31",
    "client": "011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313",
    "video": "3a76446d21899722b29dcac298e7f9c16aea4c3467ff77c8eecf4a5298ad6ea4",
    "rooms": "6b2929eb3621b208593a886b6f06a32de52af9c931663cb314e197af155f773d",
    "bridge": "8a4d6b2f0ae2da3bbe3252d8b5de3aaa2fa249168f2ed006605875e38ae6ef10",
    "panel": "a67316e3283ae713b31beb726ed48325e6a024e4e89e312a63f152787480af55",
}
SOURCES = (
    SOURCE / "station/StationGraphicsPreferences.java",
    SOURCE / "station/StationGraphicsPanel.java",
    SOURCE / "netplay/StationRoomsActivity.java",
    SOURCE / "netplay/StationHyperspaceView.java",
)


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


def jar(classes: Path, output: Path, package: str) -> None:
    with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as archive:
        for path in sorted((classes / package).glob("*.class")):
            archive.write(path, path.relative_to(classes).as_posix())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("jdk", "android", "d8", "lambda", "client", "video", "rooms", "bridge", "panel", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    for name, checksum in PINS.items():
        if sha(getattr(args, name)) != checksum:
            raise ValueError("Pinned Java input differs: " + name)
    if not all(path.is_file() for path in SOURCES):
        raise ValueError("Visual source missing")
    java, javac = args.jdk / "bin/java.exe", args.jdk / "bin/javac.exe"
    if not java.is_file() or not javac.is_file():
        raise ValueError("JDK missing")
    out.mkdir(parents=True)
    for name in ("temp", "classes", "empty", "d8-28", "d8-35"):
        (out / name).mkdir()
    classpath = os.pathsep.join(map(str, (args.client, args.video, args.rooms, args.bridge, args.panel)))
    boot = os.pathsep.join(map(str, (getattr(args, "lambda"), args.android)))
    run([javac, "-encoding", "UTF-8", "-source", "8", "-target", "8",
         "-bootclasspath", boot, "-proc:none", "-implicit:none", "-sourcepath", out / "empty",
         "-cp", classpath, "-d", out / "classes", *SOURCES], out, "javac")
    classes = out / "classes"
    jar(classes, out / "classes28.jar", "org/emulationstation/frontend/station")
    jar(classes, out / "classes35.jar", "org/emulationstation/frontend/netplay")
    common = [java, "-cp", args.d8, "com.android.tools.r8.D8", "--release", "--min-api", "28", "--lib", args.android]
    run(common + ["--classpath", args.client, "--classpath", args.video,
                  "--output", out / "d8-28", out / "classes28.jar"], out, "d8-28")
    run(common + ["--classpath", args.client, "--classpath", args.video,
                  "--classpath", args.rooms, "--classpath", out / "classes28.jar",
                  "--output", out / "d8-35", out / "classes35.jar"], out, "d8-35")
    receipt = {"schema": "station.r152.visual.java.v1", "passed": True,
               "sourceSha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in SOURCES},
               "overlayDexSha256": {name: sha(out / name / "classes.dex") for name in ("d8-28", "d8-35")},
               "compiled": True, "installed": False}
    (out / "java-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", "utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
