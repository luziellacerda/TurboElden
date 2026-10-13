"""Closed R141 HTTP scope over the exact R140 signed donor."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = "61e873e7bbd75a13fbd0d55515a3726f4debd8984cc0fe8f9d73401e0897792c"
BASE_BYTES = 2715008015
BASE_SOURCE = "b93623b708bafe151441d3e4920acad51718e118"
PARTITION = "classes28.dex"
DEX = "6c9c2d6df00919ca4c927c3719b932ebfb1ef46b24f2de778120a84fd8d30225"
PRESERVED_DEX35 = "49f381dc3ef375797d2db56b25a8a6c86a8150c2515ce115f4639b7bb243478e"
RETRO = "ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378"
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
BUILD_NAMESPACE = Path("E:/StationDirectDownloadsR141-20261013")
PREFIX = "Lorg/emulationstation/frontend/station/"
HTTP_TYPES = {PREFIX + name + ";" for name in ("StationHttp", "StationHttp$1", "StationHttp$ResponseBody",
    "StationHttp$$ExternalSyntheticLambda0", "StationHttp$$ExternalSyntheticLambda1", "StationHttp$$ExternalSyntheticLambda2")}
BODY = PREFIX + "StationHttp$ResponseBody;"
ORIGIN = PREFIX + "StationDownloadOrigin;"
MODIFIED_TYPES = HTTP_TYPES - {BODY}
FINAL_TYPES = HTTP_TYPES | {ORIGIN}
WRAPPERS = {
    "psx": ("libstation_psx_online.so", "28371f460a4dc45d86ce4cdb434c972fc4cfaa08de674503cf60cbece1397529"),
    "n64": ("libstation_mupen64plus_runtime.so", "1ef68413f83c82eb267b408f00922cc5a4c77f202182548cfd474246f3960664"),
    "dolphin": ("libstation_dolphin_runtime.so", "7df312d0e8dbbe37ea66bfec60d054e1ceeb823c3fc03a9b0fe4dca84777a42c"),
}
PARENT_FINGERPRINTS = {
    "psx": "c1c9395847d1c561065d9ae1e38061fa5c3ad4130fce7cacd821bddae42089ae",
    "n64": "f323984d9f2068677b22ee35faa32dda7561107ac54c56fed75cfa5fb59dc77b",
    "dolphin": "c3bd1dbcd98e1efd7e3b9069c9e36823b056ed641662c21abac12d1e3dcdeaf4",
}
REPLACED = {PARTITION, "assets/station-online/engines.json", *["lib/arm64-v8a/" + v[0] for v in WRAPPERS.values()]}
ROOT_DEX = {"classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]}
TOOLS = {
    "java": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "javac": "9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549",
    "androidJar": "6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad",
    "d8Jar": "305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5",
    "apktool": "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",
    "roomsJar": "6b2929eb3621b208593a886b6f06a32de52af9c931663cb314e197af155f773d",
    "clientJar": "011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313",
}


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


def source_map():
    files = {p.relative_to(ROOT).as_posix(): sha(p) for folder in ("java", "recipe")
             for p in sorted((ROOT / folder).rglob("*")) if p.is_file() and p.suffix in {".py", ".java"}}
    for name in ("PROPOSED-SCOPE.json", "PROVENANCE.json"):
        files[name] = sha(ROOT / name)
    files.update({p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "licenses").rglob("*")) if p.is_file()})
    reviewed = read(ROOT / "PROVENANCE.json")["reviewedSourceSha256"]
    need({n: h for n, h in files.items() if n.startswith("java/")} == reviewed and len(reviewed) == 2,
         "Exactly two byte-exact reviewed download Java sources required")
    need(not (ROOT / "native").exists(), "No new productive native implementation permitted")
    return files


def verify_dependencies():
    pins = read(ROOT / "PROVENANCE.json")["dependencySourceSha256"]
    for name, checksum in pins.items():
        need(sha(REPO / name) == checksum, "Retained dependency source changed: " + name)
    return pins


def verify_commit(commit):
    need(re.fullmatch("[0-9a-f]{40}", commit or ""), "Full frozen R141 source commit required before compilation")
    pins = source_map()
    prefix = ROOT.relative_to(REPO).as_posix()
    frozen = {prefix + "/" + n: h for n, h in pins.items()}
    frozen.update(verify_dependencies())
    clinical = read(ROOT / "PROVENANCE.json")["clinicalQualification"]
    need(sha(REPO / clinical["path"]) == clinical["sha256"], "Inherited R140 clinical evidence changed")
    frozen[clinical["path"]] = clinical["sha256"]
    for name, expected in frozen.items():
        raw = subprocess.check_output(["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO),
            "show", commit + ":" + name], stderr=subprocess.PIPE)
        need(digest(raw) == expected, "Frozen R141 source/provenance mismatch: " + name)
    return pins


def isolated(path):
    output = Path(path).resolve()
    need(not output.exists(), "New isolated output directory required")
    need(REPO != output and REPO not in output.parents and ".git" not in output.parts, "Output outside source repository required")
    need(BUILD_NAMESPACE.resolve() in output.parents, "R141 outputs must be children of E:/StationDirectDownloadsR141-20261013")
    return output


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, "R141 build stage failed: " + result.stderr[-1600:])
    need(not re.search(r"(?im)^.*\bwarning:", result.stderr), "Compiler warning requires review")
    return result.stdout.strip()


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


def fingerprints(archive):
    result = {}
    for kind, (name, old_hash) in WRAPPERS.items():
        raw = archive.read("lib/arm64-v8a/" + name)
        need(digest(raw) == old_hash, "Exact current R140 wrapper required")
        value = extract_fingerprint(raw)
        need(digest(canonical(value)) == PARENT_FINGERPRINTS[kind] and len(value["payloadSha256"]) == 345 and
             value["payloadSha256"].get(PARTITION) == DEX and value["payloadSha256"].get("classes35.dex") == PRESERVED_DEX35,
             "Exact R140 fingerprint must bind both DEX28 and corrected DEX35")
        result[kind] = value
    need(all(v["payloadSha256"] == result["psx"]["payloadSha256"] and
             v["productiveTransforms"] == result["psx"]["productiveTransforms"] for v in result.values()),
             "Inherited common payload/source chains differ")
    return result


def entry_sha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_dex_receipt(receipt, path, commit, pins):
    need(receipt.get("schema") == "station.r141.direct-downloads.dex.v1" and receipt.get("passed") is True and
         receipt.get("compiled") is True and receipt.get("sourceCommit") == commit and receipt.get("sourceFiles") == pins and
         receipt.get("baselineApkSha256") == BASE and receipt.get("baselineDexSha256") == DEX and
         receipt.get("outputDexSha256") == sha(path) and receipt.get("preservedDex35Sha256") == PRESERVED_DEX35 and
         receipt.get("originalClassCount") == 271 and receipt.get("finalClassCount") == 272 and
         receipt.get("unchangedClasses") == 266 and receipt.get("unrelatedClassesByteIdentical") is True and
         receipt.get("responseBodyPreserved") is True and receipt.get("originalAllowedTypes") == sorted(MODIFIED_TYPES) and
         receipt.get("finalAllowedTypes") == sorted(MODIFIED_TYPES | {ORIGIN}) and
         receipt.get("addedTypes") == [ORIGIN] and receipt.get("removedTypes") == [] and
         receipt.get("testsPackaged") is False and receipt.get("sdkOrDependenciesPackaged") is False and
         receipt.get("inputSha256") == TOOLS and
         set(receipt.get("preservedDexSha256", {})) == ROOT_DEX - {PARTITION} and
         receipt["preservedDexSha256"].get("classes35.dex") == PRESERVED_DEX35,
         "Closed reviewed HTTP DEX and all 39 preserved DEX proofs required")
    before, after, retained = (receipt.get(k, {}) for k in ("baselineClassSha256", "outputClassSha256", "unchangedClassSha256"))
    need(len(before) == 271 and len(after) == 272 and len(retained) == 266 and
         set(before) - MODIFIED_TYPES == set(after) - (MODIFIED_TYPES | {ORIGIN}) == set(retained) and
         {t: before[t] for t in retained} == {t: after[t] for t in retained} == retained and BODY in retained and
         sorted(set(after) - set(before)) == [ORIGIN] and not set(before) - set(after), "Complete retained class projections required")
    return receipt


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


def state_fields():
    return dict(revision="R141", candidateOnly=True, diagnosticLoggerIncluded=False, nativeRuntimeRebuilt=False,
                promoted=False, installed=False, serverRegistered=False, serverRegistrationPending=True,
                physicalGameplayValidated=False, physicalDownloadValidated=False, speedImprovementMeasured=False)
