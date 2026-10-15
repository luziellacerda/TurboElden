"""Build only R165 classes35.dex from the exact signed R164 APK.

The single permitted class delta is StationHumanDeparture.  This recipe never
assembles an APK, signs, contacts a server, or touches a phone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parents[1]
PARTITION = "classes35.dex"
OWNER = "org/emulationstation/frontend/netplay/StationHumanDeparture.smali"
CALLER = "org/emulationstation/frontend/netplay/StationGameSession.smali"
TYPE = "Lorg/emulationstation/frontend/netplay/StationHumanDeparture;"
SOURCE = ROOT / "java" / OWNER.replace(".smali", ".java")
SOURCE_SHA = "36db43e618eddca9167ecc1c835a42dfc64b8a5b126ec3e724d463e21e96cd5e"
DONOR_SHA = "903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210"
DONOR_BYTES = 2_715_466_850
DEX_SHA = "0489cd99a51d43d001cab4ef5374e03aea694b58f6cc72648e7217f363d79b52"
ENTRY_COUNT = 13_861
SCHEMA = "station.n64.host-exit.dex.r165.v1"
SCOPE_SCHEMA = "station.n64.host-exit.scope.r165.v1"
BASE_RECIPE = REPO / "integration/online-lifecycle-review-r135/recipe"
PINS = {
    "java": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "javac": "9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549",
    "android": "6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad",
    "d8": "305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5",
    "apktool": "dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",
    "rooms": "6b2929eb3621b208593a886b6f06a32de52af9c931663cb314e197af155f773d",
    "client": "011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313",
}
HELPERS = {
    "DecodeDolphinPartition.java": "d1365cf8cce05fb08c6e04dbcc47e9b154af268637bf0d768c32f851420c2b67",
    "VerifyScopedPartition.java": "6ff4b2e97e17e3ef83411df29e60b9b0ad42c7ae9e9fdfddfdfc9ea5f24a54bc",
    "AssembleScopedPartition.java": "5ea794aad4cb177080e331b09d449419e352020ac61a6b9ea4194e32b4b1b022",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def files(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): sha(path) for path in root.rglob("*.smali")}


def command(parts: list[object], label: str, out: Path) -> str:
    env = {**os.environ, "TMP": str(out / "temp"), "TEMP": str(out / "temp"),
           "JAVA_TOOL_OPTIONS": '-Djava.io.tmpdir="' + str(out / "temp") + '" -XX:-UsePerfData',
           "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(list(map(str, parts)), capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=300, env=env)
    (out / (label + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    need(result.returncode == 0, label + " failed; see isolated log")
    if label == "d8":
        need(not re.search(r"(?im)^\s*(warning|error)\b", result.stdout + result.stderr),
             "D8 diagnostic requires review")
    return result.stdout.strip()


def scoped_verifier(raw: bytes) -> bytes:
    text = raw.decode("utf-8")
    before = "station.online-lifecycle.scoped-types.r135.v1"
    need(text.count(before) == 1, "R135 scope schema changed")
    text = text.replace(before, SCOPE_SCHEMA, 1)
    start = "        Set<String> expected=switch (partition) {"
    stop = "        for (String type : scope.originalAllowed)"
    need(text.count(start) == text.count(stop) == 1, "R135 scoped verifier structure changed")
    first, rest = text.split(start, 1)
    _, last = rest.split(stop, 1)
    constrained = (
        '        Set<String> expected=Set.of("' + TYPE + '");\n'
        '        if (!"classes35.dex".equals(partition) || !families.equals(expected))\n'
        '            throw new IllegalStateException("R165 single-class scope");\n'
        '        Scope scope=new Scope(partition,checksum,families,\n'
        '            list(properties.getProperty("originalAllowed")),\n'
        '            list(properties.getProperty("finalAllowed")));\n'
        '        if (!scope.originalAllowed.equals(expected) || !scope.finalAllowed.equals(expected))\n'
        '            throw new IllegalStateException("R165 class scope expansion");\n'
    )
    return (first + constrained + stop + last).encode("utf-8")


def check_inputs(args: argparse.Namespace) -> dict[str, Path]:
    need(args.out.resolve() != REPO and not args.out.resolve().is_relative_to(REPO),
         "Output cannot be inside source tree")
    need(not args.out.exists() or args.out.is_dir() and not any(args.out.iterdir()),
         "New or empty output directory required")
    need(args.donor.is_file() and args.donor.stat().st_size == DONOR_BYTES and
         sha(args.donor) == DONOR_SHA, "Exact signed R164 donor required")
    need(SOURCE.is_file() and sha(SOURCE) == SOURCE_SHA, "Final reviewed R165 source required")
    inputs = {"java": args.jdk_bin / "java.exe", "javac": args.jdk_bin / "javac.exe",
              "android": args.android_jar, "d8": args.d8_jar,
              "apktool": args.apktool, "rooms": args.rooms_jar, "client": args.client_jar}
    for name, path in inputs.items():
        need(path.is_file() and sha(path) == PINS[name], "Pinned input differs: " + name)
    for name, expected in HELPERS.items():
        need(sha(BASE_RECIPE / name) == expected, "Pinned scoped assembler differs: " + name)
    with zipfile.ZipFile(args.donor) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == ENTRY_COUNT, "R164 ZIP entry set differs")
        dexes = {name for name in names if re.fullmatch(r"classes(?:\d+)?\.dex", name)}
        need(dexes == {"classes.dex", *(f"classes{i}.dex" for i in range(2, 41))},
             "Exactly forty R164 DEX partitions required")
        need(digest(archive.read(PARTITION)) == DEX_SHA, "R164 DEX35 identity differs")
    return inputs


def commit_matches(revision: str) -> None:
    need(bool(re.fullmatch(r"[0-9a-f]{40}", revision)), "Frozen 40-character source commit required")
    targets = [SOURCE, Path(__file__).resolve()]
    for path in targets:
        relative = path.relative_to(REPO).as_posix()
        raw = subprocess.check_output(["git", "-C", str(REPO), "show", revision + ":" + relative])
        need(digest(raw) == sha(path), "Source differs from frozen commit: " + relative)


def safe_remove(path: Path, out: Path) -> None:
    need(path.resolve().parent == out.resolve() and path.is_dir() and not path.is_symlink(),
         "Unsafe temporary cleanup target")
    shutil.rmtree(path)


def build(args: argparse.Namespace) -> dict:
    inputs = check_inputs(args)
    if args.check_inputs_only:
        return {"passed": True, "compiled": False, "donorApkSha256": DONOR_SHA,
                "donorDexSha256": DEX_SHA, "singleAllowedType": TYPE}
    commit_matches(args.source_commit)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "temp").mkdir()
    tools = out / "tools"
    tools.mkdir()
    for name in HELPERS:
        raw = (BASE_RECIPE / name).read_bytes()
        if name == "VerifyScopedPartition.java":
            raw = scoped_verifier(raw)
        (tools / name).write_bytes(raw)
    java, javac = inputs["java"], inputs["javac"]
    command([javac, "--release", "17", "-encoding", "UTF-8", "-cp", inputs["apktool"],
             "-d", tools, *(tools / name for name in HELPERS)], "compile-scoped-tools", out)
    cp = str(tools) + os.pathsep + str(inputs["apktool"])
    compiled = out / "java-classes"
    compiled.mkdir()
    production_cp = os.pathsep.join(str(inputs[name]) for name in ("android", "rooms", "client"))
    command([javac, "--release", "8", "-encoding", "UTF-8", "-proc:none", "-sourcepath", "",
             "-cp", production_cp, "-d", compiled, SOURCE], "compile-reviewed-source", out)
    class_files = list(compiled.rglob("*.class"))
    need(len(class_files) == 1 and class_files[0].relative_to(compiled).as_posix() == OWNER.replace(".smali", ".class") and
         class_files[0].read_bytes()[6:8] == b"\x004", "Only one Java 8 productive class allowed")
    overlay = out / "overlay"
    overlay.mkdir()
    command([java, "-cp", inputs["d8"], "com.android.tools.r8.D8", "--release", "--min-api", "28",
             "--lib", inputs["android"], "--classpath", inputs["rooms"], "--classpath", inputs["client"],
             "--output", overlay, class_files[0]], "d8", out)
    overlay_dex = overlay / "classes.dex"
    need(overlay_dex.is_file() and list(overlay.iterdir()) == [overlay_dex],
         "D8 emitted an extra class or partition")
    overlay_zip = out / "overlay.zip"
    with zipfile.ZipFile(overlay_zip, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr("classes.dex", overlay_dex.read_bytes())
    overlay_smali = out / "overlay-smali"
    command([java, "-cp", cp, "DecodeDolphinPartition", overlay_zip, "classes.dex",
             sha(overlay_dex), overlay_smali], "decode-overlay", out)
    overlay_files = files(overlay_smali)
    need(set(overlay_files) == {OWNER}, "D8 program must contain only StationHumanDeparture")
    donor = out / "donor-smali"
    command([java, "-cp", cp, "DecodeDolphinPartition", args.donor, PARTITION, DEX_SHA, donor],
            "decode-donor", out)
    original = files(donor)
    need(OWNER in original and CALLER in original and len(original) > 1,
         "R164 event-4 caller or departure class missing")
    caller = (donor / CALLER).read_bytes()
    call = (b"invoke-static {v1, v2, v3}, "
            b"Lorg/emulationstation/frontend/netplay/StationHumanDeparture;->leave("
            b"Lorg/emulationstation/frontend/netplay/StationOnlineClient;"
            b"Lorg/json/JSONObject;"
            b"Lorg/emulationstation/frontend/station/StationApi$Cancellation;)V")
    event = caller.split(b".method private declared-synchronized event(ILandroid/os/Bundle;)V", 1)
    lambda_event = caller.split(b".method synthetic lambda$event$0$org-emulationstation-frontend-netplay-StationGameSession()V", 1)
    need(len(event) == len(lambda_event) == 2 and
         b"const/4 v0, 0x4" in event[1].split(b".end method", 1)[0] and
         b"if-ne p1, v0" in event[1].split(b".end method", 1)[0] and
         b"StationGameSession$$ExternalSyntheticLambda0" in event[1].split(b".end method", 1)[0] and
         lambda_event[1].split(b".end method", 1)[0].count(call) == 1 and
         sum(path.read_bytes().count(call) for path in donor.rglob("*.smali")) == 1,
         "R164 human event 4 must already invoke the exact helper once")
    old_source = (donor / OWNER).read_bytes()
    new_source = (overlay_smali / OWNER).read_bytes()
    need(old_source != new_source and b"leave(Lorg/emulationstation/frontend/netplay/StationOnlineClient;" in old_source and
         b"leave(Lorg/emulationstation/frontend/netplay/StationOnlineClient;" in new_source,
         "Event-4 departure method missing or unchanged")
    (donor / OWNER).write_bytes(new_source)
    need({name for name, checksum in files(donor).items() if checksum != original[name]} == {OWNER},
         "Smali source delta expanded")
    scope = out / "scope.properties"
    scope.write_text("\n".join(("schema=" + SCOPE_SCHEMA, "partition=" + PARTITION,
                                "donorSha256=" + DEX_SHA, "families=" + TYPE,
                                "originalAllowed=" + TYPE, "finalAllowed=" + TYPE)) + "\n", encoding="utf-8")
    command([java, "-cp", cp, "VerifyScopedPartition", args.donor, PARTITION, DEX_SHA,
             donor, scope], "verify-source-scope", out)
    candidate = out / PARTITION
    command([java, "-cp", cp, "AssembleScopedPartition", args.donor, PARTITION, DEX_SHA,
             donor, candidate, scope], "assemble", out)
    candidate_zip = out / "candidate.zip"
    with zipfile.ZipFile(candidate_zip, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(PARTITION, candidate.read_bytes())
    final = out / "final-smali"
    command([java, "-cp", cp, "DecodeDolphinPartition", candidate_zip, PARTITION,
             sha(candidate), final], "decode-final", out)
    command([java, "-cp", cp, "VerifyScopedPartition", args.donor, PARTITION, DEX_SHA,
             final, scope], "verify-final-scope", out)
    final_files = files(final)
    need(set(final_files) == set(original) and
         all(final_files[name] == original[name] for name in original if name != OWNER) and
         final_files[OWNER] == overlay_files[OWNER] and
         (final / CALLER).read_bytes() == caller,
         "Compiled class projections or event-4 caller differ")
    need(sha(SOURCE) == SOURCE_SHA and sha(args.donor) == DONOR_SHA, "Source or donor changed during build")
    commit_matches(args.source_commit)
    for name, path in inputs.items():
        need(sha(path) == PINS[name], "Build input changed: " + name)
    preserved = {name: checksum for name, checksum in original.items() if name != OWNER}
    receipt = {"schema": SCHEMA, "passed": True, "donorApkSha256": DONOR_SHA,
               "donorDexSha256": DEX_SHA, "candidateDexSha256": sha(candidate),
               "sourceCommit": args.source_commit, "sourceSha256": SOURCE_SHA,
               "inputSha256": PINS, "helperSha256": HELPERS,
               "partition": PARTITION, "classCount": len(original),
               "allowedType": TYPE, "modifiedTypes": [TYPE], "addedTypes": [], "removedTypes": [],
               "unrelatedClassesUnchanged": len(preserved),
               "unrelatedProjectionSha256": digest(json.dumps(preserved, sort_keys=True).encode("ascii")),
               "originalOwnerProjectionSha256": original[OWNER],
               "candidateOwnerProjectionSha256": final_files[OWNER],
               "event4CallerProjectionSha256": original[CALLER],
               "event4CallerPreserved": True, "event4HelperCallCount": 1,
               "scopeSha256": sha(scope), "java8ClassSha256": sha(class_files[0]),
               "d8OverlaySha256": sha(overlay_dex), "minimumAndroidApi": 28,
               "changedDexPartitions": [PARTITION], "newThreadsTimersOrPolling": False,
               "apkAssembled": False, "signed": False, "installed": False,
               "serverRegistered": False, "physicalGameplayValidated": False}
    (out / "dex-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for temporary in (donor, final, overlay_smali, tools, compiled, overlay, out / "temp"):
        safe_remove(temporary, out)
    for temporary in (overlay_zip, candidate_zip, scope):
        need(temporary.resolve().parent == out and temporary.is_file(), "Unsafe temporary file cleanup")
        temporary.unlink()
    return {"passed": True, "candidateDexSha256": receipt["candidateDexSha256"],
            "classCount": receipt["classCount"],
            "unrelatedClassesUnchanged": receipt["unrelatedClassesUnchanged"],
            "apkAssembled": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("donor", "jdk-bin", "android-jar", "d8-jar", "apktool", "rooms-jar", "client-jar", "out"):
        parser.add_argument("--" + field, required=True, type=Path)
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--check-inputs-only", action="store_true")
    print(json.dumps(build(parser.parse_args()), sort_keys=True))
