"""Execute actual Java Session + C++ protocol with staggered owner resumes on a host JVM.

No APK/ROM/BIOS, Android process, network, auth fixture or installed library changes.
Linux host runner; never package the fixture classes or JNI probe library.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--jdk", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--cxx", default="c++")
parser.add_argument("--session-source", type=Path, help="Optional preserved baseline Java source for A/B reproduction")
parser.add_argument("--protocol-source", type=Path, help="Optional preserved baseline C++ source for A/B reproduction")
args = parser.parse_args()
module = Path(__file__).resolve().parent.parent
repo = module.parent.parent
args.out.mkdir(parents=True, exist_ok=True)
classes = args.out / "classes"
classes.mkdir(exist_ok=True)
java = module / "java/org/emulationstation/frontend/netplay"
sources = [java / name for name in ("StationPsxSession.java", "StationPsxLaunch.java", "StationPsxPolicy.java")]
if args.session_source:
    sources[0] = args.session_source.resolve()
sources += [module / "tests" / name for name in ("StationPsxSessionProbe.java", "StationPsxResumeRaceProbe.java")]
sources += [repo / "versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationContentIdentity.java"]
sources += sorted((module / "tests/session-fixtures").rglob("*.java"))
native = [module / "tests/resume_race_jni.cpp", module / "native/StationPsxProtocol.cpp", module / "native/StationPsxSha256.cpp"]
if args.protocol_source:
    native[1] = args.protocol_source.resolve()
library = (args.out / "libstation_psx_resume_probe.so").resolve()

def run(name, command):
    result = subprocess.run([str(value) for value in command], capture_output=True, text=True, timeout=90)
    (args.out / (name + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        print(result.stdout + result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()

run("javac", [args.jdk / "bin/javac", "-encoding", "UTF-8", "-d", classes, *sources])
run("native-build", [args.cxx, "-std=c++20", "-O2", "-fPIC", "-shared", "-pthread", "-Wall", "-Wextra", "-Werror",
                     "-Wno-misleading-indentation", "-I" + str(args.jdk / "include"), "-I" + str(args.jdk / "include/linux"),
                     "-I" + str(module / "native"), *native, "-o", library])
result = run("resume-race", [args.jdk / "bin/java", "-cp", classes,
                             "org.emulationstation.frontend.netplay.StationPsxResumeRaceProbe", library])
receipt = {"passed": True, "result": result, "actualJavaAndProtocol": True, "syntheticOwner": True,
           "physicalGameplay": False, "fixtureShipped": False,
           "sources": [{"file": p.relative_to(repo).as_posix() if p.is_relative_to(repo) else p.name,
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                       for p in [*sources, *native, module / "native/StationPsxProtocol.hpp"]]}
(args.out / "resume-race-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(result)
