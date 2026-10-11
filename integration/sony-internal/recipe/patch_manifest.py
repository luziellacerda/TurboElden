"""Add private internal Sony owners and delegate the existing component factory.

Preserves all existing resources, components, permissions and attributes. A
binary inverse is required before writing the candidate manifest.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct
import zipfile

REPO = Path(__file__).resolve().parents[3]
DONOR_MANIFEST_SHA = "acda0e4404e29764a32fb3452b69899dc4501b63100376620a7e41a2ad85ff31"
BASE_SHA = "d227b0af17600bf99ec097857bf182f6e7989f8ddc3b68b63e17c81f69eb30ad"
OLD_FACTORY = "org.emulationstation.frontend.station.StationComponentFactory"
NEW_FACTORY = "org.emulationstation.frontend.sony.StationSonyComponentFactory"
TEMPLATE = "org.emulationstation.frontend.netplay.StationPsxOnlineActivity"
COMPONENTS = {
    "org.emulationstation.frontend.sony.Ps3Activity": ":station_ps3",
    "org.emulationstation.frontend.sony.Ps4Activity": ":station_ps4",
}

def primitives():
    path = REPO / "versions/station-game-menu-controller-audit-r120-20261010/recipes/patch_component_factory.py"
    spec = importlib.util.spec_from_file_location("sony_axml", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(data):
    if hashlib.sha256(data).hexdigest() != DONOR_MANIFEST_SHA:
        raise ValueError("The exact R130 manifest is required")
    h = primitives()
    chunks = list(h.chunks(data))
    po, _, ph, ps = next(chunk for chunk in chunks if chunk[1] == 1)
    ro, _, rh, rs = next(chunk for chunk in chunks if chunk[1] == 0x180)
    ids = list(struct.unpack_from("<" + "I" * ((rs-rh)//4), data, ro+rh))
    strings = h.string_pool(data, po)
    added = []
    def string(text):
        if text in strings:
            return strings.index(text)
        if text not in added:
            added.append(text)
        return len(strings) + added.index(text)

    end_application = None
    factory = None
    template = None
    template_attributes = None
    for off, kind, header, size in chunks:
        if kind not in (0x102, 0x103):
            continue
        tag = strings[h.u32(data, off+20)]
        if kind == 0x103 and tag == "application":
            end_application = off
        if kind != 0x102:
            continue
        start, width, count = struct.unpack_from("<HHH", data, off+24)
        if width != 20:
            raise ValueError("Unexpected binary XML attribute format")
        attributes = {}
        for i in range(count):
            pos = off+16+start+i*width
            index = h.u32(data, pos+4)
            if index < len(ids):
                attributes[ids[index]] = pos
        if tag == "application":
            factory = attributes.get(0x0101057a)
            if factory is None or strings[h.u32(data, factory+16)] != OLD_FACTORY:
                raise ValueError("The existing factory changed")
        if tag != "activity" or 0x01010003 not in attributes:
            continue
        name = strings[h.u32(data, attributes[0x01010003]+16)]
        if name in COMPONENTS:
            raise ValueError("A Sony component is already present")
        if name != TEMPLATE:
            continue
        if h.u32(data, attributes[0x01010010]+16) != 0:
            raise ValueError("The template must be private")
        end = off+size
        if struct.unpack_from("<H", data, end)[0] != 0x103:
            raise ValueError("The template must be a leaf")
        template = (off, data[off:end+h.u32(data, end+4)])
        template_attributes = attributes
    if template is None or factory is None or end_application is None:
        raise ValueError("Required R130 components are missing")
    off, raw = template
    if 0x0101001d not in ids or 0x0101001f not in template_attributes:
        raise ValueError("The donor must provide launchMode and configChanges attributes")
    components = bytearray()
    for name, process in COMPONENTS.items():
        component = bytearray(raw)
        for attribute, value in ((0x01010003, name), (0x01010011, process)):
            pos = template_attributes[attribute]-off
            index = string(value)
            h.put32(component, pos+8, index)
            h.put32(component, pos+16, index)
        config = template_attributes[0x0101001f]-off
        h.put32(component, config+8, 0xffffffff)
        h.put32(component, config+16, 0xfb0)
        # One native session per private process. Repeated requests reach
        # onNewIntent instead of constructing another owner around that core.
        start, width, count, id_index, class_index, style_index = struct.unpack_from("<HHHHHH", component, 24)
        if (id_index, class_index, style_index) != (0, 0, 0):
            raise ValueError("Unexpected activity attribute indexes")
        begin = 16+start
        node_end = h.u32(component, 4)
        attributes = [bytes(component[begin+i*width:begin+(i+1)*width]) for i in range(count)]
        if any(ids[h.u32(attribute, 4)] == 0x0101001d for attribute in attributes):
            raise ValueError("Template launchMode must remain absent")
        namespace = h.u32(component, template_attributes[0x01010003]-off)
        attributes.append(struct.pack("<IIIHBBI", namespace, ids.index(0x0101001d), 0xffffffff, 8, 0, 0x10, 2))
        attributes.sort(key=lambda attribute: ids[h.u32(attribute, 4)])
        component = component[:begin]+b"".join(attributes)+component[begin+count*width:]
        h.put32(component, 4, node_end+width)
        struct.pack_into("<H", component, 28, count+1)
        components += component
    new_factory = string(NEW_FACTORY)
    old_pool = data[po:po+ps]
    count, styles, flags, start, style_start = struct.unpack_from("<IIIII", old_pool, 8)
    raw_strings = bytearray(old_pool[start:style_start or ps])
    offsets = []
    utf8 = bool(flags & 256)
    for text in added:
        offsets.append(len(raw_strings))
        encoded = text.encode("utf-8" if utf8 else "utf-16-le")
        raw_strings += h.encode_length(len(text), utf8)
        if utf8:
            raw_strings += h.encode_length(len(encoded), True)
        raw_strings += encoded + (b"\0" if utf8 else b"\0\0")
    raw_strings += b"\0" * (-len(raw_strings) % 4)
    pool = bytearray(old_pool[:ph] + old_pool[ph:ph+count*4] +
        struct.pack("<" + "I"*len(offsets), *offsets) +
        old_pool[ph+count*4:start] + raw_strings + (old_pool[style_start:] if style_start else b""))
    h.put32(pool, 4, len(pool))
    h.put32(pool, 8, count+len(added))
    h.put32(pool, 20, start+4*len(added))
    if style_start:
        h.put32(pool, 24, start+4*len(added)+len(raw_strings))
    delta = len(pool)-ps
    result = bytearray(data[:po]+pool+data[po+ps:end_application]+components+data[end_application:])
    h.put32(result, 4, len(result))
    factory_after = factory+delta
    if h.u32(data, factory+8) != 0xffffffff:
        h.put32(result, factory_after+8, new_factory)
    h.put32(result, factory_after+16, new_factory)
    insertion = end_application+delta
    inverse = bytearray(result)
    inverse = inverse[:insertion]+inverse[insertion+len(components):]
    h.put32(inverse, factory_after+8, h.u32(data, factory+8))
    h.put32(inverse, factory_after+16, h.u32(data, factory+16))
    inverse = inverse[:po]+old_pool+inverse[po+len(pool):]
    h.put32(inverse, 4, len(inverse))
    if inverse != data or h.string_pool(result, po) != strings+added:
        raise ValueError("The manifest transformation escaped its declared scope")
    list(h.chunks(result))
    return bytes(result)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    with args.base.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != BASE_SHA:
            raise ValueError("The exact R130 APK is required")
    with zipfile.ZipFile(args.base) as archive:
        original = archive.read("AndroidManifest.xml")
    result = patch(original)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(result)
    receipt = {"schema": "station.sony.internal.manifest.v1", "passed": True,
        "baseApkSha256": BASE_SHA, "sourceSha256": {
            "recipe/patch_manifest.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "payload": {"name": "AndroidManifest.xml", "path": str(args.out), "bytes": len(result),
            "sha256": hashlib.sha256(result).hexdigest()},
        "donorSha256": DONOR_MANIFEST_SHA, "sha256": hashlib.sha256(result).hexdigest(),
        "addedActivities": COMPONENTS, "exported": False, "factory": NEW_FACTORY,
        "ownerLaunchMode": "singleTask", "ownerConfigChanges": 0xfb0,
        "allOtherComponentsAndAttributesPreserved": True, "resourcesUnchanged": True,
        "exactInverse": True, "externalEmulatorActivityInvoked": False}
    args.receipt.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(receipt))

if __name__ == "__main__":
    main()
