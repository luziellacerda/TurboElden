"""Renew only PSX/N64/GameCube/Wii IDs for the source-bound local demo overlay.

The four online cores, options, profiles, capacities and transport are preserved.
PS3/PS4 remain external offline routes and never receive an online engine entry.
"""
import argparse
import copy
import sys
from pathlib import Path
from pipeline_common import (
    REVISION, SHARED_ADDITIONS, demo_sources, load_psx, offline_sources,
    read, sha, verify_compilation,
)


def compose_java_receipt(base, baseline, demo, strict, loop, payload, pins):
    """Describe the effective DEX without attributing an overlay to the base compiler."""
    partition = "classes35.dex"
    donor_sha = baseline["payloadSha256"][partition]
    player = "netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java"
    family = "Lorg/emulationstation/frontend/netplay/StationSinglePassVideo720;"
    changed = strict.get("changedTypes", [])
    if (base.get("compileOnlyStubsPackaged") is not False or
            base.get("classes35Sha256") != donor_sha or strict.get("donorSha256") != donor_sha or
            strict.get("sha256") != sha(payload) or
            strict.get("sha256") != demo["payloads"][partition]["sha256"] or
            strict.get("exactDonorClassSet") is not True or
            strict.get("allOtherClassesByteIdentical") is not True or
            strict.get("staticInitializersPreserved") is not True or
            strict.get("compileOnlyClasspathsPackaged") is not False or
            not changed or family not in changed or len(set(changed)) != len(changed) or
            any(name != family and not name.startswith(family[:-1] + "$" ) for name in changed) or
            changed != loop.get("dex35ChangedTypes") or
            loop["java"].get("allowedDex35Families") != [family] or
            base["sources"].get(player) != loop["java"]["sources"][player]["sourceSha256"] or
            loop["java"]["sources"][player].get("exactInverse") is not True):
        raise ValueError("Exact base Java compilation plus strict player-only DEX35 overlay required")
    effective = copy.deepcopy(base)
    effective.update({
        "receiptKind": "base-java-compilation-plus-scoped-dex35-overlay",
        "revision": REVISION,
        "classes35Sha256": strict["sha256"],
        "sourcesDescribeBaseCompilation": True,
        "baseJavaCompilationReceiptUnmodified": True,
        "composition": {
            "baseJavaReceiptSha256": pins["baseJavaCompilationReceiptSha256"],
            "baseClasses35Sha256": donor_sha,
            "baseCompilerProducedOverlayDex": False,
            "scopedDex35Overlay": {
                "partition": partition,
                "effectivePayload": demo["payloads"][partition],
                "demoCompilationReceiptSha256": pins["demoCompilationReceiptSha256"],
                "strictPartitionReceiptSha256": pins["dex35PreservationReceiptSha256"],
                "videoLoopCompilationReceiptSha256": pins["videoLoopCompilationReceiptSha256"],
                "donorApkSha256": demo["donorApkSha256"],
                "donorPartitionSha256": donor_sha,
                "changedTypes": changed,
                "classCount": strict["classCount"],
                "unchangedClasses": strict["unchangedClasses"],
                "unrelatedClassesByteIdentical": True,
                "staticInitializersPreserved": True,
                "compileOnlyClasspathsPackaged": False,
                "sourceTransform": loop["java"]["sources"][player],
            },
        },
    })
    return effective


def replace_java_receipt(arguments, path):
    result, count, i = [], 0, 0
    while i < len(arguments):
        argument = arguments[i]
        if argument == "--java-receipt":
            if i + 1 == len(arguments): raise ValueError("Missing base Java receipt")
            result.extend((argument, str(path))); count += 1; i += 2
        elif argument.startswith("--java-receipt="):
            result.append("--java-receipt=" + str(path)); count += 1; i += 1
        else:
            result.append(argument); i += 1
    if count != 1: raise ValueError("Exactly one original Java compilation receipt required")
    return result


