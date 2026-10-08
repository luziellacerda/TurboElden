"""Render the R80 candidate and frozen R79 reference through offscreen ANGLE GLES2.

PNG previews are untouched GL readbacks. Pillow decodes sources and constructs the
explicit BOX 262x393 texture fixture; it does not paint any lighting effect.
This establishes PC GLES rendering, never Android hardware performance/approval.
"""
from pathlib import Path
import argparse
import ctypes as C
import datetime
import hashlib
import json
import math
import sys
import time
import numpy as np
from PIL import Image
import angle_gles2 as H

VERSION = Path(__file__).resolve().parents[1]
REFERENCE = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r79\carousel-inputs\d0\premium-magazine-led-android.glsl')
CORPUS = Path(r'G:\TURBORAMA\RetroBat\roms\dreamcast\media\images')
TEMP = Path(r'E:\ESTUDO APK\work\station-dreamcast-led-r80-20261008\visual-tests')
FRAMES = (0, 16, 60, 111, 152, 182)
LEGACY_FRAMES = (0, 35, 60, 120, 175, 208, 209, 624, 625)
LEGACY = (
    ('snes', 0, Path(r'G:\TURBORAMA\RetroBat\roms\snes\media\revista\Arcana (USA).png')),
    ('mega', 1, Path(r'G:\TURBORAMA\RetroBat\roms\megadrive\media\revista\688 Attack Sub (USA, Europe).png')),
    ('n64', 2, Path(r"G:\TURBORAMA\RetroBat\roms\n64\media\revista\Yoshi's Story.png")),
    ('neogeo-aof', 3, Path(r'G:\TURBORAMA\RetroBat\roms\neogeo\media\revista\aof.png')),
    ('neogeo-svc', 3, Path(r'G:\TURBORAMA\RetroBat\roms\neogeo\media\revista\svc.png')),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def difference(a, b):
    d = np.abs(a.astype(np.int16) - b.astype(np.int16))
    return {'pixel_byte_equal': bool(np.array_equal(a, b)),
            'max_channel_delta': int(d.max()),
            'changed_pixels_gt1': int(np.any(d[:, :, :3] > 1, axis=2).sum()),
            'changed_alpha_pixels': int(np.count_nonzero(d[:, :, 3]))}


def diagnostic(shader, main):
    return shader[:shader.rindex('void main() {')] + main + '\n#endif\n'


def dilate(mask, radius):
    h, w = mask.shape
    padded = np.pad(mask, radius, constant_values=False)
    result = np.zeros_like(mask)
    for y in range(2 * radius + 1):
        for x in range(2 * radius + 1):
            result |= padded[y:y + h, x:x + w]
    return result


def main(args, report):
    start = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=False)
    H.DLL = args.angle_dll
    H.REPORT = {'compile': [], 'gl_errors': []}
    paths = [args.candidate, args.baseline, Path(__file__).resolve(), VERSION / 'tests/angle_gles2.py']
    report.update({'environment': 'Windows ANGLE offscreen, GLES100 shaders, ES2 context requested; not Android hardware',
                   'egl_context_client_version_requested': 2, 'shader_language_version': 100,
                   'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'output': str(args.output), 'frames': list(FRAMES),
                   'loaded_sources': {str(p): sha(p.read_bytes()) for p in paths},
                   'runtime': {'python': sys.version, 'numpy': np.__version__, 'pillow': Image.__version__},
                   'angle_dll_sha256': {name: sha((H.DLL / name).read_bytes()) for name in ('libEGL.dll', 'libGLESv2.dll')},
                   'dreamcast': [], 'legacy': [], 'controls': [], 'alpha': [], 'envelope': [], 'artifacts': [],
                   'limitations': ['PC ANGLE results do not establish Android hardware performance or visual approval.',
                       'The local Dreamcast corpus contains 26 covers; this does not establish all 243 catalog covers.',
                       'No phone, running decoder, emulator, APK or server is exercised.',
                       'ANGLE may report a newer compatible ES context despite requesting version 2; see GL.version. This does not establish strict ES2-only driver behavior.',
                       'BOX resizing is an explicit reduced texture fixture, not a readback modification.',
                       'Previews contain unmodified glReadPixels output. Masks are separate diagnostic readbacks.']})
    candidate = args.candidate.read_text('utf8')
    old = args.baseline.read_text('utf8')
    gl = H.Angle()
    pv = '#version 100\n#define VERTEX\n'
    pf = '#version 100\n#define FRAGMENT\n'
    modern = gl.program('R80 actual GLES100 magazine', pv + candidate, pf + candidate)
    previous = gl.program('Frozen R79 actual GLES100 magazine', pv + old, pf + old)
    passthrough = gl.program('Source texture passthrough', H.VERTEX, H.PASSTHROUGH)
    signature = gl.program('Dreamcast source-frame signature diagnostic', pv + candidate,
        pf + diagnostic(candidate, 'void main() { FragColor=vec4(vec3(' + args.signature + '()),1.); }'))
    geometry = gl.program('Dreamcast geometry diagnostic', pv + candidate,
        pf + diagnostic(candidate, 'void main() { vec2 p=vec2(uv.x,1.-uv.y)*vec2(1024,1536);FragColor=vec4(vec3(' + args.region + '(p)),1.); }'))
    flow_main = 'void main() {vec2 p=vec2(uv.x,1.-uv.y)*vec2(1024,1536);vec4 flow=lightEnvelope(p);FragColor=vec4(flow.xy,0.,1.);}'
    flow_new = gl.program('R80 shared movement diagnostic', pv + candidate, pf + diagnostic(candidate, flow_main))
    flow_old = gl.program('R79 SNES movement diagnostic', pv + old, pf + diagnostic(old, flow_main))
    delete_textures = H.bind(gl.gl, 'glDeleteTextures', None, [H.I, C.POINTER(H.U)])

    def free(texture):
        delete_textures(1, C.byref(H.U(texture)))

    def render(program, texture, size, frame=0, model=4, tint=(1., 1., 1., 1.)):
        gl.VertexAttrib4f(2, *tint)
        # The host selects Dreamcast orange. Legacy paths retain their existing uniforms.
        original = gl.Uniform4f
        color = gl.GetUniformLocation(program, b'ledColor')
        if model == 4:
            gl.Uniform4f = lambda loc, r, g, b, a: original(loc, 1., 106 / 255, 0., 1.) if loc == color and color >= 0 else original(loc, r, g, b, a)
        try:
            return gl.render(program, texture, size, frame=frame, model=model, sheen=0)[0]
        finally:
            gl.Uniform4f = original
            gl.VertexAttrib4f(2, 1., 1., 1., 1.)

    def save(name, pixels):
        path = args.output / (name + '.png')
        Image.fromarray(pixels).save(path)
        report['artifacts'].append({'path': str(path), 'file_sha256': sha(path.read_bytes()),
                                    'pixel_sha256': sha(pixels.tobytes()), 'size': list(pixels.shape[1::-1])})

    corpus = sorted(args.corpus.glob('*.png'))
    report['corpus_count'] = len(corpus)
    if not corpus:
        raise RuntimeError('Dreamcast corpus is empty')
    report['corpus'] = [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in corpus]
    masks = {}
    dummy = gl.texture(np.full((2, 2, 4), 255, dtype=np.uint8))
    for size in ((1024, 1536), (262, 393)):
        raw = render(geometry, dummy, size)[:, :, 0]
        radius = math.ceil(8 * size[0] / 1024) + 1
        masks[size] = dilate(raw > 0, radius)
        save('dreamcast-geometry-' + str(size[0]), np.dstack((raw, raw, raw, np.full_like(raw, 255))))
    for frame in range(0, 626, 5):
        a = render(flow_old, dummy, (8, 393), frame)
        b = render(flow_new, dummy, (8, 393), frame)
        report['envelope'].append({'frame': frame, **difference(a, b)})
    free(dummy)

    for index, file in enumerate(corpus):
        with Image.open(file) as image:
            original_image = image.convert('RGBA')
        if original_image.size != (1024, 1536):
            raise RuntimeError('Unexpected corpus dimensions: ' + str(file))
        previews = any(n in file.name for n in ('Sonic Adventure 2', 'Crazy Taxi 2', 'Marvel vs', 'Shenmue II')) and 'Disc 2' not in file.name and 'Disc 3' not in file.name
        for mode, source in (('original', original_image), ('BOX262x393', original_image.resize((262, 393), Image.Resampling.BOX))):
            pixels = np.array(source)
            texture = gl.texture(pixels)
            size = source.size
            base = render(passthrough, texture, size)
            sig = render(signature, texture, (1, 1))[0, 0, 0] / 255
            min_rgb = None
            max_rgb = None
            changed = np.zeros(pixels.shape[:2], dtype=bool)
            alpha_changes = 0
            frame_results = []
            prefix = f'{index:02d}-{mode}'
            if previews:
                save(prefix + '-source', base)
            for frame in FRAMES:
                result = render(modern, texture, size, frame)
                rgb = result[:, :, :3].astype(np.int16)
                min_rgb = rgb if min_rgb is None else np.minimum(min_rgb, rgb)
                max_rgb = rgb if max_rgb is None else np.maximum(max_rgb, rgb)
                delta = np.max(np.abs(rgb - base[:, :, :3].astype(np.int16)), axis=2)
                changed |= delta > 1
                frame_results.append({'frame': frame, **difference(base, result)})
                alpha_changes += int(np.count_nonzero(result[:, :, 3] != base[:, :, 3]))
                if previews:
                    save(prefix + '-frame-' + str(frame), result)
            moving = np.max(max_rgb - min_rgb, axis=2) > 1
            yy = (np.arange(size[1]) + .5) * 1536 / size[1]
            xx = (np.arange(size[0]) + .5) * 1024 / size[0]
            center = (yy[:, None] >= 280) & (yy[:, None] <= 1024) & (xx[None, :] >= 96) & (xx[None, :] <= 928)
            report['dreamcast'].append({'file': file.name, 'mode': mode, 'texture_dimensions': list(size),
                'texture_pixel_sha256': sha(pixels.tobytes()), 'signature': float(sig),
                'temporal_changed_pixels_gt1': int(moving.sum()),
                'changed_outside_expanded_geometry_gt1': int((changed & ~masks[size]).sum()),
                'moving_outside_expanded_geometry_gt1': int((moving & ~masks[size]).sum()),
                'central_art_changed_pixels_gt1': int((changed & center).sum()),
                'alpha_changed_pixels_all_frames': alpha_changes, 'frames': frame_results})
            free(texture)
        print(f'Dreamcast {index + 1}/{len(corpus)}: {file.name}', flush=True)

    for name, model, file in LEGACY:
        if not file.exists():
            report['legacy'].append({'name': name, 'model': model, 'missing': str(file)})
            continue
        with Image.open(file) as image:
            source = image.convert('RGBA')
        for mode, image in (('original', source), ('BOX262x393', source.resize((262, 393), Image.Resampling.BOX))):
            texture = gl.texture(np.array(image))
            for frame in LEGACY_FRAMES:
                before = render(previous, texture, (262, 393), frame, model)
                after = render(modern, texture, (262, 393), frame, model)
                report['legacy'].append({'name': name, 'model': model, 'source_sha256': sha(file.read_bytes()),
                    'texture_mode': mode, 'frame': frame, **difference(before, after)})
            free(texture)
        print('Legacy comparison: ' + name, flush=True)

    # Controls include unframed artwork, flat blue, flat orange and transparency.
    crop_fragment = '#version 100\nprecision highp float;varying vec2 uv;uniform sampler2D frame;void main(){gl_FragColor=texture2D(frame,mix(vec2(.16,.32),vec2(.88,.78),uv));}'
    crop_program = gl.program('Unframed central artwork control', H.VERTEX, crop_fragment)
    controls = []
    for name, rgba in (('plain-blue', (0, 160, 255, 255)), ('plain-orange', (255, 120, 0, 255)), ('white', (255, 255, 255, 255))):
        controls.append((name, np.full((393, 262, 4), rgba, dtype=np.uint8)))
    texture = gl.texture(np.array(Image.open(corpus[0]).convert('RGBA')))
    controls.append(('unframed-game-art', render(crop_program, texture, (262, 393))))
    free(texture)
    for name, pixels in controls:
        texture = gl.texture(pixels)
        base = render(passthrough, texture, (262, 393))
        sig = float(render(signature, texture, (1, 1))[0, 0, 0] / 255)
        for frame in FRAMES:
            actual = render(modern, texture, (262, 393), frame)
            report['controls'].append({'name': name, 'signature': sig, 'frame': frame, **difference(base, actual)})
        free(texture)

    # Exercise real Dreamcast color pixels with an alpha ramp and native vertex tint.
    with Image.open(corpus[0]) as source:
        alpha_pixels = np.array(source.convert('RGBA').resize((262, 393), Image.Resampling.BOX))
    alpha_pixels[:, :, 3] = np.linspace(0, 255, 262, dtype=np.uint8)[None, :]
    texture = gl.texture(alpha_pixels)
    for tint in ((1., 1., 1., 1.), (.8, .9, .7, .45)):
        expected_alpha = np.rint(alpha_pixels[:, :, 3].astype(float) * tint[3]).astype(np.uint8)
        for frame in FRAMES:
            result = render(modern, texture, (262, 393), frame, tint=tint)
            delta = np.abs(result[:, :, 3].astype(np.int16) - expected_alpha.astype(np.int16))
            report['alpha'].append({'frame': frame, 'tint': list(tint), 'max_alpha_error': int(delta.max()),
                                    'alpha_pixels_error_gt1': int((delta > 1).sum())})
    free(texture)
    report['sources_unchanged'] = {path: sha(Path(path).read_bytes()) == digest for path, digest in report['loaded_sources'].items()}
    report['corpus_unchanged'] = all(sha(Path(v['path']).read_bytes()) == v['sha256'] for v in report['corpus'])
    report['GL'] = H.REPORT
    report['elapsed_seconds'] = time.perf_counter() - start
    report['passed'] = (len(report['dreamcast']) == 2 * len(corpus)
        and all(v['signature'] >= .99 and v['temporal_changed_pixels_gt1'] > 0
                and v['changed_outside_expanded_geometry_gt1'] == 0
                and v['moving_outside_expanded_geometry_gt1'] == 0
                and v['central_art_changed_pixels_gt1'] == 0
                and v['alpha_changed_pixels_all_frames'] == 0 for v in report['dreamcast'])
        and all(v.get('pixel_byte_equal', False) for v in report['legacy'])
        and all(v['pixel_byte_equal'] and v['signature'] == 0 for v in report['controls'])
        and all(v['alpha_pixels_error_gt1'] == 0 for v in report['alpha'])
        and all(v['pixel_byte_equal'] for v in report['envelope'])
        and all(report['sources_unchanged'].values()) and report['corpus_unchanged'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=VERSION / 'native/premium-magazine-led-android.glsl')
    parser.add_argument('--baseline', type=Path, default=REFERENCE)
    parser.add_argument('--corpus', type=Path, default=CORPUS)
    parser.add_argument('--angle-dll', type=Path, default=H.DLL)
    parser.add_argument('--output', type=Path, default=TEMP / datetime.datetime.now().strftime('angle-%Y%m%d-%H%M%S'))
    parser.add_argument('--evidence', type=Path, default=VERSION / 'evidence/angle-visual-validation.json')
    parser.add_argument('--region', default='dreamcastRegion')
    parser.add_argument('--signature', default='dreamcastSignature')
    args = parser.parse_args()
    report = {'passed': False}
    try:
        main(args, report)
    except Exception as error:
        report['exception'] = repr(error)
        report['GL'] = H.REPORT
        raise
    finally:
        args.output.mkdir(parents=True, exist_ok=True)
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(report, indent=2) + '\n'
        (args.output / 'report.json').write_text(serialized, encoding='utf8')
        args.evidence.write_text(serialized, encoding='utf8')
        print(json.dumps({'passed': report.get('passed', False), 'output': str(args.output),
                          'evidence': str(args.evidence), 'exception': report.get('exception')}, indent=2), flush=True)
    sys.exit(0 if report.get('passed') else 1)
