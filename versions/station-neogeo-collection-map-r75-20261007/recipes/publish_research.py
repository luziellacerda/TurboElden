"""Publish only the authorized stability handoff; leave the server checkout/index untouched."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
APP=Path(__file__).resolve().parents[3]
SERVER=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
WORK=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-map-r75-20261007\publication')
BASE='815ceaca49baa0feb1e2d61726c0346ddad2bd37'
APP_BRANCH='fix/station-neogeo-collection-map-r75-20261007'
BRANCH='docs/station-r74-stability-research-20261007'
SOURCE_DOC='docs/server/PESQUISA-ESTABILIDADE-R74-20261007.md'
DOC='docs/station-android/PEDIDO-ESTABILIDADE-R74-PESQUISA-20261007.md'
PREFIX='docs/station-android/research-r74-stability-20261007/'
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
assert git('rev-parse','origin/fix/station-r73-engine-registry-20261007').decode().strip()==BASE,'New return requires review first'
assert not git('ls-remote','--heads','origin','refs/heads/'+BRANCH).strip()
assert not git('for-each-ref','--format=%(refname)','refs/heads/'+BRANCH).strip()
commit=appgit('rev-parse','HEAD').decode().strip()
assert appgit('symbolic-ref','--short','HEAD').decode().strip()==APP_BRANCH
assert not appgit('status','--porcelain').strip(),'Publish committed sources only'
assert appgit('ls-remote','--heads','origin','refs/heads/'+APP_BRANCH).decode().split()[0]==commit
lead=f'''# Pesquisa APP → SERVIDOR — estabilidade R74

Fonte integral e evidências no app `{commit}`, branch `{APP_BRANCH}`.
[Documento original](https://github.com/luziellacerda/TurboElden/blob/{commit}/{SOURCE_DOC}).

Esta é uma solicitação ao operador, NÃO resposta do servidor ou implantação.
R74 está instalada nos dois aparelhos. R75 é uma candidata visual que corrige
cinco nomes de vídeos; seu motor online é idêntico à R74. Não cadastrar engines
novas por causa da R75 nem instalar Activities antigas. O pedido R74 8d48252
continua como autoridade dos IDs rs4/runtime804b2acfea4c e das oito questões.

O mantenedor relata menos travamentos. A pesquisa distingue prova isolada,
revisão de código, hipóteses e medições ainda necessárias. Responder SRV-01/02/03
e cruzar APP-01/EXP-01 com o app; não executar a prova isolada contra produção.

---

'''
payload={DOC:lead.encode()+(APP/SOURCE_DOC).read_bytes()}
research=APP/'docs/server/research-r74-stability-20261007'
assert research.is_dir()
for p in sorted(research.rglob('*')):
 if p.is_file():
  assert p.suffix in ('.md','.json','.py','.java','.in','.txt')
  payload[PREFIX+p.relative_to(research).as_posix()]=p.read_bytes()
note=f'''# Pesquisa de estabilidade R74 recebida do APP — 07/10/2026

Ler `{DOC}`. Fonte app `{commit}`. Pedido ao operador, não retorno nem deploy.
Corrigir/coletar SRV-01 (epoch da primeira causa), SRV-02 (handshake Close)
e SRV-03 (latência real DATA/PONG/filas); cruzar APP-01 e EXP-01.
R74 instalada nos dois aparelhos; mantenedor relatou melhora, sem homologação
prolongada. R75 visual candidata mantém runtime/DEX/engines R74, não pede novo
cadastro de motor. Preservar todos os produtos, sessões, dados e segurança.
Coordenar qualquer reinício pois a recuperação reside em RAM.

## Histórico anterior

'''
for name in ('AGENTS.md','docs/station-android/AGENTS.md','docs/station-android/README.md'):
 payload[name]=note.encode()+git('show',f'{BASE}:{name}')
for name,data in payload.items():
 assert b'-----BEGIN PRIVATE KEY' not in data
 if name.endswith('.json'):json.loads(data)
files=[dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in sorted(payload.items())]
payload[PREFIX+'DELIVERY-FILES.json']=(json.dumps(dict(appCommit=commit,serverParent=BASE,files=files),indent=2)+'\n').encode()
WORK.mkdir(parents=True,exist_ok=True);index=WORK/'server-research.index';assert not index.exists()
env=dict(os.environ,GIT_INDEX_FILE=str(index))
author=appgit('show','-s','--format=%an%n%ae',commit).decode().splitlines()
env['GIT_AUTHOR_NAME']=env['GIT_COMMITTER_NAME']=author[0]
env['GIT_AUTHOR_EMAIL']=env['GIT_COMMITTER_EMAIL']=author[1]
git('read-tree',BASE,env=env)
for name,data in sorted(payload.items()):
 blob=git('hash-object','-w','--stdin',data=data).decode().strip()
 git('update-index','--add','--cacheinfo',f'100644,{blob},{name}',env=env)
tree=git('write-tree',env=env).decode().strip()
published=git('commit-tree',tree,'-p',BASE,data=b'docs(station): cross-check stability research and request precise relay fixes\n',env=env).decode().strip()
assert set(git('diff-tree','--no-commit-id','--name-only','-r',published).decode().splitlines())==set(payload)
for name,data in payload.items():assert git('show',f'{published}:{name}')==data
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
