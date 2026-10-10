from pathlib import Path
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(r"E:\ESTUDO APK\work\station-render-precision-r102-20261010")
OUT = WORK / "baseline"
OUT.mkdir(exist_ok=False)
(OUT / "temp").mkdir()

CAROUSEL_SHA = "15de577c4274ec89808156fc583920828d7aa97c31c7bab54f72856b916c8861"
FRONTEND_SHA = "d3bc8ef6fcd88a5cf16b577fdba83e5242a75f1d946a17019075ab56a9fe95ad"
COMPILER_SHA = "1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3"
NDK = Path(r"E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin")


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(command, label):
    environment = dict(os.environ, TEMP=str(OUT / "temp"), TMP=str(OUT / "temp"))
    result = subprocess.run(list(map(str, command)), capture_output=True, env=environment)
    (OUT / f"{label}.log").write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"{label} failed: {result.returncode}")
    return result.stdout.decode("utf-8", "replace")


assert sha(NDK / "clang++.exe") == COMPILER_SHA
spec = json.loads(
    Path(r"E:\ESTUDO APK\work\station-snes-light-maps-r95-20261009\carousel-command.json").read_text()
)
carousel = OUT / "libturbo_carousel.so"
command = [
    value.replace("{BACKUP}/test-up-to-4-players-r95", str(WORK)).replace("{OUTPUT}", str(carousel))
    for value in spec["command"]
]
run(command, "carousel")
assert sha(carousel) == CAROUSEL_SHA

frontend = OUT / "libstation_frontend.so"
frontend_root = WORK / "frontend"
run(
    [
        NDK / "clang++.exe",
        "--target=aarch64-linux-android26",
        "-std=c++17",
        "-shared",
        "-fPIC",
        "-O2",
        "-Wl,-z,max-page-size=16384",
        "-Wl,--no-undefined",
        "-fvisibility=hidden",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-Wno-return-type-c-linkage",
        "-static-libstdc++",
        "-Wl,--exclude-libs,ALL",
        "-I",
        frontend_root,
        frontend_root / "station_frontend.cpp",
        "-ldl",
        "-llog",
        "-o",
        frontend,
    ],
    "frontend",
)
assert sha(frontend) == FRONTEND_SHA

symbols = run([NDK / "llvm-nm.exe", "--defined-only", "--dynamic", frontend], "frontend-symbols")
segments = run([NDK / "llvm-readelf.exe", "-lW", frontend], "frontend-segments")
loads = [line.split() for line in segments.splitlines() if line.strip().startswith("LOAD")]
assert loads and all(row[-1] == "0x4000" for row in loads)

receipt = {
    "carouselSHA256": sha(carousel),
    "frontendSHA256": sha(frontend),
    "compilerSHA256": sha(NDK / "clang++.exe"),
    "frontendSymbols": sorted(line.split()[-1] for line in symbols.splitlines() if line.split()),
    "frontendLoadAlignment": "0x4000",
    "exactR99Reproduction": True,
}
(ROOT / "evidence").mkdir(exist_ok=True)
(ROOT / "evidence/native-baselines.json").write_text(
    json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(receipt, indent=2))
