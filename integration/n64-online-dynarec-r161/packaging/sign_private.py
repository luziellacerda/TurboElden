"""Sign reviewed R161 N64 online Dynarec candidate with retained Android identity."""

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


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
AUTHORITY = Path("F:/TurboStations-Backup-Completo-20261011/desenvolvimento/reconstrucao-atual/sky-blue-waves-r145-20261013/private-tooling/sign_r141_private.py")
AUTHORITY_SHA = "7963f2df3922b0726d991947efbd155fbfdf4b94763187905e5a7e23cde2c5b0"
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main(package: Path, final: Path) -> dict:
    package = package.resolve(strict=True)
    if final.exists():
        raise FileExistsError(final)
    receipt = json.loads((package / "unsigned-package.json").read_text("utf-8"))
    if receipt.get("schema") != "station.r161.n64-online-dynarec.package.v1" or receipt.get("passed") is not True or \
       receipt.get("baselineApkSha256") != "4837be706f9ac1f913b4844353741f70c539674e125ae185239611cf5faac2b3" or \
       receipt.get("entryCount") != 13860 or receipt.get("preservedEntryCount") != 13855 or \
       receipt.get("changedDexPartitions") != ["classes35.dex"] or \
       receipt.get("n64OnlineOptions", "").count("cpu=dynarec\n") != 1 or \
       receipt.get("taskRemovalChanged") is not False or \
       receipt.get("inputDelayChanged") is not False or \
       receipt.get("replacedEntries") != [
           "assets/station-online/engines.json", "classes35.dex",
           "lib/arm64-v8a/libstation_dolphin_runtime.so",
           "lib/arm64-v8a/libstation_mupen64plus_runtime.so",
           "lib/arm64-v8a/libstation_psx_online.so"]:
        raise ValueError("Reviewed R161 Dynarec unsigned package required")
    for name, checksum in receipt["sourceFilesSha256"].items():
        if sha(REPO / name) != checksum:
            raise ValueError("R161 source changed after package assembly: " + name)
    unsigned = package / "TurboStations-Premium-R161-n64-online-dynarec-unsigned.apk"
    if sha(unsigned) != receipt["unsignedApkSha256"]:
        raise ValueError("R161 unsigned package changed")
    if sha(AUTHORITY) != AUTHORITY_SHA:
        raise ValueError("Original private signing authority differs")
    spec = importlib.util.spec_from_file_location("r161_authority", AUTHORITY)
    if spec is None or spec.loader is None:
        raise ValueError("Original private authority unavailable")
    authority = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(authority)
    if {name: sha(authority.TOOLS / name) for name in authority.TOOL_PINS} != authority.TOOL_PINS:
        raise ValueError("Pinned Android signing tools differ")
    authority.entries_match(unsigned, receipt["expectedEntrySha256"])
    aligned, signed = package / "aligned.apk", package / "signed.apk"
    if aligned.exists() or signed.exists():
        raise FileExistsError("Fresh R161 signing outputs required")
    temp = package / "temp"
    if not temp.is_dir():
        raise FileNotFoundError("R161 package temporary directory missing")
    key, values = authority.credentials()
    env_name = "STATION_R161_PRIVATE_SIGNING"
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
        authority.entries_match(aligned, receipt["expectedEntrySha256"])
        authority.run([java, "-jar", signer, "sign", "--ks", key,
                       "--ks-key-alias", values["--ks-key-alias"],
                       "--ks-pass", "env:" + env_name, "--key-pass", "env:" + env_name,
                       "--v1-signing-enabled", "false", "--v2-signing-enabled", "true",
                       "--v3-signing-enabled", "true", "--v4-signing-enabled", "false",
                       "--out", signed, aligned], environment)
    finally:
        environment.pop(env_name, None)
        values.clear()
    authority.entries_match(signed, receipt["expectedEntrySha256"])
    result = subprocess.run([str(java), "-jar", str(signer), "verify", "--verbose", "--print-certs", str(signed)],
                            capture_output=True, text=True, timeout=300, env=environment)
    if result.returncode or "Verified using v2 scheme (APK Signature Scheme v2): true" not in result.stdout or \
       "Verified using v3 scheme (APK Signature Scheme v3): true" not in result.stdout or \
       CERT_SHA not in result.stdout.lower():
        raise ValueError("Signed R161 APK verification failed")
    aligned_check = subprocess.run([str(align), "-c", "-P", "16", "4", str(signed)],
                                   capture_output=True, text=True, timeout=300, env=environment)
    if aligned_check.returncode:
        raise ValueError("Signed R161 APK lost 16 KiB alignment")
    final.parent.mkdir(parents=True, exist_ok=True)
    partial = final.with_suffix(".apk.partial")
    if partial.exists():
        raise FileExistsError(partial)
    with signed.open("rb") as source, partial.open("xb") as target:
        shutil.copyfileobj(source, target, 4 * 1024 * 1024)
        target.flush()
        os.fsync(target.fileno())
    if sha(partial) != sha(signed):
        raise ValueError("R161 final APK copy differs")
    partial.rename(final)
    proof = {"schema": "station.r161.n64-online-dynarec.final.v1", "passed": True,
             "packageRevision": "R161", "apkSha256": sha(final), "apkBytes": final.stat().st_size,
             "baseApkSha256": receipt["baselineApkSha256"],
             "signatureCertificateSha256": CERT_SHA, "v2": True, "v3": True,
             "zipAlignment16KiB": True, "checkedEntries": receipt["entryCount"],
             "preservedEntryCount": receipt["preservedEntryCount"],
             "replacedEntries": receipt["replacedEntries"], "changedDexPartitions": ["classes35.dex"],
             "preservedDexPartitions": 39, "androidManifestPreserved": True,
             "androidVersionCodePreservedFromR159": True, "installed": False,
             "physicalVisualValidated": False, "stable": False}
    (package / "final-apk-proof.json").write_text(json.dumps(proof, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return proof


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--package", type=Path, required=True)
    cli.add_argument("--final", type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(main(args.package, args.final), ensure_ascii=False))
