"""Prepare ten scoped blue-literal edits against the exact R149 DEX projection.

The caller must decode the three SHA-pinned R149 DEX partitions with the
reviewed R145 DecodeDolphinPartition tool. Only seven source classes are
emitted. A downstream scoped assembler must preserve every other class.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


DEX_SHA256 = {
    "classes28.dex": "0f4e73bf6389d9d594c96f2e478d2c55fade7ea09ecccef124eba59ea2b91a3a",
    "classes35.dex": "dd9713ddace46aa902fe607a59ea13952afe374fed64f4200ab819537b9f8d2f",
    "classes40.dex": "216196f6c24095e4c51512a08782e56f6c3bc0444ce4f728308502c908489c4b",
}
TOP_OLD, TOP_NEW = "0xff287eb5", "0xff226fa7"
BOTTOM_OLD, BOTTOM_NEW = "0xff5daede", "0xff509acc"
CHANGES = {
    "classes28.dex": {
        "Lorg/emulationstation/frontend/station/StationWaveBackground;": (
            "6c436ff793c9e4287cce0cb970c36a067dfcbd45f1a0a54dc33f58914fbaac46",
            [(".method protected onDraw(Landroid/graphics/Canvas;)V", "cb90e7d997f3fc2430c7982a3f5fdfc2c5e3d94a92e7ecc4dc3f3a5009250b77", TOP_OLD, TOP_NEW)]),
        "Lorg/emulationstation/frontend/station/StationDownloadPanel;": (
            "7a34cebba5e831d8206f1b1cecb312ec8ff62cebfd514e6c0658e93a944f223e",
            [(".method protected onCreate(Landroid/os/Bundle;)V", "b2427688edaf86ec9b28dd09e191622dca7d393c1229ce60ee511bd211e98cad", TOP_OLD, TOP_NEW)]),
        "Lorg/emulationstation/frontend/station/StationDownloadUi;": (
            "8a25b5b574e89b3ecbbc0363b9aa2902975f74c5c621a04ea8863e32d1799201",
            [(".method static messageDialog(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/app/Dialog;", "ed90deb97213147bdd8ddb0833ec3fc3a5770ee0094abca2abd22a053fc10203", TOP_OLD, TOP_NEW)]),
    },
    "classes35.dex": {
        "Lorg/emulationstation/frontend/netplay/StationHyperspaceView;": (
            "97b3269bd5c11b7b383049641260df5ad416a538b28c8c07361e569ec2a5b0c3",
            [(".method private renderBackground(II)Landroid/graphics/Bitmap;", "39be90b56e14c7da5dc4ddda95c620873b2ff709ce5b1b726fb2070d17cf5e67", TOP_OLD, TOP_NEW),
             (".method private renderBackground(II)Landroid/graphics/Bitmap;", "39be90b56e14c7da5dc4ddda95c620873b2ff709ce5b1b726fb2070d17cf5e67", BOTTOM_OLD, BOTTOM_NEW),
             (".method protected onDraw(Landroid/graphics/Canvas;)V", "26e7d8c045fd715aab4194237fcfb34c468c90659d411a56df8b9f5b571e4529", TOP_OLD, TOP_NEW)]),
        "Lorg/emulationstation/frontend/netplay/StationRoomsActivity;": (
            "93ec7c1fc1b70ebacb9956ae1f3ca36f8df1a3238e5a2fb2fe3b664b2d7d287e",
            [(".method private build()V", "4fc4c01597a9d65277dfff8f4318473e5eb2b9b7d9919de301e5ee89627f29f6", TOP_OLD, TOP_NEW),
             (".method private applyGraphics()V", "3887df79865c24e56b374b0939f338d1c216d5fe0a44e547adbe30e30af12764", TOP_OLD, TOP_NEW)]),
    },
    "classes40.dex": {
        "Lorg/emulationstation/frontend/sony/Ps3Activity;": (
            "e87b17f7a1ece332051abbd4c06be7bb3104d7cfd8b10929d673fca46a60b96f",
            [(".method private showSettings()V", "fe3ed1b8fe704d5b51e894aad669f58f78f3eeb90c285615559f123694eff0d4", TOP_OLD, TOP_NEW)]),
        "Lorg/emulationstation/frontend/sony/Ps4Activity;": (
            "2cd6402d3bf862efdfd04722f6c5df6b34e64d4398f5185def64edf3f94c4a90",
            [(".method private showSettings()V", "3966593c8d8c0a79f3e563cc02c10e6f950bf322e4f892c74db82c5faecb7e31", TOP_OLD, TOP_NEW)]),
    },
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def signed(value: str) -> str:
    integer = int(value, 16)
    return hex(integer - (1 << 32) if integer >= 1 << 31 else integer)


def method_span(source: str, signature: str) -> tuple[int, int]:
    needle = signature + ("\r\n" if "\r\n" in source else "\n")
    if source.count(needle) != 1:
        raise ValueError(f"Expected one method: {signature}")
    begin = source.index(needle)
    return begin, source.index(".end method", begin) + len(".end method")


def patch(source: bytes, edits: list[tuple[str, str, str, str]], inverse: bool = False) -> bytes:
    text = source.decode("utf-8")
    checked_methods: set[str] = set()
    for signature, method_sha, old, new in reversed(edits) if inverse else edits:
        before, after = (new, old) if inverse else (old, new)
        begin, end = method_span(text, signature)
        body = text[begin:end]
        if not inverse and signature not in checked_methods:
            if sha(body.encode("utf-8")) != method_sha:
                raise ValueError(f"R149 method differs: {signature}")
            checked_methods.add(signature)
        needle = re.compile(r"(\bconst\s+[vp]\d+,\s+)(-?0x[0-9a-f]+)")
        count = 0

        def replace(match: re.Match[str]) -> str:
            nonlocal count
            if int(match[2], 16) & 0xffffffff != int(before, 16):
                return match[0]
            count += 1
            return match[1] + signed(after)

        body = needle.sub(replace, body)
        if count != 1:
            raise ValueError(f"Expected one ARGB literal in {signature}, got {count}")
        text = text[:begin] + body + text[end:]
    return text.encode("utf-8")


def prepare(donor: Path, output: Path) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    patched: dict[tuple[str, str], bytes] = {}
    input_sha: dict[str, str] = {}
    for partition, classes in CHANGES.items():
        for kind, (expected_sha, edits) in classes.items():
            path = donor / partition.replace(".dex", "") / (kind[1:-1] + ".smali")
            raw = path.read_bytes()
            if sha(raw) != expected_sha:
                raise ValueError(f"Exact R149 class differs: {partition}/{kind}")
            result = patch(raw, edits)
            if patch(result, edits, inverse=True) != raw:
                raise ValueError(f"Full class inversion failed: {partition}/{kind}")
            patched[partition, kind] = result
            input_sha[f"{partition}/{kind}"] = expected_sha
    if sum(len(edits) for classes in CHANGES.values() for _, edits in classes.values()) != 10:
        raise ValueError("Exactly ten visual constants expected")
    output.mkdir(parents=True)
    output_sha = {}
    for (partition, kind), raw in patched.items():
        rel = Path(partition.replace(".dex", "")) / (kind[1:-1] + ".smali")
        target = output / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        output_sha[f"{partition}/{kind}"] = sha(raw)
    receipt = {
        "schema": "station.r150.visual.dex-literal-overlay.v1",
        "parentRevision": "R149",
        "parentDexSha256": DEX_SHA256,
        "inputClassSha256": input_sha,
        "outputClassSha256": output_sha,
        "changedClasses": 7,
        "changedArgbConstants": 10,
        "completeClassInversePassed": True,
        "unrelatedClassesIncluded": False,
        "gameplayNetworkOrDownloadLogicChanged": False,
        "newClassesFieldsMethods": 0,
        "compiled": False,
    }
    (output / "overlay-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor-smali", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.donor_smali, args.out), ensure_ascii=False))


if __name__ == "__main__":
    main()
