"""Package Cemu 0.5.2, Wii U controls and RAR5 correction into Station."""

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import zipfile


HERE = Path(__file__).parent
ROOT = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
WORK = ROOT / "emulator-completion" / "wiiu-052"
BASE = ROOT / "TurboramaStation-Plataformas-Organizadas.apk"
BASE_SHA256 = "1189899e780cd372e8e0efdbea7dad2926ecccf896542c3349d1b79caa8ac2c7"
ARCHIVE_SOURCE = HERE.parent / "wiiu-rar5-fix-20260930" / "wiiu_archive_bridge.c"
ARCHIVE_STATIC = ROOT / "emulator-completion" / "vita-rar-diagnosis" / "libarchive-rar5-eof.a"
ARCHIVE_HEADERS = ROOT / "platform-media-refresh" / "psvita" / "archive" / "libarchive-3.8.9" / "libarchive"
NDK = Path(r"E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
MODULE = WORK / "cemu-052-module.apk"
BRIDGE = WORK / "bridge-dex" / "classes.dex"
LIBRARIES = WORK / "libs"
OUTPUT = WORK / "TurboramaStation-WiiU-Cemu-0.5.2-candidato.apk"


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(*args):
    subprocess.run([str(item) for item in args], check=True)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(WORK)
    if digest(BASE) != BASE_SHA256:
        raise RuntimeError("The Station base APK differs from the recorded revision")
    for required in (ARCHIVE_SOURCE, ARCHIVE_STATIC, MODULE, BRIDGE):
        if not required.is_file():
            raise FileNotFoundError(required)
    archive_so = WORK / "libturbo_wiiu_archive.so"
    run(NDK / "bin" / "clang.exe", "--target=aarch64-linux-android26",
        "--sysroot=" + str(NDK / "sysroot"), "-std=c11", "-O2", "-fPIC", "-shared",
        "-fvisibility=hidden", "-Wall", "-Wextra", "-Werror", "-I" + str(ARCHIVE_HEADERS),
        ARCHIVE_SOURCE, ARCHIVE_STATIC, "-Wl,--exclude-libs,ALL", "-Wl,--no-undefined",
        "-Wl,-z,max-page-size=16384", "-lz", "-lm", "-llog", "-o", archive_so)
    counter_source = HERE / "datastore_counter_jni.cpp"
    counter_so = LIBRARIES / "libwiiustore_shared_counter.so"
    run(NDK / "bin" / "clang++.exe", "--target=aarch64-linux-android26",
        "--sysroot=" + str(NDK / "sysroot"), "-std=c++17", "-O2", "-fPIC", "-shared",
        "-fvisibility=hidden", "-Wall", "-Wextra", "-Werror",
        "-Wl,-z,max-page-size=16384", counter_source, "-o", counter_so)
    with zipfile.ZipFile(MODULE) as module:
        replacements = {
            "classes19.dex": module.read("classes.dex"),
            "classes20.dex": BRIDGE.read_bytes(),
            "lib/arm64-v8a/libturbo_wiiu_archive.so": archive_so.read_bytes(),
        }
    for library in LIBRARIES.glob("*.so"):
        replacements["lib/arm64-v8a/" + library.name] = library.read_bytes()
    metadata = {
        "version": "Cemu Android 0.5.2",
        "source": "https://github.com/SapphireRhodonite/Cemu/tree/0.5.2",
        "apk": "https://github.com/SapphireRhodonite/Cemu/releases/download/0.5.2/Cemu.DualScreen.0.5.2.apk",
        "donor_sha256": "e1630fc51a4bbb18ef8499829fad011601d575726f019090abada6c9dd258387",
        "upstream_engine_rebuilt": False,
        "experimental": True,
        "integration": "Embedded engine and original menus in dedicated :wiiu process",
        "rar5_fix": True,
        "initial_touch_gamepad": True,
    }
    replacements["assets/wiiu-integration/provenance.json"] = (
        json.dumps(metadata, indent=2) + "\n").encode("utf-8")
    unsigned = WORK / "unsigned.apk"
    aligned = WORK / "aligned.apk"
    with zipfile.ZipFile(BASE) as original, zipfile.ZipFile(unsigned, "w", allowZip64=True) as updated:
        names = set(original.namelist())
        missing = set(replacements) - names
        if missing:
            raise RuntimeError("Expected components missing from Station APK: " + repr(sorted(missing)))
        for info in original.infolist():
            if info.filename.startswith("META-INF/"):
                continue
            if info.filename in replacements:
                updated.writestr(info, replacements[info.filename])
            else:
                with original.open(info) as source, updated.open(info, "w") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
    run(TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned)
    required_env = ("TURBORAMA_KEYSTORE", "TURBORAMA_KEY_ALIAS",
                    "TURBORAMA_STORE_PASSWORD", "TURBORAMA_KEY_PASSWORD")
    missing_env = [name for name in required_env if not os.environ.get(name)]
    if missing_env:
        raise RuntimeError("Missing signing environment variables: " + ", ".join(missing_env))
    run(JAVA, "-jar", TOOLS / "lib" / "apksigner.jar", "sign", "--alignment-preserved", "true",
        "--ks", os.environ["TURBORAMA_KEYSTORE"],
        "--ks-key-alias", os.environ["TURBORAMA_KEY_ALIAS"],
        "--ks-pass", "env:TURBORAMA_STORE_PASSWORD",
        "--key-pass", "env:TURBORAMA_KEY_PASSWORD", "--out", OUTPUT, aligned)
    run(JAVA, "-jar", TOOLS / "lib" / "apksigner.jar", "verify", OUTPUT)
    with zipfile.ZipFile(BASE) as original, zipfile.ZipFile(OUTPUT) as updated:
        names = {name for name in original.namelist() if not name.startswith("META-INF/")}
        if names != {name for name in updated.namelist() if not name.startswith("META-INF/")}:
            raise RuntimeError("APK file list changed")
        changed = sorted(name for name in names if
            original.getinfo(name).CRC != updated.getinfo(name).CRC or
            original.getinfo(name).file_size != updated.getinfo(name).file_size)
        if not set(changed).issubset(replacements) or not {
            "classes19.dex", "classes20.dex", "lib/arm64-v8a/libCemuAndroid.so",
            "lib/arm64-v8a/libturbo_wiiu_archive.so", "assets/wiiu-integration/provenance.json",
        }.issubset(changed):
            raise RuntimeError("Unexpected APK changes: " + repr(changed))
    record = {
        "apk": str(OUTPUT), "sha256": digest(OUTPUT), "bytes": OUTPUT.stat().st_size,
        "base_sha256": BASE_SHA256, "changed_entries": changed,
        "donor_sha256": metadata["donor_sha256"], "module_sha256": digest(MODULE),
        "bridge_sha256": digest(BRIDGE), "archive_sha256": digest(ARCHIVE_STATIC),
        "installed": False, "runtime_verified": False,
    }
    (WORK / "build-result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
