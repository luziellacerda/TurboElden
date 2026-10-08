"""Refresh the one complete backup after publication; exact channels are required."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parent.parent
APP=ROOT.parents[1]
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args):
    r=subprocess.run(['git','-c','safe.directory='+APP.as_posix(),*args],cwd=APP,capture_output=True)
    if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace'))
    return r.stdout
def main():
    active=json.loads((APP/'release-channels/ACTIVE.json').read_text('utf8'))
    assert [active['channels'][n]['version'] for n in ['stable-2p','test-4p']]==['R76','R85']
    expected=[]
    for channel in active['channels'].values():
        p=BACKUP/channel['directory']/channel['apk'];assert sha(p)==channel['apkSHA256'];expected.append(p)
    assert set(BACKUP.rglob('*.apk'))==set(expected)
    current=git('rev-parse','HEAD').decode().strip()
    assert git('rev-parse','refs/heads/fix/station-title-count-r85-20261008').decode().strip()==current
    assert not git('status','--porcelain=v1').strip(),'Commit receipts before final backup'
    bundle=WORK/'TurboElden-completo-r85.bundle';assert not bundle.exists()
    git('bundle','create',str(bundle),'--all');git('bundle','verify',str(bundle))
    refs={row.split(' ',1)[1]:row.split(' ',1)[0] for row in git('bundle','list-heads',str(bundle)).decode().splitlines()}
    assert refs['refs/heads/fix/station-title-count-r85-20261008']==current
    name='TurboElden-completo-20261008.bundle';temporary=BACKUP/(name+'.new')
    assert not temporary.exists();shutil.copyfile(bundle,temporary);assert sha(bundle)==sha(temporary)
    os.replace(temporary,BACKUP/name)
    assert bundle.resolve().parent==WORK.resolve() and bundle.name=='TurboElden-completo-r85.bundle';bundle.unlink()
    for file in (APP/'release-channels').iterdir():
        if file.is_file():shutil.copyfile(file,BACKUP/'release-channels'/file.name)
    maintenance=BACKUP/'maintenance/r85-final-delivery-20261008';maintenance.mkdir(exist_ok=True)
    for rel in ['README.md','STATUS.json','INSTALLATION.json','JAVA-SOURCE-MANIFEST.json','recipes/finalize_backup.py']:
        target=maintenance/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,target)
    for folder in ['evidence']:
        shutil.copytree(ROOT/folder,maintenance/folder,dirs_exist_ok=True)
    (BACKUP/'LEIA-ME.md').write_text('''# Backup único TurboStations — R76 e R85

Somente dois instaladores, selecionados em `release-channels/ACTIVE.json`:

- `stable-2-players-r76/TurboStations-Premium-R76-20261008.apk`: referência de dois jogadores escolhida pelo mantenedor.
- `test-up-to-4-players-r85/TurboStations-Premium-R85-20261008.apk`: informações descritivas de jogadores; servidor v3 e perfis reais ainda precisam de ativação e qualificação.

Cada canal contém fontes Java completas, manifestos, entradas do carrossel, DEX/biblioteca e receita de reprodução. `native-sources/` conserva fontes dos motores e demais integrações. `TurboElden-completo-20261008.bundle` contém o histórico Git e todas as referências locais. Ferramentas JDK/SDK/NDK e a chave original protegida continuam em seus caminhos do PC.

Use `release-channels/rebuild_verified.py` para verificar/reproduzir um canal explícito. As receitas históricas de montagem registram versões passadas; os APKs retirados não são novas bases. A R85 foi recompilada diretamente deste backup com DEX e carrossel idênticos a partir do backup consolidado R85.

Recibos da R85 em `maintenance/r85-final-delivery-20261008/`. Fonte completa e histórico estão no bundle e no Git. Nenhum telefone ou serviço foi alterado na consolidação.

O efeito Dreamcast está guardado em `effects/Dreamcast-LED-estilo-TURBORAMA-R80.zip`, sem integração automática; as capas atuais têm outra moldura. `release-channels/PENDING-VISUAL.json` mantém essa decisão.

`BUILD-INPUTS-VERIFIED.json` confere as entradas; `BACKUP-COMPLETE.json` é o índice integral atualizado. Não apagar licenças, jogos, saves, BIOS, ferramentas, chave ou fontes necessárias como se fossem temporários.
''','utf8')
    inputs=json.loads((BACKUP/'BUILD-INPUTS-VERIFIED.json').read_text('utf8'))['files']
    for name,entry in inputs.items():assert sha(BACKUP/name)==entry['sha256'],name
    files={}
    for file in sorted(BACKUP.rglob('*')):
        if file.is_file() and file.name!='BACKUP-COMPLETE.json':files[file.relative_to(BACKUP).as_posix()]={'bytes':file.stat().st_size,'sha256':sha(file)}
    record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),complete=True,gitBundleVerified=True,appCommit=current,sourceCommit=active['channels']['test-4p']['sourceCommit'],installers=2,allCurrentAndArchivedGitRefsPreserved=True,javaAndCarouselReproducedForBothChannels=True,r85Reproduction='versions/station-title-count-r85-20261008/evidence/backup-reproduction.json',serverDeliveryCommit='2cd3571919f54126f2bfe9576864a8d8329b9db3',files=files)
    (BACKUP/'BACKUP-COMPLETE.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
    print(json.dumps({'complete':True,'appCommit':current,'installers':2,'filesVerified':len(files),'gitBundleSHA256':files['TurboElden-completo-20261008.bundle']['sha256']}))
if __name__=='__main__':main()
