"""Build the two scoped R162 N64 online VideoExt DEXes from exact R161."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

from patch_bridge import STATION, INTERFACE, patch as patch_bridge


APK_SHA256 = "66f429d47af725a6767064c3623ee10c505171a85fbc8c0a50dc9e5bc4f80081"
SCHEMA = "station.n64.online-video-extension.r162.v1"
SCOPE_SCHEMA = "station.n64.online-video-extension.scoped-types.r162.v1"
PARTITIONS = {
    "classes35.dex": {
        "sha256": "59db81435a197d9e33ce20822a6bf86f2a6746e98998cdf721dff9eeafcd97bf",
        "paths": {STATION: lambda source: patch_bridge(STATION, source)},
    },
    "classes36.dex": {
        "sha256": "6e0f7116d156518fad1e65e72f4c204cfacfd9904c4ee2c3110395d56842d707",
        "paths": {INTERFACE: lambda source: patch_bridge(INTERFACE, source)},
    },
}
HELPER_HASHES = {
    "DecodeDolphinPartition.java": "d1365cf8cce05fb08c6e04dbcc47e9b154af268637bf0d768c32f851420c2b67",
    "VerifyScopedPartition.java": "2280ceb8104df843f35f81cb21e3371749db48f63dc6b6229adea0d316ee823b",
    "AssembleScopedPartition.java": "5ea794aad4cb177080e331b09d449419e352020ac61a6b9ea4194e32b4b1b022",
}


def class_type(path: Path) -> str:
    return "L" + path.as_posix().removesuffix(".smali") + ";"


SCOPES = {partition: tuple(class_type(path) for path in spec["paths"])
          for partition, spec in PARTITIONS.items()}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(command: list[str | Path], label: str, temp_dir: Path) -> None:
    environment = os.environ.copy()
    environment.update(TEMP=str(temp_dir), TMP=str(temp_dir), TMPDIR=str(temp_dir))
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                            timeout=300, env=environment)
    if result.returncode:
        raise RuntimeError(label + " failed:\n" + (result.stdout + result.stderr)[-3000:])


def files(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*.smali")}


def scoped_verifier(source: bytes) -> bytes:
    text = source.decode("utf-8")
    allowed = sorted({name for names in SCOPES.values() for name in names})
    type_check = "(" + " || ".join('type.equals("' + name + '")' for name in allowed) + ")"
    by_partition = "\n            ".join(
        'case "' + partition + '" -> Set.of(' +
        ", ".join('"' + name + '"' for name in SCOPES[partition]) + ');'
        for partition in PARTITIONS)
    replacements = {
        'station.snes-multitap-unique-flag.scoped-types.r143.v1': SCOPE_SCHEMA,
        'type.matches("Lorg/emulationstation/frontend/[A-Za-z0-9_/$]+;")': type_check,
        'case "classes35.dex" -> Set.of("Lorg/emulationstation/frontend/netplay/StationRetroLaunch;");':
            by_partition,
        'Set<String> existingRoots=Set.of("Lorg/emulationstation/frontend/netplay/StationRetroLaunch;");':
            'Set<String> existingRoots=expected;',
    }
    for before, after in replacements.items():
        if text.count(before) != 1:
            raise ValueError("Pinned scoped verifier structure changed: " + before[:60])
        text = text.replace(before, after, 1)
    return text.encode("utf-8")


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
        raise ValueError("Exact signed R161 APK required")
    with zipfile.ZipFile(args.apk) as archive:
        for partition, spec in PARTITIONS.items():
            if sha(archive.read(partition)) != spec["sha256"]:
                raise ValueError("Unexpected R161 " + partition)

    helper_dir = Path(__file__).resolve().parents[3] / (
        "integration/snes-multitap-unique-flag-r143-20261013-final2/recipe")
    sources = {name: (helper_dir / name).read_bytes() for name in HELPER_HASHES}
    for name, content in sources.items():
        if sha(content) != HELPER_HASHES[name]:
            raise ValueError("Pinned DEX helper changed: " + name)
    sources["VerifyScopedPartition.java"] = scoped_verifier(sources["VerifyScopedPartition.java"])

    java = args.jdk / "bin/java.exe"
    javac = args.jdk / "bin/javac.exe"
    if not all(path.is_file() for path in (java, javac, args.apktool)):
        raise FileNotFoundError("Pinned Java/apktool tool missing")
    out.mkdir(parents=True)
    temp_dir = out / "tmp"
    temp_dir.mkdir()
    tools = out / "tools"
    tools.mkdir()
    for name, content in sources.items():
        (tools / name).write_bytes(content)
    run([javac, "-encoding", "UTF-8", "--release", "17", "-cp", args.apktool,
         "-d", tools, *(tools / name for name in HELPER_HASHES)], "compile DEX tools", temp_dir)
    classpath = str(tools) + ";" + str(args.apktool)
    receipt = {
        "schema": SCHEMA,
        "passed": True,
        "donorApkSha256": APK_SHA256,
        "partitions": {},
        "newThreadsOrPolling": False,
        "offlineGateBroadened": False,
        "serviceOwnerValidationRelaxed": False,
        "taskRemovalChanged": False,
        "inputDelayChanged": False,
        "isolatedBridgeSelection": True,
        "videoOverrideFailClosed": True,
        "apkBuilt": False,
        "phoneInstalled": False,
        "gameplayValidated": False,
    }

    for partition, spec in PARTITIONS.items():
        base = out / partition.removesuffix(".dex")
        decoded = base.with_name(base.name + "-donor-smali")
        run([java, "-cp", classpath, "DecodeDolphinPartition", args.apk,
             partition, spec["sha256"], decoded], "decode " + partition, temp_dir)
        original = files(decoded)
        original_sources = {}
        for owner, patch in spec["paths"].items():
            owner_path = decoded / owner
            source = owner_path.read_bytes()
            original_sources[owner.as_posix()] = sha(source)
            owner_path.write_bytes(patch(source))
        patched = files(decoded)
        changed = [name for name in original if original[name] != patched.get(name)]
        allowed_paths = {path.as_posix() for path in spec["paths"]}
        if set(changed) != allowed_paths or len(patched) != len(original):
            raise ValueError("DEX source scope expanded: " + partition)

        scope = base.with_name(base.name + "-scope.properties")
        scope.write_text("\n".join((
            "schema=" + SCOPE_SCHEMA,
            "partition=" + partition,
            "donorSha256=" + spec["sha256"],
            "families=" + "|".join(SCOPES[partition]),
            "originalAllowed=" + "|".join(SCOPES[partition]),
            "finalAllowed=" + "|".join(SCOPES[partition]),
        )) + "\n", encoding="utf-8")
        candidate = out / ("candidate-" + partition)
        run([java, "-cp", classpath, "AssembleScopedPartition", args.apk,
             partition, spec["sha256"], decoded, candidate, scope],
            "assemble scoped " + partition, temp_dir)
        candidate_bytes = candidate.read_bytes()
        fixture = base.with_name(base.name + "-candidate.zip")
        with zipfile.ZipFile(fixture, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr(partition, candidate_bytes)
        compiled = base.with_name(base.name + "-compiled-smali")
        run([java, "-cp", classpath, "DecodeDolphinPartition", fixture,
             partition, sha(candidate_bytes), compiled], "decode compiled " + partition, temp_dir)
        rebuilt = files(compiled)
        if rebuilt.keys() != original.keys():
            raise ValueError("Compiled DEX class set changed: " + partition)
        unrelated = [name for name in original if name not in allowed_paths
                     and original[name] != rebuilt[name]]
        if unrelated:
            raise ValueError("Unrelated compiled classes changed: " + str(unrelated[:8]))
        owners = {name: rebuilt[name] for name in allowed_paths}
        if partition == "classes35.dex":
            owner = owners[STATION.as_posix()]
            if (b"bridgeName()Ljava/lang/String;" not in owner or
                    b"videoOverrideReady()Z" not in owner or
                    b"stationVideoOverrideReady" not in owner):
                raise ValueError("Compiled R162 StationN64Bridge contract missing")
        else:
            owner = owners[INTERFACE.as_posix()]
            if (b"bridgeName()Ljava/lang/String;" not in owner or
                    b"videoOverrideReady()Z" not in owner or
                    b"const/16 p1, 0xc" not in owner):
                raise ValueError("Compiled R162 CoreInterface contract missing")
        receipt["partitions"][partition] = {
            "owners": SCOPES[partition],
            "donorDexSha256": spec["sha256"],
            "candidateDexSha256": sha(candidate_bytes),
            "classCount": len(original),
            "unrelatedClassesUnchanged": len(original) - len(allowed_paths),
            "sourceClassSha256": original_sources,
            "patchedClassSha256": {name: sha(patched[name]) for name in allowed_paths},
            "compiledClassSha256": {name: sha(owners[name]) for name in allowed_paths},
        }
        for temporary in (decoded, compiled):
            if temporary.resolve().parent != out or not temporary.is_dir():
                raise ValueError("Unsafe temporary cleanup target")
            shutil.rmtree(temporary)
        for temporary in (fixture, scope):
            if temporary.resolve().parent != out:
                raise ValueError("Unsafe temporary cleanup target")
            temporary.unlink()

    (out / "dex-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if tools.resolve().parent != out:
        raise ValueError("Unsafe temporary cleanup target")
    shutil.rmtree(tools)
    if temp_dir.resolve().parent != out:
        raise ValueError("Unsafe temporary cleanup target")
    shutil.rmtree(temp_dir)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
