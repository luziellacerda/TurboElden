"""Prepare the complete Cemu Android 0.5.2 module for the existing APK.

Private donor APK and all generated binaries remain on E:. Only this recipe is
stored in Git. The old 0.5 integration supplies the established class and
resource namespace so other embedded emulators keep their current names.
"""

from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(r"\\?\E:\ESTUDO APK\work\native-carousel\implementation")
OLD = ROOT / "wiiu-integration"
DIAG = ROOT / "emulator-completion" / "wiiu-rar5-fix"
WORK = ROOT / "emulator-completion" / "wiiu-052"
DONOR = DIAG / "Cemu.DualScreen.0.5.2.apk"
DONOR_SHA256 = "e1630fc51a4bbb18ef8499829fad011601d575726f019090abada6c9dd258387"
DECODED = WORK / "donor-decoded"
MODULE = WORK / "module"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe")
APKTOOL = Path(r"E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar")
FRAMEWORK = OLD / "framework"
LIBRARIES = {
    "androidx.graphics.path": "twiiucor.graphics.path",
    "datastore_shared_counter": "wiiustore_shared_counter",
    "file_redirect_hook": "wile_redirect_hook",
    "gsl_alloc_hook": "wsl_alloc_hook",
    "hook_impl": "whok_impl",
    "main_hook": "wiiu_hook",
    "c++_shared": "wuc_shared",
}
DESCRIPTOR = re.compile(r"L([A-Za-z0-9_$/.-]+);")
HEX_REF = re.compile(r"(?<![\w])0x7f[0-9a-fA-F]{6}(?![\w])")
CONST_STRING = re.compile(r'(const-string(?:/jumbo)?\s+\w+,\s+")([^"\n]*)(")')


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(*args):
    subprocess.run([str(x).removeprefix("\\\\?\\") for x in args], check=True)


