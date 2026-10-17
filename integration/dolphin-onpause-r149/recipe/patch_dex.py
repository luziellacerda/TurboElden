"""Patch exactly two onPause access flags in classes10.dex from signed R148.

The encoded ULEB128 values are one byte each, so code items, offsets, and every
other DEX byte remain in place. Recalculate only the standard DEX header digest
and checksum; prove that reversing the flags restores the original partition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile
import zlib

BASE_SHA = "c8b8c30cac7d36ec2a8ca8d470542096919435c749dede535cd0d58648e00dc1"
BASE_SIZE = 2_715_089_935
DEX_NAME = "classes10.dex"
DEX_SHA = "4d200405747b4d42108fe6bd8afdccc290db3fa1a72a9aa28c779f8772a53a78"
DEX_SIZE = 6_357_400
TARGETS = {
    "Ltdolphin/fragment/app/FragmentActivity;": (0x11, 0x01),
    "Lorg/dolphinemu/dolphinemu/activities/EmulationActivity;": (0x04, 0x01),
}
INTERMEDIATE = "Ltdolphin/appcompat/app/AppCompatActivity;"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def u32(raw: bytes | bytearray, offset: int) -> int:
    need(0 <= offset <= len(raw) - 4, "DEX u32 out of bounds")
    return struct.unpack_from("<I", raw, offset)[0]


def uleb(raw: bytes | bytearray, offset: int) -> tuple[int, int]:
    value = 0
    for index in range(5):
        need(offset + index < len(raw), "Truncated DEX ULEB128")
        byte = raw[offset + index]
        value |= (byte & 0x7f) << (7 * index)
        if not byte & 0x80:
            need(value <= 0xffffffff, "DEX ULEB128 overflow")
            return value, offset + index + 1
    raise ValueError("DEX ULEB128 longer than five bytes")


def dex_header(raw: bytes | bytearray) -> None:
    need(len(raw) == DEX_SIZE and raw[:8] == b"dex\n039\0", "Unexpected DEX10 format or length")
    need(u32(raw, 0x20) == len(raw) and u32(raw, 0x24) == 0x70 and
         u32(raw, 0x28) == 0x12345678, "DEX10 file size, header or endian tag differs")
    need(raw[12:32] == hashlib.sha1(raw[32:]).digest(), "DEX10 SHA-1 signature invalid")
    need(u32(raw, 8) == zlib.adler32(raw[12:]) & 0xffffffff, "DEX10 Adler32 checksum invalid")
    expected = {0x38: 35712, 0x40: 6308, 0x48: 7277, 0x58: 31292, 0x60: 4991}
    need(all(u32(raw, offset) == count for offset, count in expected.items()),
         "DEX10 string/type/proto/method/class inventory differs")
    for size_offset, unit in ((0x38, 4), (0x40, 4), (0x48, 12), (0x58, 8), (0x60, 32)):
        size, location = u32(raw, size_offset), u32(raw, size_offset + 4)
        need(size > 0 and 0x70 <= location <= len(raw) - size * unit,
             "DEX10 ID or class table out of bounds")


def dex_string(raw: bytes | bytearray, index: int) -> str:
    need(0 <= index < u32(raw, 0x38), "DEX string index out of bounds")
    offset = u32(raw, u32(raw, 0x3c) + index * 4)
    _, start = uleb(raw, offset)
    end = raw.find(b"\0", start)
    need(start <= end < len(raw), "Unterminated DEX string")
    value = raw[start:end]
    need(all(byte < 0x80 for byte in value), "Target DEX descriptor or method name not ASCII")
    return value.decode("ascii")


def type_name(raw: bytes | bytearray, index: int) -> str:
    need(0 <= index < u32(raw, 0x40), "DEX type index out of bounds")
    return dex_string(raw, u32(raw, u32(raw, 0x44) + index * 4))


def proto_name(raw: bytes | bytearray, index: int) -> str:
    need(0 <= index < u32(raw, 0x48), "DEX proto index out of bounds")
    offset = u32(raw, 0x4c) + index * 12
    result = type_name(raw, u32(raw, offset + 4))
    params = u32(raw, offset + 8)
    if params == 0:
        return "()" + result
    count = u32(raw, params)
    need(count < 100 and params + 4 + count * 2 <= len(raw), "DEX proto parameters out of bounds")
    args = [type_name(raw, struct.unpack_from("<H", raw, params + 4 + 2 * item)[0])
            for item in range(count)]
    return "(" + "".join(args) + ")" + result


def method_identity(raw: bytes | bytearray, index: int) -> tuple[str, str, str]:
    need(0 <= index < u32(raw, 0x58), "DEX method index out of bounds")
    offset = u32(raw, 0x5c) + index * 8
    class_idx, proto_idx, name_idx = struct.unpack_from("<HHI", raw, offset)
    return type_name(raw, class_idx), dex_string(raw, name_idx), proto_name(raw, proto_idx)


def class_methods(raw: bytes | bytearray, class_data_off: int):
    need(0 < class_data_off < len(raw), "Target DEX class data missing")
    offset = class_data_off
    counts = []
    for _ in range(4):
        count, offset = uleb(raw, offset)
        need(count <= u32(raw, 0x58), "DEX class member count invalid")
        counts.append(count)
    for count in counts[:2]:
        for _ in range(count):
            _, offset = uleb(raw, offset)
            _, offset = uleb(raw, offset)
    for category, count in (("direct", counts[2]), ("virtual", counts[3])):
        method_idx = 0
        for _ in range(count):
            diff, offset = uleb(raw, offset)
            method_idx += diff
            flag_offset = offset
            flags, offset = uleb(raw, offset)
            flag_span = offset - flag_offset
            code_off, offset = uleb(raw, offset)
            need(code_off == 0 or code_off < len(raw), "DEX code item offset out of bounds")
            yield category, method_idx, flag_offset, flags, code_off, flag_span


def locate(raw: bytes | bytearray) -> dict[str, dict]:
    found = {}
    table = u32(raw, 0x64)
    for index in range(u32(raw, 0x60)):
        row = table + index * 32
        owner = type_name(raw, u32(raw, row))
        if owner not in TARGETS:
            continue
        need(owner not in found, "Duplicate target DEX class")
        matches = []
        for category, method_idx, flag_offset, flags, code_off, flag_span in class_methods(raw, u32(raw, row + 24)):
            identity = method_identity(raw, method_idx)
            if identity == (owner, "onPause", "()V"):
                matches.append({"class": owner, "method": "onPause()V", "category": category,
                                "methodIndex": method_idx, "flags": flags,
                                "flagOffset": flag_offset, "flagEncodedBytes": flag_span,
                                "codeOffset": code_off})
        need(len(matches) == 1, "Exactly one onPause()V target required: " + owner)
        found[owner] = matches[0]
    need(set(found) == set(TARGETS), "Both target DEX classes required")
    return found


def dispatch_chain(raw: bytes | bytearray) -> list[str]:
    """Resolve the actual child→parent chain from class_defs, not class indices."""
    wanted = {*TARGETS, INTERMEDIATE}
    definitions = {}
    table = u32(raw, 0x64)
    for index in range(u32(raw, 0x60)):
        row = table + index * 32
        owner = type_name(raw, u32(raw, row))
        if owner in wanted:
            need(owner not in definitions, "Duplicate dispatch-chain class")
            definitions[owner] = (type_name(raw, u32(raw, row + 8)), u32(raw, row + 24))
    need(set(definitions) == wanted, "Complete onPause inheritance chain required")
    child = "Lorg/dolphinemu/dolphinemu/activities/EmulationActivity;"
    base = "Ltdolphin/fragment/app/FragmentActivity;"
    need(definitions[child][0] == INTERMEDIATE and definitions[INTERMEDIATE][0] == base,
         "EmulationActivity must inherit FragmentActivity through AppCompatActivity")
    middle_onpause = [method_identity(raw, index) for _, index, _, _, _, _
                      in class_methods(raw, definitions[INTERMEDIATE][1])
                      if method_identity(raw, index) == (INTERMEDIATE, "onPause", "()V")]
    need(not middle_onpause, "Intermediate AppCompatActivity must not declare onPause()V")
    return [child, INTERMEDIATE, base]


def patch(raw: bytes) -> tuple[bytes, dict]:
    need(digest(raw) == DEX_SHA, "Exact signed R148 DEX10 partition required")
    dex_header(raw)
    before = locate(raw)
    chain = dispatch_chain(raw)
    changed = bytearray(raw)
    for owner, (old_flags, new_flags) in TARGETS.items():
        method = before[owner]
        need(method["category"] == "virtual" and method["flags"] == old_flags and
             method["flagEncodedBytes"] == 1 and method["codeOffset"] != 0 and
             changed[method["flagOffset"]] == old_flags,
             "Target method layout or original flags differ: " + owner)
        changed[method["flagOffset"]] = new_flags
    changed[12:32] = hashlib.sha1(changed[32:]).digest()
    struct.pack_into("<I", changed, 8, zlib.adler32(changed[12:]) & 0xffffffff)
    dex_header(changed)
    after = locate(changed)
    need(dispatch_chain(changed) == chain,
         "Dispatch inheritance chain changed")
    for owner, (_, new_flags) in TARGETS.items():
        need(after[owner] == {**before[owner], "flags": new_flags},
             "Target method changed beyond access flags: " + owner)
    positions = [index for index, pair in enumerate(zip(raw, changed)) if pair[0] != pair[1]]
    allowed = set(range(8, 32)) | {value["flagOffset"] for value in before.values()}
    need(set(positions) <= allowed and all(value["flagOffset"] in positions for value in before.values()) and
         len(raw) == len(changed), "DEX changed outside two method flags and header integrity bytes")
    reversed_dex = bytearray(changed)
    for owner, (old_flags, _) in TARGETS.items():
        reversed_dex[before[owner]["flagOffset"]] = old_flags
    reversed_dex[12:32] = hashlib.sha1(reversed_dex[32:]).digest()
    struct.pack_into("<I", reversed_dex, 8, zlib.adler32(reversed_dex[12:]) & 0xffffffff)
    need(reversed_dex == raw, "Inverse DEX patch did not restore R148 byte for byte")
    proof = {"schema": "station.r149.dolphin-onpause-dex.v1", "revision": "R149",
             "passed": True, "sourceDexSha256": DEX_SHA, "sourceDexBytes": DEX_SIZE,
             "outputDexSha256": digest(changed), "outputDexBytes": len(changed),
             "changedByteOffsets": positions, "allowedHeaderOffsets": list(range(8, 32)),
             "methodsBefore": before, "methodsAfter": after, "inverseExact": True,
             "dispatchChainChildToParent": chain, "intermediateDeclaresOnPause": False,
             "codeAndOtherDexBytesPreserved": True}
    return bytes(changed), proof


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-apk", required=True, type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    need(args.inspect != (args.out_dir is not None), "Use --inspect or --out-dir")
    base = args.base_apk.resolve(strict=True)
    need(base.stat().st_size == BASE_SIZE and sha(base) == BASE_SHA,
         "Exact signed R148 APK required")
    with zipfile.ZipFile(base) as archive:
        raw = archive.read(DEX_NAME)
    output, proof = patch(raw)
    proof["sourceApkSha256"] = BASE_SHA
    if args.inspect:
        print(json.dumps(proof, ensure_ascii=False))
        return
    target = args.out_dir.resolve()
    need(not target.exists(), "Fresh DEX output directory required")
    target.mkdir(parents=True)
    dex_path = target / DEX_NAME
    dex_path.write_bytes(output)
    need(sha(dex_path) == proof["outputDexSha256"], "Patched DEX writeback differs")
    with (target / "dex-patch-proof.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(proof, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"revision": "R149", "passed": True,
                      "dexSha256": proof["outputDexSha256"],
                      "changedByteCount": len(proof["changedByteOffsets"])}))


if __name__ == "__main__":
    main()
