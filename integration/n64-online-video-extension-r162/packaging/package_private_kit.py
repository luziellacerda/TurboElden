"""Export a byte-exact R162 independent-engine kit from the signed APK.

The kit contains engine ELF files, registry data and public handoff references.
It contains no APK, game content, signing material or device data.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import zipfile


sys.dont_write_bytecode = True
BASE_SHA = "66f429d47af725a6767064c3623ee10c505171a85fbc8c0a50dc9e5bc4f80081"
PRIOR_KIT_SHA = "bcfbe393e6e560cd04f8994de3267fd7ff76487c3e9f234aa5bd20abd7f0eadf"
NATIVE_VERIFIER_SHA = "34f05839f81450c5312208603a4eb678033c9a1f7f263a7dffa329f133004655"
INCOMING_BUILDER_SHA = "362bcae9d8915f7f43aac4c48d06b35bdf57efc88d6acb9199aa06e3a0231426"
N64_REVIEW_SHA = "7aa9da840b8dcc1a9ea3404280d9866dfc7e1b15377228be6cb8bf4800e17908"
N64_PREPARER_SHA = "4fcc40012d77624b82874239669a71bddb7dca880d47e67f72970c7673c70b7c"
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
R157_ANDROID_N64_SHA = "688d519ae641911804fe3286e6b5f50cc7f8c06c42ccb1be36781f0fb067b83d"
R161_ANDROID_N64_SHA = "ef8bfd6e6287a205da4f73422a194c7fc05b9246363a8311501a6efa3bca2b63"
BRIDGE = "libstation_ae_bridge.so"
PLATFORMS = {"psx", "n64", "gamecube", "wii"}
WRAPPERS = {"libstation_psx_online.so", "libstation_mupen64plus_runtime.so",
            "libstation_dolphin_runtime.so"}


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


def android_canonical(config: dict) -> bytes:
    """Mirror StationMultiplayerProfile.canonical/JSONObject.quote for pinned ASCII options."""
    ordered = {key: config[key] for key in
               ("schemaVersion", "controllerProfile", "devices", "coreOptions")}
    need(all(ord(char) < 128 for value in (ordered["controllerProfile"], ordered["coreOptions"])
             for char in value), "Profile requires a new Android quote compatibility proof")
    raw = json.dumps(ordered, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return raw.replace("/", "\\/").encode("utf-8")


def android_incoming(selected: list[dict], legacy_policy: dict, prior: dict) -> tuple[dict, dict]:
    """R128 manifest shape with unchanged R161 profile policy and Android quote rule."""
    need(len(selected) == 4 and {row["platform"] for row in selected} == set(legacy_policy),
         "Exactly four independent engines required")
    need(prior["n64AndroidProfileSha256"] == R161_ANDROID_N64_SHA,
         "Pinned R161 Android N64 profile differs")
    engines = copy.deepcopy(selected)
    policies = {}
    for row in engines:
        platform = row["platform"]
        name, maximum, old_python_sha = legacy_policy[platform]
        need(row.get("controllerProfiles") == [name] and
             row.get("maximumPlayers") == maximum and
             row.get("recoveryProtocol") == "station-stream.v3" and
             row.get("launchReady") is True and
             row["engineId"].endswith(row["runtimeSha256"][:12]),
             "R161 engine owner policy differs: " + platform)
        config = dict(schemaVersion=1, controllerProfile=name,
                      devices=[1] * maximum, coreOptions=row["options"])
        profile_sha = digest(android_canonical(config))
        need(profile_sha == (R161_ANDROID_N64_SHA if platform == "n64" else old_python_sha),
             "Approved Android profile changed: " + platform)
        row["controllerProfiles"] = [dict(controllerProfile=name, maximumPlayers=maximum,
                                          configuration=config)]
        row["requireExplicitEngineModes"] = True
        policies[platform] = dict(controllerProfile=name, profileSha256=profile_sha,
                                  maximumPlayers=maximum, engineId=row["engineId"],
                                  coreSha256=row["coreSha256"],
                                  runtimeSha256=row["runtimeSha256"])
    return dict(schemaVersion=1, engines=engines), policies


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Pinned kit helper unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def build(apk: Path, package: Path, dex_receipt: Path, prior_kit: Path,
          app_repo: Path, server_repo: Path, private_helper: Path, out: Path) -> dict:
    apk = apk.resolve(strict=True)
    package = package.resolve(strict=True)
    dex_receipt = dex_receipt.resolve(strict=True)
    prior_kit = prior_kit.resolve(strict=True)
    app_repo = app_repo.resolve(strict=True)
    server_repo = server_repo.resolve(strict=True)
    private_helper = private_helper.resolve(strict=True)
    out = out.resolve()
    stage = out / "kit-stage-r162"
    target = out / "Kit-Servidor-TurboStations-R162-Independentes.zip"
    receipt_path = out / "server-kit-receipt-r162.json"
    need(out.is_dir() and not any(path.exists() for path in (stage, target, receipt_path)),
         "Fresh private R162 kit output paths required")
    need(sha(prior_kit) == PRIOR_KIT_SHA and sha(private_helper) == NATIVE_VERIFIER_SHA,
         "Exact R161 reference kit and native verifier required")
    incoming_path = server_repo / "docs/station-android/r128/operator/build_incoming_manifest.py"
    review = app_repo / "docs/server/n64-completo-20261014/complete-review.json"
    preparer = app_repo / "docs/server/n64-completo-20261014/prepare_complete_n64.py"
    need(sha(incoming_path) == INCOMING_BUILDER_SHA and sha(review) == N64_REVIEW_SHA and
         sha(preparer) == N64_PREPARER_SHA, "Pinned server builder or N64 review differs")
    native = load(private_helper, "r162_native_set_verifier")
    incoming_builder = load(incoming_path, "r162_incoming_builder")
    package_path = package / "unsigned-package.json"
    proof_path = package / "final-apk-proof.json"
    assembly = json.loads(package_path.read_text("utf-8"))
    proof = json.loads(proof_path.read_text("utf-8"))
    dex_proof = json.loads(dex_receipt.read_text("utf-8"))
    need(assembly.get("schema") == "station.r162.n64-online-video-extension.package.v1" and
         assembly.get("passed") is True and assembly.get("baselineApkSha256") == BASE_SHA and
         assembly.get("entryCount") == 13861 and assembly.get("preservedEntryCount") == 13854 and
         assembly.get("changedDexPartitions") == ["classes35.dex", "classes36.dex"] and
         assembly.get("n64OnlineOptions", "").count("cpu=dynarec\n") == 1 and
         assembly.get("n64OnlineOptions", "").count("inputDelay=2\n") == 1 and
         assembly.get("taskRemovalChanged") is False and
         assembly.get("inputDelayChanged") is False and
         assembly.get("dexReceiptSha256") == sha(dex_receipt) and
         proof.get("schema") == "station.r162.n64-online-video-extension.final.v1" and
         proof.get("passed") is True and proof.get("packageRevision") == "R162" and
         proof.get("apkSha256") == sha(apk) and proof.get("apkBytes") == apk.stat().st_size and
         proof.get("baseApkSha256") == BASE_SHA and
         proof.get("signatureCertificateSha256") == CERT_SHA and
         proof.get("v2") is proof.get("v3") is proof.get("zipAlignment16KiB") is True and
         proof.get("replacedEntries") == assembly.get("replacedEntries") and
         proof.get("preservedEntryCount") == 13854 and
         dex_proof.get("schema") == "station.n64.online-video-extension.r162.v1" and
         dex_proof.get("passed") is True and
         all(dex_proof["partitions"][name]["candidateDexSha256"] ==
             assembly["expectedEntrySha256"][name]
             for name in ("classes35.dex", "classes36.dex")) and
         assembly["expectedEntrySha256"].get("lib/arm64-v8a/libstation_ae_bridge.so") ==
             assembly.get("addedOnlineAeBridgeSha256"),
         "Exact scoped R162 package and signer proofs required")
    apk_sha = proof["apkSha256"]
    apk_bytes = proof["apkBytes"]
    with zipfile.ZipFile(prior_kit) as previous:
        prior = json.loads(previous.read("MANIFESTO-KIT.json"))
        prior_registry = json.loads(previous.read("engines-apk.json"))
        provenance = previous.read("references/reviewed-78-mode-provenance.json")
        historical_return = previous.read("references/r141-server-return.json")
        licenses = {name: previous.read(name) for name in previous.namelist()
                    if name.startswith("licenses/") and not name.endswith("/")}
    need(prior.get("schema") == "station.r161.independent-private-kit.v1" and
         prior.get("apkSha256") == BASE_SHA and prior.get("binaryCount") == 6 and
         prior.get("distinctDependencyCount") == 20 and
         prior.get("approvedModesReferenceCount") == 78 and
         prior.get("n64AndroidProfileSha256") == R161_ANDROID_N64_SHA and
         prior.get("psxHleApprovalsAdded") == 0 and
         len(json.loads(provenance)["modes"]) == 78 and
         set(licenses) == {"licenses/COPYING.GPL-2.0", "licenses/COPYING.GPL-3.0",
                           "licenses/NOTICE.md"}, "R161 reference kit policy differs")
    prior_selected = {row["platform"]: row for row in prior_registry["engines"]
                      if row["platform"] in PLATFORMS}
    need(set(prior_selected) == PLATFORMS and
         prior_selected["n64"]["options"].count("cpu=dynarec\n") == 1 and
         prior_selected["n64"]["options"].count("inputDelay=2\n") == 1,
         "Exact R161 N64 profile reference required")
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13861 and
             {name: entry_sha(archive, name) for name in names} == assembly["expectedEntrySha256"],
             "Signed APK entries differ from reviewed R162 assembly")
        engine_raw = archive.read("assets/station-online/engines.json")
        registry = json.loads(engine_raw)
        selected = [row for row in registry["engines"] if row["platform"] in PLATFORMS]
        need(len(selected) == 4 and len({row["platform"] for row in selected}) == 4,
             "Exactly four independent engine descriptors required")
        n64 = next(row for row in selected if row["platform"] == "n64")
        need(n64["options"] == assembly["n64OnlineOptions"] and
             n64["options"].count("cpu=dynarec\n") == 1 and
             n64["options"].count("inputDelay=2\n") == 1,
             "N64 R162 registry must retain exact Dynarec and input delay")
        need(all(row["options"] == prior_selected[row["platform"]]["options"]
                 for row in selected),
             "Engine options changed from R161")
        expected_dependencies = {**prior["dependenciesSha256"],
                                 BRIDGE: assembly["addedOnlineAeBridgeSha256"]}
        need(all({k: v for k, v in prior_selected[platform].items()
                  if k not in {"engineId", "runtimeSha256", "dependencySha256"}} ==
                 {k: v for k, v in row.items()
                  if k not in {"engineId", "runtimeSha256", "dependencySha256"}}
                 for row in selected for platform in [row["platform"]]) and
             all(prior_selected[platform]["dependencySha256"] == row["dependencySha256"]
                 for row in selected for platform in [row["platform"]] if platform != "n64") and
             n64["dependencySha256"] ==
                 {**prior_selected["n64"]["dependencySha256"],
                  BRIDGE: assembly["addedOnlineAeBridgeSha256"]},
             "R162 registry changed owner policy outside N64 online bridge dependency")
        # The pinned R141 verifier intentionally requires exactly twenty dependencies.
        # Validate the unchanged R161 set with that verifier, then append only the
        # reviewed online VideoExt bridge using its native name/hash validation.
        baseline_selected = copy.deepcopy(selected)
        next(row for row in baseline_selected if row["platform"] == "n64")["dependencySha256"].pop(BRIDGE)
        binary, dependencies = native.native_sets(baseline_selected)
        native.native_pin(dependencies, BRIDGE, assembly["addedOnlineAeBridgeSha256"])
        need(len(binary) == 6 and len(dependencies) == 21 and
             set(binary) == set(prior["librariesSha256"]) and
             dependencies == expected_dependencies and
             {name for name in binary if binary[name] != prior["librariesSha256"][name]} == WRAPPERS,
             "Only three runtime markers and one N64 dependency may differ from R161 kit")
        artifacts = {}
        for name, checksum in (binary | dependencies).items():
            raw = archive.read("lib/arm64-v8a/" + name)
            need(digest(raw) == checksum and raw[:6] == b"\x7fELF\x02\x01" and
                 struct.unpack_from("<H", raw, 18)[0] == 183,
                 "Signed APK ELF identity differs: " + name)
            artifacts[name] = raw
        bridge = artifacts[BRIDGE]
        need(digest(bridge) == assembly["addedOnlineAeBridgeSha256"] and
             bridge[:6] == b"\x7fELF\x02\x01" and
             struct.unpack_from("<H", bridge, 18)[0] == 183,
             "Signed APK online AE bridge differs")
    incoming, policies = android_incoming(selected, incoming_builder.POLICY, prior)
    stage.mkdir()
    files = {}

    def write(name: str, raw: bytes, origin: str) -> None:
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        files[name] = {"sha256": digest(raw), "bytes": len(raw), "origin": origin}

    for name, raw in sorted(artifacts.items()):
        write("artifacts/" + name, raw, "exact signed R162 APK")
    write("engines-apk.json", engine_raw, "exact signed R162 APK")
    write("incoming.json", encoded(incoming), "pinned current additive server builder")
    write("profile-policies.json", encoded({"profiles": policies, "exactModeApprovalRequired": True}),
          "retained R161 independent owner policy and online options")
    write("references/reviewed-78-mode-provenance.json", provenance, "reviewed original mode provenance")
    write("references/r141-server-return.json", historical_return, "historical reference, not R162 application")
    write("proofs/final-apk-proof.json", proof_path.read_bytes(), "R162 signed APK proof")
    write("proofs/dex-receipt.json", dex_receipt.read_bytes(), "two-partition N64 VideoExt proof")
    for name, raw in sorted(licenses.items()):
        write(name, raw, "unchanged owner license")
    summary = {
        "schema": "station.r162.independent-private-kit.v1", "revision": "R162",
        "apkSha256": apk_sha, "apkBytes": apk_bytes, "baselineApkSha256": BASE_SHA,
        "referenceKitR161Sha256": PRIOR_KIT_SHA,
        "independentEngineIds": [row["engineId"] for row in selected],
        "binaryCount": 6, "distinctDependencyCount": 21,
        "newN64DependencyCount": 1,
        "onlineAeBridgeSha256": digest(bridge),
        "offlineAeBridgeSha256Preserved": assembly["offlineAeBridgeSha256Preserved"],
        "librariesSha256": binary, "dependenciesSha256": dependencies,
        "enginesApkSha256": digest(engine_raw),
        "dex35Sha256": assembly["expectedEntrySha256"]["classes35.dex"],
        "dex36Sha256": assembly["expectedEntrySha256"]["classes36.dex"],
        "dex10Sha256": assembly["expectedEntrySha256"]["classes10.dex"],
        "carouselSha256": assembly["expectedEntrySha256"]["lib/arm64-v8a/libturbo_carousel.so"],
        "preservedDexPartitions": 38, "changedDex": ["classes35.dex", "classes36.dex"],
        "n64OnlineOptions": assembly["n64OnlineOptions"],
        "n64AndroidProfileSha256": policies["n64"]["profileSha256"],
        "r157OldAndroidProfileSha256": R157_ANDROID_N64_SHA,
        "nonN64ApprovedProfileHashesPreserved": True,
        "unrelatedClassesPreserved": sum(row["unrelatedClassesUnchanged"]
                                         for row in dex_proof["partitions"].values()),
        "preservedRetroArchDescriptors": 9,
        "approvedModesReferenceCount": 78, "psxHleApprovalsAdded": 0,
        "n64CompleteReviewDecisionsReferenceCount": 321,
        "n64CompleteReviewEditionsReferenceCount": 157,
        "n64CompleteReviewLedgerSha256": N64_REVIEW_SHA,
        "n64CompleteReviewPreparerSha256": N64_PREPARER_SHA,
        "n64CompleteReviewCopiedIntoKit": False,
        "androidVersionCodePreservedFromR161": True,
        "serverApplied": False, "physicalGameplayValidated": False,
        "containsApkRomBiosKeySerialOrRawLogs": False,
    }
    write("MANIFESTO-KIT.json", encoded(summary), "R162 server delivery metadata")
    readme = (
        "R162: candidato delimitado para VideoExt do N64 online.\n"
        "APK assinado SHA-256: " + apk_sha + "\n"
        "Conferir quatro engineIds, seis ELF de motor, vinte e uma dependencias (incluindo a ponte Android) e engines-apk.json exatos.\n"
        "No N64, manter cpu=dynarec com inputDelay=2 e registrar o novo fingerprint; nao misturar com R161.\n"
        "A ponte libstation_ae_bridge.so e do APK Android; nao substitui libae-bridge.so offline.\n"
        "Aplicar pela rotina vigente do servidor com baseline fresca e scan.lock.\n"
        "A primeira transacao vincula 78 modos revisados; apos o recibo, a segunda\n"
        "baseline e as 321 decisoes N64 revisadas vinculam as 157 edicoes ao novo motor.\n"
        "Os documentos de revisao N64 estao no Git do app, nao neste ZIP.\n"
        "Este kit nao comprova aplicacao no servidor nem partida fisica.\n"
    )
    write("LEIA-ME.txt", readme.encode("utf-8"), "scoped server handoff")
    (stage / "MANIFESTO-ARQUIVOS.json").write_bytes(encoded(
        {"schemaVersion": 1, "revision": "R162", "files": files}))
    with zipfile.ZipFile(target, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(stage).as_posix())
    with zipfile.ZipFile(target) as output:
        need(set(output.namelist()) == {*files, "MANIFESTO-ARQUIVOS.json"} and
             all(digest(output.read(name)) == item["sha256"] for name, item in files.items()),
             "R162 private kit ZIP readback failed")
    need(target.stat().st_size < 100_000_000, "Private kit exceeds 100 MB")
    summary.update(zipSha256=sha(target), zipBytes=target.stat().st_size,
                   fileCount=len(files) + 1, manifestFileCount=len(files), manifestHashesVerified=True)
    receipt_path.write_bytes(encoded(summary))
    return {"revision": "R162", "zipSha256": summary["zipSha256"],
            "zipBytes": summary["zipBytes"], "fileCount": summary["fileCount"],
            "serverApplied": False}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("apk", "package", "dex-receipt", "prior-kit", "app-repo",
                 "server-repo", "private-helper", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.apk, args.package, args.dex_receipt, args.prior_kit,
                           args.app_repo, args.server_repo, args.private_helper, args.out),
                     ensure_ascii=False))
