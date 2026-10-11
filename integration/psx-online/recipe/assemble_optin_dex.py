#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Reproduce both complete R126 donor partitions with only the PSX opt-in hooks.

This never changes the donor APK or creates a new APK. A new output directory is
required. The three Java helpers, the two patch recipes and the pinned apktool
JAR are the complete tool classpath; no historical compiled helper is required.
Run on Windows with JDK 17. New PSX Java classes are compiled separately and must
not be inserted into these partitions, which preserve their original class set.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import zipfile


APK_SHA = "f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d"
APK_BYTES = 2233970789
JAR_SHA = "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423"
JAR_BYTES = 15478013
HELPERS = ("DecodeDolphinPartition.java", "AssembleDolphinPartition.java",
           "VerifyOptinPartition.java")
PARTITIONS = (
    {
        "partition": "classes6.dex",
        "donorSha256": "f19dd92662fd066611c0e9feefd5c814bc06110f27fda50c2b3a63565965ba95",
        "classCount": 50,
        "decodedUnchangedClasses": 49,
        "changedType": "Lorg/libsdl/app/SDLActivity;",
        "smali": "org/libsdl/app/SDLActivity.smali",
        "donorSmaliSha256": "ba8023df8f9d7bff74be26f7bbef90c01b91b5feeb0332ec646634e3eb3ece85",
        "patchedSmaliSha256": "d8e84ab5399bfcbe8e09699814dbb82ba634258654ff72eceedcb6fe68ea93fd",
        "patch": "patch_sdl_optin.py",
        "hookReceipt": "sdl-hook-receipt.json",
        "bytes": 96344,
        "sha256": "61ff49b6253a9f31f0519c2517a6b2b5b55c5af53c529cfd728bd052f0c5dacb",
        "changedMethods": ["handleNativeState", "onDestroy"],
    },
    {
        "partition": "classes28.dex",
        "donorSha256": "4d8e479f445396fa052bee5f7489a5748abdbfdccc9db4c7d035c8f2d0c646fa",
        "classCount": 271,
        "decodedUnchangedClasses": 270,
        "changedType": "Lorg/emulationstation/frontend/station/StationComponentFactory;",
        "smali": "org/emulationstation/frontend/station/StationComponentFactory.smali",
        "donorSmaliSha256": "786d7e2a6a9ded6ef4e116791c67b9b70809f4c62a147b790ae2595e3c92d47c",
        "patchedSmaliSha256": "0cc72f8ca9a6ba2a87b80ef48e6137642f0b19e7b16e1b39c370f01a4be1b270",
        "patch": "patch_factory_optin.py",
        "hookReceipt": "factory-hook-receipt.json",
        "bytes": 304476,
        "sha256": "5966ef8405701fa946c60fe6d922726cd74c27783a4cb76d240dfa4bc324de9d",
        "changedMethods": ["instantiateApplication"],
    },
)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def expect_file(path, sha, size=None):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing or linked input: " + path.name)
    if size is not None and path.stat().st_size != size:
        raise ValueError("Unexpected size: " + path.name)
    if digest(path) != sha:
        raise ValueError("Unexpected SHA256: " + path.name)


