"""Package only the two rebuilt EX+ engines and their public source changes.

Run only after the parent has finalized and validated native output. The pinned
input is the installed, control-isolated 8f494041 APK. No DEX/resources change.
"""
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import json
import os
import shutil
import struct
import subprocess
import zipfile

WORK = Path(r'E:\ESTUDO APK\work\station-hud-lzgames-20261003')
BASE = Path(r'E:\ESTUDO APK\work\station-mega-explus-20261003\TurboStations-SNES-Mega-CONTROLES-CORRIGIDOS-20261003.apk')
BASE_SHA = '8f494041ca4ae37fbd8becb50a1a7156ea2141e717af41452e5a1a923e0799b0'
UPSTREAM = Path(r'E:\ESTUDO APK\work\station-snes-explus-20261003\source\emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943')
COMMIT = '1c12fac5ce49badaadff2e2f210dcc30b89f4943'
OUT = WORK / 'TurboStations-SNES-Mega-HUD-LZGames-R2-20261003.apk'
REJECTED_V1 = WORK / 'TurboStations-SNES-Mega-HUD-LZGames-20261003.apk'
REJECTED_V1_SHA = '3d3afc380b109affe5615961b6930ffe7b88f1c96255e8cf39e6e688da66e0f7'
HERE = Path(__file__).resolve().parent
JDK = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')
BT = Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
SIGNER = '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825'
os.environ['TEMP'] = os.environ['TMP'] = str(WORK)

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def zsha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def is_signature(name):
    return name.startswith('META-INF/') and name.upper().endswith(('.MF','.RSA','.DSA','.EC','.SF'))

def native_needed(data):
    assert data[:7] == b'\x7fELF\x02\x01\x01', 'ELF64 LE required'
    assert struct.unpack_from('<H',data,18)[0] == 183, 'ARM64 required'
    off = struct.unpack_from('<Q',data,40)[0]
    stride,count = struct.unpack_from('<HH',data,58)
    sections = [struct.unpack_from('<IIQQQQIIQQ',data,off+i*stride) for i in range(count)]
    dynamic = next(s for s in sections if s[1] == 6)
    strings = sections[dynamic[6]]
    result = []
    for p in range(dynamic[4],dynamic[4]+dynamic[5],dynamic[9]):
        tag,value = struct.unpack_from('<qQ',data,p)
        if tag == 1:
            start = strings[4] + value
            result.append(data[start:data.index(b'\0',start)].decode('ascii'))
    return result

