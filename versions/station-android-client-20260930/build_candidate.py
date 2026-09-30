"""Build a review APK from the current installed baseline; all temporary files stay on E:."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "java" / "org" / "emulationstation" / "frontend" / "auth"
WORK = Path(r"E:\ESTUDO APK\work\native-carousel\implementation\station-android-client-20260930")
BASE = Path(r"E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Plataformas-Organizadas.apk")
EXPECTED = "1189899e780cd372e8e0efdbea7dad2926ecccf896542c3349d1b79caa8ac2c7"
OUTPUT = WORK / "TurboramaStation-StationAndroid-candidato.apk"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin")
SDK = Path(r"G:\Android\Sdk\platforms\android-34\android.jar")
TOOLS = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15")
APKTOOL = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar")
STUB = Path(r"E:\ESTUDO APK\work\native-carousel\implementation\login-return\compile-stubs\org\emulationstation\frontend\auth\LocalPassword.java")
PACKAGE = Path("org/emulationstation/frontend/auth")

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def run(*args):
    subprocess.run([str(x) for x in args], check=True)

def wrapper(path, dex):
    with zipfile.ZipFile(BASE) as source, zipfile.ZipFile(path, "w") as target:
        for name in ("AndroidManifest.xml", "resources.arsc"):
            target.writestr(name, source.read(name))
        target.writestr("classes.dex", dex)

def apktool(*args):
    run(JAVA / "java.exe", "-Djava.io.tmpdir=" + str(WORK / "tmp"),
        "-jar", APKTOOL, *args)

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    for folder in ("tmp", "classes", "dex"):
        (WORK / folder).mkdir(exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(WORK / "tmp")
    if digest(BASE) != EXPECTED:
        raise RuntimeError("The installed-baseline APK differs from the documented hash")
    if not STUB.exists():
        raise RuntimeError("LocalPassword compile declaration not found")

    with zipfile.ZipFile(BASE) as source:
        wrapper(WORK / "base-auth.apk", source.read("classes8.dex"))
    apktool("d", "-r", "-f", "-p", WORK / "framework", "-o",
            WORK / "base-auth", WORK / "base-auth.apk")

    sources = sorted(SOURCE.glob("*.java")) + [STUB]
    run(JAVA / "javac.exe", "-encoding", "UTF-8", "-source", "8", "-target", "8",
        "-cp", SDK, "-d", WORK / "classes", *sources)
    classes = sorted((WORK / "classes" / PACKAGE).glob("Station*.class"))
    classes += sorted((WORK / "classes" / PACKAGE).glob("LoginActivity*.class"))
    classes += [WORK / "classes" / PACKAGE / "AuthSession.class"]
    run(JAVA / "java.exe", "-Djava.io.tmpdir=" + str(WORK / "tmp"),
        "-cp", TOOLS / "lib" / "d8.jar", "com.android.tools.r8.D8",
        "--min-api", "26", "--lib", SDK, "--output", WORK / "dex", *classes)
    wrapper(WORK / "candidate-auth.apk", (WORK / "dex" / "classes.dex").read_bytes())
    apktool("d", "-r", "-f", "-p", WORK / "framework", "-o",
            WORK / "candidate-auth", WORK / "candidate-auth.apk")

    old = WORK / "base-auth" / "smali" / PACKAGE
    new = WORK / "candidate-auth" / "smali" / PACKAGE
    changed_classes = []
    for source in new.glob("*.smali"):
        if source.name.startswith(("Station", "LoginActivity")) or source.name == "AuthSession.smali":
            shutil.copy2(source, old / source.name)
            changed_classes.append(source.name)
    if "LoginActivity.smali" not in changed_classes or "AuthSession.smali" not in changed_classes:
        raise RuntimeError("Authentication classes were not compiled")
    apktool("b", "-p", WORK / "framework", "-o", WORK / "merged-auth.apk",
            WORK / "base-auth")
    with zipfile.ZipFile(WORK / "merged-auth.apk") as source:
        patched_dex = source.read("classes.dex")

    unsigned = WORK / "station-unsigned.apk"
    aligned = WORK / "station-aligned.apk"
    with zipfile.ZipFile(BASE) as source, zipfile.ZipFile(unsigned, "w", allowZip64=True) as target:
        for info in source.infolist():
            if info.filename.startswith("META-INF/"):
                continue
            target.writestr(info, patched_dex if info.filename == "classes8.dex"
                            else source.read(info.filename))
    run(TOOLS / "zipalign.exe", "-f", "-P", "16", "4", unsigned, aligned)
    run(JAVA / "java.exe", "-jar", TOOLS / "lib" / "apksigner.jar", "sign",
        "--alignment-preserved", "true", "--ks", r"C:\Users\Admin\.android\debug.keystore",
        "--ks-key-alias", "androiddebugkey", "--ks-pass", "pass:android",
        "--key-pass", "pass:android", "--out", OUTPUT, aligned)
    run(JAVA / "java.exe", "-jar", TOOLS / "lib" / "apksigner.jar", "verify", OUTPUT)

    with zipfile.ZipFile(BASE) as before, zipfile.ZipFile(OUTPUT) as after:
        names = {n for n in before.namelist() if not n.startswith("META-INF/")}
        if names != {n for n in after.namelist() if not n.startswith("META-INF/")}:
            raise RuntimeError("APK entry list changed")
        changed = sorted(n for n in names if before.getinfo(n).CRC != after.getinfo(n).CRC
                         or before.getinfo(n).file_size != after.getinfo(n).file_size)
        if changed != ["classes8.dex"]:
            raise RuntimeError("Unexpected APK entries changed: " + repr(changed))
    report = {
        "base": str(BASE), "baseSha256": EXPECTED, "apk": str(OUTPUT),
        "sha256": digest(OUTPUT), "bytes": OUTPUT.stat().st_size,
        "changedEntries": changed, "changedClasses": sorted(changed_classes),
        "serverConfigured": False, "installed": False,
        "commercialAccessEnabled": False,
    }
    (WORK / "build-result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
