"""Read-only preflight for the next Station online engine candidates.

This checks whether the exact offline cores from the reviewed R126 matrix are
still packaged, and whether R169 actually contains selectable online entries.
It deliberately does not create engine IDs or grant multiplayer modes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "audits/station-online-system-engines-20261011/remaining-systems/matrix.json"
CANDIDATES = {
    "nintendinho": "lib/arm64-v8a/libfceumm_libretro_android.so",
    "sega32x": "lib/arm64-v8a/libpicodrive_libretro_android.so",
}
REQUIRED_ABI = (
    "retro_run",
    "retro_set_environment",
    "retro_set_input_poll",
    "retro_set_input_state",
    "retro_serialize_size",
    "retro_serialize",
    "retro_unserialize",
    "retro_load_game",
    "retro_set_controller_port_device",
)


def zip_sha(archive: zipfile.ZipFile, name: str) -> str:
    digest = hashlib.sha256()
    with archive.open(name) as source:
        while block := source.read(131072):
            digest.update(block)
    return digest.hexdigest()


def assess(apk: Path, matrix: Path = MATRIX) -> dict:
    historical = json.loads(matrix.read_text(encoding="utf-8"))
    rows = {row["onlineCanonical"]: row for row in historical["rows"]}
    result = {"apk": str(apk), "scope": "read-only-static-preflight", "candidates": []}
    with zipfile.ZipFile(apk) as archive:
        registry = json.loads(archive.read("assets/station-online/engines.json"))
        result["registrySha256"] = zip_sha(archive, "assets/station-online/engines.json")
        result["registryEngineCount"] = len(registry["engines"])
        entries = set(archive.namelist())
        for platform, library in CANDIDATES.items():
            row = rows[platform]
            baseline = next(lib for lib in row["normal"]["libraries"] if lib["entry"] == library)
            present = library in entries
            current_sha = zip_sha(archive, library) if present else None
            pinned = present and current_sha == baseline["sha256"]
            abi = pinned and all(baseline["libretroAbiExports"].get(name) is True for name in REQUIRED_ABI)
            descriptors = [entry for entry in registry["engines"] if entry.get("platform") == platform]
            selectable = [entry for entry in descriptors if entry.get("launchReady") is True
                          and entry.get("recoveryProtocol") == "station-stream.v3"]
            blockers = []
            if not pinned:
                blockers.append("offline-core-identity-unverified")
            if not abi:
                blockers.append("pinned-libretro-abi-unverified")
            if not selectable:
                blockers.append("online-v3-descriptor-absent")
            # A descriptor and ABI exports do not implement the original
            # LibretroPlayer owner, frame barrier, transport or restore path.
            blockers.extend(("normal-owner-online-bridge-unproved",
                             "signed-game-mode-profile-unproved",
                             "two-device-gameplay-unproved"))
            result["candidates"].append({
                "platform": platform,
                "offlineCore": library,
                "historicalCoreSha256": baseline["sha256"],
                "currentCoreSha256": current_sha,
                "historicalAbiEvidenceBoundToCurrentBytes": bool(abi),
                "onlineDescriptorCount": len(descriptors),
                "onlineV3SelectableCount": len(selectable),
                "releaseReady": False,
                "blockers": blockers,
            })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, default=MATRIX)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = assess(args.apk, args.matrix)
    output = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
