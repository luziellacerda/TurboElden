"""Closed R147 Dolphin boot ownership/flag repair over exact signed R146."""
from pathlib import Path
import hashlib,json,re,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
SCOPE_NAME='dolphin-boot-cleanup-r147-20261014'
REPO=ROOT.parents[1] if ROOT.parent.name=='integration' else ROOT.parent/'publication-app'
BASE='04930201ad2f1c016f3385b3f08248ed4fa112d482a98761d00494b7a937468a'
BASE_BYTES=2715073551
BASE_SOURCE='bfea454d04ef297e9dfd1b397e0bf25df3937e93'
PARTITION='classes10.dex'
PARTITIONS={PARTITION}
DEX_BASE={PARTITION:'09ed47c40c4a6f5194bcb9ace23f85392b99c19c84cd654e61716de37b32e01c'}
CORE='lib/arm64-v8a/libstation_dolphin_online.so'
CORE_LIBRARY='libstation_dolphin_online.so'
CORE_SHA='f7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d'
CORE_UNSTRIPPED_SHA='92b1951facb9fca6aad644026c47adcc62e09c9b5aca61629aab7e1515a270fe'
NATIVE_BASE={CORE_LIBRARY:CORE_SHA,'libstation_dolphin_file_redirect_hook.so':'23347bb99e0e73fde1f6deaf1b39d544ab4e4a5cc9e5f2c61c8d9facf5dfe06c','libstation_dolphin_gsl_alloc_hook.so':'e9254fe5325818c1ef50cf986cd6db9a87d9b3c29c4567cd74e666b512598d02','libstation_dolphin_hook.so':'7547dd37533c4352edf7666ef3b5220db08364054578bde7570c388658e0de16','libstation_dolphin_hook_impl.so':'b3f2973bdccfb877cfc10fcaadd40b69e48af39434cc232d02bfc81a1669e264'}
PRIVATE_NATIVE_CLOSURES={'buildClosure':'d67ed8a82d26ff6c2ce1eb0e455cf13c0552dfd7e4cea92c7d76fcb9bb7ca95e','sourceClosure':'9aa6c8b937da034335b1ae7b129eb47d8ffdd39eb08ba944f5aba95faa53f9fe','graphClosure':'a073e2bdb84a8a4d5de70f74396d7ede71b41c405561e6b0cbe393c41d6e122a'}
CAROUSEL='lib/arm64-v8a/libturbo_carousel.so'
CAROUSEL_SHA='2e15a9a330c2562c71574921f5558d6142e3051bba64a315434e5714f38908a9'
RETRO='ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
ROOT_DEX={'classes.dex',*[f'classes{i}.dex' for i in range(2,41)]}
WRAPPERS={'psx':('libstation_psx_online.so','442db90ca4ba3d4f241a6a94ac42468f302a72c1919e3d50ec0638d005c46cbb'),'n64':('libstation_mupen64plus_runtime.so','d22cca056491ef952b5fa3c4c70ade0f3f2c4ba6771c06f67c2cda7880e70dd6'),'dolphin':('libstation_dolphin_runtime.so','3d3a183103d76417b74dd8fb9e6ff0bc5420d0db8720dc492f18243eb3390975')}
REPLACED={PARTITION,CORE,'assets/station-online/engines.json',*['lib/arm64-v8a/'+v[0] for v in WRAPPERS.values()]}
CHANGED_PAYLOAD={PARTITION}
CHANGED_APK_PAYLOAD={PARTITION,CORE}
BUILD_NAMESPACE=Path('E:/StationDolphinBootCleanupR147-20261014')
PARENT_SCOPE='integration/direct-v3-relay-r146-20261014'
PARENT_PROOF_PATH=Path('E:/StationDirectV3RelayR146-20261014/assembly/final-apk-proof.json')
PARENT_FINAL_PROOF_SHA='aafab1ca2231a5eeef8e2e282e4ce1b95f52111f752daaee82c6ec0afda81474'
PARENT_SOURCE_FILES={'recipe/assemble_apk.py': '78a0827c5e4ac84780b4d8867a148b075df3cbdd342362a53843845b970f9500', 'recipe/AssembleScopedPartition.java': 'cb05cfe93b6435908b3e492370ad89ad16299cbf03e3ffcecba8903ed420ee43', 'recipe/build_dex.py': 'dbf6b9d04a3d051c1d335ee05a6ec594d5c0da9bde38e2874ae25520502cbf2a', 'recipe/build_identity.py': '9c99af530815d14b2830bbf57e8d9685a73bafd79c010f6be109423c625422fd', 'recipe/common.py': 'ec3213504d6eeb0772b148c5243909ba0e07a91ad95712a1316fddc787ff77e1', 'recipe/DecodeDolphinPartition.java': '2b2085167e24964afe6a950e3978ea1c4de4bf83da12d827d6a9a3f8edc4de14', 'recipe/route_scope.py': 'a00cb361adff8d4de2c112b8f49127d9fa2f734fb5b2174af4da23af2c4130eb', 'recipe/verify_apk.py': '2d97ef4a2fafce43be211886d927f4c7baa6d7d91c69eafd3847bb51245a5986', 'recipe/VerifyScopedPartition.java': '3178f9d332c6b3921173b6c340b50a2c4d169b2d3abb369d9872bf4a361f427d', 'java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java': '95b8cf38c11c0a63919aaf9dc5cd8580110a79dd6bee7c22c1e28daca69175c1', 'java/org/emulationstation/frontend/netplay/StationRelayTls.java': '73f5c9a2f1a79ff5807efa0fc7b209a6e02dda9b72ae493cc438d778c42a0a92', 'tests/fixtures/org/emulationstation/frontend/station/StationConfig.java': '70cdee88662777853d8c40f3161663ecab9b365fd8e5e041abf6e4db5d39bdc9', 'tests/run_tests.py': 'fcadbf62ef47047c8ac94483c0e7c8063164b6fce2689d5929d49d51a87efd02', 'tests/StationRelayTlsRouteProbe.java': '4136bb464a4f341dfd7291a5f45f6afbe5bafb648931f8a4e10e144ae23eecf7', 'evidence/baseline-classes/org/emulationstation/frontend/netplay/StationMultiplayerSession$Channel.smali.txt': '303d0c135b2c0bd0e326b644daf4cbe4d2ca374cdcdd6de1b3379cded02b5ee9', 'evidence/baseline-classes/org/emulationstation/frontend/netplay/StationRelayTls.smali.txt': '494b5386879bbf7d8744245199ea4db9279b5724715ac4783e032615283e4135', 'evidence/baseline-java/StationMultiplayerSession.java.txt': '2b8fcbf368e38362e9f46701534471172ae388c1e163b2bb99f765a438ca7da2', 'evidence/baseline-java/StationRelayTls.java.txt': '423e8c5aa19c27596e69ff837749d1a2e3dbc8d06497cd74b54125af54c61abe', 'evidence/host-test-receipt.json': '135c4c29303255423c940e2c0f08528efcd6fa328af2b3f690f92b34188b07e2', 'evidence/preserved-critical/StationMultiplayerSession$Channel$1.smali.txt': '451ca6ef775d40cebb578fd2e4e63346b5e0ba3277455f0faedc09dc1e5f3dd8', 'evidence/preserved-critical/StationMultiplayerSession$Channel$2.smali.txt': 'bcc03efd60faf938fcdce22cd75611e7cf812cd4a3e1630b794ed24fb45e7f96', 'evidence/preserved-critical/StationMultiplayerSession.smali.txt': '3c0e5afd9eb6fa49038120819877efba59911390333f9ae4dceb77f5fbb20922', 'evidence/preserved-critical/StationMultiplayerTunnel$Remote.smali.txt': '27a31c17eac81ae996dbaa11deb115e7f5dbf4a977d6a1c851ecb413ab36ba29', 'evidence/preserved-critical/StationMultiplayerTunnel.smali.txt': '5840d5b2ba059f7a05de0aeb69c282eec12b029340d3b6c46ee51c872f6fa339', 'evidence/preserved-critical/StationRelayTls$1.smali.txt': '232c091b31fd7d41844a1dad5d70ba7e995da80e45d0eec3fd3e3fce80066763', 'evidence/proposed-smali/org/emulationstation/frontend/netplay/StationMultiplayerSession$Channel.smali': '080cc5408eb617b5032a5afd9d4a627615baef40e2ab0ecfe1d26857bcc2adb9', 'evidence/proposed-smali/org/emulationstation/frontend/netplay/StationRelayTls.smali': '3dca83f54e76ed81d78e88f39dacc4bee7536f1a20717f352eeab418d144fdae', 'evidence/route-scope.json': '9d7cbcf6ee1b34402b05936c5c9d71e361567d1627f27a5e0c27e8e66575a3d2'}


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


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, "R147 build stage failed: " + result.stderr[-1200:])
    return result.stdout.strip()


