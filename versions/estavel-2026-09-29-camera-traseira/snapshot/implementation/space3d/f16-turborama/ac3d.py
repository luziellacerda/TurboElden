"""Small AC3Db reader for the native F-16 asset conversion.

Format reference: https://www.inivis.com/ac3d/man/ac3dfileformat.html
No triangulation, normal generation, material remapping or mesh filtering occurs.
``materials, objects = load_ac(path)`` returns dictionaries. Object ``vertices``
are an Nx3 numpy array in model/world coordinates; ``vertices_local`` preserves
the input array. Faces contain ``refs`` of (vertex_index, u, v), ``flags`` and
the original ``mat`` index (None when omitted). Texture repeat/offset remain
separate from the unmodified face UVs. Texture paths resolve against the AC file.
"""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

try:
    import numpy as np
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'python-libs'))
    import numpy as np


class AC3DError(ValueError):
    """Malformed, unsupported or truncated AC3D input."""


def _tokens(line: str) -> list[str]:
    result = []
    cursor = 0
    pattern = re.compile(r'"(?:\\.|[^"\\])*"|[^\s"]+')
    for match in pattern.finditer(line):
        if line[cursor:match.start()].strip():
            raise AC3DError('Malformed quoted token')
        item = match.group()
        if item.startswith('"'):
            item = item[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        result.append(item)
        cursor = match.end()
    if line[cursor:].strip():
        raise AC3DError('Unterminated quoted token')
    return result


def _integer(value: str) -> int:
    # MATERIAL shininess is often emitted with decimal leading zeroes (010).
    return int(value, 16 if value.lower().lstrip('+-').startswith('0x') else 10)


class _Reader:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.raw = self.path.read_bytes()
        self.pos = 0
        self.materials = []
        self.roots = []

    def fail(self, message):
        line = self.raw.count(b'\n', 0, self.pos) + 1
        raise AC3DError(f'{self.path}:{line}: {message}')

    def line(self, required=True):
        while self.pos < len(self.raw):
            end = self.raw.find(b'\n', self.pos)
            if end < 0:
                end = len(self.raw)
            text = self.raw[self.pos:end].rstrip(b'\r').decode('latin-1').strip()
            self.pos = min(end + 1, len(self.raw))
            if text and not text.startswith('#'):
                try:
                    return _tokens(text)
                except AC3DError as exc:
                    self.fail(str(exc))
        if required:
            self.fail('Unexpected end of file')
        return None

    def count(self, tokens, key):
        if len(tokens) != 2:
            self.fail(f'{key} requires one nonnegative integer')
        try:
            count = _integer(tokens[1])
        except ValueError:
            self.fail(f'Invalid {key} count')
        if not 0 <= count <= len(self.raw):
            self.fail(f'Invalid {key} count {count}')
        return count

    def floats(self, tokens, count, label):
        if len(tokens) != count:
            self.fail(f'{label} needs {count} values, got {len(tokens)}')
        try:
            numbers = [float(v) for v in tokens]
        except ValueError:
            self.fail(f'Invalid number in {label}')
        if not np.isfinite(numbers).all():
            self.fail(f'Non-finite number in {label}')
        return numbers

    def material(self, tokens):
        if len(tokens) < 2:
            self.fail('MATERIAL requires a name')
        material = {'index': len(self.materials), 'name': tokens[1]}
        sizes = {'rgb': 3, 'amb': 3, 'emis': 3, 'spec': 3, 'shi': 1, 'trans': 1}
        cursor = 2
        while cursor < len(tokens):
            key = tokens[cursor]
            if key not in sizes or key in material:
                self.fail(f'Unexpected or repeated MATERIAL field {key}')
            n = sizes[key]
            numbers = self.floats(tokens[cursor + 1:cursor + 1 + n], n, key)
            material[key] = numbers[0] if n == 1 else numbers
            cursor += n + 1
        if not set(sizes).issubset(material):
            self.fail('Incomplete MATERIAL record')
        self.materials.append(material)

    def face(self):
        face = {'flags': 0, 'mat': None, 'refs': []}
        seen = set()
        while True:
            tokens = self.line()
            key = tokens[0]
            if key in ('SURF', 'mat'):
                if key in seen:
                    self.fail(f'Repeated surface field {key}')
                seen.add(key)
                value = self.count(tokens, key)
                face['flags' if key == 'SURF' else 'mat'] = value
            elif key == 'refs':
                for _ in range(self.count(tokens, key)):
                    ref = self.line()
                    if len(ref) != 3:
                        self.fail('A surface reference requires index, u and v')
                    try:
                        index = _integer(ref[0])
                    except ValueError:
                        self.fail('Invalid vertex reference')
                    if index < 0:
                        self.fail(f'Negative vertex index {index}')
                    u, v = self.floats(ref[1:], 2, 'UV')
                    face['refs'].append((index, u, v))
                return face
            else:
                self.fail(f'Expected SURF, mat or refs, got {key}')

    def object(self, start, depth=0):
        if depth > 512:
            self.fail('Object hierarchy exceeds 512 levels')
        if len(start) != 2 or start[0] != 'OBJECT':
            self.fail('Expected OBJECT')
        obj = {'type': start[1], 'name': '', 'data': b'', 'texture_raw': None,
               'texrep': (1., 1.), 'texoff': (0., 0.), 'crease': 45.,
               'rot': np.eye(3), 'loc': np.zeros(3), 'vertices_local': np.empty((0, 3)),
               'faces': [], 'children': [], 'extras': [], 'url': ''}
        seen = set()
        while True:
            tokens = self.line()
            key = tokens[0]
            if key in ('numvert', 'numsurf') and key in seen:
                self.fail(f'Repeated {key} in object')
            seen.add(key)
            if key == 'kids':
                for _ in range(self.count(tokens, key)):
                    obj['children'].append(self.object(self.line(), depth + 1))
                break
            elif key in ('name', 'texture', 'url'):
                if len(tokens) != 2:
                    self.fail(f'{key} requires a single string')
                obj['texture_raw' if key == 'texture' else key] = tokens[1]
            elif key == 'data':
                length = self.count(tokens, key)
                end = self.pos + length
                if end > len(self.raw):
                    self.fail('Truncated data block')
                # AC3Db is byte-oriented ASCII. Do not tokenize these N bytes:
                # arbitrary newlines and token-looking content are valid data.
                obj['data'] = self.raw[self.pos:end]
                self.pos = end
                if self.raw[self.pos:self.pos + 2] == b'\r\n':
                    self.pos += 2
                elif self.raw[self.pos:self.pos + 1] == b'\n':
                    self.pos += 1
            elif key == 'rot':
                obj['rot'] = np.array(self.floats(tokens[1:], 9, key)).reshape(3, 3)
            elif key == 'loc':
                obj['loc'] = np.array(self.floats(tokens[1:], 3, key))
            elif key in ('texrep', 'texoff'):
                obj[key] = tuple(self.floats(tokens[1:], 2, key))
            elif key == 'crease':
                obj[key] = self.floats(tokens[1:], 1, key)[0]
            elif key == 'numvert':
                count = self.count(tokens, key)
                obj['vertices_local'] = np.array(
                    [self.floats(self.line(), 3, 'vertex') for _ in range(count)],
                    dtype=np.float64).reshape(-1, 3)
            elif key == 'numsurf':
                obj['faces'] = [self.face() for _ in range(self.count(tokens, key))]
            elif key in ('OBJECT', 'MATERIAL'):
                self.fail('Object ended without required kids record')
            else:
                # Unknown single-line object metadata (e.g. subdiv, hidden) is
                # retained. Structural records are deliberately never skipped.
                obj['extras'].append(tokens)
        for face in obj['faces']:
            for index, _, _ in face['refs']:
                if index >= len(obj['vertices_local']):
                    self.fail(f'Vertex index {index} outside object {obj["name"]!r}')
        return obj

    def read(self):
        header = self.line()
        if len(header) != 1 or header[0] != 'AC3Db':
            self.fail('Only the documented AC3Db format is supported')
        while (tokens := self.line(required=False)) is not None:
            if tokens[0] == 'MATERIAL':
                self.material(tokens)
            elif tokens[0] == 'OBJECT':
                self.roots.append(self.object(tokens))
            else:
                self.fail(f'Unexpected top-level record {tokens[0]}')
        flattened = []

        def visit(obj, parent_transform, ancestors):
            transform = np.eye(4)
            transform[:3, :3] = obj['rot']
            transform[:3, 3] = obj['loc']
            transform = parent_transform @ transform
            local = obj['vertices_local']
            obj['vertices'] = local @ transform[:3, :3].T + transform[:3, 3]
            obj['transform'] = transform
            obj['ancestors'] = tuple(ancestors)
            obj['path'] = tuple(ancestors) + (obj['name'] or obj['type'],)
            texture = obj['texture_raw']
            obj['texture'] = str((self.path.parent / texture.replace('\\', '/')).resolve()) if texture else None
            obj['source'] = str(self.path)
            for face in obj['faces']:
                if face['mat'] is not None and face['mat'] >= len(self.materials):
                    self.fail(f'Material index {face["mat"]} outside palette')
            flattened.append(obj)
            for child in obj['children']:
                visit(child, transform, obj['path'])

        for root in self.roots:
            visit(root, np.eye(4), ())
        return self.materials, flattened


def load_ac(path):
    """Return (materials, preorder_objects), with composed ancestor transforms."""
    return _Reader(Path(path)).read()


def inventory(path):
    """JSON-safe structural inventory; includes all objects without filtering."""
    path = Path(path).resolve()
    materials, objects = load_ac(path)
    entries = []
    for obj in objects:
        vertices = obj['vertices']
        entries.append({
            'name': obj['name'], 'type': obj['type'], 'path': list(obj['path']),
            'vertices': len(vertices), 'surfaces': len(obj['faces']),
            'polygon_fan_triangles': sum(max(0, len(f['refs']) - 2) for f in obj['faces'] if f['flags'] & 15 == 0),
            'bbox': [vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()] if len(vertices) else None,
            'texture': obj['texture'], 'texture_raw': obj['texture_raw'],
            'texture_exists': Path(obj['texture']).is_file() if obj['texture'] else None,
            'material_indices': sorted({f['mat'] for f in obj['faces'] if f['mat'] is not None}),
            'surface_flags': dict(Counter(str(f['flags']) for f in obj['faces'])),
            'crease': obj['crease'], 'children': len(obj['children']),
            'transform': obj['transform'].tolist(), 'extras': obj['extras'],
        })
    arrays = [o['vertices'] for o in objects if len(o['vertices'])]
    all_vertices = np.concatenate(arrays) if arrays else np.empty((0, 3))
    return {'source': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'objects': entries, 'materials': materials,
            'totals': {'objects': len(objects), 'vertices': len(all_vertices),
                       'surfaces': sum(o['surfaces'] for o in entries),
                       'polygon_fan_triangles': sum(o['polygon_fan_triangles'] for o in entries)},
            'bbox': [all_vertices.min(axis=0).tolist(), all_vertices.max(axis=0).tolist()] if len(all_vertices) else None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    paths = args.paths or [directory.parent / 'f16-source/Models/f16.ac',
                           directory.parent / 'f16-source/Models/nozzle-GE.ac']
    result = {'format_reference': 'https://www.inivis.com/ac3d/man/ac3dfileformat.html',
              'models': [inventory(path) for path in paths]}
    output = args.output or directory / 'ac3d-inventory.json'
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'inventory': str(output), 'models': [
        {'source': model['source'], **model['totals'], 'bbox': model['bbox']} for model in result['models']]}, indent=2))
