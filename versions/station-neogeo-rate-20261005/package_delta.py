"""Create an unsigned R11 delta; signing uses the existing original certificate workflow."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

BASE_SHA = '7c5096d58991a9724537036e18eb42555f290e2f6d673904524520da0d0146d5'


def sha(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def entry_sha(archive, name):
    with archive.open(name) as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def signature(name):
    return name.startswith('META-INF/') and name.upper().endswith(('.MF', '.RSA', '.DSA', '.EC', '.SF'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-apk', type=Path, required=True)
    parser.add_argument('--modules', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if sha(args.base_apk) != BASE_SHA:
        raise ValueError('R11 base differs; preserve and reconcile the new APK')
    replacements = {'lib/arm64-v8a/libstation_frontend.so': args.modules / 'libstation_frontend.so',
                    'lib/arm64-v8a/libturbo_carousel.so': args.modules / 'libturbo_carousel.so'}
    for module in replacements.values():
        if not module.is_file():
            raise ValueError('Both real native modules are required')
    report_path = args.output.with_suffix(args.output.suffix + '.json')
    if report_path.exists() or args.output.exists():
        raise ValueError('Use a new output file')
    with zipfile.ZipFile(args.base_apk) as before:
        if len(before.namelist()) != len(set(before.namelist())):
            raise ValueError('Duplicate base entries')
        if not set(replacements).issubset(before.namelist()):
            raise ValueError('Base modules missing')
        with args.output.open('xb') as output, zipfile.ZipFile(output, 'w', allowZip64=True) as after:
            for info in before.infolist():
                if signature(info.filename):
                    continue
                copied = copy.copy(info)
                copied.extra = b''
                with after.open(copied, 'w') as destination:
                    if info.filename in replacements:
                        with replacements[info.filename].open('rb') as source:
                            shutil.copyfileobj(source, destination, 1024 * 1024)
                    else:
                        with before.open(info) as source:
                            shutil.copyfileobj(source, destination, 1024 * 1024)
        with zipfile.ZipFile(args.output) as after:
            names = {name for name in before.namelist() if not signature(name)}
            if names != set(after.namelist()) or len(after.namelist()) != len(names):
                raise ValueError('Payload entries changed unexpectedly')
            changed = []
            for name in names:
                if before.getinfo(name).compress_type != after.getinfo(name).compress_type:
                    raise ValueError('Compression changed: ' + name)
                if entry_sha(before, name) != entry_sha(after, name):
                    if name not in replacements or entry_sha(after, name) != sha(replacements[name]):
                        raise ValueError('Unexpected payload change: ' + name)
                    changed.append(name)
            if set(changed) != set(replacements):
                raise ValueError('Expected both native modules to change')
            report = dict(baseSha256=BASE_SHA, unsigned=True, apkSigned=False, installed=False,
                          changed=sorted(changed), preservedEntries=len(names)-len(changed),
                          dexPreserved=True, compressionPreserved=True,
                          roomsDexSha256=entry_sha(after, 'classes35.dex'),
                          libraryDexSha256=entry_sha(after, 'classes28.dex'))
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
