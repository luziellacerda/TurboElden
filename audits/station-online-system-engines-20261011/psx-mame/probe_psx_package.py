"""Read-only ABI/provenance probe. It never runs or patches an emulator.

The guards apply only to the exact packaged R126 normal frontend/core. They
do not constitute a netplay adapter, Android boot test, or determinism test.
Only public aggregate facts are written; no APK entries or personal paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile


EXPECTED = {
    "libmain.so": (4588272, "62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6"),
    "libpcsx_rearmed_libretro_android.so": (1582960, "e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9"),
    "libstation_online_pcsx.so": (1547280, "4de0afbd3bb113a4b9927b5b250860194b485f278d1dced81501dc6555fa18a8"),
    "libMAME4droid.so": (366992944, "ab587eec36db170387baa743d1078912927d6b9c0e2fe8057d56225739d62d71"),
    "libmame4droid-jni.so": (32856, "a7dea2fc4fb73a7a57fccb5ffc2dca3faf53ac11b7f54b1337b04da09edaf108"),
}


class Elf:
    def __init__(self, data: bytes):
        if data[:6] != b"\x7fELF\x02\x01":
            raise ValueError("Expected little-endian ELF64")
        if struct.unpack_from("<H", data, 18)[0] != 183:
            raise ValueError("Expected AArch64 ELF")
        self.data = data
        self.loads = []
        po = struct.unpack_from("<Q", data, 32)[0]
        es, count = struct.unpack_from("<HH", data, 54)
        for i in range(count):
            typ, _, off, va, _, size, _, _ = struct.unpack_from("<IIQQQQQQ", data, po + i * es)
            if typ == 1:
                self.loads.append((va, off, size))

    def at(self, va: int, size: int) -> bytes:
        for start, off, length in self.loads:
            if start <= va and va + size <= start + length:
                return self.data[off + va - start:off + va - start + size]
        raise ValueError("Address outside file-backed PT_LOAD")

    def text(self, va: int) -> str:
        value = self.at(va, 120).split(b"\x00", 1)[0]
        return value.decode("utf-8")

    def symbols(self) -> dict[str, int]:
        so = struct.unpack_from("<Q", self.data, 40)[0]
        es, count = struct.unpack_from("<HH", self.data, 58)
        sections = [struct.unpack_from("<IIQQQQIIQQ", self.data, so + i * es) for i in range(count)]
        found = {}
        for sec in sections:
            if sec[1] != 11:  # SHT_DYNSYM
                continue
            st = sections[sec[6]]
            strings = self.data[st[4]:st[4] + st[5]]
            for p in range(sec[4], sec[4] + sec[5], sec[9]):
                name, _, _, shndx, va, _ = struct.unpack_from("<IBBHQQ", self.data, p)
                if shndx and name:
                    found[strings[name:strings.index(0, name)].decode("utf-8")] = va
        return found


def branch_target(elf: Elf, site: int) -> int:
    word = struct.unpack("<I", elf.at(site, 4))[0]
    if word >> 26 != 0b100101:
        raise ValueError("Expected AArch64 BL")
    relative = word & 0x03ffffff
    if relative & 0x02000000:
        relative -= 0x04000000
    return site + relative * 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("apk", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks = []

    def check(name: str, condition: bool) -> None:
        checks.append({"name": name, "passed": bool(condition)})
        if not condition:
            raise ValueError("Guard failed: " + name)

    inputs = {}
    with zipfile.ZipFile(args.apk) as archive:
        for name, (size, expected) in EXPECTED.items():
            entry = "lib/arm64-v8a/" + name
            actual_size = archive.getinfo(entry).file_size
            with archive.open(entry) as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            check("entry-size:" + name, size == actual_size)
            check("entry-sha256:" + name, expected == actual)
            inputs[name] = {"bytes": actual_size, "sha256": actual}
        frontend = Elf(archive.read("lib/arm64-v8a/libmain.so"))
        normal = Elf(archive.read("lib/arm64-v8a/libpcsx_rearmed_libretro_android.so"))
        online = Elf(archive.read("lib/arm64-v8a/libstation_online_pcsx.so"))
        engines = json.loads(archive.read("assets/station-online/engines.json"))

    normal_symbols = normal.symbols()
    for name in ["retro_run", "retro_serialize_size", "retro_serialize", "retro_unserialize", "retro_load_game", "retro_set_input_poll", "retro_set_input_state", "retro_set_video_refresh", "retro_set_audio_sample_batch"]:
        check("normal-core-export:" + name, name in normal_symbols)
    check("normal-version-string", normal.text(0x5d904) == "r26 ff81ed1")
    check("normal-library-name", normal.text(0x5fd26) == "PCSX-ReARMed")
    check("online-normal-cores-differ", inputs["libpcsx_rearmed_libretro_android.so"]["sha256"] != inputs["libstation_online_pcsx.so"]["sha256"])

    frontend_symbols = frontend.symbols()
    check("normal-player-run-symbol", frontend_symbols.get("_ZN14LibretroPlayer3runERKNSt6__ndk112basic_stringIcNS0_11char_traitsIcEENS0_9allocatorIcEEEES8_") == 0x2a9718)
    check("normal-core-run-symbol", frontend_symbols.get("_ZN12LibretroCore3runEv") == 0x2be414)
    check("core-run-dispatch-and-loaded-check", frontend.at(0x2be414, 24) == struct.pack("<6I", 0x39402008, 0x7100051f, 0x54000061, 0xf9405000, 0xd61f0000, 0xd65f03c0))
    check("player-pause-gate-and-core-run", frontend.at(0x2ae600, 24) == struct.pack("<6I", 0x39662be8, 0xaa0003f3, 0x37000068, 0x910c03e0, 0x9403d748, 0xf9005bfa))
    check("input-port-zero-one-only", frontend.at(0x2b6308, 16) == struct.pack("<4I", 0x7100041f, 0x54000ae8, 0x395b3288, 0x37000aa8))
    sites = {
        "events": (0x2abe48, 0x39e290),
        "coreRun": (0x2ae610, 0x3a4330),
        "audio": (0x2aeac4, 0x3a47b0),
        "videoUpload": (0x2aec5c, 0x3a47d0),
        "stateSize": (0x2add78, 0x3a4380),
        "stateSave": (0x2addac, 0x3a4390),
        "stateLoad": (0x2b081c, 0x3a43a0),
        "pacing": (0x2b142c, 0x39e310),
        "swap": (0x2b1444, 0x39e340),
    }
    for name, (site, target) in sites.items():
        check("normal-owner-call:" + name, branch_target(frontend, site) == target)
    psx = [e for e in engines["engines"] if e["platform"] == "psx"]
    check("psx-single-online-descriptor", len(psx) == 1)
    check("psx-online-core-exact", psx[0]["coreSha256"] == inputs["libstation_online_pcsx.so"]["sha256"])
    check("psx-online-library-exact", psx[0]["library"] == "libstation_online_pcsx.so")
    check("online-abi-exists", "retro_run" in online.symbols())
    result = {
        "schemaVersion": 1,
        "scope": "R126 packaged PSX normal owner ABI and MAME library provenance, read-only",
        "passed": True,
        "checks": len(checks),
        "inputs": inputs,
        "normalPsx": {"sourceRevisionInCore": "ff81ed1", "libraryVersion": "r26 ff81ed1", "frontendSourceLocated": False, "frontendOwner": "LibretroPlayer::run", "maximumInputPortsObserved": 2, "calls": {n: hex(site) for n, (site, _) in sites.items()}},
        "onlinePsx": {"engineId": psx[0]["engineId"], "core": psx[0]["library"], "differentNormalCore": True},
        "limits": ["No emulator or Android process executed", "No patch or adapter installed", "Binary ABI guards are specific to these exact hashes", "No determinism, multiplayer, CPU pause ACK, gameplay, or performance claim", "No ROM, BIOS, credentials, serials, device logs, or extracted binaries included"],
        "results": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "checks": len(checks)}))


if __name__ == "__main__":
    main()
