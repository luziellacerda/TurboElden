"""Encode 105 untouched ANGLE readbacks as a local lossless animated WebP.

The source texture is the local private Sonic Adventure 2 cover. This script and
its JSON receipt are shareable; the generated cover animation stays outside Git.
Pillow only decodes the source, creates the explicit BOX-size texture fixture,
and encodes GL readbacks. No lighting is painted or synthesized in Python.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import sys
import numpy as np
from PIL import Image
import angle_gles2 as H

VERSION = Path(__file__).resolve().parents[1]
SOURCE = Path(r'G:\TURBORAMA\RetroBat\roms\dreamcast\media\images\Sonic Adventure 2 (Europe) (En,Ja,Fr,De,Es).png')
OUTPUT = Path(r'E:\ESTUDO APK\work\station-dreamcast-led-r80-20261008\visual-tests')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main(args, report):
    args.output.mkdir(parents=True, exist_ok=False)
    H.DLL = args.angle_dll
    H.REPORT = {'compile': [], 'gl_errors': []}
    source_hash = sha(args.source.read_bytes())
    shader_hash = sha(args.shader.read_bytes())
    shader = args.shader.read_text('utf8')
    gl = H.Angle()
    program = gl.program('R80 actual Dreamcast preview GLES100', '#version 100\n#define VERTEX\n' + shader,
                         '#version 100\n#define FRAGMENT\n' + shader)
    with Image.open(args.source) as source:
        pixels = np.array(source.convert('RGBA').resize((262, 393), Image.Resampling.BOX))
    texture = gl.texture(pixels)
    frames = []
    frame_hashes = []
    for i in range(105):
        readback = gl.render(program, texture, (262, 393), frame=2 * i, model=4, sheen=0)[0]
        frames.append(Image.fromarray(readback))
        frame_hashes.append(sha(readback.tobytes()))
    durations = [round((i + 1) * 1000 / 30) - round(i * 1000 / 30) for i in range(105)]
    path = args.output / 'sonic-adventure-2-dreamcast-led.webp'
    frames[0].save(path, format='WEBP', save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, lossless=True, quality=100, method=4, exact=True)
    with Image.open(path) as animation:
        decoded_hashes = []
        for i in range(animation.n_frames):
            animation.seek(i)
            decoded_hashes.append(sha(np.array(animation.convert('RGBA')).tobytes()))
    report.update({'passed': decoded_hashes == frame_hashes,
        'environment': 'Windows ANGLE; ES2 context requested, GLSL100 shaders. Actual context version is recorded below.',
        'private_media_kept_local': True, 'source_image': str(args.source), 'source_sha256': source_hash,
        'candidate_shader': str(args.shader), 'shader_sha256': shader_hash,
        'script_sha256': sha(Path(__file__).read_bytes()),
        'output': str(path), 'output_file_sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size,
        'size': [262, 393], 'frames': len(frames), 'frame_count_uniform': [2 * i for i in range(105)],
        'duration_ms': sum(durations), 'frame_durations_ms': durations,
        'gpu_readback_frame_sha256': frame_hashes, 'decoded_frame_sha256': decoded_hashes,
        'lossless_decoded_pixels_equal_gpu_readbacks': decoded_hashes == frame_hashes,
        'source_unchanged': sha(args.source.read_bytes()) == source_hash,
        'shader_unchanged': sha(args.shader.read_bytes()) == shader_hash,
        'GL': H.REPORT,
        'limitations': ['This is a PC ANGLE preview, not an Android screen recording or hardware performance measurement.',
                       'One local cover is used. The image and animation are private local media and are not added to Git.',
                       'ANGLE can report a newer compatible context despite requesting ES2; see GL.version.']})
    report['passed'] &= report['source_unchanged'] and report['shader_unchanged']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shader', type=Path, default=VERSION / 'native/premium-magazine-led-android.glsl')
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--angle-dll', type=Path, default=H.DLL)
    parser.add_argument('--output', type=Path, default=OUTPUT / datetime.datetime.now().strftime('preview-%Y%m%d-%H%M%S'))
    parser.add_argument('--evidence', type=Path, default=VERSION / 'evidence/animated-preview.json')
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
        (args.output / 'preview.json').write_text(serialized, encoding='utf8')
        args.evidence.write_text(serialized, encoding='utf8')
        print(json.dumps({k: report.get(k) for k in ('passed', 'output', 'bytes', 'frames', 'duration_ms', 'exception')}, indent=2), flush=True)
    sys.exit(0 if report.get('passed') else 1)
