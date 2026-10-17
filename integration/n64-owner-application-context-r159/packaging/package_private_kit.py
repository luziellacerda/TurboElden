"""Export a byte-exact R159 independent-engine kit from the signed APK.

The kit contains engine ELF files, registry data and public handoff references.
It contains no APK, game content, signing material or device data.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import zipfile


sys.dont_write_bytecode = True
APK_SHA = "4837be706f9ac1f913b4844353741f70c539674e125ae185239611cf5faac2b3"
APK_BYTES = 2_715_106_319
BASE_SHA = "fc1d2d983deb5179979a4aebac7fa64b1740da1c62ae46bfc0d1f4c11eb46cf0"
PRIOR_KIT_SHA = "240ecba97b9b6773f3177eb127f8a065bfc8f6993f6f4918869e1ffb4b5acbd3"
NATIVE_VERIFIER_SHA = "34f05839f81450c5312208603a4eb678033c9a1f7f263a7dffa329f133004655"
INCOMING_BUILDER_SHA = "362bcae9d8915f7f43aac4c48d06b35bdf57efc88d6acb9199aa06e3a0231426"
N64_REVIEW_SHA = "7aa9da840b8dcc1a9ea3404280d9866dfc7e1b15377228be6cb8bf4800e17908"
N64_PREPARER_SHA = "4fcc40012d77624b82874239669a71bddb7dca880d47e67f72970c7673c70b7c"
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
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
    stage = out / "kit-stage-r159"
    target = out / "Kit-Servidor-TurboStations-R159-Independentes.zip"
    receipt_path = out / "server-kit-receipt-r159.json"
    need(out.is_dir() and not any(path.exists() for path in (stage, target, receipt_path)),
         "Fresh private R159 kit output paths required")
    need(apk.stat().st_size == APK_BYTES and sha(apk) == APK_SHA and
         sha(prior_kit) == PRIOR_KIT_SHA and sha(private_helper) == NATIVE_VERIFIER_SHA,
         "Exact R159 APK, R157 reference kit and native verifier required")
    incoming_path = server_repo / "docs/station-android/r128/operator/build_incoming_manifest.py"
    review = app_repo / "docs/server/n64-completo-20261014/complete-review.json"
    preparer = app_repo / "docs/server/n64-completo-20261014/prepare_complete_n64.py"
    need(sha(incoming_path) == INCOMING_BUILDER_SHA and sha(review) == N64_REVIEW_SHA and
         sha(preparer) == N64_PREPARER_SHA, "Pinned server builder or N64 review differs")
    native = load(private_helper, "r159_native_set_verifier")
    incoming_builder = load(incoming_path, "r159_incoming_builder")
    package_path = package / "unsigned-package.json"
    proof_path = package / "final-apk-proof.json"
    assembly = json.loads(package_path.read_text("utf-8"))
    proof = json.loads(proof_path.read_text("utf-8"))
    dex_proof = json.loads(dex_receipt.read_text("utf-8"))
    need(assembly.get("schema") == "station.r159.n64-owner.package.v1" and
         assembly.get("passed") is True and assembly.get("baselineApkSha256") == BASE_SHA and
         assembly.get("entryCount") == 13860 and assembly.get("preservedEntryCount") == 13855 and
         assembly.get("changedDexPartitions") == ["classes35.dex"] and
         assembly.get("dexReceiptSha256") == sha(dex_receipt) and
         proof.get("schema") == "station.r159.n64-owner.final.v1" and
         proof.get("passed") is True and proof.get("packageRevision") == "R159" and
         proof.get("apkSha256") == APK_SHA and proof.get("apkBytes") == APK_BYTES and
         proof.get("signatureCertificateSha256") == CERT_SHA and
         proof.get("v2") is proof.get("v3") is proof.get("zipAlignment16KiB") is True and
         proof.get("replacedEntries") == assembly.get("replacedEntries") and
         proof.get("preservedEntryCount") == 13855 and
         dex_proof.get("schema") == "station.n64.owner-application-context.r159.v2" and
         dex_proof.get("passed") is True and dex_proof.get("candidateDexSha256") ==
         assembly["expectedEntrySha256"]["classes35.dex"] and
         dex_proof.get("unrelatedClassesUnchanged") == 607,
         "Exact scoped R159 package and signer proofs required")
    with zipfile.ZipFile(prior_kit) as previous:
        prior = json.loads(previous.read("MANIFESTO-KIT.json"))
        provenance = previous.read("references/reviewed-78-mode-provenance.json")
        historical_return = previous.read("references/r141-server-return.json")
        licenses = {name: previous.read(name) for name in previous.namelist()
                    if name.startswith("licenses/") and not name.endswith("/")}
    need(prior.get("schema") == "station.r157.independent-private-kit.v1" and
         prior.get("apkSha256") != APK_SHA and prior.get("binaryCount") == 6 and
         prior.get("distinctDependencyCount") == 20 and
         prior.get("approvedModesReferenceCount") == 78 and
         prior.get("psxHleApprovalsAdded") == 0 and
         len(json.loads(provenance)["modes"]) == 78 and
         set(licenses) == {"licenses/COPYING.GPL-2.0", "licenses/COPYING.GPL-3.0",
                           "licenses/NOTICE.md"}, "R157 reference kit policy differs")
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13860 and
             {name: entry_sha(archive, name) for name in names} == assembly["expectedEntrySha256"],
             "Signed APK entries differ from reviewed R159 assembly")
        engine_raw = archive.read("assets/station-online/engines.json")
        registry = json.loads(engine_raw)
        selected = [row for row in registry["engines"] if row["platform"] in PLATFORMS]
        need(len(selected) == 4 and len({row["platform"] for row in selected}) == 4,
             "Exactly four independent engine descriptors required")
        binary, dependencies = native.native_sets(selected)
        need(len(binary) == 6 and len(dependencies) == 20 and
             set(binary) == set(prior["librariesSha256"]) and
             dependencies == prior["dependenciesSha256"] and
             {name for name in binary if binary[name] != prior["librariesSha256"][name]} == WRAPPERS,
             "Only three runtime markers may differ from reviewed reference kit")
        artifacts = {}
        for name, checksum in (binary | dependencies).items():
            raw = archive.read("lib/arm64-v8a/" + name)
            need(digest(raw) == checksum and raw[:6] == b"\x7fELF\x02\x01" and
                 struct.unpack_from("<H", raw, 18)[0] == 183,
                 "Signed APK ELF identity differs: " + name)
            artifacts[name] = raw
    incoming, policies = incoming_builder.incoming({"engines": selected})
    stage.mkdir()
    files = {}

    def write(name: str, raw: bytes, origin: str) -> None:
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        files[name] = {"sha256": digest(raw), "bytes": len(raw), "origin": origin}

    for name, raw in sorted(artifacts.items()):
        write("artifacts/" + name, raw, "exact signed R159 APK")
    write("engines-apk.json", engine_raw, "exact signed R159 APK")
    write("incoming.json", encoded(incoming), "pinned current additive server builder")
    write("profile-policies.json", encoded({"profiles": policies, "exactModeApprovalRequired": True}),
          "unchanged independent owner policy")
    write("references/reviewed-78-mode-provenance.json", provenance, "reviewed original mode provenance")
    write("references/r141-server-return.json", historical_return, "historical reference, not R159 application")
    write("proofs/final-apk-proof.json", proof_path.read_bytes(), "R159 signed APK proof")
    write("proofs/dex-receipt.json", dex_receipt.read_bytes(), "one-class N64 owner repair proof")
    for name, raw in sorted(licenses.items()):
        write(name, raw, "unchanged owner license")
    summary = {
        "schema": "station.r159.independent-private-kit.v1", "revision": "R159",
        "apkSha256": APK_SHA, "apkBytes": APK_BYTES, "baselineApkSha256": BASE_SHA,
        "referenceKitR157Sha256": PRIOR_KIT_SHA,
        "independentEngineIds": [row["engineId"] for row in selected],
        "binaryCount": 6, "distinctDependencyCount": 20,
        "librariesSha256": binary, "dependenciesSha256": dependencies,
        "enginesApkSha256": digest(engine_raw),
        "dex35Sha256": assembly["expectedEntrySha256"]["classes35.dex"],
        "dex10Sha256": assembly["expectedEntrySha256"]["classes10.dex"],
        "carouselSha256": assembly["expectedEntrySha256"]["lib/arm64-v8a/libturbo_carousel.so"],
        "preservedDexPartitions": 39, "changedDex": ["classes35.dex"],
        "unrelatedClassesPreserved": 607, "preservedRetroArchDescriptors": 9,
        "approvedModesReferenceCount": 78, "psxHleApprovalsAdded": 0,
        "n64CompleteReviewDecisionsReferenceCount": 321,
        "n64CompleteReviewEditionsReferenceCount": 157,
        "n64CompleteReviewLedgerSha256": N64_REVIEW_SHA,
        "n64CompleteReviewPreparerSha256": N64_PREPARER_SHA,
        "n64CompleteReviewCopiedIntoKit": False,
        "androidVersionCodePreservedFromR158": True,
        "serverApplied": False, "physicalGameplayValidated": False,
        "containsApkRomBiosKeySerialOrRawLogs": False,
    }
    write("MANIFESTO-KIT.json", encoded(summary), "R159 server delivery metadata")
    readme = (
        "R159: corrigido o marcador de posse da sessao N64 no primeiro start do CoreService.\n"
        "APK assinado SHA-256: " + APK_SHA + "\n"
        "Conferir quatro engineIds, seis ELF, vinte dependencias e engines-apk.json exatos.\n"
        "Aplicar pela rotina vigente do servidor com baseline fresca e scan.lock.\n"
        "A primeira transacao vincula 78 modos revisados; apos o recibo, a segunda\n"
        "baseline e as 321 decisoes N64 revisadas vinculam as 157 edicoes ao novo motor.\n"
        "Os documentos de revisao N64 estao no Git do app, nao neste ZIP.\n"
        "Este kit nao comprova aplicacao no servidor nem partida fisica.\n"
    )
    write("LEIA-ME.txt", readme.encode("utf-8"), "scoped server handoff")
    (stage / "MANIFESTO-ARQUIVOS.json").write_bytes(encoded(
        {"schemaVersion": 1, "revision": "R159", "files": files}))
    with zipfile.ZipFile(target, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(stage).as_posix())
    with zipfile.ZipFile(target) as output:
        need(set(output.namelist()) == {*files, "MANIFESTO-ARQUIVOS.json"} and
             all(digest(output.read(name)) == item["sha256"] for name, item in files.items()),
             "R159 private kit ZIP readback failed")
    need(target.stat().st_size < 100_000_000, "Private kit exceeds 100 MB")
    summary.update(zipSha256=sha(target), zipBytes=target.stat().st_size,
                   fileCount=len(files) + 1, manifestFileCount=len(files), manifestHashesVerified=True)
    receipt_path.write_bytes(encoded(summary))
    return {"revision": "R159", "zipSha256": summary["zipSha256"],
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
