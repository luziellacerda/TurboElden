"""Permit background mode 3 in the existing atomic graphics bridge.

The single AArch64 compare implements `background > 2` in the R151 frontend.
Changing its immediate to 3 admits the new presentation mode while retaining
the mask, revision, publication, errors, ABI and every other instruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


BASE_SHA = "4e7ad58e1e8f8a284654120c27280eed8c124ad5301a9e87d769e41f100d8d0d"
OFFSET = 0x2257C
BEFORE = bytes.fromhex("7f080071")  # cmp w3, #2
AFTER = bytes.fromhex("7f0c0071")   # cmp w3, #3
SYMBOL = "Java_org_emulationstation_frontend_station_StationFrontend_publishGraphics"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--objdump", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    with zipfile.ZipFile(args.apk) as archive:
        original = archive.read("lib/arm64-v8a/libstation_frontend.so")
    if sha(original) != BASE_SHA or original[OFFSET:OFFSET + 4] != BEFORE:
        raise ValueError("Exact R151 graphics bridge required")
    args.out.mkdir(parents=True)
    before_path = args.out / "frontend-r151.so"
    after_path = args.out / "libstation_frontend.so"
    before_path.write_bytes(original)
    changed = original[:OFFSET] + AFTER + original[OFFSET + 4:]
    if changed[:OFFSET] + BEFORE + changed[OFFSET + 4:] != original:
        raise ValueError("Bridge patch is not byte reversible")
    after_path.write_bytes(changed)
    disassembly = subprocess.check_output(
        [str(args.objdump), "-d", "--disassemble-symbols=" + SYMBOL, str(after_path)],
        text=True, timeout=60)
    if "2657c: 71000c7f" not in disassembly or "cmp\tw3, #0x3" not in disassembly:
        raise ValueError("Updated instruction is not cmp w3, #3")
    receipt = {
        "schema": "station.r152.graphics-bridge.mode3.v1",
        "passed": True,
        "inputSha256": BASE_SHA,
        "outputSha256": sha(changed),
        "changedByteOffsets": [OFFSET + 1],
        "originalInstruction": "cmp w3, #2",
        "updatedInstruction": "cmp w3, #3",
        "inverseByteExact": True,
        "changedFileBytes": 1,
        "installed": False,
    }
    (args.out / "frontend-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", "utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
