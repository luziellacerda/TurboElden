"""Pin the real Mupen AE backend and build its independent runtime identity.

The marker is an identity library, not a substitute emulator or a fake ready
signal. Its fingerprint binds the complete core, native patch, Java/smali hooks,
final DEX/manifest payloads, Mupen plugins and exact deterministic options.
Only the N64 engine entry is replaced. Offline libraries and other engines stay
unchanged. A freeze manifest must be created after the integration is final.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import zipfile

VERSION = Path(__file__).resolve().parents[1]
BASE_SHA256 = "aeeb2f8167a442db5a58b990cf6d45b613fab42b1e7a9bbc0bf3214b260420c4"
OLD_ENGINE = "parallel-3be1f437-n64-v3-81b3daa38fb9"
CORE_NAME = "libstation_mupen64plus_core.so"
RUNTIME_NAME = "libstation_mupen64plus_runtime.so"
ALLOWED = Path(r"G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\r125-native-artifacts")
PREFIX = "lib/arm64-v8a/"
SEEDS = (
    "libae-bridge.so", "libjnidispatch.so", "libmupen64plus-input-android.so",
    "libmupen64plus-audio-android.so", "libmupen64plus-audio-android-fp.so",
    "libmupen64plus-video-glide64mk2.so", "libmupen64plus-rsp-hle.so",
    "libn64cpp.so", "libSDL2_net.so",
)
ANDROID_SYSTEM = frozenset((
    "libandroid.so", "libc.so", "libdl.so", "libEGL.so", "libGLESv2.so",
    "liblog.so", "libm.so", "libz.so", "libOpenSLES.so",
))
PAYLOAD_NAMES = frozenset(("classes35.dex", "classes36.dex", "AndroidManifest.xml"))

def fs(path: Path) -> Path:
    """Use native long paths for this Windows workspace, without changing IDs."""
    if os.name != "nt":
        return path
    value = str(path.absolute())
    if value.startswith("\\\\?\\"):
        return Path(value)
    if value.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + value[2:])
    return Path("\\\\?\\" + value)

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def sha(path: Path) -> str:
    result = hashlib.sha256()
    with fs(path).open("rb") as stream:
        for raw in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(raw)
    return result.hexdigest()

def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

def checked_output(path: Path, *, empty: bool = False) -> Path:
    path, allowed = path.resolve(), ALLOWED.resolve()
    if path != allowed and allowed not in path.parents:
        raise ValueError("Output must stay within the approved R125 native artifacts directory")
    if empty and path.exists() and any(path.iterdir()):
        raise ValueError("Use an empty output directory; a runtime identity may not mix builds")
    return path

def elf_metadata(raw: bytes) -> dict:
    if raw[:6] != b"\x7fELF\x02\x01":
        raise ValueError("Expected ELF64 little-endian library")
    machine = struct.unpack_from("<H", raw, 18)[0]
    if machine != 183:
        raise ValueError("Expected AArch64 ELF")
    shoff = struct.unpack_from("<Q", raw, 40)[0]
    shentsize, shnum = struct.unpack_from("<HH", raw, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", raw, shoff + i * shentsize) for i in range(shnum)]
    needed, soname = [], None
    for section in sections:
        if section[1] != 6:
            continue
        strings_section = sections[section[6]]
        strings = raw[strings_section[4]:strings_section[4] + strings_section[5]]
        if section[9] != 16:
            raise ValueError("Unexpected ELF dynamic entry size")
        for offset in range(section[4], section[4] + section[5], section[9]):
            tag, value = struct.unpack_from("<qQ", raw, offset)
            if tag not in (1, 14):
                continue
            name = strings[value:strings.index(0, value)].decode("ascii")
            if tag == 1:
                needed.append(name)
            else:
                soname = name
    phoff = struct.unpack_from("<Q", raw, 32)[0]
    phentsize, phnum = struct.unpack_from("<HH", raw, 54)
    alignments = []
    for i in range(phnum):
        program = struct.unpack_from("<IIQQQQQQ", raw, phoff + i * phentsize)
        if program[0] == 1:
            alignments.append(program[-1])
    return {"machine": "AArch64", "soname": soname, "needed": needed, "loadAlignments": alignments}

def dependencies(archive: zipfile.ZipFile, core: bytes) -> dict:
    available = {info.filename[len(PREFIX):]: info for info in archive.infolist() if info.filename.startswith(PREFIX)}
    found: dict[str, dict] = {}
    queue = list(SEEDS) + elf_metadata(core)["needed"]
    while queue:
        name = queue.pop(0)
        if name in found or name in ANDROID_SYSTEM:
            continue
        if not re.fullmatch(r"lib[A-Za-z0-9_+.-]+\.so", name):
            raise ValueError(f"Invalid dependency name: {name}")
        if name not in available:
            raise FileNotFoundError(f"Required non-system dependency absent from base APK: {name}")
        raw = archive.read(PREFIX + name)
        metadata = elf_metadata(raw)
        if metadata["soname"] not in (name, None):
            raise ValueError(f"Dependency SONAME differs from filename: {name}")
        found[name] = {"sha256": digest(raw), "bytes": len(raw), **metadata}
        queue.extend(metadata["needed"])
    if "libmupen64plus-core.so" in found or "libstation_online_n64.so" in found:
        raise ValueError("Station N64 must not depend on an offline or legacy libretro core")
    return dict(sorted(found.items()))

def literals() -> tuple[str, str]:
    source = fs(VERSION / "java/org/emulationstation/frontend/netplay/StationN64Launch.java").read_text(encoding="utf-8")
    result = []
    for field in ("BACKEND", "OPTIONS"):
        values = re.findall(r"static\s+final\s+String\s+" + field + r'\s*=\s*("(?:[^"\\]|\\.)*")\s*;', source)
        if len(values) != 1:
            raise ValueError(f"Cannot read exact StationN64Launch.{field}")
        result.append(json.loads(values[0]))
    backend, options = result
    if backend != "mupen64plus-ae-station-v1" or not options.startswith("backend=" + backend + "\nwire=SN64/1\n"):
        raise ValueError("Unsupported N64 backend/wire; update this recipe deliberately")
    return backend, options

def source_files() -> dict[str, str]:
    version_fs = fs(VERSION)
    files = list((version_fs / "java").rglob("*.java"))
    files += [version_fs / relative for relative in (
        "native/n64-station-recovery.c", "native/n64-station-recovery.h",
        "native/apply_native_patch.py", "recipes/build_native.py",
        "recipes/patch_mupen_smali.py", "docs/mupen-smali-hooks.json",
        "recipes/build_runtime_identity.py",
    )]
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(path)
    return {path.relative_to(version_fs).as_posix(): sha(path) for path in sorted(set(files))}

def payload_mapping(values: list[str]) -> dict[str, Path]:
    result = {}
    for value in values:
        name, separator, path = value.partition("=")
        if not separator or name not in PAYLOAD_NAMES or name in result:
            raise ValueError("Each final payload must be NAME=PATH, with no duplicate or unknown name")
        result[name] = Path(path).resolve()
    if set(result) != PAYLOAD_NAMES:
        raise ValueError("Freeze requires final classes35.dex, classes36.dex and AndroidManifest.xml")
    return result

def validate_core_build(core_path: Path, upstream: Path) -> dict:
    receipt = json.loads(fs(core_path.parent / "build-native.json").read_text(encoding="utf-8"))
    if receipt.get("sha256") != sha(core_path) or receipt.get("compiledSourceCount") != 79 or receipt.get("reusedObjectCount") != 0:
        raise ValueError("Full native build receipt does not match the core")
    spec = importlib.util.spec_from_file_location("identity_native_patch", fs(VERSION / "native/apply_native_patch.py"))
    patch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patch)
    expected = patch.generate(upstream)
    hashes = {name.replace("\\", "/"): value for name, value in receipt["inputHeadersAndSources"].items()}
    overlay_hashes = {}
    for name, raw in expected.items():
        if name in ("station-native.patch", "station-native-manifest.json"):
            continue
        if name.endswith("mupen64plus-core.mk"):
            raw = raw.decode("utf-8").replace("LOCAL_MODULE := mupen64plus-core", "LOCAL_MODULE := station_mupen64plus_core").encode("utf-8")
        expected_hash = digest(raw)
        if hashes.get(name) != expected_hash or sha(core_path.parent / "source" / name) != expected_hash:
            raise ValueError("Core was not compiled from the current native overlay: " + name)
        overlay_hashes[name] = expected_hash
    return {"compiledSourceCount": 79, "reusedObjectCount": 0, "overlaySha256": overlay_hashes,
            "staticDependencySha256": receipt["dependencies"]}

def freeze(base: Path, core_path: Path, upstream: Path, payloads: dict[str, Path], out: Path) -> dict:
    if sha(base) != BASE_SHA256:
        raise ValueError("Base APK is not exact R124")
    core = fs(core_path).read_bytes()
    metadata = elf_metadata(core)
    if metadata["soname"] != CORE_NAME or not metadata["loadAlignments"] or min(metadata["loadAlignments"]) < 16384:
        raise ValueError("Complete Station core must have its own SONAME and 16 KiB LOAD alignment")
    backend, options = literals()
    native_build = validate_core_build(core_path, upstream)
    with zipfile.ZipFile(base) as archive:
        original_engines = json.loads(archive.read("assets/station-online/engines.json"))
        candidates = [e for e in original_engines["engines"] if e.get("platform") == "n64"]
        if len(candidates) != 1 or candidates[0]["engineId"] != OLD_ENGINE:
            raise ValueError("Base N64 engine does not match the audited R124 entry")
        deps = dependencies(archive, core)
    value = {
        "schemaVersion": 1, "baseApkSha256": BASE_SHA256,
        "core": {"path": str(core_path.resolve()), "sha256": digest(core), "bytes": len(core)},
        "sources": source_files(), "nativeBuild": native_build, "upstreamPath": str(upstream.resolve()),
        "payloads": {name: {"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size} for name, path in sorted(payloads.items())},
        "backend": backend, "options": options, "dependencies": deps,
        "sourceFrozen": True, "androidPeerGameplayValidated": False,
    }
    checked_output(out.parent).mkdir(parents=True, exist_ok=True)
    fs(out).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return value

def fingerprint(frozen: dict) -> dict:
    return {
        "schemaVersion": 1, "backend": frozen["backend"], "wire": "SN64/1",
        "recoveryProtocol": "station-stream.v3", "maximumPlayers": 4,
        "controllerProfiles": ["direct-four-ports-v1"], "rollback": False,
        "baseApkSha256": frozen["baseApkSha256"], "coreSha256": frozen["core"]["sha256"],
        "sources": frozen["sources"], "nativeBuild": frozen["nativeBuild"],
        "payloadSha256": {name: info["sha256"] for name, info in frozen["payloads"].items()},
        "dependencySha256": {name: info["sha256"] for name, info in frozen["dependencies"].items()},
        "options": frozen["options"],
    }

def engine_manifest(original: dict, identity: dict, core_hash: str, runtime_hash: str) -> tuple[dict, dict]:
    result = copy.deepcopy(original)
    matches = [i for i, engine in enumerate(result["engines"]) if engine.get("platform") == "n64"]
    if len(matches) != 1 or result["engines"][matches[0]]["engineId"] != OLD_ENGINE:
        raise ValueError("Exactly the audited N64 entry must be replaced, not appended after a live legacy entry")
    old = result["engines"][matches[0]]
    engine = {
        "engineId": "mupen64plus-ae-33bf7021-n64-v3-" + runtime_hash[:12],
        "platform": "n64", "backend": identity["backend"],
        "library": CORE_NAME, "runtimeLibrary": RUNTIME_NAME,
        "coreSha256": core_hash, "runtimeSha256": runtime_hash,
        "dependencySha256": identity["dependencySha256"],
        "extensions": old["extensions"], "overlay": "", "options": identity["options"],
        "launchReady": True, "license": "GPL-2.0-or-later",
        "sourceDirectory": "mupen64plus-ae-33bf7021549d7873e976884370fbd1a8e7333bc7",
        "recoveryProtocol": "station-stream.v3", "maximumPlayers": 4,
        "controllerProfiles": ["direct-four-ports-v1"],
        "status": "implemented-candidate-peer-gameplay-pending",
        "contentIdentityByExtension": {"default": "launch-file-v1"},
    }
    result["engines"][matches[0]] = engine
    for i, other in enumerate(original["engines"]):
        if i != matches[0] and other != result["engines"][i]:
            raise AssertionError("An unrelated engine was changed")
    if len(result["engines"]) != len(original["engines"]):
        raise AssertionError("Engine count changed")
    if any(e["engineId"] == OLD_ENGINE for e in result["engines"]):
        raise AssertionError("Legacy engine identity remains selectable")
    return result, engine

def build(base: Path, freeze_path: Path, ndk: Path, out: Path) -> dict:
    out = checked_output(out, empty=True)
    frozen = json.loads(fs(freeze_path).read_text(encoding="utf-8"))
    if frozen.get("schemaVersion") != 1 or frozen.get("sourceFrozen") is not True:
        raise ValueError("A final frozen source manifest is required")
    if frozen["baseApkSha256"] != BASE_SHA256 or sha(base) != BASE_SHA256:
        raise ValueError("Base APK differs from frozen R124")
    if source_files() != frozen["sources"] or literals() != (frozen["backend"], frozen["options"]):
        raise ValueError("R125 source/options changed after freeze; do not emit a stale identity")
    if set(frozen["payloads"]) != PAYLOAD_NAMES:
        raise ValueError("Frozen payload set differs")
    for info in frozen["payloads"].values():
        if sha(Path(info["path"])) != info["sha256"]:
            raise ValueError("A final DEX/manifest payload changed after freeze")
    core_path = Path(frozen["core"]["path"])
    core = fs(core_path).read_bytes()
    if digest(core) != frozen["core"]["sha256"]:
        raise ValueError("Core changed after freeze")
    if validate_core_build(core_path, Path(frozen["upstreamPath"])) != frozen["nativeBuild"]:
        raise ValueError("Native build proof changed after freeze")
    with zipfile.ZipFile(base) as archive:
        original = json.loads(archive.read("assets/station-online/engines.json"))
        if dependencies(archive, core) != frozen["dependencies"]:
            raise ValueError("Base dependencies changed after freeze")
    identity = fingerprint(frozen)
    identity_bytes = canonical(identity)
    identity_hash = digest(identity_bytes)
    out.mkdir(parents=True, exist_ok=True)
    source = out / "station-mupen-runtime.c"
    # C JSON string escaping also works for this ASCII canonical JSON payload.
    source.write_text('#include <stddef.h>\n'
        '__attribute__((visibility("default"))) const char *StationMupenRuntimeIdentity(void) { return "' + identity_hash + '"; }\n'
        '__attribute__((visibility("default"))) const char *StationMupenRuntimeManifest(void) { return ' + json.dumps(identity_bytes.decode("ascii")) + '; }\n', encoding="ascii")
    tool = ndk / "toolchains/llvm/prebuilt/windows-x86_64/bin"
    library = out / RUNTIME_NAME
    command = [str(tool / "clang.exe"), "--target=aarch64-linux-android23", "-std=c11", "-Oz", "-fPIC", "-fvisibility=hidden",
        "-Wall", "-Wextra", "-Werror", "-shared", str(source), "-o", str(library),
        "-Wl,--no-undefined", "-Wl,--build-id=sha1", "-Wl,-soname," + RUNTIME_NAME,
        "-Wl,-z,max-page-size=16384", "-Wl,-z,common-page-size=16384"]
    compiler = subprocess.run(command, capture_output=True, text=True)
    (out / "compile.log").write_text(compiler.stdout + compiler.stderr, encoding="utf-8")
    if compiler.returncode:
        raise RuntimeError("Runtime marker compile failed; see compile.log")
    subprocess.run([str(tool / "llvm-strip.exe"), "--strip-unneeded", str(library)], check=True)
    elf = elf_metadata(library.read_bytes())
    if elf["soname"] != RUNTIME_NAME or min(elf["loadAlignments"]) < 16384:
        raise ValueError("Runtime ELF SONAME/alignment differs")
    symbols = subprocess.run([str(tool / "llvm-readelf.exe"), "--dyn-syms", str(library)], capture_output=True, text=True, check=True).stdout
    for name in ("StationMupenRuntimeIdentity", "StationMupenRuntimeManifest"):
        if not re.search(r"GLOBAL\s+DEFAULT\s+(?!UND)\S+\s+" + name + r"\s*$", symbols, re.MULTILINE):
            raise ValueError("Runtime API symbol missing: " + name)
    runtime_hash = sha(library)
    manifests, engine = engine_manifest(original, identity, digest(core), runtime_hash)
    engines_bytes = (json.dumps(manifests, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if len(engines_bytes) > 32768:
        raise ValueError("Engine manifest exceeds the authenticated app reader limit")
    (out / "engines.json").write_bytes(engines_bytes)
    (out / CORE_NAME).write_bytes(core)
    (out / "runtime-fingerprint.json").write_bytes(identity_bytes + b"\n")
    profile = {"schemaVersion": 1, "controllerProfile": "direct-four-ports-v1", "devices": [1, 1, 1, 1], "coreOptions": identity["options"]}
    # This order, including coreOptions last, exactly matches StationMultiplayerProfile.
    profile_bytes = json.dumps(profile, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    (out / "multiplayer-profile.json").write_bytes(profile_bytes + b"\n")
    receipt = {
        "schemaVersion": 1, "baseApkSha256": BASE_SHA256, "backend": identity["backend"],
        "fingerprintSha256": identity_hash, "runtimeLibrary": RUNTIME_NAME,
        "runtimeSha256": runtime_hash, "runtimeBytes": library.stat().st_size,
        "coreLibrary": CORE_NAME, "coreSha256": digest(core), "coreBytes": len(core),
        "engine": engine, "enginesAssetSha256": digest(engines_bytes),
        "profileSha256": digest(profile_bytes), "profileCanonical": profile_bytes.decode("utf-8"),
        "elf": elf, "compileCommand": command,
        "preservedUnrelatedEngineCount": len(original["engines"]) - 1,
        "legacyEngineReused": False, "offlineLibrariesChanged": False,
        "androidPeerGameplayValidated": False, "serverRegistrationConfirmed": False,
    }
    (out / "runtime-identity.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    a = sub.add_parser("freeze")
    a.add_argument("--base", type=Path, required=True)
    a.add_argument("--core", type=Path, required=True)
    a.add_argument("--upstream", type=Path, required=True)
    a.add_argument("--payload", action="append", required=True)
    a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("build")
    b.add_argument("--base", type=Path, required=True)
    b.add_argument("--freeze", type=Path, required=True)
    b.add_argument("--ndk", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "freeze":
        result = freeze(args.base, args.core, args.upstream, payload_mapping(args.payload), args.out)
        print(json.dumps({"sourceCount": len(result["sources"]), "dependencyCount": len(result["dependencies"]), "frozen": True}))
    else:
        result = build(args.base, args.freeze, args.ndk, args.out)
        print(json.dumps({key: result[key] for key in ("runtimeSha256", "coreSha256", "fingerprintSha256", "profileSha256")}))

if __name__ == "__main__":
    main()
