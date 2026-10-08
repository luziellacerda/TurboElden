"""Bundle exact public metadata from verified APKs and the last server export."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent.parent
APP=ROOT.parents[1]
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,value):(ROOT/'activation'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
    (ROOT/'activation').mkdir(exist_ok=True)
    current=json.loads((APP/'release-channels/ACTIVE.json').read_text('utf8'))
    paths={
      'r76':(BACKUP/'stable-2-players-r76/TurboStations-Premium-R76-20261008.apk','d7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51'),
      'r81':(BACKUP/'test-up-to-4-players-r81/TurboStations-Premium-R81-20261008.apk','85fac8f51daa3a370eabb14d98832f75c2f30ff81422c549538ee715627032c6')}
    engines={}
    for release,(path,digest) in paths.items():
        assert sha(path)==digest
        with zipfile.ZipFile(path) as z:raw=z.read('assets/station-online/engines.json')
        manifest=json.loads(raw);engines[release]=manifest
        save('engines-'+release+'.json',{'apkSHA256':digest,'assetSHA256':hashlib.sha256(raw).hexdigest(),'assetPath':'assets/station-online/engines.json','manifest':manifest})
    profiles=[]
    for release,manifest in engines.items():
        for e in manifest['engines']:
            if not e.get('launchReady') or e['platform'] not in ['snes','megadrive']:continue
            options=e['options'];known=[('standard-2p-v1',[1,1],options)]
            if release=='r81':
                if e['platform']=='snes':known+=[('snes-multitap-port2-v1',[1,257,1,1,1],options)]
                elif e['platform']=='megadrive' and not options:known+=[('megadrive-sega-teamplayer-v1',[1]*8,'clownmdemu_input_protocol = "sega"\n'),('megadrive-ea-4way-v1',[1]*4,'clownmdemu_input_protocol = "ea"\n')]
            for name,devices,opts in known:
                canonical={'schemaVersion':1,'controllerProfile':name,'devices':devices,'coreOptions':opts}
                raw=json.dumps(canonical,ensure_ascii=False,separators=(',',':')).encode('utf8')
                profiles.append(dict(release=release,platform=e['platform'],engineId=e['engineId'],coreSha256=e['coreSha256'],runtimeSha256=e['runtimeSha256'],profileSHA256=hashlib.sha256(raw).hexdigest(),canonical=canonical))
    assert any(p['profileSHA256']=='f59408b49f6e110a569fe9498af433b9f67c9586cbb8648238b8e571bb8b0143' for p in profiles)
    save('controller-profiles.json',{'schemaVersion':1,'purpose':'Exact controller/options hashes only; these do not approve a game, mode or capacity.','entries':profiles})
    source=APP/'docs/server/recovery-r79-20261008/CATALOGO-REV19.json';catalog=json.loads(source.read_text('utf8'))
    ids={'826da6daebe9edbebffb3721f83abf12','ac79b8fc351cb0811a7e9b51a099ba9c','station_df50d575815ab105084a79d68e0c8fb3'}
    items=[row for row in catalog['items'] if row['itemId'] in ids];assert len(items)==3
    save('pilot-items-revision19.json',{'schemaVersion':1,'revision':19,'catalogExportSHA256':sha(source),'requiresCurrentServerDescriptorComparison':True,'profilesApproved':False,'items':items})
    print('Verified two APK engine manifests, controller hashes and three exact pilot item records')
if __name__=='__main__':main()
