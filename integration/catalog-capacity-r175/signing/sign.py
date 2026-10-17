"""Sign the reviewed R175 using the received original private authority only.

No installation, production publication or secret in argv/logs. Fresh outputs.
The OS still confirms an in-app update; this script does not change phones.
"""
from pathlib import Path
import argparse, base64, hashlib, json, os, re, struct, subprocess, zipfile

CERT='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
KEY='8ea836990d8c7b4980d4d517ce9d83746bb11adabd1f45fdc78de7a8e7c26f9e'
CREDENTIALS='45773d5a1a96bc34ff1a268135025189bebb1d57577c6ccf1568bed705202d9f'
BASE='6ab94ff0999ef2f0d5febe0d46fd27e715692c1aea8c216a2ce87d9cb8b51c4d'

def need(value,reason):
    if not value:raise ValueError(reason)
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,log,env=None):
    r=subprocess.run(list(map(str,args)),env=env,capture_output=True,text=True,timeout=900)
    Path(log).write_text(r.stdout+r.stderr)
    need(r.returncode==0,'Signing check failed: '+Path(log).name);return r.stdout+r.stderr
def entries(path,expected):
    with zipfile.ZipFile(path) as z:
        need(len(z.namelist())==len(set(z.namelist()))==len(expected) and set(z.namelist())==set(expected),'APK entry set differs')
        for name,h in expected.items():
            with z.open(name) as f:need(hashlib.file_digest(f,'sha256').hexdigest()==h,'APK entry content differs: '+name)

def main(task,sdk,signing):
    package=task/'package';receipt=json.loads((package/'unsigned-package.json').read_text())
    need(receipt['schema']=='station.r175.package.v1' and receipt['passed'] is True and receipt['baseApkSha256']==BASE and receipt['entryCount']==13861 and receipt['preservedEntryCount']==13855 and receipt['preservedDexPartitions']==39,'Exact R175 scoped receipt required')
    allowed={'classes28.dex','AndroidManifest.xml','assets/station-online/engines.json',*('lib/arm64-v8a/'+n for n in ['libstation_psx_online.so','libstation_mupen64plus_runtime.so','libstation_dolphin_runtime.so'])}
    need(set(receipt['replacedEntries'])==allowed,'Six-entry scope required')
    for name,value in receipt['sourceSha256'].items():
        source=Path(__file__).resolve().parents[3]/name
        need(sha(source)==value,'Frozen source changed since assembly')
    need(sha(task/'compile/receipt.json')==receipt['compileReceiptSha256'] and sha(task/'native/receipt.json')==receipt['nativeReceiptSha256'],'Build receipts changed')
    unsigned=package/'TurboStations-Premium-R175-unsigned.apk';expected=receipt['expectedEntrySha256']
    need(sha(unsigned)==receipt['unsignedApkSha256'] and unsigned.stat().st_size==receipt['unsignedApkBytes'],'Unsigned APK changed')
    entries(unsigned,expected)
    key=signing/'original.keystore';credentials=signing/'credentials.json'
    need(not key.is_symlink() and not credentials.is_symlink() and sha(key)==KEY and sha(credentials)==CREDENTIALS,'Original received signing authority required')
    secret=json.loads(credentials.read_text());need(set(secret)=={'--ks-key-alias','--ks-pass','--key-pass'},'Private credential format')
    need(secret['--ks-pass'].startswith('pass:') and secret['--key-pass'].startswith('pass:'),'Private credential encoding')
    env={**os.environ,'STATION_R175_KS_SECRET':secret['--ks-pass'][5:],'STATION_R175_KEY_SECRET':secret['--key-pass'][5:]}
    tools=sdk/'build-tools/36.0.0';final=task/'final';final.mkdir(exist_ok=False)
    aligned=final/'R175-aligned.apk';partial=final/'TurboStations-Premium-R175.apk.partial';apk=final/'TurboStations-Premium-R175.apk'
    try:
        pem=run(['keytool','-list','-rfc','-keystore',key,'-alias',secret['--ks-key-alias'],'-storepass:env','STATION_R175_KS_SECRET'],final/'key-certificate.log',env)
        match=re.search(r'-----BEGIN CERTIFICATE-----\s*(.*?)\s*-----END CERTIFICATE-----',pem,re.S)
        need(match and hashlib.sha256(base64.b64decode(match[1])).hexdigest()==CERT,'Original certificate differs')
        run([tools/'zipalign','-P','16','4',unsigned,aligned],final/'alignment.log')
        entries(aligned,expected)
        run([tools/'apksigner','sign','--ks',key,'--ks-key-alias',secret['--ks-key-alias'],'--ks-pass','env:STATION_R175_KS_SECRET','--key-pass','env:STATION_R175_KEY_SECRET','--v1-signing-enabled','false','--v2-signing-enabled','true','--v3-signing-enabled','true','--v4-signing-enabled','false','--out',partial,aligned],final/'sign.log',env)
    finally:
        env.pop('STATION_R175_KS_SECRET',None);env.pop('STATION_R175_KEY_SECRET',None);secret.clear()
    verified=run([tools/'apksigner','verify','--verbose','--print-certs',partial],final/'signature.log')
    need(CERT in verified.lower() and 'Verified using v2 scheme (APK Signature Scheme v2): true' in verified and 'Verified using v3 scheme (APK Signature Scheme v3): true' in verified,'Final signature verification')
    run([tools/'zipalign','-c','-P','16','4',partial],final/'final-alignment.log');entries(partial,expected)
    badge=run([tools/'aapt2','dump','badging',partial],final/'badging.log')
    need("package: name='org.turboramastation.frontend' versionCode='17' versionName='1.0.8-R175'" in badge and "minSdkVersion:'26'" in badge and "targetSdkVersion:'34'" in badge and "native-code: 'arm64-v8a'" in badge,'Final Android metadata scope')
    partial.rename(apk)
    proof={'schema':'station.catalog-capacity.final.r175.v1','passed':True,'packageRevision':'R175','sourceCommit':receipt['sourceCommit'],
        'apkSha256':sha(apk),'apkBytes':apk.stat().st_size,'baseApkSha256':BASE,'signatureCertificateSha256':CERT,
        'v2':True,'v3':True,'zipAlignment16KiB':True,'versionCode':17,'minimumSdk':26,'targetSdk':34,
        'checkedEntries':13861,'preservedEntryCount':13855,'replacedEntries':sorted(allowed),'changedDexPartitions':['classes28.dex'],'preservedDexPartitions':39,
        'unsignedPackageReceiptSha256':sha(package/'unsigned-package.json'),'signerRecipeSha256':sha(Path(__file__)),
        'installed':False,'serverRegistered':False,'productionUpdaterEnabled':False,'physicalGameplayValidated':False,'physicalInstallerValidated':False,'stable':False}
    (final/'final-apk-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    # Only remove this signing stage's known intermediate, after final readback.
    aligned.unlink()
    print(json.dumps(proof))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--task',required=True,type=Path);p.add_argument('--sdk',required=True,type=Path);p.add_argument('--signing-directory',required=True,type=Path)
    a=p.parse_args();main(a.task.resolve(),a.sdk.resolve(),a.signing_directory.resolve())
