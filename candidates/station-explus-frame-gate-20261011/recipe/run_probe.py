"""Compile/run the candidate gate only; never compiles/packages a productive APK."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import datetime

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--compiler', type=Path, default=Path(r'C:\Program Files\LLVM\bin\clang++.exe'))
    args = p.parse_args()
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        raise SystemExit('Use a separate local binary build directory, not this source tree')
    out.mkdir(parents=True, exist_ok=True)
    native = ROOT/'native'
    exe = out/'frame_gate_probe.exe'
    command = [str(args.compiler), '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror',
               '-I'+str(native), str(native/'StationExPlusFrameGate.cpp'),
               str(ROOT/'tests/frame_gate_probe.cpp'), '-o', str(exe)]
    subprocess.run(command, check=True)
    probe = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
    results = json.loads(probe.stdout)
    receipt = {
        'schema': 1, 'generatedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'candidateOnly': True, 'packagedIntoR126': False, 'emulatorGameplay': False,
        'androidRuntimeOrJNIOrWss': False,
        'compiler': str(args.compiler), 'compilerVersion': subprocess.check_output(
            [str(args.compiler), '--version'], text=True).splitlines()[0],
        'flags': ['-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror', '-I<native-source>'],
        'results': results,
        'sourceSha256': {str(path.relative_to(ROOT)).replace('\\','/'): sha(path)
            for path in (native/'StationExPlusFrameGate.hpp', native/'StationExPlusFrameGate.cpp',
                         native/'StationSnapshotGuard.hpp',
                         ROOT/'tests/frame_gate_probe.cpp')},
        'localExecutableSha256': sha(exe),
        'limits': ['Synthetic owner only; no ROM/core execution',
                   'No JNI/native lifecycle/storage hooks', 'No WSS v3 endpoint or delivery parser',
                   'No signed new engine profile/server registration', 'No Android/gameplay/thermal measurement']}
    (out/'probe-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__': main()
