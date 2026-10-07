"""Build the Station runtime from the exact official source plus both published patches."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, zipfile

PIN = '69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
ARCHIVE_SHA = 'cecf1e3f5446724f748124d097bb9c5169c6f599404d33a8447d88fd197d17fe'
p = argparse.ArgumentParser()
p.add_argument('--source-zip', required=True, help='https://codeload.github.com/libretro/RetroArch/zip/' + PIN)
p.add_argument('--ndk', required=True)
p.add_argument('--output', required=True)
p.add_argument('--jobs', type=int, default=4)
a = p.parse_args()
snapshot = Path(__file__).resolve().parent.parent
out = Path(a.output).resolve()
ndk = Path(a.ndk).resolve()
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
if out.exists(): raise SystemExit('Use a new output directory')
if sha(a.source_zip) != ARCHIVE_SHA: raise SystemExit('Exact original RetroArch source archive required')
if 'Pkg.Revision = 28.2.13676358' not in (ndk / 'source.properties').read_text(): raise SystemExit('NDK r28c required')
if not 1 <= a.jobs <= 16: raise SystemExit('Use 1 to 16 build jobs')
out.mkdir(parents=True)
with zipfile.ZipFile(a.source_zip) as z:
    for entry in z.infolist():
        if not entry.filename.startswith('RetroArch-' + PIN + '/') or '..' in Path(entry.filename).parts:
            raise SystemExit('Unexpected source archive path')
    z.extractall(out)
src = out / ('RetroArch-' + PIN)
patches = [snapshot / 'engine-patches/retroarch-station-all.patch',
           snapshot / 'engine-patches/retroarch-station-auto-password.patch']
for name in re.findall(r'^--- a/(.+)$', patches[0].read_text(), re.M):
    f = src / name
    f.write_text(f.read_text(), newline='\n')
for patch in patches:
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=src, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=src, check=True)
from patch_native import apply
apply(src)
jni = src / 'pkg/android/phoenix-common/jni'
cmd = [str(ndk / ('ndk-build.cmd' if os.name == 'nt' else 'ndk-build')),
       'NDK_PROJECT_PATH=' + str(src / 'pkg/android/phoenix-common'),
       'APP_BUILD_SCRIPT=' + str(jni / 'Android.mk'), 'NDK_APPLICATION_MK=' + str(jni / 'Application.mk'),
       'NDK_OUT=' + str(out / 'obj'), 'NDK_LIBS_OUT=' + str(out / 'lib'),
       'APP_ABI=arm64-v8a', 'TARGET_ABIS=arm64-v8a', 'APP_PLATFORM=android-26',
       'NDK_NO_GL_HEADER_VER=26', 'APP_CPPFLAGS=-std=c++17', 'APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true',
       'HAVE_VULKAN=0', 'HAVE_CHEEVOS=0', 'HAVE_SAF=0', 'GIT_VERSION=',
       '-j' + str(a.jobs)]
with (out / 'build.log').open('w') as log:
    result = subprocess.run(cmd, cwd=jni, stdout=log, stderr=subprocess.STDOUT)
if result.returncode: raise SystemExit('Native build failed; inspect build.log')
binary = out / 'lib/arm64-v8a/libretroarch-activity.so'
dest = out / 'libstation_retroarch.so'
shutil.copyfile(binary, dest)
tool = ndk / ('toolchains/llvm/prebuilt/windows-x86_64/bin' if os.name == 'nt' else 'toolchains/llvm/prebuilt/linux-x86_64/bin')
suffix = '.exe' if os.name == 'nt' else ''
headers = subprocess.check_output([str(tool / ('llvm-readelf' + suffix)), '-h', '-l', str(dest)], text=True)
symbols = subprocess.check_output([str(tool / ('llvm-nm' + suffix)), '--defined-only', '--dynamic', str(dest)], text=True)
aligns = [int(line.split()[-1], 16) for line in headers.splitlines() if line.strip().startswith('LOAD ')]
if 'AArch64' not in headers or not aligns or min(aligns) < 16384 or not re.search(r'\bANativeActivity_onCreate\b', symbols):
    raise SystemExit('Invalid architecture, alignment or NativeActivity export')
exports = ['Java_org_emulationstation_frontend_netplay_StationRetroActivity_'+name for name in ('stationRecoveryControl','stationRecoveryStatus','stationRecoveryStalled')]
if not all(re.search(r'\b'+name+r'\b',symbols) for name in exports):raise SystemExit('All recovery JNI exports required')
inputs=json.loads((snapshot/'native/RECOVERY-SOURCE-MANIFEST.json').read_text())['files']
if inputs!={name:sha(snapshot/name) for name in inputs}:raise SystemExit('Exact recovery native inputs required')
report = {'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'compiled': True,
          'upstreamCommit': PIN, 'upstreamArchiveSHA256': ARCHIVE_SHA, 'ndkRevision': '28.2.13676358',
          'runtimeSHA256': sha(dest), 'runtimeBytes': dest.stat().st_size, 'minimumLoadAlignment': min(aligns),
          'recoveryJNIExportsPresent':True,'recoveryInputs':inputs,'buildRecipeSHA256':sha(__file__),'architecture': 'AArch64', 'nativeActivityExportPresent': True, 'minAPI': 26,
          'patches': {f.name: sha(f) for f in patches}, 'command': cmd,
          'recoveryProtocol':'station-stream.v2', 'maximumWaitSeconds':None, 'androidExecuted': False, 'apkBuilt': False, 'installed': False, 'twoDeviceGameplayVerified': False}
(out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
