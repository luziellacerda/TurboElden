"""Closed R146 v3 relay route over exact R145; private draft cannot execute."""
from pathlib import Path
import hashlib,json,re,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
SCOPE_NAME='direct-v3-relay-r146-20261014'
REPO=ROOT.parents[1] if ROOT.parent.name=='integration' else ROOT.parent/'publication-app'
BASE='275f31b34145eb77c457b1a9c09bbff4034cc28a990b74121b0b1fd4573c5df0'
BASE_BYTES=2715057167
BASE_SOURCE='25d10b2322d2e5687c9dfacc71a826c3955fad5d'
PARTITION='classes35.dex'
PARTITIONS={PARTITION}
DEX_BASE={PARTITION:'5f36d5d9b2786a2877616bedffa227f83503621ec4e7eeb24b73a19264e4f089'}
CAROUSEL='lib/arm64-v8a/libturbo_carousel.so'
CAROUSEL_SHA='2e15a9a330c2562c71574921f5558d6142e3051bba64a315434e5714f38908a9'
RETRO='ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378'
CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
ROOT_DEX={'classes.dex',*[f'classes{i}.dex' for i in range(2,41)]}
WRAPPERS={'psx':('libstation_psx_online.so','e07ec70523a93fd9020b62d6afe8f253518e7f348709b1449a4e9e620c6a0b41'),'n64':('libstation_mupen64plus_runtime.so','020ba25cb73451eb4780f2feb0239e0f4a252b65eb9c4086762fc98334a78a48'),'dolphin':('libstation_dolphin_runtime.so','6088e4d07d354dfb987ea7ede8f0e8c46ea177fc2e1acb54c3c6c4c3a6f963f6')}
REPLACED={PARTITION,'assets/station-online/engines.json',*['lib/arm64-v8a/'+v[0] for v in WRAPPERS.values()]}
CHANGED_PAYLOAD={PARTITION}
BUILD_NAMESPACE=Path('E:/StationDirectV3RelayR146-20261014')
PARENT_SCOPE='integration/sky-blue-waves-r145-20261013'
PARENT_PROOF_PATH=Path('E:/StationSkyBlueWavesR145-20261013/assembly/final-apk-proof.json')
PARENT_FINAL_PROOF_SHA='524b9a0bb0d9827cf76abb27377d69bfebd6d792b758674e6bb52ad024b9b2d2'
PARENT_SOURCE_FILES={'java/org/emulationstation/frontend/netplay/StationHyperspaceView.java': 'a7202b4a08aa0d149f423c5884992f4259179326b6fed541d080e4f2d986e77e', 'java/org/emulationstation/frontend/netplay/StationRoomsActivity.java': 'def765db4171f67c71f0a7cf3b9873a3ed7903c7b5f15da80920fedb65e4f021', 'java/org/emulationstation/frontend/sony/Ps3Activity.java': '7169d1a809bca4d693d523774648a0a8183e279c0ca61bbb3bc2a50eecf3ba7c', 'java/org/emulationstation/frontend/sony/Ps4Activity.java': '6b6b6eee62891639762e4ade42c480c195be2011a2e20c06dee07d8e401fcd5a', 'java/org/emulationstation/frontend/station/StationDownloadPanel.java': 'dff166b678ebc80b20ad4d4b32e791b3fa7ee54f4384472dd66ef0a3079b05e2', 'java/org/emulationstation/frontend/station/StationDownloadUi.java': '78aaf94a8553fcbfd4d70287437662916e8b387143685ee9c54e0cabb73c5fca', 'java/org/emulationstation/frontend/station/StationWaveBackground.java': '91972b95db7109fb0e7be2d7030b4862a7fcb5b71b8392e0d86256dbb569e027', 'native/native_space.h': '2ac9e649e27f8ed4259f01cf5116186f76b4481019f5181c36c3956ed4eb7f65', 'native/station_theme_palette.h': 'e32a61fcbbd24f522b14d78ec138ebb8edaa7a80f1f31c39b9cb03f77f516ef3', 'native/station_wave_palette.h': 'c63c0725f8446fb1cfa434a89a9bdc6f04da44280dd61fd323b0ec95b9397a97', 'recipe/assemble_apk.py': '9d9b1d12b7462393cb4b82060daf8d4136e9ab36cfc9fb47e35c620e5da52b8d', 'recipe/AssembleScopedPartition.java': 'cb05cfe93b6435908b3e492370ad89ad16299cbf03e3ffcecba8903ed420ee43', 'recipe/build_dex.py': 'a9aa2e7622083c4a3dd78187a2f665b3a044882694012c9966a88c007453f482', 'recipe/build_identity.py': '56c412e532a9eb0f965ba993ae7e145f2d18b90dfcab61ad119164738832a9c0', 'recipe/build_native.py': 'd6dae9e1b9a57ed3c4bcc0b46987e481adc449928c6e034d4030c5915729f7e1', 'recipe/common.py': 'ef255108c4304551d83b7a560eccb0ec085cd72923b141cb3e271fb2f8e484d2', 'recipe/DecodeDolphinPartition.java': '4234cefc5dd11d0f8b41a396f949f5f8d4d1fa2994639cc0cce686fdee89f156', 'recipe/verify_apk.py': '2392f169da1e0d0dbd5793e1c120e6cf4e65c8f9e7a409fba0c5180aed8db5f7', 'recipe/VerifyScopedPartition.java': 'c5d1a6f991d4fb98e2bc94c2a644a28d61a70181bfc1a85a1df0fdaacf3319ea', 'evidence/proposed-smali/classes28.dex/org/emulationstation/frontend/station/StationDownloadPanel.smali': '7a34cebba5e831d8206f1b1cecb312ec8ff62cebfd514e6c0658e93a944f223e', 'evidence/proposed-smali/classes28.dex/org/emulationstation/frontend/station/StationDownloadUi.smali': '8a25b5b574e89b3ecbbc0363b9aa2902975f74c5c621a04ea8863e32d1799201', 'evidence/proposed-smali/classes28.dex/org/emulationstation/frontend/station/StationWaveBackground.smali': '6c436ff793c9e4287cce0cb970c36a067dfcbd45f1a0a54dc33f58914fbaac46', 'evidence/proposed-smali/classes35.dex/org/emulationstation/frontend/netplay/StationHyperspaceView.smali': '97b3269bd5c11b7b383049641260df5ad416a538b28c8c07361e569ec2a5b0c3', 'evidence/proposed-smali/classes35.dex/org/emulationstation/frontend/netplay/StationRoomsActivity.smali': '93ec7c1fc1b70ebacb9956ae1f3ca36f8df1a3238e5a2fb2fe3b664b2d7d287e', 'evidence/proposed-smali/classes40.dex/org/emulationstation/frontend/sony/Ps3Activity.smali': 'e87b17f7a1ece332051abbd4c06be7bb3104d7cfd8b10929d673fca46a60b96f', 'evidence/proposed-smali/classes40.dex/org/emulationstation/frontend/sony/Ps4Activity.smali': '2cd6402d3bf862efdfd04722f6c5df6b34e64d4398f5185def64edf3f94c4a90', 'PROPOSED-SCOPE.json': '283cf29d252f875b64e0cf843e10cb2dd4d6b15c8f5e4a3381663ee4e326e562', 'evidence/java-background-scope.json': 'd4793d31921644d787e168011648764dd86b955c7628b2ec1b721ce5eab4060b', 'evidence/native-visual-scope.json': '1c8fc1bb73a953441de9bbbd1f68f42236e5e61dfcffeb955a40dcebe3be7975', 'evidence/native-palette-spec.json': 'da18018128868fe4818137a3e0abe0a6b924c173653f51461ff1bc03735666c0', 'evidence/native-inverse-map.json': '2c5db24237248854773166c57b5644e738924cfd3824786e7b9126fedbd98317', 'evidence/native-source-preservation.json': 'eae2c7e1874980720ea5770352995c8cef8c8bb5dc3c4345063ef83b32a7838d', 'evidence/native-key-provenance.json': 'a58ad94bc8a05417a7477d33b84b9d9a6b9e03b257fe4205396590697dd29755', 'evidence/native-baseline-r144-native_space.h': 'e197030037ccb922304cef57d2b99a951a952fa354bb990e8dabe6f412336725', 'evidence/native-baseline-r144-station_wave_palette.h': 'a3e42391c906fe5126b69213d97c685f4077ef6867aec4c27adbe426deea3b29', 'evidence/native-baseline-r144-station_theme_palette.h': '8a156447f7c8a8497acbfb863bd6898b10c2a7403a83f3b9afcd4fa15f6bd058'}


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
    need(result.returncode == 0, "R146 build stage failed: " + result.stderr[-1200:])
    return result.stdout.strip()


