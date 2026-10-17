"""Compile only two reviewed HTTP sources and replace only their closed DEX28 family."""
from pathlib import Path
import argparse
import json
import os
import struct
import sys
import zipfile

sys.dont_write_bytecode = True
from common import *

JAVA_CLASSES = {"org/emulationstation/frontend/station/" + n + ".class" for n in
                ("StationHttp", "StationHttp$1", "StationHttp$ResponseBody", "StationDownloadOrigin")}


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R140 donor required")
    inputs = dict(java=a.jdk_bin / "java.exe", javac=a.jdk_bin / "javac.exe", androidJar=a.android_jar,
                  d8Jar=a.d8_jar, apktool=a.apktool, roomsJar=a.rooms_jar, clientJar=a.client_jar)
    need({k: sha(v) for k, v in inputs.items()} == TOOLS, "Exact legacy Windows JDK17/API34/D8 toolchain required")
    pins = verify_commit(a.source_commit)
    with zipfile.ZipFile(a.base) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13860 and ROOT_DEX <= set(names) and
             digest(archive.read(PARTITION)) == DEX and digest(archive.read("classes35.dex")) == PRESERVED_DEX35 and
             entry_sha(archive, "lib/arm64-v8a/libstation_retroarch.so") == RETRO, "Exact current R140 DEX/runtime inventory required")
        preserved = {name: entry_sha(archive, name) for name in sorted(ROOT_DEX - {PARTITION})}
        donor_bytes = archive.read(PARTITION)
    if a.check_inputs_only:
        return dict(passed=True, compiled=False, sourceCommit=a.source_commit, sourceFiles=pins, **state_fields())
    out = isolated(a.out)
    out.mkdir(parents=True)
    classes = out / "classes"
    classes.mkdir()
    productive = sorted((ROOT / "java").rglob("*.java"))
    need(len(productive) == 2, "Exactly two reviewed productive Java files required")
    java, javac = inputs["java"], inputs["javac"]
    classpath = os.pathsep.join(map(str, (a.android_jar, a.rooms_jar, a.client_jar)))
    run([javac, "-encoding", "UTF-8", "--release", "8", "-proc:none", "-implicit:none", "-sourcepath", "",
         "-cp", classpath, "-d", classes, *productive])
    files = sorted(p for p in classes.rglob("*") if p.is_file())
    need({p.relative_to(classes).as_posix() for p in files} == JAVA_CLASSES and
         all(p.read_bytes()[:4] == b"\xca\xfe\xba\xbe" and struct.unpack(">H", p.read_bytes()[6:8])[0] == 52 for p in files),
         "Closed four-class Java8 overlay required; dependencies and fixtures forbidden")
    jar = out / "http-overlay.jar"
    with zipfile.ZipFile(jar, "w", zipfile.ZIP_STORED) as archive:
        for path in files:
            archive.writestr(zipfile.ZipInfo(path.relative_to(classes).as_posix(), (1980, 1, 1, 0, 0, 0)), path.read_bytes())
    overlay = out / "overlay-dex"
    overlay.mkdir()
    run([java, "-cp", a.d8_jar, "com.android.tools.r8.D8", "--release", "--min-api", "28", "--lib", a.android_jar,
         "--classpath", a.rooms_jar, "--classpath", a.client_jar, "--output", overlay, jar])
    need({p.name for p in overlay.iterdir()} == {"classes.dex"}, "One closed D8 overlay partition required")
    tools = out / "tools"
    tools.mkdir()
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", a.apktool, "-d", tools, ROOT / "recipe/ScopedHttpDex.java"])
    donor = out / "donor-classes28.dex"
    donor.write_bytes(donor_bytes)
    output = out / PARTITION
    class_receipt = out / "class-preservation.json"
    run([java, "-cp", os.pathsep.join(map(str, (tools, a.apktool))), "ScopedHttpDex", donor, overlay / "classes.dex", output, class_receipt])
    projection = read(class_receipt)
    need(verify_commit(a.source_commit) == pins and {k: sha(v) for k, v in inputs.items()} == TOOLS,
         "Frozen Java/recipe/tool input changed during DEX compilation")
    result = dict(schema="station.r141.direct-downloads.dex.v1", passed=True, compiled=True, sourceCommit=a.source_commit,
        sourceFiles=pins, baselineApkSha256=BASE, baselineDexSha256=DEX, outputDexSha256=sha(output),
        preservedDex35Sha256=PRESERVED_DEX35, preservedDexSha256=preserved, inputSha256=TOOLS,
        productiveJavaTarget=8, androidCompileApi=34, dexMinimumApi=28, classMajorVersion=52,
        overlayJarSha256=sha(jar), d8OverlayDexSha256=sha(overlay / "classes.dex"),
        compiledJavaClasses={p.relative_to(classes).as_posix(): sha(p) for p in files},
        classPreservationReceiptSha256=sha(class_receipt), sdkOrDependenciesPackaged=False,
        **projection, **state_fields())
    validate_dex_receipt(result, output, a.source_commit, pins)
    (out / "dex-compilation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("base", "jdk-bin", "android-jar", "d8-jar", "apktool", "rooms-jar", "client-jar", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--check-inputs-only", action="store_true")
    result = build(p.parse_args())
    print(json.dumps({k: result.get(k) for k in ("passed", "compiled", "outputDexSha256", "revision")}))
