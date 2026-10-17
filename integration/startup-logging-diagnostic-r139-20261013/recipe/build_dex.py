"""Compile only a new helper; insert two exact R139 methods and verify all other classes."""
from pathlib import Path
import argparse
import json
import os
import shutil
import sys
import zipfile

sys.dont_write_bytecode = True
from common import BASE, BASE_BYTES, DEX, ROOT, PARTITION, digest, sha, need, run, verify_commit, isolated, temporary_fields
import patch_logging

TOOLS = {
    "java": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "javac": "9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549",
    "android_jar": "6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad",
    "d8_jar": "305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5",
    "apktool": "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",
}
OWNER = "Lorg/emulationstation/frontend/netplay/StationStartupLogging;"
EXISTING = {"Lorg/emulationstation/frontend/netplay/" + n + ";" for n in patch_logging.PINS}


def projection(root):
    return {"L" + p.relative_to(root).as_posix()[:-6] + ";": sha(p) for p in root.rglob("*.smali")}


def container(path, name, raw):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(name, raw)


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R139 donor required")
    inputs = {"java": a.jdk_bin / "java.exe", "javac": a.jdk_bin / "javac.exe", "android_jar": a.android_jar, "d8_jar": a.d8_jar, "apktool": a.apktool}
    need({name: sha(path) for name, path in inputs.items()} == TOOLS, "Pinned diagnostic Java toolchain required")
    pins = verify_commit(a.source_commit)
    with zipfile.ZipFile(a.base) as archive:
        need(digest(archive.read(PARTITION)) == DEX, "Exact R139 DEX 35 required")
        need(len(archive.namelist()) == len(set(archive.namelist())) == 13860, "Donor ZIP entry set differs")
    if a.check_inputs_only:
        return dict(passed=True, compiled=False, sourceCommit=a.source_commit, sourceFiles=pins, **temporary_fields())
    out = isolated(a.out)
    out.mkdir(parents=True)
    tools, classes, overlay = out / "tools", out / "helper-classes", out / "helper-dex"
    for folder in (tools, classes, overlay):
        folder.mkdir()
    recipe = ROOT / "recipe"
    java, javac = inputs["java"], inputs["javac"]
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", a.apktool, "-d", tools, *[recipe / n for n in ("DecodeDolphinPartition.java", "VerifyScopedPartition.java", "AssembleScopedPartition.java")]])
    cp = os.pathsep.join(map(str, (tools, a.apktool)))
    source = ROOT / "java/org/emulationstation/frontend/netplay/StationStartupLogging.java"
    run([javac, "-encoding", "UTF-8", "-source", "8", "-target", "8", "-implicit:none", "-sourcepath", "", "-cp", a.android_jar, "-d", classes, source])
    outputs = list(classes.rglob("*.class"))
    need([p.relative_to(classes).as_posix() for p in outputs] == [OWNER[1:-1] + ".class"], "Only one productive Java helper may compile")
    jar = out / "helper.jar"
    container(jar, OWNER[1:-1] + ".class", outputs[0].read_bytes())
    run([java, "-cp", a.d8_jar, "com.android.tools.r8.D8", "--release", "--min-api", "28", "--lib", a.android_jar, "--output", overlay, jar])
    need(list(overlay.glob("*.dex")) == [overlay / "classes.dex"], "One helper DEX required")
    overlay_zip = out / "helper-container.zip"
    container(overlay_zip, "classes.dex", (overlay / "classes.dex").read_bytes())
    helper = out / "helper-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", overlay_zip, "classes.dex", sha(overlay / "classes.dex"), helper])
    need(set(projection(helper)) == {OWNER}, "D8 helper may not emit any other class")
    donor = out / "donor-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", a.base, PARTITION, DEX, donor])
    before = projection(donor)
    need(len(before) == 608 and OWNER not in before, "Exact donor class set required")
    working = out / "working-smali"
    shutil.copytree(donor, working)
    for name in patch_logging.PINS:
        target = working / (patch_logging.PACKAGE + name + ".smali")
        target.write_bytes(patch_logging.patch(name, target.read_bytes()))
    helper_path = OWNER[1:-1] + ".smali"
    shutil.copyfile(helper / helper_path, working / helper_path)
    method_proof = patch_logging.verify(donor, working)
    scope = out / "scope.properties"
    scope.write_text("\n".join(["schema=station.startup-logging.scoped-types.r139.diagnostic.v1", "partition=" + PARTITION, "donorSha256=" + DEX,
        "families=" + "|".join(sorted(EXISTING | {OWNER})), "originalAllowed=" + "|".join(sorted(EXISTING)),
        "finalAllowed=" + "|".join(sorted(EXISTING | {OWNER}))]) + "\n", encoding="utf-8")
    expected = f"verifiedClasses=608 finalClasses=609 unchanged=606 originalAllowed=2 finalAllowed=3 donorSHA={DEX}"
    verify = [java, "-cp", cp, "VerifyScopedPartition", a.base, PARTITION, DEX]
    need(run(verify + [working, scope]) == expected, "Preassembly unrelated class proof differs")
    output = out / PARTITION
    assembled = run([java, "-cp", cp, "AssembleScopedPartition", a.base, PARTITION, DEX, working, output, scope])
    need(assembled.splitlines()[0] == expected, "Assembly class proof differs")
    final_zip = out / "final-container.zip"
    container(final_zip, PARTITION, output.read_bytes())
    final = out / "final-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", final_zip, PARTITION, sha(output), final])
    need(run(verify + [final, scope]) == expected, "Postassembly unrelated classes differ")
    need(patch_logging.verify(donor, final) == method_proof, "Postassembly method inverse differs")
    need(projection(final)[OWNER] == projection(helper)[OWNER], "Compiled helper changed during assembly")
    need(verify_commit(a.source_commit) == pins, "Source changed during diagnostic build")
    receipt = dict(schema="station.r139.startup-logging.dex.v1", passed=True, compiled=True, sourceCommit=a.source_commit,
        sourceFiles=pins, baselineApkSha256=BASE, baselineDexSha256=DEX, outputDexSha256=sha(output),
        inputSha256=TOOLS, helperJarSha256=sha(jar), helperDexSha256=sha(overlay / "classes.dex"),
        assemblyProof=assembled, **method_proof, **temporary_fields())
    (out / "dex-compilation.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("base", "jdk-bin", "android-jar", "d8-jar", "apktool", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--check-inputs-only", action="store_true")
    result = build(p.parse_args())
    print(json.dumps({key: result.get(key) for key in ("passed", "compiled", "outputDexSha256", "diagnosticTemporary")}))
