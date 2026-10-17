"""Verify that invalid output arguments are rejected before touching frozen sources."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline',type=Path)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    args.baseline=args.baseline.resolve()
    args.work=args.work.resolve()
    args.receipt=args.receipt.resolve()
    if args.work.exists() or args.work.is_relative_to(REPO):
        raise ValueError('Guard work directory must be fresh and outside the repository')
    if args.receipt.exists() or not args.receipt.is_relative_to(ROOT/'evidence'):
        raise ValueError('Guard receipt must be fresh in this new overlay evidence directory')
    patch=ROOT/'recipe/patch_resource_lifecycle.py'
    test=ROOT/'recipe/test_resource_lifecycle.py'
    candidate=ROOT/'native/source/frontend/drivers/platform_unix.c'
    harness=ROOT/'tests/resource_tls_harness.c.in'
    protected=[args.baseline,candidate,patch,test,harness]
    before={str(p):sha(p) for p in protected}
    repo_work=REPO/'r139-forbidden-test-work'
    frozen_receipt=args.baseline.parent/'r139-forbidden-receipt.json'
    frozen_output=args.baseline.parent/'r139-forbidden-source.c'
    for p in [repo_work,frozen_receipt,frozen_output]:
        if p.exists():raise ValueError('Sentinel path already exists')
    args.work.mkdir(parents=True,exist_ok=False)
    existing_work=args.work/'existing-work'
    existing_work.mkdir()
    existing_receipt=args.work/'existing-receipt.json'
    existing_receipt.write_text('{}\n')
    common=[sys.executable,str(test),str(args.baseline),'--compiler',str(args.compiler)]
    cases={
      'relative-work':common+['--work','relative-forbidden-work','--receipt',str(args.work/'receipt-a.json')],
      'repository-work':common+['--work',str(repo_work),'--receipt',str(args.work/'receipt-b.json')],
      'existing-work':common+['--work',str(existing_work),'--receipt',str(args.work/'receipt-c.json')],
      'existing-receipt':common+['--work',str(args.work/'new-work-a'),'--receipt',str(existing_receipt)],
      'frozen-receipt-folder':common+['--work',str(args.work/'new-work-b'),'--receipt',str(frozen_receipt)],
      'candidate-as-receipt':common+['--work',str(args.work/'new-work-c'),'--receipt',str(candidate)],
      'patch-existing-baseline':[sys.executable,str(patch),str(args.baseline),'--output',str(args.baseline)],
      'patch-frozen-folder':[sys.executable,str(patch),str(args.baseline),'--output',str(frozen_output)],
    }
    results={}
    for name,command in cases.items():
        result=subprocess.run(command,capture_output=True,text=True,timeout=10)
        if result.returncode==0:raise ValueError('Unsafe recipe arguments accepted: '+name)
        results[name]=dict(exitCode=result.returncode,rejected=True)
    after={str(p):sha(p) for p in protected}
    if before!=after:raise ValueError('Protected source changed')
    for p in [repo_work,frozen_receipt,frozen_output,*[args.work/n for n in ['new-work-a','new-work-b','new-work-c','receipt-a.json','receipt-b.json','receipt-c.json']]]:
        if p.exists():raise ValueError('Rejected call created output: '+str(p))
    report=dict(schemaVersion=1,cases=results,protectedInputsSha256=before,
                allProtectedBytesPreserved=True,rejectedCallsCreatedNoOutputs=True)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),allRejected=True,allProtectedBytesPreserved=True),indent=2))


if __name__=='__main__':
    main()
