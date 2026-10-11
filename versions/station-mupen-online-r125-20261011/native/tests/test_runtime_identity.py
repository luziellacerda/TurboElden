"""Isolated identity/engine preservation checks; no server or gameplay claim."""
from __future__ import annotations
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import zipfile

VERSION = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("runtime_identity", VERSION / "recipes/build_runtime_identity.py")
recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--core", type=Path, required=True)
    args = parser.parse_args()
    checks = 0
    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)
    def rejected(callback, label: str) -> None:
        try:
            callback()
        except (ValueError, FileNotFoundError):
            check(True, label)
        else:
            check(False, label)
    core = args.core.read_bytes()
    meta = recipe.elf_metadata(core)
    check(meta["machine"] == "AArch64", "real complete core is AArch64")
    check(meta["soname"] == recipe.CORE_NAME, "own core SONAME")
    check(min(meta["loadAlignments"]) == 16384, "real core 16 KiB alignment")
    rejected(lambda: recipe.elf_metadata(b"not ELF"), "non-ELF refused")
    bad = bytearray(core);bad[18:20] = b"\x3e\x00"
    rejected(lambda: recipe.elf_metadata(bytes(bad)), "wrong architecture refused")
    with zipfile.ZipFile(args.base) as archive:
        original = json.loads(archive.read("assets/station-online/engines.json"))
        deps = recipe.dependencies(archive, core)
        check(len(deps) == 12, "complete exact plugin dependency closure")
        for name, info in deps.items():
            check(info["sha256"] == recipe.digest(archive.read(recipe.PREFIX + name)), "real APK dependency hash: " + name)
        check("libmupen64plus-core.so" not in deps, "offline core excluded")
        check("libstation_online_n64.so" not in deps, "old parallel core excluded")
        check("libmupen64plus-video-glide64mk2-egl.so" not in deps, "unused EGL plugin excluded")
        check("libmupen64plus-audio-android.so" in deps and "libmupen64plus-audio-android-fp.so" in deps, "both CoreInterface audio loads pinned")
    backend, options = recipe.literals()
    identity = {"backend": backend, "options": options, "dependencySha256": {name: info["sha256"] for name, info in deps.items()}}
    result, engine = recipe.engine_manifest(original, identity, recipe.digest(core), "a" * 64)
    check(len(result["engines"]) == 11, "engine count preserved")
    for index, entry in enumerate(original["engines"]):
        if entry["platform"] != "n64":
            check(result["engines"][index] == entry, "other engine preserved: " + entry["platform"])
    check(original != result, "only copied document changes")
    check(engine["backend"] == backend, "backend exactly matches Java")
    check(engine["options"] == options, "options exactly match Java")
    check(engine["library"] == recipe.CORE_NAME and engine["runtimeLibrary"] == recipe.RUNTIME_NAME, "own library pair")
    check(engine["maximumPlayers"] == 4, "native capacity four")
    check(engine["controllerProfiles"] == ["direct-four-ports-v1"], "direct ports profile")
    check(engine["overlay"] == "", "no RetroArch CFG overlay")
    check(engine["recoveryProtocol"] == "station-stream.v3", "existing authenticated recovery contract")
    check(not any(entry["engineId"] == recipe.OLD_ENGINE for entry in result["engines"]), "old engine identity removed")
    check(len(json.dumps(result).encode("utf-8")) < 32768, "within reader byte limit")
    duplicated = copy.deepcopy(original);duplicated["engines"].append(copy.deepcopy(original["engines"][5]))
    rejected(lambda: recipe.engine_manifest(duplicated, identity, "b" * 64, "c" * 64), "two selectable N64 candidates refused")
    changed = copy.deepcopy(original);changed["engines"][5]["engineId"] = "other"
    rejected(lambda: recipe.engine_manifest(changed, identity, "b" * 64, "c" * 64), "unknown base engine refused")
    rejected(lambda: recipe.payload_mapping(["classes35.dex=one"]), "partial final payloads refused")
    rejected(lambda: recipe.payload_mapping(["old.dex=one"]), "unknown payload refused")
    rejected(lambda: recipe.checked_output(VERSION / "other"), "artifact output constrained to approved G directory")
    frozen = {"backend": backend, "options": options, "baseApkSha256": recipe.BASE_SHA256,
        "core": {"sha256": recipe.digest(core), "path": "private/path"}, "sources": {"source.java": "d" * 64},
        "payloads": {"classes35.dex": {"sha256": "e" * 64, "path": "private/path"}}, "dependencies": deps, "nativeBuild": {"compiledSourceCount": 79}}
    fp = recipe.fingerprint(frozen)
    check(b"private/path" not in recipe.canonical(fp), "fingerprint does not bind private path")
    check(fp["rollback"] is False, "transport recovery does not claim state rollback")
    changed = copy.deepcopy(frozen);changed["payloads"]["classes35.dex"]["sha256"] = "f" * 64
    check(recipe.digest(recipe.canonical(fp)) != recipe.digest(recipe.canonical(recipe.fingerprint(changed))), "DEX change creates different identity")
    changed = copy.deepcopy(frozen);changed["options"] += "different=true\n"
    check(recipe.digest(recipe.canonical(fp)) != recipe.digest(recipe.canonical(recipe.fingerprint(changed))), "option change creates different identity")
    print(json.dumps({"checks": checks, "exactDependencyCount": len(deps), "otherEnginesPreserved": 10, "gameplayValidated": False}))

if __name__ == "__main__":
    main()
