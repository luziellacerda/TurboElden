"""Compose six reviewed replacements and one dedicated SNES video over exact R70.

Original signing credentials are supplied through STATION_KEYSTORE,
STATION_KEY_ALIAS, STATION_KS_PASS and STATION_KEY_PASS. They are never placed
in the receipt or printed. Temporary packaging stays on E:; the final APK is
written to a new G: path. This script does not install or access a device.
"""
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
from build_candidate import (BASE_SHA256, CLIENT_DEX_SHA256, BASE_ROOMS_DEX_SHA256,
                             DEFAULT_WORK, R67, R67_IDENTITIES, require, sha, zsha,
                             verified_sources, verified_navigation_sources)

CERTIFICATE_SHA256 = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
SNAPSHOT = Path(__file__).resolve().parent.parent
RECOVERY = SNAPSHOT.parent / 'station-online-recovery-r67-20261007'
NATIVE = SNAPSHOT / 'native-recovery'
DEFAULT_NATIVE_BUILD = r'E:\TurboStationsBuild\recovery-r71-native-20261007'
RECOVERY_MANIFEST_SHA256 = '6a4c528ab4e270fffb29a8ff78f1735bc5c9b5d9ab010e1f21c08700161b3f55'
NATIVE_MANIFEST_SHA256 = '25dbe0e0e68d4348e23bfe034ff82284f95b50743973b464ea6c0a9694383eac'
NATIVE_ORIGIN_SHA256 = '2f8a9baa651c9fa1c31988aba2fd0aa8e0c262d2e10bea1e8b8016930ff531b7'
NATIVE_RECIPE_SHA256 = '7d594d76e21cabda3375eb0f9f1295e903765d1a3d2ee798afb4e95d931e964a'
GENERATOR_SHA256 = 'c9288d51f010c0e91fdeee7680e63358307d54dee6b12eafa43d1df74b4e9bc4'
R64_ENGINES = SNAPSHOT.parent / 'station-online-controls-r64-20261007/assets/station-online/engines.json'
R64_ENGINES_SHA256 = 'c3857293e888e0fe0b81102676101b72826a29e4a4496d61b950d3c966ab2aba'
OLD_RUNTIME_SHA256 = '899e35279cf046242a7ae31f502078080bd6a94404770fe99e1e2e90be58a1ef'
CAROUSEL_SHA256 = 'ce963fe991e78f3e3af1fcab7109d7f1163d2296dd97c39f550bf8fc2509bd42'
NEW_CAROUSEL_SHA256 = '9671f553858ef1c98c320ea85cfa7aa29350c1a9c341a3fe08b8d46e4a8a48d7'
CAROUSEL_MANIFEST_SHA256 = '82fff23df292d6e1c92d61099826194d18af2ce2fc7cf3a1af44ad8fcccd79f4'
CAROUSEL_RECIPE_SHA256 = '0e6f280b9b3ff0e84ef9344bce6ee95303273f7e61396729b96fa7344ef5fe0c'
CAROUSEL_BUILD_RECEIPT_SHA256 = 'e54569413e7a176719bbdb0523bc640a683208bf9662acad8436fab701e4dc1a'
CAROUSEL_BASE_RECEIPT_SHA256 = '783edb4db4e2012e6e813eee0b01f631a6d7b6844bef97dd738daf3285a6ca11'
MEDIA_BUILD_RECEIPT_SHA256 = '6aaac36272d2020b063c67c8dacc197373dc9d5944b576477391d3483eb27e6e'
ALL_SNES_VIDEO_SHA256 = '780ad95803b649cac38e2db19a796a9f8bcc103dd0b4d9ae1cb5a7d68f54ed7e'
ALL_SNES_FRAME_SHA256 = 'c6d634be62eb13b5c4aeac70a3ff0aeeb2684bb9f0a7952665e9776f05431098'
ALL_SNES_SOURCE_SHA256 = 'db7190e5798bb0976ede2e849089ba41904084ee54c5bee9ee1806c15aeac272'
ALL_SNES_POSTER_SYMBOL = 'station_collection_r71_snes_all'
DEFAULT_CAROUSEL_BUILD = r'E:\ESTUDO APK\work\station-online-layout-r71-20261007-carousel-final'
BIOS_DEX_SHA256 = '1dcfa1e69686a326e22c54b9adc7c6013644e69d14642664e2ab7b5e2eee4ff4'
UPSTREAM_COMMIT = '69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
UPSTREAM_ARCHIVE_SHA256 = 'cecf1e3f5446724f748124d097bb9c5169c6f599404d33a8447d88fd197d17fe'
NDK = Path(r'E:\TurboEdenEngine\android-ndk-r28c')
RUNTIME_ENTRY = 'lib/arm64-v8a/libstation_retroarch.so'
ENGINES_ENTRY = 'assets/station-online/engines.json'
CAROUSEL_ENTRY = 'lib/arm64-v8a/libturbo_carousel.so'
ALL_SNES_VIDEO_ENTRY = 'assets/turbo-system-videos/720-collection-snes-all.mp4'
MANIFEST_ENTRY = 'AndroidManifest.xml'
BASE_MANIFEST_SHA256 = '1ce56b447f6f7afa1b7fbeab7a31bc0bc5d14bf823a6b14eab58be6b37624d6a'
NEW_MANIFEST_SHA256 = 'cc00ab597882646285b963cf28c7bbc25088092268450d610e35d83a7e6444c4'
MANIFEST_RECIPE_SHA256 = '86be68b02bf053bbb2ca0ee6c7c057f557b8e34190c2c1b1ac54e40ba17de3a0'
EXPECTED_REPLACEMENTS = {'classes28.dex', 'classes35.dex', MANIFEST_ENTRY,
                         RUNTIME_ENTRY, ENGINES_ENTRY, CAROUSEL_ENTRY}
EXPECTED_ADDITIONS = {ALL_SNES_VIDEO_ENTRY}


