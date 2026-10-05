from pathlib import Path
import xml.etree.ElementTree as ET
import re,shutil
A="{http://schemas.android.com/apk/res/android}"
AUTO="{http://schemas.android.com/apk/res-auto}"
OLD_PKG="org.turboramastation.frontend"
def platform_class(name):
    return name.startswith(("java/", "javax/", "dalvik/", "org/xml/", "org/w3c/")) or (
        name.startswith("android/") and not name.startswith("android/support/")
    )

def prefix(name):
    return "n6_"+name.replace("$","private_")
def merge_donor(D: Path, M: Path):
    front_public = ET.parse(M / "res/values/public.xml")
    pub = front_public.getroot()
    front_types = {}
    next_entry = {}
    for e in pub:
        if e.tag != "public":
            continue
        rid = int(e.attrib["id"], 16)
        typ = e.attrib["type"]
        front_types[typ] = (rid >> 16) & 255
        next_entry[typ] = max(next_entry.get(typ, 0), (rid & 65535) + 1)
    donor_public = ET.parse(D / "res/values/public.xml").getroot()
    names = {}
    idmap = {}
    for e in donor_public:
        if e.tag != "public":
            continue
        typ = e.attrib["type"]
        name = e.attrib["name"]
        if name in ("splits0",):
            continue
        new = prefix(name)
        if typ not in front_types:
            front_types[typ] = max(front_types.values()) + 1
            next_entry[typ] = 0
        rid = 0x7F000000 | (front_types[typ] << 16) | next_entry[typ]
        next_entry[typ] += 1
        old = int(e.attrib["id"], 16)
        idmap[old] = rid
        names[(typ, name)] = new
        ET.SubElement(pub, "public", {"type": typ, "name": new, "id": f"0x{rid:08x}"})
    front_public.write(M / "res/values/public.xml", encoding="utf-8", xml_declaration=True)

    resource_ref = re.compile(r"([@?])(\+?)([A-Za-z0-9_.]+:)?([a-zA-Z_][a-zA-Z_0-9]*)/([A-Za-z0-9_.$]+)")
    hex_ref = re.compile(r"(?<![\w])0x7f[0-9a-fA-F]{6}(?![\w])")
    descriptor = re.compile(r"L([A-Za-z0-9_$/.-]+);")
    const_string = re.compile(r'(const-string(?:/jumbo)?\s+\w+,\s+")([^"\n]*)(")')

    class_map = {}
    for root in D.glob("smali*"):
        for f in root.rglob("*.smali"):
            old = f.relative_to(root).as_posix()[:-6]
            if old.startswith("paulscode/android/mupen64plusae/") or old.startswith("com/sun/jna/") or platform_class(old):
                new = old
            elif old.startswith("kotlin/"):
                new = "tn64core/" + old
            else:
                new = "tn64core/shaded/" + old
            class_map[old] = new
    native_classes = set()
    for f in D.rglob("*.smali"):
        text = f.read_text("utf-8")
        if re.search(r"^\.method .*\bnative\b", text, re.M):
            name = re.search(r"^\.class (?:.* )?(L[^;]+;)", text, re.M)[1][1:-1]
            class_map[name] = name
            native_classes.add(name)
    dot_map = {k.replace("/", "."): v.replace("/", ".") for k, v in class_map.items()}

    def refs(s):
        def sub(m):
            if m[3] and m[3] not in ("org.mupen64plusae.v3.alpha:", "paulscode.android.mupen64plusae:"):
                return m[0]
            name = names.get((m[4], m[5]))
            return m[1] + m[2] + m[4] + "/" + name if name else m[0]
        s = resource_ref.sub(sub, s)
        s = re.sub(r"\?([A-Za-z_][\w.]*)", lambda m: "?" + names.get(("attr", m[1]), m[1]), s)
        return hex_ref.sub(lambda m: f"0x{idmap.get(int(m[0], 16), int(m[0], 16)):08x}", s)

    def xml_node(e, values=False, parent=None):
        if e.tag in dot_map and ("." in e.tag or e.tag not in {"item", "style", "resources", "string", "id", "array", "attr", "bool", "integer", "color", "dimen", "plurals", "font", "menu", "selector", "shape", "vector", "path", "group", "view"}):
            e.tag = dot_map[e.tag]
        for key, val in list(e.attrib.items()):
            newkey = key
            if key.startswith(AUTO):
                newkey = AUTO + "n6_" + key[len(AUTO) :]
            val = refs(val)
            if key in ("class", A + "name") and not values and val in dot_map:
                val = dot_map[val]
            if key == "name" and values:
                if parent == "resources":
                    val = prefix(val)
                elif parent == "style" and not val.startswith("android:"):
                    val = "n6_" + val
            if key == "parent" and e.tag == "style" and val and not val.startswith(("@", "android:")):
                val = "n6_" + val
            if newkey != key:
                del e.attrib[key]
            e.attrib[newkey] = val
        if e.text:
            e.text = refs(e.text)
        for child in e:
            xml_node(child, values, e.tag)

    for folder in (D / "res").iterdir():
        if not folder.is_dir():
            continue
        outdir = M / "res" / folder.name
        outdir.mkdir(exist_ok=True)
        for f in folder.iterdir():
            if f.name == "public.xml" or f.stem in ("splits0",):
                continue
            dest = outdir / prefix(f.name)
            if f.suffix == ".xml":
                tree = ET.parse(f)
                xml_node(tree.getroot(), folder.name.startswith("values"))
                tree.write(dest, encoding="utf-8", xml_declaration=True)
            else:
                shutil.copy2(f, dest)

    target = M / "smali_classes36"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()
    for root in sorted(D.glob("smali*")):
        for f in root.rglob("*.smali"):
            old = f.relative_to(root).as_posix()[:-6]
            if platform_class(old):
                continue
            dest = target / (class_map[old] + ".smali")
            dest.parent.mkdir(parents=True, exist_ok=True)
            s = f.read_text(encoding="utf-8")
            s = descriptor.sub(lambda m: "L" + class_map.get(m[1], m[1]) + ";", s)
            s = hex_ref.sub(lambda m: f"0x{idmap.get(int(m[0], 16), int(m[0], 16)):08x}", s)
            s = re.sub(
                r"const/high16(\s+\w+,\s+)(0x[0-9a-fA-F]+)",
                lambda m: ("const" if int(m[2], 16) & 65535 else "const/high16") + m[1] + m[2],
                s,
            )

            def string_sub(m):
                val = m[2]
                if "." in val or "/" in val:
                    val = dot_map.get(val, class_map.get(val, val))
                if val in ("org.mupen64plusae.v3.alpha",):
                    val = OLD_PKG
                return m[1] + val + m[3]

            s = const_string.sub(string_sub, s)
            dest.write_text(s, encoding="utf-8")

    for p in target.rglob("*.smali"):
        s = p.read_text(encoding="utf-8")
        t = s
        for method, args, fn in (
            ("getFilesDir", "", "files"),
            ("getExternalFilesDir", "Ljava/lang/String;", "userFiles"),
            ("getCacheDir", "", "cache"),
        ):
            t = re.sub(
                r"invoke-virtual(.*?)L(?:android/content/Context|android/app/Activity|paulscode/android/mupen64plusae/[^;]+);->"
                + method
                + r"\("
                + args
                + r"\)Ljava/io/File;",
                r"invoke-static\1Lorg/emulationstation/frontend/N64Bootstrap;->"
                + fn
                + "(Landroid/content/Context;"
                + args
                + ")Ljava/io/File;",
                t,
            )
        if t != s:
            p.write_text(t, encoding="utf-8")

    assets_src = D / "assets"
    assets_dst = M / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)

    return names,idmap,class_map,native_classes
