"""Compile StationTransfer into classes5 only, then graft it beside classes8."""
from pathlib import Path
import shutil
import subprocess
import zipfile

WORK = Path(r"E:\ESTUDO APK\work\native-carousel\implementation\station-security-20261001")
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin")
SDK = Path(r"G:\Android\Sdk\platforms\android-34\android.jar")
D8 = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar")
APKTOOL = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar")
FRAMEWORK = Path(r"E:\ESTUDO APK\work\native-carousel\implementation\framework")
JAVA_HOME = JAVA / "java.exe"
DEPS = WORK / "classes-transfer-deps"
APP = WORK / "classes-transfer"
DEX = WORK / "dex-transfer"
MINI = WORK / "dex-work" / "classes5-transfer-mini.apk"
BASE_MINI = WORK / "dex-work" / "classes5-mini.apk"
BAK = WORK / "dex-work" / "classes5-transfer-decoded"
TREE = WORK / "dex-work" / "classes5-decoded"
REBUILT = WORK / "dex-work" / "classes5-rebuilt.apk"
STUBS = WORK / "compile-stubs"
AUTH = WORK / "java" / "org" / "emulationstation" / "frontend" / "auth"
TRANSFER = WORK / "java" / "org" / "emulationstation" / "frontend" / "StationTransfer.java"


def run(args):
    print("run", Path(args[0]).name, flush=True)
    subprocess.run([str(item) for item in args], check=True)


def main():
    if DEPS.exists():
        shutil.rmtree(DEPS)
    if APP.exists():
        shutil.rmtree(APP)
    DEPS.mkdir(parents=True)
    APP.mkdir(parents=True)
    sources = list(AUTH.glob("*.java"))
    sources.append(STUBS / "org" / "emulationstation" / "frontend" / "auth" / "LoginActivity.java")
    sources.append(STUBS / "org" / "emulationstation" / "frontend" / "HttpBridge.java")
    sources.append(STUBS / "org" / "emulationstation" / "frontend" / "catalog" / "LocalCatalog.java")
    sources.append(STUBS / "org" / "libsdl" / "app" / "SDL.java")
    run([
        JAVA / "javac.exe", "-encoding", "UTF-8", "-source", "8", "-target", "8",
        "-classpath", SDK, "-d", DEPS, *sources,
    ])
    run([
        JAVA / "javac.exe", "-encoding", "UTF-8", "-source", "8", "-target", "8",
        "-classpath", str(SDK) + ";" + str(DEPS), "-d", APP, TRANSFER,
    ])
    if DEX.exists():
        shutil.rmtree(DEX)
    DEX.mkdir()
    transfer_dir = APP / "org" / "emulationstation" / "frontend"
    transfer_classes = sorted(transfer_dir.glob("StationTransfer*.class"))
    if not transfer_classes:
        raise SystemExit("StationTransfer class missing")
    run([
        JAVA_HOME, "-cp", D8, "com.android.tools.r8.D8",
        "--min-api", "26", "--lib", SDK, "--classpath", DEPS,
        "--output", DEX, *transfer_classes,
    ])
    if MINI.exists():
        MINI.unlink()
    with zipfile.ZipFile(BASE_MINI) as source, zipfile.ZipFile(MINI, "w") as archive:
        for info in source.infolist():
            data = (DEX / "classes.dex").read_bytes() if info.filename == "classes.dex" else source.read(info.filename)
            archive.writestr(info, data)
    if BAK.exists():
        shutil.rmtree(BAK)
    run([JAVA_HOME, "-jar", APKTOOL, "d", "-f", "-p", FRAMEWORK, "-o", BAK, MINI])
    fresh_dir = BAK / "smali" / "org" / "emulationstation" / "frontend"
    dest_dir = TREE / "smali" / "org" / "emulationstation" / "frontend"
    fresh = sorted(fresh_dir.glob("StationTransfer*.smali"))
    names = [path.name for path in fresh]
    if "StationTransfer.smali" not in names:
        raise SystemExit("StationTransfer.smali missing")
    for path in fresh:
        shutil.copy2(path, dest_dir / path.name)
    extras = [path.name for path in (BAK / "smali").rglob("*.smali")]
    if sorted(extras) != sorted(names):
        raise SystemExit("transfer dex contained extra classes: " + ", ".join(sorted(extras)))
    built = TREE / "build" / "apk" / "classes.dex"
    if built.exists():
        built.unlink()
    try:
        run([JAVA_HOME, "-jar", APKTOOL, "b", "-p", FRAMEWORK, "-o", REBUILT, TREE])
    except subprocess.CalledProcessError:
        if not built.is_file():
            raise
        print("apktool resource step failed; using assembled dex", flush=True)
    if not built.is_file():
        raise SystemExit("classes5 dex was not assembled")
    if REBUILT.exists():
        REBUILT.unlink()
    with zipfile.ZipFile(BASE_MINI) as source, zipfile.ZipFile(REBUILT, "w") as archive:
        for info in source.infolist():
            data = built.read_bytes() if info.filename == "classes.dex" else source.read(info.filename)
            archive.writestr(info, data)
    run([Path(r"C:\Python314\python.exe"), WORK / "package_station_login.py"])


if __name__ == "__main__":
    main()
