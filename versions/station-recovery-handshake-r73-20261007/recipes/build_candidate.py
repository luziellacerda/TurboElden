"""Build R73 from exact R72 plus two declared sources; preserve DEX28 byte for byte."""
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
BASE_APK = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R72-20261007.apk')
BASE_SHA256 = 'a8d3d28bb70618c52debf6e4cb0acaaf1f3bd1de19fe410dda85f6953caaec8e'
CLIENT_DEX_SHA256 = '1a04582a02804ecbe4b075dd487118a171b0b0f305dbb8884015bbede09b25d7'
BASE_ROOMS_DEX_SHA256 = '0907b8de6a7ff2653a6e8cdc53a62bbdeec1a04abda709f3ab22b90abfc1b484'
DEFAULT_WORK = r'E:\ESTUDO APK\work\station-recovery-handshake-r73-20261007-build'
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
    original = SNAPSHOT.parent / 'station-native-registration-r72-20261007'
    spec = importlib.util.spec_from_file_location('r73_frozen_r72', original / 'recipes/build_candidate.py')
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    baseline, combined, sources, _ = previous.verified_sources()
    receipt = json.loads((original / 'evidence/java-dex-build.json').read_text('utf8'))
    require({name:sha(path) for name,path in sources.items()} == receipt['sourceHashes'], 'R72 sources no longer match installed build')
    manifest_path = SNAPSHOT / 'JAVA-OVERLAY-MANIFEST.json'
    manifest = json.loads(manifest_path.read_text('utf8'))
    prefix = 'netplay-src/org/emulationstation/frontend/netplay/'
    expected = {prefix+'StationRetroActivity.java', prefix+'StationRecoveryTunnel.java'}
    require(manifest['base']=='R72' and set(manifest['files'])==expected, 'Exactly two reviewed R73 overlays required')
    actual = {p.relative_to(SNAPSHOT/'java').as_posix() for p in (SNAPSHOT/'java').rglob('*.java')}
    require(actual==expected, 'Unexpected R73 Java overlay')
    for name, digest in manifest['files'].items():
        path=SNAPSHOT/'java'/name
        require(sha(path)==digest and sha(sources[name])!=digest, 'Overlay identity mismatch: '+name)
        sources[name]=path;combined[name]=path
    require(len(sources)==198, 'Preserve full R71 composition')
    verified_navigation_sources(baseline,combined,sources)
    return baseline,combined,sources,manifest_path


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
    require(sha(base) == BASE_SHA256, 'Base must be exact installed R71 complete APK')
    with zipfile.ZipFile(base) as archive:
        require(zsha(archive, 'classes28.dex') == CLIENT_DEX_SHA256, 'R71 DEX28 identity differs')
        require(zsha(archive, 'classes35.dex') == BASE_ROOMS_DEX_SHA256, 'R71 DEX35 identity differs')
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
    require(dex_hashes['clientDexSHA256'] == CLIENT_DEX_SHA256, 'R71 DEX28 must remain identical')
    require(dex_hashes['roomsDexSHA256'] != BASE_ROOMS_DEX_SHA256, 'R73 DEX35 did not change')
    require({name: sha(java / name) for name in sources} == source_hashes, 'Compiler sources changed during the build')
    require(sha(manifest_path) == manifest_hash, 'Overlay manifest changed during compilation')
    require({name: sha(path) for name, path in sources.items()} == source_hashes,
            'Repository sources changed during compilation')
    receipt = dict(
        createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), base='R72',
        baseAPK=str(base), baseSHA256=BASE_SHA256, javaBaseline='R67',
        r67RecipeIdentities=R67_IDENTITIES, overlayManifestSHA256=manifest_hash,
        overlayFiles={name: sha(path) for name, path in sorted(overlay.items())},
        baselineSourceHashes={name: sha(path) for name, path in sorted(baseline.items())},
        sourceHashes=source_hashes, sourceCount=len(sources), baselineSourceCount=193,
        changedSources=sorted(set(overlay) & set(baseline)), addedSources=sorted(set(overlay) - set(baseline)),
        inputs=inputs, compilerSHA256={'java': sha(jdk / 'java.exe'), 'javac': sha(jdk / 'javac.exe')},
        clientJarSHA256=sha(client), roomsJarSHA256=sha(rooms), **dex_hashes,
        baseRoomsDexSHA256=BASE_ROOMS_DEX_SHA256, baseClientDexSHA256=CLIENT_DEX_SHA256, clientDexUnchanged=True,
        navigationGuards=verified_navigation_sources(baseline,overlay,sources),
        changedDexSlots=['classes35.dex'], buildRecipeSHA256=sha(__file__),
        java8API34=True, requestProofIntegrated=True, compiled=True, apkBuilt=False, installed=False,
    )
    text = json.dumps(receipt, indent=2) + '\n'
    (work / 'evidence/build.json').write_text(text, 'utf8')
    (java / 'evidence/build.json').write_text(text, 'utf8')
    print(json.dumps({name: receipt[name] for name in ('sourceCount', 'changedSources', 'addedSources',
          'clientDexSHA256', 'roomsDexSHA256', 'clientDexUnchanged', 'changedDexSlots')}, indent=2))


if __name__ == '__main__':
    main()