def run(args, log):
    result = subprocess.run([str(a) for a in args],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (WORK/log).write_text(result.stdout,encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{log} failed: {result.stdout[-5000:]}')
    return result.stdout

def discard_rejected_v1():
    """Delete one hash-pinned rejected APK after preserving its small evidence."""
    expected_root = WORK.resolve(strict=True)
    assert REJECTED_V1.parent.resolve(strict=True) == expected_root, 'Rejected file escaped build directory'
    assert not REJECTED_V1.is_symlink(), 'Refuse a symbolic link for rejected APK'
    if not REJECTED_V1.exists():
        return {'requested':True,'deleted':False,'reason':'Known rejected APK already absent'}
    resolved = REJECTED_V1.resolve(strict=True)
    assert resolved.parent == expected_root and resolved.name == 'TurboStations-SNES-Mega-HUD-LZGames-20261003.apk'
    assert resolved != BASE.resolve(strict=True) and resolved != OUT.resolve(), 'Refuse base or R2 output deletion'
    assert sha(resolved) == REJECTED_V1_SHA, 'Refuse deletion: file is not rejected V1 3d3afc38'
    evidence = WORK/'hud-build-result.json'
    previous = json.loads(evidence.read_text(encoding='utf-8'))
    assert previous['sha256'] == REJECTED_V1_SHA, 'V1 evidence does not identify rejected APK'
    assert Path(previous['apk']).resolve() == resolved, 'V1 evidence path mismatch'
    history = WORK/'history'/'hud-v1-3d3afc38'
    history.mkdir(parents=True,exist_ok=True)
    saved = []
    for name in ('hud-build-result.json','SOURCE-NOTICE.json','zipalign-build.log','sign-build.log','verify-signature.log','verify-alignment.log'):
        source,destination = WORK/name,history/name
        if not source.exists(): continue
        if destination.exists():
            assert sha(source) == sha(destination), ('Preserve existing history without overwriting',destination)
        else:
            shutil.copy2(source,destination)
        saved.append(name)
    record = {'requested':True,'deleted':True,'apk':str(resolved),'sha256':REJECTED_V1_SHA,
              'reason':'Rejected HUD V1 has overlapping text. Remove only this rebuildable candidate to provide R2 build space.',
              'evidence_preserved':saved,'evidence_history':str(history),
              'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    resolved.unlink()  # One known rejected candidate, verified by full SHA-256; no recursive deletion.
    (history/'rejected-apk-discard.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-finalized',action='store_true',help='Explicit parent approval that both native outputs are final')
    parser.add_argument('--discard-rejected-v1',action='store_true',help='Delete only the known SHA-256 pinned rejected V1 APK after retaining its evidence')
    args = parser.parse_args()
    if not args.native_finalized:
        raise SystemExit('Do not package until native outputs are finalized; pass --native-finalized after parent approval.')
    assert sha(BASE) == BASE_SHA, 'Base APK is not accepted controls-isolated 8f494041'
    assert not OUT.exists(), 'Final output already exists; preserve it and choose another reviewed revision explicitly'
    native = {
        'lib/arm64-v8a/libsnes9x_explus.so':WORK/'libsnes9x_explus.so',
        'lib/arm64-v8a/libmdemu_station.so':WORK/'libmdemu_station.so',
    }
    snes = native['lib/arm64-v8a/libsnes9x_explus.so'].read_bytes()
    mega = native['lib/arm64-v8a/libmdemu_station.so'].read_bytes()
    assert b'com/imagine' in snes and b'gpOverlay.png' in snes, 'SNES JNI/atlas mismatch'
    assert b'com/mdimagn' not in snes and b'mdOverlay.png' not in snes, 'SNES contains Mega JNI/atlas namespace'
    assert b'com/mdimagn' in mega and b'mdOverlay.png' in mega, 'Mega JNI/atlas relocation missing'
    assert b'com/imagine' not in mega and b'gpOverlay.png' not in mega, 'Mega still shares original JNI/atlas namespace'
    # Engine metadata strings in the pinned source and final linked binaries.
    # Catch a sibling build overwriting a shared libmain.so output before copy.
    assert b'Snes9x EX+' in snes and b'MD.emu' not in snes, 'SNES output is not the SNES engine'
    assert b'MD.emu' in mega and b'Snes9x EX+' not in mega, 'Mega output is not the Mega engine'
    assert hashlib.sha256(snes).digest() != hashlib.sha256(mega).digest(), 'Engines are unexpectedly identical'
    with zipfile.ZipFile(BASE) as base:
        old_names = [i.filename for i in base.infolist() if not is_signature(i.filename)]
        assert len(old_names) == len(set(old_names)), 'Duplicate input ZIP entries'
        for name,path in native.items():
            assert name in old_names
            old_deps = set(native_needed(base.read(name)))
            new_deps = set(native_needed(path.read_bytes()))
            assert new_deps <= old_deps, (name,'Unexpected shared dependency',new_deps-old_deps)
    sources = {}
    source_root = WORK/'source'
    for local in sorted(source_root.rglob('*')):
        if not local.is_file(): continue
        rel = local.relative_to(source_root)
        if any(p in ('build','.git') for p in rel.parts): continue
        original = UPSTREAM/rel
        if original.exists() and sha(original) == sha(local): continue
        assert local.suffix.lower() in ('.cc','.cpp','.c','.h','.hh','.hpp','.ccm','.cmake','.py','.json','.txt','.md','.sh') or local.name == 'CMakeLists.txt', ('Review nontext source addition',local)
        sources['assets/lzgames-hud/source/upstream/'+rel.as_posix()] = local
    for script in sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.c')):
        sources['assets/lzgames-hud/source/build/'+script.name] = script
    assert any('/EmuFramework/' in n for n in sources), 'No native HUD implementation source recorded'
    discarded = discard_rejected_v1() if args.discard_rejected_v1 else {'requested':False,'deleted':False}
    assert shutil.disk_usage(WORK).free > 2*BASE.stat().st_size + 160*1024*1024, 'Need space for two APK copies during alignment/signing'
    notice = {
        'feature':'LZ Games native pause HUD for Snes9x EX+ and MD.emu',
        'revision':'R2',
        'supersedes_rejected_apk_sha256':REJECTED_V1_SHA,
        'upstream_commit':COMMIT,'upstream_url':'https://github.com/Rakashazi/emu-ex-plus-alpha',
        'base_apk_sha256':BASE_SHA,
        'native_sha256':{n:sha(p) for n,p in native.items()},
        'modified_source_sha256':{n:sha(p) for n,p in sources.items()},
        'preserved':'Every DEX, NativeActivity storage isolation, frontend, media, auth/session, downloads and unrelated native engine',
        'licenses':'Original bundled license notices preserved; modified public source included below assets/lzgames-hud/source.',
        'mega_namespace':'MD JNI package/overlay source strings selected before the engine build; no executable binary hooks or coordinate navigation.',
        'validation_scope':'Build and package verification only. Device runtime results recorded separately.',
    }
    notice_path = WORK/'SOURCE-NOTICE-R2.json'
    notice_path.write_text(json.dumps(notice,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    additions = {**sources,'assets/lzgames-hud/SOURCE-NOTICE.json':notice_path}
    assert not (set(additions)&set(old_names)), 'New source notice would overwrite an existing asset'
    unsigned = WORK/'hud-r2-unsigned.apk'
    aligned = WORK/'hud-r2-aligned.apk'
    for p in (unsigned,aligned):
        assert not p.exists(), 'Preserve existing build output before starting another package'
    print('Packaging native HUD; all DEX/resources preserved',flush=True)
    with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(unsigned,'w',allowZip64=True) as b:
        b.comment = a.comment
        for info in a.infolist():
            name = info.filename
            if is_signature(name): continue
            output_info = copy.copy(info)
            if name in native:
                b.writestr(output_info,native[name].read_bytes())
            else:
                with a.open(info) as src,b.open(output_info,'w') as dst:
                    shutil.copyfileobj(src,dst,1024*1024)
        for name,path in additions.items():
            b.writestr(name,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
    run([BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned],'zipalign-build-r2.log')
    unsigned.unlink()  # Exact disposable file created by this invocation.
    run([JDK/'java.exe','-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true',
         '--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey',
         '--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned],'sign-build-r2.log')
    certs = run([JDK/'java.exe','-jar',BT/'lib/apksigner.jar','verify','--print-certs',OUT],'verify-signature-r2.log')
    assert SIGNER in certs, 'APK signer changed'
    run([BT/'zipalign.exe','-c','-P','16','4',OUT],'verify-alignment-r2.log')
    changed = []
    preserved = 0
    with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
        old = {n for n in a.namelist() if not is_signature(n)}
        new_list = [n for n in b.namelist() if not is_signature(n)]
        new = set(new_list)
        assert len(new_list) == len(new), 'Duplicate output ZIP entries'
        assert old <= new and new-old == set(additions), 'Unexpected added or removed ZIP payload'
        for name in sorted(old):
            before,after = zsha(a,name),zsha(b,name)
            if before != after:
                changed.append(name)
                assert name in native, ('Unexpected changed payload',name)
                assert after == sha(native[name]), ('Native payload mismatch',name)
            else:
                preserved += 1
        assert set(changed) == set(native), 'Expected exactly two rebuilt native libraries'
        for name,path in additions.items():
            assert zsha(b,name) == sha(path), ('Source asset mismatch',name)
    aligned.unlink()  # Exact disposable file created by this invocation.
    report = {**notice,'apk':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,
              'changed_entries':changed,'added_entries':sorted(additions),'removed_entries':[],
              'preserved_entries':preserved,'whole_zip_payload_equality_gate':True,
              'discard_rejected_v1':discarded,
              'installed':False,'device_runtime_verified':False,'promoted_to_stable':False}
    (WORK/'hud-build-result-r2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('apk','sha256','bytes','changed_entries','preserved_entries','installed')},indent=2))

if __name__ == '__main__':
    main()
