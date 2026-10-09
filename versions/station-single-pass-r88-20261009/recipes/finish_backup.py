"""Keep the two authorized installers; refresh the complete local Git backup."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parent.parent;REPO=ROOT.parents[1]
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
WORK=Path(r'E:\ESTUDO APK\work\station-single-pass-r88-20261009')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text('utf8'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n','utf8')
def git(*args):
    p=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),*args],cwd=REPO,capture_output=True)
    assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8','replace').strip()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--bundle',action='store_true');args=parser.parse_args()
    active=read(REPO/'release-channels/ACTIVE.json');assert active==read(BACKUP/'release-channels/ACTIVE.json')
    assert [active['channels'][k]['version'] for k in ['stable-2p','test-4p']]==['R76','R88']
    expected=[]
    for c in active['channels'].values():
        p=BACKUP/c['directory']/c['apk'];assert sha(p)==c['apkSHA256'];expected.append(p)
    result=read(ROOT/'evidence/backup-reproduction.json');assert result['javaReproduced'] and result['carouselReproduced']
    install=read(ROOT/'INSTALLATION.json');assert install['apkSHA256']==active['channels']['test-4p']['apkSHA256'] and install['installed']
    assert read(ROOT/'evidence/led-preservation.json')['preservedExactlyFromR87']
    rejected='33b0563ef1f679f5632702706a5b77a669a7646d5b00b84cd82199e12aab345d'
    candidates=[
        (BACKUP/'test-up-to-4-players-r87/TurboStations-Premium-R87-20261008.apk','a1ed3cd980b8810dab70f417cc97f9ac397b5071b7e21d74ad1b315804abc5f0'),
        (BACKUP/'test-up-to-4-players-r88.withdrawn-no-led/TurboStations-Premium-R88-20261009.apk',rejected),
        (WORK/'withdrawn-no-led/package/TurboStations-Premium-R88-20261009.apk',rejected),
        (WORK/'package/TurboStations-Premium-R88-20261009.apk',active['channels']['test-4p']['apkSHA256'])]
    if not args.bundle:
        removed=[]
        for p,h in candidates:
            if not p.exists():continue
            resolved=p.resolve();assert resolved.is_relative_to(BACKUP.resolve()) or resolved.is_relative_to(WORK.resolve())
            assert p not in expected and p.suffix=='.apk' and sha(p)==h
            size=p.stat().st_size;p.unlink();removed.append(dict(path=str(p),sha256=h,bytes=size))
        assert set(BACKUP.rglob('*.apk'))==set(expected)
        write(ROOT/'evidence/installer-cleanup.json',dict(verifiedBeforeRemoval=True,removed=removed,retainedInstallers=2,sourceHistoryPreserved=True))
        print(json.dumps({'removedCopies':len(removed),'bytesFreed':sum(x['bytes'] for x in removed)}));return
    assert set(BACKUP.rglob('*.apk'))==set(expected)
    assert not git('status','--porcelain=v1'),'Commit all final receipts first'
    current=git('rev-parse','HEAD');assert git('rev-parse','refs/heads/fix/station-single-pass-r88-20261009')==current
    output=WORK/'final-archive';output.mkdir(exist_ok=True);bundle=output/'TurboElden-completo-r88.bundle';assert not bundle.exists()
    git('bundle','create',str(bundle),'--all');git('bundle','verify',str(bundle))
    target=BACKUP/'TurboElden-completo-20261008.bundle';temporary=target.with_suffix('.bundle.new');assert not temporary.exists()
    shutil.copyfile(bundle,temporary);assert sha(bundle)==sha(temporary);os.replace(temporary,target)
    assert bundle.resolve().parent==output.resolve();bundle.unlink()
    for p in (REPO/'release-channels').iterdir():
        if p.is_file():shutil.copyfile(p,BACKUP/'release-channels'/p.name)
    maintenance=BACKUP/'maintenance/r88-final-delivery-20261009';maintenance.mkdir(exist_ok=True)
    for n in ['README.md','STATUS.json','INSTALLATION.json','JAVA-SOURCE-MANIFEST.json']:
        shutil.copyfile(ROOT/n,maintenance/n)
    shutil.copytree(ROOT/'evidence',maintenance/'evidence',dirs_exist_ok=True)
    (BACKUP/'LEIA-ME.md').write_text('''# Backup completo — R76 e R88 corrigida

Os dois instaladores selecionados estão em `release-channels/ACTIVE.json`.

- R76: referência de dois jogadores escolhida pelo mantenedor.
- R88: menu30fps; vídeo e estrelas uma vez por seleção; LEDs originais da R87 preservados. Instalada no Samsung. Motorola permaneceR86. Não altera a qualificação online nem os emuladores.

Cada canal inclui fontes completas, entradas e receita de reprodução. O histórico completo está em `TurboElden-completo-20261008.bundle`. Use `release-channels/rebuild_verified.py` para recompilar um canal explícito. Ferramentas SDK/JDK/NDK e chave protegida continuam nos caminhos existentes.

A preliminar33b0563e semLED foi rejeitada e retirada. O hash atual correto está em ACTIVE; não escolher versões pela data. Recibos em `maintenance/r88-final-delivery-20261009`. Diretórios históricos de fonte e efeitos são arquivos; não selecioná-los como versão atual.

`BUILD-INPUTS-VERIFIED.json` valida entradas atuais; `BACKUP-COMPLETE.json` indexa o conjunto. Licenças, jogos e saves não foram removidos.
''','utf8')
    for n,v in read(BACKUP/'BUILD-INPUTS-VERIFIED.json')['files'].items():assert sha(BACKUP/n)==v['sha256'],n
    files={p.relative_to(BACKUP).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(BACKUP.rglob('*')) if p.is_file() and p.name!='BACKUP-COMPLETE.json'}
    write(BACKUP/'BACKUP-COMPLETE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),complete=True,gitBundleVerified=True,appCommit=current,sourceCommit=active['channels']['test-4p']['sourceCommit'],installers=2,allCurrentAndArchivedGitRefsPreserved=True,javaAndCarouselReproducedForBothChannels=True,r88Reproduction='versions/'+ROOT.name+'/evidence/backup-reproduction.json',files=files))
    print(json.dumps({'complete':True,'appCommit':current,'installers':2,'filesVerified':len(files)}))
if __name__=='__main__':main()
