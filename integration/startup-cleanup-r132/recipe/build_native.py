"""Reproduce R131 UI binaries, then compile the two closed R132 overlays.

Only the two UI libraries are emitted. No shader, media, DEX, owner, profile,
emulator, key, game or server is modified. All outputs stay in a fresh directory.
"""
from pathlib import Path
import argparse
import hashlib
import re
import zipfile
from common import *

R124 = REPO / "versions/station-video-room-footer-r124-20261011"
GENERATED_SHA = "eb9a7e14bc50e7fac66fee14f9a98ef8b7f109860720c6564ab5da34dea7723b"
TOOL_PINS = {"clang++.exe": "1c7792ef6df195b6af5919071a9ca7850bcb850153f02bed9c7d642e266c4ff3",
             "llvm-nm.exe": "90236526ebb24c232e59ec573675e32a92190b3346cf3a342c8b0eb5ad0f8203",
             "llvm-readelf.exe": "2646e382d8b2559b5c4ae91e9a98e187ed9bd59f23936054d424049ef795ba5e"}


def generated_sources(directory):
    return {p.name: sha(p) for p in directory.iterdir()
            if p.is_file() and p.suffix in (".h", ".cpp")}

def symbols(bin_path, tool, work, label):
    return {line.split()[-1] for line in run([tool/"llvm-nm.exe", "--dynamic", "--defined-only", bin_path],work,label).splitlines() if len(line.split())>=3}

