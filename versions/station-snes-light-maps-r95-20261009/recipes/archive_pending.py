"""Refresh the complete backup while USB installation is pending; remove no APK."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
BACKUP=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
WORK=Path(r'E:\ESTUDO APK\work\station-snes-light-maps-r95-20261009')
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args):
 p=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),*args],cwd=REPO,capture_output=True)
 assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8','replace').strip()
active=read(REPO/'release-channels/ACTIVE.json');assert active==read(BACKUP/'release-channels/ACTIVE.json')
assert active['channels']['test-4p']['version']=='R95' and not read(ROOT/'INSTALLATION.json')['installed']
repro=read(ROOT/'evidence/backup-reproduction.json');assert repro['javaReproduced'] and repro['carouselReproduced']
for channel in active['channels'].values():assert sha(BACKUP/channel['directory']/channel['apk'])==channel['apkSHA256']
previous=BACKUP/'test-up-to-4-players-r94/TurboStations-Premium-R94-20261009.apk'
assert sha(previous)=='1aacf46a1e98fc21642363cab959ef40931517bb303706e35af485680bd2486e'
assert not git('status','--porcelain=v1'),'Commit source and receipts before archiving'
current=git('rev-parse','HEAD');assert current==git('rev-parse','refs/heads/fix/station-snes-light-maps-r95-20261009')
bundle=WORK/'r95-pending-installation.bundle';assert not bundle.exists()
git('bundle','create',str(bundle),'--all');git('bundle','verify',str(bundle))
target=BACKUP/'TurboElden-completo-20261008.bundle';temp=target.with_suffix('.bundle.new');assert not temp.exists()
shutil.copyfile(bundle,temp);assert sha(bundle)==sha(temp);os.replace(temp,target)
assert bundle.resolve().parent==WORK.resolve();bundle.unlink()
for p in (REPO/'release-channels').iterdir():
 if p.is_file():shutil.copyfile(p,BACKUP/'release-channels'/p.name)
maintenance=BACKUP/'maintenance/r95-pending-installation-20261009';maintenance.mkdir(exist_ok=True)
for n in ['README.md','STATUS.json','INSTALLATION.json','JAVA-SOURCE-MANIFEST.json']:shutil.copyfile(ROOT/n,maintenance/n)
shutil.copytree(ROOT/'evidence',maintenance/'evidence',dirs_exist_ok=True)
(BACKUP/'LEIA-ME.md').write_text('''# Backup completo — R76 e R95 pronta

As fontes e os dois canais selecionados estão em `release-channels/ACTIVE.json`.
R76 é a referência de dois jogadores. R95 é a candidata com o mapa GameCube corrigido e escolhas online integradas; ainda NÃO instalada, pois o Samsung saiu da USB antes da transferência. O Samsung permanece R94 e o Motorola R86.

O instalador R94 está temporariamente preservado até a R95 ser instalada e conferida. Nenhum APK foi apagado nesta etapa. O histórico completo atualizado está em `TurboElden-completo-20261008.bundle`. Os canais incluem fontes e entradas de reprodução; o backup R95 recompilou Java e carrossel idênticos.

Use os caminhos e hashes de ACTIVE, sem selecionar fontes por data. `BUILD-INPUTS-VERIFIED.json` confere as entradas atuais; `BACKUP-COMPLETE.json` indexa o conjunto e registra a aposentadoria pendente da R94. Recibos em `maintenance/r95-pending-installation-20261009`.
''','utf8')
for n,v in read(BACKUP/'BUILD-INPUTS-VERIFIED.json')['files'].items():assert sha(BACKUP/n)==v['sha256'],n
files={p.relative_to(BACKUP).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(BACKUP.rglob('*')) if p.is_file() and p.name!='BACKUP-COMPLETE.json'}
report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),complete=True,gitBundleVerified=True,appCommit=current,sourceCommit=active['channels']['test-4p']['sourceCommit'],installers=len(list(BACKUP.rglob('*.apk'))),selectedInstallers=2,pendingRetirement=[previous.relative_to(BACKUP).as_posix()],candidateInstalled=False,allCurrentAndArchivedGitRefsPreserved=True,javaAndCarouselReproduced=True,files=files)
(BACKUP/'BACKUP-COMPLETE.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps({k:v for k,v in report.items() if k!='files'}))
