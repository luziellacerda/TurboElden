"""Compile R79 baseline and the isolated R80 cover shader using frozen inputs."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess

ROOT=Path(__file__).resolve().parent.parent
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
CHANNEL=BACKUP/'test-up-to-4-players-r79'
WORK=Path(r'E:\ESTUDO APK\work\station-dreamcast-led-r80-20261008')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    config=json.loads((CHANNEL/'carousel-command.json').read_text('utf8'))
    inputs=json.loads((BACKUP/'BUILD-INPUTS-VERIFIED.json').read_text('utf8'))['files']
    changes=json.loads((ROOT/'evidence/source-changes.json').read_text('utf8'))
    for name,record in inputs.items():
        if not name.startswith('test-up-to-4-players-r79/carousel-inputs/'):continue
        assert sha(BACKUP/name)==record['sha256'],name
        local=WORK/name.split('/',1)[1]
        expected=changes['sourceChanges'].get(local.name,record['sha256'])
        assert sha(local)==expected,name
    assert sha(config['command'][0])==config['compilerSHA256']
    temp=WORK/'temp';temp.mkdir(exist_ok=True)
    env=dict(os.environ,TMP=str(temp),TEMP=str(temp))
    outputs={}
    for mode in ('baseline','dreamcast'):
        output=WORK/('libturbo_carousel-'+mode+'.so')
        command=list(config['command'])
        if mode=='dreamcast':
            command=[s.replace('{BACKUP}/test-up-to-4-players-r79/carousel-inputs',str(WORK/'carousel-inputs')) for s in command]
            assert any(str(WORK/'carousel-inputs')+'/d0/native_carousel.cpp'==s for s in command)
        command=[s.replace('{BACKUP}',str(BACKUP)).replace('{OUTPUT}',str(output)) for s in command]
        if mode!='baseline' or not output.exists() or sha(output)!=config['expectedSHA256']:
            r=subprocess.run(command,env=env,capture_output=True)
            (WORK/(mode+'-build.log')).write_bytes(r.stdout+r.stderr)
            assert r.returncode==0,mode+' build failed'
        outputs[mode]=sha(output)
    assert outputs['baseline']==config['expectedSHA256'],'Baseline must reproduce byte-for-byte'
    assert outputs['dreamcast']!=outputs['baseline']
    report={'version':'R80','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'compiled':True,'baselineReproduced':True,'hashes':outputs,
            'baseVersion':'R79','recipeSHA256':sha(__file__),'changes':changes['sourceChanges'],
            'installed':False,'androidVisualVerified':False}
    (ROOT/'evidence/build.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report))
if __name__=='__main__':main()