def verified_test_receipts(work, build):
    """Reject preliminary/stale tests; both suites must bind the final 198 sources."""
    local_path = SNAPSHOT / 'evidence/local-tests.json'
    interop_path = SNAPSHOT / 'evidence/recovery-interop.json'
    portability_path = SNAPSHOT / 'evidence/recovery-harness-portability.json'
    local = json.loads(local_path.read_text('utf8'))
    interop = json.loads(interop_path.read_text('utf8'))
    portability = json.loads(portability_path.read_text('utf8'))
    build_hash = sha(work / 'evidence/build.json')
    source_hashes = build['sourceHashes']
    source_map_hash = hashlib.sha256(json.dumps(source_hashes, sort_keys=True,
        separators=(',', ':')).encode('utf8')).hexdigest()
    require(build['sourceCount'] == len(source_hashes) == 198, 'Final 198-source production build required for tests')
    require(local['success'] is True and local['productionSourceCount'] == 198
            and local['baselineCountedChecks'] == 449 and local['countedChecks'] == 1152
            and local['relayDiagnosticsPassed'] is True and local['recoveryPublicVectorsPassed'] is True,
            'Complete final local suite must pass')
    binding = local['sourceBinding']
    require(binding['mode'] == 'production-dex' and binding['verifiedComposition'] is True
            and binding['sameSourcesAsProductionDex'] is True
            and binding['sourceInputsUnchangedDuringTests'] is True
            and binding['sourceHashes'] == source_hashes
            and binding['productionSourceMapSHA256'] == source_map_hash
            and binding['javaDexBuildReceiptSHA256'] == build_hash
            and binding['overlayManifestSHA256'] == build['overlayManifestSHA256'],
            'Local tests must bind this exact final production build, not a pre-build composition')
    require(local['recipeSHA256'] == sha(SNAPSHOT / 'recipes/run_tests.py')
            and local['compositionRecipeSHA256'] == build['buildRecipeSHA256'],
            'Local test/composition recipe changed after testing')
    guards = local['integrationGuards']
    require(local['integrationGuardCount'] == len(guards) == 56
            and len({item['check'] for item in guards}) == len(guards)
            and all(item['passed'] is True for item in guards), 'All 56 distinct integration guards must pass')
    expected_extras = {'StationTaskNavigationTest': 148, 'StationGameSessionLifecycleTest': 174,
        'StationRoomRosterTest': 73, 'StationRoomStartProtocolTest': 107,
        'StationRecoveryStateWireTest': 169, 'StationRecoveryVectorsHostTest': 32}
    expected_classes = {'org.emulationstation.frontend.netplay.' + name: count
                        for name, count in expected_extras.items()}
    extras = local['additionalTestResults']
    require(len(extras) == len(expected_classes)
            and {item['class']: item['checks'] for item in extras} == expected_classes
            and all(item['passed'] is True for item in extras), 'Required navigation/lifecycle/recovery test results differ')
    require(len(local['testResults']) == 10 and all(item['passed'] is True for item in local['testResults']),
            'All original API/security/relay suites must pass')
    require(local['testSourceCount'] == len(local['testSourceHashes']) == 19, 'Complete test source inventory required')
    repository = SNAPSHOT.parent.parent
    for name, expected in local['testSourceHashes'].items():
        path = (repository / name).resolve()
        require(path.is_relative_to(repository) and sha(path) == expected, 'Local test fixture changed: ' + name)
    for name in expected_extras:
        relative = (SNAPSHOT / 'tests' / (name + '.java')).relative_to(repository).as_posix()
        require(relative in local['testSourceHashes'], 'Required current fixture omitted: ' + name)
    require(local['memoryCompilerSHA256'] == sha(R67 / 'tests/MemoryCompile.java')
            and local['returnCode'] == 0 and local['diskClassFiles'] is False,
            'In-memory test compiler/result differs')
    require(interop['success'] is True and interop['sourceCount'] == 198
            and interop['productionSourceHashes'] == source_hashes
            and interop['buildReceiptSHA256'] == build_hash
            and interop['overlayManifestSHA256'] == build['overlayManifestSHA256'],
            'Recovery interop must rerun against this exact final production build')
    require(interop['recipeSHA256'] == sha(SNAPSHOT / 'tests/run_recovery_transport.py'),
            'Interop test recipe changed after execution')
    for module in ('client', 'rooms'):
        require(binding[module + 'DexSHA256'] == interop[module + 'DexSHA256'] == build[module + 'DexSHA256'],
                'Test production DEX binding differs: ' + module)
        require(interop[module + 'JarSHA256'] == build[module + 'JarSHA256'],
                'Interop must execute the final production JAR: ' + module)
    require(interop['vectors']['passed'] is True and interop['vectors']['checks'] == 32
            and interop['transport']['passed'] is True and interop['transport']['checks'] == 46
            and interop['transport']['tcpBytesVerified'] == 1620000,
            'Complete public vectors and preserved-TCP interoperability checks must pass')
    expected_interop_tests = {name: sha(RECOVERY / 'tests' / name) for name in
        ('StationRecoveryProofTest.java', 'StationRecoveryVectorsTest.java', 'StationRecoveryTransportTest.java')}
    require(interop['testSourceHashes'] == expected_interop_tests, 'Interop fixtures changed after execution')
    require(interop['serverSourceCommit'] == '32ce9d2b30bb23deef17899e10fc285f38ea81ab'
            and interop['serverSourceReceiptSHA256'] == '75a368902d882a6d994f2fdd27ca64f4c0578c8cc261a685ca8e8f180fd2f1dc'
            and interop['serverCandidateSourceFiles'] == 60, 'Interop server candidate differs')
    require(interop['windowsCertificatePortabilityAdaptation'] is True
            and interop['syntheticCertificateRawBytesPreserved'] is True
            and interop['syntheticCertificateNotInstalledInCertificateStore'] is True
            and interop['gracefulHarnessExit'] is True and interop['privateFixtureRemoved'] is True
            and interop['ownedServerStopped'] is True, 'Synthetic Windows TLS fixture cleanup proof missing')
    require(portability['success'] is True and portability['utc'] == interop['utc']
            and portability['incomingServerCommit'] == interop['serverSourceCommit']
            and portability['compiledHarnessSHA256'] == interop['compiledSyntheticHarnessSHA256']
            and portability['patchSHA256'] == interop['syntheticHarnessDiffSHA256']
            and portability['transportChecks'] == 46 and portability['certificateDERUnchanged'] is True
            and portability['temporaryKeyDisposedByGracefulShutdown'] is True
            and portability['productionSourceChanged'] is False and portability['certificateStoreInstallation'] is False,
            'Interop portability evidence must belong to this same final test run')
    paths = (local_path, interop_path, portability_path)
    fingerprints = {str(path): sha(path) for path in paths}
    proof = dict(localTestsReceiptSHA256=fingerprints[str(local_path)],
        recoveryInteropReceiptSHA256=fingerprints[str(interop_path)],
        recoveryHarnessPortabilityReceiptSHA256=fingerprints[str(portability_path)],
        localTestsRecipeSHA256=local['recipeSHA256'], recoveryInteropRecipeSHA256=interop['recipeSHA256'],
        javaDexBuildReceiptSHA256=build_hash, productionSourceMapSHA256=source_map_hash,
        productionSourceCount=198, localCountedChecks=1152, integrationGuardCount=56,
        recoveryVectorsChecks=32, recoveryTransportChecks=46, recoveryTcpBytesVerified=1620000,
        sourceBindingMode='production-dex', allTestReceiptsBoundToFinalProduction=True,
        androidExecuted=False, twoDeviceGameplayVerified=False)
    return proof, fingerprints


