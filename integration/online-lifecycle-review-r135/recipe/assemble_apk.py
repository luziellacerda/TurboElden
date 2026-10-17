"""Compose exactly five R135 replacements over signed R134; no ZIP additions."""
from pathlib import Path
import argparse, json, types, zipfile
from release_common import *

LEGACY_SHA='1d8c07e825fd28da68381a5e3b41cc9e6191cb6669ece1ff8f9a98624855f7a1'

def runtime():return module(ROOT/'recipe/build_runtime_identity.py','r135_runtime_contract')

def paths_for(receipt,identity):
    identity=Path(identity)
    dex_receipt=Path(receipt['payloadReceiptPath'])
    dex=read(dex_receipt)['payload']
    require(dex['name']=='classes35.dex','Only the reviewed online DEX is allowed')
    paths={'classes35.dex':dex_receipt.parent/'classes35.dex','assets/station-online/engines.json':identity.parent/'engines.json'}
    for kind,marker in receipt['markers'].items():
        name=marker['runtimeLibrary']
        paths[PREFIX+name]=identity.parent/'native'/name if kind=='psx' else identity.parent/name
    require(set(paths)==REPLACED,'Exact five-entry replacement scope required')
    return paths

def inputs(base,freeze,identity,prepared_freeze=None):
    receipt,manifest=runtime().validate_inputs(base,identity)
    frozen=read(freeze) if prepared_freeze is None else prepared_freeze
    require(frozen.get('schemaVersion')==1 and frozen.get('revision')=='R135' and frozen.get('sourceFrozen') is True and frozen.get('baseApkSha256')==BASE_SHA and frozen.get('identityReceiptSha256')==sha(identity) and frozen.get('sourceCommit')==receipt['sourceCommit'] and frozen.get('sourceSha256')==receipt['sourceSha256'] and frozen.get('payloadReceiptSha256')==receipt['payloadReceiptSha256'] and frozen.get('dexScopes')==receipt['dexScopes'],'Closed R135 source and class scope differs')
    paths=paths_for(receipt,identity)
    require(set(frozen.get('payloads',{}))==REPLACED,'Freeze scope differs')
    for name,path in paths.items():
        record={'path':str(path.resolve()),'bytes':path.stat().st_size,'sha256':sha(path)}
        checked_file(record,name)
        require(frozen['payloads'][name]==record and record['sha256']==manifest[name],'Frozen payload changed: '+name)
    expected={name:manifest[name] for name in REPLACED}
    return frozen,receipt,paths,expected,read(paths['assets/station-online/engines.json'])

def assembler():
    primitive=REPO/'integration/psx-online/recipe/assemble_apk.py'
    require(sha(primitive)==LEGACY_SHA,'Pinned streaming ZIP primitive changed')
    result=types.ModuleType('r135_streaming_zip');result.__file__=str(primitive)
    exec(compile(primitive.read_text(encoding='utf-8').replace('"R127"','"R135"'),str(primitive),'exec'),result.__dict__)
    result.BASE_SHA=BASE_SHA;result.REPLACED=REPLACED;result.ADDED=frozenset();result.PAYLOADS=REPLACED;result.inputs=inputs
    return result

def freeze_inputs(base,identity,out):
    receipt,manifest=runtime().validate_inputs(base,identity)
    paths=paths_for(receipt,identity)
    frozen={'schemaVersion':1,'revision':'R135','sourceFrozen':True,'baseApkSha256':BASE_SHA,'identityReceiptSha256':sha(identity),'sourceCommit':receipt['sourceCommit'],'sourceSha256':receipt['sourceSha256'],'payloadReceiptSha256':receipt['payloadReceiptSha256'],'dexScopes':receipt['dexScopes'],'payloads':{name:{'path':str(path.resolve()),'bytes':path.stat().st_size,'sha256':sha(path)} for name,path in paths.items()}}
    inputs(base,out,identity,frozen);write(out,frozen)
    return {'sourceFrozen':True,'payloadCount':5,'freezeSha256':sha(out)}

def package(base,freeze,identity,out):
    result=assembler().package(base,freeze,identity,out)
    report_path=Path(out).with_suffix('.package.json');report=read(report_path);receipt=read(identity)
    require(set(report['replacedEntrySha256'])==REPLACED and report['addedEntrySha256']=={} and report['preservedEntryCount']==13855,'Final unsigned composition must contain five replacements and 13855 preserved entries')
    require(PRESERVED_DEX <= set(report['preservedEntrySha256']) and DEX_ASSET in report['preservedEntrySha256'] and report['preservedEntrySha256'][PREFIX+'libstation_frontend.so']==FRONTEND_SHA,'Untouched DEX/PS4/frontend proof missing')
    report.update(sourceCommit=receipt['sourceCommit'],replacementCount=5,additionCount=0,approvedScopes=SCOPES,dexScopes=receipt['dexScopes'],existing39DexByteIdentical=True,ps4AssetDexByteIdentical=True,dexScopedClassesVerified=True,frontendLibraryByteIdentical=True,manifestByteIdentical=True,resourcesAndSonyAssetsByteIdentical=True,offlineEmulatorEntriesChanged=False,nativeRebuildsIdentityOnly=True)
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    result.update(revision='R135',replacementCount=5,additionCount=0)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('base','freeze','identity-receipt'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--out',type=Path)
    flags=p.add_mutually_exclusive_group();flags.add_argument('--write-freeze',action='store_true');flags.add_argument('--check-inputs',action='store_true')
    a=p.parse_args()
    if a.write_freeze:result=freeze_inputs(a.base,a.identity_receipt,a.freeze)
    elif a.check_inputs:inputs(a.base,a.freeze,a.identity_receipt);result={'inputsVerified':True,'apkWritten':False}
    else:require(a.out is not None,'Explicit output required');result=package(a.base,a.freeze,a.identity_receipt,a.out)
    print(json.dumps(result))

if __name__=='__main__':main()
