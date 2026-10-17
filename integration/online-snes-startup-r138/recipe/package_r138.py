"""Replace only the installed RetroArch runtime and its engine registry."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,sys,zipfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
BASE='fe4bc08fbc1f36d2790831f6bcd9593204ec0a032ca0d3a42c1cd385bc272719'
OLD='81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc'
REGISTRY='c0d75345922986c529137828e83b852612bb160870043654bd1b8d9821658ce7'
NATIVE='lib/arm64-v8a/libstation_retroarch.so'
ASSET='assets/station-online/engines.json'
REPLACED=frozenset({NATIVE,ASSET})
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def prepare(a):
    need(sha(a.base)==BASE and not a.out.exists(),'Exact R137 donor and new output required')
    a.out.mkdir(parents=True)
    build=json.loads(a.runtime_receipt.read_text('utf-8'))
    need(build['mode']=='candidate' and build['compiled'] and build['maximumPlayers']==5 and
         build['changedSourceFiles']==['frontend/drivers/platform_unix.c'] and
         build['baseRuntimeSha256']==OLD and build['runtimeSha256']==sha(a.runtime) and
         build['overlaySha256']==sha(HERE.parent/'native/source/frontend/drivers/platform_unix.c'),'Unverified native lifecycle build')
    with zipfile.ZipFile(a.base) as z:
        need(len(z.namelist())==len(set(z.namelist()))==13860,'Donor entry set changed')
        raw=z.read(ASSET);need(hashlib.sha256(raw).hexdigest()==REGISTRY,'Registry baseline drift')
        need(hashlib.sha256(z.read(NATIVE)).hexdigest()==OLD,'Installed native donor differs')
    original=json.loads(raw);updated=json.loads(raw);engines=[]
    new=sha(a.runtime)
    for before,after in zip(original['engines'],updated['engines']):
        if before.get('runtimeSha256')!=OLD:continue
        need(before['engineId'].endswith('-'+OLD[:12]),'Unrecognized native engine identity')
        after['runtimeSha256']=new
        after['engineId']=before['engineId'][:-12]+new[:12]
        if before['platform']=='snes':
            after['engineId']=before['engineId'][:-12]+'hle-'+new[:12]
            after['options']=before['options'].replace('bsnes_violate_accuracy = "disabled"','bsnes_violate_accuracy = "enabled"').replace('bsnes_chip_hle = "LLE"','bsnes_chip_hle = "HLE"')
            need(after['options']!=before['options'],'SNES HLE configuration was not applied')
        engines.append(after)
    need(any(e['platform']=='snes' for e in engines),'SNES owner absent')
    (a.out/'engines.json').write_text(json.dumps(updated,indent=2,ensure_ascii=False)+'\n','utf-8')
    receipt=dict(revision='R138',parentApkSha256=BASE,baseRuntimeSha256=OLD,runtimeSha256=new,
                 engines=engines,enginesAssetSha256=sha(a.out/'engines.json'),
                 runtimeReceiptSha256=sha(a.runtime_receipt),nativeOverlaySha256=build['overlaySha256'],
                 changedDexPartitions=[],gameplayValidated=False,serverRegistered=False)
    (a.out/'runtime-identity.json').write_text(json.dumps(receipt,indent=2)+'\n','utf-8')
    files={NATIVE:a.runtime,ASSET:a.out/'engines.json'}
    freeze=dict(schemaVersion=1,revision='R138',parentApkSha256=BASE,
                identityReceiptSha256=sha(a.out/'runtime-identity.json'),packageRecipeSha256=sha(__file__),
                replacements={n:dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size) for n,p in files.items()})
    (a.out/'source-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n','utf-8')
def assembler():
    spec=importlib.util.spec_from_file_location('r138_zip',REPO/'integration/psx-online/recipe/assemble_apk.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.BASE_SHA=BASE;m.REPLACED=REPLACED;m.ADDED=frozenset();m.PAYLOADS=REPLACED
    def inputs(base,freeze_path,identity_path):
        need(sha(base)==BASE,'Donor hash changed')
        frozen=json.loads(Path(freeze_path).read_text('utf-8'));receipt=json.loads(Path(identity_path).read_text('utf-8'))
        need(frozen['revision']==receipt['revision']=='R138' and frozen['parentApkSha256']==receipt['parentApkSha256']==BASE and
             frozen['identityReceiptSha256']==sha(identity_path) and frozen['packageRecipeSha256']==sha(__file__) and
             set(frozen['replacements'])==REPLACED,'Frozen inputs differ')
        paths={n:Path(r['path']) for n,r in frozen['replacements'].items()}
        for n,p in paths.items():need(sha(p)==frozen['replacements'][n]['sha256'] and p.stat().st_size==frozen['replacements'][n]['bytes'],'Payload changed '+n)
        need(receipt['runtimeSha256']==sha(paths[NATIVE]) and receipt['enginesAssetSha256']==sha(paths[ASSET]),'Identity payload drift')
        need(receipt['nativeOverlaySha256']==sha(HERE.parent/'native/source/frontend/drivers/platform_unix.c'),'Native source changed after freeze')
        with zipfile.ZipFile(base) as z:original=json.loads(z.read(ASSET))
        updated=json.loads(paths[ASSET].read_text('utf-8'))
        need({k:v for k,v in original.items() if k!='engines'}=={k:v for k,v in updated.items() if k!='engines'} and len(original['engines'])==len(updated['engines']),'Engine policy/count changed')
        selected=[]
        for before,after in zip(original['engines'],updated['engines']):
            if before.get('runtimeSha256')!=OLD:need(before==after,'Unrelated engine changed');continue
            allowed={'runtimeSha256','engineId'}|({'options'} if before['platform']=='snes' else set())
            need({k:v for k,v in before.items() if k not in allowed}=={k:v for k,v in after.items() if k not in allowed},'Native core/profile/library changed')
            prefix=before['engineId'][:-12]+('hle-' if before['platform']=='snes' else '')
            need(after['engineId']==prefix+receipt['runtimeSha256'][:12] and after['runtimeSha256']==receipt['runtimeSha256'] and 'pending' not in after['engineId'],'Stale native identity')
            if before['platform']=='snes':
                expected=before['options'].replace('bsnes_violate_accuracy = "disabled"','bsnes_violate_accuracy = "enabled"').replace('bsnes_chip_hle = "LLE"','bsnes_chip_hle = "HLE"')
                need(after['options']==expected,'Other SNES option changed')
            selected.append(after)
        need(selected==receipt['engines'],'Native engine list differs')
        return frozen,receipt,paths,{n:r['sha256'] for n,r in frozen['replacements'].items()},updated
    m.inputs=inputs
    return m
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('base','runtime','runtime-receipt','out'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();prepare(a)
    assembler().package(a.base,a.out/'source-freeze.json',a.out/'runtime-identity.json',a.out/'unsigned.apk')
    # package() returns a compact summary and writes the full entry manifest.
    # Keep the full manifest for independent signing and installed verification.
    result=json.loads((a.out/'unsigned.package.json').read_text('utf-8'))
    result.update(revision='R138',changedDexPartitions=[],changedApkEntries=sorted(REPLACED),all40DexByteIdentical=True)
    (a.out/'unsigned.package.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps({k:result[k] for k in ('revision','unsignedApkSha256','preservedEntryCount','all40DexByteIdentical')}))
if __name__=='__main__':main()
