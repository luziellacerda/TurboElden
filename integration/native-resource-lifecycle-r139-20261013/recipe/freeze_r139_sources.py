"""Freeze committed R139 native source and supporting recipes by role."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
import package_r139 as recipe
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    recipe.need(re.fullmatch('[0-9a-f]{40}',args.source_commit) and not args.out.exists(),'Explicit frozen Git SHA and fresh output required')
    native = ROOT/'native/source'/recipe.CHANGED_SOURCE
    roles = {'nativeRuntimeSource':[native],
             'buildAndPackagingRecipes':sorted((ROOT/'recipe').glob('*.py')),
             'nativeAndScopeTests':sorted((ROOT/'tests').glob('*'))}
    frozen = {}
    for role,files in roles.items():
        frozen[role] = {}
        for path in files:
            if not path.is_file():continue
            name = path.relative_to(REPO).as_posix()
            raw = subprocess.check_output(['git','show',args.source_commit+':'+name],cwd=REPO)
            actual = recipe.sha(path)
            recipe.need(hashlib.sha256(raw).hexdigest() == actual,'Source differs from specified commit: '+name)
            frozen[role][name] = actual
    native_sha = recipe.sha(native)
    report = {'schemaVersion':1,'revision':'R139','sourceCommit':args.source_commit,
              'baseRuntimeSha256':recipe.OLD,'nativeSourceSha256':native_sha,
              'sourceFiles':{recipe.CHANGED_SOURCE:native_sha},'changedSourceFiles':[recipe.CHANGED_SOURCE],
              'sourceRoles':frozen,'sourceArchiveSha256':'b8f7649a5edacbe9e913d5e50f66482c0aa082fbd2237f5fd7800d00723b735a',
              'baselineSourceManifestSha256':'63049a133ed0a761133f4ffc36ce642870dc699e103a5a73ab0b7683a6d90f47',
              'baselineR138OverlaySha256':'e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2',
              'committedSourceBytesVerified':True,'apkCreated':False,'nativeCompiled':False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'revision':'R139','sourceCommit':args.source_commit,'sourceFreezeSha256':recipe.sha(args.out),'nativeSourceSha256':native_sha}))

if __name__=='__main__':main()