def fingerprints(archive):
    result = {}
    for kind, (library, checksum) in WRAPPERS.items():
        raw = archive.read("lib/arm64-v8a/" + library)
        need(digest(raw) == checksum, "Exact R146 wrapper required: " + kind)
        value = extract_fingerprint(raw)
        need(len(value["payloadSha256"]) == 345 and value["payloadSha256"].get(CAROUSEL) == CAROUSEL_SHA and
             CORE not in value["payloadSha256"] and
             all(value["payloadSha256"].get(name) == checksum for name, checksum in DEX_BASE.items()),
             "Exact 345-entry R146 payload required")
        result[kind] = value
    need(all(value["payloadSha256"] == result["psx"]["payloadSha256"] and
             value["productiveTransforms"] == result["psx"]["productiveTransforms"] for value in result.values()),
         "Inherited common payload and productive source chains differ")
    return result


def verify_parent_sources():
    need(len(PARENT_SOURCE_FILES) == 28, 'Exact 28-input R146 productive source closure required')
    for name, expected in PARENT_SOURCE_FILES.items():
        path = REPO / PARENT_SCOPE / name
        result = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                                 'show', BASE_SOURCE + ':' + PARENT_SCOPE + '/' + name], capture_output=True, timeout=90)
        need(path.is_file() and sha(path) == expected and result.returncode == 0 and digest(result.stdout) == expected,
             'Original frozen R146 source changed: ' + name)
    return PARENT_SOURCE_FILES


