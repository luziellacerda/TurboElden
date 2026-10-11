"""Rebuild isolated PSX protocol probes and ARM64 objects; no APK or ROM."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess

def native(p): return Path("\\\\?\\"+str(p.resolve())) if os.name=="nt" else p

def sha(p): return hashlib.sha256(native(p).read_bytes()).hexdigest()

def run(cmd):
    r=subprocess.run([str(v) for v in cmd],capture_output=True,text=True)
    if r.returncode: raise RuntimeError("Command failed: "+r.stdout+r.stderr)
    return r.stdout+r.stderr

def main():
    root=Path(__file__).resolve().parent.parent
    args=argparse.ArgumentParser();args.add_argument("--out",type=Path,required=True)
    args.add_argument("--llvm",type=Path,default=Path(r"C:\Program Files\LLVM\bin"))
    args.add_argument("--ndk",type=Path,default=Path(r"E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64"))
    args.add_argument("--sdk",type=Path,default=Path(r"E:\ESTUDO APK\work\station-hud-lzgames-20261003\sdk\android-arm64"))
    a=args.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=True)
    originals=[root/"native"/name for name in ["StationPsxProtocol.cpp","StationPsxSha256.cpp","StationPsxProtocol.hpp"]]+[root/"tests/protocol_probe.cpp"]
    alias=out/"source-alias";alias.mkdir(exist_ok=True)
    for p in originals:(alias/p.name).write_bytes(native(p).read_bytes())
    sources=[alias/"StationPsxProtocol.cpp",alias/"StationPsxSha256.cpp"]
    probe=out/"protocol_probe.exe"
    host=[a.llvm/"clang++.exe","-std=c++20","-O2","-Wall","-Wextra","-Werror",*sources,alias/"protocol_probe.cpp","-o",probe]
    run(host);result=run([probe]).strip()
    if "result=passed;" not in result: raise RuntimeError("Probe success absent")
    commands=[list(map(str,host))];objects=[]
    for source in sources:
        obj=out/(source.stem+".o")
        cmd=[a.llvm/"clang++.exe","--target=aarch64-linux-android24","--sysroot="+str(a.ndk/"sysroot"),
             "-resource-dir="+str(a.ndk/"lib/clang/19"),"-nostdinc++","-isystem",a.sdk/"include/c++/v1",
             "-std=c++20","-fPIC","-O2","-Wall","-Wextra","-Werror","-c",source,"-o",obj]
        run(cmd);commands.append(list(map(str,cmd)));objects.append(obj)
    archive=out/"libstation_psx_protocol.a"
    cmd=[a.llvm/"llvm-ar.exe","rcs",archive,*objects];run(cmd);commands.append(list(map(str,cmd)))
    elf={}
    for obj in objects:
        header=run([a.ndk/"bin/llvm-readelf.exe","-h",obj])
        if "AArch64" not in header or "REL (" not in header: raise RuntimeError("Bad ELF architecture/type")
        elf[obj.name]=header.strip()
    receipt={"schema":1,"generatedUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "isolatedComponentOnly":True,"emulatorOrApkBuilt":False,"physicalGameplay":False,
      "target":"aarch64-linux-android24","wire":"PXL1","maxSlots":2,"standardPadMask":"0x3fff","candidateInputDelay":4,
      "sourceSha256":{p.name:sha(p) for p in originals},"compilerSha256":sha(a.llvm/"clang++.exe"),
      "compilerVersion":run([a.llvm/"clang++.exe","--version"]).splitlines()[0],
      "sdkLibcxxArchiveSha256":sha(a.sdk/"lib/libc++.a"),"sdkLibcxxModulesJsonSha256":sha(a.sdk/"lib/libc++.modules.json"),
      "hostProbe":{"result":result,"sha256":sha(probe),"bytes":probe.stat().st_size},
      "archive":{"path":str(archive),"sha256":sha(archive),"bytes":archive.stat().st_size},
      "objectSha256":{p.name:sha(p) for p in objects},"elfHeaders":elf,"commands":commands,
      "limits":["Synthetic owner tests do not execute original PSX core/SDL/JNI or two phones",
        "Static objects do not validate the linked owner shared library or Android alignment",
        "No server registry or signed production state asserted",
        "State size/SHA is checked but nested core decoder memory safety is unproven",
        "Lockstep is not rollback; pipeline4 throughput depends on actual network latency"]}
    (out/"protocol-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"result":result,"archive":receipt["archive"],"receipt":str(out/"protocol-receipt.json")},indent=2))
if __name__=="__main__": main()
