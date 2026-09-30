"""Stage the counter bridge into an explicitly supplied decoded APK tree.

This script is a proposal and has not been run against the active project.
All output goes to the caller's decoded tree (normally on E:). It modifies
only the relocated SharedCounter Factory and adds one native library.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("decoded", type=Path)
parser.add_argument("--ndk", type=Path, default=Path(r"E:\TurboEdenEngine\android-ndk-r28c"))
args = parser.parse_args()
root = args.decoded.resolve(strict=True)
source = Path(__file__).with_name("wiiu_counter_jni.c")
matches = list(root.glob("smali*/twiiucor/datastore/core/SharedCounter$Factory.smali"))
if len(matches) != 1:
    raise SystemExit(f"Expected exactly one WiiU SharedCounter Factory, got {len(matches)}")
factory = matches[0]
text = factory.read_text(encoding="utf-8")
anchor = '    const-string v0, "wiiustore_shared_counter"'
if text.count(anchor) != 1:
    raise SystemExit("Expected exactly one donor load statement")
load_call = "    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V"
start = text.index(anchor)
end = text.index(load_call, start) + len(load_call)
new_load = ('\n\n    const-string v0, "turbo_wiiu_counter_jni"\n'
            + load_call)
if '"turbo_wiiu_counter_jni"' in text:
    raise SystemExit("Bridge load already present; refusing double patch")
native_class = factory.with_name("NativeSharedCounter.smali").read_text(encoding="utf-8")
expected = {
    "nativeCreateSharedCounter(I)J",
    "nativeGetCounterValue(J)I",
    "nativeIncrementAndGetCounterValue(J)I",
    "nativeTruncateFile(I)I",
}
assert all("native " + item in native_class for item in expected)
libdir = root / "lib" / "arm64-v8a"
donor = libdir / "libwiiustore_shared_counter.so"
assert donor.is_file(), donor
donor_hash = hashlib.sha256(donor.read_bytes()).hexdigest()
binpath = args.ndk / "toolchains/llvm/prebuilt/windows-x86_64/bin"
sysroot = binpath.parent / "sysroot"
symbols = subprocess.check_output([str(binpath / "llvm-readelf.exe"), "--dyn-syms", str(donor)], text=True)
for method in expected:
    assert "Java_androidx_datastore_core_NativeSharedCounter_" + method.split("(")[0] in symbols
output = libdir / "libturbo_wiiu_counter_jni.so"
if output.exists():
    raise SystemExit("Bridge library already exists; refusing overwrite")
cmd = [str(binpath / "clang.exe"), "--target=aarch64-linux-android26",
       "--sysroot=" + str(sysroot), "-shared", "-fPIC", "-O2",
       "-fvisibility=hidden", "-Werror", "-Wall", "-Wextra",
       "-Wl,--no-undefined", "-Wl,-z,relro", "-Wl,-z,now",
       "-Wl,-z,max-page-size=16384", "-Wl,-soname,libturbo_wiiu_counter_jni.so",
       str(source), "-o", str(output), "-ldl", "-llog"]
subprocess.run(cmd, check=True)
factory.write_text(text[:end] + new_load + text[end:], encoding="utf-8")
assert hashlib.sha256(donor.read_bytes()).hexdigest() == donor_hash
print(json.dumps({"factory": str(factory), "added_library": str(output),
                  "donor_unchanged_sha256": donor_hash,
                  "bridge_sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))