def verify_parent_proof(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink() and sha(path) == PARENT_FINAL_PROOF_SHA,
         'Exact signed R146 proof required')
    proof = read(path)
    need(proof.get('schema') == 'station.r146.direct-v3-relay.final.v1' and proof.get('passed') is True and
         proof.get('sourceCommit') == BASE_SOURCE and proof.get('apkSha256') == BASE and proof.get('apkBytes') == BASE_BYTES and
         proof.get('sourceFiles') == PARENT_SOURCE_FILES and proof.get('signatureCertificateSha256') == CERT and
         proof.get('v2') is proof.get('v3') is proof.get('zipAlignment16KiB') is True and
         proof.get('checkedEntries') == 13860 and proof.get('preservedCarouselSha256') == CAROUSEL_SHA and proof.get('preservedDexPartitions') == 39,
         'Completed actual R146 parent proof differs')
    verify_parent_sources()
    return proof


def verify_commit(commit):
    need(ROOT == REPO / 'integration' / SCOPE_NAME,
         'Private preparation cannot execute production: stage the reviewed distinct R147 scope')
    need(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit) and commit != BASE_SOURCE,
         'Distinct full frozen R147 source commit required')
    verify_parent_sources()
    pins = source_map()
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, expected in pins.items():
        result = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                                 'show', commit + ':' + prefix + '/' + name], capture_output=True, timeout=90)
        need(result.returncode == 0 and digest(result.stdout) == expected, 'Frozen R147 source differs: ' + name)
    return pins


def isolated(path):
    output = Path(path).resolve()
    need(not output.exists() and BUILD_NAMESPACE.resolve() in output.parents and REPO not in output.parents and
         '.git' not in output.parts, 'Fresh isolated R147 output below its fixed namespace required')
    return output


def source_map():
    files = {}
    extensions = {'.py', '.java', '.cpp', '.c', '.h', '.hpp', '.cmake', '.smali', '.txt', '.json'}
    excluded = {'full-native-baseline', 'field-scan-tools', '__pycache__', '.git'}
    paths = list(ROOT.iterdir())
    for folder in ('recipe', 'java', 'tests', 'evidence', 'smali', 'reference-java', 'native'):
        paths.extend((ROOT / folder).rglob('*'))
    for path in sorted(set(paths)):
        relative = path.relative_to(ROOT)
        if path.is_file() and path.suffix in extensions and not set(relative.parts).intersection(excluded):
            need(not path.is_symlink() and not path.is_junction(), 'Reparse productive source refused')
            files[relative.as_posix()] = sha(path)
    # The DEX producer consumes this immutable 23-file source qualification,
    # including its original README. Preserve that precise set as well.
    ready = read(ROOT / 'SOURCE-READY.json')
    need(ready.get('schema') == 'station.r147.dolphin.boot-ownership.source-ready.v1' and
         len(ready.get('filesSha256', {})) == 23, 'Original immutable ownership qualification required')
    for name, expected in ready['filesSha256'].items():
        path = ROOT / name
        need(path.resolve().is_relative_to(ROOT.resolve()) and path.is_file() and
             not path.is_symlink() and not path.is_junction() and sha(path) == expected,
             'Previously reviewed ownership input changed: ' + name)
        files[name] = expected
    files['SOURCE-READY.json'] = sha(ROOT / 'SOURCE-READY.json')
    required = {'recipe/common.py', 'recipe/build_dex.py', 'recipe/build_native.py', 'recipe/build_identity.py',
        'recipe/assemble_apk.py', 'recipe/verify_apk.py', 'recipe/StationDolphinMainAndroidOverride.cmake',
        'recipe/AssembleScopedPartition.java', 'recipe/VerifyScopedPartition.java', 'recipe/DecodeDolphinPartition.java',
        'evidence/dex10-scope.json', 'evidence/ownership-scope.json', 'evidence/native-scope.json',
        'evidence/canonical-baseline-NetplaySession.smali.txt', 'evidence/canonical-proposed-NetplaySession.smali.txt',
        'smali/org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali',
        'native/Source/Android/jni/MainAndroid.cpp', 'audit_ownership.py', 'prepare_ownership.py', 'verify_projection.py'}
    need(required <= files.keys() and len(REPLACED) == 6, 'Closed one-class/one-native-line R147 productive closure required')
    return files


def state_fields():
    return dict(revision='R147', candidateOnly=True, diagnosticLoggerIncluded=False,
        dolphinCoreRebuiltFromQualifiedOriginal=True, promoted=False, installed=False,
        serverRegistered=False, serverRegistrationPending=True, serverKitApplied=False,
        physicalGameplayValidated=False, directV3RouteR146Preserved=True, onlineDefectsFullyFixed=False)
