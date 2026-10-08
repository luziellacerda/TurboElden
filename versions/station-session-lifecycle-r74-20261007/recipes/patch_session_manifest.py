"""Add only the private session anchor Service to the exact R73 binary manifest.

Preserves every existing XML node, resource ID and string index. No resource
table rebuild, exported component or permission change is permitted.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import zipfile

BASE_SHA = 'cc00ab597882646285b963cf28c7bbc25088092268450d610e35d83a7e6444c4'
SERVICE = 'org.emulationstation.frontend.netplay.StationSessionService'
ANDROID = 'http://schemas.android.com/apk/res/android'
NONE = 0xffffffff

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def chunks(data):
    require(struct.unpack_from('<HHI', data) == (3, 8, len(data)), 'Invalid XML header')
    offset = 8
    while offset < len(data):
        kind, header, size = struct.unpack_from('<HHI', data, offset)
        require(8 <= header <= size and offset + size <= len(data), 'Invalid chunk')
        yield kind, data[offset:offset + size]
        offset += size
    require(offset == len(data), 'Trailing XML bytes')

def append_strings(chunk, values, parser):
    kind, header, size = struct.unpack_from('<HHI', chunk)
    count, styles, flags, start, style_start = struct.unpack_from('<5I', chunk, 8)
    require(kind == 1 and header == 28 and styles == 0 and style_start == 0,
            'Exact unstyled R73 string pool required')
    strings = parser.pool(chunk, 0, header)
    additions = [s for s in values if s not in strings]
    require(len(additions) == len(set(additions)), 'Duplicate additions')
    offsets = list(struct.unpack_from('<' + 'I' * count, chunk, header))
    payload = bytearray(chunk[start:])
    def length(n, wide):
        require(n < (1 << (31 if wide else 15)), 'Oversize string')
        if wide:
            return struct.pack('<H', n) if n < 0x8000 else struct.pack('<HH', 0x8000 | (n >> 16), n & 0xffff)
        return bytes([n]) if n < 0x80 else bytes([0x80 | (n >> 8), n & 0xff])
    for value in additions:
        offsets.append(len(payload))
        utf16 = value.encode('utf-16le')
        if flags & 0x100:
            raw = value.encode('utf8')
            payload.extend(length(len(utf16) // 2, False) + length(len(raw), False) + raw + b'\0')
        else:
            payload.extend(length(len(utf16) // 2, True) + utf16 + b'\0\0')
    payload.extend(b'\0' * (-len(payload) % 4))
    count += len(additions)
    new_start = header + count * 4
    result = (struct.pack('<HHI5I', 1, header, new_start + len(payload), count, 0,
                          flags & ~1, new_start, 0)
              + struct.pack('<' + 'I' * count, *offsets) + payload)
    require(parser.pool(result, 0, header) == strings + additions, 'Pool append mismatch')
    return bytes(result), strings + additions

def patch(data, parser):
    require(sha(data) == BASE_SHA, 'Exact installed R73 manifest required')
    parts = list(chunks(data))
    pools = [i for i, (kind, _) in enumerate(parts) if kind == 1]
    require(len(pools) == 1, 'One string pool required')
    pool_index = pools[0]
    old_strings = parser.pool(parts[pool_index][1], 0, 28)
    require(SERVICE not in old_strings, 'Service already exists')
    new_pool, strings = append_strings(parts[pool_index][1], ['service', SERVICE], parser)
    indices = {s: strings.index(s) for s in ('service', SERVICE, ANDROID, 'name', 'exported')}
    resources = next(c for k, c in parts if k == 0x180)
    require(struct.unpack_from('<I', resources, 8 + indices['name'] * 4)[0] == 0x01010003,
            'Name resource differs')
    require(struct.unpack_from('<I', resources, 8 + indices['exported'] * 4)[0] == 0x01010010,
            'Exported resource differs')
    def attribute(name, typ, value, raw=NONE):
        return struct.pack('<IIIHBBI', indices[ANDROID], indices[name], raw, 8, 0, typ, value)
    attrs = (attribute('name', 3, indices[SERVICE], indices[SERVICE])
             + attribute('exported', 0x12, 0))
    start = (struct.pack('<HHIII', 0x102, 16, 36 + len(attrs), 0, NONE)
             + struct.pack('<II6H', NONE, indices['service'], 20, 20, 2, 0, 0, 0) + attrs)
    end = struct.pack('<HHIIIII', 0x103, 16, 24, 0, NONE, NONE, indices['service'])
    stack, added, output = [], 0, []
    for i, (kind, chunk) in enumerate(parts):
        if kind == 0x102:
            stack.append(old_strings[struct.unpack_from('<I', chunk, 20)[0]])
        elif kind == 0x103:
            name = old_strings[struct.unpack_from('<I', chunk, 20)[0]]
            require(stack and stack[-1] == name, 'XML nesting mismatch')
            if name == 'application':
                require(stack == ['manifest', 'application'], 'Wrong application nesting')
                output += [start, end]
                added += 1
            stack.pop()
        output.append(new_pool if i == pool_index else chunk)
    require(added == 1 and not stack, 'Service placement mismatch')
    payload = b''.join(output)
    result = struct.pack('<HHI', 3, 8, 8 + len(payload)) + payload
    # Existing node bytes, including attribute types and references, are immutable.
    old_nodes = [c for k, c in parts if k != 1]
    new_nodes = [c for k, c in chunks(result) if k != 1]
    require(new_nodes.count(start) == 1 and new_nodes.count(end) == 1, 'Duplicate Service')
    require([c for c in new_nodes if c not in (start, end)] == old_nodes, 'Existing nodes changed')
    sem = parser.attributes(result)
    services = [(tag, a) for tag, a in sem if tag == 'service' and any(v['value'] == SERVICE for v in a)]
    require(len(services) == 1, 'Service declaration missing')
    attrs = {a['name']: a for a in services[0][1]}
    require(set(attrs) == {'name', 'exported'} and attrs['exported']['value'] == 0,
            'Private main-process Service required')
    return result, dict(baseSHA256=sha(data), resultSHA256=sha(result), service=SERVICE,
                        exported=False, process='application default', addedPermissions=[],
                        existingNodesByteIdentical=True, oldStringIndicesPreserved=True,
                        addedNodes=2, size=len(result))

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--repo', required=True)
    p.add_argument('--workspace', required=True)
    p.add_argument('--base', required=True)
    a = p.parse_args()
    source = Path(a.repo) / 'versions/station-online-layout-r71-20261007/recipes/patch_navigation_manifest.py'
    spec = importlib.util.spec_from_file_location('manifest_reader', source)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    with zipfile.ZipFile(a.base) as z:
        original = z.read('AndroidManifest.xml')
    updated, receipt = patch(original, parser)
    work = Path(a.workspace)
    (work / 'AndroidManifest.xml').write_bytes(updated)
    (work / 'evidence/manifest.json').write_text(json.dumps(receipt, indent=2) + '\n', 'utf8')
    print(json.dumps(receipt, indent=2))