def platform_class(name):
    return name.startswith(("java/", "javax/", "dalvik/", "org/xml/", "org/w3c/")) or (
        name.startswith("android/") and not name.startswith("android/support/")
    )


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = str(WORK)
    if sha256(DONOR) != DONOR_SHA256:
        raise RuntimeError("The Cemu 0.5.2 donor APK does not match the official download")
    if not DECODED.is_dir():
        run(JAVA, "-jar", APKTOOL, "d", "-f", "-p", FRAMEWORK, "-o", DECODED, DONOR)

    # This fork retained all 6,027 resource names and IDs from the 0.5 donor.
    # Therefore the existing, already merged Turborama resources can be reused.
    old_xml = ET.parse(OLD / "current-decoded/res/values/public.xml").getroot()
    new_xml = ET.parse(DECODED / "res/values/public.xml").getroot()
    resources = lambda root: {(e.get("type"), e.get("name")): e.get("id") for e in root if e.tag == "public"}
    if resources(old_xml) != resources(new_xml):
        raise RuntimeError("Cemu 0.5.2 resources differ; a full resource merge is required")
    class_map = {}
    for source_root in DECODED.glob("smali*"):
        for source in source_root.rglob("*.smali"):
            old = source.relative_to(source_root).as_posix()[:-6]
            if old.startswith("info/cemu/cemu/") or platform_class(old):
                new = old
            elif old.startswith("org/libsdl/"):
                new = old.replace("org/libsdl/", "org/p2sdlx/", 1)
            elif old.startswith("androidx/"):
                new = "twiiucor/" + old[9:]
            else:
                new = "twiiucor/shaded/" + old
            class_map[old] = new
    front_classes = set(json.loads((OLD / "base-classes.json").read_text(encoding="utf-8")))
    for source in DECODED.rglob("*.smali"):
        body = source.read_text(encoding="utf-8")
        if re.search(r"^\.method .*\bnative\b", body, re.M):
            old = re.search(r"^\.class (?:.* )?(L[^;]+;)", body, re.M)[1][1:-1]
            if not old.startswith(("org/libsdl/", "androidx/")):
                if old in front_classes:
                    raise RuntimeError(f"Native class collides with frontend: {old}")
                class_map[old] = old
    dot_map = {k.replace("/", "."): v.replace("/", ".") for k, v in class_map.items()}
    id_map = {int(k, 16): int(v, 16) for k, v in json.loads(
        (OLD / "resource-map.json").read_text(encoding="utf-8")
    ).items()}

    # Reuse the earlier module shell, but regenerate every Cemu class from 0.5.2.
    shutil.copytree(OLD.parent / "emulator-completion/wiiu-counter-current", MODULE,
                    ignore=shutil.ignore_patterns("smali", "build"), dirs_exist_ok=True)
    target = MODULE / "smali"
    if target.exists():
        resolved = target.resolve()
        if not resolved.is_relative_to(WORK.resolve()):
            raise RuntimeError("Refusing to remove smali outside the E: build directory")
        shutil.rmtree(target)
    target.mkdir()

    count = 0
    for source_root in DECODED.glob("smali*"):
        for source in source_root.rglob("*.smali"):
            old = source.relative_to(source_root).as_posix()[:-6]
            if platform_class(old) and old in front_classes:
                continue
            destination = target / (class_map[old] + ".smali")
            destination.parent.mkdir(parents=True, exist_ok=True)
            body = source.read_text(encoding="utf-8")
            body = DESCRIPTOR.sub(lambda m: "L" + class_map.get(m[1], m[1]) + ";", body)
            body = HEX_REF.sub(lambda m: f"0x{id_map.get(int(m[0], 16), int(m[0], 16)):08x}", body)
            body = re.sub(r"const/high16(\s+\w+,\s+)(0x[0-9a-fA-F]+)",
                          lambda m: ("const" if int(m[2], 16) & 65535 else "const/high16") + m[1] + m[2], body)

            def relocate_string(match):
                value = match[2]
                if "." in value or "/" in value:
                    value = dot_map.get(value, class_map.get(value, value))
                value = LIBRARIES.get(value, value)
                if value == "info.cemu.cemu":
                    value = "org.emulationstation.frontend"
                if value.startswith("info.cemu.cemu.") and value.endswith(
                    ("provider", "romlibrary", "androidx-startup")
                ):
                    value = value.replace("info.cemu.cemu.", "org.emulationstation.frontend.wiiu.", 1)
                return match[1] + value + match[3]

            body = CONST_STRING.sub(relocate_string, body)
            if old == "info/cemu/cemu/CemuApplication":
                body += """
.method public static initEmbedded(Landroid/app/Application;)V
 .locals 1
 new-instance v0, Linfo/cemu/cemu/CemuApplication;
 invoke-direct {v0}, Linfo/cemu/cemu/CemuApplication;-><init>()V
 invoke-virtual {v0, p0}, Linfo/cemu/cemu/CemuApplication;->attachEmbedded(Landroid/content/Context;)V
 invoke-virtual {v0}, Linfo/cemu/cemu/CemuApplication;->onCreate()V
 return-void
.end method
.method public attachEmbedded(Landroid/content/Context;)V
 .locals 0
 invoke-super {p0, p1}, Landroid/app/Application;->attachBaseContext(Landroid/content/Context;)V
 return-void
.end method
"""
            if old == "info/cemu/cemu/common/settings/InputOverlaySettings":
                marker = ".method public synthetic constructor <init>()V"
                start = body.index(marker)
                end = body.index(".end method", start)
                segment = body[start:end]
                if segment.count("const/4 v2, 0x0") != 1:
                    raise RuntimeError("The Cemu overlay default changed upstream")
                body = body[:start] + segment.replace("const/4 v2, 0x0", "const/4 v2, 0x1", 1) + body[end:]
            for method, args, wrapper in (
                ("getFilesDir", "", "files"),
                ("getExternalFilesDir", "Ljava/lang/String;", "userFiles"),
                ("getCacheDir", "", "cache"),
            ):
                body = re.sub(
                    r"invoke-virtual(.*?)Landroid/content/Context;->" + method +
                    r"\(" + args + r"\)Ljava/io/File;",
                    r"invoke-static\1Lorg/emulationstation/frontend/WiiUBootstrap;->" +
                    wrapper + "(Landroid/content/Context;" + args + ")Ljava/io/File;", body,
                )
            body = re.sub(
                r"invoke-virtual(.*?)Landroid/content/Context;->getSharedPreferences"
                r"\(Ljava/lang/String;I\)Landroid/content/SharedPreferences;",
                r"invoke-static\1Lorg/emulationstation/frontend/WiiUBootstrap;->preferences"
                r"(Landroid/content/Context;Ljava/lang/String;I)Landroid/content/SharedPreferences;", body,
            )
            destination.write_text(body, encoding="utf-8")
            count += 1

    output = WORK / "cemu-052-module.apk"
    run(JAVA, "-jar", APKTOOL, "b", "-p", FRAMEWORK, "-o", output, MODULE)
    patched_libs = WORK / "libs"
    patched_libs.mkdir(exist_ok=True)
    replacements = {
        b"androidx/": b"twiiucor/",
        b"org/libsdl/": b"org/p2sdlx/",
        # JNI exports use underscores, unlike Java class descriptors.
        b"Java_androidx_": b"Java_twiiucor_",
        b"Java_org_libsdl_": b"Java_org_p2sdlx_",
    }
    replacements.update({("lib" + k + ".so").encode(): ("lib" + v + ".so").encode()
                         for k, v in LIBRARIES.items()})
    for source in (DECODED / "lib/arm64-v8a").glob("*.so"):
        content = source.read_bytes()
        for old, new in replacements.items():
            if len(old) != len(new):
                raise RuntimeError(f"Library rename changes length: {old} -> {new}")
            content = content.replace(old, new)
        name = "lib" + LIBRARIES.get(source.name[3:-3], source.name[3:-3]) + ".so"
        (patched_libs / name).write_bytes(content)
    (WORK / "prepare-result.json").write_text(json.dumps({
        "donor_sha256": DONOR_SHA256,
        "module_sha256": sha256(output),
        "classes": count,
        "libs": {p.name: sha256(p) for p in patched_libs.glob("*.so")},
    }, indent=2) + "\n", encoding="utf-8")
    print((WORK / "prepare-result.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
