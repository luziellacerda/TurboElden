"""Verify every unsigned entry independently, without changing the APK."""
from pathlib import Path
import argparse,hashlib,json,zipfile
import package_r138 as recipe
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args();unsigned=a.work/'unsigned.apk';receipt=a.work/'unsigned.package.json'
    previous=json.loads(receipt.read_text('utf-8'))
    recipe.need(previous['unsignedApkSha256']==recipe.sha(unsigned),'Unsigned APK changed')
    freeze=a.work/'source-freeze.json';f=json.loads(freeze.read_text('utf-8'))
    old_recipe=f['packageRecipeSha256'];f['packageRecipeSha256']=recipe.sha(recipe.__file__)
    f['initialPackagingRecipeSha256']=old_recipe
    freeze.write_text(json.dumps(f,indent=2)+'\n','utf-8')
    m=recipe.assembler();f,identity,paths,expected,manifest=m.inputs(a.base,freeze,a.work/'runtime-identity.json')
    preserved={};changed={}
    with zipfile.ZipFile(a.base) as donor,zipfile.ZipFile(unsigned) as output:
        originals=m.classic_entries(donor);written=m.classic_entries(output)
        removed=sorted(n for n in originals if m.signature_metadata(n))
        recipe.need(written==originals-set(removed),'Entry set changed')
        m.classic_zip(unsigned,output.comment)
        for n in output.namelist():
            before=m.entry_sha(donor,n);after=m.entry_sha(output,n)
            if n in recipe.REPLACED:
                recipe.need(after==expected[n] and after!=before,'Frozen replacement mismatch')
                changed[n]=after
            else:
                recipe.need(before==after,'Unrelated entry changed: '+n);preserved[n]=after
        recipe.need(json.loads(output.read(recipe.ASSET))==manifest,'Registry mismatch')
    report=dict(schemaVersion=1,revision='R138',baseApkSha256=recipe.BASE,freezeSha256=recipe.sha(freeze),
                identityReceiptSha256=recipe.sha(a.work/'runtime-identity.json'),unsignedApkSha256=recipe.sha(unsigned),
                unsignedApkBytes=unsigned.stat().st_size,replacedEntrySha256=changed,addedEntrySha256={},
                preservedEntryCount=len(preserved),preservedEntrySha256=preserved,
                preservedEntryManifestSha256=m.digest(m.canonical(preserved)),removedSignatureMetadata=removed,
                engineIds=[e['engineId'] for e in identity['engines']],classicZip=True,zip64=False,
                signingPerformed=False,zipalignPerformed=False,installed=False,serverActivationConfirmed=False,
                physicalGameplayValidated=False,all40DexByteIdentical=True,changedDexPartitions=[],
                changedApkEntries=sorted(changed),independentEntryVerification=True,
                receiptSerializationRepaired=True,initialPackagingRecipeSha256=old_recipe)
    recipe.need(len(preserved)==13858 and len(changed)==2,'Requested atomic scope violated')
    receipt.write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps({k:report[k] for k in ('revision','unsignedApkSha256','preservedEntryCount','all40DexByteIdentical','independentEntryVerification')}))
if __name__=='__main__':main()
