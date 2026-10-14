"""Build and verify the one-class N64 service owner correction on exact R158."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

from patch_smali import BRIDGE, patch


APK_SHA256 = "fc1d2d983deb5179979a4aebac7fa64b1740da1c62ae46bfc0d1f4c11eb46cf0"
DONOR_DEX_SHA256 = "e2cbccdb9af8dbeb1485c7119312875aece8660956833d22ee042b5b5306b513"
PARTITION = "classes35.dex"
OWNER = "Lorg/emulationstation/frontend/netplay/StationN64Bridge;"
SCHEMA = "station.n64.owner-application-context.r159.v2"
SCOPE_SCHEMA = "station.n64.owner-application-context.scoped-types.r159.v1"
HELPER_HASHES = {
    "DecodeDolphinPartition.java": "d1365cf8cce05fb08c6e04dbcc47e9b154af268637bf0d768c32f851420c2b67",
    "VerifyScopedPartition.java": "2280ceb8104df843f35f81cb21e3371749db48f63dc6b6229adea0d316ee823b",
    "AssembleScopedPartition.java": "5ea794aad4cb177080e331b09d449419e352020ac61a6b9ea4194e32b4b1b022",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(command: list[str | Path], label: str) -> None:
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise RuntimeError(label + " failed:\n" + (result.stdout + result.stderr)[-3000:])


def files(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*.smali")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--apktool", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    if sha_file(args.apk) != APK_SHA256:
        raise ValueError("Exact signed R158 final-v8 APK required")
    with zipfile.ZipFile(args.apk) as archive:
        donor = archive.read(PARTITION)
    if sha(donor) != DONOR_DEX_SHA256:
        raise ValueError("Unexpected R158 classes35.dex")

    helper_dir = Path(__file__).resolve().parents[3] / (
        "integration/snes-multitap-unique-flag-r143-20261013-final2/recipe")
    sources = {name: (helper_dir / name).read_bytes() for name in HELPER_HASHES}
    for name, content in sources.items():
        if sha(content) != HELPER_HASHES[name]:
            raise ValueError("Pinned DEX helper changed: " + name)

    out.mkdir(parents=True)
    tools = out / "tools"
    tools.mkdir()
    for name, content in sources.items():
        if name == "VerifyScopedPartition.java":
            source = content.decode("utf-8")
            if source.count("station.snes-multitap-unique-flag.scoped-types.r143.v1") != 1 or source.count("StationRetroLaunch;") != 2:
                raise ValueError("Pinned scoped verifier structure changed")
            source = source.replace("station.snes-multitap-unique-flag.scoped-types.r143.v1", SCOPE_SCHEMA)
            source = source.replace("StationRetroLaunch;", "StationN64Bridge;")
            content = source.encode("utf-8")
        (tools / name).write_bytes(content)
    java = args.jdk / "bin/java.exe"
    javac = args.jdk / "bin/javac.exe"
    if not all(p.is_file() for p in (java, javac, args.apktool)):
        raise FileNotFoundError("Pinned Java/apktool tool missing")
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", args.apktool,
         "-d", tools, *(tools / name for name in HELPER_HASHES)], "compile DEX tools")
    classpath = str(tools) + ";" + str(args.apktool)
    decoded = out / "donor-smali"
    run([java, "-cp", classpath, "DecodeDolphinPartition", args.apk,
         PARTITION, DONOR_DEX_SHA256, decoded], "decode donor DEX35")
    original_files = files(decoded)
    owner_path = decoded / BRIDGE
    owner_path.write_bytes(patch(owner_path.read_bytes()))
    after_patch = files(decoded)
    changed = [name for name in original_files if original_files[name] != after_patch.get(name)]
    if changed != [BRIDGE.as_posix()] or len(after_patch) != len(original_files):
        raise ValueError("DEX source scope expanded")

    scope = out / "scope.properties"
    scope.write_text("\n".join((
        "schema=" + SCOPE_SCHEMA,
        "partition=" + PARTITION,
        "donorSha256=" + DONOR_DEX_SHA256,
        "families=" + OWNER,
        "originalAllowed=" + OWNER,
        "finalAllowed=" + OWNER,
    )) + "\n", encoding="utf-8")
    candidate = out / "candidate-classes35.dex"
    run([java, "-cp", classpath, "AssembleScopedPartition", args.apk,
         PARTITION, DONOR_DEX_SHA256, decoded, candidate, scope], "assemble scoped N64 DEX")
    candidate_bytes = candidate.read_bytes()
    fixture = out / "candidate.zip"
    with zipfile.ZipFile(fixture, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(PARTITION, candidate_bytes)
    compiled = out / "candidate-smali"
    run([java, "-cp", classpath, "DecodeDolphinPartition", fixture,
         PARTITION, sha(candidate_bytes), compiled], "decode compiled N64 DEX")
    compiled_files = files(compiled)
    if compiled_files.keys() != original_files.keys():
        raise ValueError("Compiled DEX class set changed")
    unrelated_changes = [name for name in original_files if name != BRIDGE.as_posix()
                         and original_files[name] != compiled_files[name]]
    if unrelated_changes:
        raise ValueError("Unrelated compiled classes changed: " + str(unrelated_changes[:8]))
    compiled_owner = compiled_files[BRIDGE.as_posix()]
    for required in (b"getApplicationContext", b"getComponent", b"CoreService",
                     b"getPackageName", b"N64_OWNER_MISSING"):
        if required not in compiled_owner:
            raise ValueError("Compiled N64 guard missing: " + str(required))
    method_start = compiled_owner.index(b".method public static propagate")
    method_end = compiled_owner.index(b".end method", method_start)
    propagate = compiled_owner[method_start:method_end]
    if b"->closed:Z" not in propagate or propagate.index(b"->closed:Z") > propagate.index(b"getApplicationContext"):
        raise ValueError("Closed-session gate missing from ApplicationContext branch")
    receipt = {
        "schema": SCHEMA,
        "passed": True,
        "donorApkSha256": APK_SHA256,
        "partition": PARTITION,
        "donorDexSha256": DONOR_DEX_SHA256,
        "candidateDexSha256": sha(candidate_bytes),
        "owner": OWNER,
        "classCount": len(original_files),
        "unrelatedClassesUnchanged": len(original_files) - 1,
        "sourceClassSha256": sha(original_files[BRIDGE.as_posix()]),
        "patchedClassSha256": sha(after_patch[BRIDGE.as_posix()]),
        "compiledClassSha256": sha(compiled_owner),
        "newThreadsOrPolling": False,
        "offlineGateBroadened": False,
        "serviceOwnerValidationRelaxed": False,
        "apkBuilt": False,
        "phoneInstalled": False,
        "gameplayValidated": False,
    }
    (out / "dex-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for temporary in (tools, decoded, compiled):
        # All temporary targets were created immediately under this new build root.
        if temporary.resolve().parent != out or not temporary.is_dir():
            raise ValueError("Unsafe temporary cleanup target")
        shutil.rmtree(temporary)
    for temporary in (fixture, scope):
        if temporary.resolve().parent != out:
            raise ValueError("Unsafe temporary cleanup target")
        temporary.unlink()
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
