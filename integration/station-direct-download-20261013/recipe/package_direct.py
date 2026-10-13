#!/usr/bin/env python3
"""Build an unsigned classic-ZIP test APK with exactly five replacements over R139."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import build_wrappers as identity_contract

BASE = identity_contract.BASE
REPLACED = frozenset(('classes28.dex', 'assets/station-online/engines.json',
    *('lib/arm64-v8a/' + name for name in identity_contract.NAMES.values())))


def sha(path): return identity_contract.sha(path)
def need(value, message): return identity_contract.need(value, message)
def read(path): return json.loads(Path(path).read_text())


def verify_inputs(base, freeze_file, identity_file):
    need(sha(base) == BASE, 'Exact signed R139 donor required')
    freeze, identity = read(freeze_file), read(identity_file)
    need(freeze['baseApkSha256'] == identity['parentApkSha256'] == BASE and
         freeze['identityReceiptSha256'] == sha(identity_file), 'Frozen identity differs')
    need(set(freeze['payloads']) == REPLACED, 'Exactly five scoped replacements required')
    need(freeze['packageRecipeSha256'] == sha(__file__), 'Packager changed after freeze')
    for name, checksum in freeze['sources'].items():
        need(sha(REPO / name) == checksum, 'Direct download source changed after freeze')
    paths, expected = {}, {}
    for name, row in freeze['payloads'].items():
        source = Path(row['path'])
        need(source.is_file() and not source.is_symlink() and source.stat().st_size == row['bytes'] and
             sha(source) == row['sha256'], 'Frozen payload differs: ' + name)
        paths[name], expected[name] = source, row['sha256']
    need(expected['classes28.dex'] == identity['dexSha256'] and
         expected['assets/station-online/engines.json'] == identity['enginesAssetSha256'], 'DEX/engine pins differ')
    registry = read(paths['assets/station-online/engines.json'])
    need(paths['assets/station-online/engines.json'].stat().st_size <= 32768, 'Existing registry size limit exceeded')
    with zipfile.ZipFile(base) as archive:
        need(len(archive.namelist()) == len(set(archive.namelist())) == 13860, 'R139 inventory differs')
        original = json.loads(archive.read('assets/station-online/engines.json'))
        need(len(original['engines']) == len(registry['engines']) == 13, 'Engine inventory differs')
        need({k:v for k,v in original.items() if k != 'engines'} ==
             {k:v for k,v in registry.items() if k != 'engines'}, 'Global engine policy differs')
        for before, after in zip(original['engines'], registry['engines']):
            if before['platform'] not in ('psx', 'n64', 'gamecube', 'wii'):
                need(before == after, 'Unrelated engine changed')
            else:
                need({k:v for k,v in before.items() if k not in ('engineId','runtimeSha256')} ==
                     {k:v for k,v in after.items() if k not in ('engineId','runtimeSha256')}, 'Engine policy differs')
        for kind, name in identity_contract.NAMES.items():
            path = paths['lib/arm64-v8a/' + name]
            marker = identity_contract.marker(path.read_bytes())
            previous = identity_contract.marker(archive.read('lib/arm64-v8a/' + name))
            need(identity_contract.policy(marker) == identity_contract.policy(previous), 'Inherited native policy changed')
            need(marker['baseApkSha256'] == BASE and marker['payloadSha256'] == identity['payloadSha256'] and
                 sha(path) == identity['markers'][kind]['runtimeSha256'] and
                 identity_contract.digest(identity_contract.canonical(marker)) == identity['markers'][kind]['fingerprintSha256'],
                 'Native marker/receipt binding differs')
            for source, checksum in marker['productiveTransforms'].items():
                if source.startswith('station-direct-download-20261013/'):
                    need(sha(REPO / 'integration' / source) == checksum, 'Compiled overlay source changed')
            for entry, checksum in marker['payloadSha256'].items():
                if entry in expected:
                    need(expected[entry] == checksum, 'Changed bound payload differs')
                else:
                    with archive.open(entry) as stream:
                        need(hashlib.file_digest(stream, 'sha256').hexdigest() == checksum, 'Inherited bound payload differs')
        for engine in identity['engines']:
            for library, checksum in {engine['library']:engine['coreSha256'], engine['runtimeLibrary']:engine['runtimeSha256'],
                                       **engine.get('dependencySha256', {})}.items():
                need('/' not in library and '\\' not in library, 'Dependency must be a basename')
                entry = 'lib/arm64-v8a/' + library
                if entry in expected:
                    need(expected[entry] == checksum, 'Renewed runtime dependency differs')
                else:
                    with archive.open(entry) as stream:
                        need(hashlib.file_digest(stream, 'sha256').hexdigest() == checksum, 'Core/dependency changed')
    return freeze, identity, paths, expected, registry


def package(args):
    need(not args.out.exists() and not args.freeze.exists(), 'Fresh APK and source freeze are required')
    identity_file = args.identity / 'runtime-identity.json'
    identity = read(identity_file)
    sources = {str(source.relative_to(REPO)): sha(source)
               for folder in ('java', 'recipe')
               for source in sorted((HERE.parent / folder).rglob('*'))
               if source.is_file() and source.suffix in ('.java', '.py')}
    paths = {'classes28.dex': args.dex, 'assets/station-online/engines.json': args.identity / 'engines.json',
             **{'lib/arm64-v8a/' + name: args.identity / name for name in identity_contract.NAMES.values()}}
    freeze = {'revision':'DIRECT-DOWNLOAD-20261013', 'sourceFrozen':True, 'baseApkSha256':BASE,
              'identityReceiptSha256':sha(identity_file), 'packageRecipeSha256':sha(__file__), 'sources':sources,
              'payloads':{name:{'path':str(path.resolve()),'bytes':path.stat().st_size,'sha256':sha(path)}
                          for name,path in paths.items()}}
    args.freeze.write_text(json.dumps(freeze,indent=2)+'\n')
    verify_inputs(args.donor, args.freeze, identity_file)
    source = REPO / 'integration/psx-online/recipe/assemble_apk.py'
    spec = importlib.util.spec_from_file_location('classic_zip_assembler', source)
    primitive = importlib.util.module_from_spec(spec); spec.loader.exec_module(primitive)
    primitive.BASE_SHA = BASE; primitive.REPLACED = REPLACED; primitive.ADDED = frozenset(); primitive.PAYLOADS = REPLACED
    primitive.inputs = verify_inputs
    primitive.package(args.donor, args.freeze, identity_file, args.out)
    report_file = args.out.with_suffix('.package.json')
    report = read(report_file)
    need(report['preservedEntryCount'] == 13855 and set(report['replacedEntrySha256']) == REPLACED,
         'Final five-entry scope differs')
    report.update(revision='DIRECT-DOWNLOAD-20261013', changedDexPartitions=['classes28.dex'],
                  preservedDexPartitions=39, retainedDex28Classes=266, manifestResourcesAndEmulatorCoresPreserved=True,
                  signingKeyAvailable=False, signatureVerified=False, physicalDownloadValidated=False,
                  directGatewayConfigured=True)
    report_file.write_text(json.dumps(report,indent=2)+'\n')
    return {key:report[key] for key in ('revision','unsignedApkSha256','unsignedApkBytes','preservedEntryCount',
                                       'preservedDexPartitions','signingPerformed','installed')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('donor','dex','identity','freeze','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    print(json.dumps(package(parser.parse_args())))
