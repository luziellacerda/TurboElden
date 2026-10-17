"""Independently verify R139 signed/unsigned ZIP payloads against R138."""
from pathlib import Path
import argparse, json, re, zipfile
import package_r139 as recipe

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base','--baseline',dest='base',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--candidate-sha',required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args = parser.parse_args()
    recipe.need(re.fullmatch('[0-9a-f]{64}',args.candidate_sha) and recipe.sha(args.candidate) == args.candidate_sha, 'Explicit candidate APK hash differs')
    recipe.need(not args.receipt.exists() and args.receipt.resolve() not in (args.base.resolve(),args.candidate.resolve()), 'Fresh receipt path required')
    primitive = recipe.assembler()
    freeze_path, identity_path = args.work/'source-freeze.json', args.work/'runtime-identity.json'
    frozen, identity, paths, expected, manifest = primitive.inputs(args.base,freeze_path,identity_path)
    freeze_sha, identity_sha = recipe.sha(freeze_path), recipe.sha(identity_path)
    preserved, changed = {}, {}
    with zipfile.ZipFile(args.base) as original, zipfile.ZipFile(args.candidate) as candidate:
        names = primitive.classic_entries(original)
        removed = sorted(n for n in names if primitive.signature_metadata(n))
        recipe.need(primitive.classic_entries(candidate) == names-set(removed), 'APK entries added/removed outside signature metadata')
        primitive.classic_zip(args.candidate,candidate.comment)
        for name in candidate.namelist():
            before, after = primitive.entry_sha(original,name), primitive.entry_sha(candidate,name)
            if name in recipe.REPLACED:
                recipe.need(after == expected[name] and before != after, 'Frozen replacement differs: '+name); changed[name] = after
            else:
                recipe.need(before == after, 'Unrequested payload changed: '+name); preserved[name] = after
        recipe.need(json.loads(candidate.read(recipe.ASSET)) == manifest, 'Actual engine registry differs')
        recipe.need(recipe.wrapper_independence(candidate) == identity['independentWrapperPins'], 'Independent wrappers changed')
    recipe.need(len(changed) == 2 and len(preserved) == 13858 and len([n for n in preserved if re.fullmatch(r'classes(?:[0-9]+)?\.dex',n)]) == 40, 'Atomic scope/40 original DEX violated')
    recipe.need(recipe.sha(freeze_path) == freeze_sha and recipe.sha(identity_path) == identity_sha and recipe.sha(args.candidate) == args.candidate_sha, 'Frozen input or candidate changed during verification')
    primitive.inputs(args.base,freeze_path,identity_path)
    report = {'schemaVersion':1,'revision':'R139','baseApkSha256':recipe.BASE,'candidateApkSha256':args.candidate_sha,
              'candidateApkBytes':args.candidate.stat().st_size,'freezeSha256':freeze_sha,'identityReceiptSha256':identity_sha,
              'replacedEntrySha256':changed,'addedEntrySha256':{},'preservedEntryCount':len(preserved),'preservedEntrySha256':preserved,
              'preservedEntryManifestSha256':primitive.digest(primitive.canonical(preserved)),'removedSignatureMetadata':removed,
              'changedDexPartitions':[],'all40DexByteIdentical':True,'independentWrapperPins':identity['independentWrapperPins'],
              'runtimePlayerCapacity':5,'retroArchEngineDescriptors':9,'activeV3RetroArchEngines':8,'optionsAndFpsUnchanged':True,
              'independentEntryVerification':True,'signatureChecked':False,'zipalignChecked':False,'installed':False,
              'serverActivationConfirmed':False,'physicalGameplayValidated':False,'verificationRecipeSha256':recipe.sha(__file__)}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    with args.receipt.open('x',encoding='utf-8') as stream: stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('revision','candidateApkSha256','preservedEntryCount','all40DexByteIdentical','independentEntryVerification')}))

if __name__ == '__main__': main()
