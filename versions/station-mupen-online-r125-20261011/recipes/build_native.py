"""Build the full Station Mupen arm64 core from the pinned AE Android.mk inputs.

No offline library or source is overwritten; no archived objects are reused.
Compiler arguments reproduce the AE Windows NDK release C flags and arm64
source list. Paths with spaces work because subprocess receives argument lists.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

VERSION = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("native_patch", VERSION / "native/apply_native_patch.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
SONAME = "libstation_mupen64plus_core.so"
ALLOWED = Path(r"G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\r125-native-artifacts")

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def build(upstream: Path, ndk: Path, out: Path, jobs: int) -> dict:
    upstream, ndk, out = upstream.resolve(), ndk.resolve(), out.resolve()
    allowed = ALLOWED.resolve()
    if out != allowed and allowed not in out.parents:
        raise ValueError("Output must stay within the approved R125 native artifacts directory")
    if out.exists() and any(out.iterdir()):
        raise ValueError("Use an empty build directory; do not mix archived objects")
    original = {name: sha(upstream / name) for name in patch.PINS}
    overlay = patch.generate(upstream)  # all upstream pins checked before writes
    tool = ndk / "toolchains/llvm/prebuilt/windows-x86_64/bin"
    clang, readelf, strip = tool / "clang.exe", tool / "llvm-readelf.exe", tool / "llvm-strip.exe"
    for path in (clang, readelf, strip):
        if not path.is_file(): raise FileNotFoundError(path)
    dependencies = ("libpng.a", "libSDL2_net.so")
    prebuilt = upstream / "ndkLibs/libs/release/arm64-v8a"
    for name in dependencies:
        if not (prebuilt / name).is_file(): raise FileNotFoundError(prebuilt / name)
    out.mkdir(parents=True, exist_ok=True)
    source = out / "source"
    core = source / "mupen64plus-core"
    shutil.copytree(upstream / "mupen64plus-core/upstream", core / "upstream")
    for name in ("mupen64plus-core.mk", "Android.mk", "Application.mk"):
        shutil.copy2(upstream / "mupen64plus-core" / name, core / name)
    shutil.copytree(upstream / "build_common", source / "build_common")
    for name in ("SDL2_stub", "SDL_net/include", "png"):
        shutil.copytree(upstream / "ndkLibs" / name, source / "ndkLibs" / name)
    libs = out / "dependencies"; libs.mkdir()
    for name in dependencies: shutil.copy2(prebuilt / name, libs / name)
    for name, raw in overlay.items():
        path = source / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    module = core / "mupen64plus-core.mk"
    module.write_text(module.read_text().replace("LOCAL_MODULE := mupen64plus-core", "LOCAL_MODULE := station_mupen64plus_core"), newline="\n")
    src = core / "upstream/src"
    asm = src / "asm_defines/arm64-v8a"; asm.mkdir(parents=True, exist_ok=True)
    objects = out / "objects"; objects.mkdir()
    commands: list[list[str]] = []
    def run(args: list[str], log_name: str) -> str:
        commands.append(args)
        result = subprocess.run(args, capture_output=True, text=True)
        (out / log_name).write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode: raise RuntimeError(f"Native command failed ({result.returncode}); see {out / log_name}")
        return result.stdout
    flags = ["--target=aarch64-linux-android23", "-Oz", "-fcommon", "-ffast-math", "-ftree-vectorize",
        "-fno-omit-frame-pointer", "-fvisibility=hidden", "-Wno-error=implicit-function-declaration",
        "-DANDROID", "-DIOAPI_NO_64", "-DNOCRYPT", "-DNOUNCRYPT", "-DM64P_NETPLAY=1",
        "-DWITHOUT_SDL=1", "-DUSE_GLES=1", "-DDYNAREC", "-DNEW_DYNAREC=4",
        "-fPIC", "-ffunction-sections", "-fdata-sections", "-fstack-protector-strong", "-DNDEBUG"]
    include_dirs = [core / "upstream/subprojects/md5", core / "upstream/subprojects/minizip",
        core / "upstream/subprojects/xxhash", src, src / "main", asm,
        source / "ndkLibs/SDL2_stub", source / "ndkLibs/SDL_net/include", source / "ndkLibs/png"]
    includes = [arg for path in include_dirs for arg in ("-I", str(path))]
    run([str(clang), *flags, "-fno-lto", *includes, "-c", str(src / "asm_defines/asm_defines.c"),
         "-o", str(asm / "asm_defines.o")], "asm-compile.log")
    defines = re.findall(rb"@ASM_DEFINE (offsetof_struct_[a-zA-Z_0-9]+) (0x[0-9a-fA-F]+)", (asm / "asm_defines.o").read_bytes())
    if len(defines) < 20: raise RuntimeError("Incomplete assembly offsets from actual compiled structs")
    # Same records/output as upstream gen_asm_defines.awk, avoiding shell/path ambiguity.
    (asm / "asm_defines_gas.h").write_text("".join(f"#define {a.decode()} ({b.decode()})\n" for a, b in defines))
    (asm / "asm_defines_nasm.h").write_text("".join(f"%define {a.decode()} ({b.decode()})\n" for a, b in defines))
    make = module.read_text()
    block = make.split("LOCAL_SRC_FILES :=", 1)[1].split("LOCAL_CFLAGS :=", 1)[0]
    entries = re.findall(r"^\s*\$\((SRCDIR|SUBLIBS)\)/([A-Za-z0-9_./-]+)", block, re.MULTILINE)
    sources = [(src if base == "SRCDIR" else core / "upstream/subprojects") / path for base, path in entries]
    sources.append(src / "device/r4300/new_dynarec/arm64/linkage_arm64.S")
    if len(sources) < 70 or len(set(sources)) != len(sources):
        raise RuntimeError("Unexpected AE Android.mk source list")
    for required in (src / "main/netplay.c", src / "main/n64-station-recovery.c", src / "main/main.c"):
        if required not in sources: raise RuntimeError("Missing required build source: " + str(required))
    for path in sources:
        if not path.is_file(): raise FileNotFoundError(path)
    def compile_one(entry: tuple[int, Path]) -> Path:
        index, path = entry
        obj = objects / f"{index:03d}-{path.stem}.o"
        run([str(clang), *flags, *includes, "-c", str(path), "-o", str(obj)], f"compile-{index:03d}.log")
        return obj
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        compiled = list(pool.map(compile_one, enumerate(sources)))
    unstripped = out / (SONAME + ".unstripped")
    link = [str(clang), "--target=aarch64-linux-android23", "-shared", "-o", str(unstripped),
        *map(str, compiled), str(libs / "libpng.a"), "-L", str(libs), "-lSDL2_net", "-lz", "-lm", "-ldl",
        "-Wl,-Bsymbolic", "-Wl,-export-dynamic", "-Wl,--gc-sections", "-Wl,--no-undefined",
        f"-Wl,-soname,{SONAME}", f"-Wl,-version-script,{src / 'api/api_export.ver'}",
        "-Wl,-z,max-page-size=16384", "-Wl,-z,common-page-size=16384", "-Wl,-z,relro", "-Wl,-z,now"]
    run(link, "link.log")
    final = out / SONAME
    run([str(strip), "--strip-unneeded", str(unstripped), "-o", str(final)], "strip.log")
    elf = run([str(readelf), "-h", "-l", "-d", "--dyn-syms", "--wide", str(final)], "elf-validation.txt")
    if "AArch64" not in elf or f"Library soname: [{SONAME}]" not in elf: raise RuntimeError("Wrong ELF identity")
    symbols = ("StationMupenConfigure", "StationMupenControl", "StationMupenStatus", "StationMupenStalled", "StationMupenRequestQuit", "CoreDoCommand", "CoreStartup", "CoreShutdown")
    for symbol in symbols:
        if not re.search(r"\bGLOBAL\s+DEFAULT\s+(?!UND)\S+\s+" + symbol + r"\b", elf):
            raise RuntimeError(f"Missing exported defined symbol: {symbol}")
    loads = [line for line in elf.splitlines() if re.match(r"\s*LOAD\s", line)]
    if not loads or any(int(line.split()[-1], 16) < 16384 for line in loads):
        raise RuntimeError("ELF load alignment below 16KiB")
    for name, before in original.items():
        if sha(upstream / name) != before: raise RuntimeError("Original source changed: " + name)
    receipt = {"soname": SONAME, "abi": "arm64-v8a", "api": 23, "compiledSourceCount": len(sources),
        "assemblyOffsetCount": len(defines), "reusedObjectCount": 0, "sources": {str(p.relative_to(source)): sha(p) for p in sources},
        "inputHeadersAndSources": {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob("*")) if p.is_file() and p.suffix in (".h", ".c", ".cpp", ".S", ".mk", ".ver")},
        "dependencies": {p.name: sha(p) for p in libs.iterdir()}, "upstreamPins": original,
        "sha256": sha(final), "bytes": final.stat().st_size, "exports": list(symbols),
        "loadAlignment": 16384, "offlineSourceUnchanged": True, "offlineLibraryReplaced": False,
        "compileSeconds": round(time.monotonic() - started, 3), "gameplayValidated": False,
        "compiler": run([str(clang), "--version"], "compiler-version.txt"), "commands": commands}
    (out / "build-native.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {key: receipt[key] for key in ("sha256", "bytes", "compiledSourceCount", "soname", "loadAlignment", "compileSeconds", "gameplayValidated")}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--ndk", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    if args.jobs < 1 or args.jobs > 16: parser.error("jobs must be 1..16")
    print(json.dumps(build(args.upstream, args.ndk, args.out, args.jobs)))

if __name__ == "__main__": main()
