"""Verify final source/artifact/receipt linkage and prepare gates; never build/sign/install."""
from pathlib import Path
import datetime, hashlib, json

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008')
JAVA = WORK / 'java-build-final'
NET = ROOT / 'java/netplay-src/org/emulationstation/frontend/netplay'
CLIENT = ROOT / 'java/client/src/java/org/emulationstation/frontend/station'
BASE_SHA = 'd7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51'
RUNTIME_SHA = '351cee4540e916468a504788911e4c5fcb4fe141e3b544b1b1255d32e1d04a26'
CORE_SHA = '0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527'
CAROUSEL_SHA = '98e951b2aad45d63ebe563de95d7a9299339928e54ce082915a147a992ab0302'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError('Duplicate JSON field: ' + key)
        result[key] = value
    return result

def load(path):
    return json.loads(Path(path).read_text('utf8'), object_pairs_hook=unique)

def require(ok, reason):
    if not ok: raise ValueError(reason)

def main():
    receipts = []
    verified = {}

    def bound(path, digest):
        path = Path(path).resolve()
        require(path.is_file() and sha(path) == digest, 'Hash mismatch: ' + str(path))
        verified[str(path)] = digest

    def mapping(base, entries):
        for name, digest in entries.items(): bound(base / name.replace('\\', '/'), digest)

    def receipt(name, kind, passed=True):
        path = ROOT / name
        data = load(path)
        if passed: require(data.get('passed') is True, 'Receipt did not pass: ' + name)
        receipts.append(dict(kind=kind, path=str(path.resolve()), sha256=sha(path)))
        return data

    def recipe(data, name, field='recipeSHA256'):
        bound(ROOT / name, data[field])

    frozen = load(ROOT / 'SOURCE-MANIFEST.json')
    build_path = JAVA / 'evidence/build.json'
    build = load(build_path)
    require(build['compiled'] is True and build['base'] == 'R76' and not build['baselineReproduced'], 'Final R77 Java build missing')
    require(build['sourceHashes'] == frozen['sources'], 'Final Java build does not match frozen source manifest')
    bound(ROOT / 'SOURCE-MANIFEST.json', build['overlayManifestSHA256'])
    recipe(build, 'recipes/build_java.py', 'buildRecipeSHA256')
    mapping(JAVA / 'java', build['sourceHashes'])
    overlays = {p.relative_to(ROOT / 'java').as_posix():sha(p) for p in (ROOT / 'java').rglob('*.java')}
    previous = load(ROOT.parent / 'station-pump-wakeup-r76-20261008/evidence/java-dex-build.json')
    require({**previous['sourceHashes'], **overlays} == frozen['sources'], 'Java snapshot composition changed')
    mapping(ROOT / 'java', overlays)
    bound(JAVA / 'java/build/client-dex/classes.dex', build['clientDexSHA256'])
    bound(JAVA / 'java/build/rooms-dex/classes.dex', build['roomsDexSHA256'])
    bound(JAVA / 'java/build/client.jar', build['clientJarSHA256'])
    bound(JAVA / 'java/build/rooms.jar', build['roomsJarSHA256'])

    data = receipt('tests/evidence/java-contract.json', 'java-contract')
    mapping(ROOT, data['sources']); recipe(data, 'tests/run_java_contract_tests.py')
    require(data['metrics']['checks'] == 1612, 'Contract test scope changed')
    data = receipt('tests/evidence/tunnel-concurrency.json', 'java-concurrency')
    mapping(NET, data['sources']); recipe(data, 'tests/run_tunnel_concurrency_tests.py')
    bound(ROOT / 'tests/StationMultiplayerTunnelConcurrencyTest.java.in', data['templateSHA256'])
    require(data['metrics']['checks'] == 148 and data['metrics']['failures'] == 0, 'Concurrency test scope changed')
    data = receipt('tests/evidence/snapshot-merge.json', 'java-snapshot')
    bound(NET / 'StationOnlineClient.java', data['sourceSHA256']); recipe(data, 'tests/run_snapshot_merge_tests.py')
    require(data['metrics']['checks'] == 90, 'Snapshot test scope changed')
    data = receipt('tests/ui-contract-guards-result.json', 'java-ui')
    mapping(NET, data['sourceHashes']); recipe(data, 'tests/run_ui_contract_guards.py')
    require(data['metrics']['checks'] == 87, 'UI contract scope changed')
    data = receipt('tests/player-info-result.json', 'java-player-info')
    bound(NET / 'StationGamePlayerInfo.java', data['sourceSHA256'])
    bound(ROOT / 'tests/StationGamePlayerInfoTest.java.in', data['testSHA256'])
    recipe(data, 'tests/run_player_info_tests.py')
    require(data['metrics']['checks'] == 188, 'Player information scope changed')
    data = receipt('tests/catalog-evidence-result.json', 'java-player-evidence')
    bound(CLIENT / 'StationCatalogPlayerEvidence.java', data['sourceSHA256'])
    bound(ROOT / 'tests/StationCatalogPlayerEvidenceTest.java.in', data['testSHA256'])
    recipe(data, 'tests/run_catalog_evidence_tests.py')
    require(data['metrics']['checks'] == 175, 'Display evidence scope changed')
    data = receipt('evidence/presence-departure.json', 'java-human-departure')
    mapping(ROOT, data['sourceHashes'])
    require(data['checks'] == 227, 'Human departure scope changed')

    server_manifest = load(ROOT / 'server/SOURCE-MANIFEST.json')
    mapping(ROOT / 'server', {e['path']:e['sha256'] for e in server_manifest['files']})
    data = receipt('server/evidence/candidate-checks.json', 'server-candidate', False)
    bound(ROOT / 'server/SOURCE-MANIFEST.json', data['sourceManifestSha256'])
    require(data['buildPassed'] is True and all(x['passed'] is True for x in data['tests']), 'Candidate server tests failed')
    require([x['checks'] for x in data['tests']] == [253,152,91], 'Server test scope changed')
    require(data['deployed'] is False and data['productionTouched'] is False, 'Candidate must remain undeployed')
    require(load(ROOT / 'server/profiles.example.json') == [], 'Do not grant catalogue approvals')
    for number, expected in [('04',117),('05',234)]:
        data = receipt('tests/evidence/transport-java-dotnet-' + number + '.json', 'java-server-tls-' + number)
        mapping(ROOT, data['javaSources']); mapping(ROOT / 'server', data['serverSources'])
        recipe(data, 'tests/run_multiplayer_transport_tests.py')
        for name, digest in data['fixtureSources'].items():
            path = ROOT.parent / 'station-online-recovery-r67-20261007/tests' / name if name == 'StationRecoveryProofTest.java' else ROOT / 'tests' / name
            bound(path, digest)
        dependency_paths = {'client.jar':Path(r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008\compiled-final\java\build\client.jar'),
            'rooms.jar':Path(r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008\compiled-final\java\build\rooms.jar'),
            'json-20250517.jar':Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar'),
            'android.jar':Path(r'G:\Android\Sdk\platforms\android-34\android.jar')}
        require(set(data['dependencyJars']) == set(dependency_paths), 'Cross-language dependency set changed')
        for name, digest in data['dependencyJars'].items(): bound(dependency_paths[name], digest)
        bound(WORK / ('transport-java-dotnet-' + number) / 'server-bin/TurboRamaSuiteOnlineServer.dll', data['serverDLLSHA256'])
        require(all(x['passed'] is True for x in data['results']) and sum(x['checks'] for x in data['results']) == expected, 'Cross-language test did not pass')
        require({x['players'] for x in data['results']} == {2,3,4}, 'Cross-language participant coverage missing')

    native = receipt('native/build-result.json', 'native-runtime', False)
    require(native['compiled'] is True and native['runtimeSHA256'] == RUNTIME_SHA, 'Wrong native candidate')
    runtime = Path(native['runtimePath']); bound(runtime, RUNTIME_SHA)
    recipe(native, 'native/build_native.py')
    bound(ROOT / 'native/OVERLAY-MANIFEST.json', native['overlayManifestSHA256'])
    mapping(ROOT / 'native/source', native['overlaySourceHashes'])
    source_manifest = WORK / 'native/baseline-source-manifest.json'
    bound(source_manifest, native['sourceManifestSHA256'])
    native_tree = WORK / ('native/RetroArch-' + native['upstreamCommit'])
    mapping(native_tree, native['overlaySourceHashes'])
    bound(runtime.parent / 'build.log', native['buildLogSHA256'])
    require(native['minimumLoadAlignment'] >= 16384 and native['androidExecuted'] is False, 'Native alignment or qualification mismatch')
    data = receipt('native/tests/native-result.json', 'native-runtime-tests')
    bound(ROOT / 'native/OVERLAY-MANIFEST.json', data['sourceManifestSHA256'])
    bound(WORK / 'native/tests/native-multiplayer.c', data['sourceSHA256'])
    require(data['stdout'] == 'PASS native-multiplayer checks=758' and data['gameplayTested'] is False, 'Native test scope changed')
    data = receipt('native/baseline-comparison.json', 'native-baseline-comparison', False)
    bound(Path(r'E:\R74fixed\libstation_retroarch.so'), data['originalSHA256'])
    rebuilt = WORK / 'native/baseline/libstation_retroarch.so'; bound(rebuilt, data['rebuiltSHA256'])
    original_bytes = Path(r'E:\R74fixed\libstation_retroarch.so').read_bytes(); rebuilt_bytes = rebuilt.read_bytes()
    offset, length = data['excludedRegion']['descriptorOffset'], data['excludedRegion']['length']
    require(offset == 736 and length == 20 and len(original_bytes) == len(rebuilt_bytes), 'Native baseline layout changed')
    require(original_bytes[:offset] == rebuilt_bytes[:offset] and original_bytes[offset+length:] == rebuilt_bytes[offset+length:], 'Native baseline differs outside documented GNU build id')

    snes = receipt('core-snes/evidence/candidate-build.json', 'native-snes', False)
    require(snes['stage'] == 'candidate' and snes['sha256'] == CORE_SHA and snes['loadAlignment'] >= 16384, 'Wrong SNES candidate')
    core = WORK / 'snes/candidate/libstation_bsnes.so'; bound(core, CORE_SHA)
    recipe(snes, 'core-snes/build_core.py')
    wrapper = WORK / 'snes/source/target-libretro/libretro.cpp'; bound(wrapper, snes['sourceWrapperSHA256'])
    data = receipt('core-snes/evidence/source.json', 'native-snes-source', False)
    recipe(data, 'core-snes/prepare_source.py'); bound(ROOT / 'core-snes/multitap-input.patch', data['patchSHA256'])
    bound(Path(r'E:\ESTUDO APK\work\station-netplay-20261004\upstream\libretro--bsnes-mercury-79d7f9de218b.zip'), data['archiveSHA256'])
    bound(wrapper, data['patchedWrapperSHA256']); require(data['changedSourceFiles'] == ['target-libretro/libretro.cpp'], 'SNES patch scope changed')
    data = receipt('core-snes/evidence/mapping-tests.json', 'native-snes-mapping', False)
    recipe(data, 'core-snes/run_input_tests.py'); bound(wrapper, data['patchedWrapperSHA256'])
    upstream_snes = Path(r'E:\ESTUDO APK\work\station-netplay-20261004\upstream\libretro--bsnes-mercury-79d7f9de218b')
    bound(upstream_snes / 'target-libretro/libretro.cpp', data['baselineWrapperSHA256'])
    bound(upstream_snes / 'sfc/controller/multitap/multitap.cpp', data['multitapSHA256'])
    bound(upstream_snes / 'sfc/system/input.hpp', data['inputEnumsSHA256'])
    bound(WORK / 'snes/tests/input_test.cpp', data['generatedTestSHA256'])
    require(data['metrics']['checks'] == 6609 and not data['metrics']['romUsed'], 'SNES mapping test scope changed')
    data = receipt('core-snes/evidence/baseline-build.json', 'native-snes-baseline', False)
    bound(WORK / 'snes/baseline/libstation_bsnes.so', data['sha256'])
    require(data['fullBinaryEqualsInstalledBaseline'] is True and data['sha256'] == 'cc14438319709f3b7868b3e652c731f6df472ff21bb01e4a65234ba2cc6f368b', 'SNES baseline differs')

    carousel = receipt('carousel/build-result.json', 'carousel', False)
    require(carousel['compiled'] is True and carousel['nativeSHA256'] == CAROUSEL_SHA, 'Wrong carousel candidate')
    carousel_file = Path(carousel['command'][carousel['command'].index('-o')+1]); bound(carousel_file, CAROUSEL_SHA)
    recipe(carousel, 'carousel/build_carousel.py')
    bound(ROOT / 'carousel/OVERLAY-MANIFEST.json', carousel['overlayManifestSHA256'])
    mapping(ROOT / 'carousel', load(ROOT / 'carousel/OVERLAY-MANIFEST.json')['sources'])
    mapping(carousel_file.parent / 'native', carousel['nativeSources'])
    for name, digest in carousel['objects'].items(): bound(Path(name), digest)
    for row in carousel['testSources'].values(): bound(Path(row['path']), row['sha256'])
    require(all(row['exitCode'] == 0 for row in carousel['executions']), 'Carousel tool invocation failed')
    require(all(str(v).startswith('PASS') for v in carousel['results'].values()), 'Carousel tests failed')
    require(carousel['baseNativeSHA256'] == carousel['baselineReproductionSHA256'] == '3c2e22bc94f3432280e2b08c2f26ab33508cd1278ee9bd750b48d45c35105a8b', 'Carousel baseline changed')
    require(carousel['mediaChanged'] is False and carousel['minimumLoadAlignment'] >= 16384, 'Carousel preservation or alignment changed')

    data = receipt('catalog/catalog-tests.json', 'catalog', False)
    bound(ROOT / 'catalog/catalog-inventory.json', data['inventorySHA256'])
    recipe(data, 'catalog/run_catalog_tests.py'); recipe(data, 'catalog/bind_content_hashes.py', 'bindingRecipeSHA256')
    require(data['checks'] == 12361 and data['inventoryRows'] == 2467 and data['romUsed'] is False, 'Catalog test scope changed')
    data = receipt('catalog/metadata-tests.json', 'catalog-metadata')
    bound(ROOT / 'catalog/catalog-game-metadata.json', data['metadataSHA256'])
    recipe(data, 'catalog/run_metadata_tests.py'); recipe(data, 'catalog/build_game_metadata.py', 'builderSHA256')
    require(data['checks'] == 73525 and data['ids'] == 2467, 'Metadata coverage changed')
    data = receipt('catalog/metadata-coverage.json', 'catalog-metadata-coverage', False)
    bound(ROOT / 'catalog/metadata-source-manifest.json', data['sourceManifestSHA256'])
    bound(ROOT / 'catalog/catalog-inventory.json', data['inventorySHA256'])
    bound(ROOT / 'catalog/catalog-game-metadata.json', data['outputSHA256'])
    require(data['contentVerifiedIds'] == 0 and data['onlineApprovedIds'] == 0 and data['allFactsComplete'] is False, 'Research must not grant approval or claim completeness')
    data = receipt('catalog/DISPLAY-SOURCE-MANIFEST.json', 'catalog-display-binding', False)
    mapping(ROOT, data['sources']); require(data['recordsApproved'] == 0, 'Unexpected display approvals')
    data = receipt('catalog/java-binding.json', 'catalog-java-binding', False)
    mapping(CLIENT, {name:row['sha256'] for name,row in data.items()})
    asset = ROOT / 'assets/station-catalog/player-evidence-v1.json'
    require(load(asset)['records'] == [], 'Do not promote research candidates to display evidence')
    proposed = load(ROOT / 'catalog/proposed-registry.json')
    require(proposed['approved'] is False and all(row['approved'] is False for row in proposed['entries']), 'Do not activate proposed game profiles')
    engines = ROOT / 'assets/station-online/engines.json'
    engine_data = load(engines)
    require(engine_data['androidPeerPlayValidated'] is False, 'Android peer play has not been qualified')
    require(all(row['runtimeSha256'] == RUNTIME_SHA for row in engine_data['engines']), 'Engine runtime differs from candidate')
    require(next(row for row in engine_data['engines'] if row['platform']=='snes')['coreSha256'] == CORE_SHA, 'Engine SNES core differs')

    # Only generate reviewed=true after every concrete linkage check has passed.
    # These gates qualify candidate packaging; they do not authorize live profiles.
    input_data = dict(schemaVersion=1, baseApkSHA256=BASE_SHA, javaBuildDirectory=str(JAVA), javaBuildReceiptSHA256=sha(build_path),
        runtime=dict(path=str(runtime),sha256=RUNTIME_SHA), snesCore=dict(path=str(core),sha256=CORE_SHA),
        engines=dict(path=str(engines.resolve()),sha256=sha(engines)), carousel=dict(path=str(carousel_file),sha256=CAROUSEL_SHA),
        catalogAssets=[dict(entry='assets/station-catalog/player-evidence-v1.json',path=str(asset.resolve()),sha256=sha(asset))])
    input_bytes = (json.dumps(input_data,indent=2)+'\n').encode('utf8')
    gates = dict(reviewed=True, version='R77', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        inputManifestSHA256=hashlib.sha256(input_bytes).hexdigest(), javaBuildReceiptSHA256=sha(build_path),
        runtimeSHA256=RUNTIME_SHA, snesCoreSHA256=CORE_SHA, carouselSHA256=CAROUSEL_SHA,
        sourceManifestSHA256=sha(ROOT/'SOURCE-MANIFEST.json'), preparationRecipeSHA256=sha(__file__),
        receiptCount=len(receipts), receipts=receipts, verifiedFileCount=len(verified),
        reviewedScope='Frozen candidate source/artifact/receipt identity only; no Android gameplay or production approval.',
        limitations=['Transport cross-tests compile the final Session/Tunnel/Wire directly and use unchanged R76 WebSocket/proof dependencies; they do not execute the complete Android API or UI.',
            'Native tests use real extracted code with synthetic core/socket boundaries; no ROM or physical multiplayer qualification.',
            'Native baseline differs only in the documented 20-byte GNU build-id; whole-file identity is not claimed.',
            'All researched catalogue profiles remain unapproved; display evidence asset is empty.',
            'No APK signing, phone installation, Git publication or server deployment is performed by this preparation.'])
    for path,digest in verified.items(): bound(path,digest)
    for row in receipts: require(sha(row['path']) == row['sha256'], 'Receipt changed during final review')
    require(sha(build_path) == input_data['javaBuildReceiptSHA256'], 'Java build receipt changed')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/java-dex-build.json').write_bytes(build_path.read_bytes())
    (ROOT/'PACKAGE-INPUTS.json').write_bytes(input_bytes)
    (ROOT/'evidence/package-gates.json').write_text(json.dumps(gates,indent=2)+'\n','utf8')
    print(json.dumps(dict(prepared=True,receipts=len(receipts),verifiedFiles=len(verified),inputsSHA256=gates['inputManifestSHA256'],gatesSHA256=sha(ROOT/'evidence/package-gates.json'),signed=False,installed=False,deployed=False)))

if __name__ == '__main__': main()
