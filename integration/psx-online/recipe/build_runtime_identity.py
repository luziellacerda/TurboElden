"""Bind the current PSX implementation and exact shared DEX to new runtime IDs.

Normal emulators and media remain byte identical to R126. N64/Dolphin markers
are renewed because their Java/manifest bundle changed, not their core/options.
No asset ID, marker ELF or receipt is a recursive fingerprint input.
"""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE_SHA='f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d'
OWNER_SHA='62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6'
CORE_SHA='e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9'
SDL_SHA='a282b35554eb006773349430e117bfeeff32a84e246a058c8fb7c7027c2e4dee'
CPP_SHA='b5d97c38a728afe28d341cda3369f512d35eaf9c680c1b0563cd6a63e395230f'
FRONTEND_SHA='de092671462a0960665d06d1b463cd48108e65c599c5125c733d7205dd463468'
PREFIX='lib/arm64-v8a/'
PAYLOADS={'AndroidManifest.xml','classes6.dex','classes28.dex','classes35.dex'}
PARENTS={
    'n64':{'runtimeLibrary':'libstation_mupen64plus_runtime.so','runtimeSha256':'1aafea201355b58909ada9958bbe5bb5407e7ace7eb3848ade7ba04d235becac',
        'fingerprintSha256':'afe7e68e03c8661423c8509bac6e0694a95bba2fb9970a92f8dfd3e2a0aa226e','backend':'mupen64plus-ae-station-v1'},
    'dolphin':{'runtimeLibrary':'libstation_dolphin_runtime.so','runtimeSha256':'ca43a338d7992e2d9ef298387822c860945fbb16dc11dff03ee5b1d1fcd27656',
        'fingerprintSha256':'024fdc1eeb992deaf5e6383056a8a981177da52d0b07057854c338bcd812918b','backend':'dolphin-station-v1'}}

