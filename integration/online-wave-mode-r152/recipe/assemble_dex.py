"""Merge only four R152 visual owner families into the exact R151 DEX partitions."""

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
PARTITIONS = {
    "classes28.dex": {
        "sha": "a93a7257257cdd36841c6b8990b957a756ee3635f39a47881ba09c5b08d080bf",
        "families": ("Lorg/emulationstation/frontend/station/StationGraphicsPanel;",
                     "Lorg/emulationstation/frontend/station/StationGraphicsPreferences;"),
        "d8": "d8-28",
    },
    "classes35.dex": {
        "sha": "ede5309d31dd44910d4e5b841604ab5fe3e1129ba693d7ee490ad0974047efbc",
        "families": ("Lorg/emulationstation/frontend/netplay/StationHyperspaceView;",
                     "Lorg/emulationstation/frontend/netplay/StationRoomsActivity;"),
        "d8": "d8-35",
    },
}
APK_SHA = "c6090d6fc31dea07cdc6b6494acf4af39835ef9ec38ad1dbcdf7ebdba9b4eda5"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def belongs(name: str, families: tuple[str, ...]) -> bool:
    return any(name == family or name.startswith(family[:-1] + "$") for family in families)


def types(folder: Path) -> dict[str, Path]:
    return {"L" + path.relative_to(folder).as_posix()[:-6] + ";": path
            for path in folder.rglob("*.smali")}


def method(text: str, signature: str) -> str:
    needle = ".method " + signature
    if text.count(needle) != 1:
        raise ValueError("Expected one scoped method: " + signature)
    start = text.index(needle)
    end = text.index(".end method", start) + len(".end method")
    return text[start:end]


def fixture(path: Path, partition: str, raw: bytes) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr(partition, raw)


