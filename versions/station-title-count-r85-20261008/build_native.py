from pathlib import Path
import json,hashlib,subprocess,os,shutil
ROOT=Path(__file__).resolve().parent
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
BASE=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r84')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    original={p.relative_to(BASE/'carousel-inputs').as_posix():sha(p) for p in (BASE/'carousel-inputs').rglob('*') if p.is_file()}
    current={p.relative_to(WORK/'carousel-inputs').as_posix():sha(p) for p in (WORK/'carousel-inputs').rglob('*') if p.is_file()}
    assert set(original)==set(current)
    changed=sorted(n for n in current if current[n]!=original[n])
    assert changed==['d0/'+n for n in ['native_formation.h','native_game_actions.h','native_info.h','native_lottie_gear.h','native_profile_name.h','native_search_download.h','native_skin.h','native_space.h','station_bottom_action_layout.h','station_collection_settings_layout.h']]
    spec=json.loads((BASE/'carousel-command.json').read_text())
    assert sha(Path(spec['command'][0]))==spec['compilerSHA256']
    output=WORK/'native';output.mkdir();temp=output/'temp';temp.mkdir()
    cmd=[a.replace('{BACKUP}/test-up-to-4-players-r84',str(WORK)).replace('{OUTPUT}',str(output/'libturbo_carousel.so')) for a in spec['command']]
    proc=subprocess.run(cmd,env=dict(os.environ,TEMP=str(temp),TMP=str(temp)),capture_output=True)
    (output/'build.log').write_bytes(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr.decode('utf8','replace')[-4000:]
    spec['command']=[a.replace('test-up-to-4-players-r84','test-up-to-4-players-r85') for a in spec['command']]
    spec['expectedSHA256']=sha(output/'libturbo_carousel.so')
    (WORK/'carousel-command.json').write_text(json.dumps(spec,indent=2)+'\n','utf8')
    receipt=dict(compiled=True,sourceHashes=current,changedSources=changed,carouselSHA256=spec['expectedSHA256'],compilerSHA256=spec['compilerSHA256'])
    (ROOT/'evidence/native-build.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
    for n in current:
        if n in changed:
            dst=ROOT/'native'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(WORK/'carousel-inputs'/n,dst)
    print(json.dumps(dict(compiled=True,changed=changed,carouselSHA256=spec['expectedSHA256'])))
if __name__=='__main__':main()
