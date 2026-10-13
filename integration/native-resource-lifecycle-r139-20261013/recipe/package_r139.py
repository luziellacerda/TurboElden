"""Package R139 over exact R138: two replacements, no added payloads."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, re, struct, sys, zipfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[1]
BASE = '9183462e4d45cfcf2d2599d9e682b81890fee7b094505bf3073ab8183dd1dd10'
OLD = '463bdb0b409e028aa34f6c9a09d291a3715ffb3eacb8f18ee28843e7373eb80f'
REGISTRY = '76b3cb61149293200cb8853784e6b6e4023f4e4c33b6b7cfcad8a954e1f9f519'
NATIVE = 'lib/arm64-v8a/libstation_retroarch.so'
ASSET = 'assets/station-online/engines.json'
CHANGED_SOURCE = 'frontend/drivers/platform_unix.c'
REPLACED = frozenset((NATIVE, ASSET))
WRAPPERS = ('libstation_psx_online.so', 'libstation_mupen64plus_runtime.so', 'libstation_dolphin_runtime.so')

def need(ok, message):
    if not ok: raise ValueError(message)

def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()

def digest(raw): return hashlib.sha256(raw).hexdigest()
def read(path): return json.loads(Path(path).read_text('utf-8'))
def write(path, value): Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def renew_registry(original, new_runtime):
    need(re.fullmatch('[0-9a-f]{64}', new_runtime) and new_runtime != OLD, 'New explicit runtime SHA256 required')
    updated = copy.deepcopy(original); selected = []
    for before, after in zip(original['engines'], updated['engines']):
        if before.get('runtimeSha256') != OLD: continue
        need(before['engineId'].endswith('-' + OLD[:12]), 'R138 engine suffix differs')
        after['runtimeSha256'] = new_runtime
        after['engineId'] = before['engineId'][:-12] + new_runtime[:12]
        selected.append(after)
    verify_registry(original, updated, new_runtime)
    return updated, selected

def verify_registry(original, updated, new_runtime):
    need({k:v for k,v in original.items() if k != 'engines'} == {k:v for k,v in updated.items() if k != 'engines'}, 'Global engine policy changed')
    need(len(original['engines']) == len(updated['engines']) == 13, 'Engine count/order differs')
    selected = []; independent = []
    for before, after in zip(original['engines'], updated['engines']):
        if before.get('runtimeSha256') != OLD:
            need(before == after, 'Independent engine changed'); independent.append(after); continue
        need({k:v for k,v in before.items() if k not in ('engineId','runtimeSha256')} ==
             {k:v for k,v in after.items() if k not in ('engineId','runtimeSha256')}, 'Core/options/profiles/capacity/protocol changed')
        need(after['runtimeSha256'] == new_runtime and after['engineId'] == before['engineId'][:-12] + new_runtime[:12] and
             'pending' not in after['engineId'], 'New runtime identity differs')
        selected.append(after)
    need(len(selected) == 9 and sum(e.get('launchReady') is True for e in selected) == 8, 'Nine descriptors/eight active engines required')
    need(len(independent) == 4 and sorted(e['platform'] for e in independent) == ['gamecube','n64','psx','wii'], 'Four independent owners required')
    snes = next(e for e in selected if e['platform'] == 'snes')
    need('bsnes_violate_accuracy = "enabled"' in snes['options'] and 'bsnes_chip_hle = "HLE"' in snes['options'], 'R138 fixed SNES HLE options lost')
    need(len({e['engineId'] for e in updated['engines']}) == 13, 'Duplicate engine ID')
    return selected

def verify_elf(path):
    data = Path(path).read_bytes()
    need(data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', data, 18)[0] == 183, 'ARM64 little-endian ELF required')
    offset = struct.unpack_from('<Q', data, 32)[0]; size, count = struct.unpack_from('<HH', data, 54)
    need(size == 56 and count > 0 and offset + size * count <= len(data), 'Invalid ELF program table')
    loads = [struct.unpack_from('<IIQQQQQQ', data, offset + i*size) for i in range(count)]
    alignments = [h[7] for h in loads if h[0] == 1]
    need(alignments and min(alignments) >= 16384, 'Runtime ELF needs 16 KiB alignment')
    return min(alignments)

def source_and_build(runtime, runtime_sha, runtime_receipt, source_freeze):
    build, frozen = read(runtime_receipt), read(source_freeze)
    need(build.get('revision') == frozen.get('revision') == 'R139' and build.get('mode') == 'candidate' and build.get('compiled') is True, 'R139 candidate build required')
    need(build['baseRuntimeSha256'] == frozen['baseRuntimeSha256'] == OLD and build['runtimeSha256'] == runtime_sha == sha(runtime), 'Runtime/build/base identity mismatch')
    need(build['runtimeBytes'] == Path(runtime).stat().st_size and build['maximumPlayers'] == 5 and build['minimumLoadAlignment'] >= 16384, 'Runtime shape/player capacity mismatch')
    need(build['changedSourceFiles'] == frozen['changedSourceFiles'] == [CHANGED_SOURCE], 'Only native lifecycle source may change')
    need(build['sourceFreezeSha256'] == sha(source_freeze) and build['overlaySha256'] == frozen['nativeSourceSha256'], 'Native source freeze differs from build')
    need(re.fullmatch('[0-9a-f]{40}', frozen['sourceCommit']) and frozen['sourceFiles'][CHANGED_SOURCE] == frozen['nativeSourceSha256'], 'Frozen commit/overlay identity required')
    overlay = ROOT / 'native/source' / CHANGED_SOURCE
    need(overlay.is_file() and sha(overlay) == frozen['nativeSourceSha256'], 'Productive native source changed after build')
    need(build['recipeSha256'] == sha(HERE/'build_native_r139.py'), 'Build recipe changed after compilation')
    need(verify_elf(runtime) >= build['minimumLoadAlignment'], 'Actual ELF alignment differs')
    return build, frozen

def wrapper_independence(archive):
    result = {}
    for name in WRAPPERS:
        raw = archive.read('lib/arm64-v8a/' + name)
        starts = [m.start() for m in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw)]
        documents = []
        for start in starts:
            end = raw.find(b'\0', start)
            if end < 0: continue
            try: value = json.loads(raw[start:end].decode('ascii'))
            except (ValueError, UnicodeError): continue
            if isinstance(value,dict) and 'baseApkSha256' in value and 'payloadSha256' in value: documents.append(value)
        need(len(documents) == 1, 'Exactly one original wrapper fingerprint required: ' + name)
        value = documents[0]; bound = set()
        def walk(item):
            if isinstance(item,dict):
                for key, child in item.items():
                    if key in ('payloadSha256','dependencySha256') and isinstance(child,dict): bound.update(child)
                    walk(child)
            elif isinstance(item,list):
                for child in item: walk(child)
        walk(value)
        need(not (REPLACED & bound) and 'libstation_retroarch.so' not in bound, 'Independent wrapper binds changed R139 entries')
        result[name] = {'runtimeSha256':digest(raw),'fingerprintSha256':digest(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')),
                        'boundEntryCount':len(bound),'r139ReplacedEntriesBound':False}
    return result

def prepare(args):
    need(sha(args.base) == BASE, 'Exact signed R138 donor required')
    need(not args.out.exists(), 'Fresh packaging directory required')
    build, native_freeze = source_and_build(args.runtime, args.runtime_sha, args.runtime_receipt, args.source_freeze)
    with zipfile.ZipFile(args.base) as archive:
        need(len(archive.namelist()) == len(set(archive.namelist())) == 13860, 'R138 entry set differs')
        raw = archive.read(ASSET)
        need(digest(raw) == REGISTRY and digest(archive.read(NATIVE)) == OLD, 'R138 runtime/registry pin differs')
        wrappers = wrapper_independence(archive)
    updated, selected = renew_registry(json.loads(raw), args.runtime_sha)
    args.out.mkdir(parents=True)
    write(args.out/'engines.json', updated)
    need((args.out/'engines.json').stat().st_size <= 32768, 'Registry exceeds existing client limit')
    identity = {'schemaVersion':1,'revision':'R139','parentApkSha256':BASE,'baseRuntimeSha256':OLD,
                'runtimeSha256':args.runtime_sha,'runtimeBytes':build['runtimeBytes'],'engines':selected,
                'enginesAssetSha256':sha(args.out/'engines.json'),'runtimeReceiptSha256':sha(args.runtime_receipt),
                'nativeSourceFreezeSha256':sha(args.source_freeze),'nativeOverlaySha256':native_freeze['nativeSourceSha256'],
                'sourceCommit':native_freeze['sourceCommit'],'independentWrapperPins':wrappers,
                'changedDexPartitions':[],'serverRegistered':False,'gameplayValidated':False}
    write(args.out/'runtime-identity.json', identity)
    records = {NATIVE:args.runtime, ASSET:args.out/'engines.json'}
    frozen = {'schemaVersion':1,'revision':'R139','parentApkSha256':BASE,'identityReceiptSha256':sha(args.out/'runtime-identity.json'),
              'packageRecipeSha256':sha(__file__),'primitiveAssemblerSha256':sha(REPO/'integration/psx-online/recipe/assemble_apk.py'),
              'runtimeReceipt':{'path':str(args.runtime_receipt.resolve()),'sha256':sha(args.runtime_receipt)},
              'nativeSourceFreeze':{'path':str(args.source_freeze.resolve()),'sha256':sha(args.source_freeze)},
              'replacements':{n:{'path':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size} for n,p in records.items()}}
    write(args.out/'source-freeze.json', frozen)

def assembler():
    source = REPO/'integration/psx-online/recipe/assemble_apk.py'
    spec = importlib.util.spec_from_file_location('r139_classic_zip', source); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.BASE_SHA = BASE; module.REPLACED = REPLACED; module.ADDED = frozenset(); module.PAYLOADS = REPLACED
    def inputs(base, freeze_path, identity_path):
        need(sha(base) == BASE, 'R138 donor hash changed')
        frozen, identity = read(freeze_path), read(identity_path)
        need(frozen['revision'] == identity['revision'] == 'R139' and frozen['parentApkSha256'] == identity['parentApkSha256'] == BASE, 'Wrong package revision/base')
        need(frozen['identityReceiptSha256'] == sha(identity_path) and frozen['packageRecipeSha256'] == sha(__file__) and frozen['primitiveAssemblerSha256'] == sha(source), 'Packaging source/identity changed after freeze')
        need(set(frozen['replacements']) == REPLACED, 'Two exact replacements required')
        paths = {n:Path(r['path']) for n,r in frozen['replacements'].items()}
        for n,p in paths.items(): need(sha(p) == frozen['replacements'][n]['sha256'] and p.stat().st_size == frozen['replacements'][n]['bytes'], 'Frozen payload changed: '+n)
        build_path = Path(frozen['runtimeReceipt']['path']); native_freeze_path = Path(frozen['nativeSourceFreeze']['path'])
        need(sha(build_path) == frozen['runtimeReceipt']['sha256'] == identity['runtimeReceiptSha256'] and
             sha(native_freeze_path) == frozen['nativeSourceFreeze']['sha256'] == identity['nativeSourceFreezeSha256'], 'Native provenance changed')
        source_and_build(paths[NATIVE], identity['runtimeSha256'], build_path, native_freeze_path)
        need(identity['runtimeSha256'] == sha(paths[NATIVE]) and identity['enginesAssetSha256'] == sha(paths[ASSET]), 'Runtime registry identity mismatch')
        with zipfile.ZipFile(base) as z:
            original = json.loads(z.read(ASSET)); need(wrapper_independence(z) == identity['independentWrapperPins'], 'Independent wrappers drifted')
        manifest = read(paths[ASSET]); need(verify_registry(original,manifest,identity['runtimeSha256']) == identity['engines'], 'Selected engine list differs')
        return frozen, identity, paths, {n:r['sha256'] for n,r in frozen['replacements'].items()}, manifest
    module.inputs = inputs
    return module

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base','--baseline',dest='base',type=Path,required=True)
    for name in ('runtime','runtime-receipt','source-freeze','out'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--runtime-sha',required=True)
    args = parser.parse_args(); prepare(args)
    assembler().package(args.base,args.out/'source-freeze.json',args.out/'runtime-identity.json',args.out/'unsigned.apk')
    # Preserve the complete manifest written by the primitive, not its summary.
    report = read(args.out/'unsigned.package.json')
    report.update(revision='R139',changedDexPartitions=[],changedApkEntries=sorted(REPLACED),all40DexByteIdentical=True,
                  controllerProfilesUnchanged=True,optionsAndFpsUnchanged=True,maximumRuntimePlayers=5,activeV3RetroArchEngines=8)
    need(report['preservedEntryCount'] == 13858 and len(report['replacedEntrySha256']) == 2 and not report['addedEntrySha256'], 'Requested APK scope violated')
    write(args.out/'unsigned.package.json',report)
    print(json.dumps({k:report[k] for k in ('revision','unsignedApkSha256','preservedEntryCount','all40DexByteIdentical')}))

if __name__ == '__main__': main()
