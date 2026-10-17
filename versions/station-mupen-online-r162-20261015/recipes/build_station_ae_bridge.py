"""Build an isolated Android AE bridge for the Station N64 core.

The pinned AE bridge hardcodes the offline Mupen core in its video-extension
registration. This recipe changes that one library name in a copied source
file, then builds a second bridge. It never changes the offline AE bridge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


UPSTREAM_COMMIT = "33bf7021549d7873e976884370fbd1a8e7333bc7"
OFFLINE_CORE = b'libmupen64plus-core.so'
STATION_CORE = b'libstation_mupen64plus_core.so'
SONAME = "libstation_ae_bridge.so"
ORIGINAL_BRIDGE_SHA256 = "ba5a7582295215f159e197f805dbfe85851aa912462996870f61ccd752ecb360"
CPP_RUNTIME_SHA256 = "fa2c06d3c09c0d9a4931fa7cd03a3aba15f6ed7ea990d8e4a37b8a5811867c0d"
ORIGINAL_OVERRIDE = b'''extern "C" DECLSPEC void overrideAeVidExtFuncs(void)
{
\tCoreHandle = dlopen("libmupen64plus-core.so", RTLD_NOW);
\tCoreOverrideVidExt    = (ptr_CoreOverrideVidExt)   dlsym(CoreHandle, "CoreOverrideVidExt");
\tDebugMemGetPointer    = (ptr_DebugMemGetPointer)    dlsym(CoreHandle, "DebugMemGetPointer");
\tCoreOverrideVidExt(&vidExtFunctions);
}'''
STATION_OVERRIDE = b'''static int gStationVideoOverrideReady = 0;

extern "C" DECLSPEC int stationVideoOverrideReady(void)
{
    return gStationVideoOverrideReady;
}

extern "C" DECLSPEC void overrideAeVidExtFuncs(void)
{
    gStationVideoOverrideReady = 0;
    CoreHandle = dlopen("libstation_mupen64plus_core.so", RTLD_NOW);
    if (CoreHandle == NULL) {
        LOGE("Station video override: core load failed: %s", dlerror());
        return;
    }
    CoreOverrideVidExt = (ptr_CoreOverrideVidExt)dlsym(CoreHandle, "CoreOverrideVidExt");
    DebugMemGetPointer = (ptr_DebugMemGetPointer)dlsym(CoreHandle, "DebugMemGetPointer");
    if (CoreOverrideVidExt == NULL || DebugMemGetPointer == NULL) {
        LOGE("Station video override: required core symbols missing");
        return;
    }
    m64p_error result = CoreOverrideVidExt(&vidExtFunctions);
    if (result != M64ERR_SUCCESS) {
        LOGE("Station video override: CoreOverrideVidExt failed (%d)", result);
        return;
    }
    gStationVideoOverrideReady = 1;
}'''
EXPECTED_NEEDED = {
    "liblog.so", "libEGL.so", "libandroid.so", "libc.so", "libm.so",
    "libn64cpp.so", "libdl.so",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {args[0]}\n"
            + result.stdout + result.stderr
        )
    return result.stdout


def build(upstream: Path, ndk: Path, original_bridge: Path, cpp_runtime: Path,
          output: Path) -> dict:
    upstream = upstream.resolve(strict=True)
    ndk = ndk.resolve(strict=True)
    original_bridge = original_bridge.resolve(strict=True)
    cpp_runtime = cpp_runtime.resolve(strict=True)
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory must be empty")
    if output == upstream or upstream in output.parents or output in upstream.parents:
        raise ValueError("Output and pinned source must be separate")
    if run(["git", "rev-parse", "HEAD"], cwd=upstream).strip() != UPSTREAM_COMMIT:
        raise ValueError("Wrong Mupen64Plus AE source commit")
    tracked = [
        "ae-bridge/src/ae_bridge.cpp",
        "ae-bridge/src/ae_bridge.h",
        "ae-bridge/src/ae_ra_internal.c",
        "mupen64plus-core/upstream/src/api",
        "ndkLibs/GL/GL/EGLLoader.h",
        "ndkLibs/rcheevos/include",
        "ndkLibs/rcheevos/src",
        "ndkLibs/libs/release/arm64-v8a/libEGLLoader.a",
        "ndkLibs/libs/release/arm64-v8a/librcheevos.a",
    ]
    if run(["git", "status", "--porcelain", "--", *tracked], cwd=upstream).strip():
        raise ValueError("Pinned native inputs have local modifications")
    source = upstream / tracked[0]
    data = source.read_bytes()
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    original_override = ORIGINAL_OVERRIDE.replace(b"\n", newline)
    station_override = STATION_OVERRIDE.replace(b"\n", newline)
    if data.count(OFFLINE_CORE) != 1 or data.count(original_override) != 1:
        raise ValueError("AE bridge video override no longer matches pinned source")
    if STATION_CORE in data:
        raise ValueError("Source already contains Station core name")

    tool = ndk / "toolchains/llvm/prebuilt/windows-x86_64/bin"
    clang = tool / "clang.exe"
    clangxx = tool / "clang++.exe"
    readelf = tool / "llvm-readelf.exe"
    strip = tool / "llvm-strip.exe"
    for item in (clang, clangxx, readelf, strip):
        if not item.is_file():
            raise FileNotFoundError(item)
    egl_loader = upstream / "ndkLibs/libs/release/arm64-v8a/libEGLLoader.a"
    rcheevos = upstream / "ndkLibs/libs/release/arm64-v8a/librcheevos.a"
    for item in (egl_loader, rcheevos):
        if not item.is_file():
            raise FileNotFoundError(item)
    if cpp_runtime.name != "libn64cpp.so":
        raise ValueError("Expected the APK's libn64cpp.so runtime")
    if original_bridge.name != "libae-bridge.so":
        raise ValueError("Expected the APK's original libae-bridge.so")
    if sha256(original_bridge) != ORIGINAL_BRIDGE_SHA256:
        raise ValueError("Original AE bridge differs from R161")
    if sha256(cpp_runtime) != CPP_RUNTIME_SHA256:
        raise ValueError("C++ runtime differs from R161")

    output.mkdir(parents=True, exist_ok=True)
    patched = output / "ae_bridge_station.cpp"
    patched.write_bytes(data.replace(original_override, station_override))
    api = upstream / "mupen64plus-core/upstream/src/api"
    include_dirs = [
        upstream / "ae-bridge/src", api, upstream / "ndkLibs/GL",
        upstream / "ndkLibs/rcheevos/include", upstream / "ndkLibs/rcheevos/src",
    ]
    includes = [arg for path in include_dirs for arg in ("-I", str(path))]
    flags = [
        "--target=aarch64-linux-android23", "-fPIC", "-Oz", "-fcommon",
        "-ffast-math", "-ftree-vectorize", "-fno-omit-frame-pointer",
        "-fvisibility=hidden", "-Wno-error=implicit-function-declaration",
        "-DEGL", "-DRC_DISABLE_LUA", "-DRC_CLIENT_SUPPORTS_HASH",
        "-DNDEBUG",
    ]
    cpp_object = output / "ae_bridge_station.o"
    c_object = output / "ae_ra_internal.o"
    run([str(clangxx), *flags, "-fvisibility-inlines-hidden", "-std=c++11", "-g",
         *includes, "-c", str(patched), "-o", str(cpp_object)])
    run([str(clang), *flags, *includes, "-c",
         str(upstream / "ae-bridge/src/ae_ra_internal.c"), "-o", str(c_object)])
    unstripped = output / (SONAME + ".unstripped")
    run([
        str(clangxx), "--target=aarch64-linux-android23", "-shared", "-nostdlib++",
        str(cpp_object), str(c_object), str(egl_loader), str(rcheevos),
        "-L", str(cpp_runtime.parent), "-ln64cpp", "-llog", "-lEGL",
        "-landroid", "-ldl", "-lm", "-Wl,--no-undefined",
        "-Wl,-z,max-page-size=16384", "-Wl,-z,common-page-size=16384",
        "-Wl,-z,relro", "-Wl,-z,now", f"-Wl,-soname,{SONAME}",
        "-o", str(unstripped),
    ])
    final = output / SONAME
    run([str(strip), "--strip-unneeded", str(unstripped), "-o", str(final)])
    inspection = run([str(readelf), "-h", "-l", "-d", "--dyn-syms", "--wide", str(final)])
    original = run([str(readelf), "-d", "--dyn-syms", "--wide", str(original_bridge)])
    if "AArch64" not in inspection or f"Library soname: [{SONAME}]" not in inspection:
        raise RuntimeError("Wrong ABI or SONAME")
    loads = [line for line in inspection.splitlines() if re.match(r"\s*LOAD\s", line)]
    if not loads or any(int(line.split()[-1], 16) < 16384 for line in loads):
        raise RuntimeError("ELF LOAD alignment below 16 KiB")
    needed = set(re.findall(r"Shared library: \[([^]]+)\]", inspection))
    original_needed = set(re.findall(r"Shared library: \[([^]]+)\]", original))
    if needed != EXPECTED_NEEDED or needed != original_needed:
        raise RuntimeError(f"Native dependencies differ: {needed} vs {original_needed}")
    exports = ("JNI_OnLoad", "overrideAeVidExtFuncs", "stationVideoOverrideReady", "setNativeWindow",
               "unsetNativeWindow", "emuDestroySurface", "loadLibrary")
    for symbol in exports:
        if not re.search(r"\bGLOBAL\s+DEFAULT\s+(?!UND)\S+\s+" + symbol + r"\b", inspection):
            raise RuntimeError(f"Missing exported function: {symbol}")
    def defined_globals(table: str) -> set[str]:
        names: set[str] = set()
        for line in table.splitlines():
            fields = line.split()
            if (len(fields) >= 8 and fields[4] == "GLOBAL"
                    and fields[5] == "DEFAULT" and fields[6] != "UND"):
                names.add(fields[7])
        return names
    original_exports = defined_globals(original)
    station_exports = defined_globals(inspection)
    if station_exports - original_exports != {"stationVideoOverrideReady"}:
        raise RuntimeError("Unexpected Station bridge exports")
    if original_exports - station_exports:
        raise RuntimeError("Station bridge lost original ABI exports")
    if final.read_bytes().count(STATION_CORE) != 1 or OFFLINE_CORE in final.read_bytes():
        raise RuntimeError("Bridge core selection was not isolated")
    receipt = {
        "schema": "station-ae-bridge-build-v1", "upstreamCommit": UPSTREAM_COMMIT,
        "soname": SONAME, "abi": "arm64-v8a", "androidApi": 23,
        "sha256": sha256(final), "bytes": final.stat().st_size,
        "originalBridgeSha256": sha256(original_bridge),
        "cppRuntimeSha256": sha256(cpp_runtime),
        "sourceSha256": sha256(source), "patchedSourceSha256": sha256(patched),
        "eglLoaderSha256": sha256(egl_loader), "rcheevosSha256": sha256(rcheevos),
        "loadAlignment": 16384, "needed": sorted(needed), "exportsChecked": list(exports),
        "offlineSourceUnchanged": source.read_bytes() == data,
        "offlineBridgeUnchanged": True, "physicalGameplayValidated": False,
        "originalExportCount": len(original_exports),
        "stationExportCount": len(station_exports),
    }
    (output / "build-station-ae-bridge.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--ndk", type=Path, required=True)
    parser.add_argument("--original-bridge", type=Path, required=True)
    parser.add_argument("--cpp-runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.upstream, args.ndk, args.original_bridge,
                   args.cpp_runtime, args.output)
    print(json.dumps({key: result[key] for key in
                      ("soname", "sha256", "bytes", "loadAlignment", "needed")}))


if __name__ == "__main__":
    main()
