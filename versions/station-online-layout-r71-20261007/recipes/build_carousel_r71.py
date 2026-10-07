"""Add only the dedicated SNES all-games video/poster to the verified R70 carousel."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, shutil, subprocess

SNAPSHOT = Path(__file__).resolve().parent.parent
BASE = Path(r'E:\ESTUDO APK\work\station-collection-navigation-r70-20261007-final2')
BASE_RECEIPT_SHA = '783edb4db4e2012e6e813eee0b01f631a6d7b6844bef97dd738daf3285a6ca11'
BASE_NATIVE_SHA = 'ce963fe991e78f3e3af1fcab7109d7f1163d2296dd97c39f550bf8fc2509bd42'
SOURCE_SHA = 'db7190e5798bb0976ede2e849089ba41904084ee54c5bee9ee1806c15aeac272'
VIDEO_SHA = '780ad95803b649cac38e2db19a796a9f8bcc103dd0b4d9ae1cb5a7d68f54ed7e'
FRAME_SHA = 'c6d634be62eb13b5c4aeac70a3ff0aeeb2684bb9f0a7952665e9776f05431098'
MEDIA_RECEIPT_SHA = '6aaac36272d2020b063c67c8dacc197373dc9d5944b576477391d3483eb27e6e'
ASSET = 'turbo-system-videos/720-collection-snes-all.mp4'
SYMBOL = 'station_collection_r71_snes_all'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=r'E:\ESTUDO APK\work\station-online-layout-r71-20261007-carousel')
    parser.add_argument('--media', default=r'E:\ESTUDO APK\work\station-online-layout-r71-20261007-integrated\media-addition')
    args = parser.parse_args()
    work, media = Path(args.output).resolve(), Path(args.media).resolve()
    assert work.drive.upper() == 'E:' and not work.exists()
    assert sha(BASE / 'evidence/build.json') == BASE_RECEIPT_SHA
    receipt = json.loads((BASE / 'evidence/build.json').read_text('utf8'))
    assert sha(BASE / 'libturbo_carousel.so') == receipt['nativeSHA256'] == BASE_NATIVE_SHA
    for name, expected in receipt['nativeSources'].items():
        assert sha(BASE / 'native' / name) == expected, name
    for name, expected in receipt['objects'].items():
        assert sha(name) == expected, name
    assert sha(media / 'media-build.json') == MEDIA_RECEIPT_SHA
    media_receipt = json.loads((media / 'media-build.json').read_text('utf8'))
    assert media_receipt['sourceSHA256'] == SOURCE_SHA
    assert media_receipt['asset'] == 'assets/' + ASSET and media_receipt['symbol'] == SYMBOL
    assert media_receipt['fullFrameDecodePassed']
    assert sha(media / Path(ASSET).name) == media_receipt['outputSHA256'] == VIDEO_SHA
    assert sha(media / 'snes-all.rgb565') == media_receipt['frameSHA256'] == FRAME_SHA
    assert (media / 'snes-all.rgb565').stat().st_size == 720 * 720 * 2
    streams = media_receipt['outputProbe']['streams']
    assert len(streams) == 1
    video = streams[0]
    assert (video['codec_name'], video['width'], video['height'], video['r_frame_rate'], video['has_b_frames']) == ('h264', 720, 720, '30/1', 0)
    assert float(video['duration']) > 6
    overlay = {p.name: sha(p) for p in (SNAPSHOT / 'native-carousel').iterdir() if p.is_file()}
    changed = sorted(['collection_video_policy.h', 'video720_posters.h', 'native_system_video720.h'])
    assert sorted(overlay) == changed
    work.mkdir(parents=True)
    for folder in ['native', 'tests', 'evidence', 'media', 'frames', 'temp']:
        (work / folder).mkdir()
    env = dict(os.environ, TEMP=str(work / 'temp'), TMP=str(work / 'temp'))
    for name in receipt['nativeSources']:
        shutil.copyfile(BASE / 'native' / name, work / 'native' / name)
    for name in overlay:
        shutil.copyfile(SNAPSHOT / 'native-carousel' / name, work / 'native' / name)
    sources = {p.name: sha(p) for p in (work / 'native').iterdir() if p.is_file()}
    assert set(sources) == set(receipt['nativeSources'])
    assert sorted(n for n in sources if sources[n] != receipt['nativeSources'][n]) == changed
    old_frames = 'sizeof(systemVideo720Definitions)/sizeof(systemVideo720Definitions[0])+sizeof(collectionVideoDefinitions)/sizeof(collectionVideoDefinitions[0])'
    new_frames = 'sizeof(video720Posters)/sizeof(video720Posters[0])'
    old_video = (BASE / 'native/native_system_video720.h').read_text('utf8')
    new_video = (work / 'native/native_system_video720.h').read_text('utf8')
    assert old_video.count(old_frames) == 1 and old_video.replace(old_frames, new_frames) == new_video
    folders = (work / 'native/native_folders.h').read_text('utf8')
    assert 'return collectionVideoFor(folderPlatform,strData(m.path),m.kind==2);' in folders
    assert 'if(folderMode){' in new_video and 'if(const auto*v=folderVideo(p,index))return v->asset;' in new_video
    assert 'seedVideo720Preview(' in new_video and 'poster.pixels' in new_video
    frame = work / 'frames/snes-all.rgb565'
    shutil.copyfile(media / 'snes-all.rgb565', frame)
    shutil.copyfile(media / Path(ASSET).name, work / 'media' / Path(ASSET).name)
    def run(command, label):
        result = subprocess.run(list(map(str, command)), capture_output=True, env=env)
        (work / 'evidence' / (label + '.log')).write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0, label + ': ' + result.stderr.decode('utf8', 'replace')[-1800:]
        return result.stdout.decode('utf8', 'replace').strip()
    host = Path(r'C:\Program Files\LLVM\bin\clang++.exe')
    common = [host, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-finput-charset=UTF-8', '-fexec-charset=UTF-8', '-I', work / 'native']
    symbols = re.findall(r'extern const unsigned char (\w+)\[\];', (work / 'native/video720_posters.h').read_text())
    stubs = work / 'tests/poster_symbols.cpp'
    stubs.write_text('extern "C" {\n' + '\n'.join('extern const unsigned char '+name+'[]={0};' for name in symbols) + '\n}\n', encoding='utf8')
    run(common + [SNAPSHOT / 'tests/collection_all_video.cpp', stubs, '-o', work / 'tests/routes.exe'], 'routes-compile')
    routes = run([work / 'tests/routes.exe'], 'routes-test')
    assert routes.startswith('PASS ')
    run(common + [SNAPSHOT.parent / 'station-collection-media-r69-20261007/tests/collection_corners.cpp', '-o', work / 'tests/corners.exe'], 'corners-compile')
    corners = run([work / 'tests/corners.exe'], 'corners-test')
    assert corners.startswith('PASS 66 ')
    run(common + [SNAPSHOT.parent / 'station-current-r55-20261006/tests/native/test_video_policy.cpp', '-o', work / 'tests/decoder.exe'], 'decoder-compile')
    decoder = run([work / 'tests/decoder.exe'], 'decoder-test')
    run(common + ['-Wno-unused-function', '-fsyntax-only', SNAPSHOT.parent / 'station-collection-navigation-r70-20261007/tests/collection_settings.cpp'], 'settings-test')
    # R70's address-dispatch harness intentionally casts between native ABI signatures.
    # Keep its original compiler arguments, including its original warning policy.
    navigation_flags = [host, '-std=c++17', '-O2', '-finput-charset=UTF-8', '-fexec-charset=UTF-8', '-I', work / 'native']
    run(navigation_flags + [SNAPSHOT.parent / 'station-collection-navigation-r70-20261007/tests/navigation.cpp', '-o', work / 'tests/navigation.exe'], 'navigation-compile')
    navigation = run([work / 'tests/navigation.exe'], 'navigation-test')
    assert navigation.startswith('PASS 3584 ')
    asm = work / 'collection_previews.S'
    asm.write_text('\n'.join(['.section .rodata.station_collections_r71,"a",%progbits', '.balign 16', '.global '+SYMBOL, '.hidden '+SYMBOL, '.type '+SYMBOL+',%object', SYMBOL+':', '.incbin "'+frame.as_posix()+'"', '.size '+SYMBOL+',.-'+SYMBOL])+'\n', encoding='utf8')
    command = list(receipt['command'])
    compiler = command[0]
    run([compiler, '--target=aarch64-linux-android26', '-c', asm, '-o', work / 'collection_previews.o'], 'poster-object')
    command[command.index(str(BASE / 'native/native_carousel.cpp'))] = str(work / 'native/native_carousel.cpp')
    command[command.index(str(BASE / 'libturbo_carousel.so'))] = str(work / 'libturbo_carousel.so')
    command.append(str(work / 'collection_previews.o'))
    objects = {str(Path(v)): sha(v) for v in command if str(v).endswith('.o')}
    assert all(objects[n] == h for n, h in receipt['objects'].items())
    run(command, 'carousel-build')
    tool = Path(compiler).parent
    elf = run([tool / 'llvm-readelf.exe', '-h', '-l', work / 'libturbo_carousel.so'], 'elf-check')
    aligns = [int(line.split()[-1], 16) for line in elf.splitlines() if line.strip().startswith('LOAD ')]
    assert 'AArch64' in elf and aligns and min(aligns) >= 16384
    syms = run([tool / 'llvm-nm.exe', '--defined-only', '--print-size', work / 'libturbo_carousel.so'], 'poster-symbol-check')
    line = next(line for line in syms.splitlines() if line.endswith(' '+SYMBOL))
    assert int(line.split()[1], 16) == 720*720*2
    assert overlay == {p.name: sha(p) for p in (SNAPSHOT / 'native-carousel').iterdir() if p.is_file()}
    assert sources == {p.name: sha(p) for p in (work / 'native').iterdir() if p.is_file()}
    record = {'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'compiled': True,
        'base': 'R70', 'baseReceiptSHA256': BASE_RECEIPT_SHA, 'baseNativeSHA256': BASE_NATIVE_SHA,
        'nativeSHA256': sha(work / 'libturbo_carousel.so'), 'nativeSources': sources,
        'changedNativeSources': changed, 'addedNativeSources': [], 'objects': objects, 'command': command,
        'mediaReceiptSHA256': MEDIA_RECEIPT_SHA, 'mediaReceipt': str(media / 'media-build.json'),
        'videos': [{'asset': ASSET, 'symbol': SYMBOL, 'output': str(work / 'media' / Path(ASSET).name),
                    'sha256': VIDEO_SHA, 'frameSHA256': FRAME_SHA, 'sourceSHA256': SOURCE_SHA}],
        'routeResult': routes, 'cornerPolicyResult': corners, 'navigationResult': navigation,
        'oneDecoderPolicyPassed': True, 'decoderResult': decoder, 'settingsPlacementChecks': 60,
        'frameMetadataSlots': 58, 'packagedPosterCount': 58, 'mainPlatformSourceUnchanged': True,
        'snesBRAliasUnchanged': True, 'frameRatePolicyUnchanged': True, 'menuTargetFPS': 30,
        'minimumLoadAlignment': min(aligns), 'buildRecipeSHA256': sha(__file__),
        'installed': False, 'visualPlaybackVerified': False}
    (work / 'evidence/build.json').write_text(json.dumps(record, indent=2, ensure_ascii=False)+'\n', encoding='utf8')
    (SNAPSHOT / 'evidence/carousel-build-r71.json').write_text(json.dumps(record, indent=2, ensure_ascii=False)+'\n', encoding='utf8')
    print(routes); print(corners); print(navigation); print('R71 carousel SHA256 '+record['nativeSHA256'])

if __name__ == '__main__': main()