def verified_manifest(data):
    """Independent byte gate plus the pinned typed-attribute semantic parser."""
    recipe = SNAPSHOT / 'recipes/patch_navigation_manifest.py'
    require(sha(recipe) == MANIFEST_RECIPE_SHA256, 'Navigation Manifest patch recipe differs')
    spec = importlib.util.spec_from_file_location('r71_navigation_manifest', recipe)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    candidate, report = helper.patch_manifest(data)
    expected_report = dict(baseSHA256=BASE_MANIFEST_SHA256, resultSHA256=NEW_MANIFEST_SHA256,
        bytes=61604, component='org.emulationstation.frontend.ESActivity',
        attribute='android:launchMode', before='singleInstance', after='singleTask',
        beforeValue=3, afterValue=2, dataOffset=34584, changedByteOffsets=[34584],
        semanticChanges=1, allOtherManifestBytesPreserved=True)
    require(report == expected_report, 'Unexpected navigation Manifest semantic receipt')
    require(helper.digest(data) == BASE_MANIFEST_SHA256 and helper.digest(candidate) == NEW_MANIFEST_SHA256,
            'Navigation Manifest identities differ')
    require(len(data) == len(candidate) == 61604 and struct.unpack_from('<I', data, 34584)[0] == 3,
            'Original ESActivity launchMode bytes differ')
    expected = bytearray(data)
    struct.pack_into('<I', expected, 34584, 2)
    require(candidate == bytes(expected), 'Manifest changed beyond ESActivity singleInstance to singleTask')
    return candidate, dict(report, patchRecipeSHA256=MANIFEST_RECIPE_SHA256)


