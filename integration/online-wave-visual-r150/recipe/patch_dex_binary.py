"""Patch ten scoped R150 ARGB const/31i immediates in the signed R149 DEX.

Locates classes and methods through DEX tables. It changes four immediate bytes
per literal, recalculates DEX SHA-1/Adler-32, and proves a byte-exact inverse.
The reviewed smali overlay is a separate oracle for class/method/value scope.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import zipfile
import zlib

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PARSER = REPO / "integration/dolphin-onpause-r149/recipe/patch_dex.py"
SCOPE = HERE / "prepare_dex_color_overlay.py"
PARSER_SHA = "ac7ca5ae1a7638d213c5f37a102aaffe4690fbe51e562aca09777256267fa5dc"
SCOPE_SHA = "0cc778aac0d5550757cd2f08fff4fe1fda0a915d62020d4f07d90e4822f700ec"
INSTRUCTION_VERIFIER = HERE / "VerifyR150Const31i.java"
INSTRUCTION_VERIFIER_SHA = "28d999264088e2c54a0c77c8f67c0491fd1683a025f10894c4f500997afb8f8f"
TOOL_SHA = {
    "java": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "apktool": "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",
}
BASE_SHA = "698e8a7914cc7be2facc00e6701ff1f3533fa13f763358b51578a35d25c2741e"
BASE_SIZE = 2_715_089_935
PINNED_R149 = {
    "classes10.dex": "1f1b285af161fbf85573c081bee3bc6e4c95f90485d8d405ae064b86feb9144e",
    "lib/arm64-v8a/libturbo_carousel.so": "313de078f8c300b6c7944de2ce03292de697532bc1a493b7406fdbb8260fbd28",
    "lib/arm64-v8a/libmain.so": "62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6",
    "assets/station-online/engines.json": "3ee79e1ab9d55a0f043e2ad3c90e354667f06604ef5b34b8a1493f08786d9089",
    "lib/arm64-v8a/libstation_psx_online.so": "29c3d7b9e6a801db7be37caef35a1b20b5c7c94eabc3493788a07dbb40965f65",
    "lib/arm64-v8a/libstation_mupen64plus_runtime.so": "dcad075758e57caea6d94557318d03c7f834801419fa00a576f857ecaaaad5d0",
    "lib/arm64-v8a/libstation_dolphin_runtime.so": "c80ec04d17233ea3aa228b1bef6091141cfa660f3eb0f97a98d2942eaeaed946",
}


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Pinned DEX helper missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def helpers(java: Path, apktool: Path):
    need(sha(PARSER) == PARSER_SHA and sha(SCOPE) == SCOPE_SHA and
         sha(INSTRUCTION_VERIFIER) == INSTRUCTION_VERIFIER_SHA,
         "Reviewed DEX parsers or R150 visual oracle changed")
    need(sha(java) == TOOL_SHA["java"] and sha(apktool) == TOOL_SHA["apktool"],
         "Pinned JDK17 and dexlib2 tool required")
    parser = load(PARSER, "r150_dex_tables")
    scope = load(SCOPE, "r150_visual_scope")
    need(set(scope.DEX_SHA256) == {"classes28.dex", "classes35.dex", "classes40.dex"} and
         sum(len(edits) for classes in scope.CHANGES.values() for _, edits in classes.values()) == 10 and
         sum(len(classes) for classes in scope.CHANGES.values()) == 7,
         "Exactly three partitions, seven classes and ten literals required")
    return parser, scope


def decoded_consts(raw: bytes, identities: set[str], java: Path, apktool: Path) -> tuple[dict, dict]:
    """Use dexlib2 instruction iteration as an independent boundary oracle."""
    need(identities and all("|" in identity for identity in identities),
         "Nonempty exact method targets required")
    command = [str(java), "--class-path", str(apktool), str(INSTRUCTION_VERIFIER),
               digest(raw), *sorted(identities)]
    result = subprocess.run(command, input=raw, capture_output=True, timeout=180)
    need(result.returncode == 0,
         "Dexlib2 instruction walk rejected DEX: " + result.stderr.decode("utf-8", "replace")[-1200:])
    methods, instructions, done = {}, {}, None
    for line in result.stdout.decode("utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0] == "M":
            _, identity, code_offset = parts
            need(identity in identities and identity not in methods,
                 "Dexlib2 duplicate/unexpected method")
            methods[identity] = int(code_offset)
            instructions[identity] = []
        elif len(parts) == 5 and parts[0] == "I":
            _, identity, opcode_offset, register, literal = parts
            need(identity in methods, "Dexlib2 const without target method")
            instructions[identity].append({"opcodeOffset": int(opcode_offset),
                                           "register": int(register),
                                           "literal": int(literal)})
        elif len(parts) == 2 and parts[0] == "DONE":
            need(done is None, "Dexlib2 duplicate completion")
            done = int(parts[1])
        else:
            raise ValueError("Unexpected dexlib2 verifier output")
    need(set(methods) == identities and done == len(identities) and
         all(len({row["opcodeOffset"] for row in rows}) == len(rows)
             for rows in instructions.values()),
         "Dexlib2 method/instruction inventory differs")
    return methods, instructions


def header(raw: bytes | bytearray, parser) -> None:
    need(raw[:8] == b"dex\n039\0" and len(raw) == parser.u32(raw, 0x20) and
         parser.u32(raw, 0x24) == 0x70 and parser.u32(raw, 0x28) == 0x12345678,
         "Unexpected DEX header")
    need(raw[12:32] == hashlib.sha1(raw[32:]).digest() and
         parser.u32(raw, 8) == zlib.adler32(raw[12:]) & 0xffffffff,
         "DEX header signature/checksum invalid")
    for count_offset, unit in ((0x38, 4), (0x40, 4), (0x48, 12), (0x58, 8), (0x60, 32)):
        count, offset = parser.u32(raw, count_offset), parser.u32(raw, count_offset + 4)
        need(count > 0 and 0x70 <= offset <= len(raw) - count * unit,
             "DEX ID/class table out of bounds")


def method_code(raw: bytes, parser, owner: str, method: str) -> tuple[int, bytes]:
    table = parser.u32(raw, 0x64)
    rows = [table + index * 32 for index in range(parser.u32(raw, 0x60))
            if parser.type_name(raw, parser.u32(raw, table + index * 32)) == owner]
    need(len(rows) == 1, "Exactly one target DEX class required: " + owner)
    matches = []
    name, proto = method.split("(", 1)
    proto = "(" + proto
    for category, index, _, _, code_off, _ in parser.class_methods(raw, parser.u32(raw, rows[0] + 24)):
        if parser.method_identity(raw, index) == (owner, name, proto):
            matches.append((category, code_off))
    need(len(matches) == 1 and matches[0][1] > 0,
         "Exactly one concrete target method required: " + owner + "->" + method)
    code_off = matches[0][1]
    size = parser.u32(raw, code_off + 12)
    begin, end = code_off + 16, code_off + 16 + 2 * size
    need(size > 0 and end <= len(raw), "Target DEX code item out of bounds")
    return code_off, raw[begin:end]


def oracle_check(oracle_dir: Path, scope) -> dict[str, str]:
    receipt_path = oracle_dir / "overlay-receipt.json"
    receipt = json.loads(receipt_path.read_text("utf-8"))
    need(receipt.get("schema") == "station.r150.visual.dex-literal-overlay.v1" and
         receipt.get("parentRevision") == "R149" and
         receipt.get("parentDexSha256") == scope.DEX_SHA256 and
         receipt.get("changedClasses") == 7 and receipt.get("changedArgbConstants") == 10 and
         receipt.get("completeClassInversePassed") is True and
         receipt.get("unrelatedClassesIncluded") is False and
         receipt.get("newClassesFieldsMethods") == 0,
         "Direct R149 smali oracle receipt invalid")
    result = {}
    for partition, classes in scope.CHANGES.items():
        for owner, (_, edits) in classes.items():
            key = partition + "/" + owner
            path = oracle_dir / partition.replace(".dex", "") / (owner[1:-1] + ".smali")
            raw = path.read_bytes()
            need(digest(raw) == receipt["outputClassSha256"][key],
                 "Visual smali oracle class hash differs: " + key)
            text = raw.decode("utf-8")
            for signature, _, old, new in edits:
                start, end = scope.method_span(text, signature)
                body = text[start:end]
                const_values = [int(value, 16) & 0xffffffff for value in
                                re.findall(r"\bconst\s+[vp]\d+,\s+(-?0x[0-9a-f]+)", body)]
                need(const_values.count(int(new, 16)) == 1 and
                     const_values.count(int(old, 16)) == 0,
                     "Visual smali oracle literal differs: " + key + " " + signature)
            result[key] = digest(raw)
    need(set(result) == set(receipt["outputClassSha256"]), "Unexpected smali oracle class scope")
    return result


def patch_partition(raw: bytes, partition: str, parser, scope,
                    java: Path, apktool: Path) -> tuple[bytes, dict]:
    need(digest(raw) == scope.DEX_SHA256[partition], "Exact R149 DEX partition required: " + partition)
    header(raw, parser)
    identities = {owner + "|" + signature.split()[-1]
                  for owner, (_, changes) in scope.CHANGES[partition].items()
                  for signature, _, _, _ in changes}
    methods_before, decoded_before = decoded_consts(raw, identities, java, apktool)
    expected_after = {identity: [dict(row) for row in rows]
                      for identity, rows in decoded_before.items()}
    changed = bytearray(raw)
    edits = []
    allowed = set(range(8, 32))
    for owner, (_, changes) in scope.CHANGES[partition].items():
        for signature, _, old, new in changes:
            method = signature.split()[-1]
            identity = owner + "|" + method
            code_off, instructions = method_code(raw, parser, owner, method)
            need(methods_before[identity] == code_off,
                 "Python DEX table and dexlib2 method code offset disagree")
            old_u, new_u = int(old, 16) & 0xffffffff, int(new, 16) & 0xffffffff
            hits = [row for row in decoded_before[identity] if row["literal"] == old_u]
            need(len(hits) == 1, "Unique decoded const/31i target required: " + identity)
            opcode_off = hits[0]["opcodeOffset"]
            relative = opcode_off - (code_off + 16)
            need(relative >= 0 and relative % 2 == 0 and relative + 6 <= len(instructions) and
                 instructions[relative] == 0x14 and
                 instructions[relative + 1] == hits[0]["register"] and
                 struct.unpack_from("<I", instructions, relative + 2)[0] == old_u,
                 "Dexlib2 boundary/register/literal differs from raw code item")
            literal_off = opcode_off + 2
            need(changed[opcode_off:opcode_off + 2] == raw[opcode_off:opcode_off + 2] and
                 struct.unpack_from("<I", changed, literal_off)[0] == old_u,
                 "Target const/31i instruction changed during patch")
            struct.pack_into("<I", changed, literal_off, new_u)
            replacement = [row for row in expected_after[identity]
                           if row["opcodeOffset"] == opcode_off]
            need(len(replacement) == 1 and replacement[0]["literal"] == old_u and
                 replacement[0]["register"] == hits[0]["register"],
                 "Duplicate or inconsistent decoded instruction target")
            replacement[0]["literal"] = new_u
            allowed.update(range(literal_off, literal_off + 4))
            edits.append({"class": owner, "method": method, "codeOffset": code_off,
                          "opcodeOffset": opcode_off, "literalOffset": literal_off,
                          "register": hits[0]["register"], "dexlib2BoundaryVerified": True,
                          "oldArgb": old, "newArgb": new})
    changed[12:32] = hashlib.sha1(changed[32:]).digest()
    struct.pack_into("<I", changed, 8, zlib.adler32(changed[12:]) & 0xffffffff)
    header(changed, parser)
    methods_after, decoded_after = decoded_consts(bytes(changed), identities, java, apktool)
    need(methods_after == methods_before and decoded_after == expected_after,
         "Dexlib2 changed instruction inventory, boundary, register or another literal")
    positions = [index for index, pair in enumerate(zip(raw, changed)) if pair[0] != pair[1]]
    need(set(positions) <= allowed and all(any(offset in positions for offset in range(row["literalOffset"], row["literalOffset"] + 4))
                                         for row in edits) and len(raw) == len(changed),
         "DEX changed outside ten scoped immediates and header bytes")
    inverse = bytearray(changed)
    for row in edits:
        struct.pack_into("<I", inverse, row["literalOffset"], int(row["oldArgb"], 16) & 0xffffffff)
    inverse[12:32] = hashlib.sha1(inverse[32:]).digest()
    struct.pack_into("<I", inverse, 8, zlib.adler32(inverse[12:]) & 0xffffffff)
    need(inverse == raw, "R150 DEX binary inverse did not restore R149 byte for byte")
    for row in edits:
        code_off, _ = method_code(changed, parser, row["class"], row["method"])
        need(code_off == row["codeOffset"] and changed[row["opcodeOffset"]:row["opcodeOffset"] + 2] ==
             raw[row["opcodeOffset"]:row["opcodeOffset"] + 2] and
             struct.unpack_from("<I", changed, row["literalOffset"])[0] == int(row["newArgb"], 16),
             "Post-patch method/code/opcode mismatch")
    result = {"sourceSha256": digest(raw), "outputSha256": digest(changed),
              "bytes": len(changed), "changedByteOffsets": positions,
              "immediates": edits, "inverseByteExact": True,
              "dexlib2InstructionBoundariesVerified": True,
              "sameRegistersAndOtherInstructions": True,
              "allOtherDexBytesPreserved": True}
    return bytes(changed), result


def inspect(base_apk: Path, oracle_dir: Path,
            java: Path, apktool: Path) -> tuple[dict[str, bytes], dict]:
    java, apktool = java.resolve(strict=True), apktool.resolve(strict=True)
    parser, scope = helpers(java, apktool)
    base = base_apk.resolve(strict=True)
    need(base.stat().st_size == BASE_SIZE and sha(base) == BASE_SHA,
         "Exact signed R149 APK required")
    oracle = oracle_check(oracle_dir.resolve(strict=True), scope)
    output, records = {}, {}
    with zipfile.ZipFile(base) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13860,
             "R149 archive entry inventory differs")
        need(all(digest(archive.read(name)) == checksum for name, checksum in PINNED_R149.items()),
             "R149 functional entry or libmain changed")
        for partition in sorted(scope.DEX_SHA256):
            output[partition], records[partition] = patch_partition(
                archive.read(partition), partition, parser, scope, java, apktool)
    need(sum(len(row["immediates"]) for row in records.values()) == 10,
         "Exactly ten binary DEX immediates must change")
    receipt = {"schema": "station.r150.visual.binary-dex.v1", "revision": "R150",
               "passed": True, "baseApkSha256": BASE_SHA,
               "r149FunctionalEntrySha256": PINNED_R149,
               "r150SmaliOracleClassSha256": oracle,
               "scopeSourceSha256": SCOPE_SHA, "dexParserSourceSha256": PARSER_SHA,
               "dexlib2VerifierSourceSha256": INSTRUCTION_VERIFIER_SHA,
               "dexlib2ToolSha256": TOOL_SHA,
               "partitionProofs": records, "changedDex": sorted(output),
               "changedArgbConstants": 10, "inverseByteExact": True,
               "dexlib2InstructionBoundariesVerified": True,
               "dex10Preserved": True, "originalEngineIdsPreservedInDexStep": True,
               "apkCompiled": False, "installed": False}
    return output, receipt


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--base-apk", type=Path, required=True)
    cli.add_argument("--oracle-dir", type=Path, required=True)
    cli.add_argument("--java", type=Path, required=True)
    cli.add_argument("--apktool", type=Path, required=True)
    cli.add_argument("--inspect", action="store_true")
    cli.add_argument("--out-dir", type=Path)
    args = cli.parse_args()
    need(args.inspect != (args.out_dir is not None), "Use --inspect or --out-dir")
    output, proof = inspect(args.base_apk, args.oracle_dir, args.java, args.apktool)
    if args.inspect:
        print(json.dumps(proof, ensure_ascii=False))
        return
    target = args.out_dir.resolve()
    need(not target.exists(), "Fresh R150 DEX output required")
    target.mkdir(parents=True)
    for partition, raw in output.items():
        path = target / partition
        path.write_bytes(raw)
        need(sha(path) == proof["partitionProofs"][partition]["outputSha256"],
             "DEX writeback differs: " + partition)
    with (target / "binary-dex-proof.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(proof, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"revision": "R150", "passed": True,
                      "changedDex": sorted(output), "changedArgbConstants": 10,
                      "inverseByteExact": True}))


if __name__ == "__main__":
    main()
