"""Renew only PSX/N64/GameCube/Wii IDs for the source-bound local demo overlay.

The four online cores, options, profiles, capacities and transport are preserved.
PS3/PS4 remain external offline routes and never receive an online engine entry.
"""
import argparse
import sys
from pathlib import Path
from pipeline_common import (
    REVISION, SHARED_ADDITIONS, demo_sources, load_psx, offline_sources,
    read, sha, verify_compilation,
)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    for name in ("parent-offline-receipt", "parent-offline-payloads", "demo-receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    own, remaining = parser.parse_known_args()
    payload_parser = argparse.ArgumentParser(add_help=False)
    payload_parser.add_argument("--payload", action="append", required=True)
    payload_parser.add_argument("--out", type=Path, required=True)
    selected, _ = payload_parser.parse_known_args(remaining)
    module = load_psx("build_runtime_identity")
    module.PAYLOADS |= set(SHARED_ADDITIONS)
    payloads = module.mapping(selected.payload)

    def verify():
        return verify_compilation(own.parent_offline_receipt, own.parent_offline_payloads,
                                  own.demo_receipt, payloads)

    verify()
    receipt_pins = {"parentOfflineReceiptSha256": sha(own.parent_offline_receipt),
                    "demoCompilationReceiptSha256": sha(own.demo_receipt)}
    current = module.source_pins

    def sources(receipt):
        verify()
        java, transforms = current(receipt)
        return java, {**transforms, **offline_sources(), **demo_sources()}

    module.source_pins = sources
    original = sys.argv
    try:
        sys.argv = [original[0], *remaining]
        module.main()
    finally:
        sys.argv = original
    verify()
    if receipt_pins != {"parentOfflineReceiptSha256": sha(own.parent_offline_receipt),
                        "demoCompilationReceiptSha256": sha(own.demo_receipt)}:
        raise ValueError("Compilation receipt changed during runtime fingerprinting")
    path = selected.out / "runtime-identity.json"
    receipt = read(path)
    baseline = read(Path(__file__).resolve().parents[2] / "ps3-ps4-offline/evidence/runtime-final.json")
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
                    "sonyLocalPlatformVideosAdded": ["ps3", "ps4"],
                    "sonyEmulatorConfigurationMenuAdded": ["ps3", "ps4"],
                    "signedCatalogChanged": False, "ps3Ps4OnlineEnabled": False})
    module.write(path, receipt)


if __name__ == "__main__":
    main()
