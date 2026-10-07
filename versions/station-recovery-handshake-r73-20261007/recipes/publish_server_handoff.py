"""Publish the authorized R73 handshake recovery handoff without changing the server checkout."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
APP=Path(__file__).resolve().parents[3]
SERVER=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
WORK=Path(r'E:\ESTUDO APK\work\station-recovery-handshake-r73-20261007-build\publication')
BASE='c1e44a1225a101478ceb29f4e624885331872c0d'
BRANCH='docs/station-r73-handshake-flush-20261007'
VERSION='versions/station-recovery-handshake-r73-20261007'
DOC='docs/station-android/ENTREGA-APP-R73-HANDSHAKE-PARA-SERVIDOR-20261007.md'
PREFIX='docs/station-android/entrega-app-r73-20261007/'
def git(*args,data=None,env=None):
    r=subprocess.run(['git','-c','safe.directory='+SERVER.as_posix(),'-C',str(SERVER),*args],input=data,capture_output=True,env=env)
    if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace'))
    return r.stdout
def appgit(*args):return subprocess.check_output(['git','-c','safe.directory='+APP.as_posix(),'-C',str(APP),*args])
def state():
    index=Path(git('rev-parse','--path-format=absolute','--git-path','index').decode().strip())
    return [git('rev-parse','HEAD'),git('symbolic-ref','HEAD'),git('status','--porcelain=v1','-z'),hashlib.sha256(index.read_bytes()).hexdigest()]
assert '--publish' in sys.argv
before=state()
git('fetch','origin','+refs/heads/*:refs/remotes/origin/*')
assert git('rev-parse','origin/fix/station-r71-server-recovery-20261007').decode().strip()==BASE,'New return: inspect first'
assert not git('ls-remote','--heads','origin','refs/heads/'+BRANCH).strip()
assert not git('for-each-ref','--format=%(refname)','refs/heads/'+BRANCH).strip()
commit=appgit('rev-parse','HEAD').decode().strip()
assert appgit('symbolic-ref','--short','HEAD').decode().strip()=='fix/station-r73-recovery-handshake-20261007'
assert not appgit('status','--porcelain').strip()
assert appgit('ls-remote','--heads','origin','refs/heads/fix/station-r73-recovery-handshake-20261007').decode().split()[0]==commit
v=APP/VERSION
url=f'https://github.com/luziellacerda/TurboElden/tree/{commit}/{VERSION}'
lead=f'''# R73 — APP → SERVIDOR: cadastrar motor corrigido antes da instalação

Código completo do app: `{commit}`, branch `fix/station-r73-recovery-handshake-20261007`.
[Fontes, receitas, testes e estado]({url}).
Base do servidor examinada: `{BASE}`. Esta é uma entrega do cliente e um pedido ao operador, não um retorno do servidor nem uma implantação já executada.

**Ação: cadastrar as duas novas identidades exatas de SNES/Mega e runtime R73, preservando as seis existentes.** A leitura atual ocorre uma vez na inicialização do serviço; a ativação exige procedimento controlado pelo operador e coordenação das partidas. Não apagar/verificar menos os hashes.

Os dois aparelhos permanecem R72. R73 já está empacotada, mas aguarda cadastro e teste físico. APK b23ff3d1e319ee050e6eb867e2643a5f66661da481dd2e3a4e50089d1604f077; runtime9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2.

As evidências copiadas são do commit acima. Caminhos `evidence/`, `tests/` e `native/` abaixo correspondem a `entrega-app-r73-20261007/` nesta entrega; fontes completas/receitas estão no link do app. Não substituir Activities por snapshots antigos. A confirmação física de gameplay e recuperação continua pendente.

---

'''
payload={DOC:(lead+(v/'HANDOFF-APP-R73-PARA-SERVIDOR-20261007.md').read_text('utf8')).encode('utf8')}
for name in ['STATUS.json','JAVA-OVERLAY-MANIFEST.json','SOURCE-FILES.json']:
    payload[PREFIX+name]=(v/name).read_bytes()
for p in sorted((v/'evidence').glob('*.json')):payload[PREFIX+'evidence/'+p.name]=p.read_bytes()
for name in ['tests/NATIVE-FINDINGS.md','tests/transport_audit.md','tests/recovery-flush-probe.json','native/recovery-handshake-r73.patch']:
    payload[PREFIX+name]=(v/name).read_bytes()
note=f'''# APP R73 entregue — cadastro do motor de handshake — 07/10/2026

APP → SERVIDOR; ler `{DOC}`. App `{commit}`; APK b23ff3d1e319ee050e6eb867e2643a5f66661da481dd2e3a4e50089d1604f077; runtime9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2. Dois celulares permanecem R72, ambos JNI/listening/STATE1/PONGs e telas pretas. Defeito nativo MODE retido reproduzido; pump R73 envia não bloqueante sob pausa, sem avançar frames. 1206 checks Java,22 nativos,39 guardas passaram; não provam gameplay. Adicionar DOIS IDs rs3 exatos preservando seis anteriores; ativação controlada pois registro é lido na inicialização. Preservar partidas até saída humana/coordenada; não deploy automático. Dialog de espera e diagnóstico limitados. Não restaurar Activities antigas nem remover validações. Fontes/manifestos/recibos completos no app. Responder com produção efetiva e evidências, não somente JSON no Git.

## Histórico anterior

'''
for p in ['AGENTS.md','docs/station-android/AGENTS.md','docs/station-android/README.md']:
    payload[p]=note.encode('utf8')+git('show',f'{BASE}:{p}')
for p,b in payload.items():
    assert p.endswith(('.md','.json','.patch')) and b'-----BEGIN PRIVATE KEY' not in b
    if p.endswith('.json'):json.loads(b)
manifest=[dict(path=p,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for p,b in sorted(payload.items())]
payload[PREFIX+'DELIVERY-FILES.json']=(json.dumps(dict(appCommit=commit,serverParent=BASE,files=manifest),indent=2)+'\n').encode()
WORK.mkdir(parents=True,exist_ok=True)
idx=WORK/'server-r73-docs.index'
assert not idx.exists()
env=os.environ.copy();env['GIT_INDEX_FILE']=str(idx)
author=appgit('show','-s','--format=%an%n%ae',commit).decode().splitlines()
env['GIT_AUTHOR_NAME']=env['GIT_COMMITTER_NAME']=author[0]
env['GIT_AUTHOR_EMAIL']=env['GIT_COMMITTER_EMAIL']=author[1]
git('read-tree',BASE,env=env)
for p,b in sorted(payload.items()):
    blob=git('hash-object','-w','--stdin',data=b).decode().strip()
    git('update-index','--add','--cacheinfo',f'100644,{blob},{p}',env=env)
tree=git('write-tree',env=env).decode().strip()
server_commit=git('commit-tree',tree,'-p',BASE,data=b'docs(station): deliver R73 native handshake flush and exact runtime registry request\n',env=env).decode().strip()
assert set(git('diff-tree','--no-commit-id','--name-only','-r',server_commit).decode().splitlines())==set(payload)
for p,b in payload.items():assert git('show',f'{server_commit}:{p}')==b
assert state()==before
git('update-ref','refs/heads/'+BRANCH,server_commit,'0'*40)
git('push','origin',f'refs/heads/{BRANCH}:refs/heads/{BRANCH}')
assert git('ls-remote','--heads','origin','refs/heads/'+BRANCH).decode().split()[0]==server_commit
assert state()==before
receipt=dict(serverBranch=BRANCH,serverCommit=server_commit,serverParent=BASE,appCommit=commit,document=DOC,
    url=f'https://github.com/luziellacerda/Servidor-pix/blob/{server_commit}/{DOC}',serverCheckoutAndIndexPreserved=True,
    linuxDeployed=False,filesPublished=len(payload),apkUploaded=False,privateMediaUploaded=False)
(WORK/'server-publication.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
print(json.dumps(receipt,indent=2))
