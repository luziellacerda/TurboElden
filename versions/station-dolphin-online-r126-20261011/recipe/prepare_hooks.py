#!/usr/bin/env python3
"""Rename only online Adrenotools hooks in the isolated verified source stage."""
import argparse, difflib, hashlib, io, json, pathlib, tarfile
HERE=pathlib.Path(__file__).resolve().parent.parent
def digest(b): return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("--stage",required=True); p.add_argument("--cache",required=True); a=p.parse_args()
    stage=pathlib.Path(a.stage).resolve(); cache=pathlib.Path(a.cache).resolve()
    lock=json.loads((stage/"station-r126-dependency-receipt.json").read_text())
    module=next(m for m in lock["archives"] if m["path"]=="Externals/libadrenotools")
    if module["commit"]!="8fae8ce254dfc1344527e05301e43f37dea2df80": raise ValueError("Unexpected Adrenotools pin")
    data=(cache/(module["commit"]+".tar.gz")).read_bytes()
    if digest(data)!=module["sha256"]: raise ValueError("Adrenotools archive hash mismatch")
    changes={"src/driver.cpp": {"libhook_impl.so":"libstation_dolphin_hook_impl.so","libmain_hook.so":"libstation_dolphin_hook.so"},"src/hook/hook_impl.cpp": {"libhook_impl.so":"libstation_dolphin_hook_impl.so","libfile_redirect_hook.so":"libstation_dolphin_file_redirect_hook.so","libgsl_alloc_hook.so":"libstation_dolphin_gsl_alloc_hook.so"}}
    planned=[]; records=[]; patch=[]
    with tarfile.open(fileobj=io.BytesIO(data),mode="r:gz") as tar:
        for path,replacements in changes.items():
            member=next(x for x in tar.getmembers() if x.name.endswith("/"+path))
            original=tar.extractfile(member).read(); text=original.decode()
            for old,new in replacements.items():
                if text.count('"'+old+'"')!=1: raise ValueError("Pinned hook anchor mismatch")
                text=text.replace('"'+old+'"','"'+new+'"')
            modified=text.encode(); dest=stage/module["path"]/path
            if dest.read_bytes() not in (original,modified): raise ValueError("Unrecorded hook source edits")
            planned.append((dest,modified)); full=module["path"]+"/"+path
            records.append({"path":full,"upstreamSha256":digest(original),"patchedSha256":digest(modified)})
            patch.extend(difflib.unified_diff(original.decode().splitlines(True),text.splitlines(True),fromfile="a/"+full,tofile="b/"+full))
    for dest,data in planned: dest.write_bytes(data)
    patch="".join(patch).encode(); (HERE/"patches"/"adrenotools-station-r126.patch").write_bytes(patch)
    receipt={"commit":module["commit"],"sourceArchiveSha256":module["sha256"],"patchSha256":digest(patch),"files":records,"offlineLibrariesModified":False}
    (stage/"station-r126-hook-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    (HERE/"evidence"/"hooks-r126.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"files":len(records),"patchSha256":digest(patch)}))
if __name__=="__main__": main()
