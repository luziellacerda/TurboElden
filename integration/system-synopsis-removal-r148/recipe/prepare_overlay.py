"""Prepare the single native header change that hides platform descriptions.

The R147 carousel includes the historical R132 information header. This recipe
does not edit that private input, assemble an APK, or change game synopses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


INPUT_SHA256 = "e6c910b188018146a394ff2128f9f82144afcbe46d0bd3924d09b200661c5c75"
ORIGINAL = b'  heading=info?info->title:key;body=info?info->description:"";'
REPLACEMENT = b'  heading=info?info->title:key;body="";'
GAME_GUARD = b'  body=stationSynopsisChoose(serverDescription,heading,'
FOLDER_GUARD = b'  heading=strData(folderItems+index*0xe8+0x18);describeFolder(index,folderText,sizeof(folderText));body=folderText;'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare(source: Path, output: Path) -> dict[str, object]:
    before = source.read_bytes()
    if sha256(before) != INPUT_SHA256:
        raise ValueError("R132 native information header differs from the R147 input")
    if before.count(ORIGINAL) != 1 or before.count(GAME_GUARD) != 1 or before.count(FOLDER_GUARD) != 1:
        raise ValueError("Platform, game or collection synopsis anchor differs")
    after = before.replace(ORIGINAL, REPLACEMENT, 1)
    if after.replace(REPLACEMENT, ORIGINAL, 1) != before:
        raise ValueError("The one-line change does not invert to the exact original")
    if after.count(GAME_GUARD) != 1 or after.count(FOLDER_GUARD) != 1:
        raise ValueError("Game and collection synopsis paths must remain intact")
    output.mkdir(parents=True, exist_ok=False)
    target = output / "r132_native_info.h"
    target.write_bytes(after)
    receipt = {
        "schema": "station.r148.platform-synopsis-overlay.v1",
        "parentRevision": "R147",
        "parentCarouselSha256": "2e15a9a330c2562c71574921f5558d6142e3051bba64a315434e5714f38908a9",
        "inputHeaderSha256": INPUT_SHA256,
        "outputHeaderSha256": sha256(after),
        "changedLines": 1,
        "systemsDescriptionDisplayed": False,
        "systemTitleAndActionPreserved": True,
        "gameAndCollectionSynopsesPreserved": True,
        "nativeCompiled": False,
        "apkProduced": False,
        "installed": False,
    }
    (output / "overlay-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r132-native-info", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="New directory for the include overlay")
    args = parser.parse_args()
    print(json.dumps(prepare(args.r132_native_info, args.out), ensure_ascii=False))


if __name__ == "__main__":
    main()
