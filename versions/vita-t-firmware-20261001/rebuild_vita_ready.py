"""Graft VitaEntryActivity and official 3.74 PUP assets into TESTE.

Firmware stays out of git. Does not touch Cemu 0.5.2, PS2, FBNeo, or old 1.0.
"""
from pathlib import Path
import copy, hashlib, json, os, shutil, struct, subprocess, zipfile, zlib

P = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
SIDE = P / "side-by-side-turborama-20261001"
SRC_DIR = P / "emulator-completion"
STABLE = Path(r"E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk")
STABLE_SHA = "7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b"
BASE = SIDE / "TurboramaStation-TESTE-lado-a-lado.apk"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
JAVAC = JAVA.with_name("javac.exe")
SDK = Path(r"G:\Android\Sdk\platforms\android-34\android.jar")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
KEYSTORE = Path(r"C:\Users\Admin\.android\debug.keystore")
DEX_NAME = "classes24.dex"
FIRMWARE_DIR = SRC_DIR / "firmware"
FIRMWARE_ASSETS = (
    ("assets/psvita-firmware/PSVita-3.74-preinstalled.PUP", "PSVita-3.74-preinstalled.PUP", "339d1439eb329cfbd1a936f0a1563458e0555ef52975486b2844e24b6049e33e", 128798720),
    ("assets/psvita-firmware/PSVita-3.74-main.PUP", "PSVita-3.74-main.PUP", "6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf", 133834240),
    ("assets/psvita-firmware/PSVita-3.74-fonts.PUP", "PSVita-3.74-fonts.PUP", "c3c03fc7363dd573d90e5157629bf11551f434b283cc898d9ffc71dd716b791c", 56778752),
)
ALLOWED_PUP = {item[0] for item in FIRMWARE_ASSETS}


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def fix_dex(data: bytes) -> bytes:
    if len(data) < 32 or data[:4] != b"dex\n":
        raise RuntimeError("d8 did not emit a dex")
    buf = bytearray(data)
    buf[12:32] = hashlib.sha1(buf[32:]).digest()
    struct.pack_into("<I", buf, 8, zlib.adler32(buf[12:]) & 0xFFFFFFFF)
    return bytes(buf)


def put(z, old, data):
    info = copy.copy(old) if isinstance(old, zipfile.ZipInfo) else zipfile.ZipInfo(old)
    if not isinstance(old, zipfile.ZipInfo):
        stored = old.endswith((".so", ".dex", ".mp4", ".arsc", ".PUP", ".pup"))
        info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
    info.extra = b""
    if info.compress_type == zipfile.ZIP_STORED:
        align = 16384 if info.filename.endswith(".so") else 4
        off = z.fp.tell() + 30 + len(info.filename.encode())
        if off % align:
            pad = (-(off + 4)) % align
            info.extra = struct.pack("<HH", 0xFFFF, pad) + bytes(pad)
    z.writestr(info, data)


def compile_bridge(tmp: Path) -> bytes:
    classes_dir = SRC_DIR / "vita-classes-ready"
    dex_dir = SRC_DIR / "vita-dex-ready"
    if classes_dir.exists():
        shutil.rmtree(classes_dir)
    if dex_dir.exists():
        shutil.rmtree(dex_dir)
    classes_dir.mkdir()
    dex_dir.mkdir()
    sources = [SRC_DIR / "VitaBootstrap.java", SRC_DIR / "VitaEntryActivity.java"]
    for src in sources:
        if not src.is_file():
            raise RuntimeError("missing " + str(src))
    run(JAVAC, "-encoding", "UTF-8", "-source", "8", "-target", "8",
        "-cp", str(SDK), "-d", str(classes_dir), *sources)
    class_files = list(classes_dir.rglob("*.class"))
    if not class_files:
        raise RuntimeError("javac produced no classes")
    run(JAVA, "-Djava.io.tmpdir=" + str(tmp), "-cp", str(TOOLS / "lib" / "d8.jar"),
        "com.android.tools.r8.D8", "--min-api", "26", "--lib", str(SDK),
        "--output", str(dex_dir), *class_files)
    data = fix_dex((dex_dir / "classes.dex").read_bytes())
    for needle in (b"VitaEntryActivity", b"ensureReady", b"PSVita-3.74-main.PUP", b"psvita-firmware", b"Jogador", b"initial_setup_completed", b"vita3k_app"):
        if needle not in data:
            raise RuntimeError("bridge dex missing " + needle.decode())
    if b".PUP" in data and b"http://dus01.psp2.update.playstation.net" in data:
        raise RuntimeError("firmware URL leaked into dex")
    return data


