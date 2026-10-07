"""Replay the R67 in-memory suite, bound to the Java inputs used for DEX28/35.

Run with Python 3 on Windows. All build/runtime temporary files stay below the
approved E: final workspace. Only a sanitized JSON receipt is written to Git.
Java 17 is intentional for host tests; Android production targets Java 8/API34.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from source_composition import SNAPSHOT, VERSIONS, sha, verified_composition

REPOSITORY = VERSIONS.parent
WORK = Path(r'E:\ESTUDO APK\work\station-collection-videos-r67-20261007-final')
JAVA = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
ANDROID = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
JSON_JAR = Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
R63 = VERSIONS / 'station-auto-access-r63-20261006' / 'tests'
R64 = VERSIONS / 'station-online-controls-r64-20261007' / 'tests'
R55 = VERSIONS / 'station-current-r55-20261006' / 'client/tests'
NETPLAY = 'org.emulationstation.frontend.netplay.'
STATION = 'org.emulationstation.frontend.station.'
# Explicit order preserves the original receipt, including shared fixture counters.
SUITE = [
    (R63 / 'StationCompactLobbyTest.java', NETPLAY + 'StationCompactLobbyTest', 107),
    (R63 / 'StationHostConnectorTest.java', NETPLAY + 'StationHostConnectorTest', 10),
    (R63 / 'StationJoinPlayerTest.java', NETPLAY + 'StationJoinPlayerTest', 20),
    (R63 / 'StationLaunchPolicyTest.java', NETPLAY + 'StationLaunchPolicyTest', 15),
    (R63 / 'StationRoomCreationTest.java', NETPLAY + 'StationRoomCreationTest', 14),
    (R63 / 'StationShortInvitationTest.java', NETPLAY + 'StationShortInvitationTest', 23),
    (R63 / 'StationSocialTest.java', NETPLAY + 'StationSocialTest', 113),
    (R64 / 'StationRelayDiagnosticsTest.java', NETPLAY + 'StationRelayDiagnosticsTest', None),
    (R55 / 'StationOnlineApiTest.java', STATION + 'StationOnlineApiTest', 27),
    (SNAPSHOT / 'tests/StationSecurityNegotiationTest.java', STATION + 'StationSecurityNegotiationTest', 120),
]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf8')).hexdigest()


def pass_lines(output):
    result = []
    for line in output.splitlines():
        if line.startswith('PASS'):
            result.append(line)
        elif line.startswith('{'):
            try:
                if json.loads(line).get('passed') is True:
                    result.append(line)
            except (ValueError, AttributeError):
                pass
    return result


def main():
    require(not sys.flags.optimize, 'Run without -O: source_composition uses assertions')
    sources = verified_composition()
    require(len(sources) == 193, 'Expected exactly 193 production Java sources')
    source_hashes = {name: sha(path) for name, path in sorted(sources.items())}
    build_path = SNAPSHOT / 'evidence/java-dex-build.json'
    build = json.loads(build_path.read_text('utf8'))
    require(source_hashes == build['sourceHashes'], 'Tests and production DEX source inputs differ')
    original_path = SNAPSHOT / 'evidence/java-memory-tests.json'
    original = json.loads(original_path.read_text('utf8'))
    test_classes = [class_name for _, class_name, _ in SUITE]
    require(original['testClasses'] == test_classes, 'Original test class order changed')
    expected_passes = pass_lines(original['stdout'])
    require(len(expected_passes) == len(SUITE), 'Original test receipt has incomplete results')
    dependencies = {'androidJar': sha(ANDROID), 'jsonJar': sha(JSON_JAR)}
    require(dependencies == {
        'androidJar': '6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
        'jsonJar': '3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796',
    }, 'External test dependency hash differs')
    require(JAVA.is_file() and WORK.is_dir(), 'Required JDK/final E: workspace is missing')
    test_sources = [path for path, _, _ in SUITE] + [R55 / 'StationApiTest.java']
    helper = SNAPSHOT / 'tests/MemoryCompile.java'
    test_hashes = {path.relative_to(REPOSITORY).as_posix(): sha(path) for path in test_sources}
    all_sources = [sources[name] for name in sorted(sources)] + test_sources
    require(len(all_sources) == original['sourceCount'] == 204, 'Expected exactly 204 compiler inputs')
    scratch_parent = WORK / 'tests'
    scratch_parent.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix='java-memory-', dir=scratch_parent))
    require(scratch.resolve().is_relative_to(WORK.resolve()), 'Temporary path escaped E: workspace')
    temp = scratch / 'temp'
    temp.mkdir()
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp))
    # JSON implementation precedes android.jar, whose org.json methods are stubs.
    classpath = os.pathsep.join(map(str, (JSON_JAR, ANDROID)))
    command = [str(JAVA), '-Djava.io.tmpdir=' + str(temp), str(helper), classpath, *test_classes]
    started = datetime.datetime.now(datetime.timezone.utc)
    result = subprocess.run(command, input='\n'.join(map(str, all_sources)) + '\n',
                            capture_output=True, text=True, encoding='utf8', errors='replace',
                            env=env, cwd=scratch, timeout=240)
    (scratch / 'stdout.log').write_text(result.stdout, 'utf8')
    (scratch / 'stderr.log').write_text(result.stderr, 'utf8')
    actual_passes = pass_lines(result.stdout)
    compiled = re.search(r'^success=true sources=(\d+) classes=(\d+) memoryBytes=(\d+)$', result.stdout, re.M)
    no_classes = not any(scratch.rglob('*.class'))
    success = (result.returncode == 0 and compiled is not None
               and int(compiled.group(1)) == 204 and actual_passes == expected_passes and no_classes)

    def sanitized(output):
        # Compiler diagnostics may include absolute source paths; no account/host paths in Git.
        for path, label in ((REPOSITORY, '<repository>'), (WORK, '<private-work>')):
            output = output.replace(str(path), label).replace(path.as_posix(), label)
        return output

    receipt = {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'startedAt': started.isoformat(),
        'success': success,
        'scope': 'Host JVM: synthetic authority and loopback TCP; no production requests or Android execution',
        'productionSourceCount': len(sources),
        'testSourceCount': len(test_sources),
        'sourceCount': len(all_sources),
        'testClassCount': len(SUITE),
        'countedChecks': sum(count or 0 for _, _, count in SUITE) if success else None,
        'relayDiagnosticsPassed': expected_passes[7] in actual_passes,
        'testClasses': test_classes,
        'testResults': [{'class': class_name, 'expectedChecks': count,
                         'passed': expected_passes[index] in actual_passes,
                         'output': expected_passes[index] if expected_passes[index] in actual_passes else None}
                        for index, (_, class_name, count) in enumerate(SUITE)],
        'compilation': {'release': 17, 'classesInMemory': int(compiled.group(2)) if compiled else None,
                        'memoryBytes': int(compiled.group(3)) if compiled else None},
        'sourceBinding': {
            'verifiedComposition': True,
            'sameSourcesAsProductionDex': True,
            'javaSourceManifestSHA256': sha(SNAPSHOT / 'JAVA-SOURCE-MANIFEST.json'),
            'javaDexBuildReceiptSHA256': sha(build_path),
            'productionSourceMapSHA256': canonical_hash(source_hashes),
            'sourceMapHashEncoding': 'UTF-8 JSON sorted keys, separators comma/colon, no final newline',
            'clientDexSHA256': build['clientDexSHA256'],
            'roomsDexSHA256': build['roomsDexSHA256'],
        },
        'testSourceHashes': test_hashes,
        'recipeSHA256': sha(__file__),
        'compositionRecipeSHA256': sha(SNAPSHOT / 'recipes/source_composition.py'),
        'memoryCompilerSHA256': sha(helper),
        'originalTestReceiptSHA256': sha(original_path),
        'inputs': dependencies,
        'javaRuntime': 'Eclipse Adoptium JDK 17.0.20.101-hotspot',
        'javaExecutableSHA256': sha(JAVA),
        'stdout': sanitized(result.stdout),
        'stderr': sanitized(result.stderr),
        'returnCode': result.returncode,
        'diskClassFiles': not no_classes,
        'dexBuilt': False,
        'apkBuilt': False,
        'installed': False,
        'androidExecuted': False,
        'productionModified': False,
    }
    destination = SNAPSHOT / 'evidence/local-tests-final.json'
    destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', 'utf8')
    require(success, 'Local suite failed; see evidence/local-tests-final.json')
    print('PASS: 449 checks plus relay diagnostics; 193 production + 11 test sources; production DEX source binding matched.')
    print('Receipt: ' + destination.relative_to(REPOSITORY).as_posix())


if __name__ == '__main__':
    main()
