"""Build/check one unsigned candidate after scoped payload compilations.

No signing credentials, signing invocation, device operation or release promotion.
The inherited assembler independently checks every entry and the complete source
overlay. A successful unsigned.package.json is required by finalize_verified.py.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import zipfile
from pipeline_common import (
    DONOR_BYTES, DONOR_SHA, MEDIA_ADDITIONS, PARENT, ROOT, REVISION, assembler, read, sha, verify_compilation,
)


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def check_unsigned(base, assembly):
    """Recheck the exact unsigned APK, receipt, identities and every entry before signing."""
    package = assembler()
    unsigned = assembly / "unsigned.apk"
    report_path = unsigned.with_suffix(".package.json")
    report = read(report_path)
    report_sha = sha(report_path)
    freeze = assembly / "source-freeze.json"
    identity = assembly / "identity/runtime-identity.json"
    _, runtime, _, frozen_sha, _ = package.inputs(base, freeze, identity)
    if (report.get("revision") != REVISION or report.get("signingPerformed") is not False or
            report.get("zipalignPerformed") is not False or
            report.get("unsignedApkSha256") != sha(unsigned) or
            report.get("unsignedApkBytes") != unsigned.stat().st_size or
            report.get("freezeSha256") != sha(freeze) or
            report.get("identityReceiptSha256") != sha(identity)):
        raise ValueError("Unsigned candidate does not match its source/runtime package receipt")
    expected = {**report["preservedEntrySha256"], **report["replacedEntrySha256"], **report["addedEntrySha256"]}
    if (set(report["replacedEntrySha256"]) != package.REPLACED or
            set(report["addedEntrySha256"]) != package.ADDED or
            set(report["preservedEntrySha256"]) & package.PAYLOADS or
            {**report["replacedEntrySha256"], **report["addedEntrySha256"]} != frozen_sha or
            report.get("preservedEntryCount") != len(report["preservedEntrySha256"]) or
            report.get("preservedEntryManifestSha256") != package.digest(package.canonical(report["preservedEntrySha256"]))):
        raise ValueError("Unsigned receipt is not the closed " + REVISION + " overlay")
    with zipfile.ZipFile(base) as original, zipfile.ZipFile(unsigned) as final:
        original_data = {name for name in package.classic_entries(original) if not package.signature_metadata(name)}
        if (final.comment != original.comment or package.classic_entries(final) != set(expected) or
                set(expected) != original_data | package.ADDED):
            raise ValueError("Unsigned APK entry set/comment differs from package receipt")
        package.classic_zip(unsigned, final.comment)
        if any(package.signature_metadata(name) for name in final.namelist()):
            raise ValueError("Unsigned APK retained old signing metadata")
        for name, checksum in expected.items():
            if package.entry_sha(final, name) != checksum:
                raise ValueError("Unsigned APK entry changed: " + name)
        for name, checksum in report["preservedEntrySha256"].items():
            if package.entry_sha(original, name) != checksum:
                raise ValueError("Unsigned APK preserved entry differs from exact base: " + name)
    package.inputs(base, freeze, identity)
    if (sha(unsigned) != report["unsignedApkSha256"] or sha(report_path) != report_sha or
            sha(freeze) != report["freezeSha256"] or sha(identity) != report["identityReceiptSha256"]):
        raise ValueError("Unsigned candidate changed during verification")
    return {"revision": REVISION, "unsignedReadyForSigning": True,
            "unsignedApkSha256": report["unsignedApkSha256"], "unsignedApkBytes": report["unsignedApkBytes"],
            "packageReceiptSha256": sha(report_path), "freezeSha256": sha(freeze),
            "identityReceiptSha256": sha(identity), "engineIds": [item["engineId"] for item in runtime["engines"]],
            "signingPerformed": False, "installed": False, "physicalGameplayValidated": False}


def build(args):
    package = assembler()
    base = args.base.resolve(strict=True)
    donor = args.donor.resolve(strict=True)
    out = args.out.resolve()
    if out.exists() or ROOT == out or ROOT in out.parents:
        raise ValueError("Use one new isolated assembly directory outside productive sources")
    if package.sha(base) != package.BASE_SHA:
        raise ValueError("Exact preserved signed R126 assembly base required")
    if sha(donor) != DONOR_SHA or donor.stat().st_size != DONOR_BYTES:
        raise ValueError("Exact signed R128 donor required")
    baseline = read(PARENT / "evidence/runtime-final.json")
    # DEX35 now contains the scoped video loop change. Only DEX6 remains an
    # unchanged extracted partition; all other emulator classes stay byte-checked.
    out.mkdir(parents=True)
    kept = out / "preserved-payloads"
    kept.mkdir()
    temp = out / "temp"
    temp.mkdir()
    with zipfile.ZipFile(donor) as archive:
        for name, checksum in baseline["payloadSha256"].items():
            if package.entry_sha(archive, name) != checksum:
                raise ValueError("Actual signed R128 donor differs from published shared payload: " + name)
        for name in ("classes6.dex",):
            with archive.open(name) as source, (kept / name).open("xb") as target:
                package.stream_copy(source, target)
    final = {"AndroidManifest.xml": args.parent_offline_payloads / "AndroidManifest.xml",
             "classes6.dex": kept / "classes6.dex", "classes35.dex": args.demo_payloads / "classes35.dex",
             "classes28.dex": args.demo_payloads / "classes28.dex",
             "classes39.dex": args.demo_payloads / "classes39.dex",
             "lib/arm64-v8a/libturbo_carousel.so": args.demo_payloads / "libturbo_carousel.so"}
    final.update({name: args.demo_payloads / name for name in MEDIA_ADDITIONS})
    verify_compilation(args.parent_offline_receipt, args.parent_offline_payloads, args.demo_receipt, final)
    identity = out / "identity"
    command = [sys.executable, "-B", str(ROOT / "recipe/build_runtime_identity.py"),
               "--base", str(base), "--ndk", str(args.ndk), "--java-receipt", str(args.java_receipt),
               "--out", str(identity), "--parent-offline-receipt", str(args.parent_offline_receipt),
               "--parent-offline-payloads", str(args.parent_offline_payloads), "--demo-receipt", str(args.demo_receipt)]
    if args.parent_identity:
        command.extend(("--parent-identity", str(args.parent_identity)))
    for name, path in sorted(final.items()):
        command.extend(("--payload", name + "=" + str(path.resolve())))
    subprocess.run(command, check=True, timeout=1800,
                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMP": str(temp), "TEMP": str(temp)})
    runtime = read(identity / "runtime-identity.json")
    overlay = {**final, "assets/station-online/engines.json": identity / "engines.json"}
    for kind, marker in runtime["markers"].items():
        library = marker["runtimeLibrary"]
        overlay[package.PREFIX + library] = (identity / "native" / library if kind == "psx" else identity / library)
    if set(overlay) != package.PAYLOADS:
        raise ValueError("Final " + REVISION + " overlay requires the existing ten entries and two Sony videos")
    freeze = out / "source-freeze.json"
    package.freeze_inputs(base, identity / "runtime-identity.json",
                          [name + "=" + str(path.resolve()) for name, path in sorted(overlay.items())], freeze)
    package.package(base, freeze, identity / "runtime-identity.json", out / "unsigned.apk")
    report = check_unsigned(base, out)
    report.update({"baseApkSha256": package.BASE_SHA, "donorApkSha256": DONOR_SHA,
                   "parentOfflineReceiptSha256": sha(args.parent_offline_receipt),
                   "demoCompilationReceiptSha256": sha(args.demo_receipt),
                   "finalSignatureVerificationRequired": True, "ps3Ps4OnlineEnabled": False})
    write_new(out / "pipeline-unsigned.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    for name in ("base", "donor", "ndk", "java-receipt", "parent-offline-receipt", "parent-offline-payloads",
                 "demo-receipt", "demo-payloads", "out"):
        create.add_argument("--" + name, type=Path, required=True)
    create.add_argument("--parent-identity", type=Path)
    check = commands.add_parser("check-unsigned")
    check.add_argument("--base", type=Path, required=True)
    check.add_argument("--assembly", type=Path, required=True)
    args = parser.parse_args()
    result = build(args) if args.command == "build" else check_unsigned(args.base, args.assembly)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
