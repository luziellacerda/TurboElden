"""Package the private R166 server handoff from the reviewed signed APK.

The R165 kit is the policy and binary baseline. Only the three bound runtime
markers may change; all cores, dependencies, profiles, options and RetroArch
descriptors must remain identical. This does not deploy to the server and the
ZIP deliberately excludes the APK, game content, device data and credentials.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import zipfile


sys.dont_write_bytecode = True
BASE_APK_SHA = "9e7ab2441e9d75568d5d2b741b4a0ed42e9a2d9f823698c0f39dccdcb7c19145"
PRIOR_KIT_SHA = "2e260ba80f93a0a9f65c1e2dca2f0632ce29b321dd895ad84d737e5a5628179b"
CERT_SHA = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
R162_POLICY_SHA = "d4c4353eeb1fa2ecc215f6b08c33831c1cf768a42e590de0417b239a567bd722"
DEX36_SHA = "a1c12b34c5eba4060707235c86dea3bbdfa59ef52264afc7ebaaa5d73231287c"
BRIDGE_SHA = "3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986"
CAROUSEL_SHA = "3f20f862bed0d73668fdbc0fa06e7009011cbf8ea32c2cfff96029c2b8f23fc8"
FRONTEND_SHA = "438789d8e328ef6416b990ec64a41f96747a32714745088d16f88c65839a888d"
PLATFORMS = ("psx", "n64", "gamecube", "wii")
WRAPPERS = {"libstation_psx_online.so", "libstation_mupen64plus_runtime.so",
            "libstation_dolphin_runtime.so"}
REPLACED = {"classes35.dex", "assets/station-online/engines.json",
            *("lib/arm64-v8a/" + name for name in WRAPPERS)}
SOURCE_FILES = (
    "integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxLaunch.java",
    "integration/psx-dependency-r166/recipe/build_dex.py",
    "integration/psx-dependency-r166/recipe/package_candidate.py",
    "integration/psx-dependency-r166/recipe/sign_private.py",
)
TOOL_ROOT = Path("F:/TurboStations-Backup-Completo-20261011/ferramentas")
TOOL_SHA = {
    "jdk17/bin/java.exe": "1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406",
    "android-build-tools-35/lib/apksigner.jar": "00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7",
    "android-build-tools-35/zipalign.exe": "aa2475ce201962b871fb8daec020da03fd6292c9c1f422cd0fe2e39b20d4f673",
}


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def entry_sha(archive: zipfile.ZipFile, name: str) -> str:
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def load_policy(path: Path):
    need(sha(path) == R162_POLICY_SHA, "Pinned Android profile policy helper differs")
    spec = importlib.util.spec_from_file_location("r166_profile_policy", path)
    need(spec is not None and spec.loader is not None, "Android profile policy helper missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
         CERT_SHA in result.stdout.lower(), "R166 APK signature or certificate differs")
    result = subprocess.run([str(align), "-c", "-P", "16", "4", str(apk)],
                            capture_output=True, text=True, timeout=300)
    need(result.returncode == 0, "R166 APK lacks 16 KiB ZIP alignment")


def load_prior(prior_kit: Path) -> tuple[dict, dict, dict, dict, dict[str, bytes]]:
    need(sha(prior_kit) == PRIOR_KIT_SHA, "Exact R165 private kit required")
    with zipfile.ZipFile(prior_kit) as archive:
        names = archive.namelist()
        manifest = json.loads(archive.read("MANIFESTO-ARQUIVOS.json"))
        need(len(names) == len(set(names)) == 43 and
             set(names) == {*manifest["files"], "MANIFESTO-ARQUIVOS.json"},
             "R165 private kit inventory differs")
        for name, meta in manifest["files"].items():
            raw = archive.read(name)
            need(digest(raw) == meta["sha256"] and len(raw) == meta["bytes"],
                 "R165 kit file differs: " + name)
        prior = json.loads(archive.read("MANIFESTO-KIT.json"))
        registry = json.loads(archive.read("engines-apk.json"))
        incoming = json.loads(archive.read("incoming.json"))
        profiles = json.loads(archive.read("profile-policies.json"))
        reused = {name: archive.read(name) for name in names
                  if name.startswith(("references/", "licenses/"))}
        reused["references/r165-final-apk-proof.json"] = archive.read("proofs/final-apk-proof.json")
        reused["references/r165-dex35-host-exit-receipt.json"] = archive.read(
            "proofs/dex35-host-exit-receipt.json")
        reused["references/r165-native-visual-receipt.json"] = archive.read(
            "proofs/native-visual-receipt.json")
    need(prior.get("schema") == "station.r165.combined-private-kit.v1" and
         prior.get("apkSha256") == BASE_APK_SHA and prior.get("binaryCount") == 6 and
         prior.get("distinctDependencyCount") == 21 and
         prior.get("dex36Sha256Preserved") == DEX36_SHA and
         prior.get("onlineAeBridgeSha256Preserved") == BRIDGE_SHA and
         prior.get("carouselSha256") == CAROUSEL_SHA and
         prior.get("serverApplied") is False and
         set(profiles.get("profiles", {})) == set(PLATFORMS) and
         profiles.get("exactModeApprovalRequired") is True and
         incoming.get("schemaVersion") == 1 and
         len(incoming.get("engines", [])) == 4 and
         len(registry.get("engines", [])) == 13 and
         set(name for name in reused if name.startswith("licenses/")) ==
         {"licenses/COPYING.GPL-2.0", "licenses/COPYING.GPL-3.0",
          "licenses/NOTICE.md"},
         "R165 independent-engine policy reference differs")
    return prior, registry, incoming, profiles, reused


def verify_proofs(apk: Path, package: Path, dex_dir: Path, repo: Path) -> tuple[dict, dict, dict]:
    package_path = package / "unsigned-package.json"
    proof_path = package / "final-apk-proof.json"
    dex_path = dex_dir / "dex-receipt.json"
    assembly = json.loads(package_path.read_text("utf-8"))
    proof = json.loads(proof_path.read_text("utf-8"))
    dex = json.loads(dex_path.read_text("utf-8"))
    expected = assembly.get("expectedEntrySha256")
    revision = assembly.get("sourceCommit")
    need(assembly.get("schema") == "station.psx.dependency.package.r166.v1" and
         assembly.get("passed") is True and
         assembly.get("baselineApkSha256") == BASE_APK_SHA and
         assembly.get("entryCount") == 13_861 and
         assembly.get("preservedEntryCount") == 13_856 and
         set(assembly.get("replacedEntries", [])) == REPLACED and
         assembly.get("changedDexPartitions") == ["classes35.dex"] and
         assembly.get("preservedDexPartitions") == 39 and
         assembly.get("classes36Sha256Preserved") == DEX36_SHA and
         assembly.get("onlineAeBridgeSha256Preserved") == BRIDGE_SHA and
         assembly.get("carouselSha256Preserved") == CAROUSEL_SHA and
         assembly.get("retainedOwnerPolicies") is True and
         assembly.get("retainedRetroDescriptors") == 9 and
         assembly.get("newThreadsTimersOrPolling") is False and
         assembly.get("extraPerFrameDrawCalls") == 0 and
         assembly.get("visualLibraryPreserved") is True and
         isinstance(expected, dict) and len(expected) == 13_861 and
         all(re.fullmatch(r"[0-9a-f]{64}", str(value)) for value in expected.values()) and
         isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision) and
         assembly.get("dexReceiptSha256") == sha(dex_path) and
         proof.get("schema") == "station.psx.dependency.final.r166.v1" and
         proof.get("passed") is True and proof.get("packageRevision") == "R166" and
         proof.get("apkSha256") == sha(apk) and
         proof.get("apkBytes") == apk.stat().st_size and
         proof.get("baseApkSha256") == BASE_APK_SHA and
         proof.get("unsignedPackageReceiptSha256") == sha(package_path) and
         proof.get("dexReceiptSha256") == sha(dex_path) and
         proof.get("signatureCertificateSha256") == CERT_SHA and
         proof.get("v2") is proof.get("v3") is proof.get("zipAlignment16KiB") is True and
         set(proof.get("replacedEntries", [])) == REPLACED and
         proof.get("preservedEntryCount") == 13_856 and
         proof.get("changedDexPartitions") == ["classes35.dex"] and
         proof.get("preservedDexPartitions") == 39 and
         proof.get("sourceCommit") == revision and
         proof.get("onlineEngineIds") == assembly.get("onlineEngineIds") and
         proof.get("runtimeMarkers") == assembly.get("runtimeMarkers") and
         proof.get("classes35Sha256") == expected.get("classes35.dex") and
         proof.get("classes36Sha256Preserved") == DEX36_SHA and
         proof.get("onlineAeBridgeSha256Preserved") == BRIDGE_SHA and
         proof.get("carouselSha256Preserved") == CAROUSEL_SHA and
         dex.get("schema") == "station.psx.dependency.dex.r166.v1" and
         dex.get("passed") is True and dex.get("sourceCommit") == revision and
         dex.get("candidateDexSha256") == expected.get("classes35.dex") and
         dex.get("modifiedTypes") ==
         ["Lorg/emulationstation/frontend/netplay/StationPsxLaunch;"] and
         dex.get("unrelatedClassesUnchanged") == 607 and
         dex.get("changedDexPartitions") == ["classes35.dex"] and
         sha(dex_dir / "classes35.dex") == expected.get("classes35.dex"),
         "Exact signed R166 five-entry assembly and single-class proof required")
    source_hashes = assembly.get("sourceFilesSha256")
    need(isinstance(source_hashes, dict) and set(source_hashes) == set(SOURCE_FILES),
         "R166 productive source list differs")
    for name, checksum in source_hashes.items():
        need(sha(repo / name) == checksum and
             digest(subprocess.check_output(["git", "-C", str(repo), "show",
                                             revision + ":" + name])) == checksum,
             "R166 productive source changed from frozen commit: " + name)
    verify_signature(apk)
    return assembly, proof, dex


def build(apk: Path, package: Path, dex_dir: Path, prior_kit: Path,
          app_repo: Path, out: Path) -> dict:
    apk = apk.resolve(strict=True)
    package = package.resolve(strict=True)
    dex_dir = dex_dir.resolve(strict=True)
    prior_kit = prior_kit.resolve(strict=True)
    app_repo = app_repo.resolve(strict=True)
    out = out.resolve()
    need(not out.exists() and not out.is_relative_to(app_repo),
         "Fresh private output directory outside source Git required")
    assembly, proof, dex = verify_proofs(apk, package, dex_dir, app_repo)
    prior, old_registry, old_incoming, old_profiles, reused = load_prior(prior_kit)
    policy = load_policy(app_repo /
                         "integration/n64-online-video-extension-r162/packaging/package_private_kit.py")
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 13_861 and
             {name: entry_sha(archive, name) for name in names} ==
             assembly["expectedEntrySha256"],
             "Signed R166 APK differs from reviewed five-entry assembly")
        engine_raw = archive.read("assets/station-online/engines.json")
        registry = json.loads(engine_raw)
        selected = {row["platform"]: row for row in registry["engines"]
                    if row["platform"] in PLATFORMS}
        old_selected = {row["platform"]: row for row in old_registry["engines"]
                        if row["platform"] in PLATFORMS}
        need(len(registry["engines"]) == 13 and
             set(selected) == set(old_selected) == set(PLATFORMS) and
             [row for row in registry["engines"] if row["platform"] not in PLATFORMS] ==
             [row for row in old_registry["engines"] if row["platform"] not in PLATFORMS] and
             {platform: row["engineId"] for platform, row in selected.items()} ==
             proof["onlineEngineIds"] and
             all({key: value for key, value in row.items()
                  if key not in {"engineId", "runtimeSha256"}} ==
                 {key: value for key, value in old_selected[platform].items()
                  if key not in {"engineId", "runtimeSha256"}}
                 for platform, row in selected.items()),
             "Engine policies, dependencies or nine RetroArch descriptors changed")
        binary: dict[str, str] = {}
        dependencies: dict[str, str] = {}
        for platform in PLATFORMS:
            row = selected[platform]
            old = old_selected[platform]
            need(row["engineId"] != old["engineId"] and
                 row["engineId"].endswith(row["runtimeSha256"][:12]) and
                 row["runtimeSha256"] != old["runtimeSha256"],
                 "R166 bound runtime identity was not refreshed: " + platform)
            for name_key, hash_key in (("library", "coreSha256"),
                                       ("runtimeLibrary", "runtimeSha256")):
                name, checksum = row[name_key], row[hash_key]
                need(re.fullmatch(r"lib[A-Za-z0-9_-]+\.so", name) is not None,
                     "Unsafe independent engine library name")
                if name in binary:
                    need(binary[name] == checksum, "Conflicting shared engine library")
                binary[name] = checksum
            for name, checksum in row["dependencySha256"].items():
                need(re.fullmatch(r"lib[A-Za-z0-9_-]+\.so", name) is not None or
                     name == "libc++_shared.so", "Unsafe dependency library name")
                if name in dependencies:
                    need(dependencies[name] == checksum, "Conflicting shared dependency")
                dependencies[name] = checksum
        need(len(binary) == 6 and len(dependencies) == 21 and
             set(binary) == set(prior["librariesSha256"]) and
             dependencies == prior["dependenciesSha256"] and
             {name for name, checksum in binary.items()
              if checksum != prior["librariesSha256"][name]} == WRAPPERS and
             {selected[p]["runtimeSha256"] for p in ("gamecube", "wii")} ==
             {selected["gamecube"]["runtimeSha256"]} and
             selected["n64"]["dependencySha256"].get("libstation_ae_bridge.so") == BRIDGE_SHA and
             assembly["expectedEntrySha256"].get("classes36.dex") == DEX36_SHA and
             assembly["expectedEntrySha256"].get("lib/arm64-v8a/libturbo_carousel.so") == CAROUSEL_SHA and
             assembly["expectedEntrySha256"].get("lib/arm64-v8a/libstation_frontend.so") == FRONTEND_SHA,
             "Only three bound engine markers may differ from R165 kit")
        artifacts: dict[str, bytes] = {}
        for name, checksum in sorted((binary | dependencies).items()):
            raw = archive.read("lib/arm64-v8a/" + name)
            need(digest(raw) == checksum and raw[:6] == b"\x7fELF\x02\x01" and
                 struct.unpack_from("<H", raw, 18)[0] == 183,
                 "R166 engine ELF differs from signed APK: " + name)
            artifacts[name] = raw
    legacy_policy = {platform: (meta["controllerProfile"], meta["maximumPlayers"],
                                meta["profileSha256"])
                     for platform, meta in old_profiles["profiles"].items()}
    ordered = [selected[platform] for platform in PLATFORMS]
    incoming, policies = policy.android_incoming(ordered, legacy_policy, prior)
    old_incoming_rows = {row["platform"]: row for row in old_incoming["engines"]}
    new_incoming_rows = {row["platform"]: row for row in incoming["engines"]}
    need(set(old_incoming_rows) == set(new_incoming_rows) == set(PLATFORMS) and
         all({key: value for key, value in row.items()
              if key not in {"engineId", "runtimeSha256"}} ==
             {key: value for key, value in old_incoming_rows[platform].items()
              if key not in {"engineId", "runtimeSha256"}}
             for platform, row in new_incoming_rows.items()) and
         all({key: value for key, value in meta.items()
              if key not in {"engineId", "runtimeSha256"}} ==
             {key: value for key, value in old_profiles["profiles"][platform].items()
              if key not in {"engineId", "runtimeSha256"}}
             for platform, meta in policies.items()) and
         all(meta["engineId"] == selected[platform]["engineId"] and
             meta["runtimeSha256"] == selected[platform]["runtimeSha256"]
             for platform, meta in policies.items()),
         "Approved controller profiles or server policy changed")
    files: dict[str, bytes] = {}
    origins: dict[str, str] = {}

    def add(name: str, raw: bytes, origin: str) -> None:
        need(name not in files and not Path(name).is_absolute() and
             ".." not in Path(name).parts and not name.lower().endswith(".apk"),
             "Duplicate, unsafe or APK kit path")
        files[name] = raw
        origins[name] = origin

    for name, raw in sorted(artifacts.items()):
        add("artifacts/" + name, raw, "exact signed R166 APK ELF")
    add("engines-apk.json", engine_raw, "exact signed R166 APK registry")
    add("incoming.json", encoded(incoming), "approved R165 policy with R166 identities")
    add("profile-policies.json",
        encoded({"profiles": policies, "exactModeApprovalRequired": True}),
        "unchanged controller profiles with R166 identities")
    add("proofs/final-apk-proof.json", (package / "final-apk-proof.json").read_bytes(),
        "signed R166 APK hash and certificate proof, without APK")
    add("proofs/unsigned-package.json", (package / "unsigned-package.json").read_bytes(),
        "reviewed five-entry R166 APK scope and per-entry hashes")
    add("proofs/dex35-psx-dependency-receipt.json", (dex_dir / "dex-receipt.json").read_bytes(),
        "single-class PSX correction proof")
    for name, raw in sorted(reused.items()):
        add(name, raw, "unchanged pinned R165 kit reference")
    summary = {
        "schema": "station.r166.psx-dependency-private-kit.v1", "revision": "R166",
        "apkSha256": proof["apkSha256"], "apkBytes": proof["apkBytes"],
        "baselineApkSha256": BASE_APK_SHA, "referenceKitR165Sha256": PRIOR_KIT_SHA,
        "independentEngineIds": [selected[platform]["engineId"] for platform in PLATFORMS],
        "binaryCount": 6, "distinctDependencyCount": 21,
        "librariesSha256": binary, "dependenciesSha256": dependencies,
        "enginesApkSha256": digest(engine_raw),
        "dex35Sha256": assembly["expectedEntrySha256"]["classes35.dex"],
        "dex36Sha256Preserved": DEX36_SHA,
        "onlineAeBridgeSha256Preserved": BRIDGE_SHA,
        "carouselSha256Preserved": CAROUSEL_SHA,
        "preservedDexPartitions": 39, "changedDex": ["classes35.dex"],
        "changedApkEntries": sorted(REPLACED),
        "unchangedApprovedProfilesAndOptions": True,
        "n64OnlineOptions": selected["n64"]["options"],
        "n64AndroidProfileSha256": policies["n64"]["profileSha256"],
        "approvedModesReferenceCount": prior["approvedModesReferenceCount"],
        "psxHleApprovalLedgerIncluded": False,
        "serverApplied": False, "physicalGameplayValidated": False,
        "containsApkRomBiosKeySerialOrRawLogs": False,
        "attributionFilesIncluded": True,
    }
    add("MANIFESTO-KIT.json", encoded(summary), "R166 private server delivery metadata")
    readme = (
        "R166: reparo localizado na validacao de libc++_shared.so antes de iniciar PSX online.\n"
        "APK assinado SHA-256: " + proof["apkSha256"] + "\n"
        "Conferir os 27 ELF, os quatro engineIds, engines-apk.json e todos os hashes.\n"
        "DEX35 mudou em uma classe PSX; N64, Dolphin, perfis, opcoes e 39 outros DEX nao mudaram.\n"
        "Os marcadores N64/Dolphin e seus IDs mudaram porque vinculam o hash do DEX35.\n"
        "Cadastrar os quatro IDs de modo aditivo, mantendo os R165 para retorno.\n"
        "Requalificar nos IDs R166 apenas os modos ativos e aprovados do servidor, incluindo\n"
        "os 23 modos PSX de 19 edicoes exatas; nao aprovar titulos por aproximacao.\n"
        "Usar baseline e ledgers atuais do servidor, transacao com trava e recibo aplicado.\n"
        "Confirmar consulta publica dos IDs/modos antes de testar R166 em telefones.\n"
        "Este ZIP nao aplica nada e nao prova partida Android; nao contem APK, ROM, BIOS,\n"
        "chave, senha, serial nem registros brutos de aparelho.\n"
    )
    add("LEIA-ME.txt", readme.encode("utf-8"), "scoped server handoff")
    file_manifest = {"schemaVersion": 1, "revision": "R166", "files": {
        name: {"sha256": digest(raw), "bytes": len(raw), "origin": origins[name]}
        for name, raw in files.items()
    }}
    add("MANIFESTO-ARQUIVOS.json", encoded(file_manifest), "per-file SHA-256 checks")
    need(len(artifacts) == 27 and len(files) == 45,
         "R166 kit file scope differs")
    out.mkdir(parents=True)
    target = out / "Kit-Servidor-TurboStations-R166-Independentes.zip"
    with zipfile.ZipFile(target, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, raw in sorted(files.items()):
            output.writestr(name, raw)
    with zipfile.ZipFile(target) as output:
        need(set(output.namelist()) == set(files) and
             all(digest(output.read(name)) == digest(raw) for name, raw in files.items()),
             "R166 private kit ZIP readback failed")
    need(target.stat().st_size < 100_000_000, "R166 private kit exceeds 100 MB")
    receipt = {**summary, "zipSha256": sha(target), "zipBytes": target.stat().st_size,
               "fileCount": len(files), "manifestFileCount": len(files) - 1,
               "manifestHashesVerified": True, "apkSignatureVerified": True,
               "androidZipAlignment16KiB": True}
    (out / "server-kit-receipt-r166.json").write_bytes(encoded(receipt))
    return {"revision": "R166", "zipSha256": receipt["zipSha256"],
            "zipBytes": receipt["zipBytes"], "fileCount": len(files),
            "serverApplied": False}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("apk", "package", "dex-dir", "prior-kit", "app-repo", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    args = cli.parse_args()
    print(json.dumps(build(args.apk, args.package, args.dex_dir, args.prior_kit,
                           args.app_repo, args.out), ensure_ascii=False))
