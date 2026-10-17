"""Sign only the reviewed six-entry R165 combined candidate.

The signed APK is written once at its final path. The R164 donor, private key,
package data and game content are never copied into the source repository.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
AUTHORITY = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/"
                 "reconstrucao-atual/sky-blue-waves-r145-20261013/private-tooling/sign_r141_private.py")
AUTHORITY_SHA = "7963f2df3922b0726d991947efbd155fbfdf4b94763187905e5a7e23cde2c5b0"
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
BASE_SHA = "903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210"
DEX35_SHA = "7a5c1609df4d99ac4371bd4c1b06bc31dcfeeafa616c2b61f6d90bfd5694d020"
DEX36_SHA = "a1c12b34c5eba4060707235c86dea3bbdfa59ef52264afc7ebaaa5d73231287c"
ONLINE_BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
OLD_CAROUSEL_SHA = "bd3222558a43f8998d51b0b72010ecb8a94c7ae62a14d34b39863d13737a10d0"
REPLACED = sorted((
    "assets/station-online/engines.json",
    "classes35.dex",
    "lib/arm64-v8a/libstation_dolphin_runtime.so",
    "lib/arm64-v8a/libstation_mupen64plus_runtime.so",
    "lib/arm64-v8a/libstation_psx_online.so",
    "lib/arm64-v8a/libturbo_carousel.so",
))
MANDATORY_SOURCES = {
    "integration/n64-host-exit-r165/java/org/emulationstation/frontend/netplay/StationHumanDeparture.java",
    "integration/n64-host-exit-r165/recipe/build_dex.py",
    "integration/station-combined-r165/recipe/package_candidate.py",
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def entries_match(path: Path, expected: dict[str, str]) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) != 13_861 or set(names) != set(expected):
            raise ValueError("R165 APK entry set differs")
        for name in names:
            with archive.open(name) as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != expected[name]:
                    raise ValueError("R165 APK entry content differs: " + name)


def validate_package(package: Path) -> tuple[dict, Path]:
    receipt = json.loads((package / "unsigned-package.json").read_text("utf-8"))
    expected = receipt.get("expectedEntrySha256")
    if (receipt.get("schema") != "station.combined.package.r165.v1" or
        receipt.get("passed") is not True or
        receipt.get("baselineApkSha256") != BASE_SHA or
        receipt.get("entryCount") != 13_861 or
        receipt.get("preservedEntryCount") != 13_855 or
        receipt.get("preservedDexPartitions") != 39 or
        receipt.get("changedDexPartitions") != ["classes35.dex"] or
        receipt.get("replacedEntries") != REPLACED or
        receipt.get("classes36Sha256Preserved") != DEX36_SHA or
        receipt.get("onlineAeBridgeSha256Preserved") != ONLINE_BRIDGE_SHA or
        receipt.get("retainedOwnerPolicies") is not True or
        receipt.get("newThreadsTimersOrPolling") is not False or
        receipt.get("extraPerFrameDrawCalls") != 0 or
        receipt.get("effectRoutingAudited") is not True or
        receipt.get("carouselSha256ChangedFrom") != OLD_CAROUSEL_SHA or
        receipt.get("nativeLibrarySha256") == OLD_CAROUSEL_SHA or
        not re.fullmatch(r"[0-9a-f]{64}", str(receipt.get("nativeReceiptSha256"))) or
        receipt.get("dexReceiptSha256") !=
            "dc71cc3c4a4668e4db76c31521d8a3753faf02e30a223e24ecfb9641ac1b46bc" or
        not isinstance(expected, dict) or len(expected) != 13_861 or
        expected.get("classes35.dex") != DEX35_SHA or
        expected.get("classes36.dex") != DEX36_SHA or
        expected.get("lib/arm64-v8a/libstation_ae_bridge.so") != ONLINE_BRIDGE_SHA or
        expected.get("lib/arm64-v8a/libturbo_carousel.so") != receipt.get("nativeLibrarySha256")):
        raise ValueError("Reviewed R165 six-entry unsigned package required")
    source_files = receipt.get("sourceFilesSha256")
    revision = receipt.get("sourceCommit")
    if (not isinstance(source_files, dict) or not MANDATORY_SOURCES <= set(source_files) or
        len(source_files) < 4 or not isinstance(revision, str) or
        not re.fullmatch(r"[0-9a-f]{40}", revision) or
        receipt.get("dexSourceCommit") != "68fe58dadbf33538b7ad1607c88af80a7a3fc0fe"):
        raise ValueError("Frozen R165 combined source scope differs")
    for name, checksum in source_files.items():
        relative = Path(name)
        if (relative.is_absolute() or ".." in relative.parts or
            relative.parts[0] != "integration" or not re.fullmatch(r"[0-9a-f]{64}", checksum) or
            sha(REPO / name) != checksum):
            raise ValueError("R165 source changed after package assembly: " + name)
        committed = subprocess.check_output(["git", "-C", str(REPO), "show", revision + ":" + name])
        if hashlib.sha256(committed).hexdigest() != checksum:
            raise ValueError("R165 source not frozen at package commit: " + name)
    unsigned = package / "TurboStations-Premium-R165-combined-unsigned.apk"
    if not unsigned.is_file() or sha(unsigned) != receipt.get("unsignedApkSha256") or \
       unsigned.stat().st_size != receipt.get("unsignedApkBytes"):
        raise ValueError("R165 unsigned APK changed")
    markers = receipt.get("runtimeMarkers")
    ids = receipt.get("onlineEngineIds")
    if (not isinstance(markers, dict) or set(markers) != {"psx", "n64", "dolphin"} or
        not isinstance(ids, dict) or set(ids) != {"psx", "n64", "gamecube", "wii"} or
        any(not re.fullmatch(r"[0-9a-f]{64}", str(markers[k].get("runtimeSha256")))
            for k in markers)):
        raise ValueError("R165 runtime marker inventory differs")
    prefixes = {"psx": "pcsx-rearmed-ff81ed17-player-v3-",
                "n64": "mupen64plus-ae-33bf7021-n64-v3-",
                "gamecube": "dolphin-5102a033-gamecube-v3-",
                "wii": "dolphin-5102a033-wii-v3-"}
    for platform, prefix in prefixes.items():
        marker = "dolphin" if platform in {"gamecube", "wii"} else platform
        if ids[platform] != prefix + markers[marker]["runtimeSha256"][:12]:
            raise ValueError("R165 online engine ID differs: " + platform)
    with zipfile.ZipFile(unsigned) as archive:
        rows = json.loads(archive.read("assets/station-online/engines.json"))["engines"]
    selected = [row for row in rows if row["platform"] in ids]
    if (len(rows) != 13 or len(selected) != 4 or
        len({row["platform"] for row in selected}) != 4 or
        any(row["engineId"] != ids[row["platform"]] for row in selected)):
        raise ValueError("R165 registry and package engine IDs differ")
    return receipt, unsigned


def main(package: Path, final: Path, scratch: Path) -> dict:
    package = package.resolve(strict=True)
    final = final.resolve()
    scratch = scratch.resolve(strict=True)
    if final.exists():
        raise FileExistsError(final)
    if package.is_relative_to(REPO) or final.is_relative_to(REPO):
        raise ValueError("Private APK package and final output must stay outside source Git")
    if package.anchor.lower() != final.anchor.lower():
        raise ValueError("Keep the final APK on the package volume to avoid an extra large copy")
    if not scratch.is_dir() or scratch == package or scratch.is_relative_to(REPO):
        raise ValueError("Use a separate existing scratch directory outside the repository")
    receipt, unsigned = validate_package(package)
    if sha(AUTHORITY) != AUTHORITY_SHA:
        raise ValueError("Original private signing authority differs")
    spec = importlib.util.spec_from_file_location("r165_authority", AUTHORITY)
    if spec is None or spec.loader is None:
        raise ValueError("Original private authority unavailable")
    authority = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(authority)
    if {name: sha(authority.TOOLS / name) for name in authority.TOOL_PINS} != authority.TOOL_PINS:
        raise ValueError("Pinned Android signing tools differ")
    entries_match(unsigned, receipt["expectedEntrySha256"])
    temp = package / "temp"
    if not temp.is_dir():
        raise FileNotFoundError("R165 package temporary directory missing")
    aligned = scratch / "R165-combined-aligned.apk"
    final.parent.mkdir(parents=True, exist_ok=True)
    partial = final.with_suffix(final.suffix + ".partial")
    if aligned.exists() or partial.exists():
        raise FileExistsError("Fresh R165 signing outputs required")
    needed = receipt["unsignedApkBytes"] + 256 * 1024 * 1024
    package_free = shutil.disk_usage(package).free
    scratch_free = shutil.disk_usage(scratch).free
    if package.anchor.lower() == scratch.anchor.lower():
        if package_free < 2 * needed:
            raise ValueError("Package volume lacks room for aligned and signed APKs")
    elif package_free < needed or scratch_free < needed:
        raise ValueError("Package or scratch volume lacks room for signing")
    key, values = authority.credentials()
    env_name = "STATION_R165_PRIVATE_SIGNING"
    environment = {**os.environ, "TEMP": str(temp), "TMP": str(temp),
                   env_name: values["--ks-pass"][5:]}
    java = authority.TOOLS / "jdk17/bin/java.exe"
    signer = authority.TOOLS / "android-build-tools-35/lib/apksigner.jar"
    align = authority.TOOLS / "android-build-tools-35/zipalign.exe"
    try:
        certificate = authority.run([authority.TOOLS / "jdk17/bin/keytool.exe", "-list", "-rfc",
                                     "-keystore", key, "-alias", values["--ks-key-alias"],
                                     "-storepass:env", env_name], environment)
        match = re.search(r"-----BEGIN CERTIFICATE-----\s*(.*?)\s*-----END CERTIFICATE-----", certificate, re.S)
        if not match or hashlib.sha256(base64.b64decode(match[1])).hexdigest() != CERT_SHA:
            raise ValueError("Original app signing certificate differs")
        authority.run([align, "-P", "16", "4", unsigned, aligned], environment)
        entries_match(aligned, receipt["expectedEntrySha256"])
        authority.run([java, "-jar", signer, "sign", "--ks", key,
                       "--ks-key-alias", values["--ks-key-alias"],
                       "--ks-pass", "env:" + env_name, "--key-pass", "env:" + env_name,
                       "--v1-signing-enabled", "false", "--v2-signing-enabled", "true",
                       "--v3-signing-enabled", "true", "--v4-signing-enabled", "false",
                       "--out", partial, aligned], environment)
    finally:
        environment.pop(env_name, None)
        values.clear()
    entries_match(partial, receipt["expectedEntrySha256"])
    result = subprocess.run([str(java), "-jar", str(signer), "verify", "--verbose",
                             "--print-certs", str(partial)], capture_output=True, text=True,
                            timeout=300, env=environment)
    if (result.returncode or
        "Verified using v2 scheme (APK Signature Scheme v2): true" not in result.stdout or
        "Verified using v3 scheme (APK Signature Scheme v3): true" not in result.stdout or
        CERT_SHA not in result.stdout.lower()):
        raise ValueError("Signed R165 APK verification failed")
    aligned_check = subprocess.run([str(align), "-c", "-P", "16", "4", str(partial)],
                                   capture_output=True, text=True, timeout=300, env=environment)
    if aligned_check.returncode:
        raise ValueError("Signed R165 APK lost 16 KiB alignment")
    final_sha = sha(partial)
    partial.rename(final)
    proof = {
        "schema": "station.combined.final.r165.v1", "passed": True,
        "packageRevision": "R165", "apkSha256": final_sha,
        "apkBytes": final.stat().st_size, "baseApkSha256": BASE_SHA,
        "unsignedPackageReceiptSha256": sha(package / "unsigned-package.json"),
        "dexReceiptSha256": receipt["dexReceiptSha256"],
        "nativeReceiptSha256": receipt["nativeReceiptSha256"],
        "nativeLibrarySha256": receipt["nativeLibrarySha256"],
        "sourceCommit": receipt["sourceCommit"],
        "signatureCertificateSha256": CERT_SHA, "v2": True, "v3": True,
        "zipAlignment16KiB": True, "checkedEntries": 13_861,
        "preservedEntryCount": 13_855, "replacedEntries": REPLACED,
        "changedDexPartitions": ["classes35.dex"], "preservedDexPartitions": 39,
        "classes35Sha256": DEX35_SHA,
        "classes36Sha256Preserved": DEX36_SHA,
        "onlineAeBridgeSha256Preserved": ONLINE_BRIDGE_SHA,
        "onlineEngineIds": receipt["onlineEngineIds"],
        "runtimeMarkers": receipt["runtimeMarkers"],
        "androidManifestPreserved": True,
        "installed": False, "serverRegistered": False, "stable": False,
    }
    (package / "final-apk-proof.json").write_text(
        json.dumps(proof, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return proof


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--package", type=Path, required=True)
    cli.add_argument("--final", type=Path, required=True)
    cli.add_argument("--scratch", type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(main(args.package, args.final, args.scratch), ensure_ascii=False))
