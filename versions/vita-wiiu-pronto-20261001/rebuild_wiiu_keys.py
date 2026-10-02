"""Graft WiiUEntryActivity so Cemu stages owner keys.txt on open.

Does not embed keys. Does not touch Cemu 0.5.2 stable APK, PS2, FBNeo, or old 1.0.
"""
from pathlib import Path
import copy, hashlib, json, os, shutil, struct, subprocess, zipfile, zlib

P = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
SIDE = P / "side-by-side-turborama-20261001"
SRC_DIR = P / "wiiu-integration" / "java" / "org" / "emulationstation" / "frontend"
STABLE = Path(r"E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk")
STABLE_SHA = "7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b"
BASE = SIDE / "TurboramaStation-TESTE-lado-a-lado.apk"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
JAVAC = JAVA.with_name("javac.exe")
SDK = Path(r"G:\Android\Sdk\platforms\android-34\android.jar")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
KEYSTORE = Path(r"C:\Users\Admin\.android\debug.keystore")
DEX_NAME = "classes20.dex"


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
        info.compress_type = zipfile.ZIP_STORED if old.endswith((".so", ".dex", ".mp4", ".arsc")) else zipfile.ZIP_DEFLATED
    info.extra = b""
    if info.compress_type == zipfile.ZIP_STORED:
        align = 16384 if info.filename.endswith(".so") else 4
        off = z.fp.tell() + 30 + len(info.filename.encode())
        if off % align:
            pad = (-(off + 4)) % align
            info.extra = struct.pack("<HH", 0xFFFF, pad) + bytes(pad)
    z.writestr(info, data)


def compile_bridge(tmp: Path) -> bytes:
    classes_dir = SIDE / "wiiu-keys-classes"
    dex_dir = SIDE / "wiiu-keys-dex"
    if classes_dir.exists():
        shutil.rmtree(classes_dir)
    if dex_dir.exists():
        shutil.rmtree(dex_dir)
    classes_dir.mkdir()
    dex_dir.mkdir()
    sources = [SRC_DIR / "WiiUBootstrap.java", SRC_DIR / "WiiUArchive.java", SRC_DIR / "WiiUEntryActivity.java"]
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
    for needle in (b"WiiUEntryActivity", b"ensureKeys", b"keys.txt", b"Staged keys.txt"):
        if needle not in data:
            raise RuntimeError("bridge dex missing " + needle.decode())
    if b"d7b00402659ba2abd2cb0db27fa2b656" in data:
        raise RuntimeError("key material leaked into dex")
    return data


def main():
    if sha(STABLE) != STABLE_SHA:
        raise RuntimeError("Stable APK hash mismatch; aborting")
    if not BASE.is_file():
        raise RuntimeError("TESTE APK missing")
    tmp = SIDE / "tmp-wiiu-keys"
    tmp.mkdir(exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(tmp)
    dex = compile_bridge(tmp)
    unsigned = SIDE / "unsigned-wiiu-keys.apk"
    aligned = SIDE / "aligned-wiiu-keys.apk"
    unsigned.unlink(missing_ok=True)
    aligned.unlink(missing_ok=True)
    print("graft", DEX_NAME, "bytes", len(dex))
    with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(unsigned, "w", allowZip64=True) as out:
        found = False
        for info in src.infolist():
            if info.filename.startswith("META-INF/"):
                continue
            name = info.filename.replace("\\", "/").lower()
            if name.endswith("keys.txt") or name.endswith(".pup"):
                raise RuntimeError("refusing to package secrets: " + info.filename)
            if info.filename == DEX_NAME:
                put(out, DEX_NAME, dex)
                found = True
            else:
                put(out, info, src.read(info.filename))
        if not found:
            raise RuntimeError("TESTE APK missing " + DEX_NAME)
    print("zipalign")
    run(TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned)
    unsigned.unlink(missing_ok=True)
    staged = SIDE / "TurboramaStation-TESTE-wiiu-keys-signed.apk"
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
    shutil.copy2(staged, BASE)
    with zipfile.ZipFile(BASE) as a:
        names = a.namelist()
        if any(n.lower().endswith("keys.txt") or n.lower().endswith(".pup") for n in names):
            raise RuntimeError("secrets present in signed APK")
        dex_hash = hashlib.sha256(a.read(DEX_NAME)).hexdigest()
    record = {
        "stable_sha256_unchanged": sha(STABLE) == STABLE_SHA,
        "old_1_0_untouched": True,
        "keys_bundled": False,
        "output": str(BASE),
        "sha256": sha(BASE),
        "bytes": BASE.stat().st_size,
        "classes20_sha256": dex_hash,
        "note": "WiiUEntry copies owner-staged keys.txt into Cemu on open",
    }
    (SIDE / "wiiu-keys-result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
