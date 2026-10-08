"""Publish the authorized APP-to-SERVER handoff without touching the server checkout."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
APP=Path(__file__).resolve().parents[3]
SERVER=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
WORK=Path(r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\publication')
BASE='815ceaca49baa0feb1e2d61726c0346ddad2bd37'
APP_BRANCH='fix/station-r74-session-lifecycle-20261007'
BRANCH='docs/station-r74-session-lifecycle-20261007'
VERSION='versions/station-session-lifecycle-r74-20261007'
DOC='docs/station-android/ENTREGA-APP-R74-LIFECYCLE-LATENCIA-20261007.md'
PREFIX='docs/station-android/entrega-app-r74-20261007/'

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
assert git('rev-parse','origin/fix/station-r73-engine-registry-20261007').decode().strip()==BASE,'Server response changed; read before publishing'
assert not git('ls-remote','--heads','origin','refs/heads/'+BRANCH).strip()
assert not git('for-each-ref','--format=%(refname)','refs/heads/'+BRANCH).strip()
commit=appgit('rev-parse','HEAD').decode().strip()
assert appgit('symbolic-ref','--short','HEAD').decode().strip()==APP_BRANCH
assert not appgit('status','--porcelain').strip(),'Publish committed sources only'
assert appgit('ls-remote','--heads','origin','refs/heads/'+APP_BRANCH).decode().split()[0]==commit
v=APP/VERSION;status=json.loads((v/'STATUS.json').read_text('utf8'))
assert status['compiled'] and not status['installed'] and not status['stable']
url=f'https://github.com/luziellacerda/TurboElden/tree/{commit}/{VERSION}'
lead=f'''# R74 — APP → SERVIDOR: correções reproduzidas e investigação da latência

Fonte exata do app: `{commit}`, branch `{APP_BRANCH}`.
[Fontes, receitas, provas e estado]({url}). Base do servidor examinada: `{BASE}`.

Esta é a entrega do aplicativo ao operador. Não é um retorno do servidor nem implantação Linux.
APK candidato `{status['apkSHA256']}`; runtime `{status['runtimeSHA256']}`.
Ambos aparelhos permanecem R73 nesta entrega. Cadastro R73 já estava ativo; não repetir aquela pendência.
Para testar R74, adicionar os DOIS novos registros exatos mantendo os OITO existentes e coordenar a ativação sem descartar partidas.

Além do cadastro, responder às oito questões da seção8: causa da primeira queda às23:52:14UTC, origem dos epochs seguintes, NeedSync13 e tempo efetivo DATA/PONG/filas/locks/SendAsync/proxy/rede. O RTT medido no app não permite atribuir sozinho a demora ao serviço.

Os recibos abaixo foram copiados do commit acima. `evidence/` corresponde a `entrega-app-r74-20261007/evidence/`; demais fontes estão no link do app. Não restaurar Activities antigas. Não declarar gameplay ou retomada validados pelos testes isolados.

---

'''
payload={DOC:(lead+(v/'HANDOFF-APP-R74-PARA-SERVIDOR-20261007.md').read_text('utf8')).encode()}
for name in ('STATUS.json','JAVA-OVERLAY-MANIFEST.json','SOURCE-FILES.json'):
    payload[PREFIX+name]=(v/name).read_bytes()
for p in sorted((v/'evidence').glob('*.json')):payload[PREFIX+'evidence/'+p.name]=p.read_bytes()
for name in ('native/OVERLAY-MANIFEST.json','native/station-lifecycle-r74.patch','native/README.md'):
    payload[PREFIX+name]=(v/name).read_bytes()
note=f'''# R74 entregue pelo APP — lifecycle, ANR e latência — 07/10/2026

APP → SERVIDOR; ler `{DOC}`. Fonte `{commit}`; APK `{status['apkSHA256']}`; runtime `{status['runtimeSHA256']}`. Candidata local, não instalada/homologada. Os dois aparelhos ainda R73. Cadastro R73 já confirmado815ceaca, oito registros. Solicita duas adições rs4 preservando todas as existentes e retorno técnico sobre latência/queda/NeedSync13 da janela23:49:45–23:53:18UTC. Não reiniciar com sessões retidas nem executar implantação por esta publicação documental. RTT122/359ms não equivale ao tempo interno Command0,1756ms. Provas separadas: autoridade principal congelada na primeira queda; ANR de entrada durante recuperação na partida seguinte; flag antiga após catch-up reproduzida localmente. Não atribuir todos os sintomas a um único culpado. Preservar outros produtos, contratos, assinatura, licença, cores, controles, dados e segurança.

## Histórico anterior

'''
for name in ('AGENTS.md','docs/station-android/AGENTS.md','docs/station-android/README.md'):
    payload[name]=note.encode()+git('show',f'{BASE}:{name}')
for name,content in payload.items():
    assert name.endswith(('.md','.json','.patch')) and b'-----BEGIN PRIVATE KEY' not in content
    if name.endswith('.json'):json.loads(content)
files=[dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in sorted(payload.items())]
payload[PREFIX+'DELIVERY-FILES.json']=(json.dumps(dict(appCommit=commit,serverParent=BASE,files=files),indent=2)+'\n').encode()
WORK.mkdir(parents=True,exist_ok=True);index=WORK/'server-r74-docs.index';assert not index.exists()
env=dict(os.environ,GIT_INDEX_FILE=str(index))
author=appgit('show','-s','--format=%an%n%ae',commit).decode().splitlines()
env['GIT_AUTHOR_NAME']=env['GIT_COMMITTER_NAME']=author[0]
env['GIT_AUTHOR_EMAIL']=env['GIT_COMMITTER_EMAIL']=author[1]
git('read-tree',BASE,env=env)
for name,content in sorted(payload.items()):
    blob=git('hash-object','-w','--stdin',data=content).decode().strip()
    git('update-index','--add','--cacheinfo',f'100644,{blob},{name}',env=env)
tree=git('write-tree',env=env).decode().strip()
published=git('commit-tree',tree,'-p',BASE,data=b'docs(station): deliver R74 lifecycle fixes and request relay latency diagnosis\n',env=env).decode().strip()
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
