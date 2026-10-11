"""Read-only manifest metadata and targeted DEX startup references; no Android execution."""
from pathlib import Path
import importlib.util
import json
import struct
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
APK = Path(r"F:\TurboStations-Backup-Completo-20261011\desenvolvimento\TurboStations-Premium-R131-20261011.apk")
OUT = Path(__file__).parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

axml = load("audit_axml", ROOT / "versions/station-game-menu-controller-audit-r120-20261010/recipes/patch_component_factory.py")
dex_helpers = load("audit_dex", ROOT / "audits/station-online-system-engines-20261011/tests/audit_current_package.py")

def metadata(data):
    strings = []
    result = []
    stack = []
    for off, kind, header, size in axml.chunks(data):
        if kind == 1:
            strings = axml.string_pool(data, off)
        if kind == 0x102:
            tag = strings[axml.u32(data, off + 20)]
            start, width, count = struct.unpack_from("<HHH", data, off + 24)
            attrs = {}
            for i in range(count):
                pos = off + 16 + start + i * width
                name = strings[axml.u32(data, pos + 4)]
                raw, value = axml.u32(data, pos + 8), axml.u32(data, pos + 16)
                datatype = data[pos + 15]
                attrs[name] = strings[raw] if raw != 0xffffffff else strings[value] if datatype == 3 else value
            if tag == "meta-data":
                owner = next((row for row in reversed(stack) if row[0] in {"application", "activity", "service", "receiver", "provider"}), None)
                result.append({"ownerType": owner[0] if owner else None, "owner": owner[1].get("name") if owner else None, **attrs})
            stack.append((tag, attrs))
        if kind == 0x103:
            stack.pop()
    return result

WIDTH = {i: 1 for i in range(256)}
for op in [2, 5, 8, 0x13, 0x15, 0x16, 0x19, 0x1a, 0x1c, 0x1f, 0x20, 0x22, 0x23, 0x29, 0xfe, 0xff]:
    WIDTH[op] = 2
for op in [3, 6, 9, 0x14, 0x17, 0x1b, 0x24, 0x25, 0x26, 0x2a, 0x2b, 0x2c, 0xfc, 0xfd]:
    WIDTH[op] = 3
WIDTH[0x18] = 5
WIDTH[0xfa] = WIDTH[0xfb] = 4
for lo, hi in [(0x2d, 0x3d), (0x44, 0x6d), (0x90, 0xaf), (0xd0, 0xe2)]:
    for op in range(lo, hi + 1): WIDTH[op] = 2
for lo, hi in [(0x6e, 0x72), (0x74, 0x78)]:
    for op in range(lo, hi + 1): WIDTH[op] = 3

TARGETS = {
    "Lorg/yuzu/yuzu_emu/YuzuApplication;",
    "Lorg/yuzu/yuzu_emu/utils/ForegroundService;",
    "Lxendroid/compose/core/MainAliveService;",
    "Lorg/emulationstation/frontend/ESActivity;",
    "Lorg/emulationstation/frontend/auth/StationAuthActivity;",
    "Lorg/emulationstation/frontend/station/StationComponentFactory;",
    "Lorg/emulationstation/frontend/sony/StationSonyComponentFactory;",
    "Lorg/emulationstation/frontend/netplay/StationDolphinNetplayActivity;",
    "Lorg/emulationstation/frontend/netplay/StationNetplayActivity;",
    "Lorg/emulationstation/frontend/PlatformAssets;",
    "Lorg/yuzu/yuzu_emu/bootstrap/BootstrapAssets;",
    "Lorg/emulationstation/frontend/netplay/StationProcess;",
    "Lorg/emulationstation/frontend/netplay/StationSinglePassVideo720;",
    "Lorg/emulationstation/frontend/station/StationFrontend;",
    "Lorg/emulationstation/frontend/auth/StationTaskNavigation;",
    "Lorg/emulationstation/frontend/netplay/StationRoomsActivity;",
    "Lorg/emulationstation/frontend/offline/StationSonyOfflineActivity;",
}
TARGETS.update("Lorg/emulationstation/frontend/" + name + "Bootstrap;" for name in [
    "Mega", "Snes", "N64", "Mame", "Xbox", "Saturn", "Vita", "Xbox360", "WiiU", "Psp", "Ps2", "Flycast", "Dolphin"])

