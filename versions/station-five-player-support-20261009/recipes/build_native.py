"""Rebuild the complete corresponding RetroArch source with NDK r28c.

The delivered runtime is already compiled and registered on the server. A new
compiler output with a different hash requires matching engine/profile records.
This recipe writes only to an explicit fresh private directory.
"""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, json, os, shutil, struct, subprocess, tarfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--ndk', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    need(1 <= args.jobs <= 16, 'Choose 1 to 16 build workers')
    need(args.work.is_absolute() and not args.work.exists(), 'Fresh absolute work directory required')
    if os.name == 'nt':
        need(args.work.drive.upper() == 'E:', 'Use E: for production build output')
    reference = json.loads((ROOT/'evidence/native-build.json').read_text())
    archive = ROOT/'native/retroarch-corresponding-source.tar.gz'
    manifest_path = ROOT/'native/CORRESPONDING-SOURCE-MANIFEST.json'
    need(sha(archive) == reference['correspondingSourceArchiveSHA256'], 'Corresponding source archive drift')
    need(sha(manifest_path) == reference['sourceManifestSHA256'], 'Source manifest drift')
    need('Pkg.Revision = 28.2.13676358' in (args.ndk/'source.properties').read_text(), 'NDK r28c required')
    args.work.mkdir(parents=True)
    with tarfile.open(archive) as source:
        members = source.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            need(not path.is_absolute() and '..' not in path.parts and path.parts[0] == SOURCE,
                 'Unexpected source archive path')
            need(member.isfile() or member.isdir(), 'Only source files and directories expected')
        source.extractall(args.work, members=members, filter='data')
    source_root = args.work/SOURCE
    expected = json.loads(manifest_path.read_text())
    actual = {p.relative_to(source_root).as_posix(): sha(p) for p in sorted(source_root.rglob('*')) if p.is_file()}
    need(actual == expected, 'Complete extracted source did not match the build manifest')
    command = [args.ndk/('ndk-build.cmd' if os.name == 'nt' else 'ndk-build'), '-j'+str(args.jobs),
        'APP_ABI=arm64-v8a', 'TARGET_ABIS=arm64-v8a', 'APP_PLATFORM=android-26',
        'NDK_NO_GL_HEADER_VER=26', 'APP_CPPFLAGS=-std=c++17', 'APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true',
        'HAVE_VULKAN=0', 'HAVE_CHEEVOS=0', 'HAVE_SAF=0', 'GIT_VERSION=',
        'NDK_OUT='+str(args.work/'obj'), 'NDK_LIBS_OUT='+str(args.work/'lib')]
    with (args.work/'native-build.private.log').open('wb') as log:
        result = subprocess.run(list(map(str, command)), cwd=source_root/'pkg/android/phoenix/jni', stdout=log, stderr=subprocess.STDOUT)
    need(result.returncode == 0, 'Native build failed; inspect the private build log')
    raw = args.work/'lib/arm64-v8a/libretroarch-activity.so'
    binary = raw.read_bytes()
    need(binary[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', binary, 18)[0] == 183, 'AArch64 ELF required')
    offset = struct.unpack_from('<Q', binary, 32)[0]
    size, count = struct.unpack_from('<HH', binary, 54)
    loads = [struct.unpack_from('<IIQQQQQQ', binary, offset+i*size) for i in range(count)]
    alignments = [p[7] for p in loads if p[0] == 1]
    need(alignments and min(alignments) >= 16384, '16 KiB load alignment required')
    host = 'windows-x86_64' if os.name == 'nt' else 'linux-x86_64'
    readelf = args.ndk/('toolchains/llvm/prebuilt/'+host+'/bin/llvm-readelf'+('.exe' if os.name == 'nt' else ''))
    symbols = subprocess.check_output([str(readelf), '--dyn-syms', '--wide', str(raw)]).decode('utf8')
    for name in ('Configure', 'Bind', 'Unbind'):
        need('Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationMultiplayer'+name in symbols,
             'Required multiplayer JNI export missing: '+name)
    delivered = args.work/'libstation_retroarch.so'
    shutil.copyfile(raw, delivered)
    receipt = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), compiled=True, maximumPlayers=5,
        runtimeSHA256=sha(delivered), runtimeBytes=delivered.stat().st_size, architecture='AArch64', minAPI=26,
        minimumLoadAlignment=min(alignments), sourceFiles=len(actual), ndkRevision='28.2.13676358',
        sourceManifestSHA256=sha(manifest_path), correspondingSourceArchiveSHA256=sha(archive),
        matchesRegisteredRuntime=sha(delivered) == reference['runtimeSHA256'],
        apkBuilt=False, installed=False, fivePhoneGameplayVerified=False)
    (args.work/'native-build.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
