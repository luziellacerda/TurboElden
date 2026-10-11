"""Generate plain-Java localized strings and path names, never firmware/media bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

APK_SHA = "c5a58fb056ae333b8bd6ed69e6bfacdd1e5bf7e0ac2134456a0622bd94a3e466"
STRINGS_SHA = "d2caea6ea2af1f6f98091c42603e2c40dfc118504f9f711f3ae0e26f0a147d31"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--strings", type=Path, required=True)
    parser.add_argument("--java-out", type=Path, required=True)
    args = parser.parse_args()
    if hashlib.file_digest(args.apk.open("rb"), "sha256").hexdigest() != APK_SHA:
        raise SystemExit("Official APK identity mismatch")
    raw = args.strings.read_bytes()
    if hashlib.sha256(raw).hexdigest() != STRINGS_SHA:
        raise SystemExit("Official source strings identity mismatch")
    with zipfile.ZipFile(args.apk) as archive:
        icons = sorted(name.removeprefix("assets/") for name in archive.namelist()
                       if name.startswith("assets/Icons/ui/") and not name.endswith("/"))
    if len(icons) != 59:
        raise SystemExit("Official icon inventory mismatch")
    root = ET.fromstring(raw)
    strings = {}
    for element in root.findall("string"):
        name = element.get("name", "")
        if re.fullmatch(r"[A-Z][A-Z0-9_]+", name):
            value = "".join(element.itertext())
            value = value.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
            strings[name] = value
    if len(strings) != 297:
        raise SystemExit("Official localized environment inventory incomplete")
    args.java_out.mkdir(parents=True, exist_ok=True)
    encode = lambda value: json.dumps(value, ensure_ascii=True)
    icon_lines = ",\n".join("        " + encode(icon) for icon in icons)
    (args.java_out / "Ps3AssetPaths.java").write_text(
        "package org.emulationstation.frontend.sony;\n"
        "/** Exact asset path names from official aPS3e 2.43; no media bytes. */\n"
        "final class Ps3AssetPaths { static final String[] ICONS = {\n" + icon_lines +
        "\n    }; private Ps3AssetPaths() {} }\n", encoding="utf-8")
    pairs = ",\n".join("        {" + encode(key) + ", " + encode(value) + "}"
                         for key, value in sorted(strings.items()))
    (args.java_out / "Ps3LocalizedStrings.java").write_text(
        "// SPDX-License-Identifier: WTFPL\n"
        "package org.emulationstation.frontend.sony;\n"
        "/** Native environment text from pinned official source; no resource package merge. */\n"
        "final class Ps3LocalizedStrings {\n    private static final String[][] TEXT = {\n" + pairs +
        "\n    };\n    static void installEnvironment() {\n"
        "        for (String[] text : TEXT) aenu.lang.System.setenv(text[0], text[1], true);\n"
        "    }\n    private Ps3LocalizedStrings() {}\n}\n", encoding="utf-8")
    print(json.dumps({"iconPaths": len(icons), "nativeTextEntries": len(strings)}))

if __name__ == "__main__":
    main()
