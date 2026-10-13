"""Assemble only the exact Launch insertion; never compile replacement program classes."""
from pathlib import Path
import argparse
import json
import os
import shutil
import sys
import zipfile

sys.dont_write_bytecode = True
from common import BASE, BASE_BYTES, DEX, ROOT, PARTITION, CLINICAL_SHA, sha, digest, need, run, isolated, verify_clinical, verify_commit, state_fields
import patch_binding

TOOLS = {
    "java": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "javac": "9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549",
    "apktool": "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",
}


def container(path, raw):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(PARTITION, raw)


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact original R139 signed donor required")
    inputs = {"java": a.jdk_bin / "java.exe", "javac": a.jdk_bin / "javac.exe", "apktool": a.apktool}
    need({k: sha(v) for k, v in inputs.items()} == TOOLS, "Pinned scoped assembler toolchain required")
    verify_clinical(a.resolver_receipt)
    pins = verify_commit(a.source_commit)
    with zipfile.ZipFile(a.base) as archive:
        need(len(archive.namelist()) == len(set(archive.namelist())) == 13860 and digest(archive.read(PARTITION)) == DEX, "Exact original R139 DEX/entry set required")
    if a.check_inputs_only:
        return dict(passed=True, compiled=False, sourceCommit=a.source_commit, sourceFiles=pins, clinicalQualificationSha256=CLINICAL_SHA, **state_fields())
    out = isolated(a.out)
    out.mkdir(parents=True)
    tools = out / "tools"
    tools.mkdir()
    recipe = ROOT / "recipe"
    java, javac = inputs["java"], inputs["javac"]
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", a.apktool, "-d", tools,
         *[recipe / n for n in ("DecodeDolphinPartition.java", "VerifyScopedPartition.java", "AssembleScopedPartition.java")]])
    cp = os.pathsep.join(map(str, (tools, a.apktool)))
    donor = out / "donor-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", a.base, PARTITION, DEX, donor])
    working = out / "working-smali"
    shutil.copytree(donor, working)
    target = working / patch_binding.RELATIVE
    target.write_bytes(patch_binding.patch(target.read_bytes()))
    method_proof = patch_binding.verify(donor, working)
    scope = out / "scope.properties"
    scope.write_text("\n".join(["schema=station.snes-multitap-unique-flag.scoped-types.r143.v1", "partition=" + PARTITION,
        "donorSha256=" + DEX, "families=" + patch_binding.OWNER, "originalAllowed=" + patch_binding.OWNER,
        "finalAllowed=" + patch_binding.OWNER]) + "\n", encoding="utf-8")
    expected = f"verifiedClasses=608 finalClasses=608 unchanged=607 originalAllowed=1 finalAllowed=1 donorSHA={DEX}"
    verify = [java, "-cp", cp, "VerifyScopedPartition", a.base, PARTITION, DEX]
    need(run(verify + [working, scope]) == expected, "Unrelated source classes changed")
    output = out / PARTITION
    assembled = run([java, "-cp", cp, "AssembleScopedPartition", a.base, PARTITION, DEX, working, output, scope])
    need(assembled.splitlines()[0] == expected, "Assembly class proof differs")
    final_zip = out / "final-container.zip"
    container(final_zip, output.read_bytes())
    final = out / "final-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", final_zip, PARTITION, sha(output), final])
    need(run(verify + [final, scope]) == expected and patch_binding.verify(donor, final) == method_proof, "Postassembly class/method inverse differs")
    need(verify_commit(a.source_commit) == pins and verify_clinical(a.resolver_receipt)["passed"] is True, "Frozen source/clinical evidence changed during DEX build")
    receipt = dict(schema="station.r143.snes-multitap-unique-flag.dex.v1", passed=True, compiled=True,
        sourceCommit=a.source_commit, sourceFiles=pins, baselineApkSha256=BASE, baselineDexSha256=DEX,
        outputDexSha256=sha(output), inputSha256=TOOLS, clinicalQualificationSha256=CLINICAL_SHA,
        assemblyProof=assembled, existingProgramClassesRecompiled=False, newProgramClassesCompiled=False,
        **method_proof, **state_fields())
    (out / "dex-compilation.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("base", "jdk-bin", "apktool", "resolver-receipt", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--check-inputs-only", action="store_true")
    result = build(p.parse_args())
    print(json.dumps({k: result.get(k) for k in ("passed", "compiled", "outputDexSha256", "revision")}))
