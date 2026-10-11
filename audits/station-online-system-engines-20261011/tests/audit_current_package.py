"""Read the frozen APK and classify all normal/online system routes.

No room is authenticated, emulator executed, package changed, or phone operated.
Missing normal fallback cores are recorded as findings, never silently replaced.
"""
from pathlib import Path
import argparse
import collections
import datetime
import hashlib
import json
import re
import struct
import zipfile

EXPECTED_APK = "f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d"
NATIVE_BACKENDS = {
    "n64": "mupen64plus-ae-station-v1",
    "gamecube": "dolphin-station-v1",
    "wii": "dolphin-station-v1",
}
PLATFORM_RENAMES = {
    "super-nintendo": "snes", "super-nintendo--br": "snes",
    "megadrive--br": "megadrive", "neo-geo": "neogeo",
    "neo-geo-cd": "neogeocd", "nintendo-64": "n64",
    "nintendo-64--br": "n64", "ps2br": "ps2",
}
SYSTEM_LIBS = {"libandroid.so", "liblog.so", "libdl.so", "libc.so", "libm.so",
               "libz.so", "libGLESv1_CM.so", "libGLESv2.so", "libGLESv3.so",
               "libEGL.so", "libOpenSLES.so", "libvulkan.so", "libmediandk.so",
               "libaaudio.so", "libjnigraphics.so", "libnativewindow.so",
               "libneuralnetworks.so", "libcamera2ndk.so", "libstdc++.so"}


