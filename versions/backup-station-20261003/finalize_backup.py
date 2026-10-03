"""Record public evidence and bundle the committed Git history; no APK/server deployment."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ROOT = Path(r'G:\BAKUP SISTEMA APP 03-10-2026').resolve()
CAPACITY = REPO / 'versions/station-capacity-40000-20261003'
STABLE = '97938400d3fa82d5d1564445c36fc70328add1c4'
BRANCH = 'capacidade-station-40000-20261003'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(*args):
    return subprocess.check_output(
        ['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO), *args])


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def copy_new(source, target):
    if not target.resolve().is_relative_to(ROOT):
        raise RuntimeError('Outside requested backup')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if digest(source) != digest(target):
            raise RuntimeError('Refusing to replace different backup file: ' + str(target))
    else:
        shutil.copy2(source, target)
    if digest(source) != digest(target):
        raise RuntimeError('Documentation copy mismatch')


def prepare():
    summary_path = ROOT / 'RESUMO-BACKUP.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    manifest_path = ROOT / 'MANIFESTO-ARQUIVOS-PRIVADO.json'
    assert summary['status'] == 'complete-copy-readback-verified'
    assert digest(manifest_path) == summary['privateManifestSha256']
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert len(manifest['entries']) == summary['files']
    assert sum(e['sizeBytes'] for e in manifest['entries']) == summary['bytes']
    assert len({e['path'] for e in manifest['entries']}) == summary['files']
    shutil.copy2(summary_path, HERE / summary_path.name)

    sources = json.loads((CAPACITY / 'source-manifest.json').read_text(encoding='utf-8'))
    records = []
    for entry in sources['files']:
        relative = entry['path']
        local = (REPO / relative).read_bytes()
        published = git('show', ':' + relative)
        assert hashlib.sha256(local).hexdigest() == entry['sha256'], relative
        assert local.replace(b'\r\n', b'\n') == published.replace(b'\r\n', b'\n'), relative
        records.append({'path': relative, 'localBuildSha256': entry['sha256'],
                        'gitBlobSha256': hashlib.sha256(published).hexdigest(),
                        'gitBlobBytes': len(published), 'sameContentAfterLfNormalization': True})
    write_json(CAPACITY / 'git-source-integrity.json', {
        'scope': 'Indexed bytes for the 63 build/source/test files, before delivery commit. '
                 'Local build bytes remain in source-manifest.json and the private backup. '
                 'Git normalizes line endings per .gitattributes.',
        'files': records})
    for name in ['README.md', 'RESTAURACAO.md']:
        copy_new(HERE / name, ROOT / name)
    copy_new(CAPACITY / 'git-source-integrity.json', ROOT / 'documentacao/git-source-integrity.json')
    print(json.dumps({'backupVerifiedFiles': summary['files'], 'backupBytes': summary['bytes'],
                      'gitSourceFilesChecked': len(records)}))


def bundle():
    assert git('branch', '--show-current').decode().strip() == BRANCH
    assert not git('status', '--porcelain').strip(), 'Commit all reviewed delivery files first'
    assert git('rev-parse', 'refs/tags/estavel-station-snes-megadrive-20261003^{}').decode().strip() == STABLE
    commit = git('rev-parse', 'HEAD').decode().strip()
    folder = ROOT / 'git'
    folder.mkdir(exist_ok=True)
    target = folder / 'TurboElden-completo-20261003.bundle'
    if target.exists():
        raise RuntimeError('Existing bundle must be reviewed, not overwritten')
    git('bundle', 'create', str(target), '--all')
    verification = subprocess.run(
        ['git', '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
         'bundle', 'verify', str(target)], capture_output=True, check=True)
    heads = git('bundle', 'list-heads', str(target)).decode('utf-8').splitlines()
    assert commit + ' refs/heads/' + BRANCH in heads
    result = {'status': 'complete-git-bundle-verified', 'deliveryCommit': commit,
              'stableCommit': STABLE, 'branch': BRANCH, 'bundle': target.name,
              'sha256': digest(target), 'sizeBytes': target.stat().st_size,
              'refs': heads,
              'verification': (verification.stdout + verification.stderr).decode('utf-8', errors='replace'),
              'scope': 'All refs present in the existing app clone at backup completion. '
                       'Untracked/private build files are covered by the separate private manifest.'}
    write_json(folder / 'BUNDLE-MANIFEST.json', result)
    print(json.dumps({k: result[k] for k in ['status', 'deliveryCommit', 'sha256', 'sizeBytes']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'bundle'])
    args = parser.parse_args()
    assert str(ROOT).lower() == r'g:\bakup sistema app 03-10-2026'
    (prepare if args.action == 'prepare' else bundle)()
