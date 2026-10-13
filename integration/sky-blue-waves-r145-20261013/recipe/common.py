"""Closed R145 visual package over exact R144; draft cannot execute before scope freeze."""
from pathlib import Path
import hashlib, json, re, struct, subprocess
ROOT = Path(__file__).resolve().parents[1]
SCOPE_NAME = "sky-blue-waves-r145-20261013"
REPO = ROOT.parents[1] if ROOT.parent.name == "integration" else ROOT.parent / "publication-app"
BASE = "01427f4e73141b7d6a462c2420a9abeb018a8716102e7fb959bf9a1d69eccee0"
BASE_BYTES = 2715024399
BASE_SOURCE = "1ac3f7d2fdd7cd349a5b37127b66712834e844fd"
PARTITIONS = {"classes28.dex", "classes35.dex", "classes40.dex"}
DEX_BASE = {"classes28.dex": "b1ceabcfc17eeda1e76fb9a0adadc056141605e20bbfce0c684df09a9e321fdd", "classes35.dex": "0cc5f639202ed3da50c246a9b07eda91c8c8d81bdc9764c67f08f3da459a74c4", "classes40.dex": "47689f896202fb6a109fcfc7f4d820114b1416ce66d521db9d4780055443f4dd"}
CAROUSEL = "lib/arm64-v8a/libturbo_carousel.so"
CAROUSEL_SHA = "67180bdd145cd03f456249b31b9163ee0baa3e66fb10b909e20831823accea10"
RETRO = "ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378"
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
ROOT_DEX = {"classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]}
WRAPPERS = {"psx": ("libstation_psx_online.so", "3537bea1a6d27056ef9c0269eb2988596524b67d5d92fe9f25f59e25e3c7ac55"), "n64": ("libstation_mupen64plus_runtime.so", "4783da1ca2f5b46987b6aa27cfde7f230365126d695e73d6e9ad660af19ce6e9"), "dolphin": ("libstation_dolphin_runtime.so", "3e87fc03cdd1115492e984b26c5f051f7abc8a5783041e04dd2803920b01847d")}
REPLACED = {*PARTITIONS, CAROUSEL, "assets/station-online/engines.json", *["lib/arm64-v8a/" + v[0] for v in WRAPPERS.values()]}
CHANGED_PAYLOAD = {*PARTITIONS, CAROUSEL}
BUILD_NAMESPACE = Path("E:/StationSkyBlueWavesR145-20261013")
PARENT_NATIVE_RECEIPT_SHA = "a885ba6bdcb09bf34b6368a33f200c5fb86e20724ff2fd680f6e05c71609249e"
PARENT_NATIVE_INPUT_MAP_SHA = "257a141bb735e4d14d52ead80807512c8ff4a9dfd6b66db3cd0b5c5bc7929af2"
PARENT_FINAL_PROOF_SHA = "24092e4418d477939da2e832fdd91527dc346028d61a44d792c66e022be16825"
PARENT_SOURCE_FILES = {'java/org/emulationstation/frontend/station/StationWaveBackground.java': '553c98972c89954c01da7b0f192e4d2978c11c1069c4661e542b735e67c88da4', 'native/native_space.h': 'e197030037ccb922304cef57d2b99a951a952fa354bb990e8dabe6f412336725', 'native/station_wave_palette.h': 'a3e42391c906fe5126b69213d97c685f4077ef6867aec4c27adbe426deea3b29', 'recipe/assemble_apk.py': 'a374f2364a581e080f1f690d94c38552de1f1124e142e9908935bb5344c1afcc', 'recipe/AssembleScopedPartition.java': '5ea794aad4cb177080e331b09d449419e352020ac61a6b9ea4194e32b4b1b022', 'recipe/build_dex.py': 'aee63b26ad2c57fb1ae36c84b42bb12d484c9e24fc5c1fa616e655878be4b55a', 'recipe/build_identity.py': '0585bc95cf09dc87e3e274c91bb5831a4defca429d1ad0994b52dcee9d3b2e2f', 'recipe/build_native.py': '3c5cc2b72a6af09714b91935b9b7148585e86c6b4819f0a128e2e670c0fd4873', 'recipe/common.py': 'cece0f499dcb38ca9a66078cc20d2ffcacdbd70fd684310b4c6faed467f95cdf', 'recipe/DecodeDolphinPartition.java': 'd1365cf8cce05fb08c6e04dbcc47e9b154af268637bf0d768c32f851420c2b67', 'recipe/verify_apk.py': '806e412a509d375fc5b8900106b3b7a204d6de0526a2fb9096f9feb0ccab1363', 'recipe/VerifyScopedPartition.java': 'c58eac1f58bfe7b8ee182374d183fb8b8f6dece25a485613b6f8c94fb62996ed', 'PROPOSED-SCOPE.json': 'ff57df00de3338f5cff05867cf32f040fbb48d5971048128acac40158a057702', 'java/evidence/java-source-preservation.json': '1b389ddc4d8aa58588593439aadee7e5754b4a2d8be9a7fccad8df2e1181ee59'}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

def read(path):
    return json.loads(Path(path).read_text("utf-8"))

def entry_sha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def extract_fingerprint(raw):
    docs = []
    for match in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw):
        end = raw.find(b"\0", match.start())
        if end < 0:
            continue
        try:
            value = json.loads(raw[match.start():end].decode("ascii"))
        except (ValueError, UnicodeError):
            continue
        if isinstance(value, dict) and "baseApkSha256" in value and "payloadSha256" in value:
            docs.append(value)
    need(len(docs) == 1, "Exactly one canonical wrapper identity required")
    value = docs[0]
    need(canonical(value) in raw and digest(canonical(value)).encode("ascii") in raw, "Embedded wrapper fingerprint differs")
    return value

