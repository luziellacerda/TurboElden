"""Closed R129 overlay on the exact, frozen R128 offline implementation."""
from pathlib import Path
import hashlib
import json
import sys
import types

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent / "ps3-ps4-offline"
PSX = ROOT.parent / "psx-online"
REVISION = "R129"
DONOR_SHA = "0189527c7537845562a2be4be15c0fab976c85f4f9c7f8ab884915c8bc3052dc"
DONOR_BYTES = 2234617901
SHARED_ADDITIONS = frozenset(("classes39.dex", "lib/arm64-v8a/libturbo_carousel.so"))
MEDIA_ADDITIONS = frozenset(("assets/turbo-system-videos/720-ps3.mp4", "assets/turbo-system-videos/720-ps4.mp4"))
SHARED_ADDITIONS |= MEDIA_ADDITIONS
PARENT_PAYLOADS = {
    "AndroidManifest.xml": "AndroidManifest.xml",
    "classes28.dex": "classes28.dex",
    "classes39.dex": "classes39.dex",
    "libturbo_carousel.so": "lib/arm64-v8a/libturbo_carousel.so",
}
DEMO_PAYLOADS = {
    "classes28.dex": "classes28.dex",
    "classes39.dex": "classes39.dex",
    "libturbo_carousel.so": "lib/arm64-v8a/libturbo_carousel.so",
    "assets/turbo-system-videos/720-ps3.mp4": "assets/turbo-system-videos/720-ps3.mp4",
    "assets/turbo-system-videos/720-ps4.mp4": "assets/turbo-system-videos/720-ps4.mp4",
}
PARENT_JAVA = (
    "java/org/emulationstation/frontend/offline/StationSonyOfflineActivity.java",
    "java/org/emulationstation/frontend/offline/StationSonyOfflinePolicy.java",
)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_psx(name, *, revision=False):
    source = PSX / "recipe" / (name + ".py")
    text = source.read_text(encoding="utf-8")
    if revision:
        text = text.replace('"R127"', '"' + REVISION + '"')
    module = types.ModuleType("r129_parent_" + name)
    module.__file__ = str(source)
    exec(compile(text, str(source), "exec"), module.__dict__)
    return module


def offline_sources():
    source = PARENT / "recipe" / "pipeline_common.py"
    module = types.ModuleType("r129_frozen_offline_sources")
    module.__file__ = str(source)
    exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), module.__dict__)
    return module.offline_sources()


def demo_source_map():
    result = {}
    for directory, suffix in (("java", ".java"), ("recipe", ".py")):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and path.suffix == suffix:
                result[path.relative_to(ROOT).as_posix()] = sha(path)
    for path in sorted(ROOT.glob("*.json")):
        result[path.relative_to(ROOT).as_posix()] = sha(path)
    if not any(name.startswith("java/") for name in result):
        raise ValueError("Complete local demonstration Java sources required")
    return result


def demo_sources():
    return {"local-demos/" + name: value for name, value in demo_source_map().items()}


def check_file(path, record, label):
    path = Path(path)
    if not path.is_file() or path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
        raise ValueError("Compilation payload changed: " + label)


