"""Publish the single R81 operator delivery with an isolated index; no checkout or deployment."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parent.parent
APP=ROOT.parents[1]
SERVER=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
WORK=Path(r'E:\ESTUDO APK\work\station-online-readiness-r81-20261008')
PARENT='a4fd0d73a7eaaf43fafbae1c42e9b83580985433'
RETURN_BRANCH='docs/station-r79-server-return-20261008'
BRANCH='docs/station-r81-activation-final-20261008'
PREFIX='docs/station-android/entrega-app-r81-20261008/'
DOC='docs/station-android/FECHAMENTO-APP-R81-ATIVACAO-20261008.md'
VERSION='versions/station-online-readiness-r81-20261008'
def need(ok,message):
    if not ok:raise RuntimeError(message)
def git(repo,*args,data=None,env=None):
    run=subprocess.run(['git','-c','safe.directory='+repo.as_posix(),'-c','core.longpaths=true',*args],cwd=repo,input=data,env=dict(os.environ,**(env or {})),capture_output=True)
    need(run.returncode==0,'Git failed '+str(args[:2])+': '+run.stderr.decode('utf8','replace')[:2000]);return run.stdout
def digest(data):return hashlib.sha256(data).hexdigest()
def state():
    index=git(SERVER,'rev-parse','--git-path','index').decode().strip();p=Path(index);p=p if p.is_absolute() else SERVER/p
    return git(SERVER,'rev-parse','HEAD'),git(SERVER,'status','--porcelain=v1','-z'),digest(p.read_bytes()) if p.exists() else None
def remote(branch):
    output=git(SERVER,'ls-remote','--heads','origin','refs/heads/'+branch).decode().strip();return output.split()[0] if output else None
def main():
    p=argparse.ArgumentParser();p.add_argument('--app-commit',required=True);p.add_argument('--publish',action='store_true');a=p.parse_args()
    need(re.fullmatch('[0-9a-f]{40}',a.app_commit),'Explicit app commit required')
    need(git(SERVER,'remote','get-url','origin').decode().strip() in ['https://github.com/luziellacerda/Servidor-pix.git','https://github.com/luziellacerda/Servidor-pix'],'Authorized server repository only')
    need(remote(RETURN_BRANCH)==PARENT,'A newer server response must be reviewed first')
    before=state();files={}
    for raw in git(APP,'ls-tree','-rz','--full-tree',a.app_commit,'--',VERSION+'/').split(b'\0'):
        if not raw:continue
        meta,name=raw.split(b'\t',1);mode,kind,oid=meta.decode().split();rel=name.decode()[len(VERSION)+1:]
        if not (rel.startswith('server-tools/') or rel.startswith('activation/') or rel in ['README.md','STATUS.json','FECHAMENTO-SERVIDOR-R81-20261008.md','JAVA-SOURCE-MANIFEST.json'] or rel.startswith('evidence/')):continue
        need(mode=='100644' and kind=='blob' and Path(rel).suffix in ['.md','.json','.py'],'Text source only')
        content=git(APP,'cat-file','blob',oid);need(b'\0' not in content and len(content)<2*1024*1024,'Oversized/binary payload')
        text=content.decode('utf8');need(not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b',text),'Potential credential')
        if rel.endswith('.json'):json.loads(text)
        files[rel]=content
    need({'FECHAMENTO-SERVIDOR-R81-20261008.md','server-tools/prepare_content_identity_registry.py','server-tools/TEST-RESULT.json','evidence/package.json'}<=files.keys(),'Incomplete delivery')
    payload={PREFIX+n:b for n,b in files.items()}
    lead=f'# Entrega única R81 — pacote pronto para ativação\n\nFonte do app `{a.app_commit}`. [Java completo, testes e receitas](https://github.com/luziellacerda/TurboElden/tree/{a.app_commit}/{VERSION}).\n\nPai: último retorno real `{PARENT}`. Esta entrega fornece código offline e critérios de conclusão; não implanta Linux. Execute a ferramenta em `{PREFIX}server-tools/prepare_content_identity_registry.py`. Todos os arquivos referidos abaixo acompanham `{PREFIX}`.\n\n'
    payload[DOC]=lead.encode()+files['FECHAMENTO-SERVIDOR-R81-20261008.md']
    manifest=dict(appCommit=a.app_commit,serverParent=PARENT,linuxDeployed=False,apkUploaded=False,files=[dict(path=n,sha256=digest(b),bytes=len(b)) for n,b in sorted(payload.items())])
    payload[PREFIX+'DELIVERY-FILES.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    plan=dict(appCommit=a.app_commit,serverParent=PARENT,branch=BRANCH,document=DOC,files=len(payload),bytes=sum(map(len,payload.values())),published=False)
    need(state()==before,'Server checkout changed')
    if not a.publish:print(json.dumps(plan,indent=2));return
    need(remote(BRANCH) is None,'Delivery branch already exists')
    work=WORK/('publication-'+a.app_commit[:12]);need(not work.exists(),'Fresh publication directory');work.mkdir()
    author=git(APP,'show','-s','--format=%an%n%ae',a.app_commit).decode().splitlines();need(len(author)==2 and all(author),'Source author required')
    env=dict(GIT_INDEX_FILE=str(work/'delivery.index'),GIT_AUTHOR_NAME=author[0],GIT_COMMITTER_NAME=author[0],GIT_AUTHOR_EMAIL=author[1],GIT_COMMITTER_EMAIL=author[1])
    git(SERVER,'read-tree',PARENT,env=env)
    for name,body in sorted(payload.items()):
        blob=git(SERVER,'hash-object','-w','--stdin',data=body).decode().strip();git(SERVER,'update-index','--add','--cacheinfo',f'100644,{blob},{name}',env=env)
    tree=git(SERVER,'write-tree',env=env).decode().strip()
    commit=git(SERVER,'commit-tree',tree,'-p',PARENT,data=b'docs(station): deliver complete R81 client and offline activation preparation\n',env=env).decode().strip()
    need(set(git(SERVER,'diff-tree','--no-commit-id','--name-only','-r',commit).decode().splitlines())==set(payload),'Unexpected path')
    for name,body in payload.items():need(git(SERVER,'show',commit+':'+name)==body,'Committed byte mismatch')
    need(state()==before and remote(RETURN_BRANCH)==PARENT and remote(BRANCH) is None,'Concurrent update')
    git(SERVER,'update-ref','refs/heads/'+BRANCH,commit,'0'*40)
    git(SERVER,'push','origin','refs/heads/'+BRANCH+':refs/heads/'+BRANCH)
    need(remote(BRANCH)==commit and state()==before,'Remote verification or checkout preservation failed')
    receipt=dict(plan,published=True,serverCommit=commit,serverCheckoutAndIndexPreserved=True,linuxDeployed=False,apkUploaded=False,url=f'https://github.com/luziellacerda/Servidor-pix/blob/{commit}/{DOC}')
    (work/'server-publication.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
