"""Rebuild the verified R74 native baseline, then apply only the R77 overlay."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, shutil, struct, subprocess

PIN = '69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576'
BASE = Path(r'E:\R74fixed')
EXPECTED = '804b2acfea4c6d615bf40dba30e1777015098bf7375d0745db8d117555eb2516'
ROOT = Path(__file__).resolve().parent
WORK = Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008\native')
ALIAS = Path(r'E:\R77native')
NDK = Path(r'E:\TurboEdenEngine\android-ndk-r28c')
# Reviewed first R77 candidate, superseded only to claim a slot after buffer
# allocation. This permits updating that exact local candidate, not arbitrary
# dirty native source or changes to the R74 baseline.
SUPERSEDED = {'network/netplay/netplay_frontend.c':
              'a694e59ca83c58ff485dbfe6355063aea44c7992cbf26993947dfe568133c651'}

def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def require(ok, msg):
    if not ok: raise ValueError(msg)

def compare_baseline(path):
    original=(BASE/'libstation_retroarch.so').read_bytes()
    rebuilt=Path(path).read_bytes()
    require(len(original)==len(rebuilt), 'Baseline ELF size changed')
    def sections(data):
        require(data[:6] == b'\x7fELF\x02\x01', 'Expected ELF64 little-endian')
        offset=struct.unpack_from('<Q',data,40)[0]
        size,count,string_index=struct.unpack_from('<HHH',data,58)
        require(size==64 and 0<string_index<count, 'Invalid ELF section table')
        heads=[struct.unpack_from('<IIQQQQIIQQ',data,offset+i*size) for i in range(count)]
        strings=heads[string_index]
        names=data[strings[4]:strings[4]+strings[5]]
        return {names[h[0]:].split(b'\0',1)[0].decode():h for h in heads}
    old_sections=sections(original);new_sections=sections(rebuilt)
    require(old_sections==new_sections, 'Baseline ELF section layout changed')
    note=old_sections['.note.gnu.build-id'];start=note[4];length=note[5]
    require(length==36 and original[start:start+16]==struct.pack('<III',4,20,3)+b'GNU\0',
            'Unexpected build-id note layout')
    require(original[:start+16]==rebuilt[:start+16] and original[start+36:]==rebuilt[start+36:],
            'Baseline differs outside the 20-byte GNU build-id descriptor')
    result={'originalSHA256':hashlib.sha256(original).hexdigest(),
            'rebuiltSHA256':hashlib.sha256(rebuilt).hexdigest(),
            'identicalWholeFile':original==rebuilt,
            'identicalOutsideBuildId':True,
            'differentByteCount':sum(a!=b for a,b in zip(original,rebuilt)),
            'excludedRegion':{'section':'.note.gnu.build-id','descriptorOffset':start+16,'length':20},
            'originalBuildId':original[start+16:start+36].hex(),
            'rebuiltBuildId':rebuilt[start+16:start+36].hex(),
            'sectionSHA256':{n:hashlib.sha256(original[h[4]:h[4]+h[5]]).hexdigest()
                            for n,h in old_sections.items() if h[1]!=8 and n!='.note.gnu.build-id'},
            'qualification':'Whole-file identity is not claimed when the build-id differs. All other bytes, including ELF code/data/layout/relocations, must match.'}
    return result

def main():
    recipe_sha=sha(__file__)
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['baseline', 'candidate'])
    p.add_argument('--jobs', type=int, default=4)
    p.add_argument('--rebuild', action='store_true')
    a = p.parse_args()
    require(1 <= a.jobs <= 6, 'Bounded jobs required')
    require(sha(BASE/'libstation_retroarch.so') == EXPECTED, 'R74 runtime mismatch')
    require(ALIAS.resolve() == WORK.resolve(), 'E:\\R77native must be a junction to the owned native directory')
    source = ALIAS/('RetroArch-'+PIN)
    if not source.exists():
        require(a.mode == 'baseline', 'Build baseline first')
        receipt = json.loads((BASE/'result.json').read_text('utf8'))
        original = BASE/('RetroArch-'+PIN)
        require(all(sha(original/n) == v['afterSHA256'] for n,v in receipt['sourceDelta'].items()), 'R74 source changed')
        shutil.copytree(original, source)
        files = {str(p.relative_to(source)).replace('\\','/'):sha(p) for p in source.rglob('*') if p.is_file()}
        (WORK/'baseline-source-manifest.json').write_text(json.dumps(files, indent=2)+'\n', 'utf8')
    files = json.loads((WORK/'baseline-source-manifest.json').read_text('utf8'))
    if a.mode == 'baseline':
        require(all(sha(source/n) == v for n,v in files.items()), 'Baseline source changed')
    else:
        require((WORK/'baseline/result.json').is_file(), 'Missing baseline compilation')
        baseline=json.loads((WORK/'baseline/result.json').read_text('utf8'))
        require(sha(WORK/'baseline/libstation_retroarch.so') == baseline['runtimeSHA256'],
                'Baseline receipt does not match the rebuilt runtime')
        comparison=compare_baseline(WORK/'baseline/libstation_retroarch.so')
        (WORK/'baseline/comparison.json').write_text(json.dumps(comparison,indent=2)+'\n','utf8')
        overlay_bytes=(ROOT/'OVERLAY-MANIFEST.json').read_bytes()
        overlay_sha=hashlib.sha256(overlay_bytes).hexdigest()
        overlay = json.loads(overlay_bytes)
        require(overlay['baseRuntimeSHA256'] == EXPECTED, 'Overlay base mismatch')
        for n,v in overlay['files'].items():
            require(sha(ROOT/'source'/n) == v['afterSHA256'], 'Overlay hash mismatch '+n)
            require((v['beforeSHA256'] is None and n not in files) or files.get(n) == v['beforeSHA256'], 'Overlay before mismatch '+n)
            if v['beforeSHA256'] is None and (source/n).exists():
                require(sha(source/n)==v['afterSHA256'], 'Unreviewed added source change '+n)
        for n,v in files.items():
            require(sha(source/n) in {v, overlay['files'].get(n,{}).get('afterSHA256'),SUPERSEDED.get(n)}, 'Unreviewed source change '+n)
        for n in overlay['files']:
            dest=source/n; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/'source'/n,dest)
    out = ALIAS/a.mode
    out.mkdir(parents=True, exist_ok=True)
    jni=source/'pkg/android/phoenix-common/jni'
    require('Pkg.Revision = 28.2.13676358' in (NDK/'source.properties').read_text(), 'Wrong NDK')
    cmd=[str(NDK/'ndk-build.cmd'), 'NDK_PROJECT_PATH='+str(source/'pkg/android/phoenix-common'),
         'APP_BUILD_SCRIPT='+str(jni/'Android.mk'), 'NDK_APPLICATION_MK='+str(jni/'Application.mk'),
         'NDK_OUT='+str(out/'obj'), 'NDK_LIBS_OUT='+str(out/'lib'), 'APP_ABI=arm64-v8a',
         'TARGET_ABIS=arm64-v8a', 'APP_PLATFORM=android-26', 'NDK_NO_GL_HEADER_VER=26',
         'APP_CPPFLAGS=-std=c++17', 'APP_SUPPORT_FLEXIBLE_PAGE_SIZES=true',
         'HAVE_VULKAN=0', 'HAVE_CHEEVOS=0', 'HAVE_SAF=0', 'GIT_VERSION=', '-j'+str(a.jobs)]
    if a.rebuild:cmd.append('-B')
    print('Building '+a.mode, flush=True)
    # __DATE__ is included in RetroArch's string pool; pin the historical UTC
    # build date for reproduction, without changing the clock or source files.
    source_date_epoch='1791331200' if a.mode=='baseline' else '1791417600'
    env=dict(os.environ,TEMP=str(out),TMP=str(out),PYTHONDONTWRITEBYTECODE='1',SOURCE_DATE_EPOCH=source_date_epoch)
    with (out/'build.log').open('w',encoding='utf8') as f:
        r=subprocess.run(cmd,cwd=jni,env=env,stdout=f,stderr=subprocess.STDOUT)
    require(r.returncode == 0, 'Build failed; inspect '+str(out/'build.log'))
    final=out/'libstation_retroarch.so'
    shutil.copyfile(out/'lib/arm64-v8a/libretroarch-activity.so',final)
    tool=NDK/'toolchains/llvm/prebuilt/windows-x86_64/bin'
    headers=subprocess.check_output([str(tool/'llvm-readelf.exe'),'-h','-l',str(final)],text=True)
    symbols=subprocess.check_output([str(tool/'llvm-nm.exe'),'--defined-only','--dynamic',str(final)],text=True)
    alignment=[int(l.split()[-1],16) for l in headers.splitlines() if l.strip().startswith('LOAD ')]
    require('AArch64' in headers and min(alignment)>=16384,'ELF ABI/alignment')
    methods=['stationRecoveryControl','stationRecoveryStatus','stationRecoveryStalled','stationRequestQuit']
    if a.mode=='candidate':methods+=['stationMultiplayerConfigure','stationMultiplayerBind','stationMultiplayerUnbind']
    require(all('Java_org_emulationstation_frontend_netplay_StationRetroActivity_'+n in symbols for n in methods),'JNI export missing')
    report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':a.mode,'compiled':True,
       'baseRuntimeSHA256':EXPECTED,'runtimeSHA256':sha(final),'runtimeBytes':final.stat().st_size,
       'runtimePath':str(final),'matchesR74':sha(final)==EXPECTED,'upstreamCommit':PIN,
       'minimumLoadAlignment':min(alignment),'jniMethods':methods,'command':cmd,'recipeSHA256':recipe_sha,
       'sourceManifestSHA256':sha(WORK/'baseline-source-manifest.json'),'buildLogSHA256':sha(out/'build.log'),
       'sourceDateEpoch':source_date_epoch,
       'androidExecuted':False,'installed':False,'serverDeployed':False}
    if a.mode=='candidate':
        require(all(sha(source/n)==v['afterSHA256'] for n,v in overlay['files'].items()), 'Compiled overlay changed during build')
        require(sha(ROOT/'OVERLAY-MANIFEST.json')==overlay_sha, 'Snapshot manifest changed during build; rebuild required')
        report['overlayManifestSHA256']=overlay_sha
        report['overlaySourceHashes']={n:v['afterSHA256'] for n,v in overlay['files'].items()}
    else:
        comparison=compare_baseline(final)
        (out/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n','utf8')
        report['matchesR74OutsideBuildId']=comparison['identicalOutsideBuildId']
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    (out/'elf-headers.txt').write_text(headers,'utf8'); (out/'elf-exports.txt').write_text(symbols,'utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
