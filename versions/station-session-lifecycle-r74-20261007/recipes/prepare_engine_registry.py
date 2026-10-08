"""Prepare only R74 app engine IDs and append-only server additions; no deployment."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,re,zipfile

BASE_SHA='b23ff3d1e319ee050e6eb867e2643a5f66661da481dd2e3a4e50089d1604f077'
OLD_RUNTIME='9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2'
NATIVE_MANIFEST='94f878ad49504c6a1b8e2e4a915f1d81428467e47286be78baf088f06b393096'
FLUSH_SHA='d3a42419124dda592fea217088ed4e4687bf63718f657299ac8d73ad9fa41e12'
DEFAULT_WORK=r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\compiled-final'
DEFAULT_DELTA=r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\native'
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R73-20261007.apk')

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)

def native_identity(native_dir,delta):
    require(native_dir.resolve()==Path(r'E:\R74fixed').resolve(),'Use exact R74 native build directory')
    receipt_path=native_dir/'result.json';r=json.loads(receipt_path.read_text('utf8'))
    manifest_path=delta/'OVERLAY-MANIFEST.json';m=json.loads(manifest_path.read_text('utf8'))
    require(sha(manifest_path)==r['manifestSHA256']==NATIVE_MANIFEST,'Final six-file native delta required')
    require(r['compiled'] and r['baseRuntimeSHA256']==m['baseRuntimeSHA256']==OLD_RUNTIME,'Native baseline/build mismatch')
    require(r['sourceDelta']==m['files'] and len(m['files'])==6,'Native source delta mismatch')
    require(r['r73HandshakePreserved'] and r['handshakeFunctionSHA256']==m['preservedRecoveryPollSHA256']==FLUSH_SHA,'Handshake changed')
    require(r['architecture']=='AArch64' and r['minimumLoadAlignment']>=16384,'Native ABI/alignment mismatch')
    runtime=native_dir/'libstation_retroarch.so'
    require(Path(r['runtimePath']).resolve()==runtime.resolve() and sha(runtime)==r['runtimeSHA256']!=OLD_RUNTIME,'Runtime identity mismatch')
    for name,v in m['files'].items():
        require('..' not in Path(name).parts and not Path(name).is_absolute(),'Invalid delta path')
        require(sha(delta/'source'/name)==sha(Path(r['sourceFolder'])/name)==v['afterSHA256'],'Compiled source changed: '+name)
    require(sha(native_dir/'build.log')==r['buildLogSHA256'],'Build log changed')
    require('Java_org_emulationstation_frontend_netplay_StationRetroActivity_stationRequestQuit' in r['exportsVerified'],'Quit JNI not verified')
    return runtime,r,receipt_path

def engine_delta(original,digest):
    candidate=copy.deepcopy(original);additions=[]
    require(len(original['engines'])==3,'Exact three-engine app manifest required')
    for old,new in zip(original['engines'],candidate['engines']):
        require(old['runtimeSha256']==OLD_RUNTIME,'Wrong R73 engine runtime')
        require(old['engineId'].endswith('-rs3-'+OLD_RUNTIME[:12]),'Wrong R73 engine ID')
        new['runtimeSha256']=digest
        new['engineId']=re.sub(r'-rs3-'+OLD_RUNTIME[:12]+r'$', '-rs4-'+digest[:12],old['engineId'])
        require({k:v for k,v in old.items() if k not in ('runtimeSha256','engineId')}=={k:v for k,v in new.items() if k not in ('runtimeSha256','engineId')},'Core/options/availability changed')
        if old.get('launchReady'):
            require(old['platform'] in ('snes','megadrive') and old['recoveryProtocol']=='station-stream.v2','Unexpected ready engine')
            additions.append(dict(id=new['engineId'],platform=new['platform'],coreSha256=new['coreSha256'],runtimeSha256=digest,recoveryProtocol='station-stream.v2'))
        else:require(old['platform']=='neogeo','Unexpected unavailable engine')
    require(len(additions)==2 and {e['platform'] for e in additions}=={'snes','megadrive'},'Only two server additions allowed')
    return candidate,additions

def main():
    p=argparse.ArgumentParser();p.add_argument('--native-work',default=r'E:\R74fixed');p.add_argument('--native-delta',default=DEFAULT_DELTA)
    p.add_argument('--workspace',default=DEFAULT_WORK);p.add_argument('--base',default=str(BASE));a=p.parse_args()
    w=Path(a.workspace);n=Path(a.native_work);delta=Path(a.native_delta);base=Path(a.base)
    require(w.drive.upper()=='E:' and w.is_dir(),'Existing E: Java build workspace required')
    require(sha(base)==BASE_SHA,'Exact R73 APK required')
    runtime,native,native_receipt=native_identity(n,delta)
    with zipfile.ZipFile(base) as z:
        original=json.loads(z.read('assets/station-online/engines.json'))
        require(hashlib.sha256(z.read('assets/station-online/engines.json')).hexdigest()=='ab47fa69aedc7c5969cb30bb65e027b3b9c1b4282609f8b54fa3e1fd6769b7a7','R73 engine manifest differs')
    candidate,additions=engine_delta(original,native['runtimeSHA256'])
    out=w/'assets/station-online/engines.json';out.parent.mkdir(parents=True,exist_ok=True)
    evidence=w/'evidence';evidence.mkdir(exist_ok=True)
    out.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n','utf8')
    (evidence/'server-engine-registry-additions.json').write_text(json.dumps(additions,indent=2)+'\n','utf8')
    (evidence/'engine-manifest.json').write_bytes(out.read_bytes())
    receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),runtime=str(runtime),runtimeSHA256=native['runtimeSHA256'],
      nativeBuildReceiptSHA256=sha(native_receipt),nativeOverlayManifestSHA256=NATIVE_MANIFEST,manifest=str(out),manifestSHA256=sha(out),
      registryAdditions=additions,registryOperation='append only; never replace existing registry',existingEntriesToPreserve=8,
      removeExistingIds=[],serverRegistryPreservationVerified=False,neogeoLaunchReady=False,serverActivationVerified=False,
      baseAPK_SHA256=BASE_SHA,recipeSHA256=sha(__file__))
    (evidence/'engine-registry.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    print(json.dumps(additions,indent=2))

if __name__=='__main__':main()
