# SPDX-License-Identifier: GPL-3.0-or-later
"""Build only a separate JNI audit JAR. Never executes Android or modifies an APK."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
RUNTIME_SHA256 = 'ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('jdk-bin', 'd8-jar', 'android-jar', 'sidecar', 'sidecar-receipt', 'runtime', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    require(re.fullmatch('[0-9a-f]{40}', args.source_commit), 'Frozen source commit required')
    require(args.output.is_absolute(), 'Fresh absolute output required')
    args.output = args.output.resolve()
    require(not args.output.exists(), 'Output already exists')
    for protected in (REPO.resolve(), args.jdk_bin.resolve(), args.d8_jar.resolve().parent,
                      args.android_jar.resolve().parent, args.runtime.resolve().parent, args.sidecar.resolve().parent):
        require(not args.output.is_relative_to(protected), 'Output overlaps a protected input directory')
    require(digest(args.runtime) == RUNTIME_SHA256, 'Exact R139 runtime required')
    receipt = json.loads(args.sidecar_receipt.read_text('utf-8'))
    require(receipt.get('compiled') is True and receipt.get('diagnosticOnly') is True
            and receipt.get('unchangedRuntimeSha256') == RUNTIME_SHA256
            and receipt.get('sourceCommit') == args.source_commit
            and receipt.get('sidecarSha256') == digest(args.sidecar), 'Qualified sidecar build receipt required')
    inputs = {}
    for path in (ROOT / 'StationStartupLogging.java', Path(__file__).resolve()):
        relative = path.relative_to(REPO).as_posix()
        data = subprocess.check_output(['git', '-C', str(REPO), 'show', args.source_commit + ':' + relative], timeout=30)
        require(path.read_bytes() == data, 'Probe differs from the frozen commit')
        inputs[relative] = hashlib.sha256(data).hexdigest()
    args.output.mkdir(parents=True, exist_ok=False)
    classes = args.output / 'classes'; classes.mkdir()
    java = args.jdk_bin / 'java.exe'; javac = args.jdk_bin / 'javac.exe'
    process = subprocess.run([str(javac), '--release', '8', '-encoding', 'UTF-8', '-d', str(classes),
                              str(ROOT / 'StationStartupLogging.java')], capture_output=True, timeout=60)
    (args.output / 'javac.log').write_bytes(process.stdout + process.stderr)
    require(process.returncode == 0, 'Probe Java compilation failed')
    dex = args.output / 'dex'; dex.mkdir()
    process = subprocess.run([str(java), '-cp', str(args.d8_jar), 'com.android.tools.r8.D8', '--release',
                              '--min-api', '26', '--lib', str(args.android_jar), '--output', str(dex),
                              *[str(path) for path in sorted(classes.rglob('*.class'))]], capture_output=True, timeout=60)
    (args.output / 'd8.log').write_bytes(process.stdout + process.stderr)
    require(process.returncode == 0 and sorted(path.name for path in dex.iterdir()) == ['classes.dex'], 'Probe D8 failed')
    jar = args.output / 'logging-probe.jar'
    entry = zipfile.ZipInfo('classes.dex', (2026, 10, 13, 0, 0, 0)); entry.compress_type = zipfile.ZIP_STORED
    with zipfile.ZipFile(jar, 'x') as archive:
        archive.writestr(entry, (dex / 'classes.dex').read_bytes())
    result = dict(schemaVersion=1, diagnosticOnly=True, sourceCommit=args.source_commit, sourceFiles=inputs,
                  sidecarSha256=digest(args.sidecar), sidecarBuildReceiptSha256=digest(args.sidecar_receipt),
                  unchangedRuntimeSha256=RUNTIME_SHA256, jarSha256=digest(jar), jarBytes=jar.stat().st_size,
                  javaSha256=digest(java), javacSha256=digest(javac), d8JarSha256=digest(args.d8_jar),
                  androidJarSha256=digest(args.android_jar), minimumApi=26, plannedCases=7,
                  built=True, androidExecuted=False, apkInstalled=False, nativeActivityStarted=False,
                  gameplayValidated=False)
    (args.output / 'probe-build-receipt.json').write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps({'built': True, 'jarBytes': result['jarBytes'], 'androidExecuted': False}))


if __name__ == '__main__':
    main()
