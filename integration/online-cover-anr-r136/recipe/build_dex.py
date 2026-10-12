"""Rebuild R136 classes35.dex from exact R135 without touching other classes."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DONOR_APK = "f6abe89490e7ba5e2cdd432625888bed6f40aea115d730cf612d509ec6ca9896"
DONOR_DEX = "a7a66724f26c06075ec1833e11866a073f93ee056aeabf58301cab016f96a4f5"
OUTPUT_DEX = "84b8aa3935a8e84eb69f8f7cc45885ac693e38bf1f26cfb07b811d3df60b8c05"
PARTITION = "classes35.dex"
OWNER = "org/emulationstation/frontend/netplay/StationOnlineCoverView"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True, timeout=300)
    require(result.returncode == 0, "Scoped DEX stage failed: " + str(args[-1]) + "\n" + result.stderr[-1200:])
    return result.stdout.strip()


def projection(root):
    return {"L" + path.relative_to(root).as_posix()[:-6] + ";": sha(path)
            for path in root.rglob("*.smali")}


def build(args):
    require(not args.out.exists(), "Output directory already exists")
    require(sha(args.base) == DONOR_APK, "Exact signed R135 APK required")
    with zipfile.ZipFile(args.base) as archive:
        require(hashlib.sha256(archive.read(PARTITION)).hexdigest() == DONOR_DEX,
                "R135 classes35.dex changed")
    args.out.mkdir(parents=True)
    tools = args.out / "tools"
    tools.mkdir()
    java = args.jdk / "bin/java.exe"
    javac = args.jdk / "bin/javac.exe"
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", args.apktool,
         "-d", tools, *(HERE / name for name in
                         ("DecodeDolphinPartition.java", "VerifyScopedPartition.java",
                          "AssembleScopedPartition.java"))])
    cp = str(tools) + ";" + str(args.apktool)
    donor = args.out / "donor-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", args.base, PARTITION, DONOR_DEX, donor])
    before = projection(donor)
    require(len(before) == 608, "R135 class count changed")
    owner = "L" + OWNER + ";"
    allowed = sorted(t for t in before if t == owner or t.startswith(owner[:-1] + "$"))
    require(len(allowed) == 17, "Cover owner family changed")
    working = args.out / "working-smali"
    run([sys.executable, "-B", HERE / "patch_cover.py", donor, working])
    changed = sorted(t for t, digest in projection(working).items() if before[t] != digest)
    require(changed == [owner], "Only StationOnlineCoverView may change")
    scope = args.out / "scope.properties"
    fields = ["schema=station.online-cover-static-g52.scoped-types.r136.v1",
              "partition=" + PARTITION, "donorSha256=" + DONOR_DEX,
              "families=" + owner, "originalAllowed=" + "|".join(allowed),
              "finalAllowed=" + "|".join(allowed)]
    scope.write_text("\n".join(fields) + "\n", encoding="utf-8")
    checked = run([java, "-cp", cp, "VerifyScopedPartition", args.base, PARTITION,
                   DONOR_DEX, working, scope])
    require("verifiedClasses=608 finalClasses=608 unchanged=591" in checked,
            "Unrelated class projection was not verified")
    output = args.out / PARTITION
    assembled = run([java, "-cp", cp, "AssembleScopedPartition", args.base, PARTITION,
                     DONOR_DEX, working, output, scope])
    require("assembledClasses=608 restoredInitializerArrays=1" in assembled,
            "Scoped DEX assembly proof missing")
    require(sha(output) == OUTPUT_DEX, "Compiled DEX differs from reviewed R136")
    container = args.out / "container.zip"
    with zipfile.ZipFile(container, "w", zipfile.ZIP_STORED) as archive:
        archive.write(output, PARTITION)
    final = args.out / "final-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", container, PARTITION, OUTPUT_DEX, final])
    after = projection(final)
    require(set(after) == set(before) and sorted(t for t in before if before[t] != after[t]) == [owner],
            "Assembled DEX changed another class")
    require(run([java, "-cp", cp, "VerifyScopedPartition", args.base, PARTITION,
                 DONOR_DEX, final, scope]) == checked, "Postassembly class verification differs")
    receipt = dict(schema="station.online-cover-anr.dex.r136.v1", donorApkSha256=DONOR_APK,
                   donorDexSha256=DONOR_DEX, outputDexSha256=OUTPUT_DEX,
                   originalClassCount=608, finalClassCount=608, unchangedClasses=607,
                   modifiedClasses=[owner], addedClasses=[], removedClasses=[],
                   scopeFamilyTypes=allowed, staticInitializerArraysRestored=1,
                   compiledPayloadOnly=True, signed=False, installed=False)
    (args.out / "dex-compilation.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("base", "jdk", "apktool", "out"):
        p.add_argument("--" + field, type=Path, required=True)
    result = build(p.parse_args())
    print(json.dumps({"outputDexSha256": result["outputDexSha256"],
                      "unchangedClasses": result["unchangedClasses"]}))
