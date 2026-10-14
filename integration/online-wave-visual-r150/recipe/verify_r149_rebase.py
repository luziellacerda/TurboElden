"""Cryptographically prove that R150 visual inputs survive the signed R149 APK.

The script reads both signed APKs without changing them. The output receipt
belongs in private build evidence, not alongside source art or credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


R148_SHA256 = "c8b8c30cac7d36ec2a8ca8d470542096919435c749dede535cd0d58648e00dc1"
R149_SHA256 = "698e8a7914cc7be2facc00e6701ff1f3533fa13f763358b51578a35d25c2741e"
CHANGED = {
    "assets/station-online/engines.json": (
        "dcfcbc9f25e357edf3efc5a53e872b7bf8d4db41284fc8a796d2f4ca2b138af3",
        "3ee79e1ab9d55a0f043e2ad3c90e354667f06604ef5b34b8a1493f08786d9089",
    ),
    "classes10.dex": (
        "4d200405747b4d42108fe6bd8afdccc290db3fa1a72a9aa28c779f8772a53a78",
        "1f1b285af161fbf85573c081bee3bc6e4c95f90485d8d405ae064b86feb9144e",
    ),
    "lib/arm64-v8a/libstation_dolphin_runtime.so": (
        "bc104856a716ca758ddf01fbb801280ff4b4d3542dbd61df43ab9896d2af9497",
        "c80ec04d17233ea3aa228b1bef6091141cfa660f3eb0f97a98d2942eaeaed946",
    ),
    "lib/arm64-v8a/libstation_mupen64plus_runtime.so": (
        "7ca91607d2f88012793fe49b58e175755fa9a0c745abae6d2bc3b7bb6c4625dd",
        "dcad075758e57caea6d94557318d03c7f834801419fa00a576f857ecaaaad5d0",
    ),
    "lib/arm64-v8a/libstation_psx_online.so": (
        "9ceec5d203b0f2de3ec2ee381b0e37ededd7794fda2981ce8649b83356d71024",
        "29c3d7b9e6a801db7be37caef35a1b20b5c7c94eabc3493788a07dbb40965f65",
    ),
}
VISUAL_INPUTS = {
    "classes28.dex": "0f4e73bf6389d9d594c96f2e478d2c55fade7ea09ecccef124eba59ea2b91a3a",
    "classes35.dex": "dd9713ddace46aa902fe607a59ea13952afe374fed64f4200ab819537b9f8d2f",
    "classes40.dex": "216196f6c24095e4c51512a08782e56f6c3bc0444ce4f728308502c908489c4b",
    "lib/arm64-v8a/libmain.so": "62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6",
}


def hash_stream(stream) -> str:
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def hash_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hash_stream(stream)


def hash_entry(archive: ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hash_stream(stream)


def verify(r148: Path, r149: Path, output: Path) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    if hash_file(r148) != R148_SHA256 or hash_file(r149) != R149_SHA256:
        raise ValueError("Signed APK SHA mismatch")
    with ZipFile(r148) as left, ZipFile(r149) as right:
        names_left = set(left.namelist())
        names_right = set(right.namelist())
        if names_left != names_right:
            raise ValueError("APK entry set changed")
        differences: dict[str, dict[str, str]] = {}
        unchanged = 0
        for name in sorted(names_left):
            before = hash_entry(left, name)
            after = hash_entry(right, name)
            if before == after:
                unchanged += 1
            else:
                differences[name] = {"R148": before, "R149": after}
        expected = {name: {"R148": pair[0], "R149": pair[1]} for name, pair in CHANGED.items()}
        if differences != expected:
            raise ValueError("R149 includes an unexpected changed entry")
        for name, expected_sha in VISUAL_INPUTS.items():
            if hash_entry(right, name) != expected_sha:
                raise ValueError(f"R149 visual input differs: {name}")
    receipt = {
        "schema": "station.r150.visual.r149-rebase-proof.v1",
        "signedApkSha256": {"R148": R148_SHA256, "R149": R149_SHA256},
        "zipEntriesCheckedSha256": unchanged + len(differences),
        "unchangedEntries": unchanged,
        "changedEntries": differences,
        "visualInputSha256": VISUAL_INPUTS,
        "r149FunctionalEntriesMustRemainInR150": list(CHANGED),
        "archiveEntriesFullyHashed": True,
        "buildOrInstallPerformed": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r148-apk", type=Path, required=True)
    parser.add_argument("--r149-apk", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.r148_apk, args.r149_apk, args.out)
    print(json.dumps({k: v for k, v in result.items() if k != "changedEntries"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
