"""Compile the Wii U bootstrap and archive bridge into classes20.dex on E:."""

from pathlib import Path
import os
import subprocess
import zipfile


HERE = Path(__file__).parent
ROOT = Path(r"E:\ESTUDO APK\work\native-carousel\implementation")
WORK = ROOT / "emulator-completion" / "wiiu-052"
SOURCES = ROOT / "emulator-completion" / "wiiu-archive-final" / "java" / "org" / "emulationstation" / "frontend"
JDK = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin")
ANDROID_JAR = Path(r"G:\Android\Sdk\platforms\android-34\android.jar")
D8 = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar")


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = str(WORK)
    classes = WORK / "bridge-classes"
    classes.mkdir(exist_ok=True)
    run(JDK / "javac.exe", "-encoding", "UTF-8", "-source", "8", "-target", "8",
        "-classpath", ANDROID_JAR, "-d", classes,
        HERE / "WiiUBootstrap.java", SOURCES / "WiiUArchive.java", SOURCES / "WiiUEntryActivity.java")
    archive = WORK / "bridge.jar"
    with zipfile.ZipFile(archive, "w") as output:
        for cls in classes.rglob("*.class"):
            output.write(cls, cls.relative_to(classes).as_posix())
    dex = WORK / "bridge-dex"
    dex.mkdir(exist_ok=True)
    run(JDK / "java.exe", "-cp", D8, "com.android.tools.r8.D8", "--min-api", "26",
        "--lib", ANDROID_JAR, "--output", dex, archive)
    print(dex / "classes.dex")


if __name__ == "__main__":
    main()
