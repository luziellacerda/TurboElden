"""Replace the Sambox S default avatar with the Turborama T.

Only assets/resources/profile_mockup.png in TESTE.
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
ASSET = "assets/resources/profile_mockup.png"
ICON = P / "brand-login" / "assets" / "profile_mockup.png"
OLD_S_SHA = "7f15496857ab308de9e6831dd7a1ce673745585a13d3dd1517f7553948d2742c"


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


def main():
    if sha(STABLE) != STABLE_SHA:
        raise RuntimeError("Stable APK hash mismatch; aborting")
    if not BASE.is_file():
        raise RuntimeError("TESTE APK missing")
    if not ICON.is_file():
        raise RuntimeError("T profile icon missing")
    png = ICON.read_bytes()
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("profile icon is not PNG")
    new_hash = hashlib.sha256(png).hexdigest()
    if new_hash == OLD_S_SHA:
        raise RuntimeError("new icon still hashes as the Sambox S")
    tmp = SIDE / "tmp-profile-icon"
    tmp.mkdir(exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(tmp)
    unsigned = SIDE / "unsigned-profile-icon.apk"
    aligned = SIDE / "aligned-profile-icon.apk"
    unsigned.unlink(missing_ok=True)
    aligned.unlink(missing_ok=True)
    print("graft", ASSET, "bytes", len(png), "sha", new_hash)
    with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(unsigned, "w", allowZip64=True) as out:
        found = False
        for info in src.infolist():
            name = info.filename
            if name.startswith("META-INF/"):
                continue
            lower = name.lower()
            if lower.endswith(".pup") or lower.endswith("keys.txt"):
                raise RuntimeError("refusing to package " + name)
            if name == ASSET:
                put(out, info, png)
                found = True
            else:
                put(out, info, src.read(name))
        if not found:
            raise RuntimeError("TESTE APK missing " + ASSET)
    print("zipalign")
    run(TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned)
    unsigned.unlink(missing_ok=True)
    staged = SIDE / "TurboramaStation-TESTE-profile-t-signed.apk"
    print("sign")
    run(
        JAVA, "-jar", str(TOOLS / "lib" / "apksigner.jar"), "sign",
        "--ks", KEYSTORE, "--ks-key-alias", "androiddebugkey",
        "--ks-pass", "pass:android", "--key-pass", "pass:android",
        "--out", staged, aligned,
    )
    run(JAVA, "-jar", str(TOOLS / "lib" / "apksigner.jar"), "verify", staged)
    aligned.unlink(missing_ok=True)
    shutil.copy2(staged, BASE)
    with zipfile.ZipFile(BASE) as a:
        packed = a.read(ASSET)
        packed_hash = hashlib.sha256(packed).hexdigest()
        if packed_hash != new_hash:
            raise RuntimeError("packed profile icon hash mismatch")
        if packed_hash == OLD_S_SHA:
            raise RuntimeError("packed icon still the Sambox S")
    record = {
        "stable_sha256_unchanged": sha(STABLE) == STABLE_SHA,
        "old_1_0_untouched": True,
        "xbox_dex_untouched": True,
        "output": str(BASE),
        "sha256": sha(BASE),
        "bytes": BASE.stat().st_size,
        "asset": ASSET,
        "profile_icon_sha256": packed_hash,
        "old_sambox_s_sha256": OLD_S_SHA,
        "note": "default profile avatar is Turborama T when the user has no photo",
    }
    (SIDE / "profile-icon-result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