def verified_carousel(carousel_build):
    """Bind the SNES-only route, first-frame poster, tests and encoded bytes."""
    manifest_path = SNAPSHOT / 'NATIVE-CAROUSEL-MANIFEST.json'
    recipe_path = SNAPSHOT / 'recipes/build_carousel_r71.py'
    report_path = carousel_build / 'evidence/build.json'
    require(sha(manifest_path) == CAROUSEL_MANIFEST_SHA256, 'Carousel overlay manifest differs')
    require(sha(recipe_path) == CAROUSEL_RECIPE_SHA256, 'Carousel build recipe differs')
    require(sha(report_path) == CAROUSEL_BUILD_RECEIPT_SHA256, 'Reviewed carousel build receipt differs')
    require(sha(SNAPSHOT / 'evidence/carousel-build-r71.json') == CAROUSEL_BUILD_RECEIPT_SHA256,
            'Saved carousel build evidence differs')
    manifest = json.loads(manifest_path.read_text('utf8'))
    report = json.loads(report_path.read_text('utf8'))
    expected_headers = {'collection_video_policy.h', 'video720_posters.h', 'native_system_video720.h'}
    require(set(manifest['files']) == {'native-carousel/' + name for name in expected_headers},
            'Unexpected carousel overlay files')
    require(manifest['base'] == report['base'] == 'R70'
            and manifest['baseNativeSHA256'] == report['baseNativeSHA256'] == CAROUSEL_SHA256
            and report['baseReceiptSHA256'] == CAROUSEL_BASE_RECEIPT_SHA256, 'Carousel R70 ancestry differs')
    require(manifest['route'] == {'folderKind': 2, 'platformAliases': ['Super Nintendo', 'snes'],
            'excludedAliases': ['Super Nintendo - BR', 'snesbr'],
            'asset': ALL_SNES_VIDEO_ENTRY.removeprefix('assets/'), 'symbol': ALL_SNES_POSTER_SYMBOL},
            'Dedicated video must be confined to normal SNES all-games')
    require(manifest['menuTargetFPS'] == 30 and manifest['concurrentDecoders'] == 1
            and manifest['frameMetadataSlots'] == 58 and manifest['allGamesCornerPolicy'] == 'unchanged R70',
            'Carousel playback/corner policy differs')
    for name, expected in manifest['files'].items():
        require(sha(SNAPSHOT / name) == expected
                and report['nativeSources'][Path(name).name] == expected, 'Carousel overlay hash differs: ' + name)
    for name, expected in report['nativeSources'].items():
        require(sha(carousel_build / 'native' / name) == expected, 'Staged carousel source differs: ' + name)
    for name, expected in report['objects'].items():
        require(sha(name) == expected, 'Carousel linked object differs: ' + name)
    require(report['compiled'] is True and report['buildRecipeSHA256'] == CAROUSEL_RECIPE_SHA256
            and set(report['changedNativeSources']) == expected_headers and report['addedNativeSources'] == [],
            'Carousel build composition differs')
    require(report['frameMetadataSlots'] == report['packagedPosterCount'] == 58
            and report['oneDecoderPolicyPassed'] is True and report['menuTargetFPS'] == 30
            and report['mainPlatformSourceUnchanged'] is True and report['snesBRAliasUnchanged'] is True
            and report['frameRatePolicyUnchanged'] is True and report['settingsPlacementChecks'] == 60,
            'Carousel scope/playback preservation gates missing')
    for key, prefix in [('routeResult', 'PASS 3444 '), ('cornerPolicyResult', 'PASS 66 '),
                        ('navigationResult', 'PASS 3584 '), ('decoderResult', 'PASS: 199592 ')]:
        require(report[key].startswith(prefix), 'Carousel test gate missing: ' + key)
    posters = (carousel_build / 'native/video720_posters.h').read_text('utf8')
    assets = re.findall(r'\{"(turbo-system-videos/[^"]+)",\s*(\w+)\}', posters)
    require(len(assets) == len({name for name, _ in assets}) == 58,
            'Every retained-frame slot must have one unique packaged poster')
    require(assets.count((ALL_SNES_VIDEO_ENTRY.removeprefix('assets/'), ALL_SNES_POSTER_SYMBOL)) == 1,
            'Dedicated SNES poster mapping missing')
    video_source = (carousel_build / 'native/native_system_video720.h').read_text('utf8')
    require('video720FrameCount=sizeof(video720Posters)/sizeof(video720Posters[0]);' in video_source,
            'Retained-frame metadata capacity must cover all 58 posters')
    media_path = Path(report['mediaReceipt'])
    require(report['mediaReceiptSHA256'] == sha(media_path) == MEDIA_BUILD_RECEIPT_SHA256,
            'Encoded media receipt differs')
    media = json.loads(media_path.read_text('utf8'))
    require(media['sourceSHA256'] == ALL_SNES_SOURCE_SHA256 and media['asset'] == ALL_SNES_VIDEO_ENTRY
            and media['symbol'] == ALL_SNES_POSTER_SYMBOL and media['fullFrameDecodePassed'] is True,
            'Dedicated source/decoding evidence differs')
    video, frame = carousel_build / 'media/720-collection-snes-all.mp4', carousel_build / 'frames/snes-all.rgb565'
    require(sha(video) == media['outputSHA256'] == ALL_SNES_VIDEO_SHA256
            and video.stat().st_size == media['outputBytes'] == 3033869, 'Dedicated video bytes differ')
    require(sha(frame) == media['frameSHA256'] == ALL_SNES_FRAME_SHA256
            and frame.stat().st_size == media['frameBytes'] == 720 * 720 * 2, 'Dedicated first-frame poster bytes differ')
    streams = media['outputProbe']['streams']
    require(len(streams) == 1 and streams[0]['codec_type'] == 'video'
            and streams[0]['codec_name'] == 'h264' and streams[0]['width'] == streams[0]['height'] == 720
            and streams[0]['r_frame_rate'] == '30/1' and streams[0]['has_b_frames'] == 0,
            'Dedicated video must remain square 720p30 without audio or B frames')
    carousel = carousel_build / 'libturbo_carousel.so'
    require(sha(carousel) == report['nativeSHA256'] == NEW_CAROUSEL_SHA256
            and report['minimumLoadAlignment'] >= 16384, 'Carousel binary/alignment differs')
    require(len(report['videos']) == 1 and report['videos'][0] == {
            'asset': ALL_SNES_VIDEO_ENTRY.removeprefix('assets/'), 'symbol': ALL_SNES_POSTER_SYMBOL,
            'output': str(video), 'sha256': ALL_SNES_VIDEO_SHA256,
            'frameSHA256': ALL_SNES_FRAME_SHA256, 'sourceSHA256': ALL_SNES_SOURCE_SHA256},
            'Carousel build video binding differs')
    return carousel, video, report, report_path


def signature(name):
    return name.startswith('META-INF/') and name.upper().endswith(('.MF', '.SF', '.RSA', '.DSA', '.EC'))


def verified_native(native_build):
    """Require the reviewed R71 fix and preserve the imported recovery source."""
    original_manifest = RECOVERY / 'native/RECOVERY-SOURCE-MANIFEST.json'
    manifest = NATIVE / 'native/RECOVERY-SOURCE-MANIFEST.json'
    origin_path = NATIVE / 'ORIGIN.json'
    require(sha(original_manifest) == RECOVERY_MANIFEST_SHA256, 'Original recovery manifest differs')
    require(sha(manifest) == NATIVE_MANIFEST_SHA256, 'Reviewed R71 native manifest differs')
    require(sha(origin_path) == NATIVE_ORIGIN_SHA256, 'R71 native source origin differs')
    original = json.loads(original_manifest.read_text('utf8'))
    selected = json.loads(manifest.read_text('utf8'))
    origin = json.loads(origin_path.read_text('utf8'))
    require(original['upstreamCommit'] == selected['upstreamCommit'] == UPSTREAM_COMMIT,
            'Native upstream revision differs')
    require(origin['sourceCommit'] == '4d30401a80658dd56666ef10f48d9556b3fdd9e9'
            and origin['sourceManifestSHA256'] == RECOVERY_MANIFEST_SHA256, 'Native origin is not the imported recovery')
    require(set(selected['files']) == set(original['files']), 'Native input set differs')
    require(set(origin['modifiedFiles']) == {'recipes/patch_native.py', 'engine-patches/retroarch-station-recovery.patch'},
            'Unexpected native fix scope')
    for name, expected in origin['originalFiles'].items():
        require(sha(RECOVERY / name) == expected, 'Imported recovery file changed: ' + name)
        require(sha(NATIVE / name) == origin['modifiedFiles'].get(name, {}).get('after', expected),
                'R71 native source changed: ' + name)
    for name, expected in original['files'].items():
        require(origin['originalFiles'].get(name) == expected, 'Native origin omits an original input: ' + name)
        require(sha(NATIVE / name) == selected['files'][name], 'R71 native manifest mismatch: ' + name)
    for name, change in origin['modifiedFiles'].items():
        require(change['before'] == original['files'][name] and change['after'] == selected['files'][name],
                'Native fix ancestry mismatch: ' + name)
    require(sha(NATIVE / 'recipes/build_native_runtime.py') == NATIVE_RECIPE_SHA256, 'Native builder differs')
    report_path = native_build / 'result.json'
    report = json.loads(report_path.read_text('utf8'))
    runtime = native_build / 'libstation_retroarch.so'
    require(report['compiled'] is True and report['recoveryProtocol'] == 'station-stream.v2', 'Compiled recovery runtime required')
    require(report['upstreamCommit'] == UPSTREAM_COMMIT and report['upstreamArchiveSHA256'] == UPSTREAM_ARCHIVE_SHA256,
            'Native build used another upstream source')
    require(report['buildRecipeSHA256'] == NATIVE_RECIPE_SHA256 and report['recoveryInputs'] == selected['files'],
            'Native build must use the reviewed R71 recovery fix')
    require(report['ndkRevision'] == '28.2.13676358' and report['architecture'] == 'AArch64'
            and report['minAPI'] == 26 and report['minimumLoadAlignment'] >= 16384, 'Native toolchain or target differs')
    require(report['recoveryJNIExportsPresent'] is True and report['nativeActivityExportPresent'] is True,
            'Native recovery JNI/Activity exports missing')
    require(report['maximumWaitSeconds'] is None, 'A recovery wait timeout was introduced')
    require(report['patches'] == {Path(name).name: expected for name, expected in selected['files'].items()
            if name in ('engine-patches/retroarch-station-all.patch', 'engine-patches/retroarch-station-auto-password.patch')},
            'Historical runtime patches differ')
    require(sha(runtime) == report['runtimeSHA256'] != OLD_RUNTIME_SHA256
            and runtime.stat().st_size == report['runtimeBytes'], 'Native runtime bytes differ or are still legacy')
    return runtime, report, report_path


