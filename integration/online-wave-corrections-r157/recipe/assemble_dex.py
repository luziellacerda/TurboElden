"""Replace only StationHyperspaceView in exact R156 classes35.dex."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile


HERE = Path(__file__).resolve().parent
APK_SHA = "a072af70c04f0b9f9455b22a856bcdf0995b42da5650c2f9ee87243d17f5d5a6"
PARTITION = "classes35.dex"
DEX_SHA = "5196b3c63438675edce68b3d27cdbd84e3ff44010ff7aa19e1f1a233ea30f3fb"
VIEW = "Lorg/emulationstation/frontend/netplay/StationHyperspaceView;"
SCHEMA = "station.visual.scoped-types.r157.v1"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def types(folder: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in folder.rglob("*.smali"):
        name = "L" + path.relative_to(folder).as_posix()[:-6] + ";"
        if name in result:
            raise ValueError("Duplicate decoded class: " + name)
        result[name] = path
    return result


def belongs(name: str) -> bool:
    return name == VIEW or name.startswith(VIEW[:-1] + "$")


def run(command: list[str | Path], out: Path, label: str) -> None:
    environment = {**os.environ, "TEMP": str(out / "temp"), "TMP": str(out / "temp")}
    process = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                             encoding="utf-8", errors="replace", env=environment, timeout=1800)
    (out / (label + ".log")).write_text(process.stdout + process.stderr, "utf-8")
    if process.returncode:
        raise ValueError(label + " failed; inspect isolated log")


def fixture(path: Path, partition: str, raw: bytes) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(partition, raw)


def require_view_abi(smali: str) -> None:
    required = (
        "<init>(Landroid/content/Context;)V",
        "setResumed(Z)V",
        "onGraphicsChanged(Lorg/emulationstation/frontend/station/StationGraphicsPreferences$State;)V",
    )
    for signature in required:
        if smali.count(signature) < 1:
            raise ValueError("Required online View ABI missing: " + signature)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--java-root", type=Path, required=True)
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--apktool", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    if sha(args.apk) != APK_SHA:
        raise ValueError("Exact signed R156 APK required")
    receipt_path = args.java_root / "java-receipt.json"
    java_receipt = json.loads(receipt_path.read_text("utf-8"))
    overlay_dex = args.java_root / "d8/classes.dex"
    if (java_receipt.get("schema") != "station.r157.online-wave.java.v1" or
            java_receipt.get("passed") is not True or
            java_receipt.get("overlayDexSha256") != sha(overlay_dex)):
        raise ValueError("Scoped R157 Java overlay differs")
    java, javac = args.jdk / "bin/java.exe", args.jdk / "bin/javac.exe"
    if not all(path.is_file() for path in (java, javac, args.apktool)):
        raise ValueError("Pinned Java/apktool tools missing")
    with zipfile.ZipFile(args.apk) as archive:
        raw_dex = archive.read(PARTITION)
    if digest(raw_dex) != DEX_SHA:
        raise ValueError("R156 online DEX differs")

    out.mkdir(parents=True)
    (out / "temp").mkdir()
    helpers = out / "helpers"
    helpers.mkdir()
    run([javac, "--release", "17", "-cp", args.apktool, "-d", helpers,
         HERE / "DecodeDolphinPartition.java", HERE / "VerifyScopedPartition.java",
         HERE / "AssembleScopedPartition.java"], out, "helpers")
    helper_cp = os.pathsep.join((str(helpers), str(args.apktool)))

    donor = out / "donor"
    run([java, "-cp", helper_cp, "DecodeDolphinPartition", args.apk, PARTITION, DEX_SHA,
         donor], out, "donor-decode")
    overlay_zip = out / "overlay.zip"
    fixture(overlay_zip, "classes.dex", overlay_dex.read_bytes())
    overlay = out / "overlay"
    run([java, "-cp", helper_cp, "DecodeDolphinPartition", overlay_zip, "classes.dex",
         sha(overlay_dex), overlay], out, "overlay-decode")
    original_types, overlay_types = types(donor), types(overlay)
    original_family = {name for name in original_types if belongs(name)}
    final_family = set(overlay_types)
    if original_family != {VIEW} or final_family != {VIEW}:
        raise ValueError("R157 overlay must change exactly the one online View class")
    require_view_abi(overlay_types[VIEW].read_text("utf-8"))
    working = out / "working"
    shutil.copytree(donor, working)
    for name in original_family:
        (working / (name[1:-1] + ".smali")).unlink()
    for name, path in overlay_types.items():
        target = working / (name[1:-1] + ".smali")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    scope = out / "scope.properties"
    scope.write_text("\n".join((
        "schema=" + SCHEMA,
        "partition=" + PARTITION,
        "donorSha256=" + DEX_SHA,
        "families=" + VIEW,
        "originalAllowed=" + "|".join(sorted(original_family)),
        "finalAllowed=" + "|".join(sorted(final_family)),
    )) + "\n", "utf-8")
    run([java, "-cp", helper_cp, "VerifyScopedPartition", args.apk, PARTITION,
         DEX_SHA, working, scope], out, "verify-source")
    product = out / PARTITION
    run([java, "-cp", helper_cp, "AssembleScopedPartition", args.apk, PARTITION,
         DEX_SHA, working, product, scope], out, "assemble")
    if sha(product) == DEX_SHA:
        raise ValueError("No online View change reached the final DEX")
    final_zip = out / "final.zip"
    fixture(final_zip, PARTITION, product.read_bytes())
    final = out / "final"
    run([java, "-cp", helper_cp, "DecodeDolphinPartition", final_zip, PARTITION,
         sha(product), final], out, "final-decode")
    run([java, "-cp", helper_cp, "VerifyScopedPartition", args.apk, PARTITION,
         DEX_SHA, final, scope], out, "verify-final")
    final_types = types(final)
    if set(final_types) != (set(original_types) - original_family | final_family):
        raise ValueError("Final DEX class set differs from scoped View family")
    unrelated = 0
    for name, original_path in original_types.items():
        if belongs(name):
            continue
        if original_path.read_bytes() != final_types[name].read_bytes():
            raise ValueError("Unrelated DEX class changed: " + name)
        unrelated += 1
    receipt = {
        "schema": "station.r157.online-wave.dex.v1",
        "passed": True,
        "baseApkSha256": APK_SHA,
        "baseDexSha256": DEX_SHA,
        "outputSha256": sha(product),
        "javaReceiptSha256": sha(receipt_path),
        "sourceSha256": java_receipt["sourceSha256"],
        "originalViewFamilyCount": len(original_family),
        "finalViewFamilyCount": len(final_family),
        "unrelatedClassCount": unrelated,
        "unrelatedClassProjectionsIdentical": True,
        "changedClassFamily": VIEW,
        "otherDexPartitionsChanged": False,
        "installed": False,
    }
    (out / "dex-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", "utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
