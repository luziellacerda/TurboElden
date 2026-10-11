"""Freeze actual R126 payloads and build Dolphin/N64 runtime identity markers.

Markers identify a compiled backend; they implement no emulator or readiness.
Only productive sources, source pins, actual dependency/core bytes and final
DEX/AXML enter the canonical fingerprint. Documents, tests, local output paths,
receipt files and this identity recipe are not fingerprint inputs.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import zipfile

HERE = Path(__file__).resolve().parents[1]
R125 = HERE.parent / "station-mupen-online-r125-20261011"
R124 = HERE.parent / "station-video-room-footer-r124-20261011"
ALLOWED = Path(r"G:\StationDolphinR126")
BASE_SHA = "a3ed815c01fdb0bd06a3a2485991fe8d19a51c63fee0e9255a45ecd8a9b6d4a5"
N64_CORE_SHA = "fe6e810a1c7fc50a494b50b1dccf581b84385667191c0cbcd235d585a0703dd8"
N64_OLD_ID = "mupen64plus-ae-33bf7021-n64-v3-500d48cd10f3"
DEX36_SHA = "6e0f7116d156518fad1e65e72f4c204cfacfd9904c4ee2c3110395d56842d707"
PIN = "5102a0339c2177575378107b76541e47cc52122d"
PAYLOADS = frozenset(("classes10.dex", "classes12.dex", "classes35.dex", "AndroidManifest.xml"))
DOLPHIN_NAMES = (
    "libstation_dolphin_online.so", "libstation_dolphin_hook.so",
    "libstation_dolphin_hook_impl.so", "libstation_dolphin_file_redirect_hook.so",
    "libstation_dolphin_gsl_alloc_hook.so",
)
N64_CORE = "libstation_mupen64plus_core.so"
N64_MARKER = "libstation_mupen64plus_runtime.so"
DOLPHIN_MARKER = "libstation_dolphin_runtime.so"
PREFIX = "lib/arm64-v8a/"
PROFILES = {"n64": "direct-four-ports-v1", "gamecube": "dolphin-gamecube-four-ports-v1",
            "wii": "dolphin-wii-remotes-four-v1"}

def fs(path):
    path = Path(path).absolute()
    if os.name != "nt": return path
    value = str(path)
    if value.startswith("\\\\?\\"): return path
    return Path("\\\\?\\UNC\\" + value[2:] if value.startswith("\\\\") else "\\\\?\\" + value)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def sha(path):
    result = hashlib.sha256()
    with fs(path).open("rb") as stream:
        for raw in iter(lambda: stream.read(1048576), b""): result.update(raw)
    return result.hexdigest()

def read_json(path): return json.loads(fs(path).read_text(encoding="utf-8"))
def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
def write_json(path, value): fs(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def checked_output(path, empty=False):
    path = Path(path).resolve()
    if ALLOWED.resolve() not in path.parents:
        raise ValueError("Output must be an isolated child of G:\\StationDolphinR126")
    if empty and fs(path).exists() and any(fs(path).iterdir()):
        raise ValueError("Do not mix identity builds; use an empty output directory")
    return path

def old_recipe():
    spec = importlib.util.spec_from_file_location("r125_identity_primitives", fs(R125 / "recipes/build_runtime_identity.py"))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def literals(source):
    text = fs(source).read_text(encoding="utf-8")
    values = []
    for field in ("BACKEND", "OPTIONS"):
        matches = re.findall(r"static\s+final\s+String\s+" + field + r'\s*=\s*("(?:[^"\\]|\\.)*")\s*;', text)
        if len(matches) != 1: raise ValueError("Missing exact launch literal: " + field)
        values.append(json.loads(matches[0]))
    return tuple(values)

def productive_sources():
    """Exactly mirror the final Java compilation overlay, using long paths."""
    manifest = read_json(R124 / "JAVA-SOURCE-MANIFEST.json")
    effective = {}
    for name, expected in manifest.items():
        path = R124 / "java" / name
        if sha(path) != expected: raise ValueError("R124 productive source changed: " + name)
        if name.startswith(("netplay-src/", "dependency-src/")): effective[name] = path
    for revision in (R125, HERE):
        root = fs(revision / "java")
        for path in root.rglob("*.java"):
            effective["netplay-src/" + path.relative_to(root).as_posix()] = path
    java = {name: sha(path) for name, path in sorted(effective.items())}
    other = {}
    for revision, relatives in ((R125, (
        "native/n64-station-recovery.c", "native/n64-station-recovery.h", "native/apply_native_patch.py",
        "recipes/patch_mupen_smali.py",
    )), (HERE, (
        "recipe/generate_source.py", "recipe/prepare_hooks.py", "recipe/patch_dolphin_smali.py",
        "recipe/patch_manifest.py", "recipe/dependencies.lock.json",
        "patches/dolphin-station-r126.patch", "patches/adrenotools-station-r126.patch",
    ))):
        for name in relatives:
            path = revision / name
            other[revision.name + "/" + name] = sha(path)
    native_root = fs(HERE / "native")
    for path in sorted(native_root.rglob("*")):
        if path.is_file() and path.suffix in (".cpp", ".h"):
            other[HERE.name + "/native/" + path.relative_to(native_root).as_posix()] = sha(path)
    return java, dict(sorted(other.items()))

def payload_mapping(values):
    result = {}
    for raw in values:
        name, separator, path = raw.partition("=")
        if not separator or name not in PAYLOADS or name in result: raise ValueError("Invalid/duplicate final payload")
        result[name] = Path(path).resolve()
    if set(result) != PAYLOADS: raise ValueError("Require final DEX10/12/35 and AndroidManifest.xml")
    return result

def validate_n64(base, frozen_path):
    old = old_recipe(); frozen = read_json(frozen_path)
    if frozen.get("sourceFrozen") is not True or frozen.get("schemaVersion") != 1:
        raise ValueError("Need real R125 final freeze receipt")
    core = Path(frozen["core"]["path"]); raw = fs(core).read_bytes()
    if sha(core) != N64_CORE_SHA or frozen["core"]["sha256"] != N64_CORE_SHA:
        raise ValueError("N64 core must remain final full-5, never an intermediate")
    build = old.validate_core_build(core, Path(frozen["upstreamPath"]))
    if build != frozen["nativeBuild"]: raise ValueError("N64 source/build receipt changed")
    with zipfile.ZipFile(base) as archive:
        if digest(archive.read(PREFIX + N64_CORE)) != N64_CORE_SHA: raise ValueError("Base N64 core differs")
        if digest(archive.read("classes36.dex")) != DEX36_SHA: raise ValueError("N64 hooks DEX36 must remain unchanged")
        deps = old.dependencies(archive, raw)
    if deps != frozen["dependencies"]: raise ValueError("Normal AE plugins/dependencies changed after R125")
    backend, options = literals(R125 / "java/org/emulationstation/frontend/netplay/StationN64Launch.java")
    if (backend, options) != (frozen["backend"], frozen["options"]): raise ValueError("N64 exact options changed")
    return {"corePath": str(core.resolve()), "coreSha256": N64_CORE_SHA, "coreBytes": len(raw),
            "backend": backend, "options": options, "nativeBuild": build, "dependencies": deps,
            "r125FreezePath": str(Path(frozen_path).resolve()), "upstreamPath": frozen["upstreamPath"]}

def validate_dolphin(base, directory, stage):
    old = old_recipe(); directory = Path(directory).resolve(); stage = Path(stage).resolve()
    receipt = read_json(directory / "native-receipt.json")
    source = read_json(stage / "station-r126-source-receipt.json")
    hooks = read_json(stage / "station-r126-hook-receipt.json")
    deps = read_json(stage / "station-r126-dependency-receipt.json")
    if receipt.get("compiled") is not True or receipt.get("upstream") != PIN or receipt.get("androidApi") != 24 or receipt.get("abi") != "arm64-v8a":
        raise ValueError("Need actual compiled pinned Dolphin API24/ARM64 receipt")
    if len(receipt.get("jniExports", [])) != 21 or receipt.get("allLoadSegments16KiB") is not True:
        raise ValueError("Dolphin native API/alignment proof differs")
    if source["upstream"] != PIN or not deps.get("complete") or source["patchSha256"] != receipt["sourcePatchSha256"] or hooks["patchSha256"] != receipt["hookPatchSha256"]:
        raise ValueError("Native source/dependency stage differs from compiled receipt")
    if sha(HERE / "patches/dolphin-station-r126.patch") != receipt["sourcePatchSha256"] or sha(HERE / "patches/adrenotools-station-r126.patch") != receipt["hookPatchSha256"]:
        raise ValueError("Native productive patch changed after compilation")
    for record in source["patchedFiles"] + hooks["files"]:
        if sha(stage / record["path"]) != record["patchedSha256"]: raise ValueError("Native stage source changed")
    for record in source["addedFiles"]:
        if sha(stage / record["path"]) != record["sha256"]: raise ValueError("Native addition changed")
    current_native = {path.name: sha(path) for path in fs(HERE / "native").iterdir() if path.suffix in (".cpp", ".h")}
    for record in source["addedFiles"]:
        if Path(record["path"]).name in current_native and current_native[Path(record["path"]).name] != record["sha256"]:
            raise ValueError("Compiled native addition no longer matches productive source")
    records = {record["name"]: record for record in receipt["libraries"]}
    if set(records) != set(DOLPHIN_NAMES): raise ValueError("Require all five unique online libraries")
    libraries = {}
    for name in DOLPHIN_NAMES:
        path = directory / name; raw = fs(path).read_bytes(); elf = old.elf_metadata(raw)
        if digest(raw) != records[name]["sha256"] or len(raw) != records[name]["bytes"]:
            raise ValueError("Final compiled native bytes changed: " + name)
        if elf["soname"] != name or not elf["loadAlignments"] or min(elf["loadAlignments"]) < 16384:
            raise ValueError("Bad native SONAME/alignment: " + name)
        libraries[name] = {"path": str(path), "sha256": digest(raw), "bytes": len(raw), **elf}
    bundle = digest("".join(name + " " + libraries[name]["sha256"] + "\n" for name in DOLPHIN_NAMES).encode())
    if bundle != receipt["nativeBundleSha256"]: raise ValueError("Native library bundle differs")
    # Include manually loaded hooks and each non-system DT_NEEDED dependency.
    required = {}; queue = list(DOLPHIN_NAMES[1:]) + libraries[DOLPHIN_NAMES[0]]["needed"]
    with zipfile.ZipFile(base) as archive:
        while queue:
            name = queue.pop(0)
            if name in required or name in old.ANDROID_SYSTEM: continue
            if not re.fullmatch(r"lib[A-Za-z0-9_+.-]+\.so", name): raise ValueError("Bad native dependency name")
            if name in libraries:
                record = libraries[name]
            else:
                raw = archive.read(PREFIX + name); elf = old.elf_metadata(raw)
                record = {"sha256": digest(raw), "bytes": len(raw), **elf}
            if name in ("libdolp.so", "libmain.so", "libmain_hook.so", "libhook_impl.so", "libc++_shared.so"):
                raise ValueError("Online Dolphin depends on an old/global offline library")
            required[name] = {key: value for key, value in record.items() if key != "path"}
            queue.extend(record["needed"])
    backend, options = literals(HERE / "java/org/emulationstation/frontend/netplay/StationDolphinLaunch.java")
    if backend != "dolphin-station-v1" or not options.startswith("backend=" + backend + "\nwire=DPL1\n"):
        raise ValueError("Wrong Dolphin backend/wire")
    proofs = {"upstream": PIN, "sourcePatchSha256": source["patchSha256"], "hookPatchSha256": hooks["patchSha256"],
              "addedSourceSha256": {record["path"]: record["sha256"] for record in source["addedFiles"]},
              "patchedSourceSha256": {record["path"]: record["patchedSha256"] for record in source["patchedFiles"] + hooks["files"]},
              "dependencyPins": deps["archives"], "jniExports": receipt["jniExports"], "androidApi": 24,
              "nativeBundleSha256": bundle}
    return {"directory": str(directory), "stage": str(stage), "backend": backend, "options": options,
            "libraries": libraries, "dependencies": dict(sorted(required.items())), "nativeBuild": proofs}

def freeze(base, n64_frozen, dolphin, stage, java_receipt, payloads, out):
    if sha(base) != BASE_SHA: raise ValueError("Require exact signed R125 base APK")
    java, transforms = productive_sources(); compiled = read_json(java_receipt)
    if compiled.get("sourceCount") != 198 or compiled["sources"] != java or compiled["classes35SHA256"] != sha(payloads["classes35.dex"]):
        raise ValueError("Fresh Java compiler receipt must prove the exact effective 198 productive sources")
    n64 = validate_n64(base, n64_frozen); dpl = validate_dolphin(base, dolphin, stage)
    with zipfile.ZipFile(base) as archive:
        original = json.loads(archive.read("assets/station-online/engines.json"))
    n64_entries = [engine for engine in original["engines"] if engine.get("platform") == "n64"]
    if len(n64_entries) != 1 or n64_entries[0]["engineId"] != N64_OLD_ID:
        raise ValueError("Exactly R125 live N64 entry required")
    if any(engine.get("platform") in ("gamecube", "wii") for engine in original["engines"]):
        raise ValueError("Do not append a native backend behind another live Dolphin entry")
    value = {"schemaVersion": 2, "baseApkSha256": BASE_SHA, "basePath": str(base.resolve()),
             "javaSources": java, "productiveTransforms": transforms,
             "payloads": {name: {"path": str(path), "sha256": sha(path), "bytes": fs(path).stat().st_size} for name, path in sorted(payloads.items())},
             "preservedClasses36Sha256": DEX36_SHA, "n64": n64, "dolphin": dpl,
             "sourceFrozen": True, "physicalGameplayValidated": False, "serverRegistrationConfirmed": False}
    checked_output(out.parent); fs(out.parent).mkdir(parents=True, exist_ok=True); write_json(out, value)
    return value

def fingerprint(frozen, kind):
    value = frozen[kind]; options = value["options"]
    profiles = [PROFILES["n64"]] if kind == "n64" else [PROFILES["gamecube"], PROFILES["wii"]]
    core_hash = value["coreSha256"] if kind == "n64" else value["libraries"][DOLPHIN_NAMES[0]]["sha256"]
    return {"schemaVersion": 2, "backend": value["backend"], "wire": "SN64/1" if kind == "n64" else "DPL1",
            "recoveryProtocol": "station-stream.v3", "maximumPlayers": 4, "controllerProfiles": profiles,
            "rollback": False, "baseApkSha256": frozen["baseApkSha256"], "coreSha256": core_hash,
            "javaSources": frozen["javaSources"], "productiveTransforms": frozen["productiveTransforms"],
            "payloadSha256": {name: record["sha256"] for name, record in frozen["payloads"].items()},
            "compiledBackendSha256": {N64_CORE: frozen["n64"]["coreSha256"],
                                       **{name: record["sha256"] for name, record in frozen["dolphin"]["libraries"].items()}},
            "controllerProfileSha256": {platform: digest(profile_bytes(PROFILES[platform], frozen["n64" if platform == "n64" else "dolphin"]["options"])) for platform in PROFILES},
            "preservedClasses36Sha256": DEX36_SHA, "nativeBuild": value["nativeBuild"],
            "dependencySha256": {name: record["sha256"] for name, record in value["dependencies"].items()},
            "options": options}

def marker(identity, name, api, ndk, out):
    old = old_recipe(); raw = canonical(identity); fingerprint_hash = digest(raw)
    source = out / (name + ".c"); library = out / name
    source.write_text('__attribute__((visibility("default"))) const char *' + api + 'Identity(void) { return "' + fingerprint_hash + '"; }\n' +
                      '__attribute__((visibility("default"))) const char *' + api + 'Manifest(void) { return ' + json.dumps(raw.decode("ascii")) + '; }\n', encoding="ascii")
    tools = ndk / "toolchains/llvm/prebuilt/windows-x86_64/bin"
    command = [str(tools / "clang.exe"), "--target=aarch64-linux-android24", "-std=c11", "-Oz", "-fPIC", "-fvisibility=hidden", "-Wall", "-Wextra", "-Werror", "-shared", str(source), "-o", str(library),
               "-Wl,--no-undefined", "-Wl,--build-id=sha1", "-Wl,-soname," + name, "-Wl,-z,max-page-size=16384", "-Wl,-z,common-page-size=16384"]
    result = subprocess.run(command, capture_output=True, text=True)
    (out / (name + ".compile.log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode: raise RuntimeError("Runtime marker compilation failed")
    subprocess.run([str(tools / "llvm-strip.exe"), "--strip-unneeded", str(library)], check=True)
    elf = old.elf_metadata(library.read_bytes())
    if elf["soname"] != name or min(elf["loadAlignments"]) < 16384: raise ValueError("Marker ELF SONAME/alignment differs")
    symbols = subprocess.check_output([str(tools / "llvm-readelf.exe"), "--dyn-syms", "--wide", str(library)], text=True)
    for symbol in (api + "Identity", api + "Manifest"):
        if not re.search(r"GLOBAL\s+DEFAULT\s+(?!UND)\S+\s+" + symbol + r"\s*$", symbols, re.M): raise ValueError("Marker API missing")
    (out / (name + ".fingerprint.json")).write_bytes(raw + b"\n")
    return {"runtimeLibrary": name, "runtimeSha256": sha(library), "runtimeBytes": library.stat().st_size,
            "fingerprintSha256": fingerprint_hash, "elf": elf}

def profile_bytes(name, options):
    # Same insertion order/JSON string escaping as StationMultiplayerProfile.
    return json.dumps({"schemaVersion": 1, "controllerProfile": name, "devices": [1, 1, 1, 1], "coreOptions": options}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

def engines(original, frozen, markers):
    result = copy.deepcopy(original); matches = [i for i, e in enumerate(result["engines"]) if e.get("platform") == "n64"]
    if len(matches) != 1 or result["engines"][matches[0]]["engineId"] != N64_OLD_ID: raise ValueError("Wrong N64 replacement")
    if any(e.get("platform") in ("gamecube", "wii") for e in result["engines"]): raise ValueError("Dolphin entry already exists")
    created = []
    for platform in ("n64", "gamecube", "wii"):
        kind = "n64" if platform == "n64" else "dolphin"; source = frozen[kind]; marker_info = markers[kind]
        if kind == "n64":
            entry = copy.deepcopy(result["engines"][matches[0]])
            entry["engineId"] = "mupen64plus-ae-33bf7021-n64-v3-" + marker_info["runtimeSha256"][:12]
        else:
            entry = {"engineId": "dolphin-5102a033-" + platform + "-v3-" + marker_info["runtimeSha256"][:12],
                     "platform": platform, "backend": source["backend"], "library": DOLPHIN_NAMES[0],
                     "extensions": ["iso", "gcm", "gcz", "ciso", "wia", "rvz"] if platform == "gamecube" else ["iso", "gcz", "ciso", "wbfs", "wia", "rvz"],
                     "overlay": "", "options": source["options"],
                     "launchReady": True, "license": "GPL-2.0-or-later", "sourceDirectory": "dolphin-" + PIN,
                     "recoveryProtocol": "station-stream.v3", "maximumPlayers": 4,
                     "status": "implemented-candidate-peer-gameplay-pending", "contentIdentityByExtension": {"default": "launch-file-v1"}}
        entry.update(runtimeLibrary=marker_info["runtimeLibrary"], runtimeSha256=marker_info["runtimeSha256"],
                     coreSha256=source["coreSha256"] if kind == "n64" else source["libraries"][DOLPHIN_NAMES[0]]["sha256"],
                     dependencySha256={name: record["sha256"] for name, record in source["dependencies"].items()},
                     controllerProfiles=[PROFILES[platform]])
        if platform == "n64": result["engines"][matches[0]] = entry
        else: result["engines"].append(entry)
        created.append(entry)
    for policy in result.get("platformPolicies", []):
        if policy.get("platform") in ("gamecube", "wii"):
            policy["reason"] = "O Dolphin desta edição está preparado; aguarda o cadastro do motor e a aprovação dos modos de cada jogo no servidor."
    for index, entry in enumerate(original["engines"]):
        if index != matches[0] and entry != result["engines"][index]: raise AssertionError("Unrelated engine modified")
    if any(e["engineId"] == N64_OLD_ID for e in result["engines"]): raise AssertionError("Old live N64 identity remains")
    if len({e["engineId"] for e in result["engines"]}) != len(result["engines"]): raise AssertionError("Duplicate engine ID")
    return result, created

def build(freeze_path, ndk, out):
    out = checked_output(out, empty=True); frozen = read_json(freeze_path)
    if frozen.get("schemaVersion") != 2 or frozen.get("sourceFrozen") is not True: raise ValueError("Need exact final freeze")
    base = Path(frozen["basePath"])
    if sha(base) != BASE_SHA or frozen["baseApkSha256"] != BASE_SHA: raise ValueError("Frozen base changed")
    java, transforms = productive_sources()
    if java != frozen["javaSources"] or transforms != frozen["productiveTransforms"]: raise ValueError("Productive source changed after freeze")
    for name, info in frozen["payloads"].items():
        if name not in PAYLOADS or sha(info["path"]) != info["sha256"]: raise ValueError("Final payload changed after freeze")
    if set(frozen["payloads"]) != PAYLOADS: raise ValueError("Payload set differs")
    if validate_n64(base, frozen["n64"]["r125FreezePath"]) != frozen["n64"]: raise ValueError("N64 proof changed after freeze")
    if validate_dolphin(base, frozen["dolphin"]["directory"], frozen["dolphin"]["stage"]) != frozen["dolphin"]: raise ValueError("Dolphin proof changed after freeze")
    fs(out).mkdir(parents=True, exist_ok=True)
    markers = {"n64": marker(fingerprint(frozen, "n64"), N64_MARKER, "StationMupenRuntime", ndk, out),
               "dolphin": marker(fingerprint(frozen, "dolphin"), DOLPHIN_MARKER, "StationDolphinRuntime", ndk, out)}
    with zipfile.ZipFile(base) as archive: original = json.loads(archive.read("assets/station-online/engines.json"))
    manifest, created = engines(original, frozen, markers)
    raw = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if len(raw) > 32768: raise ValueError("Final engine asset exceeds 32 KiB reader limit")
    (out / "engines.json").write_bytes(raw)
    profiles = {}
    for entry in created:
        platform = entry["platform"]; raw_profile = profile_bytes(PROFILES[platform], entry["options"])
        (out / (platform + "-controller-profile.json")).write_bytes(raw_profile + b"\n")
        profiles[platform] = {"controllerProfile": PROFILES[platform], "sha256": digest(raw_profile), "canonical": raw_profile.decode("utf-8")}
    receipt = {"schemaVersion": 2, "baseApkSha256": BASE_SHA, "markers": markers, "engines": created,
               "enginesAssetSha256": sha(out / "engines.json"), "enginesAssetBytes": len(raw), "profiles": profiles,
               "preservedUnrelatedEngineCount": len(original["engines"]) - 1, "n64CorePreserved": True,
               "n64PluginsPreserved": True, "preservedClasses36Sha256": DEX36_SHA, "offlineLibrariesChanged": False,
               "physicalGameplayValidated": False, "serverRegistrationConfirmed": False}
    write_json(out / "runtime-identity.json", receipt)
    return receipt

def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest="action", required=True)
    f = sub.add_parser("freeze")
    for name in ("base", "n64-freeze", "dolphin", "stage", "java-receipt", "out"): f.add_argument("--" + name, type=Path, required=True)
    f.add_argument("--payload", action="append", required=True)
    b = sub.add_parser("build")
    for name in ("freeze", "ndk", "out"): b.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    if a.action == "freeze":
        result = freeze(a.base, a.n64_freeze, a.dolphin, a.stage, a.java_receipt, payload_mapping(a.payload), a.out)
        print(json.dumps({"frozen": True, "javaSources": len(result["javaSources"]), "physicalGameplayValidated": False}))
    else:
        result = build(a.freeze, a.ndk, a.out)
        print(json.dumps({"engines": [e["engineId"] for e in result["engines"]], "markers": result["markers"], "physicalGameplayValidated": False}))

if __name__ == "__main__": main()