def targeted_methods(data):
    u32 = lambda off: struct.unpack_from("<I", data, off)[0]
    sc, so = struct.unpack_from("<II", data, 56)
    tc, to = struct.unpack_from("<II", data, 64)
    mc, mo = struct.unpack_from("<II", data, 88)
    cc, co = struct.unpack_from("<II", data, 96)
    strings = []
    for i in range(sc):
        _, off = dex_helpers.uleb(data, u32(so + 4 * i))
        strings.append(data[off:data.index(b"\0", off)].decode("utf-8", errors="replace"))
    types = [strings[u32(to + 4 * i)] for i in range(tc)]
    methods = []
    for i in range(mc):
        cls, proto, name = struct.unpack_from("<HHI", data, mo + 8 * i)
        methods.append((types[cls], strings[name], proto))
    result = []
    for i in range(cc):
        cls = types[u32(co + 32 * i)]
        if cls not in TARGETS: continue
        off = u32(co + 32 * i + 24)
        if not off: continue
        counts = []
        for _ in range(4):
            val, off = dex_helpers.uleb(data, off); counts.append(val)
        for _ in range(counts[0] + counts[1]):
            _, off = dex_helpers.uleb(data, off); _, off = dex_helpers.uleb(data, off)
        for number in counts[2:]:
            method_id = 0
            for _ in range(number):
                diff, off = dex_helpers.uleb(data, off); method_id += diff
                access, off = dex_helpers.uleb(data, off)
                code, off = dex_helpers.uleb(data, off)
                method = methods[method_id]
                calls, literals, flow, class_refs = [], [], [], []
                if code:
                    size = u32(code + 12)
                    words = struct.unpack_from("<" + "H" * size, data, code + 16)
                    pc = 0
                    while pc < size:
                        op = words[pc] & 255; width = WIDTH[op]
                        if op == 0 and words[pc]:
                            tag = words[pc]
                            if tag == 0x100: width = 4 + words[pc + 1] * 2
                            elif tag == 0x200: width = 2 + words[pc + 1] * 4
                            elif tag == 0x300:
                                elements = words[pc + 2] | words[pc + 3] << 16
                                width = 4 + (words[pc + 1] * elements + 1) // 2
                            else: raise ValueError("Unknown instruction payload")
                        if op in [*range(0x6e, 0x73), *range(0x74, 0x79), 0xfa, 0xfb]:
                            target = methods[words[pc + 1]]
                            calls.append(target[0] + "->" + target[1])
                            if method[1] in {"onCreate", "initProcess", "isProcess", "install", "installKeys"}:
                                flow.append({"pc": pc, "invoke": target[0] + "->" + target[1]})
                        if method[1] in {"onCreate", "initProcess", "isProcess", "install", "installKeys"}:
                            if 0x32 <= op <= 0x3d:
                                relative = struct.unpack("<h", struct.pack("<H", words[pc + 1]))[0]
                                flow.append({"pc": pc, "conditionalOpcode": hex(op), "targetPc": pc + relative})
                            if 0x0e <= op <= 0x11: flow.append({"pc": pc, "returnOpcode": hex(op)})
                        if op in (0x1a, 0x1b):
                            index = words[pc + 1] | (words[pc + 2] << 16 if op == 0x1b else 0)
                            value = strings[index]
                            # Only class/package/process/file-like literals, no user or private material.
                            if len(value) < 250 and (".so" in value or value.startswith(("org.", "com.", "xendroid", ":", "EmulationStation")) or "sandbox" in value.lower()): literals.append(value)
                        if op in (0x1c, 0x1f, 0x20, 0x22, 0x23):
                            class_refs.append(types[words[pc + 1]])
                        pc += width
                    if pc != size: raise ValueError("DEX instruction boundary mismatch")
                result.append({"class": cls, "method": method[1], "protoIndex": method[2], "native": bool(access & 0x100), "code": bool(code), "directCalls": list(dict.fromkeys(calls)), "selectedClassAndLibraryLiterals": list(dict.fromkeys(literals)), "classInstructionReferences": list(dict.fromkeys(class_refs)), "selectedControlFlow": flow})
    return result

with zipfile.ZipFile(APK) as archive:
    entries = metadata(archive.read("AndroidManifest.xml"))
    refs = []
    for name in archive.namelist():
        if name.startswith("classes") and name.endswith(".dex") and "/" not in name:
            for row in targeted_methods(archive.read(name)):
                refs.append({"dex": name, **row})
result = {"schema": "station.r131.startup-roots.readonly.v1", "apkSha256": "0273ab9ae1b7ef5a061fdcc76c49558db4180bedd10a8100e6d5f764ac2ab175", "manifestMetadata": entries, "targetedDexMethods": refs, "scope": "Direct bytecode references and manifest metadata, not transitive reachability or runtime execution", "privateMaterialIncluded": False}
(OUT / "startup-roots.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"metadataRows": len(entries), "targetedMethods": len(refs), "output": str(OUT / "startup-roots.json")}))
