"""Compile only new Sony hosts; preserve every R130 DEX and resource unchanged."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d227b0af17600bf99ec097857bf182f6e7989f8ddc3b68b63e17c81f69eb30ad"
BRIDGE_JAR_SHA = "8a4d6b2f0ae2da3bbe3252d8b5de3aaa2fa249168f2ed006605875e38ae6ef10"

def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def source_map():
    result = {}
    for directory in ("java", "composition/java", "ps3/java", "ps4/java"):
        for path in sorted((ROOT/directory).rglob("*.java")):
            name = path.relative_to(ROOT).as_posix()
            if name in result:
                raise ValueError("Duplicated host source")
            result[name] = path
    return result

def dex_types(raw):
    if not raw.startswith(b"dex\n") or len(raw) < 112:
        raise ValueError("Invalid DEX")
    def u32(offset):
        return struct.unpack_from("<I", raw, offset)[0]
    def text(index):
        offset = u32(u32(60)+index*4)
        while raw[offset] & 128:
            offset += 1
        offset += 1
        return raw[offset:raw.index(0, offset)].decode("ascii")
    types = [text(u32(u32(68)+i*4)) for i in range(u32(64))]
    return {types[u32(u32(100)+i*32)] for i in range(u32(96))}

def run(command, output, label):
    result = subprocess.run(list(map(str, command)), capture_output=True, encoding="utf-8", errors="replace")
    (output/(label+".log")).write_text(result.stdout+result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(label+" failed; inspect private diagnostics")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "assets-receipt", "bridge-jar", "jdk", "android-jar", "d8-jar", "out"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    if sha(args.base) != BASE_SHA:
        raise ValueError("Exact installed R130 base required")
    if sha(args.bridge_jar) != BRIDGE_JAR_SHA:
        raise ValueError("Exact R130 compile-only bridge classpath required")
    if args.out.exists():
        raise ValueError("Do not overwrite a compiled owner")
    assets = json.loads(args.assets_receipt.read_text(encoding="utf-8"))
    if assets.get("passed") is not True:
        raise ValueError("Prepared and pinned Sony assets required")
    generated = Path(assets["generatedSource"]["path"])
    if sha(generated) != assets["generatedSource"]["sha256"]:
        raise ValueError("Generated module pins changed")
    for name, row in assets["payloads"].items():
        path = Path(row["path"])
        if not name.startswith("assets/sony/") or path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise ValueError("Private Sony artifact changed")
    sources = source_map()
    pins = {name: sha(path) for name, path in sources.items()}
    classes = args.out/"classes"
    dex = args.out/"dex"
    classes.mkdir(parents=True)
    dex.mkdir()
    dependencies = [args.android_jar, args.bridge_jar]
    run([args.jdk/"bin/javac.exe", "-encoding", "UTF-8", "--release", "8", "-proc:none",
        "-cp", os.pathsep.join(map(str, dependencies)), "-d", classes, *sources.values(), generated], args.out, "javac")
    jar = args.out/"sony-host.jar"
    with zipfile.ZipFile(jar, "w", zipfile.ZIP_STORED) as archive:
        for path in sorted(classes.rglob("*.class")):
            archive.writestr(zipfile.ZipInfo(path.relative_to(classes).as_posix(), (1980,1,1,0,0,0)), path.read_bytes())
    run([args.jdk/"bin/java.exe", "-cp", args.d8_jar, "com.android.tools.r8.D8",
        "--release", "--min-api", "28", "--lib", args.android_jar,
        "--classpath", args.bridge_jar, "--output", dex, jar], args.out, "d8")
    if list(dex.glob("*.dex")) != [dex/"classes.dex"]:
        raise ValueError("Only one new DEX partition is permitted")
    new_types = dex_types((dex/"classes.dex").read_bytes())
    if not new_types or any(not name.startswith(("Lorg/emulationstation/frontend/sony/", "Laenu/")) for name in new_types):
        raise ValueError("A foreign dependency was packaged in the host DEX")
    preserved = {}
    with zipfile.ZipFile(args.base) as archive:
        for i in range(1,40):
            name = "classes.dex" if i == 1 else "classes"+str(i)+".dex"
            raw = archive.read(name)
            if new_types & dex_types(raw):
                raise ValueError("An existing Station class was shadowed")
            preserved[name] = hashlib.sha256(raw).hexdigest()
    if pins != {name: sha(path) for name, path in source_map().items()}:
        raise ValueError("Sources changed during compilation")
    result = args.out/"classes40.dex"
    result.write_bytes((dex/"classes.dex").read_bytes())
    receipt = {"schema": "station.sony.internal.host.v1", "passed": True,
        "baseApkSha256": BASE_SHA, "sourceSha256": pins,
        "assetReceiptSha256": sha(args.assets_receipt), "generatedSourceSha256": sha(generated),
        "compileOnlyClasspathSha256": {"bridge.jar": sha(args.bridge_jar), "android.jar": sha(args.android_jar)},
        "compileOnlyClassesPackaged": False, "newTypes": sorted(new_types),
        "preservedDexSha256": preserved, "payload": {"name": "classes40.dex", "path": str(result),
            "bytes": result.stat().st_size, "sha256": sha(result)},
        "androidBootstrapOrGameplayValidated": False}
    (args.out/"host-compilation.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"compiled": True, "addedTypes": len(new_types), "existingDexUnmodified": 39}))

if __name__ == "__main__":
    main()