def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda:stream.read(1048576),b''):digest.update(part)
    return digest.hexdigest()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def import_recipe():
    path=REPO/'versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py'
    spec=importlib.util.spec_from_file_location('r126_identity_primitives',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def mapping(values):
    result={}
    for value in values:
        name,sep,path=value.partition('=')
        if not sep or name not in PAYLOADS or name in result:raise ValueError('Exact final payloads required')
        result[name]=Path(path).resolve()
    if set(result)!=PAYLOADS:raise ValueError('Missing final DEX/manifest')
    return result
def source_pins(java_receipt):
    # The compilation receipt contains the complete effective R124+125+126+PSX
    # source overlay; verify it against the same recipe, not a directory count.
    spec=importlib.util.spec_from_file_location('psx_compile_sources',ROOT/'recipe/compile_java.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    expected={name:module.sha(path) for name,path in sorted(module.sources().items())}
    if expected!=java_receipt['sources']:raise ValueError('Source changed after Java compilation')
    extra={}
    for directory,extensions in [('native',{'.cpp','.hpp','.h'}),('recipe',{'.py'})]:
        for path in sorted((ROOT/directory).rglob('*')):
            if path.is_file() and path.suffix in extensions and path.name!='build_runtime_identity.py':
                extra[path.relative_to(ROOT).as_posix()]=sha(path)
    extra['profile.json']=sha(ROOT/'profile.json')
    return expected,extra

def main():
    p=argparse.ArgumentParser()
    for name in ('base','ndk','java-receipt','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--parent-identity',type=Path)
    p.add_argument('--payload',action='append',required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    if sha(a.base)!=BASE_SHA:raise ValueError('Wrong exact R126 base APK')
    payload=mapping(a.payload);jr=read(a.java_receipt)
    if sha(payload['classes35.dex'])!=jr['classes35Sha256'] or jr['compileOnlyStubsPackaged']:raise ValueError('Wrong compiled Java')
    java,extra=source_pins(jr);policy=read(ROOT/'profile.json')
    parent={'markers':PARENTS};parents={}
    with zipfile.ZipFile(a.base) as z:
        original=json.loads(z.read('assets/station-online/engines.json'))
        expected_pins={'libmain.so':OWNER_SHA,'libSDL2.so':SDL_SHA,'libpcsx_rearmed_libretro_android.so':CORE_SHA,
            'libc++_shared.so':CPP_SHA,'libstation_frontend.so':FRONTEND_SHA}
        pins={name:digest(z.read(PREFIX+name)) for name in expected_pins}
        if pins!=expected_pins:raise ValueError('Normal PSX owner/core/dependency changed')
        preserved={name:digest(z.read(name)) for name in ('classes10.dex','classes12.dex','classes36.dex')}
        for kind in ('n64','dolphin'):
            marker=parent['markers'][kind];library=marker['runtimeLibrary']
            elf=z.read(PREFIX+library)
            if a.parent_identity:
                raw=(a.parent_identity/(library+'.fingerprint.json')).read_bytes().rstrip(b'\r\n')
            else:
                prefix=('{"backend":"'+marker['backend']+'",').encode('ascii')
                start=elf.find(prefix)
                if start<0:raise ValueError('Missing canonical parent fingerprint in R126 ELF')
                text=elf[start:].split(b'\0',1)[0].decode('ascii')
                value,end=json.JSONDecoder().raw_decode(text);raw=text[:end].encode('ascii')
                if canonical(value)!=raw:raise ValueError('Non-canonical embedded parent fingerprint')
            if digest(elf)!=marker['runtimeSha256'] or digest(raw)!=marker['fingerprintSha256'] or raw not in elf:
                raise ValueError('Parent marker fingerprint does not match actual R126 APK')
            parents[kind]={'value':json.loads(raw),'sha256':digest(raw),'runtimeSha256':digest(elf)}
    shared={'schemaVersion':3,'baseApkSha256':BASE_SHA,
        'payloadSha256':{name:sha(path) for name,path in sorted(payload.items())},
        'preservedPayloadSha256':preserved,'javaSources':java,'productiveTransforms':extra}
    psx={**shared,'backend':policy['backend'],'wire':'PXL1','recoveryProtocol':'station-stream.v3',
        'ownerSha256':OWNER_SHA,'coreSha256':CORE_SHA,'dependencySha256':pins,
        'compiledDefaultsSha256':policy['compiledDefaultsSha256'],'options':policy['options'],
        'optionsSha256':policy['optionsSha256'],'maximumPlayers':2,'controllerProfiles':['standard-2p-v1'],
        'inputDelayFrames':4,'biosPolicy':'HLE-per-game-approved','saves':'session-only-fresh'}
    raw=canonical(psx);identity_hash=digest(raw)
    (a.out/'psx.fingerprint.json').write_bytes(raw+b'\n')
    identity_source=a.out/'StationPsxIdentity.cpp'
    identity_source.write_text('extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "'+identity_hash+'";}\n'+
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return '+json.dumps(raw.decode('ascii'))+';}\n',encoding='ascii')
    native=a.out/'native'
    subprocess.run([sys.executable,str(ROOT/'recipe/build_entry.py'),'--ndk',str(a.ndk),
        '--owner',str(ROOT/'native'),'--protocol',str(ROOT/'native'),'--pinned-options',str(ROOT/'native'),
        '--identity-source',str(identity_source),'--out',str(native)],check=True)
    runtime=native/'libstation_psx_online.so'
    if raw not in runtime.read_bytes():raise ValueError('Final runtime lacks exact fingerprint')
    markers={'psx':{'runtimeLibrary':runtime.name,'runtimeSha256':sha(runtime),'runtimeBytes':runtime.stat().st_size,'fingerprintSha256':identity_hash}}
    old=import_recipe()
    for kind in ('n64','dolphin'):
        previous=parents[kind]
        value={**previous['value'],**shared,'parentFingerprintSha256':previous['sha256'],
            'parentRuntimeSha256':previous['runtimeSha256'],'psxRuntimeSha256':sha(runtime)}
        library=parent['markers'][kind]['runtimeLibrary'];api='StationMupenRuntime' if kind=='n64' else 'StationDolphinRuntime'
        markers[kind]=old.marker(value,library,api,a.ndk,a.out)
    updated=copy.deepcopy(original)
    replaced=[]
    for i,e in enumerate(updated['engines']):
        platform=e['platform']
        if platform in ('n64','gamecube','wii'):
            kind='n64' if platform=='n64' else 'dolphin';mark=markers[kind]
            e['runtimeSha256']=mark['runtimeSha256']
            e['engineId']=('mupen64plus-ae-33bf7021-n64-v3-' if platform=='n64' else 'dolphin-5102a033-'+platform+'-v3-')+mark['runtimeSha256'][:12]
            replaced.append(platform)
        elif platform=='psx':
            mark=markers['psx']
            updated['engines'][i]={'engineId':'pcsx-rearmed-ff81ed17-player-v3-'+mark['runtimeSha256'][:12],
                'platform':'psx','backend':policy['backend'],'library':policy['coreLibrary'],'runtimeLibrary':mark['runtimeLibrary'],
                'coreSha256':CORE_SHA,'runtimeSha256':mark['runtimeSha256'],
                'dependencySha256':{name:value for name,value in pins.items() if name!='libpcsx_rearmed_libretro_android.so'},
                'extensions':['pbp','chd','cue'],'overlay':'','options':policy['options'],'launchReady':True,
                'license':'GPL-2.0-or-later','sourceRevision':'ff81ed17a15241d2f3730cdd7585b38e172532ca',
                'recoveryProtocol':'station-stream.v3','maximumPlayers':2,'controllerProfiles':['standard-2p-v1'],
                'status':'implemented-candidate-peer-gameplay-pending','contentIdentityByExtension':{'cue':'cue-set-v1','default':'launch-file-v1'}}
            replaced.append(platform)
    if sorted(replaced)!=['gamecube','n64','psx','wii']:raise ValueError('Wrong engine replacement set')
    for before,after in zip(original['engines'],updated['engines']):
        if before['platform'] not in replaced and before!=after:raise ValueError('Unrelated engine changed')
        if before['platform'] in ('n64','gamecube','wii'):
            stripped=lambda value:{k:v for k,v in value.items() if k not in ('engineId','runtimeSha256')}
            if stripped(before)!=stripped(after):raise ValueError('Existing emulator/core/policy changed')
    engines=a.out/'engines.json';write(engines,updated)
    if engines.stat().st_size>32768:raise ValueError('Client engine asset size limit')
    profile={'schemaVersion':1,'controllerProfile':'standard-2p-v1','devices':[1,1],'coreOptions':policy['options']}
    profile_raw=json.dumps(profile,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    (a.out/'psx-controller-profile.json').write_bytes(profile_raw+b'\n')
    receipt={'schemaVersion':3,'baseApkSha256':BASE_SHA,'markers':markers,
        'engines':[e for e in updated['engines'] if e['platform'] in replaced],
        'psxControllerProfileSha256':digest(profile_raw),'psxOptionsSha256':policy['optionsSha256'],
        'enginesAssetSha256':sha(engines),'payloadSha256':shared['payloadSha256'],
        'normalPsxLibrariesPreserved':pins,'n64DolphinCoreAndOptionsUnchanged':True,
        'snesMegadriveEntriesUnchanged':True,'registeredOnServer':False,'installed':False,'physicalGameplayValidated':False}
    write(a.out/'runtime-identity.json',receipt)
    print(json.dumps({'engines':[e['engineId'] for e in receipt['engines']],'markers':markers,'productionActivated':False}))

if __name__=='__main__':main()
