"""Derive new runtime identities from actual bytes; preserve R64 controls/core options."""
from pathlib import Path
import argparse, copy, hashlib, json

SNAPSHOT = Path(__file__).resolve().parent.parent
OLD_RUNTIME = '899e35279cf046242a7ae31f502078080bd6a94404770fe99e1e2e90be58a1ef'
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def generate(runtime_sha):
    if len(runtime_sha) != 64 or any(c not in '0123456789abcdef' for c in runtime_sha) or runtime_sha == OLD_RUNTIME:
        raise ValueError('New compiled runtime SHA256 required')
    original = SNAPSHOT.parent / 'station-online-controls-r64-20261007/assets/station-online/engines.json'
    document = json.loads(original.read_text('utf8'))
    registry = []
    for engine in document['engines']:
        engine['engineId'] = engine['engineId'].removesuffix('-autopass1') + '-rs2-' + runtime_sha[:12]
        if len(engine['engineId']) > 64: raise ValueError('Engine ID too long')
        engine['runtimeSha256'] = runtime_sha
        if engine['launchReady']:
            engine['recoveryProtocol'] = 'station-stream.v2'
            registry.append(dict(id=engine['engineId'], platform=engine['platform'],
                                 coreSha256=engine['coreSha256'], runtimeSha256=runtime_sha,
                                 recoveryProtocol='station-stream.v2'))
    document['androidPeerPlayValidated'] = False
    return document, registry
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--runtime', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    out = Path(a.output).resolve()
    if out.exists(): raise SystemExit('Use a new output directory')
    app, server = generate(sha(a.runtime))
    out.mkdir(parents=True)
    (out/'engines.json').write_text(json.dumps(app,indent=2)+'\n')
    # Append these entries to the effective private registry; never replace legacy entries.
    (out/'server-engine-registry-additions.json').write_text(json.dumps(server,indent=2)+'\n')
    print(json.dumps({'runtimeSHA256':sha(a.runtime),'newEngineIds':[e['id'] for e in server],
                      'legacyRegistryMustBePreserved':True,'productionActivated':False}))
