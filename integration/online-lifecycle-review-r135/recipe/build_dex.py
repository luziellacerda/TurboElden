"""Build only the scoped R135 classes35.dex payload over the exact signed R134.

No APK assembly, runtime identity, signing, phone, or network operation.
All inputs are explicit and hard pinned. The reviewed Java sources are not compiled
or changed here: only the closed, previously compiled Java8 overlay is D8 program.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE_SHA = "f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2"
BASE_BYTES = 2714991631
PARTITION = "classes35.dex"
PARTITION_SHA = "d5a689c7e60df0d3a822f97f17a27875c7c1b38da00f44419735724d4d1dda76"
SOURCE_PINS_SHA = "098b53075ca15255fc3df1d5637d169d694d7ebf84e5ae481cf6fed1cc03c54e"
PACKAGE = "org/emulationstation/frontend/netplay/"
FAMILIES = tuple("L" + PACKAGE + n + ";" for n in (
    "StationDolphinSession", "StationGameSession", "StationHumanDeparture"))
JAR_CLASSES = {PACKAGE + n + ".class" for n in (
    "StationDolphinSession", "StationDolphinSession$Session",
    "StationDolphinSession$Session$1", "StationDolphinSession$Session$2",
    "StationDolphinSession$Session$Control", "StationGameSession",
    "StationGameSession$1", "StationGameSession$LaunchReturn", "StationHumanDeparture")}
ORIGINAL_TYPES = {"L" + PACKAGE + n + ";" for n in (
    "StationDolphinSession", "StationDolphinSession$Session",
    "StationDolphinSession$Session$1", "StationDolphinSession$Session$2",
    "StationDolphinSession$Session$Control",
    "StationDolphinSession$$ExternalSyntheticLambda0",
    "StationDolphinSession$$ExternalSyntheticLambda1",
    *["StationDolphinSession$Session$$ExternalSyntheticLambda" + str(i) for i in range(1, 10)],
    "StationGameSession", "StationGameSession$1", "StationGameSession$LaunchReturn",
    *["StationGameSession$$ExternalSyntheticLambda" + str(i) for i in range(5)])}
INPUT_PINS = {
    "overlay_jar": "8e746f8fa449cfebae14b9db68b0080ffa9a9bfb6a45300449c4d2f7c9ce2bc4",
    "compile_receipt": "1807e0200ff5750b2c636bd7318e4afd831fecfa7f1dd9b5064f34ebb65b262a",
    "android_jar": "6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad",
    "d8_jar": "305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5",
    "apktool": "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",
    "rooms_jar": "6b2929eb3621b208593a886b6f06a32de52af9c931663cb314e197af155f773d",
    "client_jar": "011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313",
    "java": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "javac": "9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549",
}
HELPER_PINS = {
    "AssembleScopedPartition.java": "5ea794aad4cb177080e331b09d449419e352020ac61a6b9ea4194e32b4b1b022",
    "DecodeDolphinPartition.java": "d1365cf8cce05fb08c6e04dbcc47e9b154af268637bf0d768c32f851420c2b67",
    "VerifyScopedPartition.java": "6ff4b2e97e17e3ef83411df29e60b9b0ad42c7ae9e9fdfddfdfc9ea5f24a54bc",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def source_map():
    return {p.relative_to(ROOT).as_posix(): sha(p)
            for directory in ("java", "recipe")
            for p in sorted((ROOT / directory).rglob("*"))
            if p.is_file() and p.suffix in {".py", ".java"}}


def verify_commit(commit, frozen):
    require(re.fullmatch(r"[0-9a-f]{40}", commit or ""), "Full frozen source commit required for DEX compilation")
    prefix = ROOT.relative_to(REPO).as_posix()
    git = ["git", "-c", "safe.directory=" + REPO.as_posix(), "-C", str(REPO)]
    for name, checksum in {**frozen, "SOURCE-PINS.json": SOURCE_PINS_SHA}.items():
        raw = subprocess.check_output(git + ["show", commit + ":" + prefix + "/" + name], stderr=subprocess.PIPE)
        require(digest(raw) == checksum, "Source differs from frozen commit: " + name)


def belongs(type_name):
    return any(type_name == root or type_name.startswith(root[:-1] + "$") for root in FAMILIES)


def dex_types(raw):
    require(raw.startswith(b"dex\n") and len(raw) >= 112, "Invalid DEX header")
    require(struct.unpack_from("<I", raw, 32)[0] == len(raw), "DEX file size differs")
    require(struct.unpack_from("<I", raw, 36)[0] == 112, "DEX header size differs")
    string_count, string_offset, type_count, type_offset = struct.unpack_from("<4I", raw, 56)
    class_count, class_offset = struct.unpack_from("<2I", raw, 96)
    require(class_count < 65536 and string_count < 1000000 and type_count < 65536, "DEX table limits")
    require(string_offset + 4 * string_count <= len(raw) and
            type_offset + 4 * type_count <= len(raw) and
            class_offset + 32 * class_count <= len(raw), "DEX table bounds")
    strings = []
    for i in range(string_count):
        offset = struct.unpack_from("<I", raw, string_offset + 4 * i)[0]
        for _ in range(5):
            require(offset < len(raw), "DEX string bounds")
            byte = raw[offset]
            offset += 1
            if not byte & 128:
                break
        else:
            raise ValueError("Invalid DEX ULEB128")
        # Type descriptors are ASCII; unrelated source/debug MUTF8 strings are
        # never normalized or written by this inventory reader.
        end = raw.index(0, offset)
        strings.append(raw[offset:end])
    types = [strings[struct.unpack_from("<I", raw, type_offset + 4 * i)[0]] for i in range(type_count)]
    classes = [types[struct.unpack_from("<I", raw, class_offset + 32 * i)[0]].decode("ascii")
               for i in range(class_count)]
    require(len(set(classes)) == class_count, "Duplicate DEX class")
    return set(classes)


def smali_types(root):
    result = {}
    for path in sorted(root.rglob("*.smali")):
        require(not path.is_symlink(), "Symbolic smali input")
        name = "L" + path.relative_to(root).as_posix()[:-6] + ";"
        require(name not in result, "Duplicate smali type")
        result[name] = path
    return result


def run(command, out, label):
    env = {**os.environ, "TMP": str(out / "temp"), "TEMP": str(out / "temp"),
           "JAVA_TOOL_OPTIONS": '-Djava.io.tmpdir="' + str(out / "temp") + '" -XX:-UsePerfData',
           "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env, timeout=300)
    (out / (label + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    require(result.returncode == 0, label + " failed; inspect isolated diagnostics")
    if label == "overlay-d8":
        require(not re.search(r"(?im)^\s*(warning|error)\b", result.stdout + result.stderr),
                "D8 resolution warning/error requires review")
    return result.stdout.strip()


def container(path, partition, raw):
    require(not path.exists(), "Container output exists")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(zipfile.ZipInfo(partition, (1980, 1, 1, 0, 0, 0)), raw)


def check_inputs(a):
    require(a.donor.is_file() and not a.donor.is_symlink() and
            a.donor.stat().st_size == BASE_BYTES and sha(a.donor) == BASE_SHA, "Exact signed R134 donor required")
    inputs = {name: getattr(a, name) for name in INPUT_PINS if name not in {"java", "javac"}}
    inputs.update(java=a.jdk_bin / "java.exe", javac=a.jdk_bin / "javac.exe")
    for name, path in inputs.items():
        require(path.is_file() and not path.is_symlink() and sha(path) == INPUT_PINS[name],
                "Pinned input differs: " + name)
    require(sha(ROOT / "SOURCE-PINS.json") == SOURCE_PINS_SHA, "Reviewed source pins differ")
    pins = json.loads((ROOT / "SOURCE-PINS.json").read_text(encoding="utf-8"))
    for name, checksum in pins["overlaySha256"].items():
        require(sha(ROOT / name) == checksum, "Reviewed productive source differs: " + name)
    for name, checksum in pins["baselineSha256"].items():
        require(sha(REPO / name) == checksum, "Historical baseline source differs: " + name)
    for name, checksum in HELPER_PINS.items():
        require(sha(ROOT / "recipe" / name) == checksum, "Scoped helper differs: " + name)
    receipt = json.loads(a.compile_receipt.read_text(encoding="utf-8"))
    require(receipt["status"] == "compiled-java-overlay-only" and receipt["classCount"] == 9 and
            receipt["classMajorVersion"] == 52 and receipt["productionJavaTarget"] == 8 and
            receipt["androidApi"] == 34 and receipt["jarSha256"] == INPUT_PINS["overlay_jar"] and
            receipt["sourcePinsSha256"] == SOURCE_PINS_SHA and
            receipt["sourcesSha256"] == pins["overlaySha256"] and
            receipt["testsOrFixturesPackaged"] is False and receipt["sdkOrDependenciesPackaged"] is False,
            "Reviewed productive compilation receipt differs")
    with zipfile.ZipFile(a.overlay_jar) as archive:
        require(len(archive.namelist()) == 9 and set(archive.namelist()) == JAR_CLASSES,
                "Closed nine-class productive JAR required")
        for name in archive.namelist():
            raw = archive.read(name)
            require(raw[:4] == b"\xca\xfe\xba\xbe" and struct.unpack_from(">H", raw, 6)[0] == 52,
                    "Java8 class required: " + name)
            require(digest(raw) == receipt["classesSha256"][name], "Productive class differs: " + name)
    donor_dex = {}
    with zipfile.ZipFile(a.donor) as archive:
        names = {n for n in archive.namelist() if re.fullmatch(r"classes(?:[2-9]|[1-9][0-9])?\.dex", n)}
        expected = {"classes.dex", *[f"classes{i}.dex" for i in range(2, 41)]}
        require(names == expected, "Exact forty-partition R134 donor required")
        for name in sorted(names):
            raw = archive.read(name)
            types = dex_types(raw)
            allowed = {t for t in types if belongs(t)}
            donor_dex[name] = digest(raw)
            if name == PARTITION:
                require(digest(raw) == PARTITION_SHA and len(types) == 606 and allowed == ORIGINAL_TYPES,
                        "Exact R134 online lifecycle partition required")
            else:
                require(not allowed, "Scoped class already present in another partition")
    return inputs, pins, donor_dex


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("donor", "overlay-jar", "compile-receipt", "jdk-bin", "android-jar", "d8-jar",
                "apktool", "rooms-jar", "client-jar", "out"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--check-inputs-only", action="store_true")
    parser.add_argument("--source-commit", help="Full committed recipe/productive source identity; required for compilation")
    a = parser.parse_args()
    a.out = a.out.resolve()
    require(not a.out.exists() or a.out.is_dir() and not any(a.out.iterdir()), "New or empty isolated output required")
    require(a.out != ROOT and ROOT not in a.out.parents and a.out != REPO and REPO not in a.out.parents and
            all(".git" != p for p in a.out.parts), "Output cannot be source tree or Git metadata")
    require(not a.out.is_symlink(), "Symbolic output directory")
    inputs, pins, donor_dex = check_inputs(a)
    frozen = source_map()
    if a.source_commit:
        verify_commit(a.source_commit, frozen)
    if a.check_inputs_only:
        print(json.dumps(dict(passed=True, compiled=False, baselineApkSha256=BASE_SHA,
                              changedPartitions=[PARTITION], baselineClassCount=606,
                              baselineAllowedCount=24, unchangedClasses=582,
                              inputSha256=INPUT_PINS, sourceSha256=frozen, sourceCommit=a.source_commit,
                              sourceCommitVerified=bool(a.source_commit))))
        return
    verify_commit(a.source_commit, frozen)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "temp").mkdir()
    tools = a.out / "tools"
    tools.mkdir()
    java, javac = inputs["java"], inputs["javac"]
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", a.apktool, "-d", tools,
         *[ROOT / "recipe" / name for name in sorted(HELPER_PINS)]], a.out, "scoped-tools")
    cp = os.pathsep.join(map(str, (tools, a.apktool)))
    overlay_dex = a.out / "overlay-dex"
    overlay_dex.mkdir()
    run([java, "-cp", a.d8_jar, "com.android.tools.r8.D8", "--release", "--min-api", "28",
         "--lib", a.android_jar, "--classpath", a.rooms_jar, "--classpath", a.client_jar,
         "--output", overlay_dex, a.overlay_jar], a.out, "overlay-d8")
    require(sorted(overlay_dex.glob("*.dex")) == [overlay_dex / "classes.dex"], "Exactly one D8 overlay partition required")
    d8_types = dex_types((overlay_dex / "classes.dex").read_bytes())
    require(set(FAMILIES) <= d8_types and all(belongs(t) for t in d8_types),
            "D8 emitted a dependency, fixture, or foreign synthetic class")
    overlay_zip = a.out / "overlay-container.zip"
    container(overlay_zip, "classes.dex", (overlay_dex / "classes.dex").read_bytes())
    overlay_smali = a.out / "overlay-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", overlay_zip, "classes.dex",
         sha(overlay_dex / "classes.dex"), overlay_smali], a.out, "overlay-decode")
    final_allowed = smali_types(overlay_smali)
    require(set(final_allowed) == d8_types, "D8 decode type set differs")
    donor = a.out / "donor-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", a.donor, PARTITION, PARTITION_SHA, donor], a.out, "donor-decode")
    original = smali_types(donor)
    require(len(original) == 606 and {t for t in original if belongs(t)} == ORIGINAL_TYPES, "Decoded donor type set differs")
    outside = {t: sha(path) for t, path in original.items() if t not in ORIGINAL_TYPES}
    require(len(outside) == 582, "Unrelated class count differs")
    working = a.out / "working-smali"
    shutil.copytree(donor, working)
    # Paths come only from verified exact donor types, inside this new private
    # working directory; no donor/APK/source file is moved or deleted.
    for name in ORIGINAL_TYPES:
        target = working / (name[1:-1] + ".smali")
        require(target.is_file() and target.resolve().is_relative_to(working.resolve()), "Unsafe family member")
        target.unlink()
    for name, path in final_allowed.items():
        target = working / (name[1:-1] + ".smali")
        target.parent.mkdir(parents=True, exist_ok=True)
        require(belongs(name) and not target.exists(), "Overlay would replace a foreign class")
        shutil.copyfile(path, target)
    scope = a.out / "scope.properties"
    scope.write_text("\n".join(["schema=station.online-lifecycle.scoped-types.r135.v1",
        "partition=" + PARTITION, "donorSha256=" + PARTITION_SHA,
        "families=" + "|".join(sorted(FAMILIES)),
        "originalAllowed=" + "|".join(sorted(ORIGINAL_TYPES)),
        "finalAllowed=" + "|".join(sorted(final_allowed))]) + "\n", encoding="utf-8")
    expected = (f"verifiedClasses=606 finalClasses={582 + len(final_allowed)} unchanged=582 "
                f"originalAllowed=24 finalAllowed={len(final_allowed)} donorSHA={PARTITION_SHA}")
    verify = [java, "-cp", cp, "VerifyScopedPartition", a.donor, PARTITION, PARTITION_SHA]
    require(run(verify + [working, scope], a.out, "verify-source") == expected, "Preassembly class comparison differs")
    output = a.out / PARTITION
    assembled = run([java, "-cp", cp, "AssembleScopedPartition", a.donor, PARTITION,
                     PARTITION_SHA, working, output, scope], a.out, "assemble").splitlines()
    pattern = (rf"assembledClasses={582 + len(final_allowed)} restoredInitializerArrays=([0-9]+) "
               rf"originalAllowed=24 finalAllowed={len(final_allowed)} donorSHA={PARTITION_SHA}")
    restored = re.fullmatch(pattern, assembled[-1] if assembled else "")
    require(len(assembled) == 2 and assembled[0] == expected and restored is not None and
            int(restored.group(1)) <= 582, "Static initializer preservation receipt missing")
    final_zip = a.out / "final-container.zip"
    container(final_zip, PARTITION, output.read_bytes())
    final_smali = a.out / "final-smali"
    run([java, "-cp", cp, "DecodeDolphinPartition", final_zip, PARTITION, sha(output), final_smali], a.out, "final-decode")
    require(run(verify + [final_smali, scope], a.out, "verify-final") == expected,
            "Final unrelated class projection changed")
    final = smali_types(final_smali)
    require(set(final) == set(outside) | set(final_allowed) and dex_types(output.read_bytes()) == set(final), "Final class set differs")
    require({t: sha(final[t]) for t in outside} == outside, "Unrelated class bytes differ")
    require({t: sha(final[t]) for t in final_allowed} == {t: sha(p) for t, p in final_allowed.items()},
            "D8 productive class projection changed during assembly")
    require(source_map() == frozen, "Recipe or productive source changed during DEX build")
    verify_commit(a.source_commit, frozen)
    for name, path in inputs.items():
        require(sha(path) == INPUT_PINS[name], "Input changed during DEX build: " + name)
    require(sha(a.donor) == BASE_SHA, "Donor changed during DEX build")
    common = ORIGINAL_TYPES & set(final_allowed)
    receipt = dict(schema="station.online-lifecycle.dex.r135.v1", status="compiled-dex-payload-only",
        createdUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), passed=True,
        sourceCommit=a.source_commit, sourceCommitVerified=True,
        baseAppCommit="4f9039eb9ce13907ce043870bfe1f6e294888556", baselineApkSha256=BASE_SHA,
        baselineApkBytes=BASE_BYTES, sourcePinsSha256=SOURCE_PINS_SHA, sourceSha256=frozen,
        sourceCanonicalSha256=digest(canonical(frozen)), inputSha256=INPUT_PINS,
        inputFiles={name: dict(path=str(path.resolve()), bytes=path.stat().st_size,
                              sha256=INPUT_PINS[name]) for name, path in inputs.items()},
        productiveJavaTarget=8, classMajorVersion=52, androidCompileApi=34, dexMinimumApi=28,
        changedDexPartitions=[PARTITION], preservedDexSha256={n: h for n, h in donor_dex.items() if n != PARTITION},
        partition=PARTITION, baselineDexSha256=PARTITION_SHA, allowedFamilies=list(FAMILIES),
        originalClassCount=606, finalClassCount=len(final), unchangedClasses=582,
        originalAllowedTypes=sorted(ORIGINAL_TYPES), finalAllowedTypes=sorted(final_allowed),
        addedTypes=sorted(set(final_allowed) - ORIGINAL_TYPES), removedTypes=sorted(ORIGINAL_TYPES - set(final_allowed)),
        modifiedTypes=sorted(t for t in common if sha(original[t]) != sha(final[t])),
        baselineClassSha256={t: sha(p) for t, p in original.items()}, outputClassSha256={t: sha(p) for t, p in final.items()},
        unchangedClassSha256=outside, unrelatedClassesByteIdentical=True,
        classProjectionFormat="apktool-3.0.3-baksmali-locals-sequential-labels-debug-info",
        unrelatedProjectionCanonicalSha256=digest(canonical(outside)), classDeltaRestrictedToAllowedFamilies=True,
        staticInitializersPreserved=True, restoredInitializerArrays=int(restored.group(1)),
        d8SyntheticTypes=sorted(t for t in final_allowed if "$$ExternalSynthetic" in t),
        d8OverlayDexSha256=sha(overlay_dex / "classes.dex"), scopeDeclarationSha256=sha(scope),
        payload=dict(name=PARTITION, bytes=output.stat().st_size, sha256=sha(output)),
        compileOnlyClassesPackaged=False, sdkOrDependenciesPackaged=False, testsOrFixturesPackaged=False,
        productiveSourcesChanged=False, runtimeIdentityBuilt=False, apkAssembled=False, signed=False,
        installed=False, physicalGameplayValidated=False, productionAccess=False)
    (a.out / "dex-compilation.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=True, partition=PARTITION, sha256=sha(output), originalClasses=606,
        finalClasses=len(final), unchangedClasses=582, addedTypes=len(receipt["addedTypes"]),
        removedTypes=len(receipt["removedTypes"]), restoredInitializerArrays=receipt["restoredInitializerArrays"],
        apkAssembled=False, installed=False)))


if __name__ == "__main__":
    main()
