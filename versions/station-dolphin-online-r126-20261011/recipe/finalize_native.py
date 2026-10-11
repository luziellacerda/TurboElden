#!/usr/bin/env python3
"""Verify/copy uniquely named online libraries. Never packages an APK or changes offline libs."""
import argparse, hashlib, json, pathlib, re, shutil, subprocess
HERE=pathlib.Path(__file__).resolve().parent.parent
PIN="5102a0339c2177575378107b76541e47cc52122d"
NAMES=("libstation_dolphin_online.so","libstation_dolphin_hook.so","libstation_dolphin_hook_impl.so","libstation_dolphin_file_redirect_hook.so","libstation_dolphin_gsl_alloc_hook.so")
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(tool,*args): return subprocess.check_output([str(tool),*map(str,args)],text=True,encoding="utf-8",errors="replace")
def main():
    p=argparse.ArgumentParser(); p.add_argument("--stage",required=True); p.add_argument("--build",required=True); p.add_argument("--output",required=True); p.add_argument("--ndk",default=r"E:\TurboEdenEngine\android-ndk-r28c"); a=p.parse_args()
    stage=pathlib.Path(a.stage).resolve(); build=pathlib.Path(a.build).resolve(); out=pathlib.Path(a.output).resolve()
    if any(x.drive.upper()!="G:" for x in (stage,build,out)) or len({stage,build,out})!=3: raise ValueError("Use isolated G: stage/build/output directories")
    src=json.loads((stage/"station-r126-source-receipt.json").read_text()); deps=json.loads((stage/"station-r126-dependency-receipt.json").read_text()); hooks=json.loads((stage/"station-r126-hook-receipt.json").read_text())
    if src["upstream"]!=PIN or not deps["complete"]: raise ValueError("Wrong/incomplete source stage")
    for record in src["patchedFiles"]:
        if sha(stage/record["path"])!=record["patchedSha256"]: raise ValueError("Unrecorded source modification")
    for record in src["addedFiles"]:
        if sha(stage/record["path"])!=record["sha256"]: raise ValueError("Unrecorded native addition")
    for record in hooks["files"]:
        if sha(stage/record["path"])!=record["patchedSha256"]: raise ValueError("Unrecorded hook modification")
    cache=(build/"CMakeCache.txt").read_text()
    if not re.search(r"^ANDROID_ABI:(?:STRING|UNINITIALIZED)=arm64-v8a$",cache,re.M) or not re.search(r"^ANDROID_PLATFORM:(?:STRING|UNINITIALIZED)=android-24$",cache,re.M): raise ValueError("Final target must preserve API24/arm64")
    tools=pathlib.Path(a.ndk)/"toolchains"/"llvm"/"prebuilt"/"windows-x86_64"/"bin"
    readelf=tools/"llvm-readelf.exe"; strip=tools/"llvm-strip.exe"
    old=json.loads((out/"native-receipt.json").read_text()) if (out/"native-receipt.json").exists() else None
    if out.exists() and any(out.iterdir()):
        if not old: raise ValueError("Output directory must be new or carry its own prior receipt")
        for record in old["libraries"]:
            if sha(out/record["name"])!=record["sha256"]: raise ValueError("Do not overwrite modified output")
    out.mkdir(parents=True,exist_ok=True)
    records=[]; symbols=""; mainfile=None
    modified=max((stage/r["path"]).stat().st_mtime_ns for r in src["patchedFiles"]+src["addedFiles"])
    for name in NAMES:
        matches=list(build.rglob(name))
        if len(matches)!=1: raise ValueError("Missing/ambiguous final library: "+name)
        original=matches[0]; dest=out/name
        if name==NAMES[0] and original.stat().st_mtime_ns<modified: raise ValueError("Main library predates latest source; run the incremental build")
        shutil.copy2(original,dest); subprocess.check_call([str(strip),"--strip-unneeded",str(dest)])
        elf=run(readelf,"-h","-l","-d",dest)
        if "AArch64" not in elf or "DYN (Shared object file)" not in elf: raise ValueError("Wrong ELF architecture/type")
        aligns=re.findall(r"^\s*LOAD\s+.*\s+(0x[0-9a-f]+)\s*$",elf,re.M)
        if not aligns or any(int(x,16)<16384 for x in aligns): raise ValueError("Library lacks 16KiB load alignment")
        soname=re.search(r"Library soname: \[([^]]+)\]",elf)
        if not soname or soname.group(1)!=name: raise ValueError("Unexpected SONAME")
        needed=re.findall(r"Shared library: \[([^]]+)\]",elf)
        if any(x in needed for x in ("libdolp.so","libmain.so","libmain_hook.so","libhook_impl.so","libc++_shared.so")): raise ValueError("Old/conflicting native dependency")
        if name==NAMES[0]: symbols=run(readelf,"--dyn-syms","--wide",dest); mainfile=dest
        records.append({"name":name,"bytes":dest.stat().st_size,"sha256":sha(dest),"unstrippedSha256":sha(original),"soname":name,"needed":needed,"minLoadAlignment":min(int(x,16) for x in aligns)})
    expected=set(re.findall(r"Java_org_emulationstation_frontend_netplay_StationDolphinBridge_(native\w+)\(",(HERE/"native"/"StationDolphinBridge.cpp").read_text()))
    actual=set(re.findall(r"Java_org_emulationstation_frontend_netplay_StationDolphinBridge_(native\w+)\b",symbols))
    if expected!=actual or len(actual)!=21: raise ValueError("JNI export mismatch")
    required=("Java_org_dolphinemu_dolphinemu_NativeLibrary_RunNetPlay","Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeHost","Java_org_dolphinemu_dolphinemu_features_netplay_NetplaySession_nativeJoin")
    if not all(x in symbols for x in required): raise ValueError("Official Dolphin NetPlay exports absent")
    blob=mainfile.read_bytes()
    if (PIN+"-station-dpl1-r126").encode() not in blob or b"tdolphin/core/util/Pair" not in blob: raise ValueError("Pinned native revision/JNI relocation absent")
    if b"androidx/core/util/Pair" in blob: raise ValueError("Unrelocated Pair JNI")
    bundle=hashlib.sha256("".join(r["name"]+" "+r["sha256"]+"\n" for r in records).encode()).hexdigest()
    result={"upstream":PIN,"compiled":True,"androidApi":24,"abi":"arm64-v8a","ndk":"28.2.13676358 (r28c)","clang":"19.0.1","cmake":"4.4.2","sourceDateEpoch":1790576668,"sourcePatchSha256":src["patchSha256"],"hookPatchSha256":hooks["patchSha256"],"nativeSourceSha256":[r for r in src["addedFiles"]],"libraries":records,"nativeBundleSha256":bundle,"jniExports":sorted(actual),"officialNetplayExports":list(required),"allLoadSegments16KiB":True,"offlineLibraryReplaced":False,"gameplayVerified":False,"apkPackaged":False,"serverActivated":False}
    (out/"native-receipt.json").write_text(json.dumps(result,indent=2)+"\n")
    (HERE/"evidence"/"native-build-r126.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"compiled":True,"libraries":len(records),"jniExports":len(actual),"nativeBundleSha256":bundle,"bytes":sum(r["bytes"] for r in records),"gameplay":False}))
if __name__=="__main__": main()
