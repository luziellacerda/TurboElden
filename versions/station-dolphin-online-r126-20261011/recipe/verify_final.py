"""Verify an aligned/signed R126 APK using the actual Android tools and bytes."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import zipfile

spec=importlib.util.spec_from_file_location("r126_package",Path(__file__).with_name("package_r126.py"))
package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
identity=package.identity
CERT="7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("base","apk","freeze","runtime-dir","receipt","java","apksigner-jar","zipalign"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    frozen,runtime,replacements,additions,expected=package.inputs(a.base,a.freeze,a.runtime_dir)
    signature=subprocess.run([str(a.java),"-jar",str(a.apksigner_jar),"verify","--verbose","--print-certs",str(a.apk)],
                             capture_output=True,text=True,encoding="utf-8",errors="replace",check=True)
    certificate=re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-f]+)",signature.stdout)
    if not certificate or certificate.group(1)!=CERT: raise ValueError("Installed signing identity was not preserved")
    if re.search(r"Signer #2 certificate",signature.stdout): raise ValueError("Unexpected additional signer")
    for scheme in ("v2","v3"):
        if not re.search(r"Verified using "+scheme+r" scheme.*: true",signature.stdout): raise ValueError("Missing verified signature scheme: "+scheme)
    subprocess.run([str(a.zipalign),"-P","16","-c","4",str(a.apk)],capture_output=True,text=True,encoding="utf-8",errors="replace",check=True)
    preserved,changed={},{}
    with zipfile.ZipFile(a.base) as base,zipfile.ZipFile(a.apk) as final:
        original={n for n in base.namelist() if not package.signature_metadata(n)}
        names={n for n in final.namelist() if not package.signature_metadata(n)}
        if len(final.namelist())!=len(set(final.namelist())): raise ValueError("Duplicate final ZIP entry")
        if names-original!=package.ADDED or original-names: raise ValueError("Final entry set differs")
        for name in sorted(original):
            old,new=package.entry_sha(base,name),package.entry_sha(final,name)
            if name in package.REPLACED:
                if old==new or new!=expected[name]: raise ValueError("Replacement differs from frozen bytes: "+name)
                changed[name]=new
            else:
                if old!=new: raise ValueError("Preserved entry changed: "+name)
                preserved[name]=new
        for name in sorted(package.ADDED):
            changed[name]=package.entry_sha(final,name)
            if changed[name]!=expected[name]: raise ValueError("New native bytes differ: "+name)
        if preserved[identity.PREFIX+identity.N64_CORE]!=identity.N64_CORE_SHA or preserved["classes36.dex"]!=identity.DEX36_SHA:
            raise ValueError("N64 core/hooks not preserved")
        for engine in runtime["engines"]:
            for name,digest in engine["dependencySha256"].items():
                if package.entry_sha(final,identity.PREFIX+name)!=digest: raise ValueError("Pinned native dependency differs")
        package.classic_zip(a.apk,final.comment)
    report={"schemaVersion":2,"revision":"R126","baseApkSha256":identity.BASE_SHA,"apkSha256":identity.sha(a.apk),
            "apkBytes":identity.fs(a.apk).stat().st_size,"changedEntries":changed,"preservedEntriesCount":len(preserved),
            "preservedEntryManifestSha256":identity.digest(identity.canonical(preserved)),"signingCertificateSha256":CERT,
            "signatureSchemesVerified":["v2","v3"],"zipAlignmentVerifiedBytes":16384,"classicZip":True,
            "engineIds":[engine["engineId"] for engine in runtime["engines"]],"offlineLibrariesChanged":False,
            "n64CorePreserved":True,"n64PluginsPreserved":True,"physicalGameplayValidated":False,
            "serverActivationConfirmed":False,"installed":False}
    identity.write_json(a.receipt,report)
    print(json.dumps({key:report[key] for key in ("revision","apkSha256","apkBytes","preservedEntriesCount","installed")}))

if __name__=="__main__":main()
