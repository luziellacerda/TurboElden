"""Add only the private Dolphin Station launch anchors to the R125 AXML.

The normal Dolphin, EmulationActivity, application, permissions and processes
remain byte-identical. The process entry clones the existing Dolphin Netplay
entry, while the result anchor clones the main-process Station room activity.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct, zipfile

BASE_SHA = 'cf37f63733c735a967fe98ac2e8f3fa1ac4969f7f7a1e1c4e52d0a933780283c'
ACTIVITIES = (
    ('org.emulationstation.frontend.netplay.StationDolphinActivity',
     'org.emulationstation.frontend.netplay.StationRoomsActivity', None),
    ('org.emulationstation.frontend.netplay.StationDolphinOnlineActivity',
     'org.emulationstation.frontend.netplay.StationDolphinNetplayActivity', ':dolphin'),
)

def fs(path):
    path = str(Path(path).resolve())
    if path.startswith('\\\\?\\'): return path
    return '\\\\?\\UNC\\' + path[2:] if path.startswith('\\\\') else '\\\\?\\' + path

def patch(data, helper):
    if hashlib.sha256(data).hexdigest() != BASE_SHA:
        raise ValueError('Unexpected R125 manifest')
    chunks = list(helper.chunks(data))
    po, _, ph, ps = next(c for c in chunks if c[1] == 1)
    ro, _, rh, rs = next(c for c in chunks if c[1] == 0x180)
    resources = list(struct.unpack_from('<' + 'I' * ((rs - rh) // 4), data, ro + rh))
    strings = helper.string_pool(data, po)
    if any(name in strings for name, _, _ in ACTIVITIES):
        raise ValueError('Dolphin anchors already present')
    application_end = None
    clones = {}
    for offset, kind, header, size in chunks:
        if kind == 0x103 and strings[helper.u32(data, offset + 20)] == 'application':
            application_end = offset
        if kind != 0x102 or strings[helper.u32(data, offset + 20)] != 'activity':
            continue
        attr_start, attr_size, count = struct.unpack_from('<HHH', data, offset + 24)
        if attr_size != 20: raise ValueError('Unexpected attribute width')
        attrs = {}
        for i in range(count):
            pos = offset + 16 + attr_start + i * attr_size
            index = helper.u32(data, pos + 4)
            if index < len(resources): attrs[resources[index]] = pos
        name_at = attrs.get(0x01010003)
        if name_at is None: continue
        old_name = strings[helper.u32(data, name_at + 16)]
        for index, (new_name, template, expected_process) in enumerate(ACTIVITIES):
            if old_name != template: continue
            if helper.u32(data, attrs[0x01010010] + 16) != 0:
                raise ValueError('Template must remain private')
            process_at = attrs.get(0x01010011)
            if expected_process is None:
                if process_at is not None: raise ValueError('Anchor must remain in main process')
            elif process_at is None or strings[helper.u32(data, process_at + 16)] != expected_process:
                raise ValueError('Dolphin process mismatch')
            end = offset + size
            if struct.unpack_from('<H', data, end)[0] != 0x103:
                raise ValueError('Activity template is not a leaf')
            clone = bytearray(data[offset:end + helper.u32(data, end + 4)])
            rel = name_at - offset
            helper.put32(clone, rel + 8, len(strings) + index)
            helper.put32(clone, rel + 16, len(strings) + index)
            clones[new_name] = bytes(clone)
    if application_end is None or len(clones) != len(ACTIVITIES):
        raise ValueError('Missing private activity template')

    count, styles, flags, start, style_start = struct.unpack_from('<IIIII', data, po + 8)
    old_pool = data[po:po + ps]
    end = style_start or ps
    original_string_data = old_pool[start:end]
    utf8 = bool(flags & 256)
    new_data = bytearray(original_string_data)
    offsets = []
    for name, _, _ in ACTIVITIES:
        offsets.append(len(new_data))
        encoded = name.encode('utf-8' if utf8 else 'utf-16-le')
        new_data += helper.encode_length(len(name), utf8)
        if utf8: new_data += helper.encode_length(len(encoded), True)
        new_data += encoded + (b'\0' if utf8 else b'\0\0')
    new_data += b'\0' * (-len(new_data) % 4)
    offset_data = struct.pack('<' + 'I' * len(offsets), *offsets)
    pool = bytearray(old_pool[:ph] + old_pool[ph:ph + count * 4] + offset_data +
                     old_pool[ph + count * 4:start] + new_data +
                     (old_pool[style_start:] if style_start else b''))
    helper.put32(pool, 4, len(pool)); helper.put32(pool, 8, count + len(ACTIVITIES))
    helper.put32(pool, 20, start + len(offset_data))
    if style_start: helper.put32(pool, 24, start + len(offset_data) + len(new_data))
    added = b''.join(clones[name] for name, _, _ in ACTIVITIES)
    output = bytearray(data[:po] + pool + data[po + ps:application_end] + added + data[application_end:])
    helper.put32(output, 4, len(output))
    insert = application_end + len(pool) - ps
    reverse = bytearray(output[:insert] + output[insert + len(added):])
    reverse = reverse[:po] + old_pool + reverse[po + len(pool):]
    helper.put32(reverse, 4, len(reverse))
    if bytes(reverse) != data: raise ValueError('Original manifest changed')
    if helper.string_pool(output, po) != strings + [a[0] for a in ACTIVITIES]:
        raise ValueError('String pool changed')
    list(helper.chunks(output))
    return bytes(output)

def main():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--apk', type=Path); source.add_argument('--manifest', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    helper_path = Path(__file__).resolve().parents[2] / 'station-game-menu-controller-audit-r120-20261010/recipes/patch_component_factory.py'
    spec = importlib.util.spec_from_file_location('axml', fs(helper_path))
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    if args.apk:
        with zipfile.ZipFile(fs(args.apk)) as archive: original = archive.read('AndroidManifest.xml')
    else:
        with open(fs(args.manifest), 'rb') as stream: original = stream.read()
    result = patch(original, helper)
    Path(fs(args.out.parent)).mkdir(parents=True, exist_ok=True)
    with open(fs(args.out), 'xb') as stream: stream.write(result)
    print(json.dumps({'sha256': hashlib.sha256(result).hexdigest(),
                      'addedActivities': [a[0] for a in ACTIVITIES], 'reverseIdentity': True}))

if __name__ == '__main__': main()
