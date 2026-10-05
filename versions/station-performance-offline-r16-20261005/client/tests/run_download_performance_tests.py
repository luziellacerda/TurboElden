"""Compile and run the isolated client without rewriting sources or canonical outputs."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess, json, hashlib

root = Path(__file__).resolve().parents[1]
assert root == Path(r'E:\ESTUDO APK\work\station-download-performance-20261005\client')
source, tests = root / 'src/java', root / 'tests'
build = root / 'build-agent-tests' / datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
host, android = build / 'host-classes', build / 'android-classes'
host.mkdir(parents=True, exist_ok=False)
android.mkdir()
jdk = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
jsonjar = Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
androidjar = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
sources = list(source.rglob('*.java'))
files = [p for p in sources if 'import android.' not in p.read_text(encoding='utf-8-sig')] + list(tests.glob('*.java'))
before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources + list(tests.glob('*.java'))}
subprocess.run([str(jdk / 'javac.exe'), '-encoding', 'UTF-8', '--release', '11', '-cp', str(jsonjar), '-d', str(host)] + list(map(str, files)), check=True)
results = []
names = ['StationCatalogPollTest', 'StationAutomaticCatalogTest', 'StationFoldersTest', 'StationFilesTest', 'StationApiTest', 'StationOnlineApiTest', 'StationStorageTest', 'StationCoordinatorTest', 'StationInstallerTest', 'StationClosureTest', 'StationBootstrapTest', 'StationCoverConcurrencyTest', 'StationTransferReuseTest', 'StationCoverPublicationTest', 'StationDownloadPerformanceTest']
for name in names:
    result = subprocess.run([str(jdk / 'java.exe'), '-cp', str(host) + ';' + str(jsonjar), 'org.emulationstation.frontend.station.' + name, str(build / name)], capture_output=True, text=True)
    entry = {'test': name, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    results.append(entry)
    print(result.stdout.strip(), flush=True)
    if result.returncode:
        print(result.stderr, flush=True)
        (build / 'test-results.json').write_text(json.dumps({'tests': results, 'sources': before}, indent=2), encoding='utf-8')
        raise SystemExit(result.returncode)
subprocess.run([str(jdk / 'javac.exe'), '-encoding', 'UTF-8', '--release', '8', '-cp', str(androidjar), '-d', str(android)] + list(map(str, sources)), check=True)
after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources + list(tests.glob('*.java'))}
if before != after:
    raise RuntimeError('Sources changed during validation; results do not cover one frozen source set')
(build / 'test-results.json').write_text(json.dumps({'tests': results, 'androidCompile': 'API34 Java8', 'sources': before, 'sourcesUnmodified': True}, indent=2), encoding='utf-8')
print('PASS Android API 34 source compilation (Java 8 bytecode)', flush=True)
print('RESULTS ' + str(build / 'test-results.json'), flush=True)