def digest_file(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def uleb(data, offset):
    value, shift = 0, 0
    while True:
        byte = data[offset]; offset += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
        shift += 7
        if shift > 35:
            raise ValueError("Malformed DEX uleb")


def dex_classes(data):
    if data[:4] != b"dex\n":
        raise ValueError("Not a DEX")
    strings_count, strings_off = struct.unpack_from("<II", data, 56)
    type_count, type_off = struct.unpack_from("<II", data, 64)
    class_count, class_off = struct.unpack_from("<II", data, 96)
    def string(index):
        if not 0 <= index < strings_count:
            raise ValueError("Invalid DEX string")
        off = struct.unpack_from("<I", data, strings_off + 4 * index)[0]
        _, off = uleb(data, off)
        return data[off:data.index(b"\0", off)].decode("utf-8", errors="replace")
    result = set()
    for i in range(class_count):
        index = struct.unpack_from("<I", data, class_off + 32 * i)[0]
        if index >= type_count:
            raise ValueError("Invalid DEX type")
        string_id = struct.unpack_from("<I", data, type_off + 4 * index)[0]
        result.add(string(string_id))
    return result


def elf_info(data):
    if data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("Expected little-endian ELF64")
    machine = struct.unpack_from("<H", data, 18)[0]
    phoff = struct.unpack_from("<Q", data, 32)[0]
    phsize, phcount = struct.unpack_from("<HH", data, 54)
    loads, dynamic = [], None
    for i in range(phcount):
        p = struct.unpack_from("<IIQQQQQQ", data, phoff + i * phsize)
        if p[0] == 1:
            loads.append({"offset": p[2], "vaddr": p[3], "filesz": p[5], "align": p[7]})
        elif p[0] == 2:
            dynamic = (p[2], p[5])
    tags = collections.defaultdict(list)
    if dynamic:
        for off in range(dynamic[0], dynamic[0] + dynamic[1], 16):
            tag, value = struct.unpack_from("<qQ", data, off)
            if tag == 0:
                break
            tags[tag].append(value)
    def address(value):
        for p in loads:
            if p["vaddr"] <= value < p["vaddr"] + p["filesz"]:
                return p["offset"] + value - p["vaddr"]
        raise ValueError("Unmapped ELF address")
    strings = address(tags[5][0]) if tags[5] else 0
    def text(off):
        off += strings
        return data[off:data.index(b"\0", off)].decode("utf-8")
    shoff = struct.unpack_from("<Q", data, 40)[0]
    shsize, shcount = struct.unpack_from("<HH", data, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", data, shoff + i * shsize) for i in range(shcount)]
    exports = []
    for section in sections:
        if section[1] != 11:  # SHT_DYNSYM
            continue
        string_section = sections[section[6]]
        for off in range(section[4], section[4] + section[5], section[9]):
            symbol_name, info, _, owner, _, _ = struct.unpack_from("<IBBHQQ", data, off)
            if not symbol_name or not owner or (info >> 4) not in (1, 2):
                continue
            start = string_section[4] + symbol_name
            name = data[start:data.index(b"\0", start)].decode("utf-8")
            if name.startswith(("StationMupen", "Java_org_emulationstation_frontend_netplay_StationDolphinBridge_")):
                exports.append(name)
    return {"machine": machine, "loadAlignments": [p["align"] for p in loads],
            "soname": text(tags[14][0]) if tags[14] else None,
            "needed": [text(value) for value in tags[1]], "stationBridgeExports": sorted(exports)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    checks = 0
    def check(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)
    apk_sha = digest_file(args.apk)
    check(apk_sha == EXPECTED_APK, "The frozen R126 APK identity changed")
    matrix_path = args.repo / "versions/station-game-menu-controller-audit-r120-20261010/evidence/launch-matrix-r120.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    check(len(matrix["rows"]) == 50, "Canonical system matrix incomplete")
    checks_source = args.repo / "versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay/StationRoomsActivity.java"
    game_source = args.repo / "versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay/StationOnlineGame.java"
    route_text = checks_source.read_text(encoding="utf-8")
    for literal in ("StationN64Activity.class", "StationDolphinActivity.class", "StationRetroActivity.class",
                    "systemN64?StationN64Launch.prepare", "systemDolphin?StationDolphinLaunch.prepare"):
        check(literal in route_text, "Actual room dispatch changed: " + literal)
    policy_source = args.repo / "versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationOnlinePlatformPolicy.java"
    policy_text = policy_source.read_text(encoding="utf-8")
    for folder, platform in PLATFORM_RENAMES.items():
        check('case "' + folder + '":' in policy_text and 'return "' + platform + '";' in policy_text,
              "Renamed canonical platform no longer in source: " + folder)
    rows, libs = [], {}
    with zipfile.ZipFile(args.apk) as archive:
        entries = set(archive.namelist())
        engines_data = archive.read("assets/station-online/engines.json")
        manifest = json.loads(engines_data)
        source_asset = args.repo / "versions/station-dolphin-online-r126-20261011/assets/station-online/engines.json"
        check(source_asset.read_bytes() == engines_data, "Published engines differ from packaged engines")
        check(len(manifest["engines"]) == 13, "Engine entry inventory changed")
        class_location = {}
        for entry in sorted(entries):
            if entry.startswith("classes") and entry.endswith(".dex"):
                for descriptor in dex_classes(archive.read(entry)):
                    check(descriptor not in class_location, "Duplicate actual DEX class: " + descriptor)
                    class_location[descriptor] = entry
        def library(entry):
            if entry in libs:
                return libs[entry]
            if entry not in entries:
                return None
            data = archive.read(entry)
            info = elf_info(data)
            check(info["machine"] == 183, "Non ARM64 engine: " + entry)
            info.update({"entry": entry, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                         "unresolvedNeeded": [n for n in info["needed"] if n not in SYSTEM_LIBS and
                                             "lib/arm64-v8a/" + n not in entries]})
            libs[entry] = info
            return info
        active = {}
        for engine in manifest["engines"]:
            if not engine.get("launchReady") or engine.get("recoveryProtocol") != "station-stream.v3":
                continue
            platform = engine["platform"]
            check(platform not in active, "Ambiguous eligible engine for platform " + platform)
            active[platform] = engine
            core = library("lib/arm64-v8a/" + engine["library"])
            check(core is not None and core["sha256"] == engine["coreSha256"], "Online core hash mismatch " + platform)
            runtime = library("lib/arm64-v8a/" + engine.get("runtimeLibrary", "libstation_retroarch.so"))
            check(runtime is not None and runtime["sha256"] == engine["runtimeSha256"], "Online runtime hash mismatch " + platform)
            if platform in NATIVE_BACKENDS:
                check(engine.get("backend") == NATIVE_BACKENDS[platform], "Real native adapter missing " + platform)
                check(engine.get("maximumPlayers") == 4, "Native physical-port ceiling changed " + platform)
                check(not core["unresolvedNeeded"] and not runtime["unresolvedNeeded"], "Native adapter dependency unresolved " + platform)
                check(all(n >= 16384 for n in core["loadAlignments"] + runtime["loadAlignments"]), "Native adapter ELF pages too small " + platform)
                for dependency, expected_hash in engine["dependencySha256"].items():
                    actual = library("lib/arm64-v8a/" + dependency)
                    check(actual is not None and actual["sha256"] == expected_hash, "Native dependency hash mismatch: " + dependency)
        dolphin_api = args.repo / "versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay/StationDolphinBridge.java"
        native_names = re.findall(r"public static native [\w\[\]]+ (\w+)\(", dolphin_api.read_text(encoding="utf-8"))
        dolphin_exports = libs["lib/arm64-v8a/libstation_dolphin_online.so"]["stationBridgeExports"]
        check(len(native_names) == 21, "Dolphin bridge declaration count changed")
        for native_name in native_names:
            check("Java_org_emulationstation_frontend_netplay_StationDolphinBridge_" + native_name in dolphin_exports,
                  "Dolphin JNI declaration has no actual ELF export " + native_name)
        n64_bridge = args.repo / "versions/station-mupen-online-r125-20261011/java/org/emulationstation/frontend/netplay/StationN64Bridge.java"
        n64_names = set(re.findall(r'"(StationMupen\w+)"', n64_bridge.read_text(encoding="utf-8")))
        n64_exports = libs["lib/arm64-v8a/libstation_mupen64plus_core.so"]["stationBridgeExports"]
        check(n64_names == {"StationMupenStatus", "StationMupenControl", "StationMupenStalled",
                            "StationMupenRequestQuit", "StationMupenConfigure"}, "N64 bridge API changed")
        for native_name in sorted(n64_names):
            check(native_name in n64_exports, "N64 FFI call has no actual ELF export " + native_name)
        for original in matrix["rows"]:
            folder = original["nativeFolder"]
            platform = PLATFORM_RENAMES.get(folder, folder)
            binding = original["binding"]
            normal_libs = []
            for expected in binding["libraries"]:
                entry = expected.get("entry") or "lib/arm64-v8a/" + expected["requestedName"]
                current = library(entry)
                normal_libs.append(current or {"entry": entry, "present": False})
                if expected.get("entry"):
                    check(current is not None, "Previously packaged normal core disappeared: " + folder)
                    check(current["bytes"] == expected["bytes"], "Normal core length changed: " + folder)
                    check(f'{archive.getinfo(entry).CRC:08x}' == expected["crc32"], "Normal core bytes differ from preserved route: " + folder)
            activities = []
            for component in binding["activityChain"]:
                descriptor = "L" + component["name"].replace(".", "/") + ";"
                current_dex = class_location.get(descriptor)
                check(current_dex is not None, "Original activity missing: " + component["name"])
                activities.append({"class": component["name"], "dexEntry": current_dex,
                                   "originalProcess": component.get("manifestComponent", {}).get("process")})
            online = active.get(platform)
            if platform in NATIVE_BACKENDS and online:
                classification = "real-system-adapter-implemented-physical-pending"
                activity = "StationN64Activity" if platform == "n64" else "StationDolphinActivity"
            elif online:
                classification = "same-core-family-different-owner" if platform in ("psx", "fbneo") else "different-core-and-owner"
                activity = "StationRetroActivity"
            else:
                classification = "no-eligible-online-engine"
                activity = None
            rows.append({"label": original["label"], "folder": folder, "onlinePlatform": platform,
                         "aliases": original["catalogAliases"], "normalEngine": binding["engine"],
                         "normalCommand": original["selectedOfflineCommand"], "normalActivityChain": activities,
                         "normalLibraries": normal_libs,
                         "onlineEngine": None if not online else {
                             "engineId": online["engineId"], "backend": online.get("backend", "retroarch"),
                             "library": online["library"], "coreSha256": online["coreSha256"],
                             "runtimeSha256": online["runtimeSha256"], "anchor": activity},
                         "classification": classification,
                         "signedGameProfileAndServerActivationVerified": False,
                         "physicalGameplayVerified": False})
        anchors = ("StationN64Activity", "StationDolphinActivity", "StationDolphinOnlineActivity", "StationRetroActivity")
        for name in anchors:
            check("Lorg/emulationstation/frontend/netplay/" + name + ";" in class_location, "Online anchor missing: " + name)
    check(sum(len(r["aliases"]) for r in rows) == matrix["catalogLookupKeys"], "Catalog alias coverage incomplete")
    receipt = {"schemaVersion": 1, "recordedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "kind": "read-only-current-apk-system-route-audit", "checks": checks, "failures": 0,
               "apkSha256": apk_sha, "apkBytes": args.apk.stat().st_size,
               "canonicalSystems": len(rows), "catalogAliases": matrix["catalogLookupKeys"],
               "enginesAssetSha256": hashlib.sha256(engines_data).hexdigest(),
               "classificationCounts": dict(collections.Counter(r["classification"] for r in rows)),
               "rows": rows, "libraries": libs,
               "sources": {str(p.relative_to(args.repo)).replace("\\", "/"): digest_file(p)
                           for p in (matrix_path, checks_source, game_source, policy_source)},
               "apkChanged": False, "phonesOperated": False, "serverOperated": False,
               "allSystemsUseNormalEngineOnline": all(r["classification"] == "real-system-adapter-implemented-physical-pending" for r in rows),
               "physicalGameplayVerified": False,
               "limitations": ["DEX declarations and ELF hashes prove package contents, not game execution.",
                               "Normal launch-command bodies were tested in the separate R120 host receipt and preserved through R126.",
                               "No fresh signed server profile or Android netplay was captured.",
                               "Missing fallback cores and unintegrated systems are findings, not automatic core replacements."]}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("checks", "failures", "canonicalSystems", "catalogAliases", "classificationCounts", "allSystemsUseNormalEngineOnline")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
