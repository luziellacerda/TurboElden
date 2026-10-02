"""Replace Vita3K native engine in TESTE with official continuous Android build.

Java DEX, helper libs and assets stay. Does not touch Cemu 0.5.2, PS2, FBNeo, or old 1.0.
Firmware PUPs and classes24 VitaEntry stay in the APK.
"""
from pathlib import Path
import copy, hashlib, json, os, shutil, struct, subprocess, zipfile

P = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
SIDE = P / "side-by-side-turborama-20261001"
VITA = P / "platform-media-refresh" / "psvita"
STABLE = Path(r"E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk")
STABLE_SHA = "7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b"
BASE = SIDE / "TurboramaStation-TESTE-lado-a-lado.apk"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
KEYSTORE = Path(r"C:\Users\Admin\.android\debug.keystore")
DONOR = VITA / "vita3k-4115.apk"
ENGINE = "lib/arm64-v8a/libVita3K.so"
DONOR_SHA = "b9c7cf96dcc2d5bb0286dbf29676ea6ce4b556bc030b0d7c90ef27db8d8963dc"
JAVA_DEX_SHA = "b80d41d5c544264647408db068affeec4d856c2c8059709a311853d11d649f42"
ENGINE_BUILD = "4115"
ENGINE_COMMIT = "a366df69"
ALLOWED_PUP = {
    "assets/psvita-firmware/PSVita-3.74-preinstalled.PUP",
    "assets/psvita-firmware/PSVita-3.74-main.PUP",
    "assets/psvita-firmware/PSVita-3.74-fonts.PUP",
}
LIBRARY_NAMES = {
    "SPIRV-Tools-shared": "X360V-Tools-shared",
    "androidx.graphics.path": "tvita3kc.graphics.path",
    "datastore_shared_counter": "x360store_shared_counter",
    "file_redirect_hook": "vile_redirect_hook",
    "gsl_alloc_hook": "vsl_alloc_hook",
    "hook_impl": "vhok_impl",
    "main_hook": "vita_hook",
    "c++_shared": "v3c_shared",
}


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def relocate(data: bytes) -> bytes:
    replacements = {b"androidx/": b"tvita3kc/", b"org/libsdl/": b"org/vtsdlx/"}
    for old, new in LIBRARY_NAMES.items():
        replacements[("lib" + old + ".so").encode()] = ("lib" + new + ".so").encode()
    out = data
    for old, new in replacements.items():
        if len(old) != len(new):
            raise RuntimeError("replacement length mismatch " + repr(old))
        out = out.replace(old, new)
    return out


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