def main():
    parser = argparse.ArgumentParser(add_help=False)
    for name in ("parent-offline-receipt", "parent-offline-payloads", "demo-receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    own, remaining = parser.parse_known_args()
    payload_parser = argparse.ArgumentParser(add_help=False)
    payload_parser.add_argument("--payload", action="append", required=True)
    payload_parser.add_argument("--out", type=Path, required=True)
    payload_parser.add_argument("--java-receipt", type=Path, required=True)
    selected, _ = payload_parser.parse_known_args(remaining)
    module = load_psx("build_runtime_identity")
    module.PAYLOADS |= set(SHARED_ADDITIONS)
    payloads = module.mapping(selected.payload)

    def verify():
        return verify_compilation(own.parent_offline_receipt, own.parent_offline_payloads,
                                  own.demo_receipt, payloads)

    _, demo = verify()
    baseline = read(Path(__file__).resolve().parents[2] / "ps3-ps4-offline/evidence/runtime-final.json")
    base_java = read(selected.java_receipt)
    strict_path = own.demo_receipt.parent / "dex35-receipt.json"
    loop_path = own.demo_receipt.parent / "video-loop-receipt.json"
    receipt_paths = {"parentOfflineReceiptSha256": own.parent_offline_receipt,
                     "demoCompilationReceiptSha256": own.demo_receipt,
                     "baseJavaCompilationReceiptSha256": selected.java_receipt,
                     "dex35PreservationReceiptSha256": strict_path,
                     "videoLoopCompilationReceiptSha256": loop_path}
    receipt_pins = {name: sha(path) for name, path in receipt_paths.items()}
    current = module.source_pins
    current(base_java)  # Validate the unchanged complete base source set first.
    effective = compose_java_receipt(base_java, baseline, demo, read(strict_path),
                                     read(loop_path), payloads["classes35.dex"], receipt_pins)
    selected.out.mkdir(parents=True, exist_ok=True)
    composite_path = (selected.out / "java-effective-receipt.json").resolve()
    if composite_path == selected.java_receipt.resolve() or composite_path.exists():
        raise ValueError("Never overwrite original or existing effective Java receipt")
    module.write(composite_path, effective)
    receipt_paths["compositeJavaReceiptSha256"] = composite_path
    receipt_pins["compositeJavaReceiptSha256"] = sha(composite_path)

    def sources(receipt):
        verify()
        if receipt != effective or receipt_pins != {name: sha(path) for name, path in receipt_paths.items()}:
            raise ValueError("Explicit base/overlay Java composition changed during fingerprinting")
        java, transforms = current(base_java)
        return java, {**transforms, **offline_sources(), **demo_sources()}

    module.source_pins = sources
    original = sys.argv
    try:
        sys.argv = [original[0], *replace_java_receipt(remaining, composite_path)]
        module.main()
    finally:
        sys.argv = original
    verify()
    if receipt_pins != {name: sha(path) for name, path in receipt_paths.items()}:
        raise ValueError("Compilation receipt changed during runtime fingerprinting")
    path = selected.out / "runtime-identity.json"
    receipt = read(path)
    by_platform = {engine["platform"]: engine for engine in receipt["engines"]}
    if set(by_platform) != {"psx", "n64", "gamecube", "wii"}:
        raise ValueError("Only the four existing online engine identities may be renewed")
    strip = lambda value: {key: val for key, val in value.items() if key not in ("engineId", "runtimeSha256")}
    for previous in baseline["engines"]:
        current_engine = by_platform[previous["platform"]]
        if strip(previous) != strip(current_engine):
            raise ValueError("R128 engine core/options/policy changed: " + previous["platform"])
        if previous["engineId"] == current_engine["engineId"]:
            raise ValueError("Changed shared DEX requires a new engine identity")
    receipt.update({"revision": REVISION, **receipt_pins, "localDemonstrationsOnly": True,
                    "javaReceiptComposition": effective["composition"],
                    "baseJavaCompilerProducedOverlayDex": False,
                    "sonyLocalPlatformVideosAdded": ["ps3", "ps4"],
                    "sonyEmulatorConfigurationMenuAdded": ["ps3", "ps4"],
                    "signedCatalogChanged": False, "ps3Ps4OnlineEnabled": False})
    module.write(path, receipt)


if __name__ == "__main__":
    main()
