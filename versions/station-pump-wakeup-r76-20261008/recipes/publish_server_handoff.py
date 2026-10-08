"""Publish the authorized APP-to-SERVER handoff without touching the server checkout."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
APP=Path(__file__).resolve().parents[3]
SERVER=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
WORK=Path(r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008\publication')
BASE='ed9ca9fdcc16f3b9f86792d43ed01d5812a9f1d8'
APP_BRANCH='fix/station-pump-wakeup-r76-20261008'
BRANCH='docs/station-r76-pump-wakeup-20261008'
VERSION='versions/station-pump-wakeup-r76-20261008'
DOC='docs/station-android/ENTREGA-APP-R76-PUMP-WAKEUP-20261008.md'
PREFIX='docs/station-android/entrega-app-r76-20261008/'

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
assert git('rev-parse','origin/docs/station-r74-server-stability-return-20261007').decode().strip()==BASE,'Server response changed; read before publishing'
assert not git('ls-remote','--heads','origin','refs/heads/'+BRANCH).strip()
assert not git('for-each-ref','--format=%(refname)','refs/heads/'+BRANCH).strip()
commit=appgit('rev-parse','HEAD').decode().strip()
assert appgit('symbolic-ref','--short','HEAD').decode().strip()==APP_BRANCH
assert not appgit('status','--porcelain').strip(),'Publish committed sources only'
assert appgit('ls-remote','--heads','origin','refs/heads/'+APP_BRANCH).decode().split()[0]==commit
v=APP/VERSION;status=json.loads((v/'STATUS.json').read_text('utf8'))
assert status['compiled'] and status['signed'] and not status['stable']
url=f'https://github.com/luziellacerda/TurboElden/tree/{commit}/{VERSION}'
lead=f'''# R76 — APP → SERVIDOR: APP-01 integrada e compilada

Fonte exata: `{commit}`, branch `{APP_BRANCH}`.
[Fontes, receitas, evidências e estado]({url}). Retorno do servidor analisado: `{BASE}`.

Esta é a entrega do aplicativo ao operador. Não é retorno do servidor nem implantação Linux.
APK `{status['apkSHA256']}`; DEX35 `{status['roomsDexSHA256']}`.
Runtime `{status['runtimeSHA256']}` preservado, motores rs4 já ativos. Não cadastrar novos IDs nem reiniciar por esta entrega.
R75 visual incluída. Instalação individual: `{status['phones']}`; conferir os recibos, sem tratar testes sintéticos como gameplay físico.

Ações do operador na seção 6: receber correção APP-01, preservar registro, resolver a divergência TLS da candidata 6f27 e correlacionar coleta da próxima sessão. Os testes R76 usam código servidor 32ce/ab192bf, NÃO homologam a DLL 6f27.

---

'''
payload={DOC:(lead+(v/'HANDOFF-APP-R76-PARA-SERVIDOR-20261008.md').read_text('utf8')).encode()}
for name in ('STATUS.json','JAVA-OVERLAY-MANIFEST.json','SOURCE-FILES.json'):
    payload[PREFIX+name]=(v/name).read_bytes()
for p in sorted((v/'evidence').glob('*.json')):payload[PREFIX+'evidence/'+p.name]=p.read_bytes()
for p in sorted((v/'java').rglob('*.java')):payload[PREFIX+p.relative_to(v).as_posix()]=p.read_bytes()
note=f'''# R76 recebida do APP: sinal de envio corrigido — 08/10/2026

APP → SERVIDOR, ler `{DOC}`. Fonte `{commit}`; APK `{status['apkSHA256']}`. APP-01 agora integrada no DEX35, R75 visual preservada. Runtime/rs4 inalterados, registro de dez engines já ativo; não reiniciar por esta entrega. Seis testes TLS/WSS/TCP locais passaram com 30.817.216 bytes exatos contra 32ce/ab192bf; não homologam a candidata 6f27 nem gameplay Android. Conferir STATUS/recibos dos aparelhos. Manter SRV-01/02/03 candidatos até resolver TLS/gates. Preservar todos os produtos e dados.

## Histórico anterior

'''
for name in ('AGENTS.md','docs/station-android/AGENTS.md','docs/station-android/README.md'):
    payload[name]=note.encode()+git('show',f'{BASE}:{name}')
for name,content in payload.items():
    assert name.endswith(('.md','.json','.java')) and b'-----BEGIN PRIVATE KEY' not in content
    if name.endswith('.json'):json.loads(content)
files=[dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in sorted(payload.items())]
payload[PREFIX+'DELIVERY-FILES.json']=(json.dumps(dict(appCommit=commit,serverParent=BASE,files=files),indent=2)+'\n').encode()
WORK.mkdir(parents=True,exist_ok=True);index=WORK/'server-r76-docs.index';assert not index.exists()
env=dict(os.environ,GIT_INDEX_FILE=str(index))
author=appgit('show','-s','--format=%an%n%ae',commit).decode().splitlines()
env['GIT_AUTHOR_NAME']=env['GIT_COMMITTER_NAME']=author[0]
env['GIT_AUTHOR_EMAIL']=env['GIT_COMMITTER_EMAIL']=author[1]
git('read-tree',BASE,env=env)
for name,content in sorted(payload.items()):
    blob=git('hash-object','-w','--stdin',data=content).decode().strip()
    git('update-index','--add','--cacheinfo',f'100644,{blob},{name}',env=env)
tree=git('write-tree',env=env).decode().strip()
published=git('commit-tree',tree,'-p',BASE,data=b'docs(station): deliver R76 pump wakeup fix and exact transport qualification\n',env=env).decode().strip()
assert set(git('diff-tree','--no-commit-id','--name-only','-r',published).decode().splitlines())==set(payload)
for name,content in payload.items():assert git('show',f'{published}:{name}')==content
assert state()==before
git('update-ref','refs/heads/'+BRANCH,published,'0'*40)
git('push','origin',f'refs/heads/{BRANCH}:refs/heads/{BRANCH}')
assert git('ls-remote','--heads','origin','refs/heads/'+BRANCH).decode().split()[0]==published
assert state()==before
receipt=dict(serverBranch=BRANCH,serverCommit=published,serverParent=BASE,appCommit=commit,document=DOC,
 url=f'https://github.com/luziellacerda/Servidor-pix/blob/{published}/{DOC}',serverCheckoutAndIndexPreserved=True,
 linuxDeployed=False,filesPublished=len(payload),apkUploaded=False,privateMediaUploaded=False)
(WORK/'server-publication.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')
print(json.dumps(receipt,indent=2))