def main():
    if sha(STABLE) != STABLE_SHA:
        raise RuntimeError("Stable APK hash mismatch; aborting")
    if not BASE.is_file():
        raise RuntimeError("TESTE APK missing")
    if not DONOR.is_file():
        raise RuntimeError("4115 donor APK missing")
    tmp = SIDE / "tmp-vita-engine"
    tmp.mkdir(exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(tmp)
    donor_sha = sha(DONOR)
    if donor_sha != DONOR_SHA:
        raise RuntimeError("donor hash mismatch")
    with zipfile.ZipFile(DONOR) as z:
        raw = z.read("lib/arm64-v8a/libVita3K.so")
        classes_sha = sha_bytes(z.read("classes.dex"))
    if classes_sha != JAVA_DEX_SHA:
        raise RuntimeError("4115 Java DEX changed; full merge required")
    engine = relocate(raw)
    (SIDE / "libVita3K-4115-reloc.so").write_bytes(engine)
    print("relocated libVita3K", len(engine), sha_bytes(engine), flush=True)
    with zipfile.ZipFile(BASE) as src:
        old_engine = src.read(ENGINE)
        old_classes23 = sha_bytes(src.read("classes23.dex"))
        old_classes24 = sha_bytes(src.read("classes24.dex"))
        old_jni = sha_bytes(src.read("lib/arm64-v8a/libturbo_vita_jni.so"))
        provenance = json.loads(src.read("assets/psvita-integration/provenance.json").decode("utf-8"))
    if old_engine == engine:
        raise RuntimeError("engine already at 4115")
    provenance.update({
        "source": "https://github.com/Vita3K/Vita3K-builds/releases/tag/4115",
        "release_body": "renderer/gl: Honor the hashless-texture-cache config (#4163)",
        "donor_sha256": donor_sha,
        "engine_build": ENGINE_BUILD,
        "engine_commit": ENGINE_COMMIT,
        "libVita3K_sha256": sha_bytes(engine),
        "java_dex_unchanged_from_4103": True,
        "firmware": "Official 3.74 PUPs bundled in APK assets/psvita-firmware",
    })
    prov_bytes = (json.dumps(provenance, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    unsigned = SIDE / "unsigned-vita-engine.apk"
    aligned = SIDE / "aligned-vita-engine.apk"
    unsigned.unlink(missing_ok=True)
    aligned.unlink(missing_ok=True)
    print("graft", ENGINE, "bytes", len(engine), flush=True)
    with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(unsigned, "w", allowZip64=True) as out:
        replaced = False
        for info in src.infolist():
            if info.filename.startswith("META-INF/"):
                continue
            lower = info.filename.lower()
            if lower.endswith(".pup") and info.filename not in ALLOWED_PUP:
                raise RuntimeError("refusing unexpected firmware: " + info.filename)
            if lower.endswith("keys.txt"):
                raise RuntimeError("refusing keys in APK: " + info.filename)
            if info.filename == ENGINE:
                put(out, info.filename, engine)
                replaced = True
            elif info.filename == "assets/psvita-integration/provenance.json":
                put(out, info, prov_bytes)
            else:
                put(out, info, src.read(info.filename))
        if not replaced:
            raise RuntimeError("TESTE APK missing " + ENGINE)
    print("zipalign", flush=True)
    run(TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned)
    unsigned.unlink(missing_ok=True)
    staged = SIDE / "TurboramaStation-TESTE-vita-4115-signed.apk"
    print("sign", flush=True)
    run(
        JAVA, "-jar", str(TOOLS / "lib" / "apksigner.jar"), "sign",
        "--alignment-preserved", "true",
        "--ks", str(KEYSTORE), "--ks-key-alias", "androiddebugkey",
        "--ks-pass", "pass:android", "--key-pass", "pass:android",
        "--out", str(staged), aligned,
    )
    run(JAVA, "-jar", str(TOOLS / "lib" / "apksigner.jar"), "verify", str(staged))
    aligned.unlink(missing_ok=True)
    bak = SIDE / "libVita3K-4103-from-teste.so"
    if not bak.exists():
        bak.write_bytes(old_engine)
    shutil.copy2(staged, BASE)
    with zipfile.ZipFile(BASE) as a:
        unexpected = [n for n in a.namelist() if n.lower().endswith(".pup") and n not in ALLOWED_PUP]
        if unexpected:
            raise RuntimeError("unexpected PUP in signed APK: " + ", ".join(unexpected))
        if any(n.lower().endswith("keys.txt") for n in a.namelist()):
            raise RuntimeError("keys.txt present in signed APK")
        if sha_bytes(a.read(ENGINE)) != sha_bytes(engine):
            raise RuntimeError("packed engine mismatch")
        if sha_bytes(a.read("classes23.dex")) != old_classes23:
            raise RuntimeError("classes23 changed")
        if sha_bytes(a.read("classes24.dex")) != old_classes24:
            raise RuntimeError("classes24 changed")
        if sha_bytes(a.read("lib/arm64-v8a/libturbo_vita_jni.so")) != old_jni:
            raise RuntimeError("jni bridge changed")
        packed_engine = sha_bytes(a.read(ENGINE))
    record = {
        "stable_sha256_unchanged": sha(STABLE) == STABLE_SHA,
        "old_1_0_untouched": True,
        "ps2_fbneo_untouched": True,
        "vita_engine": ENGINE_BUILD,
        "vita_commit": ENGINE_COMMIT,
        "donor_sha256": donor_sha,
        "libVita3K_sha256": packed_engine,
        "previous_libVita3K_sha256": sha_bytes(old_engine),
        "classes23_unchanged": old_classes23,
        "classes24_unchanged": old_classes24,
        "java_dex_identical_to_4103": True,
        "firmware_bundled": True,
        "output": str(BASE),
        "sha256": sha(BASE),
        "bytes": BASE.stat().st_size,
        "keys_bundled": False,
        "note": "TESTE Vita3K native engine updated 4103 -> 4115; Java/firmware/entry unchanged; keys stay off APK",
    }
    (SIDE / "vita-engine-4115-result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    main()
