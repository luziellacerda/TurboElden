"""Build only DEX8 with the exact one-class Switch path overlay; never an APK."""
from pathlib import Path
import argparse
import hashlib
import os
import re
import struct
import zipfile
from common import *
import patch_switch_path as patcher

PARTITION = "classes8.dex"
CLASS_PATH = "org/emulationstation/frontend/switchengine/SwitchConfigPatcher.smali"
APKTOOL_SHA = "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423"
TOOLS = {"java.exe": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
         "javac.exe": "9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549"}
DEPENDENCIES = {
    "integration/psx-online/recipe/DecodeDolphinPartition.java": "d1365cf8cce05fb08c6e04dbcc47e9b154af268637bf0d768c32f851420c2b67",
    "integration/local-sony-demos/recipe/VerifyScopedPartition.java": "32b627f5334d1c7b62c94ab2fef05d10df44707241f9379416fb44f6464f8acd",
}


def file_map(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob("*.smali"))}


def methods(raw):
    result = {}
    for block in re.findall(rb"(?m)^\.method [^\r\n]+\r?\n.*?^\.end method", raw, re.S):
        signature = block.splitlines()[0].decode("ascii").split()[-1]
        require(signature not in result, "Duplicate Switch method")
        result[signature] = block
    return result


def verify_tools(a):
    require(sha(a.apktool) == APKTOOL_SHA, "Exact Apktool 3.0.3 required")
    require(all(sha(a.jdk / "bin" / n) == h for n, h in TOOLS.items()), "Pinned Java 17 tools required")
    require(all(sha(REPO / n) == h for n, h in DEPENDENCIES.items()), "Pinned scoped helpers changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base-apk", "jdk", "apktool", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    a = parser.parse_args()
    a.out = a.out.resolve()
    require(REPO != a.out and REPO not in a.out.parents,
            "Keep generated DEX and tools outside repository sources")
    pins = verify_source_commit(a.source_commit)
    require(a.base_apk.stat().st_size == BASE_BYTES and sha(a.base_apk) == BASE_SHA, "Exact corrected R131 APK required")
    require(not a.out.exists(), "Choose a fresh separate output directory")
    verify_tools(a)
    with zipfile.ZipFile(a.base_apk) as archive:
        raw = archive.read(PARTITION)
    require(len(raw) == 11664 and hashlib.sha256(raw).hexdigest() == patcher.BASE_DEX_SHA,
            "Exact R131 DEX8 required")
    count = struct.unpack_from("<I", raw, 96)[0]
    require(count == 3, "Exact Switch partition class set required")
    a.out.mkdir(parents=True)
    tools = a.out / "tools"
    tools.mkdir()
    java, javac = a.jdk / "bin/java.exe", a.jdk / "bin/javac.exe"
    helpers = [REPO / n for n in DEPENDENCIES] + [ROOT / "recipe/AssembleScopedPartition.java"]
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", a.apktool, "-d", tools, *helpers], a.out, "scope-tools")
    cp = str(tools) + os.pathsep + str(a.apktool)
    decoded = a.out / "donor-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", a.base_apk, PARTITION, patcher.BASE_DEX_SHA, decoded], a.out, "decode-donor")
    original = file_map(decoded)
    require(len(original) == count and CLASS_PATH in original, "Decoded Switch class set differs")
    target = decoded / CLASS_PATH
    old = target.read_bytes()
    transformed, transform = patcher.patch(old)
    target.write_bytes(transformed)
    changed = file_map(decoded)
    require(set(changed) == set(original) and [n for n in changed if changed[n] != original[n]] == [CLASS_PATH],
            "Exact one-class overlay required")
    verified = f"verifiedClasses=3 unchanged=2 changed=1 donorSHA={patcher.BASE_DEX_SHA}"
    check = run([java, "-cp", cp, "VerifyScopedPartition", a.base_apk, PARTITION, patcher.BASE_DEX_SHA,
                 decoded, patcher.TYPE], a.out, "verify-before")
    require(check.strip() == verified, "Original non-scoped Switch classes changed")
    dex = a.out / PARTITION
    assembled = run([java, "-cp", cp, "AssembleScopedPartition", a.base_apk, PARTITION, patcher.BASE_DEX_SHA,
                     decoded, dex, patcher.TYPE], a.out, "assemble-switch").splitlines()
    pattern = rf"assembledClasses=3 restoredInitializerArrays=([0-2]) changed=1 donorSHA={patcher.BASE_DEX_SHA}"
    match = re.fullmatch(pattern, assembled[-1] if assembled else "")
    require(len(assembled) == 2 and assembled[0] == verified and match is not None,
            "Exact scoped initializer-preserving assembly required")
    final_raw = dex.read_bytes()
    require(final_raw.startswith(b"dex\n") and struct.unpack_from("<I", final_raw, 96)[0] == count and
            sha(dex) != patcher.BASE_DEX_SHA, "Exact changed DEX8 class set required")
    # Decode the actual assembled partition and compare every outside class
    # again against the real donor, not merely the input directory.
    fixture = a.out / "scoped-container.zip"
    with zipfile.ZipFile(fixture, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(PARTITION, final_raw)
    final_smali = a.out / "final-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", fixture, PARTITION, sha(dex), final_smali], a.out, "decode-final")
    actual = file_map(final_smali)
    require(set(actual) == set(original) and all(actual[n] == h for n, h in original.items() if n != CLASS_PATH),
            "Actual assembled DEX changed another class")
    check = run([java, "-cp", cp, "VerifyScopedPartition", a.base_apk, PARTITION, patcher.BASE_DEX_SHA,
                 final_smali, patcher.TYPE], a.out, "verify-after")
    require(check.strip() == verified, "Actual non-scoped DEX classes changed")
    # Smali writing can relabel branches; allow no opaque post-assembly edits.
    final_target = (final_smali / CLASS_PATH).read_text(encoding="utf-8")
    require(final_target.count("r132MigrateLegacyPath(Ljava/io/File;Lorg/w3c/dom/Element;)Z") == 2 and
            final_target.count("r132LegacyVacant(Ljava/io/File;)Z") == 3 and
            final_target.count('"SAMBOX-Vfull/sistema/roms/switch"') == 1 and
            final_target.count('"roms/switch"') == 2,
            "Actual Switch path/migration methods absent")
    original_methods = methods(old)
    final_class_raw = (final_smali / CLASS_PATH).read_bytes()
    actual_methods = methods(final_class_raw)
    modified_method = "apply(Ljava/io/File;)Ljava/lang/String;"
    added_methods = ["r132LegacyVacant(Ljava/io/File;)Z",
                     "r132MigrateLegacyPath(Ljava/io/File;Lorg/w3c/dom/Element;)Z"]
    require(set(actual_methods) == set(original_methods) | set(added_methods) and
            all(actual_methods[n] == body for n, body in original_methods.items() if n != modified_method),
            "An existing Switch method outside apply changed")
    old_fields = re.findall(rb"(?m)^\.field [^\r\n]+", old)
    final_fields = re.findall(rb"(?m)^\.field [^\r\n]+", final_class_raw)
    require(final_fields == old_fields and len(old_fields) == 1,
            "Original Switch static COMMAND or fields changed")
    require(source_map() == pins and sha(a.base_apk) == BASE_SHA, "Inputs changed while building DEX8")
    verify_tools(a)
    require(file_map(decoded) == changed, "Scoped smali inputs changed during assembly")
    receipt = {"schema": "station.startup.cleanup.switch.v1", "revision": "R132",
        "sourceCommit": a.source_commit, "sourceSha256": pins, "baseApkSha256": BASE_SHA,
        "baselineDexSha256": patcher.BASE_DEX_SHA, "baselineClassCount": 3, "unchangedClassCount": 2,
        "allowedTypes": [patcher.TYPE], "approvedScopes": ["switch-canonical-config-path"],
        "payloads": {PARTITION: {"path": str(dex.resolve()), "bytes": dex.stat().st_size, "sha256": sha(dex)}},
        "inputClassSha256": original, "scopedInputClassSha256": changed,
        "assembledClassSha256": actual, "transform": transform,
        "changedExistingMethods": [modified_method], "addedPrivateMethods": added_methods,
        "unchangedExistingMethodSha256": {n: hashlib.sha256(v).hexdigest() for n, v in original_methods.items()
                                          if n != modified_method},
        "existingMethodsOutsideApplyByteVerified": True, "staticCommandUnchanged": True,
        "dependencySourceSha256": dict(DEPENDENCIES), "toolSha256": {**TOOLS, "apktool": APKTOOL_SHA},
        "restoredInitializerArrays": int(match.group(1)), "dexChanged": True, "noNewClasses": True,
        "outsideAllowlistByteVerified": True, "gameAndSaveFilesPreserved": True,
        "customConfiguredPathsPreserved": True, "noLegacyDirectoryCreated": True,
        "missingOrEmptyLegacyOnly": True, "recursiveScan": False,
        "classSetExactlyPreserved": True, "unrelatedClassesByteIdentical": True,
        "originalEngineCommandsPreserved": True, "noFilesMovedOrDeleted": True,
        "filePreservationScope": "Existing games, saves and ROM directories; original atomic CFG temporary writer is retained",
        "onlyExactEmptyLegacyPathMigrated": True,
        "migrationAllowedLegacyStates": ["missing", "empty-directory"],
        "newSwitchRoot": patcher.CANONICAL, "migrationLegacyRoot": patcher.LEGACY,
        "apkProduced": False, "installed": False, "physicalValidation": False}
    write(a.out / "switch-receipt.json", receipt)
    print(json.dumps({"compiled": True, "allowedTypes": receipt["allowedTypes"], "payloads": receipt["payloads"]}))


if __name__ == "__main__":
    main()
