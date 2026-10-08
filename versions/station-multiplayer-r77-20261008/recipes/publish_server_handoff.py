"""Publish the reviewed R77 APP->SERVER documents from an exact public app commit.

Default invocation is a read-only plan. --publish explicitly permits an alternate
Git index, commit-tree, a new branch and a non-forced push in the existing server
clone. No checkout, normal index, application, phone or live service is modified.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import subprocess

APP = Path(__file__).resolve().parents[3]
SERVER = Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
WORK_ROOT = Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008')
BASE = 'bee3dcd5c2c0c0a228805957fe89b9a6023e8402'
BASE_REF = 'refs/remotes/origin/docs/station-r76-server-review-20261008'
APP_BRANCH = 'feat/station-multiplayer-r77-20261008'
BRANCH = 'docs/station-r77-multiplayer-candidate-20261008'
VERSION = 'versions/station-multiplayer-r77-20261008'
DOC = 'docs/station-android/ENTREGA-APP-R77-MULTIPLAYER-20261008.md'
PREFIX = 'docs/station-android/entrega-app-r77-20261008/'
APP_URL = 'https://github.com/luziellacerda/TurboElden'
SERVER_URL = 'https://github.com/luziellacerda/Servidor-pix'
TEXT_SUFFIXES = {'.md', '.json', '.py', '.cs', '.csproj', '.props', '.targets',
                 '.java', '.in', '.cpp', '.h', '.c', '.tsv', '.txt', '.patch', '.pem'}
TOP_LEVEL = {'HANDOFF-APP-R77-PARA-SERVIDOR-20261008.md', 'README.md',
             'PROFILE-IDENTITY.json', 'STATUS.json', 'SOURCE-FILES.json',
             'JAVA-OVERLAY-MANIFEST.json', 'INSTALLATION.json',
             'SOURCE-MANIFEST.json', 'PACKAGE-INPUTS.json'}
TREES = {'server', 'catalog', 'tests', 'evidence'}
ASSETS = {'assets/station-online/engines.json', 'assets/station-catalog/player-evidence-v1.json'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(repo, *args, data=None, env=None):
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    for key in ('GIT_INDEX_FILE', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR'):
        environment.pop(key, None)
    if env:
        environment.update(env)
    result = subprocess.run(['git', '-c', 'safe.directory=' + repo.as_posix(),
                             '-C', str(repo), *args], input=data, capture_output=True,
                            env=environment, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        raise RuntimeError('Git operation failed: ' + ' '.join(args[:2]) + '\n' +
                           result.stderr.decode('utf8', 'replace'))
    return result.stdout


def state():
    index = Path(git(SERVER, 'rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    # A detached checkout is supported: inspect HEAD as a ref instead of requiring symbolic-ref.
    head_file = Path(git(SERVER, 'rev-parse', '--path-format=absolute', '--git-path', 'HEAD').decode().strip())
    return {'head': git(SERVER, 'rev-parse', 'HEAD').decode().strip(),
            'headFileSHA256': sha(head_file.read_bytes()),
            'indexSHA256': sha(index.read_bytes()) if index.exists() else None,
            'statusSHA256': sha(git(SERVER, 'status', '--porcelain=v1', '-z', '--untracked-files=all'))}


def remote_ref(repo, ref):
    lines = git(repo, 'ls-remote', '--heads', 'origin', ref).decode().splitlines()
    exact = [line.split()[0] for line in lines if line.split()[1] == ref]
    require(len(exact) <= 1, 'Ambiguous remote ref')
    return exact[0] if exact else None


def read_version(commit):
    files = {}
    listing = git(APP, 'ls-tree', '-rz', '--full-tree', commit, '--', VERSION + '/')
    for record in listing.split(b'\0'):
        if not record:
            continue
        meta, raw_path = record.split(b'\t', 1)
        mode, kind, object_id = meta.decode().split()
        path = raw_path.decode('utf8')
        require(path.startswith(VERSION + '/'), 'Unexpected source root')
        relative = path[len(VERSION) + 1:]
        posix = PurePosixPath(relative)
        if relative not in TOP_LEVEL and posix.parts[0] not in TREES and relative not in ASSETS:
            continue
        require(mode == '100644' and kind == 'blob', 'No symlink or executable payload: ' + relative)
        require(not any(part in ('..', '.', '.git', 'bin', 'obj', '__pycache__') for part in posix.parts),
                'Generated/private directory in candidate: ' + relative)
        require(posix.suffix.lower() in TEXT_SUFFIXES, 'Non-allowlisted artifact: ' + relative)
        data = git(APP, 'cat-file', 'blob', object_id)
        require(len(data) <= 16 * 1024 * 1024 and b'\0' not in data, 'Binary/oversized payload: ' + relative)
        text = data.decode('utf-8-sig')
        if posix.suffix.lower() == '.pem':
            require(relative == 'server/src/TurboRamaSuiteOnlineServer/Security/android-attestation-roots.pem'
                    and re.fullmatch(r'(?:\s*-----BEGIN CERTIFICATE-----[A-Za-z0-9+/=\r\n]+-----END CERTIFICATE-----\s*)+', text),
                    'Only the existing public Android attestation certificate bundle is allowed')
        require(not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----', text),
                'Private key material in candidate: ' + relative)
        require(not re.search(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b', text),
                'Possible credential in candidate: ' + relative)
        if posix.suffix.lower() == '.json':
            json.loads(text)
        files[relative] = data
    require(sum(map(len, files.values())) <= 64 * 1024 * 1024, 'Unexpectedly large documentary delivery')
    required = {'HANDOFF-APP-R77-PARA-SERVIDOR-20261008.md', 'PROFILE-IDENTITY.json',
                'SOURCE-MANIFEST.json', 'PACKAGE-INPUTS.json',
                'assets/station-online/engines.json', 'assets/station-catalog/player-evidence-v1.json',
                'server/SOURCE-MANIFEST.json', 'server/CONTRACT.json', 'server/CONTRACT.md',
                'server/proposed-game-profiles-r77.json', 'server/evidence/candidate-checks.json',
                'catalog/catalog-inventory.json', 'catalog/proposed-registry.json',
                'catalog/metadata-coverage.json', 'tests/README.md',
                'tests/evidence/transport-java-dotnet-04.json', 'tests/evidence/transport-java-dotnet-05.json'}
    require(required <= files.keys(), 'Committed delivery is incomplete: ' + ', '.join(sorted(required - files.keys())))
    manifest = json.loads(files['server/SOURCE-MANIFEST.json'])
    for entry in manifest['files']:
        path = 'server/' + entry['path']
        require(path in files and sha(files[path]) == entry['sha256'] and len(files[path]) == entry['bytes'],
                'Server manifest mismatch: ' + path)
    profiles = json.loads(files['server/proposed-game-profiles-r77.json'])
    require(isinstance(profiles, list) and profiles and all(p.get('approved') is False for p in profiles),
            'Delivery must preserve unapproved candidate profiles')
    require(json.loads(files['catalog/proposed-registry.json']).get('approved') is False,
            'Research registry must remain unapproved')
    profile = json.loads(files['PROFILE-IDENTITY.json'])
    require(profile.get('approved') is False and sha(profile['canonical'].encode('utf8')) == profile['sha256'],
            'Profile canonical hash or candidate status mismatch')
    for path in ('tests/evidence/transport-java-dotnet-04.json', 'tests/evidence/transport-java-dotnet-05.json'):
        require(json.loads(files[path]).get('passed') is True, 'Transport receipt is not passed: ' + path)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app-commit', required=True, help='Exact 40-character app commit already pushed')
    parser.add_argument('--app-branch', default=APP_BRANCH, help='Published app branch whose tip must equal that commit')
    parser.add_argument('--work', type=Path, help='Fresh child directory of the explicit E: R77 workspace')
    parser.add_argument('--publish', action='store_true', help='Create documentary commit/branch and push; otherwise only plan')
    args = parser.parse_args()
    require(re.fullmatch(r'[0-9a-f]{40}', args.app_commit), 'Supply an exact lowercase 40-character app commit')
    git(APP, 'check-ref-format', '--branch', args.app_branch)
    require(git(APP, 'rev-parse', args.app_commit + '^{commit}').decode().strip() == args.app_commit,
            'App commit is unavailable')
    before = state()
    if args.publish:
        git(SERVER, 'fetch', 'origin', '+refs/heads/*:refs/remotes/origin/*')
    require(git(SERVER, 'rev-parse', BASE_REF).decode().strip() == BASE,
            'Server return changed; read the new response before publishing')
    require(remote_ref(SERVER, BASE_REF.replace('refs/remotes/origin/', 'refs/heads/')) == BASE,
            'Remote server return changed; read it before publishing')
    require(remote_ref(APP, 'refs/heads/' + args.app_branch) == args.app_commit,
            'Exact app commit must already be published at the selected branch tip')
    require(remote_ref(SERVER, 'refs/heads/' + BRANCH) is None,
            'Delivery branch already exists remotely; do not overwrite it')
    require(not git(SERVER, 'for-each-ref', '--format=%(refname)', 'refs/heads/' + BRANCH).strip(),
            'Delivery branch already exists locally; inspect prior attempt')
    files = read_version(args.app_commit)
    app_url = f'{APP_URL}/tree/{args.app_commit}/{VERSION}'
    lead = f'''# R77 — APP → SERVIDOR: candidata para salas de 2, 3 e 4 jogadores

Fonte imutável do aplicativo: `{args.app_commit}`, ramo `{args.app_branch}`.
[Snapshot completo, receitas e evidências]({app_url}).
Último retorno real do servidor analisado: `{BASE}`.

Esta entrega é documental. As fontes C# são uma **candidata para revisão**, mantidas
sob `docs/`; não substituem `src/`, não implantam Linux nem reiniciam serviços.
Perfis continuam `approved:false`. Estado do APK/aparelhos e limites dos testes
devem ser lidos no handoff e nos recibos do commit acima.

Árvore documental nesta entrega: `{PREFIX}`. O manifesto `DELIVERY-FILES.json`
amarra cada arquivo ao commit do aplicativo e ao pai do servidor. O operador deve
conciliar o contrato, cadastro e fontes com sua versão atual antes de ativar.
As receitas cruzadas Java dependem do snapshot completo do aplicativo referenciado
acima; esta cópia documental não é um projeto Android nem uma instalação do servidor.

---

'''
    payload = {PREFIX + path: data for path, data in files.items()}
    payload[DOC] = lead.encode('utf8') + files['HANDOFF-APP-R77-PARA-SERVIDOR-20261008.md']
    rows = [{'path': path, 'bytes': len(data), 'sha256': sha(data)} for path, data in sorted(payload.items())]
    delivery = {'schemaVersion': 1, 'appCommit': args.app_commit, 'appBranch': args.app_branch,
                'serverParent': BASE, 'candidateServerSourceManifestSHA256': sha(files['server/SOURCE-MANIFEST.json']),
                'files': rows, 'docsOnly': True, 'linuxDeployed': False, 'apkUploaded': False,
                'gameplayAndroidValidatedByThisPublication': False}
    payload[PREFIX + 'DELIVERY-FILES.json'] = (json.dumps(delivery, indent=2) + '\n').encode('utf8')
    require(all(path == DOC or path.startswith(PREFIX) for path in payload), 'Payload outside documentary scope')
    plan = {'mode': 'publish' if args.publish else 'plan-only', 'appCommit': args.app_commit,
            'serverParent': BASE, 'serverBranch': BRANCH, 'files': len(payload),
            'bytes': sum(map(len, payload.values())), 'document': DOC,
            'candidateServerSourceManifestSHA256': delivery['candidateServerSourceManifestSHA256']}
    require(state() == before, 'Server checkout/index changed during preflight')
    if not args.publish:
        print(json.dumps(plan, indent=2))
        return
    work = (args.work or WORK_ROOT / ('publication-' + args.app_commit[:12])).resolve()
    require(work != WORK_ROOT.resolve() and work.is_relative_to(WORK_ROOT.resolve()),
            'Publication directory must remain a child of the explicit E: workspace')
    require(not work.exists(), 'Choose a fresh publication directory; do not erase prior evidence')
    work.mkdir(parents=True)
    (work / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf8')
    author = git(APP, 'show', '-s', '--format=%an%n%ae', args.app_commit).decode('utf8').splitlines()
    require(len(author) == 2 and all(author), 'App author identity unavailable')
    env = {'GIT_INDEX_FILE': str(work / 'server-r77-docs.index'),
           'GIT_AUTHOR_NAME': author[0], 'GIT_COMMITTER_NAME': author[0],
           'GIT_AUTHOR_EMAIL': author[1], 'GIT_COMMITTER_EMAIL': author[1]}
    git(SERVER, 'read-tree', BASE, env=env)
    for path, data in sorted(payload.items()):
        blob = git(SERVER, 'hash-object', '-w', '--stdin', data=data).decode().strip()
        git(SERVER, 'update-index', '--add', '--cacheinfo', f'100644,{blob},{path}', env=env)
    tree = git(SERVER, 'write-tree', env=env).decode().strip()
    published = git(SERVER, 'commit-tree', tree, '-p', BASE,
                    data=b'docs(station): deliver R77 multiplayer candidate, contract and exact qualification\n', env=env).decode().strip()
    changed = set(git(SERVER, 'diff-tree', '--no-commit-id', '--name-only', '-r', published).decode().splitlines())
    require(changed == set(payload), 'Commit changed paths outside the exact documentary payload')
    for path, data in payload.items():
        require(git(SERVER, 'show', f'{published}:{path}') == data, 'Committed bytes mismatch: ' + path)
    require(state() == before, 'Server checkout/index changed before publishing')
    # Recheck remote state after preparing the commit. No force push is permitted.
    require(remote_ref(SERVER, 'refs/heads/docs/station-r76-server-review-20261008') == BASE,
            'Server response moved during publication preparation')
    require(remote_ref(SERVER, 'refs/heads/' + BRANCH) is None, 'Remote delivery appeared concurrently')
    git(SERVER, 'update-ref', 'refs/heads/' + BRANCH, published, '0' * 40)
    prepared = dict(plan, serverCommit=published, tree=tree, pushed=False, serverCheckoutAndIndexPreserved=True)
    (work / 'prepared-commit.json').write_text(json.dumps(prepared, indent=2) + '\n', encoding='utf8')
    git(SERVER, 'push', 'origin', f'refs/heads/{BRANCH}:refs/heads/{BRANCH}')
    require(remote_ref(SERVER, 'refs/heads/' + BRANCH) == published, 'Remote commit does not match delivery')
    require(state() == before, 'Server checkout/index changed after publishing')
    receipt = dict(prepared, pushed=True, url=f'{SERVER_URL}/blob/{published}/{DOC}',
                   linuxDeployed=False, apkUploaded=False, privateMediaUploaded=False)
    (work / 'server-publication.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