def engine_documents(runtime_sha):
    """Use the imported generator with its original R64 sibling resolution."""
    recipe = RECOVERY / 'recipes/generate_engines.py'
    require(sha(recipe) == GENERATOR_SHA256 and sha(R64_ENGINES) == R64_ENGINES_SHA256,
            'Engine generator or original R64 manifest differs')
    spec = importlib.util.spec_from_file_location('r71_recovery_engines', recipe)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    require(helper.OLD_RUNTIME == OLD_RUNTIME_SHA256, 'Generator legacy runtime identity differs')
    document, additions = helper.generate(runtime_sha)
    original = json.loads(R64_ENGINES.read_text('utf8'))
    expected = copy.deepcopy(original)
    expected_additions = []
    for engine in expected['engines']:
        require(engine['runtimeSha256'] == OLD_RUNTIME_SHA256, 'Original engine runtime identity differs')
        engine['engineId'] = engine['engineId'].removesuffix('-autopass1') + '-rs2-' + runtime_sha[:12]
        engine['runtimeSha256'] = runtime_sha
        if engine['launchReady']:
            engine['recoveryProtocol'] = 'station-stream.v2'
            expected_additions.append(dict(id=engine['engineId'], platform=engine['platform'],
                coreSha256=engine['coreSha256'], runtimeSha256=runtime_sha, recoveryProtocol='station-stream.v2'))
    expected['androidPeerPlayValidated'] = False
    require(document == expected and additions == expected_additions, 'Unexpected engine identity/configuration change')
    require(len(additions) == 2 and {item['platform'] for item in additions} == {'snes', 'megadrive'},
            'Only the existing ready engines may be registered')
    return original, document, additions


def write_derived(path, document):
    data = (json.dumps(document, indent=2) + '\n').encode('utf8')
    if path.exists():
        require(path.read_bytes() == data, 'Preserve different existing generated output: ' + path.name)
    else:
        with path.open('xb') as stream:
            stream.write(data)


