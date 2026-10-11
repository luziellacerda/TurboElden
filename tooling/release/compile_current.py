#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Resolve and verify the explicit current release without publishing it.

This orchestration is outside the source sets fingerprinted by the runtime.
There is no signing key, phone operation, checkout change or latest-file search.
The current APK is read from CURRENT, never selected from a historical recipe.
Build phases require --allow-build, use the single existing G: work tree and
never overwrite the installed/current APK or write reconstruction receipts to F:.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
REPO_DEFAULT = Path(__file__).resolve().parents[2]
WORK = Path(r"G:\StationNormalOwnersR127")
REBUILD = WORK / "psx/backup-r128-rebuild"
ASSEMBLY = WORK / "offline-emulators/assembly"
TEMP = WORK / "offline-emulators/release-temp"
PACKAGE = "org.turboramastation.frontend"
LOGIN = "org.emulationstation.frontend.auth.LoginActivity"
R128_SOURCE = "3ea94ade312640ab69ca09e4092f60607996ccba"
R131_SOURCE = "8503c2e32d7487d3bb31397ba9533dc7e1bfe981"
R131_ASSEMBLY = WORK / "sony-internal/correction/assembly"
R131_FINAL = "versions/station-sony-internal-r131-20261011/evidence/package-final.json"
CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
PHASES = ("plan", "preflight", "verify", "rebuild-payloads", "assemble")
INTEGRATIONS = {"R128": "ps3-ps4-offline", "R129": "local-sony-demos", "R130": "local-sony-demos",
                "R131": "sony-internal"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def within(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    require(path != root and root in path.parents, "Output must remain within the single active work tree")
    return path


def resolve_current(current_path, repo):
    """Small read-only resolver shared with an installation orchestrator."""
    current = read(current_path)
    candidate = current["currentDevelopmentCandidate"]
    revision = candidate["revision"]
    require(revision in INTEGRATIONS, "No explicitly reviewed integration for the requested revision")
    if revision == "R128":
        require(candidate["sourceCommit"] == R128_SOURCE, "Current executable source differs from the reviewed R128")
    elif revision == "R131":
        require(candidate["sourceCommit"] == R131_SOURCE, "Current executable source differs from the reviewed R131")
    backup = Path(current["singleCompleteBackup"]).resolve(strict=True)
    mirror = read(backup / "CURRENT-LOCAL-ARTIFACTS.json")["currentDevelopmentCandidate"]
    for name in ("revision", "apk", "sha256", "bytes", "sourceCommit"):
        require(candidate[name] == mirror[name], "Current pointers disagree: " + name)
    actual = read(backup / "desenvolvimento/ATUAL.json")
    for name in ("revision", "apk", "sha256", "bytes", "sourceCommit"):
        require(candidate[name] == actual[name], "Development ATUAL disagrees with CURRENT: " + name)
    apk = Path(candidate["apk"]).resolve(strict=True)
    require(apk.parent == backup / "desenvolvimento", "Current APK must be the explicit development installer in the sole backup")
    integration = INTEGRATIONS[revision]
    final_path = repo / (R131_FINAL if revision == "R131" else
                         "integration/" + integration + "/evidence/package-final.json")
    final = read(final_path)
    require(final["revision"] == candidate["revision"], "Package evidence revision differs")
    require(final["apkSha256"] == candidate["sha256"] and final["apkBytes"] == candidate["bytes"],
            "Current APK identity differs from final package evidence")
    require(final["signingCertificateSha256"] == CERT, "Final package evidence has another signing identity")
    require(candidate.get("signedAndVerified") is True and actual.get("signedAndVerified") is True,
            "Current candidate is not marked as signed and verified")
    if revision != "R128":
        require(final.get("sourceCommit") == candidate["sourceCommit"], "New integration evidence does not bind the current executable source")
    tools = backup / "ferramentas"
    if revision == "R131":
        require(final.get("internalSonyOwnersAdded") is True and
                final.get("existing39DexByteIdentical") is True and
                final.get("existingResourcesAndCarouselByteIdentical") is True and
                final.get("ps3Ps4OfflineOnly") is True and
                final.get("ps3Ps4OnlineEnabled") is False and
                final.get("sonyNativeLibrariesModified") is False and
                final.get("externalSonyEmulatorInvoked") is False,
                "R131 final evidence differs from the reviewed internal-Sony/offline-only scope")
        require(final.get("signatureSchemesVerified") == ["v2", "v3"] and
                final.get("zipAlignmentVerifiedBytes") == 16384,
                "R131 final evidence lacks the original signature/alignment contract")
        require("assemblyPath" in candidate, "R131 requires its explicit reviewed assembly path")
        assembly = Path(candidate["assemblyPath"]).resolve(strict=True)
        require(assembly == R131_ASSEMBLY.resolve(strict=True),
                "R131 assembly path escaped the reviewed internal-Sony work tree")
        require(all("assemblyPath" in row and Path(row["assemblyPath"]).resolve(strict=True) == assembly
                    for row in (mirror, actual)), "R131 current pointers disagree on the reviewed assembly")
        base = backup / "desenvolvimento/TurboStations-Premium-R130-20261011.apk"
        require(base.is_file(), "Exact R130 reproduction donor is missing; no historical fallback is allowed")
        freeze = assembly / "source-freeze.json"
        identity = assembly / "identity/runtime-identity.json"
        for name, expected in (("sourceFreezeSha256", final["freezeSha256"]),
                               ("runtimeIdentityReceiptSha256", final["identityReceiptSha256"])):
            require(candidate.get(name) == actual.get(name) == mirror.get(name) == expected,
                    "R131 current pointers differ from the final source binding: " + name)
        return {"current": candidate, "backup": backup, "apk": apk, "final": final,
                "integration": integration, "tools": tools, "base": base, "donor": base,
                "repo": repo, "freeze": freeze, "identity": identity}
    base = backup / "desenvolvimento/bases-necessarias/TurboStations-Premium-R126-20261011.apk"
    donor = backup / "desenvolvimento/bases-necessarias/TurboStations-Premium-R127-20261011.apk"
    require(base.is_file() and donor.is_file(), "Pinned R126/R127 reproduction donors are missing; no historical fallback is allowed")
    assembly = ASSEMBLY if revision == "R128" else WORK / "local-sony-demos/assembly"
    if "assemblyPath" in candidate:
        require(revision == "R130", "Explicit assembly path is scoped to R130")
        selected = Path(candidate["assemblyPath"]).resolve(strict=True)
        allowed = {(WORK / "local-sony-demos/assembly").resolve(),
                   (WORK / "local-sony-demos/assembly-next").resolve()}
        require(selected in allowed, "Assembly path escaped the reviewed current work tree")
        assembly = selected
    freeze_name = "INPUTS.json" if revision == "R128" else "source-freeze.json"
    return {"current": candidate, "backup": backup, "apk": apk, "final": final, "integration": integration,
            "tools": tools, "base": base, "donor": donor, "repo": repo,
            "freeze": assembly / freeze_name, "identity": assembly / "identity/runtime-identity.json"}


def env_for_tools(context=None):
    temporary = R131_ASSEMBLY / "release-temp" if context is not None and context["current"]["revision"] == "R131" else TEMP
    within(temporary, WORK).mkdir(parents=True, exist_ok=True)
    return {**os.environ, "TMP": str(temporary), "TEMP": str(temporary),
            "JAVA_TOOL_OPTIONS": "-Djava.io.tmpdir=" + str(temporary), "PYTHONDONTWRITEBYTECODE": "1"}


def run(command, *, timeout=300, env=None):
    """Bound the exact child tree, retaining diagnostics locally, never stdout secrets."""
    process = subprocess.Popen(list(map(str, command)), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run([str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/taskkill.exe"),
                            "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=30)
        else:
            process.kill()
        stdout, stderr = process.communicate(timeout=30)
        raise RuntimeError("Build/tool deadline exceeded; the spawned child tree was stopped")
    if process.returncode:
        # No shell interpolation and no credentials appear in these commands.
        raise RuntimeError("Reviewed tool failed: " + Path(str(command[0])).name +
                           "; exit=" + str(process.returncode))
    return stdout.decode("utf-8", "replace"), stderr.decode("utf-8", "replace")


def manifest_entry(apk, repo):
    """Inspect the actual APK's small AXML, not a package name in a receipt."""
    patch = load(repo / "integration/ps3-ps4-offline/recipe/patch_manifest.py", "release_manifest")
    helper = patch.helper()
    with zipfile.ZipFile(apk) as archive:
        data = archive.read("AndroidManifest.xml")
    chunks = list(helper.chunks(data))
    pool = next(c for c in chunks if c[1] == 1)
    strings = helper.string_pool(data, pool[0])
    stack, activity, login, package = [], None, None, None
    for offset, kind, header, size in chunks:
        if kind not in (0x102, 0x103):
            continue
        tag = strings[helper.u32(data, offset + 20)]
        if kind == 0x103:
            require(stack and stack[-1] == tag, "Malformed actual AXML nesting")
            stack.pop()
            if tag == "activity":
                if activity and activity["name"] == LOGIN:
                    require(login is None, "Duplicate login activity")
                    login = activity
                activity = None
            continue
        start, width, count = struct.unpack_from("<HHH", data, offset + 24)
        require(width == 20, "Actual AXML attribute width differs")
        attrs = {}
        for index in range(count):
            at = offset + 16 + start + index * width
            name = strings[helper.u32(data, at + 4)]
            value = helper.u32(data, at + 16)
            attrs[name] = strings[value] if data[at + 15] == 3 else value
        if tag == "manifest":
            package = attrs.get("package")
        elif tag == "activity":
            activity = {"name": attrs.get("name"), "exported": attrs.get("exported"),
                        "launchMode": attrs.get("launchMode"), "filters": []}
        elif tag == "intent-filter" and activity is not None:
            activity["filters"].append({"actions": [], "categories": []})
        elif tag in ("action", "category") and activity is not None and "intent-filter" in stack:
            activity["filters"][-1]["actions" if tag == "action" else "categories"].append(attrs.get("name"))
        stack.append(tag)
    require(package == PACKAGE and login is not None, "Actual APK package/login differs")
    require(login["exported"] == 0xffffffff and login["launchMode"] == 2,
            "Official Login must remain exported and singleTask")
    require(any("android.intent.action.MAIN" in row["actions"] and
                "android.intent.category.LAUNCHER" in row["categories"] for row in login["filters"]),
            "Official Login lacks its actual MAIN/LAUNCHER contract")
    return {"package": package, "launchActivity": LOGIN, "exported": True,
            "singleTask": True, "mainLauncher": True}


def source_guard(context, *, rebuilt=False):
    require(not rebuilt or context["current"]["revision"] == "R128",
            "Later integrations require their reviewed reconstruction recipes; no R128 rebuild fallback")
    recipe = context["repo"] / ("integration/" + context["integration"] + "/recipe")
    if context["current"]["revision"] == "R131":
        identity, freeze = context["identity"], context["freeze"]
        wrapper = load(recipe / "assemble_apk.py", "release_r131_assembly")
        assembler = wrapper.assembler(identity)
        frozen, runtime, paths, expected, _ = assembler.inputs(context["base"], freeze, identity)
        require(runtime["sourceCommit"] == context["current"]["sourceCommit"],
                "R131 runtime identity does not bind the current executable source")
        require(expected == {**context["final"]["replacedEntrySha256"], **context["final"]["addedEntrySha256"]},
                "R131 productive payloads differ from the reviewed current installer")
        require([row["engineId"] for row in runtime["engines"]] == context["final"]["engineIds"],
                "R131 productive engine identities differ from the reviewed current installer")
        require(runtime["sonyModules"] == context["final"]["sonyModules"],
                "R131 internal module identities differ from final package evidence")
        require(sha(freeze) == context["final"]["freezeSha256"] and
                sha(identity) == context["final"]["identityReceiptSha256"],
                "R131 current freeze/identity receipt differs")
        return assembler, identity, freeze
    old = list(sys.path)
    try:
        sys.path.insert(0, str(recipe))
        module = load(recipe / "pipeline_common.py", "release_pipeline")
        assembler = module.assembler()
        identity = REBUILD / "identity/runtime-identity.json" if rebuilt else context["identity"]
        freeze = REBUILD / "release/INPUTS.json" if rebuilt else context["freeze"]
        frozen, runtime, paths, expected, _ = assembler.inputs(context["base"], freeze, identity)
        require(expected == {**context["final"]["replacedEntrySha256"], **context["final"]["addedEntrySha256"]},
                "Productive payloads differ from the reviewed current installer")
        require([row["engineId"] for row in runtime["engines"]] == context["final"]["engineIds"],
                "Productive engine identities differ from the reviewed current installer")
        if not rebuilt:
            require(sha(freeze) == context["final"]["freezeSha256"] and
                    sha(identity) == context["final"]["identityReceiptSha256"], "Current freeze/identity receipt differs")
        return assembler, identity, freeze
    finally:
        sys.path[:] = old


def preflight(context):
    current, apk, final, tools = context["current"], context["apk"], context["final"], context["tools"]
    require(apk.stat().st_size == current["bytes"] and sha(apk) == current["sha256"], "Actual current APK identity differs")
    for name, recorded in final["verificationTools"].items():
        path = {"java": tools / "jdk17/bin/java.exe", "apksignerJar": tools / "android-build-tools-35/lib/apksigner.jar",
                "zipalign": tools / "android-build-tools-35/zipalign.exe"}[name]
        require(sha(path) == recorded["sha256"], "Preserved verification tool differs: " + name)
    source_guard(context)
    entry = manifest_entry(apk, context["repo"])
    stdout, _ = run([tools / "jdk17/bin/java.exe", "-jar", tools / "android-build-tools-35/lib/apksigner.jar",
                     "verify", "--verbose", "--print-certs", apk], timeout=900, env=env_for_tools(context))
    signer = re.search(r"^Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]{64})\s*$", stdout, re.M)
    require(signer and signer.group(1).lower() == CERT, "Actual current APK signer differs")
    require(not re.search(r"^Signer #[2-9]\d* certificate", stdout, re.M), "Unexpected additional APK signer")
    for scheme in ("v2", "v3"):
        require(re.search(r"^Verified using " + scheme + r" scheme.*: true\s*$", stdout, re.M), "Actual APK signature scheme missing: " + scheme)
    run([tools / "android-build-tools-35/zipalign.exe", "-P", "16", "-c", "4", apk], timeout=300)
    return {**entry, "sourceFreezeAndRuntimeBindingsVerified": True, "actualCurrentAPKHashVerified": True,
            "actualSignatureAndAlignmentVerified": True, "engineIds": final["engineIds"]}


def rebuild_payloads(context, timeout):
    """Reuse exact completed outputs; incomplete directories fail explicitly."""
    require(context["current"]["revision"] == "R128",
            "R129 reconstruction uses integration/local-sony-demos/recipe/build_demo_payloads.py then build_unsigned.py")
    backup, tools = context["backup"], context["tools"]
    runner = backup / "desenvolvimento/reconstrucao-atual/RECRIAR-PAYLOADS-R128.py"
    source = backup / "fontes/TurboElden/integration/ps3-ps4-offline/evidence/package-final.json"
    require(read(source) == context["final"], "Single backup sources do not describe the current package")
    hashes = {**context["final"]["replacedEntrySha256"], **context["final"]["addedEntrySha256"]}
    steps = ("java", "optin", "offline", "identity")
    expected = {"java": {"classes35.dex": hashes["classes35.dex"]},
                "optin": {"classes6.dex": hashes["classes6.dex"]},
                "offline": {name: hashes[name] for name in ("AndroidManifest.xml", "classes28.dex", "classes39.dex")},
                "identity": {"engines.json": hashes["assets/station-online/engines.json"],
                             "native/libstation_psx_online.so": hashes["lib/arm64-v8a/libstation_psx_online.so"],
                             "libstation_mupen64plus_runtime.so": hashes["lib/arm64-v8a/libstation_mupen64plus_runtime.so"],
                             "libstation_dolphin_runtime.so": hashes["lib/arm64-v8a/libstation_dolphin_runtime.so"]}}
    expected["offline"]["libturbo_carousel.so"] = hashes["lib/arm64-v8a/libturbo_carousel.so"]
    reused = []
    for phase in steps:
        output = within(REBUILD / phase, WORK)
        if output.exists():
            require(all((output / name).is_file() and sha(output / name) == digest for name, digest in expected[phase].items()),
                    "Incomplete or differing " + phase + " output in the sole work tree; no silent overwrite/reuse")
            reused.append(phase)
            continue
        run([tools / "python314/python.exe", runner, "--phase", phase], timeout=timeout, env=env_for_tools())
        require(all((output / name).is_file() and sha(output / name) == digest for name, digest in expected[phase].items()),
                "Rebuilt current payload differs in phase: " + phase)
    payloads = {"AndroidManifest.xml": REBUILD / "offline/AndroidManifest.xml",
                "classes6.dex": REBUILD / "optin/classes6.dex", "classes28.dex": REBUILD / "offline/classes28.dex",
                "classes35.dex": REBUILD / "java/classes35.dex", "classes39.dex": REBUILD / "offline/classes39.dex",
                "lib/arm64-v8a/libturbo_carousel.so": REBUILD / "offline/libturbo_carousel.so",
                "assets/station-online/engines.json": REBUILD / "identity/engines.json",
                "lib/arm64-v8a/libstation_psx_online.so": REBUILD / "identity/native/libstation_psx_online.so",
                "lib/arm64-v8a/libstation_mupen64plus_runtime.so": REBUILD / "identity/libstation_mupen64plus_runtime.so",
                "lib/arm64-v8a/libstation_dolphin_runtime.so": REBUILD / "identity/libstation_dolphin_runtime.so"}
    freeze = REBUILD / "release/INPUTS.json"
    identity = REBUILD / "identity/runtime-identity.json"
    recipe = context["repo"] / "integration/ps3-ps4-offline/recipe/assemble_apk.py"
    if not freeze.exists():
        command = [tools / "python314/python.exe", recipe, "--base", context["base"], "--freeze", freeze,
                   "--identity-receipt", identity, "--write-freeze"]
        for name, path in payloads.items():
            command.extend(("--payload", name + "=" + str(path)))
        run(command, timeout=timeout, env=env_for_tools())
    source_guard(context, rebuilt=True)
    return {"rebuiltOrReusedPayloadCount": len(payloads), "reusedExactPhases": reused,
            "currentCandidateOverwritten": False, "apkProduced": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--allow-build", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    args = parser.parse_args()
    require(60 <= args.timeout_seconds <= 7200, "Build deadline must be 60..7200 seconds")
    require(args.phase not in ("rebuild-payloads", "assemble") or args.allow_build,
            "Building requires explicit --allow-build; plan/verify never compile")
    context = resolve_current(args.current.resolve(strict=True), args.repo.resolve(strict=True))
    require(context["current"]["revision"] == "R128" or args.phase not in ("rebuild-payloads", "assemble"),
            "R129/R130/R131 build uses its own reviewed integration recipes; no R128 fallback")
    report = {"schemaVersion": 1, "revision": context["current"]["revision"], "phase": args.phase,
              "recordedUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "sourceCommit": context["current"]["sourceCommit"], "apkSha256": context["current"]["sha256"],
              "apkBytes": context["current"]["bytes"], "currentResolvedFromExplicitPointer": True,
              "historicalRecipeSelected": False, "signed": False, "installed": False,
              "currentCandidateOverwritten": False, "runtimeOrOwnerSourceChanged": False,
              "serverActivationVerified": False, "physicalGameplayValidated": False}
    if args.phase != "plan":
        report.update(preflight(context))
    if args.phase == "verify":
        # The exact final bytes already have a full preserved-entry receipt.
        # Revalidating hash + current source bindings + real certificate means
        # this receipt is reusable without generating another signed APK.
        report["fullPackageReceiptMatchesExactCurrentBytes"] = True
        report["preservedEntryCount"] = context["final"]["preservedEntryCount"]
    elif args.phase == "rebuild-payloads":
        report.update(rebuild_payloads(context, args.timeout_seconds))
    elif args.phase == "assemble":
        assembler, identity, freeze = source_guard(context, rebuilt=True)
        output = within(REBUILD / "release/unsigned.apk", WORK)
        receipt = output.with_suffix(".package.json")
        if output.exists() or receipt.exists():
            require(output.is_file() and receipt.is_file(), "Incomplete unsigned assembly; no overwrite")
            existing = read(receipt)
            require(existing["freezeSha256"] == sha(freeze) and existing["identityReceiptSha256"] == sha(identity),
                    "Unsigned package belongs to another source freeze/runtime")
            require(existing["unsignedApkBytes"] == output.stat().st_size and existing["unsignedApkSha256"] == sha(output),
                    "Unsigned package changed after assembly")
            report["existingExactUnsignedReused"] = True
        else:
            require(shutil.disk_usage(WORK).free >= context["current"]["bytes"] + 512 * 1024 * 1024,
                    "Insufficient space for one unsigned build; current/backup are preserved")
            tools = context["tools"]
            run([tools / "python314/python.exe", context["repo"] / "integration/ps3-ps4-offline/recipe/assemble_apk.py",
                 "--base", context["base"], "--freeze", freeze, "--identity-receipt", identity, "--out", output],
                timeout=args.timeout_seconds, env=env_for_tools())
            source_guard(context, rebuilt=True)
        report["apkProduced"] = True
        report["unsignedAPKHash"] = sha(output)
        report["signingOrPublicationStillRequired"] = True
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    stage = args.receipt.with_name(args.receipt.name + ".tmp")
    stage.write_text(encoded, encoding="utf-8")
    os.replace(stage, args.receipt)
    print(json.dumps({key: report[key] for key in ("revision", "phase", "apkSha256", "signed", "installed")}))


if __name__ == "__main__":
    main()
