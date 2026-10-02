"""Graft Station classes8 and the old-host transfer in classes5.

classes8 keeps the Station client. classes5 answers old-host cover and game
requests from that client. Does not embed firmware and does not touch the stable Cemu APK.
"""
from pathlib import Path
import copy, hashlib, json, os, shutil, struct, zipfile

P = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
SIDE = P / "side-by-side-turborama-20261001"
WORK = P / "station-security-20261001"
BASE = SIDE / "TurboramaStation-TESTE-lado-a-lado.apk"
BACKUP = SIDE / "TurboramaStation-TESTE-lado-a-lado-pre-station-login.apk"
STAGED = SIDE / "TurboramaStation-TESTE-station-login.apk"
REBUILT = WORK / "dex-work" / "classes8-rebuilt.apk"
REBUILT5 = WORK / "dex-work" / "classes5-rebuilt.apk"
DEX5 = "classes5.dex"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
KEYSTORE = Path(r"C:\Users\Admin\.android\debug.keystore")
DEX_NAME = "classes8.dex"
STABLE = Path(r"E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk")
STABLE_SHA = "7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(args):
    import subprocess
    print("run", args[0].name if isinstance(args[0], Path) else args[0], flush=True)
    subprocess.run([str(a) for a in args], check=True)


def fix_dex(data: bytes) -> bytes:
    if len(data) < 32 or data[:4] != b"dex\n":
        raise RuntimeError("rebuilt file is not a dex")
    buf = bytearray(data)
    buf[12:32] = hashlib.sha1(buf[32:]).digest()
    import zlib
    struct.pack_into("<I", buf, 8, zlib.adler32(buf[12:]) & 0xFFFFFFFF)
    return bytes(buf)


def put(z, old, data):
    info = copy.copy(old) if isinstance(old, zipfile.ZipInfo) else zipfile.ZipInfo(old)
    if not isinstance(old, zipfile.ZipInfo):
        info.compress_type = zipfile.ZIP_STORED if str(old).endswith((".so", ".dex", ".mp4", ".arsc")) else zipfile.ZIP_DEFLATED
    info.extra = b""
    if info.compress_type == zipfile.ZIP_STORED:
        align = 16384 if info.filename.endswith(".so") else 4
        off = z.fp.tell() + 30 + len(info.filename.encode())
        if off % align:
            pad = (-(off + 4)) % align
            info.extra = struct.pack("<HH", 0xFFFF, pad) + bytes(pad)
    z.writestr(info, data)


def load_dex() -> bytes:
    with zipfile.ZipFile(REBUILT) as z:
        data = fix_dex(z.read("classes.dex"))
    required = [
        b"LoginActivity", b"StationAuth", b"wantsCommercial", b"openCommercial",
        b"Conferindo acesso", b"Senha incorreta", b"Bem-vindo", b"AuthSession",
        b"LocalPassword", b"LocalCatalog", b"TurboEdenBridge", b"ThemeInstaller",
        b"station-license-id.txt", b"https://app.lzgames.com.br",
        b"TurboRamaStationAndroid/activate/v1", b"TurboRamaStationAndroid/profile/v1",
        b"stationLogin",
        b"/v1/station/catalog",
        b"/v1/station/covers/",
        b"/v1/station/downloads/authorize",
        b"/v1/station/artifacts/",
    ]
    for needle in required:
        if needle not in data:
            raise RuntimeError("classes8 missing " + needle.decode())
    for banned in (b"miami", b"?e=", b"?s="):
        if banned in data:
            raise RuntimeError("classes8 must not contain " + banned.decode())
    return data


def load_classes5() -> bytes:
    with zipfile.ZipFile(REBUILT5) as z:
        data = fix_dex(z.read("classes.dex"))
    required = (b"StationTransfer", b"HttpBridge", b"GameDownload", b"miami", b"sambox", b"squareweb")
    for needle in required:
        if needle not in data:
            raise RuntimeError("classes5 missing " + needle.decode())
    return data


