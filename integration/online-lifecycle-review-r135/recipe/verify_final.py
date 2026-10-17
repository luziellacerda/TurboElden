"""Verify real signature/alignment and every entry of the closed R135 APK."""
from pathlib import Path
import argparse,json,types,zipfile
from release_common import *

def verify(base,apk,freeze,identity,receipt_path,java,apksigner,zipalign):
    for path,expected in [(java,'1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406'),(apksigner,'00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7'),(zipalign,'aa2475ce201962b871fb8daec020da03fd6292c9c1f422cd0fe2e39b20d4f673')]:
        require(sha(path)==expected,'Pinned signature/alignment tool differs: '+Path(path).name)
    assembly=module(ROOT/'recipe/assemble_apk.py','r135_assembly')
    primitive=REPO/'integration/psx-online/recipe/verify_final.py'
    require(sha(primitive)=='9d7c40088a848367df431fac8088ad778a139bcc31bcb4ef10a219ce4a085ddf','Pinned independent verifier changed')
    verifier=types.ModuleType('r135_independent_verifier');verifier.__file__=str(primitive)
    raw=primitive.read_text(encoding='utf-8');start=raw.index('spec = importlib.util.spec_from_file_location(');end=raw.index('\n\n\ndef verify(',start)
    exec(compile((raw[:start]+raw[end:]).replace('"R127"','"R135"'),str(primitive),'exec'),verifier.__dict__)
    verifier.package=assembly.assembler()
    verifier.verify(base,apk,freeze,identity,receipt_path,java,apksigner,zipalign)
    report=read(receipt_path);runtime=read(identity)
    require(set(report['replacedEntrySha256'])==REPLACED and report['addedEntrySha256']=={} and report['preservedEntryCount']==13855,'Signed APK scope differs')
    preserved={}
    with zipfile.ZipFile(apk) as archive:
        for name in archive.namelist():
            if name not in REPLACED and not verifier.package.signature_metadata(name):preserved[name]=verifier.package.entry_sha(archive,name)
    require(len(preserved)==13855 and digest(canonical(preserved))==report['preservedEntryManifestSha256'],'Complete independent preserved map differs')
    require(PRESERVED_DEX<=set(preserved) and DEX_ASSET in preserved and preserved[PREFIX+'libstation_frontend.so']==FRONTEND_SHA,'Untouched DEX and frontend bytes differ')
    require(sha(apk)==report['apkSha256'],'Signed APK changed during proof aggregation')
    report.update(sourceCommit=runtime['sourceCommit'],sourceSha256=runtime['sourceSha256'],replacementCount=5,additionCount=0,preservedEntrySha256=preserved,completeAggregateEntryHashMaps=True,existing39DexByteIdentical=True,ps4AssetDexByteIdentical=True,dexScopes=runtime['dexScopes'],dexScopedClassesVerified=True,frontendLibraryByteIdentical=True,manifestByteIdentical=True,resourcesAndSonyAssetsByteIdentical=True,offlineEmulatorEntriesChanged=False,offlineEmulatorLibraryEntriesChanged=False,nativeRebuildsIdentityOnly=True,coreAndControllerPoliciesUnchanged=True,approvedScopes=SCOPES,payloadReceiptSha256=runtime['payloadReceiptSha256'],physicalStartupValidated=False,physicalGameplayValidated=False,verificationScope='original-signature-16KiB-and-every-entry-with-five-closed-replacements')
    Path(receipt_path).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return {k:report[k] for k in ('revision','apkSha256','apkBytes','preservedEntryCount','replacementCount','additionCount','installed')}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('base','apk','freeze','identity-receipt','receipt','java','apksigner-jar','zipalign'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(verify(a.base,a.apk,a.freeze,a.identity_receipt,a.receipt,a.java,a.apksigner_jar,a.zipalign)))
if __name__=='__main__':main()
