"""Build only JNI and carousel from isolated changed files plus current R15 inputs."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

root = Path(__file__).resolve().parents[1]
base = Path(r'E:\ESTUDO APK\work\station-download-performance-20261005')
bin_dir = Path(r'E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin')
compiler = bin_dir / 'clang++.exe'
output = base / 'native-build'
output.mkdir(exist_ok=True)
temporary = output / 'tmp'
temporary.mkdir(exist_ok=True)
os.environ['TEMP'] = os.environ['TMP'] = str(temporary)
common = [str(compiler), '--target=aarch64-linux-android26', '-std=c++17', '-shared', '-fPIC', '-O2',
          '-Wl,-z,max-page-size=16384', '-Wl,--no-undefined']
commands = [
    [r'C:\Program Files\LLVM\bin\clang++.exe', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
     str(root / 'native-tests/transfer-rate-phases.cpp'), '-o', str(output / 'transfer-rate-phases.exe')],
    [*common, '-fvisibility=hidden', '-Wall', '-Wextra', '-Werror', '-Wno-return-type-c-linkage',
     '-static-libstdc++', '-Wl,--exclude-libs,ALL', '-I', str(base / 'client/src/native'),
     str(root / 'client/src/native/station_frontend.cpp'), '-ldl', '-llog',
     '-o', str(output / 'libstation_frontend.so')],
    [*common, '-nostdlib', '-fno-exceptions', '-fno-rtti', '-fno-stack-protector', '-fno-builtin',
     '-Wl,-soname,libturbo_carousel.so', '-I', str(base / 'frontend-native'),
     str(root / 'frontend-native/native_carousel.cpp'), str(base / 'frontend-native/video720_posters.o'),
     '-L', str(base / 'frontend-native'), '-lc', '-ldl', '-llog',
     '-o', str(output / 'libturbo_carousel.so')],
]
for command in commands:
    subprocess.run(command, check=True)
test_result = subprocess.run([str(output / 'transfer-rate-phases.exe')], check=True, text=True, capture_output=True)
print(test_result.stdout, end='')
files = {name: {'bytes': (output / name).stat().st_size,
                'sha256': hashlib.sha256((output / name).read_bytes()).hexdigest()}
         for name in ['libstation_frontend.so', 'libturbo_carousel.so']}
report = {'commands': commands, 'files': files, 'sourceBaseUnmodified': True,
          'testOutput': test_result.stdout.strip(),
          'target': 'aarch64-linux-android26', 'maximumPageSize': 16384,
          'apkPackaged': False, 'installed': False}
(output / 'compiled-modules.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(files, indent=2))
