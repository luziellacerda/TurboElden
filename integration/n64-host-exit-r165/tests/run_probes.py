"""Manual, offline R165 JVM probe and API34 source compilation; no APK or ADB."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE.parent / "java/org/emulationstation/frontend/netplay/StationHumanDeparture.java"
JSON_SHA256 = "3cf6cd6892e32e2b4c1c39e0f52f5248a2f5b37646fdfbb79a66b46b618414ed"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    subprocess.run([str(part) for part in args], check=True, timeout=40)


def main():
    parser = argparse.ArgumentParser()
    for name in ("out", "jdk-bin", "json-jar", "android-jar", "rooms-jar", "client-jar"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads((ROOT / "integration/online-lifecycle-review-r135/SOURCE-PINS.json").read_text(
        encoding="utf-8"))["inputsSha256"]
    paths = {
        "javac": args.jdk_bin / "javac.exe",
        "java": args.jdk_bin / "java.exe",
        "androidJar": args.android_jar,
        "roomsJar": args.rooms_jar,
        "clientJar": args.client_jar,
    }
    for name, path in paths.items():
        if digest(path) != pins[name]:
            raise ValueError("R135-pinned input mismatch: " + name)
    if digest(args.json_jar) != JSON_SHA256:
        raise ValueError("R165 JSON test dependency mismatch")
    if args.out.exists() and any(args.out.iterdir()):
        raise ValueError("Output directory must be empty")
    args.out.mkdir(parents=True, exist_ok=True)
    javac, java = paths["javac"], paths["java"]
    production = args.out / "production"
    production.mkdir()
    prod_cp = ";".join(map(str, [args.android_jar, args.rooms_jar, args.client_jar]))
    run([javac, "--release", "8", "-encoding", "UTF-8", "-proc:none", "-sourcepath", "",
         "-cp", prod_cp, "-d", production, SOURCE])
    fixture = args.out / "fixture"
    fixture.mkdir()
    sources = [SOURCE, HERE / "StationHumanDepartureR165Test.java", *sorted((HERE / "fixtures").rglob("*.java"))]
    run([javac, "--release", "8", "-encoding", "UTF-8", "-proc:none", "-cp", args.json_jar,
         "-d", fixture, *sources])
    run([java, "-cp", str(fixture) + ";" + str(args.json_jar),
         "org.emulationstation.frontend.netplay.StationHumanDepartureR165Test"])
    receipt = {"baseline": "a762b4614d4c1909ea9482028c4d6464de49f2a2",
               "scope": "JVM fixture + API34 source compile; no Android device/server/APK test",
               "helperSha256": digest(SOURCE), "inputSha256": {k: digest(v) for k, v in paths.items()},
               "jsonJarSha256": digest(args.json_jar), "assertions": 71, "passed": True}
    (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("receipt=" + str(args.out / "receipt.json"))


if __name__ == "__main__":
    main()
