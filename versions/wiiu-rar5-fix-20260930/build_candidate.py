"""Build the Wii U archive and touch-control candidate from the Station APK."""

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import zipfile


ROOT = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
WORK = ROOT / "emulator-completion" / "wiiu-rar5-fix"
BASE = ROOT / "TurboramaStation-Plataformas-Organizadas.apk"
BASE_SHA256 = "1189899e780cd372e8e0efdbea7dad2926ecccf896542c3349d1b79caa8ac2c7"
SOURCE = Path(__file__).parent / "wiiu_archive_bridge.c"
ARCHIVE = ROOT / "emulator-completion" / "vita-rar-diagnosis" / "libarchive-rar5-eof.a"
HEADER = ROOT / "platform-media-refresh" / "psvita" / "archive" / "libarchive-3.8.9" / "libarchive"
NDK = Path(r"E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
LIB_NAME = "lib/arm64-v8a/libturbo_wiiu_archive.so"
CONTROLS_MODULE = WORK / "cemu-controls-module.apk"
BRIDGE_DEX = WORK / "bridge-dex" / "classes.dex"
OUTPUT = WORK / "TurboramaStation-WiiU-RAR5-candidato.apk"


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(*args):
    subprocess.run([str(item) for item in args], check=True)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(WORK)
    if digest(BASE) != BASE_SHA256:
        raise RuntimeError("APK base differs from the installed version recorded for this change")
    for component in (ARCHIVE, CONTROLS_MODULE, BRIDGE_DEX):
        if not component.is_file():
            raise FileNotFoundError(f"Missing private build component: {component}; see README.md")
    native = WORK / "libturbo_wiiu_archive.so"
    run(NDK / "bin" / "clang.exe", "--target=aarch64-linux-android26",
        "--sysroot=" + str(NDK / "sysroot"), "-std=c11", "-O2", "-fPIC", "-shared",
        "-fvisibility=hidden", "-Wall", "-Wextra", "-Werror", "-I" + str(HEADER),
        SOURCE, ARCHIVE, "-Wl,--exclude-libs,ALL", "-Wl,--no-undefined",
        "-Wl,-z,max-page-size=16384", "-lz", "-lm", "-llog", "-o", native)

    with zipfile.ZipFile(CONTROLS_MODULE) as controls:
        replacements = {
            LIB_NAME: native.read_bytes(),
            "classes19.dex": controls.read("classes.dex"),
            "classes20.dex": BRIDGE_DEX.read_bytes(),
        }
    unsigned = WORK / "unsigned.apk"
    aligned = WORK / "aligned.apk"
    with zipfile.ZipFile(BASE) as original, zipfile.ZipFile(unsigned, "w", allowZip64=True) as updated:
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
        if changed != sorted(replacements):
            raise RuntimeError("Unexpected APK changes: " + repr(changed))
    record = {
        "apk": str(OUTPUT), "sha256": digest(OUTPUT), "bytes": OUTPUT.stat().st_size,
        "base_sha256": BASE_SHA256, "changed_entries": changed,
        "lib_sha256": digest(native), "archive_sha256": digest(ARCHIVE),
        "cemu_module_sha256": digest(CONTROLS_MODULE),
        "bridge_dex_sha256": digest(BRIDGE_DEX),
        "installed": False, "runtime_verified": False,
    }
    (WORK / "build-result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