def fingerprints(archive):
    result = {}
    for kind, (library, checksum) in WRAPPERS.items():
        raw = archive.read("lib/arm64-v8a/" + library)
        need(digest(raw) == checksum, "Exact R145 wrapper required: " + kind)
        value = extract_fingerprint(raw)
        need(len(value["payloadSha256"]) == 345 and value["payloadSha256"].get(CAROUSEL) == CAROUSEL_SHA and
             all(value["payloadSha256"].get(name) == checksum for name, checksum in DEX_BASE.items()),
             "Exact 345-entry R145 payload required")
        result[kind] = value
    need(all(value["payloadSha256"] == result["psx"]["payloadSha256"] and
             value["productiveTransforms"] == result["psx"]["productiveTransforms"] for value in result.values()),
         "Inherited common payload and productive source chains differ")
    return result


def verify_parent_sources():
    need(len(PARENT_SOURCE_FILES) == 36, 'Exact 36-input R145 productive source closure required')
    for name, expected in PARENT_SOURCE_FILES.items():
        path = REPO / PARENT_SCOPE / name
        result = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                                 'show', BASE_SOURCE + ':' + PARENT_SCOPE + '/' + name], capture_output=True, timeout=90)
        need(path.is_file() and sha(path) == expected and result.returncode == 0 and digest(result.stdout) == expected,
             'Original frozen R145 source changed: ' + name)
    return PARENT_SOURCE_FILES