def aligned(bin_path, tool, work, label):
    output = run([tool/"llvm-readelf.exe", "-lW", bin_path], work, label)
    loads = re.findall(r"^\s*LOAD\s+.*\s(0x[0-9a-fA-F]+)\s*$", output, re.M)
    require(loads and all(int(v,16)>=16384 for v in loads), "Native LOAD alignment below 16 KiB")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base-apk","native-inputs","generated-native","media-inputs","ndk","out"):
        parser.add_argument("--"+name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    a=parser.parse_args()
    frozen=verify_source_commit(a.source_commit)
    require(a.base_apk.stat().st_size==BASE_BYTES and sha(a.base_apk)==BASE_SHA,"R131 APK differs")
    require(not a.out.exists(),"Choose a fresh build directory")
    inventory=read(R124/"CAROUSEL-INPUT-MANIFEST.json")
    resolved={}
    for name, checksum in inventory.items():
        public=R124/"native"/name
        path=public if public.is_file() else a.native_inputs/name
        require(path.is_file() and sha(path)==checksum,"Pinned native input changed: "+name)
        shadow=a.native_inputs/name
        require(not shadow.is_file() or sha(shadow)==checksum,"Private native shadow changed: "+name)
        resolved[name]=path
    frontend_inputs=read(R124/"FRONTEND-SOURCE-MANIFEST.json")
    for name,checksum in frontend_inputs.items():
        require(sha(R124/"frontend"/name)==checksum,"Pinned frontend input changed: "+name)
    media=read(a.media_inputs/"sony-media.json")
    media_pins={}
    for name,record in media["files"].items():
        require((a.media_inputs/name).stat().st_size==record["bytes"] and
                sha(a.media_inputs/name)==record["sha256"],"Sony media input changed: "+name)
        media_pins[name]=record["sha256"]
    generated=generated_sources(a.generated_native)
    require(generated.get("native_carousel.cpp")==GENERATED_SHA,"Current generated carousel changed")
    parent_receipt=a.generated_native.parent/"native-receipt.json"
    parent_receipt_sha=sha(parent_receipt)
    media_receipt_sha=sha(a.media_inputs/"sony-media.json")
    parent_native=read(parent_receipt)
    require(parent_native["sha256"]==CAROUSEL_SHA and parent_native["sonyMediaReceipt"]==media,
            "Current native/media receipt relationship changed")
    loop_pins=parent_native["primaryPlatformVideoLoopReceipt"]["headers"]
    require(all(generated.get(name)==checksum for name,checksum in loop_pins.items()),"Current loop header changed")
    require(generated.get("native_settings.h")==parent_native["sonySettingsMenuReceipt"]["patchedSha256"],"Current settings header changed")
    require(generated=={"native_carousel.cpp": GENERATED_SHA,
                        "native_settings.h": parent_native["sonySettingsMenuReceipt"]["patchedSha256"],
                        **loop_pins},"Unexpected generated native source/header")
    tool=a.ndk/"toolchains/llvm/prebuilt/windows-x86_64/bin"
    require(all(sha(tool/name)==checksum for name,checksum in TOOL_PINS.items()),"Pinned native compiler/tools changed")
    a.out.mkdir(parents=True)
    common=[tool/"clang++.exe","--target=aarch64-linux-android26","-std=c++17","-shared","-fPIC","-O2","-Wl,-z,max-page-size=16384","-Wl,--no-undefined"]
    carousel_flags=[*common,"-nostdlib","-fno-exceptions","-fno-rtti","-fno-stack-protector","-fno-builtin","-Wl,-soname,libturbo_carousel.so"]
    includes=["-I",a.generated_native,"-I",a.media_inputs/"include","-I",REPO/"integration/ps3-ps4-offline/native","-I",R124/"native/d0","-I",a.native_inputs/"d0","-I",a.native_inputs/"d2","-I",a.native_inputs/"d1"]
    objects=[resolved[n] for n in ("d1/video720_posters.o","d3/collection_previews.o","d4/lottie_frames.o")]+[a.media_inputs/n for n in media["extraObjects"]]
    tail=["-L",a.native_inputs/"d1","-lc","-ldl","-llog",resolved["d5/installed_art.o"]]
    last=[resolved[n] for n in ("d6/collection_previews.o","d7/collection_previews.o","d8/collection_previews.o")]
    baseline=a.out/"baseline-carousel.so"
    run(carousel_flags+includes+[a.generated_native/"native_carousel.cpp"]+objects+tail+["-o",baseline]+last,a.out,"baseline-carousel")
    require(sha(baseline)==CAROUSEL_SHA,"R131 carousel is not reproduced byte-for-byte")
    frontflags=[*common,"-fvisibility=hidden","-Wall","-Wextra","-Werror","-Wno-return-type-c-linkage","-static-libstdc++","-Wl,--exclude-libs,ALL","-I",R124/"frontend"]
    frontbase=a.out/"baseline-frontend.so"
    run(frontflags+[R124/"frontend/station_frontend.cpp","-ldl","-llog","-o",frontbase],a.out,"baseline-frontend")
    require(sha(frontbase)==FRONTEND_SHA,"R131 frontend is not reproduced byte-for-byte")
    with zipfile.ZipFile(a.base_apk) as apk:
        owner=apk.read("lib/arm64-v8a/libmain.so")
        require(hashlib.sha256(apk.read("lib/arm64-v8a/libturbo_carousel.so")).hexdigest()==CAROUSEL_SHA,"Base carousel differs")
        require(hashlib.sha256(apk.read("lib/arm64-v8a/libstation_frontend.so")).hexdigest()==FRONTEND_SHA,"Base frontend differs")
    synopsis=module(ROOT/"recipe/patch_sony_synopsis.py","sony_synopsis")
    d0=R124/"native/d0"
    cpp,headers,synopsis_receipt=synopsis.patch((a.generated_native/"native_carousel.cpp").read_bytes(),*( (d0/name).read_bytes() for name in ("native_info.h","native_folders.h","collection_presentation.h","system_infos.h") ))
    loading=module(ROOT/"recipe/patch_loading.py","loading")
    changes,loading_receipt=loading.patch(cpp,(R124/"frontend/station_frontend.cpp").read_bytes())
    loading_receipt["verifiedBindings"]=loading.verify_bindings(owner,resolved["d1/relocations.h"].read_bytes())
    overlay=a.out/"overlay"
    for name,raw in changes.items():
        p=overlay/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    for name,raw in headers.items(): (overlay/"native"/name).write_bytes(raw)
    carousel=a.out/"libturbo_carousel.so"
    frontend=a.out/"libstation_frontend.so"
    run(carousel_flags+["-I",overlay/"native"]+includes+[overlay/"native/native_carousel.cpp"]+objects+tail+["-o",carousel]+last,a.out,"r132-carousel")
    run(frontflags+[overlay/"frontend/station_frontend.cpp","-ldl","-llog","-o",frontend],a.out,"r132-frontend")
    require(symbols(carousel,tool,a.out,"carousel-exports")==symbols(baseline,tool,a.out,"baseline-carousel-exports"),"Carousel exports changed")
    fs=symbols(frontend,tool,a.out,"frontend-exports")
    bs=symbols(frontbase,tool,a.out,"baseline-frontend-exports")
    require(fs==bs|{"StationLoading_graphicsReady","StationLoading_stage"},"Frontend export scope changed")
    for name,path in (("carousel",carousel),("frontend",frontend)): aligned(path,tool,a.out,name+"-loads")
    require(frozen==source_map(),"R132 source changed during compile")
    require(all(sha(p)==inventory[n] for n,p in resolved.items()),"Frozen native input changed during compile")
    require(all(sha(R124/"frontend"/n)==h for n,h in frontend_inputs.items()),"Frozen frontend changed during compile")
    require(all(sha(a.media_inputs/n)==h for n,h in media_pins.items()),"Media changed during compile")
    require(generated_sources(a.generated_native)==generated and
            sha(parent_receipt)==parent_receipt_sha and sha(a.media_inputs/"sony-media.json")==media_receipt_sha,
            "Generated native source/header or parent/media receipt changed during compile")
    require(all(sha(tool/n)==h for n,h in TOOL_PINS.items()),"Native tools changed during compile")
    payloads={"lib/arm64-v8a/"+p.name:{"path":str(p.resolve()),"bytes":p.stat().st_size,"sha256":sha(p)} for p in (carousel,frontend)}
    receipt={"schema":"station.startup.cleanup.native.v1","revision":"R132","baseApkSha256":BASE_SHA,"sourceCommit":a.source_commit,"sourceSha256":frozen,"payloads":payloads,"baselineReproduced":{"carousel":True,"frontend":True},"approvedScopes":["shader-prewarm-loading-barrier","sony-platform-synopses"],"dexChanged":False,"transforms":{"loading":loading_receipt,"synopsis":synopsis_receipt},"inputSha256":inventory,"frontendInputSha256":frontend_inputs,"mediaInputSha256":media_pins,"generatedInputSha256":generated,"parentNativeReceiptSha256":parent_receipt_sha,"mediaReceiptSha256":media_receipt_sha,"toolSha256":dict(TOOL_PINS),"loadAlignmentBytes":16384,"apkProduced":False,"installed":False,"physicalValidation":False}
    write(a.out/"native-receipt.json",receipt)
    print(json.dumps({"compiled":True,"baselineReproduced":True,"payloads":payloads}))

if __name__=="__main__": main()
