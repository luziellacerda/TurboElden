"""Recheck the signed artifact independently of ZIP alignment/signing."""
from pathlib import Path
import argparse, hashlib, json, zipfile, subprocess, re

BASE='aeeb2f8167a442db5a58b990cf6d45b613fab42b1e7a9bbc0bf3214b260420c4'
REPLACED={'AndroidManifest.xml','classes35.dex','classes36.dex','assets/station-online/engines.json'}
ADDED={'lib/arm64-v8a/libstation_mupen64plus_core.so','lib/arm64-v8a/libstation_mupen64plus_runtime.so'}
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def entry(z,n):
    h=hashlib.sha256()
    with z.open(n) as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--apk',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--java',type=Path,required=True);p.add_argument('--apksigner-jar',type=Path,required=True);p.add_argument('--zipalign',type=Path,required=True);a=p.parse_args()
    assert sha(a.base)==BASE
    signature=subprocess.run([str(a.java),'-jar',str(a.apksigner_jar),'verify','--verbose','--print-certs',str(a.apk)],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True).stdout
    certificate=re.search(r'Signer #1 certificate SHA-256 digest: ([0-9a-f]+)',signature)
    assert certificate and certificate.group(1)=='7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825','Certificate changed'
    assert re.search(r'Verified using v2 scheme.*: true',signature) and re.search(r'Verified using v3 scheme.*: true',signature),'v2/v3 signature missing'
    subprocess.run([str(a.zipalign),'-P','16','-c','4',str(a.apk)],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
    identity=json.loads((Path(__file__).resolve().parents[1]/'native/RUNTIME-IDENTITY.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(a.base) as base,zipfile.ZipFile(a.apk) as final:
        original={n for n in base.namelist() if not n.startswith('META-INF/')}; names={n for n in final.namelist() if not n.startswith('META-INF/')}
        assert len(final.namelist())==len(set(final.namelist())), 'Duplicate entries'
        assert names-original==ADDED and original-names==set()
        preserved={};changes={}
        for n in sorted(original):
            old=entry(base,n);new=entry(final,n)
            if n in REPLACED:assert old!=new;changes[n]=new
            else:assert old==new,n;preserved[n]=new
        for n in sorted(ADDED):changes[n]=entry(final,n)
        assert changes['lib/arm64-v8a/libstation_mupen64plus_core.so']==identity['coreSha256']
        assert changes['lib/arm64-v8a/libstation_mupen64plus_runtime.so']==identity['runtimeSha256']
        assert changes['assets/station-online/engines.json']==identity['enginesAssetSha256']
    receipt={'schemaVersion':1,'revision':'R125','baseApkSha256':BASE,'apkSha256':sha(a.apk),'apkBytes':a.apk.stat().st_size,'changedEntries':changes,'preservedEntriesCount':len(preserved),'preservedEntryManifestSha256':hashlib.sha256(json.dumps(preserved,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'signingCertificateSha256':'7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825','signatureSchemesVerified':['v2','v3'],'zipAlignmentVerifiedBytes':16384,'physicalGameplayValidated':False,'serverActivationConfirmed':False,'installed':False}
    a.receipt.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:receipt[k] for k in ('revision','apkSha256','apkBytes','preservedEntriesCount','installed')}))
if __name__=='__main__':main()
