"""Sign the scoped R163 candidate with the retained Android certificate.

The signed APK is written once at its final path.  The original R162 APK,
private key, package data and game content are never copied into the repo.
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
BASE_SHA = "7ec742c4cae7b663f2198e347253986b4c4c5d0d0461052dd75df56ca6335dd7"
DEX35_SHA = "0489cd99a51d43d001cab4ef5374e03aea694b58f6cc72648e7217f363d79b52"
DEX36_SHA = "a1c12b34c5eba4060707235c86dea3bbdfa59ef52264afc7ebaaa5d73231287c"
ONLINE_BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
REPLACED = sorted((
    "assets/station-online/engines.json",
    "lib/arm64-v8a/libstation_dolphin_runtime.so",
    "lib/arm64-v8a/libstation_mupen64plus_runtime.so",
    "lib/arm64-v8a/libstation_psx_online.so",
    "lib/arm64-v8a/libturbo_carousel.so",
))


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def entries_match(path: Path, expected: dict[str, str]) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) != 13_861 or set(names) != set(expected):
            raise ValueError("R163 APK entry set differs")
        for name in names:
            with archive.open(name) as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != expected[name]:
                    raise ValueError("R163 APK entry content differs: " + name)


def validate_package(package: Path) -> tuple[dict, Path]:
    receipt = json.loads((package / "unsigned-package.json").read_text("utf-8"))
    expected = receipt.get("expectedEntrySha256")
    if (receipt.get("schema") != "station.r163.selection-n64-cover.package.v1" or
        receipt.get("passed") is not True or
        receipt.get("baselineApkSha256") != BASE_SHA or
        receipt.get("entryCount") != 13_861 or
        receipt.get("preservedEntryCount") != 13_856 or
        receipt.get("preservedDexPartitions") != 40 or
        receipt.get("replacedEntries") != REPLACED or
        receipt.get("classes35Sha256Preserved") != DEX35_SHA or
        receipt.get("classes36Sha256Preserved") != DEX36_SHA or
        receipt.get("onlineAeBridgeSha256Preserved") != ONLINE_BRIDGE_SHA or
        receipt.get("retainedOwnerPolicies") is not True or
        receipt.get("visualAndLayoutOnly") is not True or
        receipt.get("newTimersThreadsHeapAllocations") != 0 or
        not isinstance(expected, dict) or len(expected) != 13_861 or
        expected.get("classes35.dex") != DEX35_SHA or
        expected.get("classes36.dex") != DEX36_SHA or
        expected.get("lib/arm64-v8a/libstation_ae_bridge.so") != ONLINE_BRIDGE_SHA or
        expected.get("lib/arm64-v8a/libturbo_carousel.so") != receipt.get("nativeLibrarySha256")):
        raise ValueError("Reviewed R163 five-entry unsigned package required")
    source_files = receipt.get("sourceFilesSha256")
    if not isinstance(source_files, dict) or set(source_files) != {
        "integration/game-selection-n64-cover-r163/recipe/patch_layout.py",
        "integration/game-selection-n64-cover-r163/recipe/patch_n64_cover.py",
        "integration/game-selection-n64-cover-r163/recipe/build_native.py",
        "integration/game-selection-n64-cover-r163/recipe/package_candidate.py",
        "integration/game-selection-n64-cover-r163/recipe/sign_private.py",
    }:
        raise ValueError("R163 source scope differs")
    for name, checksum in source_files.items():
        if sha(REPO / name) != checksum:
            raise ValueError("R163 source changed after package assembly: " + name)
    unsigned = package / "TurboStations-Premium-R163-selection-n64-cover-unsigned.apk"
    if not unsigned.is_file() or sha(unsigned) != receipt.get("unsignedApkSha256") or \
       unsigned.stat().st_size != receipt.get("unsignedApkBytes"):
        raise ValueError("R163 unsigned APK changed")
    return receipt, unsigned


def main(package: Path, final: Path) -> dict:
    package = package.resolve(strict=True)
    final = final.resolve()
    if final.exists():
        raise FileExistsError(final)
    if package.anchor.lower() != final.anchor.lower():
        raise ValueError("Keep the final APK on the package volume to avoid an extra large copy")
    receipt, unsigned = validate_package(package)
    if sha(AUTHORITY) != AUTHORITY_SHA:
        raise ValueError("Original private signing authority differs")
    spec = importlib.util.spec_from_file_location("r163_authority", AUTHORITY)
    if spec is None or spec.loader is None:
        raise ValueError("Original private authority unavailable")
    authority = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(authority)
    if {name: sha(authority.TOOLS / name) for name in authority.TOOL_PINS} != authority.TOOL_PINS:
        raise ValueError("Pinned Android signing tools differ")
    entries_match(unsigned, receipt["expectedEntrySha256"])
    temp = package / "temp"
    if not temp.is_dir():
        raise FileNotFoundError("R163 package temporary directory missing")
    aligned = package / "aligned.apk"
    final.parent.mkdir(parents=True, exist_ok=True)
    partial = final.with_suffix(final.suffix + ".partial")
    if aligned.exists() or partial.exists():
        raise FileExistsError("Fresh R163 signing outputs required")
    key, values = authority.credentials()
    env_name = "STATION_R163_PRIVATE_SIGNING"
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
        raise ValueError("Signed R163 APK verification failed")
    aligned_check = subprocess.run([str(align), "-c", "-P", "16", "4", str(partial)],
                                   capture_output=True, text=True, timeout=300, env=environment)
    if aligned_check.returncode:
        raise ValueError("Signed R163 APK lost 16 KiB alignment")
    final_sha = sha(partial)
    partial.rename(final)
    proof = {
        "schema": "station.r163.selection-n64-cover.final.v1", "passed": True,
        "packageRevision": "R163", "apkSha256": final_sha,
        "apkBytes": final.stat().st_size, "baseApkSha256": BASE_SHA,
        "signatureCertificateSha256": CERT_SHA, "v2": True, "v3": True,
        "zipAlignment16KiB": True, "checkedEntries": 13_861,
        "preservedEntryCount": 13_856, "replacedEntries": REPLACED,
        "preservedDexPartitions": 40, "classes35Sha256Preserved": DEX35_SHA,
        "classes36Sha256Preserved": DEX36_SHA,
        "onlineAeBridgeSha256Preserved": ONLINE_BRIDGE_SHA,
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
    args = cli.parse_args()
    print(json.dumps(main(args.package, args.final), ensure_ascii=False))
