"""Prepare the nine supplied collection clips and rebuild the R57 native layer retained in R66.

All generated files go to a new E: directory. No phone, Git or server mutation.
Run package_r67.py separately after this script completes successfully.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, shutil, subprocess

SNAPSHOT = Path(__file__).resolve().parent.parent
DEFAULT = r'E:\ESTUDO APK\work\station-collection-videos-r67-20261007'
parser = argparse.ArgumentParser()
parser.add_argument('--output', default=DEFAULT)
args = parser.parse_args()
work = Path(args.output).resolve()
if work.drive.upper() != 'E:' or work.exists():
    raise SystemExit('Use a new, nonexistent build directory on E:.')
if shutil.disk_usage(work.parent).free < 3 * 1024**3:
    raise SystemExit('Need at least 3 GiB free on E: for media, native compilation and unsigned APK.')

mapping = json.loads((SNAPSHOT / 'mapping.json').read_text('utf8'))
base = Path(r'E:\ESTUDO APK\work\station-compact-header-r57-20261006')
receipt = json.loads((base / 'evidence/native-build.json').read_text('utf8'))
ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
assert ffmpeg and ffprobe, 'FFmpeg and ffprobe are required'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

for name, expected in receipt['overlaySources'].items():
    assert sha(base / 'native' / name) == expected, name
assert receipt['soSHA256'] == '1dd67942358abebca8e82a4c457a9d4163a48b2e73aa856ce62ab78018cde922'
for row in mapping['videos']:
    assert sha(Path(mapping['sourceDirectory']) / row['file']) == row['sourceSha256'], row['file']

work.mkdir()
for folder in ('native', 'media', 'frames', 'temp', 'evidence', 'tests'):
    (work / folder).mkdir()
env = dict(os.environ, TEMP=str(work / 'temp'), TMP=str(work / 'temp'))
for name in receipt['overlaySources']:
    shutil.copyfile(base / 'native' / name, work / 'native' / name)
for source in (SNAPSHOT / 'native').iterdir():
    shutil.copyfile(source, work / 'native' / source.name)

def run(arguments, label):
    result = subprocess.run(list(map(str, arguments)), capture_output=True, env=env)
    (work / 'evidence' / (label + '.log')).write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(label + ': ' + result.stderr.decode('utf8', 'replace')[-2500:])
    return result.stdout

def probe(path):
    return json.loads(run([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path], 'probe-' + Path(path).stem))

assembly = ['.section .rodata.station_collections_r67,"a",%progbits']
media = []
for row in mapping['videos']:
    source = Path(mapping['sourceDirectory']) / row['file']
    original = probe(source)
    stream = next(s for s in original['streams'] if s['codec_type'] == 'video' and not s.get('disposition', {}).get('attached_pic'))
    assert (stream['width'], stream['height']) == (960, 960), row['file']
    output = work / 'media' / Path(row['asset']).name
    # 0:V:0 selects the moving video, excluding the embedded JPEG cover stream.
    run([ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', source,
         '-map', '0:V:0', '-vf', 'scale=720:720:flags=lanczos,setsar=1,fps=30',
         '-an', '-sn', '-dn', '-map_metadata', '-1', '-c:v', 'libx264',
         '-profile:v', 'baseline', '-level:v', '3.1', '-pix_fmt', 'yuv420p',
         '-preset', 'fast', '-crf', '20', '-maxrate', '3500k', '-bufsize', '7000k',
         '-threads', '2', '-g', '60', '-bf', '0', '-movflags', '+faststart', output], 'encode-' + row['key'])
    result = probe(output)
    assert len(result['streams']) == 1
    target = result['streams'][0]
    assert (target['codec_type'], target['codec_name'], target['width'], target['height'],
            target['r_frame_rate'], target['pix_fmt'], target['has_b_frames']) == ('video', 'h264', 720, 720, '30/1', 'yuv420p', 0)
    assert abs(float(target['duration']) - float(stream['duration'])) <= 1 / 30 + 0.00001
    run([ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-xerror', '-i', output,
         '-map', '0:V:0', '-f', 'null', '-'], 'decode-all-' + row['key'])
    frame = work / 'frames' / (row['key'] + '.rgb565')
    run([ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', output,
         '-map', '0:V:0', '-frames:v', '1', '-vf', 'vflip', '-pix_fmt', 'rgb565le', '-f', 'rawvideo', frame], 'frame-' + row['key'])
    assert frame.stat().st_size == 720 * 720 * 2
    symbol = row['symbol']
    assembly += ['.balign 16', '.global ' + symbol, '.hidden ' + symbol,
                 '.type ' + symbol + ',%object', symbol + ':',
                 '.incbin "' + frame.as_posix() + '"', '.size ' + symbol + ',.-' + symbol]
    media.append(dict(row, output=str(output), sha256=sha(output), bytes=output.stat().st_size,
                      probe=result, frameSHA256=sha(frame), fullFrameDecodePassed=True,
                      sourceFps=stream['r_frame_rate'], playbackSpeed=1, cropped=False, stretched=False))
    print('Prepared', row['key'], flush=True)

assembly_path = work / 'collection_previews.S'
assembly_path.write_text('\n'.join(assembly) + '\n', 'utf8')
compiler = Path(receipt['command'][0])
run([compiler, '--target=aarch64-linux-android26', '-c', assembly_path,
     '-o', work / 'collection_previews.o'], 'previews-object')
command = list(receipt['command'])
command[command.index(str(base / 'native/native_carousel.cpp'))] = str(work / 'native/native_carousel.cpp')
command[command.index(str(base / 'libturbo_carousel.so'))] = str(work / 'libturbo_carousel.so')
old_object = r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\neogeo_previews.o'
command[command.index(old_object)] = str(work / 'collection_previews.o')
run(command, 'native-build')

# Existing one-decoder policy regression; decoder selection is unchanged.
test = SNAPSHOT.parent / 'station-current-r55-20261006/tests/native/test_video_policy.cpp'
host = Path(r'C:\Program Files\LLVM\bin\clang++.exe')
run([host, '-std=c++17', '-Wall', '-Wextra', '-I', work / 'native', test,
     '-o', work / 'tests/video-policy.exe'], 'video-policy-compile')
run([work / 'tests/video-policy.exe'], 'video-policy-run')
run([host, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsyntax-only',
     '-I', work / 'native', SNAPSHOT / 'tests/menu_frame_policy.cpp'], 'menu-frame-policy')
catalog = json.loads((SNAPSHOT / 'evidence/catalog-bindings.json').read_text('utf8'))
cases = ['#include "collection_video_policy.h"', '#include <cstring>', '#include <cassert>', 'int main(){']
count = 0
for row in mapping['videos']:
    match = next(b for b in catalog['bindings'] if b['key'] == row['key'])
    for actual in match['matches']:
        platform, folder, asset = (json.dumps(value, ensure_ascii=False) for value in (actual['platform'], actual['folderPath'], row['asset'].removeprefix('assets/')))
        cases += ['{auto*v=collectionVideoFor(' + platform + ',' + folder + ',false);assert(v&&v->aspect==1.f&&std::strcmp(v->asset,' + asset + ')==0);}',
                  'assert(!collectionVideoFor(' + platform + ',' + folder + ',true));']
        count += 2
cases += ['assert(!collectionVideoFor("snes","# 5 - HACKS #",false));',
          'assert(!collectionVideoFor("neogeocd","# 5 - HACKS #",false));',
          'assert(!collectionVideoFor("neogeo","missing",false));',
          'assert(!collectionVideoFor(nullptr,"",false));', '}']
source = work / 'tests/routes.cpp'
source.write_text('\n'.join(cases) + '\n', 'utf8')
run([host, '-std=c++17', '-finput-charset=UTF-8', '-fexec-charset=UTF-8', '-I', work / 'native',
     source, '-o', work / 'tests/routes.exe'], 'routes-compile')
run([work / 'tests/routes.exe'], 'routes-run')

current = {p.name: sha(p) for p in (work / 'native').iterdir() if p.is_file()}
changed = [name for name in receipt['overlaySources'] if current[name] != receipt['overlaySources'][name]]
assert set(changed) == {'collection_video_policy.h', 'video720_posters.h'}
added = sorted(set(current) - set(receipt['overlaySources']))
assert set(added) == {'native_menu_power.h', 'station_menu_frame_policy.h'}
record = dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              baseAPK=r'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R66-20261007.apk',
              baseSHA256='e4397fd743c410ea060f17446706d9475b5568caad379e1a6df37672c60398d1',
              nativeSHA256=sha(work / 'libturbo_carousel.so'), nativeBytes=(work / 'libturbo_carousel.so').stat().st_size,
              nativeSources=current, changedNativeSources=changed, addedNativeSources=added,
              menuMaximumFps=30, idleDialogFps=15, menuFramePolicyChecks=8, videos=media, routingChecks=count + 4,
              oneDecoderPolicyTestsPassed=True, command=command, apkBuilt=False, installed=False)
(work / 'evidence/build.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', 'utf8')
print('R67 media and native layer ready; APK packaging and Android verification remain pending.')