def run(command):
    result = subprocess.run([str(x) for x in command], check=True,
                            text=True, encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True,
                        help="Exact full R126 APK, read only")
    parser.add_argument("--jdk", type=Path, required=True,
                        help="JDK 17 home containing bin/java.exe and javac.exe")
    parser.add_argument("--apktool", type=Path, required=True,
                        help="Exact apktool_3.0.3.jar (sole external classpath JAR)")
    parser.add_argument("--out", type=Path, required=True,
                        help="New output directory; existing directories are rejected")
    args = parser.parse_args()
    if os.name != "nt":
        raise ValueError("Pinned smali line endings and ordering require Windows")
    recipe = Path(__file__).resolve().parent
    apk = args.apk.resolve(strict=True)
    jar = args.apktool.resolve(strict=True)
    jdk = args.jdk.resolve(strict=True)
    out = args.out.resolve()
    if out.exists():
        raise ValueError("Output must be a new directory")
    if out == recipe or recipe in out.parents:
        raise ValueError("Build output must remain outside the source recipe")
    java = jdk / "bin/java.exe"
    javac = jdk / "bin/javac.exe"
    if not java.is_file() or not javac.is_file():
        raise ValueError("Missing JDK tools")
    expect_file(apk, APK_SHA, APK_BYTES)
    expect_file(jar, JAR_SHA, JAR_BYTES)
    version = subprocess.run([str(java), "-version"], check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", errors="replace")
    version_text = (version.stdout + version.stderr).strip()
    if 'version "17.' not in version_text:
        raise ValueError("This workflow requires JDK 17")
    files = [recipe / name for name in HELPERS]
    files += [recipe / item["patch"] for item in PARTITIONS]
    files += [Path(__file__).resolve()]
    sources = {path.name: digest(path) for path in files}
    with zipfile.ZipFile(apk) as archive:
        for item in PARTITIONS:
            info = archive.getinfo(item["partition"])
            if not 0 < info.file_size <= 16 * 1024 * 1024:
                raise ValueError("Unexpected donor partition size")
            if hashlib.sha256(archive.read(info)).hexdigest() != item["donorSha256"]:
                raise ValueError("Unexpected donor partition SHA256")
    out.mkdir(parents=True)
    tools = out / "tools"
    tools.mkdir()
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", jar,
         "-d", tools, *(recipe / name for name in HELPERS)])
    classpath = str(tools) + os.pathsep + str(jar)
    commands = []
    outputs = []
    for item in PARTITIONS:
        stem = item["partition"].removesuffix(".dex")
        smali = out / ("smali" + stem.removeprefix("classes"))
        run([java, "-cp", classpath, "DecodeDolphinPartition", apk,
             item["partition"], item["donorSha256"], smali])
        original = smali / item["smali"]
        expect_file(original, item["donorSmaliSha256"])
        patched = out / (stem + "-patched.smali")
        hook_receipt = out / item["hookReceipt"]
        run([sys.executable, "-X", "utf8", recipe / item["patch"],
             "--smali", original, "--out", patched,
             "--receipt", hook_receipt])
        expect_file(patched, item["patchedSmaliSha256"])
        original.write_bytes(patched.read_bytes())
        verification = run([java, "-cp", classpath, "VerifyOptinPartition", apk,
                            item["partition"], item["donorSha256"], smali,
                            item["changedType"]])
        required = ("verifiedClasses=" + str(item["classCount"]) +
                    " unchanged=" + str(item["decodedUnchangedClasses"]) +
                    " changed=1 donorSHA=" + item["donorSha256"])
        if verification != required:
            raise ValueError("Class preservation verification did not match")
        target = out / item["partition"]
        run([java, "-cp", classpath, "AssembleDolphinPartition", smali, target])
        expect_file(target, item["sha256"], item["bytes"])
        with target.open("rb") as stream:
            header = stream.read(112)
        if not header.startswith(b"dex\n") or len(header) != 112:
            raise ValueError("Missing DEX header")
        if struct.unpack_from("<I", header, 96)[0] != item["classCount"]:
            raise ValueError("Final DEX class set count changed")
        commands += [
            {"tool": "DecodeDolphinPartition", "partition": item["partition"]},
            {"tool": item["patch"], "changedType": item["changedType"]},
            {"tool": "VerifyOptinPartition", "result": verification},
            {"tool": "AssembleDolphinPartition", "partition": item["partition"]},
        ]
        outputs.append({key: item[key] for key in (
            "partition", "bytes", "sha256", "donorSha256", "classCount",
            "decodedUnchangedClasses", "changedMethods")})
        outputs[-1]["changedClasses"] = [item["changedType"][1:-1].replace("/", ".")]
        outputs[-1]["inverseOriginalClassByteIdentical"] = True
        outputs[-1]["hookReceiptSha256"] = digest(hook_receipt)
    if sources != {path.name: digest(path) for path in files}:
        raise ValueError("Recipe source changed during assembly")
    receipt = {
        "schema": 2, "passed": True,
        "scope": "Complete pinned donor partitions with PSX opt-in hooks only",
        "inputApk": {"sha256": APK_SHA, "bytes": APK_BYTES},
        "toolClasspath": [{"name": jar.name, "sha256": JAR_SHA, "bytes": JAR_BYTES}],
        "helperClasspath": "<out>/tools;<pinned-apktool.jar>",
        "jdkVersion": version_text.splitlines(),
        "sourceSha256": sources,
        "sequence": commands,
        "outputs": outputs,
        "classSetPreserved": True, "otherProcessesUnchanged": True,
        "apkChanged": False, "signatureChanged": False,
        "limits": [
            "Reassembly changes DEX ordering/indices; unchanged classes compare decoded source",
            "Only classes6.dex and classes28.dex are produced, never an APK",
            "New PSX Java is compiled separately; do not duplicate donor classes",
            "No Android process, controller or game is executed by this workflow",
        ],
    }
    (out / "complete-dex-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
