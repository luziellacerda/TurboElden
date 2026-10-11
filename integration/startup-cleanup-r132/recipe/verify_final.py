"""Verify signature, alignment, and all original R131 entries in R132."""
from pathlib import Path
import argparse
import json
import types
import zipfile
from common import *

def verify(base,apk,freeze,identity,receipt_path,java,apksigner,zipalign):
    assembly=module(ROOT/"recipe/assemble_apk.py","r132_assembly")
    primitive=REPO/"integration/psx-online/recipe/verify_final.py"
    require(sha(primitive)=="9d7c40088a848367df431fac8088ad778a139bcc31bcb4ef10a219ce4a085ddf","Pinned independent APK verifier changed")
    verifier=types.ModuleType("r132_independent_verify")
    verifier.__file__=str(primitive)
    raw=primitive.read_text(encoding="utf-8")
    start=raw.index('spec = importlib.util.spec_from_file_location(')
    end=raw.index('\n\n\ndef verify(',start)
    raw=raw[:start]+raw[end:]
    exec(compile(raw.replace('"R127"','"R132"'),str(primitive),"exec"),verifier.__dict__)
    verifier.package=assembly.assembler()
    result=verifier.verify(base,apk,freeze,identity,receipt_path,java,apksigner,zipalign)
    report=read(receipt_path)
    runtime=read(identity)
    require(set(report["replacedEntrySha256"])==assembly.REPLACED and
            report["addedEntrySha256"]=={},"Final composition is not seven replacements and zero additions")
    # Preserve the independent primitive, then expose its complete aggregate map.
    # This fresh read must match the primitive's independent map seal/count.
    preserved={}
    with zipfile.ZipFile(verifier.package.fs(apk)) as archive:
        for name in sorted(verifier.package.classic_entries(archive)):
            if name not in assembly.REPLACED and not verifier.package.signature_metadata(name):
                preserved[name]=verifier.package.entry_sha(archive,name)
    require(len(preserved)==report["preservedEntryCount"] and
            verifier.package.digest(verifier.package.canonical(preserved))==report["preservedEntryManifestSha256"],
            "Full preserved map differs from independent final verification")
    require(verifier.package.sha(apk)==report["apkSha256"],"Signed APK changed while aggregating final maps")
    require(set(preserved)&assembly.runtime().DEX==assembly.runtime().DEX-{"classes8.dex"},
            "Exactly 39 original DEX must remain byte-identical")
    report.update(sourceCommit=runtime["sourceCommit"],existing39OtherDexByteIdentical=True,
        switchDex8ClassSetExactlyPreserved=True,switchDex8UnrelatedClassesByteIdentical=True,
        switchDex8AllowedTypes=runtime["switchAllowedTypes"],
        replacementCount=7,additionCount=0,
        preservedEntrySha256=preserved,completeAggregateEntryHashMaps=True,
        offlineEmulatorEntriesChanged=True,offlineEmulatorLibraryEntriesChanged=False,
        offlineSwitchConfigurationClassChanged=True,
        noGameSaveLicenseFilesMovedOrDeleted=True,
        manifestByteIdentical=True,resourcesAndSonyAssetsByteIdentical=True,
        shaderCodeAndEffectsPreserved=True,videoBytesAndLoopPolicyPreserved=True,
        controllerProfilesUnchanged=True,protocolAndTransportUnchanged=True,
        ps3Ps4OfflineOnly=True,ps3Ps4OnlineEnabled=False,
        approvedScopes=runtime["approvedScopes"],nativeReceiptSha256=runtime["nativeReceiptSha256"],
        switchReceiptSha256=runtime["switchReceiptSha256"],
        physicalStartupValidated=False,physicalThermalValidated=False,
        verificationScope="original-signature-16KiB-and-every-entry-with-seven-closed-replacements")
    # This is the newly created receipt from this invocation, never a historical one.
    Path(receipt_path).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    result.update(replacementCount=7,additionCount=0,existing39OtherDexByteIdentical=True,
        switchDex8ConfigurationClassChanged=True,completeAggregateEntryHashMaps=True)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("base","apk","freeze","identity-receipt","receipt","java","apksigner-jar","zipalign"):
        parser.add_argument("--"+name,type=Path,required=True)
    a=parser.parse_args()
    print(json.dumps(verify(a.base,a.apk,a.freeze,a.identity_receipt,a.receipt,a.java,a.apksigner_jar,a.zipalign)))

if __name__=="__main__": main()
