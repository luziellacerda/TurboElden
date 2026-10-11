"""Renew four existing online identities for the exact internal-Sony shared bundle.

Sony remains offline. R130 Java/render/media/native cores and options are inherited,
not recompiled or attributed to the new host compiler.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import types
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PSX = ROOT.parent / "psx-online"
BASE_SHA = "d227b0af17600bf99ec097857bf182f6e7989f8ddc3b68b63e17c81f69eb30ad"
BASE_BYTES = 2237522133
REVISION = "R131"
PREFIX = "lib/arm64-v8a/"
MARKERS = {"psx": "libstation_psx_online.so", "n64": "libstation_mupen64plus_runtime.so",
    "dolphin": "libstation_dolphin_runtime.so"}
PARENT_MARKER_SHA = {"psx": "8502dc971a89e578890843a1ba44eb79eaffbbd2a4a988deac880a17dc2a5377",
    "n64": "61d0bdd0db5e4be480e2390104d76c08dd40b87f639650ac5e5065ac6616a8df",
    "dolphin": "e1be15478a3d4ddc31c605bee19539744714a32d0b6cdef51a07f85c2c661dd6"}
PARENT_FINGERPRINT_SHA = {"psx": "9f6ef71e107cdbf14514e7b76bb8a02c63bdc3b697d1b2aa279396149a42eec1",
    "n64": "8c7a78dac3a77c5c430b8c593f4ae32d001dde517d118be7483ec80cf4b40b8a",
    "dolphin": "44c83d5d8f58d0c43d4acec2e6cbca9f777555329687f69fb09a593b9f16ce34"}
INHERITED = frozenset(["classes.dex", *[f"classes{i}.dex" for i in range(2, 40)],
    "resources.arsc", PREFIX + "libturbo_carousel.so",
    "assets/turbo-system-videos/720-ps3.mp4", "assets/turbo-system-videos/720-ps4.mp4"])


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def digest(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def legacy(name):
    path = PSX / "recipe" / (name + ".py")
    module = types.ModuleType("sony_r131_" + name)
    module.__file__ = str(path)
    text = path.read_text(encoding="utf-8").replace('"R127"', '"R131"')
    exec(compile(text, str(path), "exec"), module.__dict__)
    return module


def source_map():
    return {path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted(ROOT.rglob("*")) if path.is_file() and
        path.suffix in {".java", ".py", ".cpp", ".h", ".hpp", ".json"} and
        "__pycache__" not in path.parts}


def dependency_source_map():
    paths = (PSX / "recipe/build_runtime_identity.py",
        REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py",
        REPO / "versions/station-game-menu-controller-audit-r120-20261010/recipes/patch_component_factory.py")
    return {path.relative_to(REPO).as_posix(): sha(path) for path in paths}


def productive_transforms(inherited):
    return {**inherited, **{"sony-internal/" + name: value for name, value in source_map().items()},
        **{"sony-internal-dependencies/" + name: value for name, value in dependency_source_map().items()}}


def check_file(record, label):
    original = Path(record["path"])
    path = original.resolve(strict=True)
    if original.is_symlink() or not path.is_file() or path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
        raise ValueError("Pinned compilation artifact changed: " + label)
    return path


def archive_sha(archive, name):
    result = hashlib.sha256()
    with archive.open(name) as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""): result.update(part)
    return result.hexdigest()


def compilation(base, asset_path, host_path, manifest_path, derived_path, child_path):
    if Path(base).stat().st_size != BASE_BYTES or sha(base) != BASE_SHA:
        raise ValueError("Exact R130 donor required")
    assets, host, manifest, derived, child = map(read, (asset_path, host_path, manifest_path, derived_path, child_path))
    prep = load(ROOT / "composition/recipe/prepare_assets.py", "r131_asset_contract")
    compiler = load(ROOT / "recipe/compile_host.py", "r131_host_contract")
    axml = load(ROOT / "recipe/patch_manifest.py", "r131_manifest_contract")
    if (assets.get("schema") != "station.sony.internal.assets.v1" or assets.get("passed") is not True or
            assets.get("assetsOnly") is not True or assets.get("packageBuilt") is not False or
            assets.get("sourceRecipeSha256") != sha(ROOT / "composition/recipe/prepare_assets.py") or
            set(assets.get("modules", {})) != {"ps3", "ps4"}):
        raise ValueError("Frozen private Sony asset preparation required")
    if (host.get("schema") != "station.sony.internal.host.v1" or host.get("passed") is not True or
            host.get("baseApkSha256") != BASE_SHA or host.get("compileOnlyClassesPackaged") is not False or
            host.get("assetReceiptSha256") != sha(asset_path) or
            host.get("sourceSha256") != {name: sha(path) for name, path in compiler.source_map().items()} or
            host.get("generatedSourceSha256") != assets["generatedSource"]["sha256"]):
        raise ValueError("Actual new-host compilation bound to the asset pins is required")
    check_file(assets["generatedSource"], "generated Sony pins")
    if (manifest.get("passed") is not True or manifest.get("baseApkSha256") != BASE_SHA or
            manifest.get("exactInverse") is not True or manifest.get("resourcesUnchanged") is not True or
            manifest.get("allOtherComponentsAndAttributesPreserved") is not True or
            manifest.get("addedActivities") != axml.COMPONENTS or manifest.get("factory") != axml.NEW_FACTORY or
            manifest.get("sourceSha256") != {"recipe/patch_manifest.py": sha(ROOT / "recipe/patch_manifest.py")} or
            manifest.get("ownerLaunchMode") != "singleTask" or manifest.get("ownerConfigChanges") != 0xfb0 or
            manifest.get("exported") is not False):
        raise ValueError("Exact private activity/factory-only Manifest patch required")
    shared = {name: check_file(record, name) for name, record in assets["payloads"].items()}
    if len(shared) != 299 or any(not name.startswith(("assets/sony/ps3/", "assets/sony/ps4/")) for name in shared):
        raise ValueError("Exact 299 Sony asset additions required")
    for system, module in assets["modules"].items():
        if module.get("sourceApkSha256") != prep.OFFICIAL[system]["sha256"]:
            raise ValueError("Wrong official Sony source")
        path = shared["assets/sony/" + system + "/module.json"]
        raw = path.read_bytes()
        if digest(raw) != module["manifestSha256"]:
            raise ValueError("Module descriptor pin mismatch")
        descriptor = json.loads(raw)
        expected = {"assets/" + row["asset"]: {"path": str(shared["assets/" + row["asset"]]),
            "bytes": row["bytes"], "sha256": row["sha256"]} for row in descriptor["files"]}
        for name, row in expected.items():
            if row != assets["payloads"][name]: raise ValueError("Module files differ from asset receipt")
        if module.get("sourceNativeBytesUnmodified") is not True:
            raise ValueError("Official native bytes were changed")
    if (derived.get("schema") != "station.sony.ps4.derived.v1" or
            derived.get("sourceApkSha256") != prep.OFFICIAL["ps4"]["sha256"] or
            assets["modules"]["ps4"]["derivedReceipt"]["inputReceiptSha256"] != sha(derived_path) or
            child.get("sourceApkSha256") != prep.OFFICIAL["ps4"]["sha256"] or
            child.get("nativeLibrariesModified") is not False or
            len(child.get("nativeRegistration", [])) != 67 or
            child.get("recipeSha256") != sha(ROOT / "ps4/recipe/build_owner.py")):
        raise ValueError("Actual isolated PS4 child compilation/derivation required")
    expected_child = {path.relative_to(ROOT / "ps4").as_posix(): sha(path)
        for path in sorted((ROOT / "ps4/child-java").rglob("*.java"))}
    if {row["path"]: row["sha256"] for row in child.get("sourceFiles", [])} != expected_child:
        raise ValueError("PS4 child sources changed after compilation")
    toolchain = child.get("toolchain", [])
    if (len(toolchain) != 6 or {row.get("role") for row in toolchain} !=
            {"javac", "java", "androidJar", "d8Jar", "apktoolJar", "decoderSource"} or
            any(not re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", "")) for row in toolchain)):
        raise ValueError("Actual six-tool PS4 child compilation provenance required")
    hashes = {row["path"]: row["sha256"] for row in derived["files"]}
    if (set(hashes) != prep.PS4_DERIVED_PATHS or hashes["upstream/derived/owner.dex"] != child["ownerDexSha256"] or
            hashes["upstream/derived/pkg-rsa.bin"] != child["pkgMaterialSha256"] or
            any(row.get("derivationReceiptSha256") != sha(child_path) for row in derived["files"])):
        raise ValueError("Derived child/material differs from real derivation receipt")
    for row in derived["files"]:
        path = shared["assets/sony/ps4/" + row["path"]]
        if sha(path) != row["sha256"]: raise ValueError("Frozen PS4 child payload changed")
    new_host = host["payload"]
    new_manifest = manifest["payload"]
    if new_host["name"] != "classes40.dex" or new_manifest["name"] != "AndroidManifest.xml":
        raise ValueError("Exact new DEX40/Manifest payloads required")
    shared["classes40.dex"] = check_file(new_host, "DEX40")
    shared["AndroidManifest.xml"] = check_file(new_manifest, "Manifest")
    jni = load(ROOT / "ps3/recipe/verify_jni.py", "r131_actual_ps3_jni")
    jni.verify(shared["classes40.dex"], ROOT / "ps3/evidence/official-contract.json")
    with zipfile.ZipFile(base) as archive:
        inherited = {name: archive_sha(archive, name) for name in INHERITED}
        dex = {name: inherited[name] for name in INHERITED if name.endswith(".dex")}
        if host["preservedDexSha256"] != dex:
            raise ValueError("Host was not compiled against the exact 39 preserved DEX")
        if archive_sha(archive, "AndroidManifest.xml") != manifest["donorSha256"]:
            raise ValueError("Manifest donor differs")
        if axml.patch(archive.read("AndroidManifest.xml")) != shared["AndroidManifest.xml"].read_bytes():
            raise ValueError("Manifest bytes do not match the closed source transform")
        if compiler.dex_types(shared["classes40.dex"].read_bytes()) != set(host["newTypes"]):
            raise ValueError("Compiled host class set differs")
        for name in dex:
            if set(host["newTypes"]) & compiler.dex_types(archive.read(name)):
                raise ValueError("New host shadows an existing Station class")
    return shared, inherited, {"assets": assets, "host": host, "manifest": manifest, "child": child}


def parent_sources():
    common = load(ROOT.parent / "local-sony-demos/recipe/pipeline_common.py", "r131_r130_sources")
    return common.assembler().current_sources()


def parents(base, directory):
    receipt = read(directory / "runtime-identity.json")
    if receipt.get("revision") != "R130" or receipt.get("markers", {}).keys() != MARKERS.keys():
        raise ValueError("Exact R130 parent identity receipt required")
    result = {}
    with zipfile.ZipFile(base) as archive:
        for kind, library in MARKERS.items():
            name = "psx.fingerprint.json" if kind == "psx" else library + ".fingerprint.json"
            raw = (directory / name).read_bytes().rstrip(b"\r\n")
            value = json.loads(raw)
            binary = archive.read(PREFIX + library)
            if (digest(raw) != PARENT_FINGERPRINT_SHA[kind] or raw != canonical(value) or raw not in binary or
                    digest(binary) != PARENT_MARKER_SHA[kind] or
                    receipt["markers"][kind]["runtimeSha256"] != PARENT_MARKER_SHA[kind]):
                raise ValueError("Parent runtime differs from actual installed R130: " + kind)
            result[kind] = value
    sources = parent_sources()
    if any((value["javaSources"], value["productiveTransforms"]) != sources for value in result.values()):
        raise ValueError("Frozen R130 productive sources changed")
    return receipt, result, sources


class DonorEntry:
    """An actual ZIP-entry digest, not a fabricated filesystem/compiler artifact."""
    def __init__(self, name, checksum): self.name, self.checksum = name, checksum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "ndk", "assets-receipt", "host-receipt", "manifest-receipt", "derived-receipt",
            "child-receipt", "parent-identity", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.source): raise ValueError("Explicit source commit required")
    if args.out.exists(): raise ValueError("Never overwrite a runtime identity tree")
    paths = {name: getattr(args, name.replace("-", "_")) for name in
        ("assets-receipt", "host-receipt", "manifest-receipt", "derived-receipt", "child-receipt")}
    shared, inherited, compiled = compilation(args.base, *paths.values())
    parent, fingerprints, inherited_sources = parents(args.base, args.parent_identity)
    parent_java_path = args.parent_identity / "java-effective-receipt.json"
    parent_java = read(parent_java_path)
    if (parent_java.get("receiptKind") != "base-java-compilation-plus-scoped-dex35-overlay" or
            parent_java.get("classes35Sha256") != inherited["classes35.dex"] or
            parent_java.get("compileOnlyStubsPackaged") is not False or
            parent_java.get("composition", {}).get("baseCompilerProducedOverlayDex") is not False):
        raise ValueError("Unmodified actual R130 effective Java receipt required")
    source_pins = source_map()
    dependency_pins = dependency_source_map()
    receipt_pins = {name: sha(path) for name, path in paths.items()}
    extra = productive_transforms(inherited_sources[1])
    module = legacy("build_runtime_identity")
    module.BASE_SHA = BASE_SHA
    module.PAYLOADS = set(shared) | set(inherited)
    module.PARENTS = {kind: {**parent["markers"][kind], "backend": fingerprints[kind]["backend"]}
        for kind in ("n64", "dolphin")}
    actual_sha = module.sha
    module.sha = lambda path: path.checksum if isinstance(path, DonorEntry) else actual_sha(path)
    bound = {**shared, **{name: DonorEntry(name, checksum) for name, checksum in inherited.items()}}
    module.mapping = lambda values: bound
    def sources(receipt):
        if (receipt != parent_java or source_map() != source_pins or dependency_source_map() != dependency_pins or
                {name: sha(path) for name, path in paths.items()} != receipt_pins or parent_sources() != inherited_sources):
            raise ValueError("Actual compilation/source receipt changed during fingerprinting")
        return inherited_sources[0], extra
    module.source_pins = sources
    argv = sys.argv
    try:
        sys.argv = [argv[0], "--base", str(args.base), "--ndk", str(args.ndk),
            "--java-receipt", str(parent_java_path), "--parent-identity", str(args.parent_identity),
            "--payload", "classes40.dex=" + str(shared["classes40.dex"]), "--out", str(args.out)]
        module.main()
    finally:
        sys.argv = argv
    again, preserved, _ = compilation(args.base, *paths.values())
    if again != shared or preserved != inherited or source_map() != source_pins or dependency_source_map() != dependency_pins:
        raise ValueError("Inputs changed during identity compilation")
    path = args.out / "runtime-identity.json"
    result = read(path)
    strip = lambda row: {key: value for key, value in row.items() if key not in ("engineId", "runtimeSha256")}
    if len(result["engines"]) != 4:
        raise ValueError("Only four existing online identities may be renewed")
    for before, after in zip(parent["engines"], result["engines"]):
        if strip(before) != strip(after) or before["engineId"] == after["engineId"]:
            raise ValueError("Existing engine policy changed or its identity was not renewed")
    result.update({"revision": REVISION, "sourceCommit": args.source, "r130ParentIdentityReceiptSha256": sha(args.parent_identity / "runtime-identity.json"),
        "r130JavaEffectiveReceiptSha256": sha(parent_java_path), "r130JavaReceiptUnmodified": True,
        "r130ParentIdentityDirectory": str(args.parent_identity.resolve()),
        "newHostCompilerProducedExistingDex": False, "existing39DexByteIdentical": True,
        "preservedR130PayloadSha256": inherited, "sourceSha256": source_pins,
        "dependencySourceSha256": dependency_pins,
        "compilationReceiptSha256": receipt_pins,
        "compilationReceiptPaths": {name: str(path.resolve()) for name, path in paths.items()},
        "newSharedPayloadSha256": {name: sha(path) for name, path in shared.items()},
        "sonyModules": {key: {name: value[name] for name in ("moduleId", "manifestSha256", "sourceApkSha256")}
            for key, value in compiled["assets"]["modules"].items()},
        "ps3Ps4OfflineOnly": True, "ps3Ps4OnlineEnabled": False, "sonyNativeLibrariesModified": False,
        "resourcesAndEconomyRenderControllerCodeChanged": False,
        "firmwareBundledIsNotProofOfImport": True, "androidBootstrapOrGameplayValidated": False})
    module.write(path, result)


if __name__ == "__main__": main()
