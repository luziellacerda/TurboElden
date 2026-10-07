"""Restore verified R67 Java, apply the R71 UI manifest, and compile on E:.

The compiler, module boundaries, Java 8/API 34 settings, deterministic JAR
timestamps and D8 arguments match R67 recipes/build_java.py. DEX28 changes only
for the authorized Login/task helpers; all other client sources stay frozen.
No APK is signed or installed by this script.

JAVA-OVERLAY-MANIFEST.json schema:
  {"base": "R67", "files": {"netplay-src/.../Example.java": "sha256"}}
Paths are relative to this snapshot's java/ directory. The manifest must list
every Java overlay file exactly, including any added presentation helper.
"""
from pathlib import Path, PurePosixPath
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
SNAPSHOT = Path(__file__).resolve().parent.parent
R67 = SNAPSHOT.parent / 'station-collection-videos-r67-20261007'
BASE_APK = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R70-20261007.apk')
BASE_SHA256 = 'c12ee4e2928a629be4a2cc6dc9201fc7c5722e21a1fa8385d21da7a7dc69a32e'
CLIENT_DEX_SHA256 = '4e912015b3daac63cf48f4621ee0022448e917927a41990e9bd22e96feecb810'
BASE_ROOMS_DEX_SHA256 = 'b3a6e8c3fe7ba30665a2c7058216f51c1ec7e39025e30de502c96466f89904bb'
DEFAULT_WORK = r'E:\ESTUDO APK\work\station-online-layout-r71-20261007-final'
CLIENT_LOGIN = 'client/src/java/org/emulationstation/frontend/auth/LoginActivity.java'
CLIENT_HELPERS = tuple('client/src/java/org/emulationstation/frontend/auth/' + name + '.java' for name in ('StationTaskNavigation', 'StationTaskPolicy'))
CLIENT_OVERLAY = (CLIENT_LOGIN,) + CLIENT_HELPERS
JAVA_PREFIXES = ('client/src/java/', 'netplay-src/', 'dependency-src/')
R67_IDENTITIES = {
    'recipes/source_composition.py': 'adbf438a0edd56c29221d253cb4cb571ac7b327ceb3ca1a431eb394a05548fcc',
    'recipes/build_java.py': '3d8d992246867ee6f79756c3f947c88a3f703c85f2e422282dfa458c6fcf39d2',
    'recipes/dex_gates.py': '3dee834410b422761a197a37669730a010dcf1e5dd194b0b74a7a58308cb6fa6',
    'JAVA-SOURCE-MANIFEST.json': 'd3053920cca98bca0bda6cb77c7115a3c53489efa2e358880d5a1790830920ce',
    'evidence/java-dex-build.json': 'ca8078d098eaacff7e1a36637dd454975827ce9cad6c2da633d34e0af5559d02',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def zsha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verified_sources():
    """Return the exact baseline, declared overlay and final compiler inputs."""
    for name, expected in R67_IDENTITIES.items():
        require(sha(R67 / name) == expected, 'R67 recipe/input identity changed: ' + name)
    spec = importlib.util.spec_from_file_location('r71_r67_source_composition', R67 / 'recipes/source_composition.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    baseline = helper.verified_composition()
    require(len(baseline) == 193, 'Expected the complete 193-source R67 composition')
    frozen = json.loads((R67 / 'JAVA-SOURCE-MANIFEST.json').read_text('utf8'))
    require(frozen['files'] == {name: sha(path) for name, path in baseline.items()},
            'Restored baseline must match every frozen R67 source hash')
    manifest_path = SNAPSHOT / 'JAVA-OVERLAY-MANIFEST.json'
    manifest = json.loads(manifest_path.read_text('utf8'))
    require(manifest.get('base') == 'R67', 'Overlay must identify the R67 Java baseline')
    declared = manifest.get('files')
    require(isinstance(declared, dict) and declared, 'An exact nonempty overlay manifest is required')
    overlay_root = (SNAPSHOT / 'java').resolve()
    actual = {p.relative_to(overlay_root).as_posix() for p in overlay_root.rglob('*.java')}
    require(actual == set(declared), 'Overlay manifest does not exactly match the Java files')
    overlay = {}
    for name, expected in declared.items():
        rel = PurePosixPath(name)
        require(isinstance(expected, str) and re.fullmatch(r'[0-9a-f]{64}', expected), 'Invalid overlay SHA: ' + name)
        require(not rel.is_absolute() and '\\' not in name and '..' not in rel.parts
                and rel.as_posix() == name and (name.startswith('netplay-src/') or name in CLIENT_OVERLAY)
                and name.endswith('.java'), 'Only netplay and the exact authorized Login/navigation paths are permitted: ' + name)
        source = (overlay_root / name).resolve()
        require(source.is_relative_to(overlay_root), 'Overlay escaped its source directory')
        require(sha(source) == expected, 'Overlay hash differs: ' + name)
        require(name not in baseline or sha(baseline[name]) != expected, 'Unchanged file should not be in the overlay: ' + name)
        overlay[name] = source
    sources = dict(baseline)
    sources.update(overlay)
    verified_navigation_sources(baseline, overlay, sources)
    return baseline, overlay, sources, manifest_path


def verified_navigation_sources(baseline, overlay, sources):
    """Bounded client change; commercial access and every other client byte remain frozen."""
    actual = {name for name in overlay if name.startswith('client/')}
    require(actual == set(CLIENT_OVERLAY), 'Client overlay escaped Login/task navigation')
    old = baseline[CLIENT_LOGIN].read_text('utf8')
    before = '        this.opening = true;\n        Intent intent = new Intent();'
    after = '        this.opening = true;\n        if(StationTaskNavigation.resumeExistingTask(this)){finish();return;}\n        Intent intent = new Intent();'
    require(old.count(before) == 1 and old.replace(before, after) == sources[CLIENT_LOGIN].read_text('utf8'),
            'Login changed outside the post-authorization task resume insertion')
    frozen = {name: sha(path) for name, path in baseline.items() if name.startswith('client/') and name != CLIENT_LOGIN}
    require(all(sha(sources[name]) == expected for name, expected in frozen.items()), 'Non-navigation client source changed')
    return dict(changedClientSources=[CLIENT_LOGIN], addedClientSources=list(CLIENT_HELPERS),
                baselineLoginSHA256=sha(baseline[CLIENT_LOGIN]), preservedClientSources=frozen,
                navigationSourceHashes={name: sha(sources[name]) for name in CLIENT_OVERLAY},
                loginChange='resume existing task after authorization and storage gates')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=DEFAULT_WORK)
    parser.add_argument('--base-apk', default=str(BASE_APK))
    args = parser.parse_args()
    work = Path(args.output).resolve()
    base = Path(args.base_apk).resolve()
    require(work.drive.upper() == 'E:' and not work.exists(), 'Use a new, nonexistent E: build directory')
    baseline, overlay, sources, manifest_path = verified_sources()
    manifest_hash = sha(manifest_path)
    require(sha(base) == BASE_SHA256, 'Base must be the exact installed R70 APK')
    with zipfile.ZipFile(base) as archive:
        require(zsha(archive, 'classes28.dex') == CLIENT_DEX_SHA256, 'R70 DEX28 identity differs')
        require(zsha(archive, 'classes35.dex') == BASE_ROOMS_DEX_SHA256, 'R70 DEX35 identity differs')
    sdk = Path(r'G:\Android\Sdk')
    jdk = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
    android = sdk / 'platforms/android-34/android.jar'
    d8 = sdk / 'build-tools/34.0.0/lib/d8.jar'
    inputs = {'androidJar': sha(android), 'd8Jar': sha(d8)}
    require(inputs == {
        'androidJar': '6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
        'd8Jar': 'd43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0',
    }, 'Use the verified R67 Android SDK/D8 inputs')
    require(shutil.disk_usage(work.parent).free > 256 * 1024**2, 'Insufficient space for Java restoration/build')
    work.mkdir()
    java = work / 'java'
    for directory in (work / 'temp', work / 'evidence', java, java / 'build', java / 'evidence'):
        directory.mkdir()
    env = dict(os.environ, TEMP=str(work / 'temp'), TMP=str(work / 'temp'))
    source_hashes = {name: sha(source) for name, source in sorted(sources.items())}
    for name, source in sorted(sources.items()):
        destination = java / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        require(sha(destination) == source_hashes[name], 'Staged source mismatch: ' + name)

    def run(command, label):
        result = subprocess.run(list(map(str, command)), capture_output=True, env=env)
        (work / 'evidence' / (label + '.log')).write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(label + ' failed; inspect the private build log')

    def compile_module(name, prefixes, classpath):
        classes = java / 'build' / (name + '-classes')
        classes.mkdir()
        paths = sorted(java / rel for rel in sources if rel.startswith(prefixes))
        options = ['-encoding', 'UTF-8', '--release', '8', '-proc:none', '-cp', classpath,
                   '-d', str(classes)] + list(map(str, paths))
        argfile = java / 'build' / (name + '.args')
        argfile.write_text('\n'.join('"' + value.replace('\\', '/') + '"' for value in options), 'utf8')
        run([jdk / 'javac.exe', '-J-Djava.io.tmpdir=' + str(work / 'temp'), '@' + str(argfile)], name + '-javac')
        jar = java / 'build' / (name + '.jar')
        with zipfile.ZipFile(jar, 'w', zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(classes.rglob('*.class')):
                info = zipfile.ZipInfo(source.relative_to(classes).as_posix(), (2026, 10, 7, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, source.read_bytes())
        return jar

    client = compile_module('client', ('client/src/java/',), str(android))
    rooms = compile_module('rooms', ('netplay-src/', 'dependency-src/'), str(android) + os.pathsep + str(client))
    dex_hashes = {}
    for name, jar in [('client', client), ('rooms', rooms)]:
        dex = java / 'build' / (name + '-dex')
        dex.mkdir()
        command = [jdk / 'java.exe', '-Djava.io.tmpdir=' + str(work / 'temp'), '-cp', d8,
                   'com.android.tools.r8.D8', '--min-api', '26', '--lib', android, '--output', dex]
        if name == 'rooms':
            command += ['--classpath', client]
        run(command + [jar], name + '-d8')
        require(sorted(p.name for p in dex.iterdir()) == ['classes.dex'], 'Unexpected DEX module split: ' + name)
        dex_hashes[name + 'DexSHA256'] = sha(dex / 'classes.dex')
    require(dex_hashes['clientDexSHA256'] != CLIENT_DEX_SHA256, 'Authorized Login/navigation DEX28 did not change')
    require(dex_hashes['roomsDexSHA256'] != BASE_ROOMS_DEX_SHA256, 'R71 DEX35 did not change')
    require({name: sha(java / name) for name in sources} == source_hashes, 'Compiler sources changed during the build')
    require(sha(manifest_path) == manifest_hash, 'Overlay manifest changed during compilation')
    require({name: sha(path) for name, path in sources.items()} == source_hashes,
            'Repository sources changed during compilation')
    receipt = dict(
        createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), base='R70',
        baseAPK=str(base), baseSHA256=BASE_SHA256, javaBaseline='R67',
        r67RecipeIdentities=R67_IDENTITIES, overlayManifestSHA256=manifest_hash,
        overlayFiles={name: sha(path) for name, path in sorted(overlay.items())},
        baselineSourceHashes={name: sha(path) for name, path in sorted(baseline.items())},
        sourceHashes=source_hashes, sourceCount=len(sources), baselineSourceCount=193,
        changedSources=sorted(set(overlay) & set(baseline)), addedSources=sorted(set(overlay) - set(baseline)),
        inputs=inputs, compilerSHA256={'java': sha(jdk / 'java.exe'), 'javac': sha(jdk / 'javac.exe')},
        clientJarSHA256=sha(client), roomsJarSHA256=sha(rooms), **dex_hashes,
        baseRoomsDexSHA256=BASE_ROOMS_DEX_SHA256, baseClientDexSHA256=CLIENT_DEX_SHA256, clientDexUnchanged=False,
        navigationGuards=verified_navigation_sources(baseline,overlay,sources),
        changedDexSlots=['classes28.dex','classes35.dex'], buildRecipeSHA256=sha(__file__),
        java8API34=True, requestProofIntegrated=True, compiled=True, apkBuilt=False, installed=False,
    )
    text = json.dumps(receipt, indent=2) + '\n'
    (work / 'evidence/build.json').write_text(text, 'utf8')
    (java / 'evidence/build.json').write_text(text, 'utf8')
    print(json.dumps({name: receipt[name] for name in ('sourceCount', 'changedSources', 'addedSources',
          'clientDexSHA256', 'roomsDexSHA256', 'clientDexUnchanged', 'changedDexSlots')}, indent=2))


if __name__ == '__main__':
    main()