def write_derived_bytes(path, data):
    if path.exists():
        require(path.read_bytes() == data, 'Preserve different existing generated output: ' + path.name)
    else:
        with path.open('xb') as stream:
            stream.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', default=DEFAULT_WORK)
    parser.add_argument('--native-build', default=DEFAULT_NATIVE_BUILD)
    parser.add_argument('--carousel-build', default=DEFAULT_CAROUSEL_BUILD)
    parser.add_argument('--output', default=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R71-Completa-20261007.apk')
    args = parser.parse_args()
    work, output = Path(args.workspace).resolve(), Path(args.output).resolve()
    native_build = Path(args.native_build).resolve()
    carousel_build = Path(args.carousel_build).resolve()
    require(work.drive.upper() == 'E:' and output.drive.upper() == 'G:', 'Use E: for packaging and G: for the final APK')
    require(native_build.drive.upper() == 'E:', 'Native build must remain on E:')
    require(carousel_build.drive.upper() == 'E:', 'Carousel build must remain on E:')
    receipt = json.loads((work / 'evidence/build.json').read_text('utf8'))
    base = Path(receipt['baseAPK']).resolve()
    unsigned = work / 'unsigned.apk'
    require(not unsigned.exists() and not output.exists(), 'Preserve existing outputs; select a fresh destination')
    require(receipt['base'] == 'R70' and receipt['compiled'] and receipt['javaBaseline'] == 'R67', 'R71 Java build receipt required')
    require(receipt['java8API34'] is True and receipt['requestProofIntegrated'] is True,
            'R67 API/security compilation gates required')
    require(receipt['inputs'] == {
        'androidJar': '6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
        'd8Jar': 'd43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0',
    }, 'Java API/D8 inputs differ from R67')
    require(receipt['baseSHA256'] == BASE_SHA256 and sha(base) == BASE_SHA256, 'Exact R70 base APK required')
    require(receipt['clientDexUnchanged'] is False
            and receipt['changedDexSlots'] == ['classes28.dex', 'classes35.dex'],
            'Only the reviewed client/navigation and rooms DEX slots may change')
    require(receipt['buildRecipeSHA256'] == sha(Path(__file__).with_name('build_candidate.py')), 'Build recipe changed after compilation')
    baseline, overlay, sources, manifest_path = verified_sources()
    navigation_guards = verified_navigation_sources(baseline, overlay, sources)
    require(receipt['navigationGuards'] == navigation_guards, 'Client navigation guards differ from compiled sources')
    client_prefix = 'client/src/java/org/emulationstation/frontend/auth/'
    client_login = client_prefix + 'LoginActivity.java'
    client_helpers = {client_prefix + name + '.java' for name in ('StationTaskNavigation', 'StationTaskPolicy')}
    require(navigation_guards['changedClientSources'] == [client_login]
            and set(navigation_guards['addedClientSources']) == client_helpers
            and set(navigation_guards['navigationSourceHashes']) == {client_login} | client_helpers,
            'Client changes must be exactly LoginActivity plus two task navigation helpers')
    require(set(navigation_guards['preservedClientSources']) ==
            {name for name in baseline if name.startswith('client/') and name != client_login},
            'Non-navigation client preservation proof is incomplete')
    require(navigation_guards['loginChange'] == 'resume existing task after authorization and storage gates',
            'Login navigation guard has an unexpected scope')
    require(receipt['r67RecipeIdentities'] == R67_IDENTITIES, 'R67 recipe identities differ')
    require(receipt['overlayManifestSHA256'] == sha(manifest_path), 'Overlay manifest changed after compilation')
    require(receipt['overlayFiles'] == {name: sha(path) for name, path in sorted(overlay.items())}, 'Overlay changed after compilation')
    require(receipt['baselineSourceHashes'] == {name: sha(path) for name, path in sorted(baseline.items())}, 'Java baseline differs')
    require(receipt['sourceHashes'] == {name: sha(path) for name, path in sorted(sources.items())}, 'Source composition differs')
    require(receipt['sourceCount'] == len(sources) == 198 and receipt['baselineSourceCount'] == 193,
            'Complete R67 plus R71 recovery/UI/navigation composition required')
    java_work = work / 'java'
    for name, expected in receipt['sourceHashes'].items():
        require(sha(java_work / name) == expected, 'Staged source differs: ' + name)
    for module in ('client', 'rooms'):
        require(sha(java_work / 'build' / (module + '.jar')) == receipt[module + 'JarSHA256'], 'Built JAR differs: ' + module)
        require(sha(java_work / 'build' / (module + '-dex/classes.dex')) == receipt[module + 'DexSHA256'], 'Built DEX differs: ' + module)
    require(receipt['baseClientDexSHA256'] == CLIENT_DEX_SHA256
            and receipt['clientDexSHA256'] != CLIENT_DEX_SHA256,
            'DEX28 must change only through the verified client navigation source composition')
    require(receipt['baseRoomsDexSHA256'] == BASE_ROOMS_DEX_SHA256, 'Baseline DEX35 differs')
    require(receipt['roomsDexSHA256'] != BASE_ROOMS_DEX_SHA256, 'No changed DEX35 to package')
    test_proof, test_fingerprints = verified_test_receipts(work, receipt)
    replacement = java_work / 'build/rooms-dex/classes.dex'
    client_replacement = java_work / 'build/client-dex/classes.dex'
    target = 'classes35.dex'
    runtime, native_report, native_report_path = verified_native(native_build)
    carousel, all_snes_video, carousel_report, carousel_report_path = verified_carousel(carousel_build)
    original_engines, engines, additions = engine_documents(native_report['runtimeSHA256'])
    engine_file = work / 'engines.json'
    additions_file = work / 'server-engine-registry-additions.json'
    manifest_file = work / 'AndroidManifest.xml'
    manifest_receipt_file = work / 'evidence/manifest-patch.json'
    spec = importlib.util.spec_from_file_location('r71_r67_dex_gates', R67 / 'recipes/dex_gates.py')
    gates = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gates)

    tools = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
    java = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
    env = dict(os.environ, TEMP=str(work / 'temp'), TMP=str(work / 'temp'))
    for name in ('STATION_KEYSTORE', 'STATION_KEY_ALIAS', 'STATION_KS_PASS', 'STATION_KEY_PASS'):
        require(bool(env.get(name)), 'Provide original signing credentials privately: ' + name)

    def run(command, label):
        process = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                                 encoding='utf8', errors='replace', env=env)
        log = process.stdout + process.stderr
        (work / 'evidence' / (label + '.log')).write_text(log, 'utf8')
        if process.returncode:
            raise RuntimeError(label + ' failed; inspect its private local log')
        return log

    require('Pkg.Revision = 28.2.13676358' in (NDK / 'source.properties').read_text('utf8'), 'NDK r28c inspection tools required')
    llvm = NDK / 'toolchains/llvm/prebuilt/windows-x86_64/bin'
    headers = run([llvm / 'llvm-readelf.exe', '-h', '-l', runtime], 'native-elf')
    symbols = run([llvm / 'llvm-nm.exe', '--defined-only', '--dynamic', runtime], 'native-exports')
    aligns = [int(line.split()[-1], 16) for line in headers.splitlines() if line.strip().startswith('LOAD ')]
    exports = ['ANativeActivity_onCreate'] + ['Java_org_emulationstation_frontend_netplay_StationRetroActivity_' + name
               for name in ('stationRecoveryControl', 'stationRecoveryStatus', 'stationRecoveryStalled')]
    require('AArch64' in headers and aligns and min(aligns) >= 16384
            and min(aligns) == native_report['minimumLoadAlignment'], 'Actual runtime ELF target/alignment differs')
    require(all(re.search(r'\b' + name + r'\b', symbols) for name in exports), 'Actual runtime JNI/Activity exports missing')
    carousel_headers = run([llvm / 'llvm-readelf.exe', '-h', '-l', carousel], 'carousel-elf')
    carousel_symbols = run([llvm / 'llvm-nm.exe', '--defined-only', '--print-size', carousel], 'carousel-posters')
    carousel_aligns = [int(line.split()[-1], 16) for line in carousel_headers.splitlines() if line.strip().startswith('LOAD ')]
    poster_symbols = [line.split() for line in carousel_symbols.splitlines() if line.endswith(' ' + ALL_SNES_POSTER_SYMBOL)]
    require('AArch64' in carousel_headers and carousel_aligns and min(carousel_aligns) >= 16384
            and min(carousel_aligns) == carousel_report['minimumLoadAlignment'], 'Actual carousel ELF target/alignment differs')
    require(len(poster_symbols) == 1 and int(poster_symbols[0][1], 16) == 720 * 720 * 2,
            'Actual carousel first-frame poster size/symbol differs')
    require(CERTIFICATE_SHA256 in run([java, '-jar', tools / 'lib/apksigner.jar', 'verify', '--print-certs', base],
                                     'base-signature'), 'Original base signer differs')
    with zipfile.ZipFile(base) as old:
        require(len(old.namelist()) == len(set(old.namelist())), 'Duplicate base APK entries')
        require(zsha(old, 'classes28.dex') == CLIENT_DEX_SHA256, 'Original client DEX28 differs')
        require(zsha(old, MANIFEST_ENTRY) == BASE_MANIFEST_SHA256, 'Original Android Manifest differs')
        require(zsha(old, target) == BASE_ROOMS_DEX_SHA256, 'Original rooms DEX35 differs')
        require(zsha(old, RUNTIME_ENTRY) == OLD_RUNTIME_SHA256, 'Original runtime is not the R70 legacy runtime')
        require(json.loads(old.read(ENGINES_ENTRY)) == original_engines, 'Original R70 engine identities/configuration differ')
        require(zsha(old, CAROUSEL_ENTRY) == CAROUSEL_SHA256, 'R70 carousel differs')
        require(ALL_SNES_VIDEO_ENTRY not in old.namelist(), 'Dedicated SNES video already exists in the base')
        require(sum(name.startswith('assets/turbo-system-videos/') and name.endswith('.mp4')
                    for name in old.namelist()) == 57, 'R70 video inventory differs')
        require(zsha(old, 'classes30.dex') == BIOS_DEX_SHA256, 'Bundled BIOS launcher DEX30 differs')
        for engine in original_engines['engines']:
            require(zsha(old, 'lib/arm64-v8a/' + engine['library']) == engine['coreSha256'],
                    'Original core differs: ' + engine['library'])
        write_derived(engine_file, engines)
        write_derived(additions_file, additions)
        manifest_bytes, manifest_report = verified_manifest(old.read(MANIFEST_ENTRY))
        write_derived_bytes(manifest_file, manifest_bytes)
        write_derived(manifest_receipt_file, manifest_report)
        # Keep the composition explicit so a separately reviewed manifest/launch change
        # can be added without conflating it with the media or recovery inputs.
        replacements = {'classes28.dex': client_replacement, target: replacement,
                        MANIFEST_ENTRY: manifest_file, RUNTIME_ENTRY: runtime,
                        ENGINES_ENTRY: engine_file, CAROUSEL_ENTRY: carousel}
        added_entries = {ALL_SNES_VIDEO_ENTRY: all_snes_video}
        require(set(replacements) == EXPECTED_REPLACEMENTS and set(added_entries) == EXPECTED_ADDITIONS,
                'Exactly six reviewed replacements and one dedicated video addition are required')
        replacement_hashes = {name: sha(path) for name, path in replacements.items()}
        added_hashes = {name: sha(path) for name, path in added_entries.items()}
        require(set(replacements).issubset(old.namelist()), 'Required replacement entry absent')
        require(set(added_entries).isdisjoint(old.namelist()), 'New media entry collides with the base')
        require(all(zsha(old, name) != expected for name, expected in replacement_hashes.items()),
                'Every one of the six replacement entries must change')
        class_gate = gates.verify_modules(old, {'classes28.dex': client_replacement.read_bytes(), target: replacement.read_bytes()})
        client_classes = gates.definitions(client_replacement.read_bytes())
        require({'Lorg/emulationstation/frontend/station/StationRequestProof;',
                 'Lorg/emulationstation/frontend/auth/LoginActivity;',
                 'Lorg/emulationstation/frontend/auth/StationTaskNavigation;',
                 'Lorg/emulationstation/frontend/auth/StationTaskPolicy;'}.issubset(client_classes),
                'Protected client or verified task navigation classes absent from DEX28')
        expected_size = base.stat().st_size + sum(path.stat().st_size for path in replacements.values()) + sum(path.stat().st_size for path in added_entries.values())
        require(shutil.disk_usage(work).free > expected_size + 64 * 1024**2, 'Insufficient E: packaging space')
        require(shutil.disk_usage(output.parent).free > expected_size + 64 * 1024**2, 'Insufficient G: final artifact space')
        with zipfile.ZipFile(unsigned, 'w', allowZip64=True) as new:
            for info in old.infolist():
                if signature(info.filename):
                    continue
                item = copy.copy(info)
                item.extra = b''
                if item.filename in replacements:
                    item.file_size = replacements[item.filename].stat().st_size
                if item.compress_type == zipfile.ZIP_STORED:
                    alignment = 16384 if item.filename.endswith('.so') else 4
                    offset = new.fp.tell() + 30 + len(item.filename.encode('utf8'))
                    if offset % alignment:
                        padding = (-(offset + 4)) % alignment
                        item.extra = struct.pack('<HH', 0xffff, padding) + bytes(padding)
                with new.open(item, 'w') as destination:
                    with (replacements[item.filename].open('rb') if item.filename in replacements else old.open(info)) as source:
                        shutil.copyfileobj(source, destination, 1024 * 1024)
            for name, source_path in sorted(added_entries.items()):
                item = zipfile.ZipInfo(name, (2026, 10, 7, 0, 0, 0))
                item.compress_type = zipfile.ZIP_STORED
                item.create_system = 3
                item.external_attr = 0o100644 << 16
                item.file_size = source_path.stat().st_size
                offset = new.fp.tell() + 30 + len(name.encode('utf8'))
                if offset % 4:
                    padding = (-(offset + 4)) % 4
                    item.extra = struct.pack('<HH', 0xffff, padding) + bytes(padding)
                with new.open(item, 'w') as destination, source_path.open('rb') as source:
                    shutil.copyfileobj(source, destination, 1024 * 1024)
    run([tools / 'zipalign.exe', '-c', '-P', '16', '4', unsigned], 'unsigned-alignment')
    run([java, '-Djava.io.tmpdir=' + str(work / 'temp'), '-jar', tools / 'lib/apksigner.jar', 'sign',
         '--alignment-preserved', 'true', '--v4-signing-enabled', 'false', '--ks', env['STATION_KEYSTORE'],
         '--ks-key-alias', env['STATION_KEY_ALIAS'], '--ks-pass', 'env:STATION_KS_PASS',
         '--key-pass', 'env:STATION_KEY_PASS', '--out', output, unsigned], 'sign')
    require(CERTIFICATE_SHA256 in run([java, '-jar', tools / 'lib/apksigner.jar', 'verify', '--print-certs', output],
                                     'signature'), 'Final signer differs from the original certificate')
    run([tools / 'zipalign.exe', '-c', '-P', '16', '4', output], 'alignment')
    changed = []
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(output) as new:
        names = {name for name in old.namelist() if not signature(name)}
        new_names = {name for name in new.namelist() if not signature(name)}
        require(new_names == names | EXPECTED_ADDITIONS and new_names - names == EXPECTED_ADDITIONS,
                'Final APK must add exactly the dedicated SNES video and remove no entries')
        require(len(new.namelist()) == len(set(new.namelist())), 'Duplicate final APK entries')
        for name in sorted(names):
            before = zsha(old, name)
            expected = replacement_hashes.get(name, before)
            require(zsha(new, name) == expected, 'APK entry bytes differ: ' + name)
            require(new.getinfo(name).compress_type == old.getinfo(name).compress_type, 'APK storage mode changed: ' + name)
            if expected != before:
                changed.append(name)
        require(changed == sorted(EXPECTED_REPLACEMENTS),
                'Exactly DEX28/35, Manifest, runtime, engines and carousel must change')
        for name, expected in added_hashes.items():
            require(zsha(new, name) == expected and new.getinfo(name).compress_type == zipfile.ZIP_STORED,
                    'New video bytes/storage mode differ: ' + name)
        final_gate = gates.verify_modules(new, {})
        require(final_gate == class_gate, 'Final DEX class gate differs')
        video_count = sum(name.startswith('assets/turbo-system-videos/') and name.endswith('.mp4') for name in new_names)
        require(video_count == 58, 'Exactly 57 preserved videos plus one new SNES all-games video required')
        require(all(new.getinfo(name).compress_type == zipfile.ZIP_STORED for name in new_names
                    if name.startswith('assets/turbo-system-videos/') and name.endswith('.mp4')),
                'All preserved/new videos must remain stored')
    require({name: sha(path) for name, path in replacements.items()} == replacement_hashes,
            'Replacement input changed during packaging')
    require({name: sha(path) for name, path in added_entries.items()} == added_hashes,
            'Added media input changed during packaging')
    require({path: sha(path) for path in test_fingerprints} == test_fingerprints,
            'A required test receipt changed during packaging')
    require(sha(work / 'evidence/build.json') == test_proof['javaDexBuildReceiptSHA256'],
            'Production build receipt changed during packaging')
    result = dict(
        createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), apk=str(output),
        sha256=sha(output), bytes=output.stat().st_size, baseSHA256=BASE_SHA256,
        certificateSHA256=CERTIFICATE_SHA256, changed=changed, added=sorted(added_entries), preservedEntries=len(names) - len(replacements),
        allPackageEntriesVerified=True, alignment16KiB=True, classGate=class_gate,
        clientDexSHA256=receipt['clientDexSHA256'], baseClientDexSHA256=CLIENT_DEX_SHA256,
        clientDexUnchanged=False, navigationGuards=navigation_guards, roomsDexSHA256=receipt['roomsDexSHA256'],
        allOtherDexPreserved=True, allOtherNativeLibrariesPreserved=True, allCoreLibrariesPreserved=True,
        runtimeSHA256=native_report['runtimeSHA256'], recoveryProtocol='station-stream.v2',
        nativeSourceManifestSHA256=NATIVE_MANIFEST_SHA256, nativeSourceOriginSHA256=NATIVE_ORIGIN_SHA256,
        originalRecoveryManifestSHA256=RECOVERY_MANIFEST_SHA256, nativeBuildReceiptSHA256=sha(native_report_path),
        nativeBuildRecipeSHA256=NATIVE_RECIPE_SHA256, recoveryJNIExportsPresent=True,
        engineManifestSHA256=replacement_hashes[ENGINES_ENTRY], engineGeneratorSHA256=GENERATOR_SHA256,
        serverRegistryAdditionsSHA256=sha(additions_file), newEngineIds=[item['id'] for item in additions],
        legacyServerRegistryMustBePreserved=True, serverRecoveryActivationRequired=True, serverActivated=False,
        videoAssetsPreserved=True, totalVideos=video_count, originalRSAIdentityPreserved=True,
        nonNavigationClientR67Preserved=True, requestProofProtocolPreserved=True,
        loginAuthorizationAndStorageGatesPreserved=True, menu30FpsPreserved=True, carouselSHA256=NEW_CAROUSEL_SHA256,
        manifestBaseSHA256=BASE_MANIFEST_SHA256, manifestSHA256=NEW_MANIFEST_SHA256,
        manifestPatchReceiptSHA256=sha(manifest_receipt_file), manifestPatchRecipeSHA256=MANIFEST_RECIPE_SHA256,
        manifestSemanticChanges=1, allOtherManifestBytesPreserved=True,
        carouselBaseSHA256=CAROUSEL_SHA256, carouselManifestSHA256=CAROUSEL_MANIFEST_SHA256,
        carouselBuildReceiptSHA256=sha(carousel_report_path), carouselBuildRecipeSHA256=CAROUSEL_RECIPE_SHA256,
        newVideoSHA256=ALL_SNES_VIDEO_SHA256, newVideoSourceSHA256=ALL_SNES_SOURCE_SHA256,
        newVideoPosterSHA256=ALL_SNES_FRAME_SHA256, newVideoReceiptSHA256=MEDIA_BUILD_RECEIPT_SHA256,
        newVideoScope='Folder kind 2 only: Super Nintendo/snes; main platforms and SNES BR preserved',
        packagedPosterCount=58, frameMetadataSlots=58, concurrentVideoDecoders=1,
        buildReceiptSHA256=sha(work / 'evidence/build.json'), packageRecipeSHA256=sha(__file__),
        testEvidence=test_proof,
        installed=False, stable=False, twoDeviceGameplayVerified=False,
    )
    (work / 'evidence/package.json').write_text(json.dumps(result, indent=2) + '\n', 'utf8')
    require(unsigned.resolve().parent == work and unsigned.name == 'unsigned.apk', 'Unexpected unsigned intermediate path')
    unsigned.unlink()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
