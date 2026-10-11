#!/usr/bin/env python3
"""Sign only an assembled, source-bound APK and promote verified bytes atomically.

No password is stored here. The explicitly selected key must have the original
certificate. All intermediate files stay in the one supplied assembly folder.
The existing current installer is never overwritten by this command.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def run(command, env):
    process = subprocess.Popen(list(map(str, command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    try:
        stdout, stderr = process.communicate(timeout=1800)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run([str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/taskkill.exe"),
                            "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=30)
        else:
            process.kill()
        process.communicate(timeout=30)
        raise RuntimeError("Release deadline exceeded; only the spawned tool tree was stopped")
    require(process.returncode == 0, "Release tool failed: " + Path(str(command[0])).name)
    return stdout

def load(path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("release_assembler", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def scoped_final_guard(receipt, identity, package):
    """R133/R134 promotions require their explicit closed-scope final proof."""
    runtime = json.loads(Path(identity).read_text(encoding="utf-8"))
    if runtime.get("revision") == "R134":
        release = load(Path(__file__).with_name("compile_current.py"))
        require(package.REPLACED == release.R134_REPLACED, "R134 assembler scope differs from reviewed release")
        release.r134_final_guard(receipt, runtime)
        return
    if runtime.get("revision") != "R133":
        return
    require(receipt.get("revision") == "R133" and
            receipt.get("sourceCommit") == runtime["sourceCommit"] and
            receipt.get("baseApkSha256") == "47a619a194c095e70738a4d191fb8491ee410d868e4c11742530ffcaaf844f20" and
            receipt.get("replacementCount") == 5 and receipt.get("additionCount") == 0 and
            set(receipt.get("replacedEntrySha256", {})) == package.REPLACED and
            receipt.get("addedEntrySha256") == {} and
            receipt.get("approvedScopes") == runtime["approvedScopes"] == ["console-hardware-panel-psp-ps3-ps4"] and
            receipt.get("nativeReceiptSha256") == runtime["nativeReceiptSha256"] and
            receipt.get("existing40DexByteIdentical") is True and
            receipt.get("dexClassSetsPreserved") is True and
            receipt.get("frontendLibraryByteIdentical") is True and
            receipt.get("completeAggregateEntryHashMaps") is True and
            receipt.get("manifestByteIdentical") is True and
            receipt.get("resourcesAndSonyAssetsByteIdentical") is True and
            receipt.get("offlineEmulatorEntriesChanged") is False and
            receipt.get("offlineEmulatorLibraryEntriesChanged") is False and
            receipt.get("controllerProfilesUnchanged") is True and
            receipt.get("protocolAndTransportUnchanged") is True and
            receipt.get("ps3Ps4OfflineOnly") is True and receipt.get("ps3Ps4OnlineEnabled") is False and
            receipt.get("verificationScope") == "original-signature-16KiB-and-every-entry-with-five-closed-replacements",
            "R133 final promotion lacks the exact five-entry console-only scope")
    dex = {"classes.dex", *["classes" + str(n) + ".dex" for n in range(2, 41)]}
    preserved = receipt.get("preservedEntrySha256", {})
    require(len(preserved) == receipt.get("preservedEntryCount") and dex <= set(preserved) and
            all(preserved[name] == runtime["payloadSha256"][name] for name in dex) and
            preserved.get("lib/arm64-v8a/libstation_frontend.so") == "4e7ad58e1e8f8a284654120c27280eed8c124ad5301a9e87d769e41f100d8d0d" and
            receipt.get("engineIds") == [row["engineId"] for row in runtime["engines"]],
            "R133 final promotion differs from preserved DEX/frontend or final engine identities")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "freeze", "identity", "recipe", "assembly", "final", "key", "tools"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--alias", required=True)
    parser.add_argument("--password-env", required=True)
    args = parser.parse_args()
    require(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.password_env), "Invalid environment variable name")
    require(args.password_env in os.environ, "Signing password environment is missing")
    work = args.assembly.resolve(strict=True)
    active = Path(r"G:\StationNormalOwnersR127").resolve(strict=True)
    require(work != Path(work.anchor) and active in work.parents, "Assembly must remain inside the single active G: work tree")
    forbidden = (args.base.resolve(), work / "unsigned.apk", work / "aligned.apk", work / "signed.apk", args.freeze.resolve(), args.identity.resolve())
    require(args.final.resolve() not in forbidden, "Invalid release destination")
    temp = work / "temp"
    temp.mkdir(exist_ok=True)
    env = {**os.environ, "TMP": str(temp), "TEMP": str(temp), "JAVA_TOOL_OPTIONS": "-Djava.io.tmpdir=" + str(temp), "PYTHONDONTWRITEBYTECODE": "1"}
    module = load(args.recipe / "assemble_apk.py")
    package = module.assembler() if hasattr(module, "assembler") else module
    package.inputs(args.base, args.freeze, args.identity)
    unsigned = work / "unsigned.apk"
    recorded = json.loads(unsigned.with_suffix(".package.json").read_text(encoding="utf-8"))
    require(recorded["unsignedApkSha256"] == sha(unsigned) and recorded["unsignedApkBytes"] == unsigned.stat().st_size, "Unsigned APK changed after assembly")
    require(recorded["freezeSha256"] == sha(args.freeze) and recorded["identityReceiptSha256"] == sha(args.identity), "Unsigned APK belongs to another source/runtime")
    raw = run([args.tools / "jdk17/bin/keytool.exe", "-list", "-rfc", "-keystore", args.key, "-alias", args.alias, "-storepass:env", args.password_env], env)
    cert = re.search(rb"-----BEGIN CERTIFICATE-----\s*(.*?)\s*-----END CERTIFICATE-----", raw, re.S)
    require(cert is not None and hashlib.sha256(base64.b64decode(cert.group(1))).hexdigest() == CERT, "Key certificate differs; signing refused")
    aligned, signed = work / "aligned.apk", work / "signed.apk"
    align = args.tools / "android-build-tools-35/zipalign.exe"
    java = args.tools / "jdk17/bin/java.exe"
    signer = args.tools / "android-build-tools-35/lib/apksigner.jar"
    if not aligned.exists():
        run([align, "-P", "16", "4", unsigned, aligned], env)
    # A previous complete alignment is reusable only if every data entry is exact.
    with zipfile.ZipFile(unsigned) as before, zipfile.ZipFile(aligned) as after:
        require(before.namelist() == after.namelist() and before.comment == after.comment, "Partial or differing aligned APK")
        for name in before.namelist():
            require(package.entry_sha(before, name) == package.entry_sha(after, name), "Aligned entry differs: " + name)
    run([align, "-P", "16", "-c", "4", aligned], env)
    if not signed.exists():
        run([java, "-jar", signer, "sign", "--ks", args.key, "--ks-key-alias", args.alias,
             "--ks-pass", "env:" + args.password_env, "--key-pass", "env:" + args.password_env,
             "--v1-signing-enabled", "false", "--v2-signing-enabled", "true", "--v3-signing-enabled", "true",
             "--v4-signing-enabled", "false", "--out", signed, aligned], env)
    verification = work / "verified-final.json"
    if verification.exists():
        receipt = json.loads(verification.read_text(encoding="utf-8"))
        require(receipt["apkSha256"] == sha(signed) and receipt["apkBytes"] == signed.stat().st_size, "Existing final verification differs")
        require(receipt["freezeSha256"] == sha(args.freeze) and receipt["identityReceiptSha256"] == sha(args.identity), "Final verification belongs to another source/runtime")
        require(receipt["signingCertificateSha256"] == CERT and receipt["signatureSchemesVerified"] == ["v2", "v3"] and receipt["zipAlignmentVerifiedBytes"] == 16384, "Final verification signature/alignment differs")
    else:
        run([args.tools / "python314/python.exe", "-B", args.recipe / "verify_final.py", "--base", args.base,
             "--apk", signed, "--freeze", args.freeze, "--identity-receipt", args.identity, "--receipt", verification,
             "--java", java, "--apksigner-jar", signer, "--zipalign", align], env)
        receipt = json.loads(verification.read_text(encoding="utf-8"))
    scoped_final_guard(receipt, args.identity, package)
    package.inputs(args.base, args.freeze, args.identity)
    # Never replace an installer with another identity, including after retry.
    if args.final.exists():
        require(sha(args.final) == receipt["apkSha256"], "Destination already contains another installer")
    else:
        args.final.parent.mkdir(parents=True, exist_ok=True)
        stage = args.final.with_suffix(".verified-part")
        require(not stage.exists(), "A partial promotion requires inspection")
        shutil.copyfile(signed, stage)
        require(sha(stage) == receipt["apkSha256"], "Copied release bytes differ")
        require(not args.final.exists(), "Destination appeared during promotion")
        os.rename(stage, args.final)
    print(json.dumps({"signedAndVerified": True, "apkSha256": receipt["apkSha256"], "apkBytes": receipt["apkBytes"], "originalCertificatePreserved": True, "existingInstallerOverwritten": False, "installed": False}))

if __name__ == "__main__":
    main()
