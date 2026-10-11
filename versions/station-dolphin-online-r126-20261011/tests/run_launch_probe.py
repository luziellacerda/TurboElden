"""Compile the real private Dolphin launch and run its isolated JVM probe.

No Android API is executed and no emulator, room authentication, network,
APK signing or phone operation is performed by this probe.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess

HERE = Path(__file__).resolve().parent.parent
ALLOWED = Path(r"G:\StationDolphinR126")

def fs(path):
    path = Path(path).absolute()
    if os.name != "nt": return path
    value = str(path)
    if value.startswith("\\\\?\\"): return path
    return Path("\\\\?\\UNC\\" + value[2:] if value.startswith("\\\\") else "\\\\?\\" + value)

def sha(path):
    return hashlib.sha256(fs(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("out", "jdk", "android-jar", "json-jar", "rooms-jar", "client-jar"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    out = a.out.resolve()
    if ALLOWED.resolve() not in out.parents or fs(out).exists():
        raise ValueError("Use a new isolated child of G:\\StationDolphinR126")
    fs(out).mkdir(parents=True)
    sources = [HERE / "java/org/emulationstation/frontend/netplay/StationDolphinLaunch.java",
               HERE / "tests/StationDolphinLaunchProbe.java"]
    copied = []
    for source in sources:
        target = out / source.name
        fs(target).write_bytes(fs(source).read_bytes()); copied.append(target)
    deps = [a.json_jar, a.android_jar, a.rooms_jar, a.client_jar]
    cp = os.pathsep.join(str(path.resolve()) for path in deps)
    classes = out / "classes"; fs(classes).mkdir()
    command = [str(a.jdk / "javac.exe"), "--release", "8", "-encoding", "UTF-8", "-proc:none",
               "-cp", cp, "-d", str(classes), *map(str, copied)]
    compile_result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    fs(out / "javac.log").write_text(compile_result.stdout + compile_result.stderr, encoding="utf-8")
    if compile_result.returncode: raise RuntimeError("Launch probe compilation failed; inspect javac.log")
    run = [str(a.jdk / "java.exe"), "-cp", str(classes) + os.pathsep + cp,
           "org.emulationstation.frontend.netplay.StationDolphinLaunchProbe", str(out / "fixtures")]
    result = subprocess.run(run, capture_output=True, text=True, encoding="utf-8", errors="replace")
    fs(out / "probe.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    match = re.fullmatch(r"launchChecks=(\d+) physicalGameplayValidated=false\s*", result.stdout)
    if result.returncode or not match or int(match[1]) != 231:
        raise RuntimeError("Actual launch probe did not pass all 231 checks")
    receipt = {"schemaVersion": 1, "checks": int(match[1]), "failures": 0,
               "actualProductionLaunchCompiled": True,
               "sourceSha256": {path.relative_to(HERE).as_posix(): sha(path) for path in sources},
               "dependencySha256": {path.name: sha(path) for path in deps},
               "scope": ["private-descriptor-validation", "two-to-four-signed-shape-fixtures",
                         "canonical-controller-profile-and-options", "bounded-private-input-copy",
                         "Unicode-input-profile", "cancellation", "atomic-input-replacement"],
               "roomAuthenticationVerified": False, "androidApisExecuted": False,
               "emulatorExecuted": False, "physicalGameplayValidated": False,
               "apkChanged": False}
    fs(out / "launch-probe-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": receipt["checks"], "failures": 0, "physicalGameplayValidated": False}))

if __name__ == "__main__": main()
