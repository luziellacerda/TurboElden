"""Copy only the reviewed sources and receipts into the isolated E: delivery."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parent
OUT=Path(r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\native')
manifest=json.loads((ROOT/'native-delta-manifest.json').read_text(encoding='utf8'))
overlay={
    'baseRuntimeSHA256':'9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2',
    'files':{name:{'beforeSHA256':values['baseSHA256'],'afterSHA256':values['patchedSHA256']}
             for name,values in manifest['files'].items()},
    'jniMethods':['stationRecoveryControl','stationRecoveryStatus','stationRecoveryStalled','stationRequestQuit'],
    'baseNetworkFrontendSHA256':manifest['baseFrontendSHA256'],
    'preservedRecoveryPollSHA256':manifest['preservedRecoveryPollSHA256'],
    'scope':'Native lifecycle, recovery input queue, and upstream catch-up pacing',
}
(ROOT/'OVERLAY-MANIFEST.json').write_text(json.dumps(overlay,indent=2)+'\n',encoding='utf8')
OUT.mkdir(parents=True,exist_ok=True)
copied={}
for name in manifest['files']:
    source=ROOT/'sources'/name;target=OUT/'source'/name
    assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['files'][name]['patchedSHA256']
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    copied['source/'+name]=hashlib.sha256(target.read_bytes()).hexdigest()
for name in ('prepare_native_delta.py','publish_delta.py','README.md','OVERLAY-MANIFEST.json',
             'native-delta-manifest.json','station-lifecycle-r74.patch',
             'tests/lifecycle_probe.py','tests/lifecycle-probe-result.json',
             'tests/recovery_input_probe.py','tests/recovery-input-result.json',
             'tests/pacing_probe.py','tests/pacing-result.json'):
    target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    copied[name]=hashlib.sha256(target.read_bytes()).hexdigest()
(OUT/'DELIVERY-SHA256.json').write_text(json.dumps(copied,indent=2)+'\n',encoding='utf8')
print(json.dumps({'output':str(OUT),'files':len(copied),'overlaySHA256':copied['OVERLAY-MANIFEST.json']},indent=2))