def verify_parent_proof(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink() and sha(path) == PARENT_FINAL_PROOF_SHA,
         'Exact signed R145 proof required')
    proof = read(path)
    need(proof.get('schema') == 'station.r145.sky-blue-waves.final.v1' and proof.get('passed') is True and
         proof.get('sourceCommit') == BASE_SOURCE and proof.get('apkSha256') == BASE and proof.get('apkBytes') == BASE_BYTES and
         proof.get('sourceFiles') == PARENT_SOURCE_FILES and proof.get('signatureCertificateSha256') == CERT and
         proof.get('v2') is proof.get('v3') is proof.get('zipAlignment16KiB') is True and
         proof.get('checkedEntries') == 13860 and proof.get('changedDexSha256', {}).get(PARTITION) == DEX_BASE[PARTITION],
         'Completed actual R145 parent proof differs')
    verify_parent_sources()
    return proof


def source_map():
    # This closure is intentionally identical to build_dex.source_map().
    files = {}
    for folder in ('recipe', 'java', 'tests', 'evidence'):
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and path.suffix in {'.py', '.java', '.smali', '.txt', '.json'}:
                need(not path.is_symlink(), 'Symbolic source refused')
                files[path.relative_to(ROOT).as_posix()] = sha(path)
    required = {'recipe/common.py', 'recipe/build_identity.py', 'recipe/assemble_apk.py', 'recipe/verify_apk.py',
        'recipe/build_dex.py', 'recipe/route_scope.py', 'recipe/AssembleScopedPartition.java',
        'recipe/VerifyScopedPartition.java', 'recipe/DecodeDolphinPartition.java',
        'evidence/route-scope.json', 'evidence/host-test-receipt.json',
        'tests/run_tests.py', 'tests/StationRelayTlsRouteProbe.java'}
    need(required <= files.keys() and len(REPLACED) == 5, 'Closed route-only R146 recipes, evidence and tests required')
    return files


def verify_commit(commit):
    need(ROOT == REPO / 'integration' / SCOPE_NAME,
         'Private preparation cannot execute production: stage the reviewed distinct R146 scope')
    need(isinstance(commit, str) and re.fullmatch('[0-9a-f]{40}', commit) and commit != BASE_SOURCE,
         'Distinct full frozen R146 source commit required')
    verify_parent_sources()
    pins = source_map()
    prefix = ROOT.relative_to(REPO).as_posix()
    for name, expected in pins.items():
        result = subprocess.run(['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                                 'show', commit + ':' + prefix + '/' + name], capture_output=True, timeout=90)
        need(result.returncode == 0 and digest(result.stdout) == expected, 'Frozen R146 source differs: ' + name)
    return pins


def isolated(path):
    output = Path(path).resolve()
    need(not output.exists() and BUILD_NAMESPACE.resolve() in output.parents and REPO not in output.parents and
         '.git' not in output.parts, 'Fresh isolated R146 output below its fixed namespace required')
    return output


def state_fields():
    return dict(revision='R146', candidateOnly=True, diagnosticLoggerIncluded=False, nativeRuntimeRebuilt=False,
        promoted=False, installed=False, serverRegistered=False, serverRegistrationPending=True,
        serverKitApplied=False, physicalGameplayValidated=False, directV3UriIntegrated=True,
        directV3TlsFactoryIntegrated=True, onlineDefectsFullyFixed=False)