def elf_contract(raw):
    need(raw[:6] == b"\x7fELF\x02\x01" and struct.unpack_from("<H", raw, 18)[0] == 183, "ARM64 ELF required")
    phoff = struct.unpack_from("<Q", raw, 32)[0]
    phsize, phnum = struct.unpack_from("<HH", raw, 54)
    loads = [struct.unpack_from("<IIQQQQQQ", raw, phoff + i * phsize) for i in range(phnum)]
    aligns = [row[-1] for row in loads if row[0] == 1]
    need(aligns and min(aligns) >= 16384, "16 KiB native load alignment required")
    shoff = struct.unpack_from("<Q", raw, 40)[0]
    shsize, shnum = struct.unpack_from("<HH", raw, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", raw, shoff + i * shsize) for i in range(shnum)]
    def string(table, index):
        end = table.find(b"\0", index)
        need(0 <= index < len(table) and end >= index, "Invalid ELF string")
        return table[index:end].decode("ascii")
    exports, needed, sonames = [], [], []
    for row in sections:
        if row[1] not in (6, 11):
            continue
        table = sections[row[6]]
        strings = raw[table[4]:table[4] + table[5]]
        data = raw[row[4]:row[4] + row[5]]
        need(row[9] > 0 and len(data) % row[9] == 0, "Invalid ELF table stride")
        for offset in range(0, len(data), row[9]):
            if row[1] == 11:
                name, info, other, index, _, _ = struct.unpack_from("<IBBHQQ", data, offset)
                if name and index and info >> 4 in (1, 2):
                    exports.append((string(strings, name), info, other))
            else:
                tag, value = struct.unpack_from("<qQ", data, offset)
                if tag == 1:
                    needed.append(string(strings, value))
                elif tag == 14:
                    sonames.append(string(strings, value))
    return dict(exports=sorted(exports), needed=sorted(needed), soname=sonames, minimumLoadAlignment=min(aligns))

def wrapper_contract(before, after, kind, ndk=None):
    old, new = elf_contract(before), elf_contract(after)
    need(old["exports"] == new["exports"] and old["needed"] == new["needed"] and
         old["soname"] == new["soname"] == [WRAPPERS[kind][0]], "Wrapper exports/dependencies/SONAME changed: " + kind)
    return new


def verify_parent_sources():
    parent = REPO / "integration/wave-palette-r144-20261013-final"
    for name, expected in PARENT_SOURCE_FILES.items():
        need(sha(parent / name) == expected, "Frozen R144 source was altered: " + name)
    return PARENT_SOURCE_FILES

def source_map():
    files = {p.relative_to(ROOT).as_posix(): sha(p)
             for folder in ("java", "native", "recipe", "smali", "evidence/proposed-smali") for p in sorted((ROOT / folder).rglob("*"))
             if p.is_file() and p.suffix in {".py", ".java", ".cpp", ".c", ".h", ".hpp", ".smali"}}
    for name in ("PROPOSED-SCOPE.json", "evidence/java-background-scope.json", "evidence/native-visual-scope.json",
                 "evidence/native-palette-spec.json", "evidence/native-inverse-map.json",
                 "evidence/native-source-preservation.json", "evidence/native-key-provenance.json",
                 "evidence/native-baseline-r144-native_space.h", "evidence/native-baseline-r144-station_wave_palette.h",
                 "evidence/native-baseline-r144-station_theme_palette.h"):
        files[name] = sha(ROOT / name)
    need(len(REPLACED) == 8 and all("recipe/" + name in files for name in
         ("common.py", "build_dex.py", "build_native.py", "build_identity.py", "assemble_apk.py", "verify_apk.py")),
         "Closed multi-DEX/native R145 source set required")
    return files

def verify_commit(commit):
    need(ROOT == REPO / "integration" / SCOPE_NAME,
         "Private preparation is not executable; stage the reviewed fresh R145 scope first")
    need(isinstance(commit, str) and re.fullmatch("[0-9a-f]{40}", commit), "Full new frozen R145 source commit required")
    need(commit != BASE_SOURCE, "R145 must use its own source commit")
    verify_parent_sources()
    pins = source_map(); prefix = ROOT.relative_to(REPO).as_posix()
    for name, expected in pins.items():
        result = subprocess.run(["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO),
                                 "show", commit + ":" + prefix + "/" + name], capture_output=True, timeout=90)
        need(result.returncode == 0 and digest(result.stdout) == expected, "Frozen R145 source differs: " + name)
    return pins

def isolated(path):
    output = Path(path).resolve()
    need(not output.exists() and BUILD_NAMESPACE.resolve() in output.parents and REPO not in output.parents and ".git" not in output.parts,
         "Fresh isolated R145 output below the fixed build namespace required")
    return output

def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, "R145 build stage failed: " + result.stderr[-1200:])
    return result.stdout.strip()

def fingerprints(archive):
    result = {}
    for kind, (library, checksum) in WRAPPERS.items():
        raw = archive.read("lib/arm64-v8a/" + library)
        need(digest(raw) == checksum, "Exact R144 wrapper required: " + kind)
        value = extract_fingerprint(raw)
        need(len(value["payloadSha256"]) == 345 and value["payloadSha256"].get(CAROUSEL) == CAROUSEL_SHA and
             all(value["payloadSha256"].get(name) == checksum for name, checksum in DEX_BASE.items()),
             "Exact 345-entry R144 payload required")
        result[kind] = value
    need(all(value["payloadSha256"] == result["psx"]["payloadSha256"] and
             value["productiveTransforms"] == result["psx"]["productiveTransforms"] for value in result.values()),
         "Inherited common payload and productive source chains differ")
    return result

def state_fields():
    return dict(revision="R145", candidateOnly=True, diagnosticLoggerIncluded=False, nativeRuntimeRebuilt=False,
                promoted=False, installed=False, serverRegistered=False, serverRegistrationPending=True,
                physicalVisualValidated=False, onlineDefectsFixed=False, serverKitApplied=False)