def verify_compilation(parent_receipt_path, parent_payloads, demo_receipt_path, final_payloads):
    """Check both compilation receipts and actual payload bytes before fingerprinting."""
    parent = read(parent_receipt_path)
    published = read(PARENT / "evidence" / "offline-payloads.json")
    baseline = read(PARENT / "evidence" / "runtime-final.json")
    demo = read(demo_receipt_path)
    if parent != published:
        raise ValueError("Parent receipt must be the exact frozen R128 offline compilation")
    if parent.get("passed") is not True or parent.get("offlineOnly") is not True:
        raise ValueError("Successful offline-only parent compilation required")
    if {"offline/" + name: value for name, value in parent["sourceSha256"].items()} != offline_sources():
        raise ValueError("Frozen R128 offline source changed")
    if set(parent["payloads"]) != set(PARENT_PAYLOADS):
        raise ValueError("Four exact R128 offline parent payloads required")
    for name, target in PARENT_PAYLOADS.items():
        check_file(Path(parent_payloads) / name, parent["payloads"][name], name)
        if parent["payloads"][name]["sha256"] != baseline["payloadSha256"][target]:
            raise ValueError("R128 parent payload differs from published identity: " + name)
    if (demo.get("passed") is not True or demo.get("offlineOnly") is not True or
            demo.get("localDisplayOnly") is not True or demo.get("signedCatalogChanged") is not False or
            demo.get("donorApkSha256") != DONOR_SHA or demo.get("realDownloadsChanged") is not False or
            demo.get("graphicsRenderMethodsChanged") is not True or
            demo.get("graphicsRenderChangeScope") != "two-new-Sony-settings-owned-label-exclusions-only" or
            demo.get("existingCarouselGeometryAndEffectRenderMethodsChanged") is not False or
            demo.get("existingOnlineCodePreserved") is not True):
        raise ValueError("Successful local-only demonstration compilation from exact R128 required")
    native = read(Path(demo_receipt_path).parent / "native-receipt.json")
    settings = native.get("sonySettingsMenuReceipt", {})
    if (native.get("sha256") != demo["payloads"]["libturbo_carousel.so"]["sha256"] or
            settings.get("nativeCppExactInverse") is not True or
            settings.get("sonyLabelsDrawnOnlyByOpenSettingsModal") is not True):
        raise ValueError("Compiled Sony modal label guard is missing or binds another native payload")
    if demo.get("sourceSha256") != demo_source_map():
        raise ValueError("Local demonstration sources changed after compilation")
    expected_parent = {name: sha(PARENT / name) for name in PARENT_JAVA}
    if demo.get("parentSourceSha256") != expected_parent:
        raise ValueError("Demo bridge compilation did not bind exact frozen Sony parent Java")
    expected_native_parent = {name: sha(PARENT / name) for name in (*PARENT_JAVA, "recipe/patch_native.py", "native/offline_routes.h")}
    if demo.get("parentNativeSourceInputs") != expected_native_parent:
        raise ValueError("Demo native hook did not bind exact frozen R128 source inputs")
    if set(demo.get("payloads", {})) != set(DEMO_PAYLOADS):
        raise ValueError("Exact DEX28/DEX39, Sony native hook and two Sony media additions required")
    if (demo.get("nativeBaselineSha256") != parent["payloads"]["libturbo_carousel.so"]["sha256"] or
            demo.get("baselineNativeByteIdentical") is not True):
        raise ValueError("Native demo hook must be based on byte-reproduced R128 carousel")
    expected_shared = set(baseline["payloadSha256"]) | MEDIA_ADDITIONS
    if set(final_payloads) != expected_shared:
        raise ValueError("Exact six R128 shared names and two Sony media additions required")
    for name, target in DEMO_PAYLOADS.items():
        check_file(final_payloads[target], demo["payloads"][name], name)
    for name in expected_shared - set(DEMO_PAYLOADS.values()):
        if sha(final_payloads[name]) != baseline["payloadSha256"][name]:
            raise ValueError("Unchanged R128 payload differs: " + name)
    if demo.get("preservedParentPayloadSha256") != {
            name: baseline["payloadSha256"][name] for name in ("AndroidManifest.xml", "classes6.dex", "classes35.dex")}:
        raise ValueError("Demo compilation did not preserve exact parent manifest/shared Java partitions")
    return parent, demo


def assembler():
    module = load_psx("assemble_apk", revision=True)
    module.SHARED |= SHARED_ADDITIONS
    module.REPLACED |= frozenset(("lib/arm64-v8a/libturbo_carousel.so",))
    module.ADDED |= frozenset(("classes39.dex",))
    module.ADDED |= MEDIA_ADDITIONS
    module.PAYLOADS = module.REPLACED | module.ADDED
    current = module.current_sources

    def sources():
        java, transforms = current()
        offline, demos = offline_sources(), demo_sources()
        if set(transforms) & (set(offline) | set(demos)) or set(offline) & set(demos):
            raise ValueError("Productive source namespace collision")
        return java, {**transforms, **offline, **demos}

    module.current_sources = sources
    return module
