from pathlib import Path
import difflib
import hashlib
import json
import os
import shutil
import subprocess

ROOT=Path(__file__).resolve().parent
BUILD=Path(os.environ.get("STATION_FRONTEND_BUILD",str(ROOT/"build")))
EVIDENCE=Path(os.environ.get("STATION_FRONTEND_EVIDENCE",str(ROOT/"evidence")))
TEMP=BUILD/"temp"
BASE_SO=Path(os.environ["STATION_BASE_FRONTEND_SO"])
BASELINE=ROOT/"baseline/station_frontend.r112.cpp"
BASELINE_ABI=ROOT/"baseline/station_catalog_abi.r112.hpp"
BASELINE_SOURCE_SHA="5f77d82d902dbe17bcba7870cd12e61b3bd44000caa395be4fede783512768bc"
BASELINE_SO_SHA="ce2282dd627783011648ee67bdb1f2998c28edd9b96d5f2d917235621ef46958"
UNCHANGED_HEADERS={
 "station_collections.hpp":"a6e07c629355d34ae1ce4bdabf46654a2fed3ad4fde33b45fbfe5c9043e9647f",
 "station_cover_plan.hpp":"5255664c4d04c943efc33c96ff7c9056b8a38f5536fb717f2bcfcf5b1526ac19",
 "station_cover_publication.hpp":"0de61431fc7bbff10d446bf9a0cee36a9953d3fb57344ff61fe10b2b2d711c52",
 "station_cover_retry.hpp":"c8384ba7c61e3fa091d099e1a2c3148f509fdc5927a11976530c9f50eebaf2cf",
 "station_profile_bridge.h":"093212f9266d9c8c648268123a2099b946fdc6dac61b64cedf1b18a1f55a4447",
 "station_profile_state.hpp":"4691220d78ab1f103276771aa658dd5c2573dbc8ce79646c368436860ff375d5",
 "station_synopsis_pages.hpp":"db770934587c73a627d0c333249d7e6cd93c11b4e98abda8cf524dc77b7194e0",
 "station_transfer_rate.hpp":"cf37bcdd37e0ff6abeeeff2116847e064fe8d66d546bfc4ae4917818ffd9272f",
}
NDK=Path(r"E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin")
HOST=Path(r"C:\Program Files\LLVM\bin")

def sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(args,label,cwd=ROOT):
 args=list(map(str,args));commands.append(args)
 result=subprocess.run(args,cwd=cwd,env=environment,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 outputs.append(f"[{label}]\n"+result.stdout)
 print(result.stdout,end="",flush=True)
 if result.returncode:raise RuntimeError(f"{label} failed ({result.returncode})")
 return result.stdout

def compile_android(source,destination):
 run([NDK/"clang++.exe","--target=aarch64-linux-android26","-std=c++17","-shared","-fPIC","-O2",
      "-Wl,-z,max-page-size=16384","-Wl,--no-undefined","-fvisibility=hidden","-Wall","-Wextra","-Werror",
      "-Wno-return-type-c-linkage","-static-libstdc++","-Wl,--exclude-libs,ALL","-I",ROOT,source,"-ldl","-llog","-o",destination],destination.stem)

def symbol_names(path):
 output=run([NDK/"llvm-nm.exe","--defined-only","--dynamic",path],path.stem+"-symbols")
 return {line.split()[-1] for line in output.splitlines() if line.split()}

BUILD.mkdir(parents=True,exist_ok=True);EVIDENCE.mkdir(parents=True,exist_ok=True);TEMP.mkdir(parents=True,exist_ok=True)
environment=dict(os.environ,TEMP=str(TEMP),TMP=str(TEMP));commands=[];outputs=[]

assert sha(BASE_SO)==BASELINE_SO_SHA,"R112 frontend binary mismatch"
assert sha(BASELINE)==BASELINE_SOURCE_SHA,"R112 reproducible source mismatch"
assert sha(BASELINE_ABI)=="16c65f6c7bba9eecec4c914490bd552978735be3d2da3c732d5f5c8486639824"
for filename,digest in UNCHANGED_HEADERS.items():assert sha(ROOT/filename)==digest,filename
baseline_abi=BASELINE_ABI.read_text(encoding="utf-8")
expected_abi=baseline_abi.replace(
 "// Read-only renderer contract recovered from libmain a1ae357d. No network URLs are stored.\n",
 "// Read-only renderer contract recovered from libmain a1ae357d. No network URLs are stored.\n"
 "// R113 extends only the bounded JNI row tail (revision, optional private cover path).\n"
 "// Item and Catalog remain byte-for-byte ABI compatible with the retained renderer.\n",1)
assert (ROOT/"station_catalog_abi.hpp").read_text(encoding="utf-8")==expected_abi,"Native Item ABI changed"

run([HOST/"clang.exe","-x","c","-std=c11","-Wall","-Wextra","-Werror","-fsyntax-only",ROOT/"tests/bridge_header_c_test.c"],"bridge-header-c")
run([HOST/"clang++.exe","-std=c++17","-O2","-Wall","-Wextra","-Werror",ROOT/"tests/profile_name_test.cpp","-o",BUILD/"profile_name_test.exe"],"profile-test-compile")
profile_output=run([BUILD/"profile_name_test.exe"],"profile-test-run").strip()
run([HOST/"clang++.exe","-std=c++17","-O2","-Wall","-Wextra","-Werror","-I",ROOT,ROOT/"tests/warm_cover_test.cpp","-o",BUILD/"warm_cover_test.exe"],"warm-test-compile")
warm_output=run([BUILD/"warm_cover_test.exe"],"warm-test-run").strip()
assert profile_output.startswith("PASS ") and warm_output=="PASS 23 native warm-cover checks"

# Compile the authoritative R102/R112 source under its original basename. The
# exact ce2282 result proves that all retained headers and compiler flags match.
baseline_dir=BUILD/"baseline-source";baseline_dir.mkdir(exist_ok=True)
baseline_named=baseline_dir/"station_frontend.cpp";shutil.copyfile(BASELINE,baseline_named)
baseline_built=BUILD/"libstation_frontend-r112-baseline.so";compile_android(baseline_named,baseline_built)
assert sha(baseline_built)==BASELINE_SO_SHA,"R112 native baseline is not byte reproducible"

current_built=BUILD/"libstation_frontend.so";compile_android(ROOT/"station_frontend.cpp",current_built)
base_symbols=symbol_names(BASE_SO);current_symbols=symbol_names(current_built)
assert current_symbols==base_symbols,"R113 changed the exported native ABI"
elf=run([NDK/"llvm-readelf.exe","-lW",current_built],"readelf")
loads=[line.split() for line in elf.splitlines() if line.strip().startswith("LOAD")]
assert loads and all(row[-1]=="0x4000" for row in loads),"16KiB LOAD alignment"

baseline_text=BASELINE.read_text(encoding="utf-8").splitlines(keepends=True)
current_text=(ROOT/"station_frontend.cpp").read_text(encoding="utf-8").splitlines(keepends=True)
native_diff="".join(difflib.unified_diff(baseline_text,current_text,fromfile="R112/station_frontend.cpp",tofile="R113/station_frontend.cpp"))
assert "preservedCovers" in native_diff and "parseNativeCatalogRow" in native_diff and "station_cover_warmstart.hpp" in native_diff
(EVIDENCE/"r112-to-r113-native.diff").write_text(native_diff,encoding="utf-8")

tracked=[ROOT/"station_frontend.cpp",ROOT/"station_catalog_abi.hpp",ROOT/"station_catalog_row.hpp",ROOT/"station_cover_warmstart.hpp",
         ROOT/"tests/warm_cover_test.cpp",ROOT/"tests/profile_name_test.cpp",ROOT/"tests/bridge_header_c_test.c",current_built,baseline_built]
files={str(path.relative_to(ROOT)).replace("\\","/") if path.is_relative_to(ROOT) else path.name:{"bytes":path.stat().st_size,"sha256":sha(path)} for path in tracked}
receipt={
 "version":"R113-candidate","sourceBase":"R112 / reproducible R102 frontend source","baseFrontendSO":BASELINE_SO_SHA,
 "baselineSourceSHA256":BASELINE_SOURCE_SHA,"baselineRecompiledSHA256":sha(baseline_built),"r113FrontendSHA256":sha(current_built),
 "profileTest":profile_output,"warmCoverParserAndRefreshTest":warm_output,"exportsExactlyPreserved":True,
 "exportCount":len(current_symbols),"itemAbiBytes":232,"coverPathOffset":200,"coverReadyOffset":225,
 "maximumPageSize":16384,"target":"aarch64-linux-android26","files":files,"commands":commands,
 "apkPackaged":False,"installed":False,"serverChanged":False,
}
(EVIDENCE/"compiled-warmstart.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
(EVIDENCE/"build.log").write_text("".join(outputs),encoding="utf-8")
print("PASS exact R112 baseline, real row ABI fixtures, preserved exports, 16KiB alignment")
print(json.dumps({"sha256":sha(current_built),"bytes":current_built.stat().st_size}))
