"""Compile/run host-only actual adapter fixture. Never use in Android/package."""
from pathlib import Path
import argparse,hashlib,json,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--compiler',type=Path,required=True);ap.add_argument('--protocol',type=Path,required=True);ap.add_argument('--pinned-options',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();module=Path(__file__).resolve().parent.parent;here=module/'native';a.out.mkdir(parents=True,exist_ok=True)
sources=[module/'tests/owner_probe.cpp',a.protocol/'StationPsxProtocol.cpp',a.protocol/'StationPsxSha256.cpp']
cmd=[str(a.compiler),'-std=c++20','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-I'+str(here),'-I'+str(a.protocol),'-I'+str(a.pinned_options),*[str(p) for p in sources],'-o',str(a.out/'owner_probe.exe')]
build=subprocess.run(cmd,capture_output=True,text=True)
(a.out/'probe-build.log').write_text(build.stdout+build.stderr,encoding='utf-8')
if build.returncode: print(build.stdout+build.stderr);raise SystemExit(build.returncode)
run=subprocess.run([str(a.out/'owner_probe.exe')],capture_output=True,text=True)
(a.out/'probe-run.log').write_text(run.stdout+run.stderr,encoding='utf-8')
if run.returncode: print(run.stdout+run.stderr);raise SystemExit(run.returncode)
result=json.loads(run.stdout.strip())
def pin(p):return {'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
receipt={'schemaVersion':1,'passed':result['passed'],'scope':result['scope'],'checks':result['checks'],'realAdapterCheckpointRuns':result['realAdapterCheckpointRuns'],'flags':['C++20','O2','Wall','Wextra','Werror','host-fixture-only','-I<protocol>','-I<pinned-options>'],'sources':[pin(p) for p in sources]+[pin(here/'StationPsxOwner.cpp'),pin(here/'StationPsxOwner.hpp'),pin(a.protocol/'StationPsxProtocol.hpp'),pin(a.pinned_options/'PsxPinnedOptions.h')],'coverage':['exact 10 dlsym hook return PCs and missing/moved rejects','59 compiled V2 options defaults plus valid pinned overrides','factory only actual loaded owner checkpoint','actual wrapper input sample/lease/rawrun/complete sequence','delay0 regression and productive signed delay4','first four neutral synchronized inputs and N+4 original poll','future-input pause, exact current-frame snapshot and post-Ready prime','wrong-thread and wrong-size state denied before raw decoder','manual native save/load/exit disabled before effects','local menu pause separated from network pause','sticky core failure clears lease without executed commit','explicit human owner exit only'],'limitations':['Mock SDL/rawcore on host, no Android or ROM','No physical controller, gameplay, performance or heat measurement','Does not prove nested original core decoder memory safety','No original ELF, productive APK or offline route was patched']}
(a.out/'owner-probe.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':receipt['passed'],'checks':receipt['checks'],'realAdapterCheckpointRuns':receipt['realAdapterCheckpointRuns']}))
