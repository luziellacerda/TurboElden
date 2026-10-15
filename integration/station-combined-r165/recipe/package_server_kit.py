"""Build the private R165 independent-engine kit from the signed combined APK.

No APK, credential, game or device data is placed in the kit. The free-software
licenses and attribution are retained from R164. R165 changes the scoped DEX35,
carousel and three bound runtime markers. This recipe does not contact or alter
the server.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import zipfile


sys.dont_write_bytecode = True
BASE_SHA = "903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210"
R164_KIT_SHA = "37e3b9dd5b8efaae1a222b27661cb7a838689fa2b484b16268e2efa26d11457a"
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
VERIFIER_SHA = "34f05839f81450c5312208603a4eb678033c9a1f7f263a7dffa329f133004655"
INCOMING_BUILDER_SHA = "362bcae9d8915f7f43aac4c48d06b35bdf57efc88d6acb9199aa06e3a0231426"
R162_PACKAGER_SHA = "d4c4353eeb1fa2ecc215f6b08c33831c1cf768a42e590de0417b239a567bd722"
N64_REVIEW_SHA = "7aa9da840b8dcc1a9ea3404280d9866dfc7e1b15377228be6cb8bf4800e17908"
N64_PREPARER_SHA = "4fcc40012d77624b82874239669a71bddb7dca880d47e67f72970c7673c70b7c"
OLD_DEX35_SHA = "0489cd99a51d43d001cab4ef5374e03aea694b58f6cc72648e7217f363d79b52"
DEX35_SHA = "7a5c1609df4d99ac4371bd4c1b06bc31dcfeeafa616c2b61f6d90bfd5694d020"
DEX_RECEIPT_SHA = "dc71cc3c4a4668e4db76c31521d8a3753faf02e30a223e24ecfb9641ac1b46bc"
DEX36_SHA = "a1c12b34c5eba4060707235c86dea3bbdfa59ef52264afc7ebaaa5d73231287c"
BRIDGE = "libstation_ae_bridge.so"
BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
OLD_CAROUSEL_SHA = "bd3222558a43f8998d51b0b72010ecb8a94c7ae62a14d34b39863d13737a10d0"
PLATFORMS = {"psx", "n64", "gamecube", "wii"}
WRAPPERS = {"libstation_psx_online.so", "libstation_mupen64plus_runtime.so",
            "libstation_dolphin_runtime.so"}
TOOL_ROOT = Path("F:/TurboStations-Backup-Completo-20261011/ferramentas")
TOOL_SHA = {
    "jdk17/bin/java.exe": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "android-build-tools-35/lib/apksigner.jar": "00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7",
    "android-build-tools-35/zipalign.exe": "aa2475ce201962b871fb8daec020da03fd6292c9c1f422cd0fe2e39b20d4f673",
}


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Pinned kit helper missing: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_signature(apk: Path) -> None:
    need({name: sha(TOOL_ROOT / name) for name in TOOL_SHA} == TOOL_SHA,
         "Pinned read-only Android verifier differs")
    java = TOOL_ROOT / "jdk17/bin/java.exe"
    signer = TOOL_ROOT / "android-build-tools-35/lib/apksigner.jar"
    align = TOOL_ROOT / "android-build-tools-35/zipalign.exe"
    result = subprocess.run([str(java), "-jar", str(signer), "verify", "--verbose",
                             "--print-certs", str(apk)], capture_output=True, text=True, timeout=300)
    need(result.returncode == 0 and
         "Verified using v2 scheme (APK Signature Scheme v2): true" in result.stdout and
         "Verified using v3 scheme (APK Signature Scheme v3): true" in result.stdout and
         CERT_SHA in result.stdout.lower(), "R165 signed APK certificate or scheme differs")
    aligned = subprocess.run([str(align), "-c", "-P", "16", "4", str(apk)],
                             capture_output=True, text=True, timeout=300)
    need(aligned.returncode == 0, "R165 signed APK lacks 16 KiB ZIP alignment")


def build(apk: Path, package: Path, prior_kit: Path, app_repo: Path,
          server_repo: Path, private_helper: Path, dex_receipt: Path,
          native_receipt: Path, out: Path) -> dict:
    apk = apk.resolve(strict=True)
    package = package.resolve(strict=True)
    prior_kit = prior_kit.resolve(strict=True)
    app_repo = app_repo.resolve(strict=True)
    server_repo = server_repo.resolve(strict=True)
    private_helper = private_helper.resolve(strict=True)
    dex_receipt = dex_receipt.resolve(strict=True)
    native_receipt = native_receipt.resolve(strict=True)
    out = out.resolve()
    need(not out.is_relative_to(app_repo) and not out.is_relative_to(server_repo),
         "Private server kit output must stay outside source Git repositories")
    need(not out.exists(), "Fresh R165 private kit directory required")
    need(sha(prior_kit) == R164_KIT_SHA and sha(private_helper) == VERIFIER_SHA,
         "Exact R164 reference kit and native verifier required")
    r162_path = app_repo / "integration/n64-online-video-extension-r162/packaging/package_private_kit.py"
    incoming_path = server_repo / "docs/station-android/r128/operator/build_incoming_manifest.py"
    review_path = app_repo / "docs/server/n64-completo-20261014/complete-review.json"
    preparer_path = app_repo / "docs/server/n64-completo-20261014/prepare_complete_n64.py"
    need(sha(r162_path) == R162_PACKAGER_SHA and
         sha(incoming_path) == INCOMING_BUILDER_SHA and
         sha(review_path) == N64_REVIEW_SHA and sha(preparer_path) == N64_PREPARER_SHA,
         "Pinned R162 policy, server builder or N64 mode review differs")
    native = load(private_helper, "r165_native_set_verifier")
    inherited = load(r162_path, "r165_inherited_kit_policy")
    incoming_builder = load(incoming_path, "r165_incoming_builder")
    assembly = json.loads((package / "unsigned-package.json").read_text("utf-8"))
    proof_path = package / "final-apk-proof.json"
    proof = json.loads(proof_path.read_text("utf-8"))
    expected = assembly.get("expectedEntrySha256")
    replaced = {
        "assets/station-online/engines.json",
        "classes35.dex",
        "lib/arm64-v8a/libturbo_carousel.so",
        *("lib/arm64-v8a/" + name for name in WRAPPERS),
    }
    need(assembly.get("schema") == "station.combined.package.r165.v1" and
         assembly.get("passed") is True and assembly.get("baselineApkSha256") == BASE_SHA and
         assembly.get("entryCount") == 13_861 and assembly.get("preservedEntryCount") == 13_855 and
         set(assembly.get("replacedEntries", [])) == replaced and
         assembly.get("changedDexPartitions") == ["classes35.dex"] and
         assembly.get("preservedDexPartitions") == 39 and
         assembly.get("dexReceiptSha256") == DEX_RECEIPT_SHA and
         assembly.get("nativeReceiptSha256") == sha(native_receipt) and
         assembly.get("nativeLibrarySha256") != OLD_CAROUSEL_SHA and
         assembly.get("classes36Sha256Preserved") == DEX36_SHA and
         assembly.get("onlineAeBridgeSha256Preserved") == BRIDGE_SHA and
         assembly.get("retainedOwnerPolicies") is True and
         assembly.get("newThreadsTimersOrPolling") is False and
         assembly.get("effectRoutingAudited") is True and
         isinstance(expected, dict) and len(expected) == 13_861 and
         proof.get("schema") == "station.combined.final.r165.v1" and
         proof.get("passed") is True and proof.get("packageRevision") == "R165" and
         proof.get("apkSha256") == sha(apk) and proof.get("apkBytes") == apk.stat().st_size and
         proof.get("baseApkSha256") == BASE_SHA and
         proof.get("unsignedPackageReceiptSha256") == sha(package / "unsigned-package.json") and
         proof.get("dexReceiptSha256") == DEX_RECEIPT_SHA and
         proof.get("nativeReceiptSha256") == sha(native_receipt) and
         proof.get("signatureCertificateSha256") == CERT_SHA and
         proof.get("v2") is proof.get("v3") is proof.get("zipAlignment16KiB") is True and
         set(proof.get("replacedEntries", [])) == replaced,
         "Exact six-entry R165 assembly and signing proofs required")
    need(expected.get("classes35.dex") == DEX35_SHA and
         expected.get("classes36.dex") == DEX36_SHA and
         expected.get("lib/arm64-v8a/" + BRIDGE) == BRIDGE_SHA and
         expected.get("lib/arm64-v8a/libturbo_carousel.so") == assembly["nativeLibrarySha256"] and
         sha(dex_receipt) == DEX_RECEIPT_SHA,
         "R165 carousel, N64 bridge or DEX proof differs")
    dex_evidence = json.loads(dex_receipt.read_text("utf-8"))
    native_evidence = json.loads(native_receipt.read_text("utf-8"))
    need(dex_evidence.get("schema") == "station.n64.host-exit.dex.r165.v1" and
         dex_evidence.get("passed") is True and
         dex_evidence.get("candidateDexSha256") == DEX35_SHA and
         dex_evidence.get("changedDexPartitions") == ["classes35.dex"] and
         native_evidence.get("schema") == "station.r165.selection-native.v1" and
         native_evidence.get("passed") is True and
         native_evidence.get("outputSha256") == assembly["nativeLibrarySha256"] and
         native_evidence.get("effectRoutingAudited") is True and
         proof.get("classes35Sha256") == DEX35_SHA and
         proof.get("nativeLibrarySha256") == assembly["nativeLibrarySha256"] and
         proof.get("runtimeMarkers") == assembly.get("runtimeMarkers") and
         proof.get("onlineEngineIds") == assembly.get("onlineEngineIds") and
         proof.get("changedDexPartitions") == ["classes35.dex"] and
         proof.get("preservedDexPartitions") == 39 and
         proof.get("preservedEntryCount") == 13_855,
         "R165 DEX, visual or signed identity proof differs")
    verify_signature(apk)
    with zipfile.ZipFile(prior_kit) as previous:
        names = previous.namelist()
        file_manifest = json.loads(previous.read("MANIFESTO-ARQUIVOS.json"))
        need(set(names) == {*file_manifest["files"], "MANIFESTO-ARQUIVOS.json"} and
             all(digest(previous.read(name)) == meta["sha256"] and
                 len(previous.read(name)) == meta["bytes"]
                 for name, meta in file_manifest["files"].items()),
             "R164 reference kit archive contents differ")
        prior = json.loads(previous.read("MANIFESTO-KIT.json"))
        prior_registry = json.loads(previous.read("engines-apk.json"))
        prior_profiles = json.loads(previous.read("profile-policies.json"))
        provenance = previous.read("references/reviewed-78-mode-provenance.json")
        historical_return = previous.read("references/r141-server-return.json")
        prior_dex_proof = previous.read("proofs/dex-receipt.json")
        licenses = {name: previous.read(name) for name in previous.namelist()
                    if name.startswith("licenses/") and not name.endswith("/")}
    need(prior.get("schema") == "station.r164.independent-private-kit.v1" and
         prior.get("apkSha256") == BASE_SHA and prior.get("binaryCount") == 6 and
         prior.get("distinctDependencyCount") == 21 and
         prior.get("onlineAeBridgeSha256Preserved") == BRIDGE_SHA and
         prior.get("dex35Sha256Preserved") == OLD_DEX35_SHA and
         prior.get("dex36Sha256Preserved") == DEX36_SHA and
         prior.get("carouselSha256") == OLD_CAROUSEL_SHA and
         prior.get("n64AndroidProfileSha256") == inherited.R161_ANDROID_N64_SHA and
         prior.get("approvedModesReferenceCount") == 78 and
         prior.get("psxHleApprovalsAdded") == 0 and
         len(json.loads(provenance)["modes"]) == 78 and
         set(licenses) == {"licenses/COPYING.GPL-2.0", "licenses/COPYING.GPL-3.0",
                           "licenses/NOTICE.md"},
         "R164 independent-engine policy reference differs")
    prior_selected = {row["platform"]: row for row in prior_registry["engines"]
                      if row["platform"] in PLATFORMS}
    need(set(prior_selected) == PLATFORMS and
         set(prior_profiles["profiles"]) == PLATFORMS,
         "R164 four-engine policy reference differs")
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13_861 and
             {name: entry_sha(archive, name) for name in names} == expected,
             "Signed R165 APK differs from reviewed six-entry assembly")
        engine_raw = archive.read("assets/station-online/engines.json")
        registry = json.loads(engine_raw)
        selected = [row for row in registry["engines"] if row["platform"] in PLATFORMS]
        need(len(selected) == 4 and len({row["platform"] for row in selected}) == 4 and
             len(registry["engines"]) == 13 and
             [row for row in registry["engines"] if row["platform"] not in PLATFORMS] ==
             [row for row in prior_registry["engines"] if row["platform"] not in PLATFORMS],
             "Independent engine or nine RetroArch descriptors changed")
        need({row["platform"]: row["engineId"] for row in selected} ==
             assembly.get("onlineEngineIds"),
             "Signed R165 engine IDs differ from the package proof")
        need(all({key: value for key, value in row.items()
                  if key not in {"engineId", "runtimeSha256"}} ==
                 {key: value for key, value in prior_selected[row["platform"]].items()
                  if key not in {"engineId", "runtimeSha256"}}
                 for row in selected) and
             all(row["engineId"] != prior_selected[row["platform"]]["engineId"]
                 for row in selected) and
             next(row for row in selected if row["platform"] == "n64")["dependencySha256"].get(BRIDGE) == BRIDGE_SHA,
             "R165 changed owner options, dependencies, core or profile")
        baseline = copy.deepcopy(selected)
        next(row for row in baseline if row["platform"] == "n64")["dependencySha256"].pop(BRIDGE)
        binary, dependencies = native.native_sets(baseline)
        native.native_pin(dependencies, BRIDGE, BRIDGE_SHA)
        need(len(binary) == 6 and len(dependencies) == 21 and
             {name for name in binary if binary[name] != prior["librariesSha256"][name]} == WRAPPERS and
             set(binary) == set(prior["librariesSha256"]) and
             dependencies == prior["dependenciesSha256"],
             "Only the three bound runtime markers may change from R164 kit")
        artifacts = {}
        for name, checksum in (binary | dependencies).items():
            raw = archive.read("lib/arm64-v8a/" + name)
            need(digest(raw) == checksum and raw[:6] == b"\x7fELF\x02\x01" and
                 struct.unpack_from("<H", raw, 18)[0] == 183,
                 "Signed R165 engine ELF differs: " + name)
            artifacts[name] = raw
    incoming, policies = inherited.android_incoming(selected, incoming_builder.POLICY, prior)
    need(set(policies) == PLATFORMS and
         all({key: value for key, value in policies[platform].items()
              if key not in {"engineId", "runtimeSha256"}} ==
             {key: value for key, value in prior_profiles["profiles"][platform].items()
              if key not in {"engineId", "runtimeSha256"}}
             for platform in PLATFORMS),
         "Approved player counts, profile hashes or core hashes changed")
    files: dict[str, bytes] = {}
    origins: dict[str, str] = {}

    def add(name: str, raw: bytes, origin: str) -> None:
        need(name not in files and ".." not in Path(name).parts,
             "Duplicate or unsafe kit path")
        files[name] = raw
        origins[name] = origin

    for name, raw in sorted(artifacts.items()):
        add("artifacts/" + name, raw, "exact signed R165 APK")
    add("engines-apk.json", engine_raw, "exact signed R165 APK")
    add("incoming.json", encoded(incoming), "pinned additive server manifest policy")
    add("profile-policies.json", encoded({"profiles": policies, "exactModeApprovalRequired": True}),
        "unchanged R164 policy with R165 owner identities")
    add("references/reviewed-78-mode-provenance.json", provenance, "reviewed mode provenance")
    add("references/r141-server-return.json", historical_return, "historical reference only")
    add("references/r162-video-bridge-dex-receipt.json", prior_dex_proof,
        "inherited N64 video bridge proof from R164 kit")
    add("proofs/final-apk-proof.json", proof_path.read_bytes(),
        "R165 signed APK proof; no APK content")
    add("proofs/unsigned-package.json", (package / "unsigned-package.json").read_bytes(),
        "R165 six-entry APK scope and per-entry hashes")
    add("proofs/dex35-host-exit-receipt.json", dex_receipt.read_bytes(),
        "R165 single-class N64 host-exit proof")
    add("proofs/native-visual-receipt.json", native_receipt.read_bytes(),
        "R165 scoped carousel and Mega Drive effect proof")
    for name, raw in sorted(licenses.items()):
        add(name, raw, "unchanged R164 free-software license and attribution")
    summary = {
        "schema": "station.r165.combined-private-kit.v1", "revision": "R165",
        "apkSha256": proof["apkSha256"], "apkBytes": proof["apkBytes"],
        "baselineApkSha256": BASE_SHA, "referenceKitR164Sha256": R164_KIT_SHA,
        "independentEngineIds": [row["engineId"] for row in selected],
        "binaryCount": 6, "distinctDependencyCount": 21,
        "librariesSha256": binary, "dependenciesSha256": dependencies,
        "onlineAeBridgeSha256Preserved": BRIDGE_SHA,
        "enginesApkSha256": digest(engine_raw),
        "dex35Sha256": DEX35_SHA, "dex36Sha256Preserved": DEX36_SHA,
        "carouselSha256": assembly["nativeLibrarySha256"],
        "preservedDexPartitions": 39, "changedDex": ["classes35.dex"],
        "n64OnlineOptions": next(row for row in selected if row["platform"] == "n64")["options"],
        "n64AndroidProfileSha256": policies["n64"]["profileSha256"],
        "approvedModesReferenceCount": 78,
        "psxHleApprovalLedgerIncluded": False,
        "n64CompleteReviewDecisionsReferenceCount": 321,
        "n64CompleteReviewEditionsReferenceCount": 157,
        "n64CompleteReviewLedgerSha256": N64_REVIEW_SHA,
        "n64CompleteReviewPreparerSha256": N64_PREPARER_SHA,
        "serverApplied": False, "physicalGameplayValidated": False,
        "containsApkRomBiosKeySerialOrRawLogs": False,
        "attributionFilesIncluded": True,
    }
    add("MANIFESTO-KIT.json", encoded(summary), "R165 private server delivery metadata")
    readme = (
        "R165: saida N64 confirmada e carrossel visual com efeito Mega Drive auditado.\n"
        "APK assinado SHA-256: " + proof["apkSha256"] + "\n"
        "Conferir seis ELF de motor, vinte e uma dependencias, quatro engineIds e engines-apk.json.\n"
        "Somente DEX35 mudou entre as 40 particoes; DEX36 e ponte N64 continuam R164.\n"
        "N64 continua cpu=dynarec, video=glide64mk2 e inputDelay=2.\n"
        "Cadastrar aditivamente pela rotina vigente, com baseline fresca, scan.lock e recibo.\n"
        "Transferir os 78 modos e 321 decisoes N64 para os novos IDs conforme ledger vigente.\n"
        "Aprovacoes PSX HLE por edicao sao separadas e nao estao neste kit.\n"
        "As tres licencas/avisos de software livre sao copias exatas do kit R164.\n"
        "Este ZIP nao contem APK, ROM, BIOS, chave ou dados de aparelho.\n"
    )
    add("LEIA-ME.txt", readme.encode("utf-8"), "scoped server handoff")
    file_manifest = {"schemaVersion": 1, "revision": "R165", "files": {
        name: {"sha256": digest(raw), "bytes": len(raw), "origin": origins[name]}
        for name, raw in files.items()
    }}
    add("MANIFESTO-ARQUIVOS.json", encoded(file_manifest), "per-file SHA-256 checks")
    need(len(files) == 43 and set(name for name in files if name.startswith("licenses/")) == set(licenses),
         "R165 kit file scope differs")
    out.mkdir(parents=True)
    target = out / "Kit-Servidor-TurboStations-R165-Independentes.zip"
    with zipfile.ZipFile(target, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, raw in sorted(files.items()):
            output.writestr(name, raw)
    with zipfile.ZipFile(target) as output:
        need(set(output.namelist()) == set(files) and
             all(digest(output.read(name)) == digest(raw) for name, raw in files.items()),
             "R165 private kit ZIP readback failed")
    need(target.stat().st_size < 100_000_000, "R165 private kit exceeds 100 MB")
    receipt = {**summary, "zipSha256": sha(target), "zipBytes": target.stat().st_size,
               "fileCount": len(files), "manifestFileCount": len(files) - 1,
               "manifestHashesVerified": True, "apkSignatureVerified": True,
               "androidZipAlignment16KiB": True}
    (out / "server-kit-receipt-r165.json").write_bytes(encoded(receipt))
    return {"revision": "R165", "zipSha256": receipt["zipSha256"],
            "zipBytes": receipt["zipBytes"], "fileCount": len(files),
            "serverApplied": False}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("apk", "package", "prior-kit", "app-repo", "server-repo",
                 "private-helper", "dex-receipt", "native-receipt", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.apk, args.package, args.prior_kit,
                           args.app_repo, args.server_repo, args.private_helper,
                           args.dex_receipt, args.native_receipt, args.out),
                     ensure_ascii=False))
