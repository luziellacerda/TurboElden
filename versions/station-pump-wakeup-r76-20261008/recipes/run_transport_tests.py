"""Run the incoming TLS/TCP recovery fixture against the actual R76 JARs.

Uses a hash-verified export of server commit 32ce9d2, copied to a new E: test
directory before .NET builds it. NuGet restore uses an existing local feed
only. The owned loopback process and its synthetic secret fixture are removed
after the run. No production request, service, device or global SDK change.
"""
from pathlib import Path
import argparse
import datetime
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
SNAPSHOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SNAPSHOT / 'recipes'))
from build_candidate import require, sha, verified_sources
JAVA = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
ANDROID = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
JSON_JAR = Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
RECOVERY = SNAPSHOT.parent / 'station-online-recovery-r67-20261007'

FROZEN_COMMIT = '32ce9d2b30bb23deef17899e10fc285f38ea81ab'
PRODUCTION_COMMIT = 'ab192bf1585e30f303d041f13b36a1f9c96d2caa'
SERVER_RECEIPT_SHA256 = '75a368902d882a6d994f2fdd27ca64f4c0578c8cc261a685ca8e8f180fd2f1dc'
TRANSPORT_TEST_SHA256 = 'a860a4d2e5a62a85a05a855537892cafc56f23a02fdb3b3a274ad07d572d01d8'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', required=True)
    p.add_argument('--server-source', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--server-commit', choices=(FROZEN_COMMIT, PRODUCTION_COMMIT), default=PRODUCTION_COMMIT)
    p.add_argument('--server-repository', default=r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
    p.add_argument('--stress', action='store_true', help='Additional bidirectional burst, bounded credit and repeated reconnect fixture')
    p.add_argument('--dotnet', default=r'C:\Program Files\dotnet\dotnet.exe')
    p.add_argument('--local-nuget-feed', default=r'C:\Users\Admin\.nuget\packages')
    p.add_argument('--harness-tls-diagnostics', action='store_true',
                   help='Add TLS error logging to the copied synthetic harness only')
    p.add_argument('--windows-certificate', action='store_true',
                   help='Reimport the identical synthetic certificate for Windows SChannel; graceful disposal required')
    a = p.parse_args()
    work, server, out = (Path(value).resolve() for value in (a.workspace, a.server_source, a.output))
    require(out.drive.upper() == 'E:' and not out.exists(), 'Use a new E: test output directory')
    require(not sys.flags.optimize, 'Run without -O')
    baseline, _, sources, manifest_path = verified_sources()
    require(len(sources) == 201, 'Production source composition must contain 201 Java files')
    source_hashes = {name: sha(path) for name, path in sorted(sources.items())}
    build_path = work / 'evidence/build.json'
    build = json.loads(build_path.read_text('utf8'))
    require(build.get('compiled') and build['sourceHashes'] == source_hashes,
            'Transport test must use the exact R76 production source composition')
    require(build['overlayManifestSHA256'] == sha(manifest_path), 'Production overlay manifest differs')
    jars = [work / 'java/build' / (name + '.jar') for name in ('client', 'rooms')]
    for name, jar in zip(('client', 'rooms'), jars):
        require(sha(jar) == build[name + 'JarSHA256'], 'Production JAR hash differs: ' + name)
        require(sha(work / 'java/build' / (name + '-dex/classes.dex')) == build[name + 'DexSHA256'],
                'Production DEX hash differs: ' + name)
    require(sha(ANDROID) == '6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad'
            and sha(JSON_JAR) == '3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796',
            'Exact existing test dependencies required')
    require(sha(server / 'SOURCE-RECEIPT.json') == SERVER_RECEIPT_SHA256, 'Frozen server export receipt differs')
    server_receipt = json.loads((server / 'SOURCE-RECEIPT.json').read_text('utf8'))
    require(server_receipt['sourceCommit'] == FROZEN_COMMIT, 'Wrong server candidate')
    for item in server_receipt['files']:
        path = (server / item['path']).resolve()
        require(path.is_relative_to(server) and sha(path) == item['sha256'], 'Frozen server source differs')
    tests = [RECOVERY / 'tests' / name for name in
             ('StationRecoveryProofTest.java', 'StationRecoveryVectorsTest.java', 'StationRecoveryTransportTest.java')]
    require(sha(tests[-1]) == TRANSPORT_TEST_SHA256, 'Incoming transport fixture differs')
    if a.stress:
        tests.append(SNAPSHOT / 'tests/StationRecoveryTransportStressTest.java')
    test_hashes = {path.name: sha(path) for path in tests}
    require(Path(a.dotnet).is_file() and Path(a.local_nuget_feed).is_dir(), 'Use installed .NET and existing local packages')
    out.mkdir()
    for name in ('temp', 'classes', 'dotnet-home', 'packages', 'http-cache', 'server-bin'):
        (out / name).mkdir()
    local_server = out / 'server'
    server_repo = Path(a.server_repository).resolve()
    git = ['git', '-c', 'safe.directory=' + server_repo.as_posix(), '-C', str(server_repo)]
    require(subprocess.check_output(git + ['rev-parse', a.server_commit]).decode().strip() == a.server_commit, 'Server commit unavailable')
    effective_source_hashes = {}
    baseline_differences = []
    for item in server_receipt['files']:
        destination = local_server / item['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = subprocess.check_output(git + ['show', a.server_commit + ':' + item['path']])
        destination.write_bytes(data)
        effective_source_hashes[item['path']] = sha(destination)
        if sha(destination) != item['sha256']:
            baseline_differences.append(item['path'])
    expected_differences = [] if a.server_commit == FROZEN_COMMIT else ['src/TurboRamaSuiteOnlineServer/StationOnline.cs']
    require(baseline_differences == expected_differences, 'Server delta escaped the reviewed roster-only change')
    (out / 'server-source-receipt.json').write_text(json.dumps({'sourceCommit': a.server_commit, 'files': effective_source_hashes, 'differencesFromFrozen32ce': baseline_differences}, indent=2) + '\n', 'utf8')
    harness = local_server / 'tests/StationRecovery/Http.cs'
    original_harness = harness.read_text('utf8')
    source = original_harness
    if a.harness_tls_diagnostics:
        before = 'builder.Logging.ClearProviders();'
        after = ('builder.Logging.ClearProviders();builder.Logging.AddConsole();'
                 'builder.Logging.AddFilter("Microsoft.AspNetCore.Server.Kestrel.Https",LogLevel.Debug);')
        require(source.count(before) == 1, 'Unexpected synthetic TLS harness')
        source = source.replace(before, after)
    if a.windows_certificate:
        require(os.name == 'nt', 'SChannel certificate adaptation is Windows-only')
        before = 'using var certificate=certificateRequest.CreateSelfSigned(DateTimeOffset.UtcNow.AddMinutes(-1),DateTimeOffset.UtcNow.AddMinutes(30));'
        after = ('using var ephemeralCertificate=certificateRequest.CreateSelfSigned(DateTimeOffset.UtcNow.AddMinutes(-1),DateTimeOffset.UtcNow.AddMinutes(30));\n'
                 'using var certificate=new X509Certificate2(ephemeralCertificate.Export(X509ContentType.Pfx),(string?)null,X509KeyStorageFlags.UserKeySet);\n'
                 'if(!certificate.HasPrivateKey||!certificate.RawData.SequenceEqual(ephemeralCertificate.RawData))throw new InvalidOperationException("Synthetic certificate changed during Windows import");')
        require(source.count(before) == 1, 'Unexpected synthetic certificate creation')
        source = source.replace(before, after)
        before = 'await app.WaitForShutdownAsync();File.Delete(args[0]);'
        after = ('_ = Task.Run(async()=>{await Console.In.ReadLineAsync();app.Lifetime.StopApplication();});\n'
                 'await app.WaitForShutdownAsync();File.Delete(args[0]);')
        require(source.count(before) == 1, 'Unexpected synthetic harness lifetime')
        source = source.replace(before, after)
    harness.write_text(source, 'utf8')
    portability_diff = ''.join(difflib.unified_diff(original_harness.splitlines(True), source.splitlines(True),
        fromfile='incoming/tests/StationRecovery/Http.cs', tofile='scratch/tests/StationRecovery/Http.cs'))
    (out / 'harness-portability.patch').write_text(portability_diff, 'utf8')
    config = out / 'NuGet.Config'
    config.write_text('<configuration><packageSources><clear /></packageSources></configuration>\n', 'utf8')
    env = dict(os.environ, TEMP=str(out / 'temp'), TMP=str(out / 'temp'),
               DOTNET_CLI_HOME=str(out / 'dotnet-home'), DOTNET_CLI_TELEMETRY_OPTOUT='1',
               DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1', DOTNET_NOLOGO='1',
               NUGET_PACKAGES=str(out / 'packages'), NUGET_HTTP_CACHE_PATH=str(out / 'http-cache'),
               NUGET_SCRATCH=str(out / 'temp'))
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

    def run(command, label, timeout=180):
        result = subprocess.run(list(map(str, command)), cwd=out, env=env,
                                capture_output=True, text=True, encoding='utf8', errors='replace',
                                timeout=timeout, creationflags=flags)
        (out / (label + '.log')).write_text(result.stdout + result.stderr, 'utf8')
        require(result.returncode == 0, label + ' failed; inspect its private test log')
        return result.stdout

    project = local_server / 'tests/StationRecovery/Http.Tests.csproj'
    run([a.dotnet, 'restore', project, '--configfile', config, '--source', a.local_nuget_feed,
         '--packages', out / 'packages', '-p:NuGetAudit=false'], 'server-restore')
    run([a.dotnet, 'build', project, '--no-restore', '-c', 'Release', '-o', out / 'server-bin',
         '-p:NuGetAudit=false'], 'server-build')
    cp = os.pathsep.join(map(str, [JSON_JAR, ANDROID] + jars))
    run([JAVA.with_name('javac.exe'), '--release', '17', '-encoding', 'UTF-8', '-cp', cp,
         '-d', out / 'classes', *tests], 'java-fixtures')
    java = [JAVA, '-Djava.io.tmpdir=' + str(out / 'temp'), '-cp', str(out / 'classes') + os.pathsep + cp]

    def result(command, label):
        output = run(command, label, 150)
        value = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
        require(value.get('passed') is True, label + ' fixture did not pass')
        return value

    vectors = result(java + ['org.emulationstation.frontend.netplay.StationRecoveryVectorsTest',
                             RECOVERY / 'tests/contract-vectors.json'], 'vectors')
    require(vectors.get('checks') == 32, 'Original 32-vector fixture required')
    fixture = out / 'private-fixture.properties'
    process = None
    graceful_exit = False
    transport = None
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        with (out / 'server.log').open('w', encoding='utf8') as log:
            process = subprocess.Popen([a.dotnet, str(out / 'server-bin/Http.Tests.dll'), str(fixture)],
                                       cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE if a.windows_certificate else None, creationflags=flags)
            deadline = time.monotonic() + 45
            while not fixture.exists():
                require(process.poll() is None and time.monotonic() < deadline, 'Private TLS harness did not start')
                time.sleep(0.1)
            # Certificate, keys and tickets stay in the temporary fixture, never in receipts.
            transport_class = 'StationRecoveryTransportStressTest' if a.stress else 'StationRecoveryTransportTest'
            transport = result(java + ['org.emulationstation.frontend.netplay.' + transport_class, fixture], 'transport')
            expected_checks, expected_bytes = (72, 12168608) if a.stress else (46, 1620000)
            require(transport.get('checks') == expected_checks and transport.get('tcpBytesVerified') == expected_bytes,
                    'Expected every recovery interop check and exact TCP byte count')
    finally:
        if process is not None and process.poll() is None:
            if a.windows_certificate:
                try:
                    process.stdin.write(b'stop\n')
                    process.stdin.flush()
                    process.stdin.close()
                    process.wait(timeout=15)
                    graceful_exit = process.returncode == 0
                except (OSError, subprocess.TimeoutExpired):
                    pass
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        fixture.unlink(missing_ok=True)
    require(not fixture.exists() and process is not None and process.poll() is not None,
            'Owned loopback process or private fixture was not cleaned up')
    require(not a.windows_certificate or graceful_exit, 'Synthetic certificate was not disposed through graceful shutdown')
    require(source_hashes == {name: sha(path) for name, path in sorted(sources.items())}
            and all(sha(server / item['path']) == item['sha256'] for item in server_receipt['files'])
            and test_hashes == {path.name: sha(path) for path in tests}, 'Source inputs changed during interop')
    report = {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'startedAt': started,
        'success': True, 'vectors': vectors, 'transport': transport,
        'serverSourceCommit': a.server_commit, 'serverSourceReceiptSHA256': SERVER_RECEIPT_SHA256,
        'serverCandidateSourceFiles': len(server_receipt['files']),
        'serverEffectiveSourceHashes': effective_source_hashes,
        'serverDifferencesFromFrozen32ce': baseline_differences,
        'stressFixture': a.stress,
        'syntheticHarnessTlsLoggingAdded': a.harness_tls_diagnostics,
        'windowsCertificatePortabilityAdaptation': a.windows_certificate,
        'syntheticCertificateRawBytesPreserved': a.windows_certificate,
        'syntheticCertificateNotInstalledInCertificateStore': True,
        'gracefulHarnessExit': graceful_exit,
        'syntheticHarnessDiffSHA256': sha(out / 'harness-portability.patch'),
        'compiledSyntheticHarnessSHA256': sha(harness),
        'serverTestAssemblySHA256': sha(out / 'server-bin/Http.Tests.dll'),
        'serverAssemblySHA256': sha(out / 'server-bin/TurboRamaSuiteOnlineServer.dll'),
        'sourceCount': len(sources), 'productionSourceHashes': source_hashes,
        'buildReceiptSHA256': sha(build_path), 'overlayManifestSHA256': sha(manifest_path),
        'clientJarSHA256': sha(jars[0]), 'roomsJarSHA256': sha(jars[1]),
        'clientDexSHA256': build['clientDexSHA256'], 'roomsDexSHA256': build['roomsDexSHA256'],
        'testSourceHashes': test_hashes, 'recipeSHA256': sha(__file__),
        'scope': 'Actual loopback TLS/WSS .NET routes and Java bridge; native pause is synthetic, no core/gameplay',
        'localPackageFeedOnly': True, 'globalSoftwareChanged': False,
        'privateFixtureRemoved': True, 'ownedServerStopped': True,
        'productionTouched': False, 'androidExecuted': False, 'twoDeviceGameplayVerified': False,
    }
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    (out / 'result.json').write_text(encoded, 'utf8')
    evidence_name = ('stress-' if a.stress else '') + a.server_commit[:7] + ('-logging' if a.harness_tls_diagnostics else '-quiet')
    (SNAPSHOT / ('evidence/recovery-interop-' + evidence_name + '.json')).write_text(encoded, 'utf8')
    if a.windows_certificate:
        portability = {
            'utc': report['utc'], 'success': True, 'productionSourceChanged': False,
            'incomingServerCommit': a.server_commit, 'scope': 'Synthetic TLS fixture portability only',
            'observedOriginalFailure': 'Windows SChannel: platform does not support ephemeral keys; 0x8009030E',
            'originalHarnessSHA256': sha(server / 'tests/StationRecovery/Http.cs'),
            'originalHarnessLFNormalizedSHA256': hashlib.sha256(original_harness.encode('utf8')).hexdigest(),
            'compiledHarnessSHA256': sha(harness), 'patchSHA256': sha(out / 'harness-portability.patch'),
            'patch': portability_diff, 'certificateDERUnchanged': True,
            'certificateStoreInstallation': False, 'persistKeySetRequested': False,
            'temporaryKeyDisposedByGracefulShutdown': graceful_exit,
            'nativePauseSynthetic': True, 'transportChecks': transport['checks'],
        }
        (SNAPSHOT / ('evidence/recovery-harness-portability-' + evidence_name + '.json')).write_text(
            json.dumps(portability, indent=2, ensure_ascii=False) + '\n', 'utf8')
    print(json.dumps({'success': True, 'vectors': vectors['checks'], 'transport': transport['checks'],
                      'tcpBytesVerified': transport['tcpBytesVerified'], 'privateFixtureRemoved': True,
                      'ownedServerStopped': True, 'productionTouched': False}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if '--output' in sys.argv:
            failure_out = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
            if failure_out.is_dir() and failure_out.drive.upper() == 'E:':
                (failure_out / 'failure.json').write_text(json.dumps({'success': False, 'errorType': type(error).__name__, 'error': str(error), 'recipeSHA256': sha(__file__), 'productionTouched': False}, indent=2) + '\n', 'utf8')
        raise