def main():
    if sha_file(STABLE) != STABLE_SHA:
        raise RuntimeError("Stable Cemu APK hash mismatch; aborting")
    if not BASE.is_file():
        raise RuntimeError("TESTE APK missing")
    dex = load_dex()
    dex5 = load_classes5()
    print("dex8", len(dex), sha_bytes(dex), flush=True)
    print("dex5", len(dex5), sha_bytes(dex5), flush=True)
    unsigned = SIDE / "unsigned-station-login.apk"
    aligned = SIDE / "aligned-station-login.apk"
    unsigned.unlink(missing_ok=True)
    aligned.unlink(missing_ok=True)
    expected = {}
    old_classes8 = None
    old_classes5 = None
    print("graft", flush=True)
    with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(unsigned, "w", allowZip64=True) as out:
        found8 = False
        found5 = False
        for info in src.infolist():
            if info.filename.startswith("META-INF/"):
                continue
            original = src.read(info.filename)
            if info.filename == DEX_NAME:
                found8 = True
                old_classes8 = sha_bytes(original)
                data = dex if original != dex else original
            elif info.filename == DEX5:
                found5 = True
                old_classes5 = sha_bytes(original)
                data = dex5
            else:
                data = original
            expected[info.filename] = sha_bytes(data)
            put(out, info, data)
        if not found8 or old_classes8 is None or not found5 or old_classes5 is None:
            raise RuntimeError("TESTE APK missing classes5.dex or classes8.dex")
        if old_classes8 == sha_bytes(dex) and old_classes5 == sha_bytes(dex5):
            raise RuntimeError("neither Station dex changed")
    print("entries", len(expected), flush=True)
    print("zipalign", flush=True)
    run([TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned])
    unsigned.unlink(missing_ok=True)
    if STAGED.exists():
        STAGED.unlink()
    print("sign", flush=True)
    run([
        JAVA, "-jar", TOOLS / "lib" / "apksigner.jar", "sign",
        "--alignment-preserved", "true",
        "--ks", KEYSTORE, "--ks-key-alias", "androiddebugkey",
        "--ks-pass", "pass:android", "--key-pass", "pass:android",
        "--out", STAGED, aligned,
    ])
    run([JAVA, "-jar", TOOLS / "lib" / "apksigner.jar", "verify", STAGED])
    run([TOOLS / "zipalign.exe", "-c", "-P", "16", "4", STAGED])
    aligned.unlink(missing_ok=True)
    print("compare", flush=True)
    with zipfile.ZipFile(STAGED) as signed:
        names = [n for n in signed.namelist() if not n.startswith("META-INF/")]
        pups = [n for n in names if n.lower().endswith(".pup")]
        base_pups = sorted(n for n in expected if n.lower().endswith(".pup"))
        if sorted(pups) != base_pups:
            raise RuntimeError("PUP set changed: " + ", ".join(sorted(pups)))
        extra = sorted(set(names) - set(expected))
        missing = sorted(set(expected) - set(names))
        if extra or missing:
            raise RuntimeError("zip entries changed extra=%s missing=%s" % (extra, missing))
        changed = []
        for name, digest in expected.items():
            if sha_bytes(signed.read(name)) != digest:
                changed.append(name)
        if changed:
            raise RuntimeError("signed payload drifted: " + ", ".join(changed))
        signed_classes8 = sha_bytes(signed.read(DEX_NAME))
        signed_classes5 = sha_bytes(signed.read(DEX5))
        if signed_classes5 == old_classes5 and signed_classes8 == old_classes8:
            raise RuntimeError("signed Station dexes match the previous apk")
        if signed_classes8 != sha_bytes(dex) and signed_classes8 != old_classes8:
            raise RuntimeError("signed classes8 drifted")
        classes24 = sha_bytes(signed.read("classes24.dex"))
    if not BACKUP.exists():
        print("backup", flush=True)
        shutil.copy2(BASE, BACKUP)
    print("replace canonical", flush=True)
    shutil.copy2(STAGED, BASE)
    record = {
        "staged": str(STAGED),
        "canonical": str(BASE),
        "backup": str(BACKUP),
        "staged_sha256": sha_file(STAGED),
        "staged_bytes": STAGED.stat().st_size,
        "classes8_sha256": sha_bytes(dex),
        "classes8_bytes": len(dex),
        "classes5_sha256": sha_bytes(dex5),
        "classes5_bytes": len(dex5),
        "classes24_sha256": classes24,
        "changed": [DEX5] if sha_bytes(dex) == old_classes8 else [DEX_NAME, DEX5],
        "stable_sha256_unchanged": sha_file(STABLE) == STABLE_SHA,
        "catalog_and_download_not_in_classes8": False,
        "installed": False,
    }
    (WORK / "station-login-result.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("DONE", record["staged_sha256"], record["staged_bytes"], flush=True)


if __name__ == "__main__":
    main()
