#!/usr/bin/env python3
"""Fetch immutable public source archives into a NEW build stage, never git clone.

The Gitlinks from the pinned Dolphin tree are the authority for revisions.
Archives are recorded by SHA256; subsequent runs verify the recorded bytes.
Nested gitlinks are fetched by exact tree entries, not branch names.
"""
import argparse, concurrent.futures, configparser, hashlib, io, json, pathlib, re, tarfile, urllib.request

HERE=pathlib.Path(__file__).resolve().parent.parent
def sha256(data): return hashlib.sha256(data).hexdigest()
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Station-Dolphin-pinned-source/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response: return response.read()
def repo_parts(url):
    url=url.rstrip("/")
    m=re.fullmatch(r"https://github.com/([^/]+)/([^/]+?)(?:\.git)?",url)
    return m.groups() if m else None
def archive_url(url,commit):
    if repo_parts(url):
        owner,repo=repo_parts(url); return f"https://codeload.github.com/{owner}/{repo}/tar.gz/{commit}"
    if url=="https://gitlab.com/bzip2/bzip2.git":
        return f"https://gitlab.com/bzip2/bzip2/-/archive/{commit}/bzip2-{commit}.tar.gz"
    raise ValueError("Unrecognized pinned public source origin: "+url)
def unpack(data,dest):
    dest=dest.resolve(); dest.mkdir(parents=True,exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data),mode="r:gz") as tar:
        members=tar.getmembers(); roots={x.name.split("/",1)[0] for x in members}
        if len(roots)!=1: raise ValueError("Archive must have one root")
        root=next(iter(roots))+"/"
        for member in members:
            if member.name==root[:-1]: continue
            if not member.name.startswith(root): raise ValueError("Unexpected root")
            member.name=member.name[len(root):]
            target=(dest/member.name).resolve()
            if not target.is_relative_to(dest): raise ValueError("Archive path escape")
            if member.islnk():
                if not member.linkname.startswith(root): raise ValueError("Hard link root")
                member.linkname=member.linkname[len(root):]
            if member.issym() or member.islnk():
                link=(target.parent/member.linkname).resolve() if member.issym() else (dest/member.linkname).resolve()
                if not link.is_relative_to(dest): raise ValueError("Archive link escape")
            tar.extract(member,dest,filter="data")
def nested_pins(dest,url,commit):
    path=dest/".gitmodules"
    if not path.exists(): return []
    parts=repo_parts(url)
    if not parts: raise ValueError("Nested gitlinks require verified GitHub tree API")
    owner,repo=parts
    tree=json.loads(get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{commit}?recursive=1"))
    if tree.get("truncated"): raise ValueError("Nested tree API was truncated")
    pins={x["path"]:x["sha"] for x in tree["tree"] if x["mode"]=="160000"}
    parser=configparser.ConfigParser(); parser.read(path,encoding="utf-8")
    out=[]
    for section in parser.sections():
        p=parser[section]["path"]; origin=parser[section]["url"]
        if p not in pins: raise ValueError("Missing exact nested gitlink "+p)
        if origin.startswith("../"):
            origin="https://github.com/"+owner+"/"+origin[3:]
        out.append({"path":p,"gitUrl":origin,"commit":pins[p]})
    return out
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--stage",required=True); parser.add_argument("--cache",required=True); parser.add_argument("--jobs",type=int,default=4); args=parser.parse_args()
    stage=pathlib.Path(args.stage).resolve(); cache=pathlib.Path(args.cache).resolve()
    source=json.loads((stage/"station-r126-source-receipt.json").read_text())
    lock=json.loads((HERE/"recipe"/"dependencies.lock.json").read_text())
    if source["upstream"]!=lock["upstream"]: raise ValueError("Stage/lock mismatch")
    cache.mkdir(parents=True,exist_ok=True); records=[]
    def fetch(module,base=stage):
        dest=(base/module["path"]).resolve()
        if not dest.is_relative_to(stage): raise ValueError("Dependency target outside stage")
        recordfile=cache/(module["commit"]+".json"); archive=cache/(module["commit"]+".tar.gz")
        if archive.exists():
            data=archive.read_bytes()
            if not recordfile.exists() or json.loads(recordfile.read_text())["sha256"]!=sha256(data):
                raise ValueError("Cached archive has no matching receipt")
        else:
            resolved=archive_url(module["gitUrl"],module["commit"])
            try: data=get(resolved)
            except urllib.error.HTTPError:
                if module["gitUrl"]!="https://gitlab.com/bzip2/bzip2.git": raise
                # Public libarchive mirror contains the SAME immutable commit.
                # No newer release or substitute revision is accepted.
                commit=json.loads(get("https://api.github.com/repos/libarchive/bzip2/git/commits/"+module["commit"]))
                if commit["sha"]!=module["commit"]: raise ValueError("Bzip2 mirror commit mismatch")
                resolved="https://codeload.github.com/libarchive/bzip2/tar.gz/"+module["commit"]
                data=get(resolved)
            archive.write_bytes(data)
            recordfile.write_text(json.dumps({"commit":module["commit"],"gitUrl":module["gitUrl"],"archiveUrl":resolved,"sha256":sha256(data),"bytes":len(data)},indent=2)+"\n")
        marker=dest/"station-pinned-archive.json"
        if dest.exists() and any(dest.iterdir()):
            if not marker.exists() or json.loads(marker.read_text())["sha256"]!=sha256(data): raise ValueError("Nonempty dependency not owned by this recipe")
        else: unpack(data,dest)
        record={"path":str(dest.relative_to(stage)).replace("\\","/"),"commit":module["commit"],"gitUrl":module["gitUrl"],"archiveUrl":json.loads(recordfile.read_text()).get("archiveUrl",archive_url(module["gitUrl"],module["commit"])),"sha256":sha256(data),"bytes":len(data)}
        marker.write_text(json.dumps(record,indent=2)+"\n")
        children=nested_pins(dest,module["gitUrl"],module["commit"])
        nested=[]
        for child in children: nested.extend(fetch(child,dest))
        print(json.dumps({"dependency":record["path"],"commit":record["commit"],"bytes":record["bytes"],"nested":len(children)}),flush=True)
        return [record]+nested
    modules=[m for m in lock["modules"] if m["android"]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.jobs,8))) as pool:
        futures=[pool.submit(fetch,m) for m in modules]
        failures=[]
        for future in futures:
            try: records.extend(future.result())
            except Exception as e: failures.append(type(e).__name__+": "+str(e))
    receipt={"upstream":lock["upstream"],"topLevelRequired":len(modules),"archives":sorted(records,key=lambda x:x["path"]),"failures":failures,"complete":not failures,"cloneModified":False}
    (stage/"station-r126-dependency-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    (HERE/"evidence"/"dependencies-r126.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"archives":len(records),"complete":not failures,"failures":failures}),flush=True)
    if failures: raise SystemExit(1)
if __name__=="__main__": main()
