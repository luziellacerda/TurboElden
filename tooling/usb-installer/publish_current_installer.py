"""Publish a verified signed APK to the fixed, on-demand USB installer.

The APK stays in its release directory.  This command updates only the small
installer manifest after checking the release proof and Android signature.
It never contacts a telephone or starts a background process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid


sys.dont_write_bytecode = True

EXPECTED_CERT = "7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825"
PACKAGE = "org.turboramastation.frontend"
MANIFEST_NAME = "turbostations-apk-teste.json"
DEFAULT_INSTALLER = Path("E:/TurboStations-Instalador-Atual")
DEFAULT_TOOLS = Path("F:/TurboStations-Backup-Completo-20261011/ferramentas")
BOOTSTRAP_FILES = (
    "Instalar-TurboStations-USB.exe",
    "Instalar-TurboStations-USB.ps1",
    "Instalar-TurboStations-USB.bat",
    "platform-tools/adb.exe",
    "platform-tools/AdbWinApi.dll",
    "platform-tools/AdbWinUsbApi.dll",
    "platform-tools/NOTICE.txt",
    "platform-tools/source.properties",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON inválido: {path}")
    return value


def run_checked(arguments: list[str], label: str, timeout: int = 900) -> str:
    result = subprocess.run(arguments, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout)
    if result.returncode:
        detail = (result.stdout + "\n" + result.stderr).strip()[-1200:]
        raise RuntimeError(f"{label} falhou: {detail}")
    return result.stdout + "\n" + result.stderr


def verify_apk(apk: Path, proof: dict, tools: Path) -> tuple[str, int, str]:
    revision = proof.get("packageRevision")
    if not isinstance(revision, str) or not re.fullmatch(r"R[0-9]+[A-Za-z0-9._-]*", revision):
        raise ValueError("A prova não identifica uma revisão válida.")
    if proof.get("passed") is not True or proof.get("v2") is not True or \
       proof.get("v3") is not True or proof.get("zipAlignment16KiB") is not True:
        raise ValueError("A assinatura e o alinhamento final não estão aprovados na prova.")
    if proof.get("signatureCertificateSha256", "").lower() != EXPECTED_CERT:
        raise ValueError("A prova não usa o certificado original do aplicativo.")
    if not apk.is_file() or apk.suffix.lower() != ".apk":
        raise FileNotFoundError("APK assinado não encontrado.")
    length = apk.stat().st_size
    if type(proof.get("apkBytes")) is not int or proof["apkBytes"] != length:
        raise ValueError("Tamanho do APK diverge da prova final.")
    actual_hash = sha256(apk)
    if actual_hash != proof.get("apkSha256", "").lower():
        raise ValueError("SHA-256 do APK diverge da prova final.")

    java = tools / "jdk17/bin/java.exe"
    signer = tools / "android-build-tools-35/lib/apksigner.jar"
    align = tools / "android-build-tools-35/zipalign.exe"
    aapt = tools / "android-build-tools-35/aapt.exe"
    if not all(path.is_file() for path in (java, signer, align, aapt)):
        raise FileNotFoundError("Ferramentas Android de verificação não encontradas.")
    signature = run_checked([str(java), "-jar", str(signer), "verify", "--verbose",
                             "--print-certs", str(apk)], "Verificação da assinatura")
    if ("Verified using v2 scheme (APK Signature Scheme v2): true" not in signature or
        "Verified using v3 scheme (APK Signature Scheme v3): true" not in signature or
        EXPECTED_CERT not in signature.lower()):
        raise ValueError("Assinatura ou certificado do APK não corresponde ao original.")
    run_checked([str(align), "-c", "-P", "16", "4", str(apk)],
                "Verificação do alinhamento 16 KiB")
    badging = run_checked([str(aapt), "dump", "badging", str(apk)],
                          "Verificação do pacote Android")
    if not re.search(r"(?m)^package: name='" + re.escape(PACKAGE) + r"'(?:\s|$)", badging):
        raise ValueError("O APK não identifica o pacote oficial do TurboStations.")
    return revision, length, actual_hash


def copy_bootstrap(source: Path, destination: Path) -> None:
    receipt = read_json(source / "installer-receipt-r165.json")
    expected = receipt.get("filesSha256")
    if not isinstance(expected, dict):
        raise ValueError("Recibo do instalador de origem indisponível.")
    for relative in BOOTSTRAP_FILES:
        original = source / relative
        checksum = expected.get(relative.replace("/", "\\"), expected.get(relative))
        if not original.is_file() or not isinstance(checksum, str) or sha256(original) != checksum:
            raise ValueError(f"Instalador de origem não confere: {relative}")
    for relative in BOOTSTRAP_FILES:
        original = source / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha256(target) == sha256(original):
            continue
        temporary = target.with_name(target.name + ".new-" + uuid.uuid4().hex)
        try:
            shutil.copyfile(original, temporary)
            if sha256(temporary) != sha256(original):
                raise ValueError(f"Cópia do instalador diverge: {relative}")
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)


def write_atomic(target: Path, content: bytes) -> None:
    temporary = target.with_name(target.name + ".new-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def publish(apk: Path, proof_path: Path, installer: Path, tools: Path,
            bootstrap: Path | None, warning: str | None) -> dict:
    apk = apk.resolve(strict=True)
    proof_path = proof_path.resolve(strict=True)
    installer = installer.resolve()
    tools = tools.resolve(strict=True)
    repository = Path(__file__).resolve().parents[2]
    if apk.is_relative_to(repository) or installer.is_relative_to(repository):
        raise ValueError("APK e instalador privado devem ficar fora do Git de fontes.")
    proof = read_json(proof_path)
    revision, size, checksum = verify_apk(apk, proof, tools)

    manifest_path = installer / MANIFEST_NAME
    if manifest_path.is_file():
        previous = read_json(manifest_path)
        old_revision = previous.get("revision", "")
        old_match = re.match(r"R([0-9]+)", old_revision)
        new_match = re.match(r"R([0-9]+)", revision)
        if old_match and new_match and int(old_match[1]) > int(new_match[1]):
            raise ValueError("Revisão anterior recusada; o instalador atual foi preservado.")
        if old_revision == revision and previous.get("sha256", "").lower() != checksum:
            raise ValueError("A mesma revisão já aponta para outro APK; publicação recusada.")

    if bootstrap is not None:
        installer.mkdir(parents=True, exist_ok=True)
        copy_bootstrap(bootstrap.resolve(strict=True), installer)
    elif not all((installer / relative).is_file() for relative in BOOTSTRAP_FILES):
        raise FileNotFoundError("Instalador fixo incompleto; informe --bootstrap-from.")

    registered = proof.get("serverRegistered") is True
    stable = proof.get("stable") is True
    default_warning = (f"{revision} pronta para instalar. "
                       + ("Versão estável." if stable else
                          "Versão de teste; confira o cadastro dos motores no servidor."))
    manifest = {
        "schemaVersion": 1,
        "revision": revision,
        "apkPath": str(apk),
        "sha256": checksum,
        "package": PACKAGE,
        "adbPath": "platform-tools/adb.exe",
        "status": "stable" if stable else "test",
        "warning": warning if warning is not None else default_warning,
        "bytes": size,
        "serverBindingsRegistered": registered,
    }
    candidate = installer / ("." + MANIFEST_NAME + ".candidate-" + uuid.uuid4().hex)
    old_content = manifest_path.read_bytes() if manifest_path.is_file() else None
    payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        candidate.write_bytes(payload)
        run_checked(["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy",
                     "Bypass", "-File", str(installer / "Instalar-TurboStations-USB.ps1"),
                     "-ManifestPath", str(candidate), "-ValidateOnly"],
                    "Conferência do pacote no instalador")
        write_atomic(manifest_path, payload)
        try:
            run_checked([str(installer / "Instalar-TurboStations-USB.exe"), "--validate"],
                        "Conferência do instalador final")
        except Exception:
            if old_content is None:
                manifest_path.unlink(missing_ok=True)
            else:
                write_atomic(manifest_path, old_content)
            raise
    finally:
        candidate.unlink(missing_ok=True)
    return {"revision": revision, "apkSha256": checksum,
            "installer": str(installer / "Instalar-TurboStations-USB.exe"),
            "phoneAccess": False, "installationPerformed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--proof", required=True, type=Path)
    parser.add_argument("--installer-dir", type=Path, default=DEFAULT_INSTALLER)
    parser.add_argument("--tools-dir", type=Path, default=DEFAULT_TOOLS)
    parser.add_argument("--bootstrap-from", type=Path)
    parser.add_argument("--warning")
    options = parser.parse_args()
    try:
        result = publish(options.apk, options.proof, options.installer_dir,
                         options.tools_dir, options.bootstrap_from, options.warning)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as error:
        print(f"Instalador atual não foi publicado: {error}", file=sys.stderr)
        sys.exit(1)