def main():
    if sha(STABLE) != STABLE_SHA:
        raise RuntimeError("Stable APK hash mismatch; aborting")
    if not BASE.is_file():
        raise RuntimeError("TESTE APK missing")
    tmp = SIDE / "tmp-vita-ready"
    tmp.mkdir(exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(tmp)
    firmware = []
    for asset, name, digest, size in FIRMWARE_ASSETS:
        path = FIRMWARE_DIR / name
        if not path.is_file():
            raise RuntimeError("missing firmware " + name)
        data = path.read_bytes()
        if len(data) != size:
            raise RuntimeError("firmware size mismatch " + name)
        got = hashlib.sha256(data).hexdigest()
        if got != digest:
            raise RuntimeError("firmware hash mismatch " + name)
        firmware.append((asset, data, digest))
        print("firmware", name, "bytes", size)
    dex = compile_bridge(tmp)
    (SRC_DIR / "vita-dex-ready" / "classes.dex").write_bytes(dex)
    shutil.copy2(SRC_DIR / "VitaEntryActivity.java", P / "platform-media-refresh" / "psvita" / "VitaEntryActivity.java")
    unsigned = SIDE / "unsigned-vita-ready.apk"
    aligned = SIDE / "aligned-vita-ready.apk"
    unsigned.unlink(missing_ok=True)
    aligned.unlink(missing_ok=True)
    print("graft", DEX_NAME, "bytes", len(dex), "plus", len(firmware), "PUP assets")
    with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(unsigned, "w", allowZip64=True) as out:
        found = False
        for info in src.infolist():
            if info.filename.startswith("META-INF/"):
                continue
            lower = info.filename.lower()
            if lower.endswith(".pup"):
                if info.filename not in ALLOWED_PUP:
                    raise RuntimeError("refusing unexpected firmware: " + info.filename)
                continue
            if info.filename.startswith("assets/psvita-firmware/"):
                continue
            if info.filename == DEX_NAME:
                put(out, DEX_NAME, dex)
                found = True
            else:
                put(out, info, src.read(info.filename))
        if not found:
            raise RuntimeError("TESTE APK missing " + DEX_NAME)
        for asset, data, digest in firmware:
            put(out, asset, data)
    print("zipalign")
    run(TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned)
    unsigned.unlink(missing_ok=True)
    staged = SIDE / "TurboramaStation-TESTE-vita-ready-signed.apk"
    print("sign")
    run(
        JAVA, "-jar", str(TOOLS / "lib" / "apksigner.jar"), "sign",
        "--alignment-preserved", "true",
        "--ks", str(KEYSTORE), "--ks-key-alias", "androiddebugkey",
        "--ks-pass", "pass:android", "--key-pass", "pass:android",
        "--out", str(staged), aligned,
    )
    run(JAVA, "-jar", str(TOOLS / "lib" / "apksigner.jar"), "verify", str(staged))
    aligned.unlink(missing_ok=True)
    bak_dex = SIDE / "classes24-pre-vita-ready.dex"
    if not bak_dex.exists():
        with zipfile.ZipFile(BASE) as z:
            bak_dex.write_bytes(z.read(DEX_NAME))
    shutil.copy2(staged, BASE)
    packed = {}
    with zipfile.ZipFile(BASE) as a:
        names = a.namelist()
        unexpected = [n for n in names if n.lower().endswith(".pup") and n not in ALLOWED_PUP]
        if unexpected:
            raise RuntimeError("unexpected PUP in signed APK: " + ", ".join(unexpected))
        for asset, name, digest, size in FIRMWARE_ASSETS:
            data = a.read(asset)
            got = hashlib.sha256(data).hexdigest()
            if len(data) != size or got != digest:
                raise RuntimeError("packed firmware mismatch " + name)
            packed[name] = {"bytes": len(data), "sha256": got}
        dex_hash = hashlib.sha256(a.read(DEX_NAME)).hexdigest()
    record = {
        "stable_sha256_unchanged": sha(STABLE) == STABLE_SHA,
        "old_1_0_untouched": True,
        "firmware_bundled": True,
        "output": str(BASE),
        "sha256": sha(BASE),
        "bytes": BASE.stat().st_size,
        "classes24_sha256": dex_hash,
        "firmware": packed,
        "note": "TESTE APK includes official 3.74 PUPs; VitaEntry copies them to setup and installs on first open",
    }
    (SIDE / "vita-ready-result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
