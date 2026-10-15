"""Patch only the unresolved PSX CAS call in the exact signed R168 DEX35.

No APK assembly, signing, server access, USB access or background service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import zipfile
import zlib

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
SESSION_SOURCE = REPO / "integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxSession.java"
SOURCE_SHA = "73fdcb47ad0472dd0f4a398020e647af8da5f82b4ab3af78dbbbb457be29288b"
DONOR_SHA = "875fb0696c4fb50ce4af953bccd62fcd68dfdecb247f65d2fc027b71aa330b3d"
DONOR_BYTES = 2_715_483_234
DONOR_DEX_SHA = "072ec067c3f61e8c9320683ed45dd37cb99b2e6f6851e841a53d6961f60672bc"
PARTITION = "classes35.dex"
ENTRY_COUNT = 13_861
DEX_COUNT = 40
PATCH_AT = 0x08BA82
BAD_BYTES = bytes.fromhex("71 30 ee 0f 92 0a")
GOOD_BYTES = bytes.fromhex("6e 30 1d 05 92 0a")
BAD_METHOD_ID = 0x0FEE
GOOD_METHOD_ID = 0x051D
SESSION_TYPE = "Lorg/emulationstation/frontend/netplay/StationPsxSession$Session;"
HELPER_TYPE = "Lorg/emulationstation/frontend/netplay/StationSinglePassVideo720$2$$ExternalSyntheticBackportWithForwarding0;"
BAD_METHOD = (HELPER_TYPE, "m", "(Ljava/util/concurrent/atomic/AtomicReference;Ljava/lang/Object;Ljava/lang/Object;)Z")
GOOD_METHOD = ("Ljava/util/concurrent/atomic/AtomicReference;", "compareAndSet",
               "(Ljava/lang/Object;Ljava/lang/Object;)Z")
SCHEMA = "station.psx.cas.dex.r169.v1"


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def uleb(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for count in range(5):
        part = data[offset + count]
        value |= (part & 0x7F) << (count * 7)
        if not part & 0x80:
            return value, offset + count + 1
    raise ValueError("Invalid DEX ULEB128")


class Dex:
    def __init__(self, data: bytes):
        self.data = data
        require(data[:8] == b"dex\n039\0" and read_u32(data, 32) == len(data),
                "Expected exact-size DEX 039")
        self.string_count = read_u32(data, 56)
        self.string_off = read_u32(data, 60)
        self.type_count = read_u32(data, 64)
        self.type_off = read_u32(data, 68)
        self.proto_count = read_u32(data, 72)
        self.proto_off = read_u32(data, 76)
        self.method_count = read_u32(data, 88)
        self.method_off = read_u32(data, 92)
        self.class_count = read_u32(data, 96)
        self.class_off = read_u32(data, 100)

    def string(self, index: int) -> str:
        require(0 <= index < self.string_count, "String index outside DEX")
        offset = read_u32(self.data, self.string_off + 4 * index)
        _, cursor = uleb(self.data, offset)
        end = self.data.index(0, cursor)
        return self.data[cursor:end].decode("ascii")

    def type(self, index: int) -> str:
        require(0 <= index < self.type_count, "Type index outside DEX")
        return self.string(read_u32(self.data, self.type_off + 4 * index))

    def proto(self, index: int) -> str:
        require(0 <= index < self.proto_count, "Proto index outside DEX")
        base = self.proto_off + 12 * index
        result = self.type(read_u32(self.data, base + 4))
        parameters_off = read_u32(self.data, base + 8)
        if parameters_off:
            count = read_u32(self.data, parameters_off)
            parameters = "".join(self.type(read_u16(self.data, parameters_off + 4 + 2 * i))
                                 for i in range(count))
        else:
            parameters = ""
        return "(" + parameters + ")" + result

    def method(self, index: int) -> tuple[str, str, str]:
        require(0 <= index < self.method_count, "Method index outside DEX")
        owner, proto, name = struct.unpack_from("<HHI", self.data, self.method_off + 8 * index)
        return self.type(owner), self.string(name), self.proto(proto)

    def defined_methods(self, owner: str) -> dict[int, int]:
        for index in range(self.class_count):
            base = self.class_off + 32 * index
            if self.type(read_u32(self.data, base)) != owner:
                continue
            cursor = read_u32(self.data, base + 24)
            require(cursor != 0, "Expected DEX class data for " + owner)
            static_fields, cursor = uleb(self.data, cursor)
            instance_fields, cursor = uleb(self.data, cursor)
            direct_methods, cursor = uleb(self.data, cursor)
            virtual_methods, cursor = uleb(self.data, cursor)
            for _ in range(static_fields + instance_fields):
                _, cursor = uleb(self.data, cursor)
                _, cursor = uleb(self.data, cursor)
            methods = {}
            for count in (direct_methods, virtual_methods):
                method_index = 0
                for _ in range(count):
                    difference, cursor = uleb(self.data, cursor)
                    method_index += difference
                    _, cursor = uleb(self.data, cursor)
                    code_off, cursor = uleb(self.data, cursor)
                    methods[method_index] = code_off
            return methods
        raise ValueError("Class definition absent: " + owner)

    def validate_header(self) -> None:
        require(self.data[12:32] == hashlib.sha1(self.data[32:]).digest(),
                "DEX SHA-1 header differs")
        require(read_u32(self.data, 8) == zlib.adler32(self.data[12:]) & 0xFFFFFFFF,
                "DEX Adler-32 header differs")


def verify_source(revision: str) -> None:
    require(bool(re.fullmatch(r"[0-9a-f]{40}", revision)),
            "Frozen 40-character source commit required")
    require(sha(SESSION_SOURCE) == SOURCE_SHA and
            "desired.compareAndSet(old,next)" in SESSION_SOURCE.read_text(encoding="utf-8"),
            "Reviewed PSX source identity differs")
    for path in (Path(__file__).resolve(), SESSION_SOURCE):
        relative = path.relative_to(REPO).as_posix()
        committed = subprocess.check_output(["git", "-C", str(REPO), "show", revision + ":" + relative])
        require(digest(committed) == sha(path), "Working source differs from frozen commit: " + relative)


def inspect(dex: Dex, expected_bytes: bytes) -> dict[str, object]:
    dex.validate_header()
    require(dex.method(BAD_METHOD_ID) == BAD_METHOD, "Broken method ID changed")
    require(dex.method(GOOD_METHOD_ID) == GOOD_METHOD, "Direct CAS method ID changed")
    helper = dex.defined_methods(HELPER_TYPE)
    require(BAD_METHOD_ID not in helper and
            any(dex.method(index)[1:] == ("m", "(Ljava/util/concurrent/atomic/AtomicReferenceArray;ILjava/lang/Object;Ljava/lang/Object;)Z")
                for index in helper),
            "Expected signature mismatch in synthetic helper differs")
    session = dex.defined_methods(SESSION_TYPE)
    methods = [(index, code_off) for index, code_off in session.items()
               if dex.method(index)[1:] == ("nativeControl", "(JZZ)V")]
    require(len(methods) == 1 and methods[0][1] != 0, "PSX nativeControl method changed")
    code_off = methods[0][1]
    instructions_start = code_off + 16
    instructions_end = instructions_start + 2 * read_u32(dex.data, code_off + 12)
    require(instructions_start <= PATCH_AT < PATCH_AT + len(expected_bytes) <= instructions_end and
            PATCH_AT % 2 == 0 and dex.data[PATCH_AT:PATCH_AT + len(expected_bytes)] == expected_bytes,
            "Pinned CAS invoke is outside PSX nativeControl or bytes differ")
    return {"sessionMethodId": methods[0][0], "sessionCodeOffset": code_off,
            "sessionInstructionRange": [instructions_start, instructions_end],
            "helperDefinedMethodIds": sorted(helper),
            "brokenMethodId": BAD_METHOD_ID, "directMethodId": GOOD_METHOD_ID}


def preflight(args: argparse.Namespace) -> tuple[bytes, list[str]]:
    require(args.out.resolve() != REPO and not args.out.resolve().is_relative_to(REPO),
            "Output must stay outside source worktree")
    require(not args.out.exists() or args.out.is_dir() and not any(args.out.iterdir()),
            "New or empty output directory required")
    require(args.donor.is_file() and args.donor.stat().st_size == DONOR_BYTES and
            sha(args.donor) == DONOR_SHA, "Exact signed R168 APK required")
    with zipfile.ZipFile(args.donor) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) == ENTRY_COUNT, "Donor ZIP entry set differs")
        partitions = sorted((name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)),
                            key=lambda item: int(item[7:-4]) if item != "classes.dex" else 1)
        require(partitions == ["classes.dex", *(f"classes{i}.dex" for i in range(2, DEX_COUNT + 1))],
                "Expected forty DEX partitions")
        raw = archive.read(PARTITION)
    require(digest(raw) == DONOR_DEX_SHA, "Exact R168 DEX35 required")
    return raw, partitions


def patch(args: argparse.Namespace) -> dict[str, object]:
    raw, partitions = preflight(args)
    before = Dex(raw)
    diagnosis = inspect(before, BAD_BYTES)
    if args.check_inputs_only:
        return {"passed": True, "patched": False, "diagnosis": diagnosis,
                "donorApkSha256": DONOR_SHA, "donorDexSha256": DONOR_DEX_SHA}
    verify_source(args.source_commit)
    candidate = bytearray(raw)
    candidate[PATCH_AT:PATCH_AT + len(BAD_BYTES)] = GOOD_BYTES
    candidate[12:32] = hashlib.sha1(candidate[32:]).digest()
    struct.pack_into("<I", candidate, 8, zlib.adler32(candidate[12:]) & 0xFFFFFFFF)
    patched = bytes(candidate)
    after = Dex(patched)
    inspect(after, GOOD_BYTES)
    non_header_diff = [i for i in range(32, len(raw)) if raw[i] != patched[i]]
    require(non_header_diff == [PATCH_AT, PATCH_AT + 2, PATCH_AT + 3],
            "Unexpected DEX body byte changed")
    require(len(patched) == len(raw) and patched.count(BAD_BYTES) == 0 and
            patched.count(GOOD_BYTES) >= 1, "CAS call replacement incomplete")
    verify_source(args.source_commit)
    require(sha(args.donor) == DONOR_SHA, "Donor changed during patch")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    dex_path = out / PARTITION
    dex_path.write_bytes(patched)
    require(sha(dex_path) == digest(patched), "Written DEX differs")
    receipt = {
        "schema": SCHEMA, "passed": True, "sourceCommit": args.source_commit,
        "sourceSha256": SOURCE_SHA, "donorApkSha256": DONOR_SHA,
        "donorDexSha256": DONOR_DEX_SHA, "candidateDexSha256": digest(patched),
        "partition": PARTITION, "dexVersion": "039", "dexLength": len(patched),
        "dexPartitionsInDonor": partitions, "changedDexPartitions": [PARTITION],
        "diagnosis": diagnosis,
        "instructionOffset": PATCH_AT, "instructionBefore": BAD_BYTES.hex(),
        "instructionAfter": GOOD_BYTES.hex(), "nonHeaderChangedOffsets": non_header_diff,
        "sha1AndAdler32Regenerated": True, "classDefinitionsChanged": False,
        "newThreadsTimersOrPolling": False, "apkAssembled": False,
        "signed": False, "installed": False, "serverRegistered": False,
        "physicalGameplayValidated": False,
    }
    (out / "dex-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {"passed": True, "candidateDexSha256": receipt["candidateDexSha256"],
            "nonHeaderChangedOffsets": non_header_diff, "apkAssembled": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--check-inputs-only", action="store_true")
    print(json.dumps(patch(parser.parse_args()), sort_keys=True))