def run(command: list[str | Path], out: Path, label: str) -> str:
    environment = {**os.environ, "TEMP": str(out / "temp"), "TMP": str(out / "temp")}
    process = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                             encoding="utf-8", errors="replace", env=environment, timeout=1800)
    (out / (label + ".log")).write_text(process.stdout + process.stderr, "utf-8")
    if process.returncode:
        raise ValueError(label + " failed; inspect isolated log")
    return process.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--d8-root", type=Path, required=True)
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--apktool", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    if sha(args.apk) != APK_SHA:
        raise ValueError("Exact signed R151 APK required")
    java_receipt_path = args.d8_root / "java-receipt.json"
    java_receipt = json.loads(java_receipt_path.read_text("utf-8"))
    if java_receipt.get("schema") != "station.r152.visual.java.v1" or java_receipt.get("passed") is not True:
        raise ValueError("Scoped R152 Java compile receipt required")
    for spec in PARTITIONS.values():
        if java_receipt.get("overlayDexSha256", {}).get(spec["d8"]) != sha(args.d8_root / spec["d8"] / "classes.dex"):
            raise ValueError("Compiled D8 overlay differs")
    java, javac = args.jdk / "bin/java.exe", args.jdk / "bin/javac.exe"
    if not all(path.is_file() for path in (java, javac, args.apktool)):
        raise ValueError("Pinned Java tools missing")
    with zipfile.ZipFile(args.apk) as archive:
        for partition, spec in PARTITIONS.items():
            if digest(archive.read(partition)) != spec["sha"]:
                raise ValueError("R151 DEX differs: " + partition)
    out.mkdir(parents=True)
    (out / "temp").mkdir()
    helpers = out / "helpers"
    helpers.mkdir()
    run([javac, "--release", "17", "-cp", args.apktool, "-d", helpers,
         HERE / "DecodeDolphinPartition.java", HERE / "VerifyScopedPartition.java",
         HERE / "AssembleScopedPartition.java"], out, "helpers")
    helper_cp = os.pathsep.join((str(helpers), str(args.apktool)))
    proofs = {}
    for partition, spec in PARTITIONS.items():
        short = partition[:-4]
        root = out / short
        root.mkdir()
        donor = root / "donor"
        run([java, "-cp", helper_cp, "DecodeDolphinPartition", args.apk, partition,
             spec["sha"], donor], out, short + "-donor-decode")
        overlay_raw = (args.d8_root / spec["d8"] / "classes.dex").read_bytes()
        overlay_zip = root / "overlay.zip"
        fixture(overlay_zip, "classes.dex", overlay_raw)
        overlay = root / "overlay"
        run([java, "-cp", helper_cp, "DecodeDolphinPartition", overlay_zip,
             "classes.dex", digest(overlay_raw), overlay], out, short + "-overlay-decode")
        old_types, new_types = types(donor), types(overlay)
        families = spec["families"]
        original_allowed = {name for name in old_types if belongs(name, families)}
        final_allowed = original_allowed
        if not set(families) <= original_allowed or not set(families) <= final_allowed or not all(belongs(name, families) for name in new_types):
            raise ValueError("Overlay family scope differs: " + partition)
        working = root / "working"
        shutil.copytree(donor, working)
        if partition == "classes35.dex":
            changes = (
                ("Lorg/emulationstation/frontend/netplay/StationRoomsActivity;", "private applyGraphics()V"),
                ("Lorg/emulationstation/frontend/netplay/StationHyperspaceView;", "private allowed()Z"),
            )
        else:
            changes = (
                ("Lorg/emulationstation/frontend/station/StationGraphicsPreferences;", "private static sanitizeMode(I)I"),
                ("Lorg/emulationstation/frontend/station/StationGraphicsPanel$Content;", "constructor <init>(Landroid/app/Activity;Ljava/lang/Runnable;)V"),
                ("Lorg/emulationstation/frontend/station/StationGraphicsPanel$Content;", "private render(Lorg/emulationstation/frontend/station/StationGraphicsPreferences$State;)V"),
                ("Lorg/emulationstation/frontend/station/StationGraphicsPanel$Content;", "synthetic lambda$new$3$org-emulationstation-frontend-station-StationGraphicsPanel$Content(Landroid/widget/RadioGroup;I)V"),
            )
        for name, signature in changes:
                target = working / (name[1:-1] + ".smali")
                before = target.read_text("utf-8")
                updated = before.replace(method(before, signature), method(new_types[name].read_text("utf-8"), signature))
                if updated == before:
                    raise ValueError("Scoped method did not change: " + signature)
                target.write_text(updated, "utf-8", newline="")
        if partition == "classes28.dex":
            name = "Lorg/emulationstation/frontend/station/StationGraphicsPreferences;"
            target = working / (name[1:-1] + ".smali")
            before = target.read_text("utf-8")
            field = ".field public static final ONLINE_WAVES:I = 0x3\n"
            if field in before or field not in new_types[name].read_text("utf-8"):
                raise ValueError("New mode field differs")
            target.write_text(before.replace(".field public static final OFF:I = 0x2\n",
                                             ".field public static final OFF:I = 0x2\n" + field), "utf-8", newline="")
        scope = root / "scope.properties"
        scope.write_text("\n".join((
            "schema=station.visual.scoped-types.r152.v1",
            "partition=" + partition,
            "donorSha256=" + spec["sha"],
            "families=" + "|".join(sorted(families)),
            "originalAllowed=" + "|".join(sorted(original_allowed)),
            "finalAllowed=" + "|".join(sorted(final_allowed)),
        )) + "\n", "utf-8")
        run([java, "-cp", helper_cp, "VerifyScopedPartition", args.apk, partition,
             spec["sha"], working, scope], out, short + "-verify-source")
        product = out / partition
        run([java, "-cp", helper_cp, "AssembleScopedPartition", args.apk, partition,
             spec["sha"], working, product, scope], out, short + "-assemble")
        final_zip = root / "final.zip"
        fixture(final_zip, partition, product.read_bytes())
        final = root / "final"
        run([java, "-cp", helper_cp, "DecodeDolphinPartition", final_zip, partition,
             sha(product), final], out, short + "-final-decode")
        run([java, "-cp", helper_cp, "VerifyScopedPartition", args.apk, partition,
             spec["sha"], final, scope], out, short + "-verify-final")
        final_types = types(final)
        for name, original_path in old_types.items():
            original_text = original_path.read_text("utf-8")
            final_text = final_types[name].read_text("utf-8")
            for changed_name, signature in changes:
                if name == changed_name:
                    final_text = final_text.replace(method(final_text, signature), method(original_text, signature))
            if partition == "classes28.dex" and name == "Lorg/emulationstation/frontend/station/StationGraphicsPreferences;":
                final_text = final_text.replace(".field public static final ONLINE_WAVES:I = 0x3\n\n", "")
            if final_text != original_text:
                raise ValueError("Unrelated visual method/class changed: " + name)
        proofs[partition] = {
            "inputSha256": spec["sha"], "outputSha256": sha(product),
            "originalFamilies": len(original_allowed), "finalFamilies": len(final_allowed),
            "unrelatedClassProjectionsIdentical": True,
            "changedMethods": [signature for _, signature in changes],
        }
    receipt = {"schema": "station.r152.online-wave-mode.dex.v1", "passed": True,
               "javaReceiptSha256": sha(java_receipt_path),
               "baseApkSha256": APK_SHA, "partitions": proofs, "installed": False}
    (out / "dex-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", "utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
