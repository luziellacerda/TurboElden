"""Exercise the real R138 registry and rejection guards, without writing APKs."""
from pathlib import Path
import argparse,copy,importlib.util,json,sys,zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'recipe/package_r139.py'
spec=importlib.util.spec_from_file_location('scope_r139',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-apk',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args();checks=[]
    with zipfile.ZipFile(args.baseline_apk) as archive:
        raw=archive.read(module.ASSET)
        module.need(module.digest(raw)==module.REGISTRY,'Exact R138 registry required')
        baseline=json.loads(raw)
        wrappers=module.wrapper_independence(archive)
        module.need(module.digest(archive.read(module.NATIVE))==module.OLD,'Exact R138 runtime required')
    before=copy.deepcopy(baseline);new='1'*64
    updated,selected=module.renew_registry(baseline,new)
    assert baseline==before and len(selected)==9 and sum(x['launchReady'] is True for x in selected)==8
    assert all(x['runtimeSha256']==new for x in selected)
    checks.append('positive: nine descriptors, eight active, donor immutable')
    def rejected(label,mutate):
        changed=copy.deepcopy(updated);mutate(changed)
        try:module.verify_registry(baseline,changed,new)
        except (ValueError,KeyError,StopIteration):checks.append('rejected: '+label);return
        raise AssertionError('Unauthorized scope accepted: '+label)
    snes_index=next(i for i,x in enumerate(updated['engines']) if x['platform']=='snes')
    independent_index=next(i for i,x in enumerate(updated['engines']) if x['platform']=='psx')
    inactive_index=next(i for i,x in enumerate(updated['engines']) if x.get('runtimeSha256')==new and not x.get('launchReady'))
    rejected('global policy',lambda x:x.update(extraCpuPolicy=True))
    rejected('engine addition',lambda x:x['engines'].append(copy.deepcopy(x['engines'][0])))
    rejected('engine removal',lambda x:x['engines'].pop())
    rejected('SNES HLE options',lambda x:x['engines'][snes_index].update(options=x['engines'][snes_index]['options'].replace('"HLE"','"LLE"')))
    rejected('SNES extra frameskip',lambda x:x['engines'][snes_index].update(options=x['engines'][snes_index]['options']+'\nframeskip = "1"\n'))
    rejected('core hash',lambda x:x['engines'][snes_index].update(coreSha256='2'*64))
    rejected('controller device profile',lambda x:x['engines'][snes_index].update(controllerProfiles=['other']))
    rejected('maximum players',lambda x:x['engines'][snes_index].update(maximumPlayers=9))
    rejected('Geolith activation',lambda x:x['engines'][inactive_index].update(launchReady=True))
    rejected('independent PSX mutation',lambda x:x['engines'][independent_index].update(engineId='changed'))
    rejected('stale native suffix',lambda x:x['engines'][snes_index].update(engineId=baseline['engines'][snes_index]['engineId']))
    rejected('wrong runtime SHA',lambda x:x['engines'][snes_index].update(runtimeSha256='2'*64))
    rejected('recovery protocol',lambda x:x['engines'][snes_index].update(recoveryProtocol='other'))
    for bad in (module.OLD,'1'*63,'A'*64,'pending'):
        try:module.renew_registry(baseline,bad)
        except ValueError:checks.append('rejected: invalid/old runtime hash '+str(len(bad)));continue
        raise AssertionError('Invalid runtime pin accepted')
    report={'schemaVersion':1,'revision':'R139','scopeChecksPassed':len(checks),'checks':checks,
            'baselineRegistrySha256':module.REGISTRY,'baselineRuntimeSha256':module.OLD,'independentWrapperPins':wrappers,
            'packageRecipeSha256':module.sha(source),'testSourceSha256':module.sha(__file__),
            'apkCreated':False,'nativeCompiled':False,'signed':False,'installed':False,'productionTouched':False,'physicalGameplayValidated':False}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    with args.receipt.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'scopeChecksPassed':len(checks),'independentWrappersConfirmed':len(wrappers),'apkCreated':False}))

if __name__=='__main__':main()
