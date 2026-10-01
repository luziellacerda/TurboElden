"""Replace only libturbo_carousel.so in TESTE with the two-tone cell laser palette.

Does not touch Cemu 0.5.2, PS2, FBNeo, Xbox DEX, videos, or old 1.0.
"""
from pathlib import Path
import copy, hashlib, json, os, shutil, struct, subprocess, zipfile

P = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
SIDE = P / "side-by-side-turborama-20261001"
STABLE = Path(r"E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk")
STABLE_SHA = "7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b"
BASE = SIDE / "TurboramaStation-TESTE-lado-a-lado.apk"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
KEYSTORE = Path(r"C:\Users\Admin\.android\debug.keystore")
MODULE = "lib/arm64-v8a/libturbo_carousel.so"
EXPECTED = {
    "naomi2": ("FF0911FF", "0070FFFF"),
    "model2": ("FF0911FF", "0070FFFF"),
    "Psvita": ("FFFFFFFF", "0070FFFF"),
    "Nintendo DS": ("FFFFFFFF", "FF0911FF"),
    "Nintendo 64": ("FFD500FF", "FFFFFFFF"),
    "Nintendo 64 - BR": ("FFD500FF", "FFFFFFFF"),
}


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


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


def verify_header():
    text = (P / "laser_assets.h").read_text(encoding="utf-8")
    missing = []
    for key, (hue, secondary) in EXPECTED.items():
        needle = "{" + json.dumps(key) + ",0x" + hue + ","
        if needle not in text or ",0x" + secondary + "}," not in text:
            missing.append(key)
        else:
            line = [ln for ln in text.splitlines() if ln.startswith("{" + json.dumps(key) + ",")]
            if not line or not line[0].endswith(",0x" + secondary + "},"):
                missing.append(key + ":" + (line[0] if line else "absent"))
    if missing:
        raise RuntimeError("laser_assets.h missing two-tone entries: " + ", ".join(missing))


def main():
    if sha(STABLE) != STABLE_SHA:
        raise RuntimeError("Stable APK hash mismatch; aborting")
    verify_header()
    lib = (P / "libturbo_carousel.so").read_bytes()
    tmp = SIDE / "tmp-laser"
    tmp.mkdir(exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(tmp)
    unsigned = SIDE / "unsigned-laser.apk"
    aligned = SIDE / "aligned-laser.apk"
    unsigned.unlink(missing_ok=True)
    aligned.unlink(missing_ok=True)
    print("graft", MODULE, "bytes", len(lib))
    with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(unsigned, "w", allowZip64=True) as out:
        found = False
        for info in src.infolist():
            if info.filename.startswith("META-INF/"):
                continue
            if info.filename == MODULE:
                put(out, MODULE, lib)
                found = True
            else:
                put(out, info, src.read(info.filename))
        if not found:
            raise RuntimeError("TESTE APK missing " + MODULE)
    print("zipalign")
    run(TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned)
    unsigned.unlink(missing_ok=True)
    staged = SIDE / "TurboramaStation-TESTE-laser-signed.apk"
    print("sign")
    run(
        JAVA, "-jar", TOOLS / "lib" / "apksigner.jar", "sign",
        "--ks", KEYSTORE, "--ks-key-alias", "androiddebugkey",
        "--ks-pass", "pass:android", "--key-pass", "pass:android",
        "--out", staged, aligned,
    )
    run(JAVA, "-jar", TOOLS / "lib" / "apksigner.jar", "verify", staged)
    aligned.unlink(missing_ok=True)
    shutil.copy2(staged, BASE)
    with zipfile.ZipFile(BASE) as a:
        so_hash = hashlib.sha256(a.read(MODULE)).hexdigest()
    record = {
        "stable_sha256_unchanged": sha(STABLE) == STABLE_SHA,
        "old_1_0_untouched": True,
        "xbox_dex_untouched": True,
        "output": str(BASE),
        "sha256": sha(BASE),
        "bytes": BASE.stat().st_size,
        "native_module_sha256": hashlib.sha256(lib).hexdigest(),
        "apk_module_sha256": so_hash,
        "palette": {k: list(v) for k, v in EXPECTED.items()},
        "note": "carousel outer laser two-tone; Naomi2/Model2 red+blue; Vita white+blue; DS white+red; N64/N64BR yellow+white",
    }
    (SIDE / "laser-colors-result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
