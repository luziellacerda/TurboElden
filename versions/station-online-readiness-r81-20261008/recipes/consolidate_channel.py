"""Consolidate the verified R81 test channel before deleting its exact superseded copies."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, json, os, shutil, zipfile

SNAPSHOT = Path(__file__).resolve().parents[1]
REPO = SNAPSHOT.parents[1]
WORK = Path(r'E:\ESTUDO APK\work\station-online-readiness-r81-20261008')
BACKUP = Path(r'G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008')
OLD = 'test-up-to-4-players-r79'
NEW = 'test-up-to-4-players-r81'
APK = 'TurboStations-Premium-R81-20261008.apk'
APK_SHA = '85fac8f51daa3a370eabb14d98832f75c2f30ff81422c549538ee715627032c6'
OLD_APK_SHA = 'c2aeee4443dedc2862b29dde1f972574bc25464d6993abf01f34d43531558f0a'
CHANNEL_BRANCH = 'fix/station-online-readiness-r81-20261008'

README = r'''# Duas versões atuais

O mantenedor pediu um único backup do projeto, somente dois instaladores atuais e limpeza de APKs anteriores/temporários. Histórico de fontes permanece no Git.

| Canal | Versão | Uso |
|---|---|---|
| `stable-2p` | R76 | Referência de dois jogadores escolhida pelo mantenedor. Houve partida física; engasgos anteriores continuam documentados. |
| `test-4p` | R81 | Candidata para até quatro, com correções de descoberta e apresentação dos perfis individuais/multiplayer. Depende da ativação v3 e de perfis exatos aprovados, inclusive para salas de duas pessoas. Não instalada nem homologada em quatro aparelhos. |

Backup único: `G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008`.

Leia `ACTIVE.json`, escolha explicitamente um canal e use suas fontes completas congeladas. Não selecionar APK por data, procurar a versão com maior número ou recuperar uma Activity de outra revisão. A R81 substitui somente o instalador de teste R79; a referência estável permanece R76.

## Efeito arquivado

`PENDING-VISUAL.json` registra o LED Dreamcast em `versions/station-dreamcast-led-r80-20261008` como **arquivado, sem integração automática**. O mantenedor confirmou que as capas atuais são diferentes das 26 artes usadas na referência. O efeito só poderá ser aplicado após novo pedido e conferência da moldura correspondente. Não há APK R80 nem instalação; o efeito não foi incorporado à R81.

## Fontes e reprodução

`rebuild_verified.py` verifica o APK, os 201/209 Java e as dependências do carrossel; com `--build both --output <pasta nova em E:>`, reproduz o DEX e a biblioteca e exige hashes idênticos. Não usa receitas de sobreposição de versões antigas. Ferramentas JDK/SDK/NDK instaladas e chave original foram preservadas; não apagar como temporários.

Para uma alteração futura, partir de uma cópia de trabalho do canal escolhido, registrar nova versão/manifesto e preservar os hashes da referência. As receitas históricas em `versions/` registram compilações passadas; alguns caminhos de APKs nelas foram aposentados pela limpeza autorizada. Instaladores atuais são somente os de `ACTIVE.json`.

Backup inclui os APKs exatos, fontes Java completas, fontes e dependências do carrossel, fontes nativas dos motores, histórico Git e recibos. APKs, objetos, mídia e arquivos locais de assinatura não são enviados ao Git. A chave original e o backup privado preexistente de assinatura permanecem em seus locais protegidos.

## Conferência da R81

As 209 fontes Java da R81 foram compiladas e seus DEX conferidos com o pacote assinado. Somente `classes35.dex` mudou em relação à R79; os 13.225 demais arquivos do pacote e os 59 vídeos foram preservados. Runtime, cores, engines e carrossel permanecem idênticos à R79. A consolidação confere as fontes, entradas e binários por hash, sem recompilar receitas históricas.

O APK R81 ainda não foi instalado. Últimas instalações comprovadas: Motorola R79 e Samsung R78. Os testes locais não qualificam gameplay Android, quatro aparelhos ou estabilidade WAN. Produção permanece v2, sem perfis reais v3 aprovados. A publicação do catálogo 19 já permite receber as sinopses pelo fluxo vigente; não depende deste APK.

Na conferência anterior da R79 no Motorola, capa/nome/plataforma/avaliação de Battletoads e estado Online estavam visíveis, assim como a sinopse de Bust-A-Move 4. Isso não demonstra a ativação das novas salas.

O recibo `versions/station-online-readiness-r81-20261008/evidence/consolidation.json` registra a substituição do canal, a preservação da referência R76 e do efeito arquivado e a remoção das duas cópias aposentadas após verificar o backup completo.
'''

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text('utf8'))

def regular_files(root):
    """Reject links/junctions before walking or later deleting an exact named tree."""
    root = Path(root)
    need(root.is_dir() and not root.is_symlink() and not root.is_junction(), 'Regular directory required: ' + str(root))
    result = []
    for current, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(current) / name
            need(not path.is_symlink() and not path.is_junction(), 'Reparse entry refused: ' + str(path))
            need(path.resolve().is_relative_to(root.resolve()), 'Escaping entry refused: ' + str(path))
        for name in files:
            path = Path(current) / name
            need(path.is_file(), 'Regular file required: ' + str(path))
            result.append(path)
    return sorted(result)

def inventory(root):
    return {file.relative_to(root).as_posix(): {'sha256': sha(file), 'bytes': file.stat().st_size} for file in regular_files(root)}

def atomic_bytes(path, content):
    path = Path(path)
    need(any(path.resolve().is_relative_to(scope.resolve()) for scope in [BACKUP, REPO / 'release-channels', SNAPSHOT / 'evidence']), 'Write outside consolidation scope')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.r81-tmp')
    need(not temporary.exists(), 'Unexpected temporary file: ' + str(temporary))
    temporary.write_bytes(content)
    os.replace(temporary, path)

def atomic_json(path, value):
    atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

def zsha(archive, name):
    with archive.open(name) as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def receipt_paths():
    return [SNAPSHOT / 'evidence/consolidation.json', BACKUP / 'maintenance/r81-consolidation-20261008/consolidation.json']

def save_receipt(receipt):
    for path in receipt_paths():
        atomic_json(path, receipt)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--prepare-only', action='store_true', help='Copy, verify and select R81; retain both superseded copies without deleting anything')
    modes.add_argument('--cleanup-prepared', action='store_true', help='After authorized preparation, reverify receipts and remove only the exact R79 directory and temporary R81 APK')
    args = parser.parse_args()
    if args.cleanup_prepared:
        cleanup_prepared()
        return
    backup = BACKUP.resolve(strict=True)
    need(backup == BACKUP.absolute() and backup.drive.upper() == 'G:', 'Exact backup root required')
    old = BACKUP / OLD
    new = BACKUP / NEW
    temporary_apk = WORK / 'package' / APK
    need(old.resolve(strict=True).parent == backup and old.name == OLD, 'Exact R79 source required')
    need(not new.exists(), 'Fresh R81 backup destination required')
    active_path = REPO / 'release-channels' / 'ACTIVE.json'
    active = read_json(active_path)
    need(active == read_json(BACKUP / 'release-channels' / 'ACTIVE.json'), 'Repo/backup channel mismatch')
    need(active['channels']['test-4p']['version'] == 'R79' and active['channels']['test-4p']['directory'] == OLD, 'Expected canonical R79 channel')
    need(active['channels']['test-4p']['apkSHA256'] == OLD_APK_SHA, 'R79 identity mismatch')
    need(read_json(REPO / 'release-channels' / 'PENDING-VISUAL.json')['integrateAutomatically'] is False, 'Effect must remain archived')
    preserved_policies = {str(path): sha(path) for path in [REPO / 'release-channels' / 'PENDING-VISUAL.json', BACKUP / 'release-channels' / 'PENDING-VISUAL.json']}
    stable = BACKUP / active['channels']['stable-2p']['directory']
    stable_before = inventory(stable)
    effects_before = inventory(BACKUP / 'effects')
    old_before = inventory(old)
    need(old_before[active['channels']['test-4p']['apk']]['sha256'] == OLD_APK_SHA, 'Wrong old APK')
    for name in ['StationMultiplayerProfile.java', 'StationGamePlayerInfo.java']:
        need(sha(SNAPSHOT / 'tests' / 'baseline-r79' / name) == sha(old / 'java/netplay-src/org/emulationstation/frontend/netplay' / name), 'Preserved R79 regression fixture required: ' + name)
    guard = read_json(BACKUP / 'BUILD-INPUTS-VERIFIED.json')
    for name, entry in guard['files'].items():
        if name.startswith(OLD + '/'):
            relative = name[len(OLD) + 1:]
            need(old_before.get(relative) == {key: entry[key] for key in ['sha256', 'bytes']}, 'Old build input drift: ' + name)
    manifest = read_json(WORK / 'JAVA-SOURCE-MANIFEST.json')
    java_receipt = read_json(WORK / 'java-build-receipt.json')
    package = read_json(SNAPSHOT / 'evidence' / 'package.json')
    need(manifest['version'] == java_receipt['version'] == package['version'] == 'R81', 'Version mismatch')
    need(len(manifest['sources']) == java_receipt['sourceCount'] == 209, '209 frozen Java required')
    need(manifest['sources'] == java_receipt['sourceHashes'], 'Java source manifests differ')
    sources = {p.relative_to(WORK / 'java').as_posix(): p for p in regular_files(WORK / 'java')}
    need(set(sources) == set(manifest['sources']), 'Extra or missing Java source')
    for name, path in sources.items():
        need(sha(path) == manifest['sources'][name], 'R81 source drift: ' + name)
    need(sha(WORK / 'java-build-receipt.json') == package['javaReceiptSHA256'], 'Package/build receipt mismatch')
    need(package['sha256'] == APK_SHA and package['allPackageEntriesVerified'] and package['alignment16KiB'], 'Verified signed package required')
    need(package['installed'] is False and package['archivedDreamcastEffectIncluded'] is False and package['runtimeCoresEnginesUnchangedFromR79'], 'Release scope mismatch')
    need(temporary_apk.stat().st_size == package['bytes'] and sha(temporary_apk) == APK_SHA, 'Temporary APK hash mismatch')
    dexes = {'classes28.dex': WORK / 'compiled-final/client-dex/classes.dex', 'classes35.dex': WORK / 'compiled-final/rooms-dex/classes.dex'}
    for name, path in dexes.items():
        expected = java_receipt['clientDexSHA256' if name == 'classes28.dex' else 'roomsDexSHA256']
        need(sha(path) == expected, 'Compiled DEX mismatch: ' + name)
    carousel = read_json(old / 'carousel-command.json')
    need(sha(old / 'compiled/libturbo_carousel.so') == carousel['expectedSHA256'] == package['protectedEntries']['lib/arm64-v8a/libturbo_carousel.so'], 'Canonical carousel mismatch')
    need(shutil.disk_usage(BACKUP).free > package['bytes'] + 600 * 1024**2, 'Backup free space required')
    print('Verified source APK, 209 Java, DEX, stable channel and archived effect.', flush=True)

    new.mkdir()
    origins = {}
    def copy_file(source, relative):
        destination = new / relative
        need(destination.resolve().is_relative_to(new.resolve()), 'Destination escaped new channel')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        need(sha(destination) == sha(source), 'Copy hash mismatch: ' + relative)
        origins[relative] = str(source)
    for name, path in sources.items():
        copy_file(path, 'java/' + name)
    for path in regular_files(old / 'carousel-inputs'):
        copy_file(path, path.relative_to(old).as_posix())
    for name in ['JAVA-SOURCE-MANIFEST.json', 'java-build-receipt.json']:
        copy_file(WORK / name, name)
    for name, path in dexes.items():
        copy_file(path, 'compiled/' + name)
    copy_file(old / 'compiled/libturbo_carousel.so', 'compiled/libturbo_carousel.so')
    copy_file(temporary_apk, APK)
    carousel['command'] = [argument.replace('{BACKUP}/' + OLD + '/', '{BACKUP}/' + NEW + '/') for argument in carousel['command']]
    need(all(OLD not in argument for argument in carousel['command']), 'Old path remains in carousel command')
    atomic_json(new / 'carousel-command.json', carousel)
    origins['carousel-command.json'] = 'Canonical R79 command; only channel directory replaced with R81'
    copied = inventory(new)
    need(len(copied) == len(old_before), 'Complete channel inventory required')
    need(copied[APK]['sha256'] == APK_SHA, 'Destination APK mismatch')
    for name, old_entry in old_before.items():
        if name.startswith('carousel-inputs/') or name == 'compiled/libturbo_carousel.so':
            need(copied[name] == old_entry, 'Carousel input not preserved: ' + name)
    with zipfile.ZipFile(new / APK) as apk:
        for name, expected in package['protectedEntries'].items():
            need(zsha(apk, name) == expected, 'Protected APK entry mismatch: ' + name)
        videos = [name for name in apk.namelist() if name.endswith('.mp4')]
        need(set(videos) == set(package['videoHashes']) and len(videos) == 59, 'Video inventory mismatch')
        for name in videos:
            need(zsha(apk, name) == package['videoHashes'][name], 'Video changed: ' + name)
        for name, path in dexes.items():
            need(zsha(apk, name) == copied['compiled/' + name]['sha256'], 'Packaged DEX mismatch: ' + name)
    need(inventory(stable) == stable_before and inventory(BACKUP / 'effects') == effects_before, 'Protected backup changed')
    print('Complete R81 backup verified; runtime, carousel and all 59 videos preserved.', flush=True)

    updated = copy.deepcopy(active)
    updated['channels']['test-4p'] = {
        'version': 'R81', 'directory': NEW, 'branch': CHANNEL_BRANCH,
        'sourceCommit': None, 'sourceCommitStatus': 'pending-source-commit',
        'sourceDirectory': 'versions/station-online-readiness-r81-20261008',
        'apk': APK, 'apkSHA256': APK_SHA, 'javaSourceCount': 209,
        'protocol': 'station-stream.v3',
        'status': 'experimental; server activation and exact per-game approved profiles required including two-player rooms',
        'fourPhoneGameplayQualified': False, 'installed': False,
        'runtimeCoresEnginesUnchangedFromR79': True, 'archivedDreamcastEffectIncluded': False,
    }
    need(updated['channels']['stable-2p'] == active['channels']['stable-2p'], 'Stable metadata must remain unchanged')
    updated_guard = copy.deepcopy(guard)
    updated_guard['utc'] = datetime.now(timezone.utc).isoformat()
    updated_guard['updatedBy'] = 'R81 channel consolidation; complete hash verification before cleanup'
    updated_guard['files'] = {name: entry for name, entry in guard['files'].items() if not name.startswith(OLD + '/')}
    for name, entry in copied.items():
        updated_guard['files'][NEW + '/' + name] = dict(entry, origin=origins[name])
    for path in [active_path, BACKUP / 'release-channels' / 'ACTIVE.json']:
        atomic_json(path, updated)
    for path in [REPO / 'release-channels' / 'README.md', BACKUP / 'release-channels' / 'README.md']:
        atomic_bytes(path, README.encode('utf8'))
    atomic_json(BACKUP / 'BUILD-INPUTS-VERIFIED.json', updated_guard)
    maintenance = BACKUP / 'maintenance' / 'r81-consolidation-20261008'
    atomic_bytes(maintenance / 'consolidate_channel.py', Path(__file__).read_bytes())
    receipt = {
        'version': 'R81', 'utc': datetime.now(timezone.utc).isoformat(), 'phase': 'backup-verified-before-cleanup',
        'backupDirectory': str(new), 'apk': str(new / APK), 'apkSHA256': APK_SHA,
        'apkBytes': copied[APK]['bytes'], 'javaSourceCount': 209,
        'clientDexSHA256': java_receipt['clientDexSHA256'], 'roomsDexSHA256': java_receipt['roomsDexSHA256'],
        'carouselSHA256': carousel['expectedSHA256'], 'totalVideos': 59,
        'verifiedFiles': copied, 'verifiedFileCount': len(copied),
        'stableChannelUnchanged': True, 'stableFilesVerified': len(stable_before),
        'archivedEffectsUnchanged': True, 'archivedEffectFiles': effects_before,
        'protectedEntries': package['protectedEntries'], 'previousChannel': active['channels']['test-4p'],
        'recipeSHA256': sha(__file__), 'packageReceiptSHA256': sha(SNAPSHOT / 'evidence/package.json'),
        'newChannelCompleteBeforeCleanup': True, 'removed': [], 'installed': False,
        'compiledDuringConsolidation': False, 'serverChanged': False,
        'serverV3ActivationStillRequired': True, 'exactApprovedGameProfilesStillRequired': True,
        'backupCompleteIndexAndGitBundlePending': True,
        'previousVerifiedFiles': old_before, 'stableVerifiedFiles': stable_before,
        'preservedPolicyHashes': preserved_policies,
    }
    save_receipt(receipt)
    if args.prepare_only:
        pending = '\n## Limpeza pendente\n\nA R81 foi copiada e verificada. A pasta R79 e o APK temporário R81 em E: estão preservados enquanto a autorização para removê-los é resolvida. ACTIVE.json seleciona R76/R81; há temporariamente três APKs no backup. O recibo de consolidação registra esta pendência.\n'
        for path in [REPO / 'release-channels/README.md', BACKUP / 'release-channels/README.md']:
            atomic_bytes(path, (README + pending).encode('utf8'))
        receipt.update(cleanupPending=True, backupApkCount=3, activeInstallerCount=2, temporaryApkPreserved=str(temporary_apk))
        save_receipt(receipt)
        print(json.dumps({'phase': receipt['phase'], 'backupDirectory': str(new), 'apkSHA256': APK_SHA, 'verifiedFiles': len(copied), 'cleanupPending': True, 'removed': []}), flush=True)
        return
    cleanup_prepared()

def cleanup_prepared():
    receipt = read_json(receipt_paths()[0])
    need(receipt == read_json(receipt_paths()[1]), 'Prepared receipts must agree')
    need(receipt['phase'] == 'backup-verified-before-cleanup' and receipt['newChannelCompleteBeforeCleanup'], 'Verified preparation required')
    need(receipt['recipeSHA256'] == sha(__file__), 'Consolidation recipe drift')
    backup = BACKUP.resolve(strict=True)
    need(backup == BACKUP.absolute() and backup.drive.upper() == 'G:', 'Exact backup root required')
    old, new, temporary_apk = BACKUP / OLD, BACKUP / NEW, WORK / 'package' / APK
    active_path = REPO / 'release-channels/ACTIVE.json'
    active = read_json(active_path)
    need(active == read_json(BACKUP / 'release-channels/ACTIVE.json'), 'Repo/backup channel mismatch')
    channel = active['channels']['test-4p']
    need(channel['version'] == 'R81' and channel['directory'] == NEW and channel['apk'] == APK and channel['apkSHA256'] == APK_SHA, 'R81 must be selected before cleanup')
    stable = BACKUP / active['channels']['stable-2p']['directory']
    stable_before, effects_before = receipt['stableVerifiedFiles'], receipt['archivedEffectFiles']
    old_before, copied = receipt['previousVerifiedFiles'], receipt['verifiedFiles']
    need(inventory(stable) == stable_before and inventory(BACKUP / 'effects') == effects_before and inventory(new) == copied, 'Prepared backup drift')
    # Exact absolute deletion boundaries, checked immediately before native Python removal.
    old_resolved = old.resolve(strict=True)
    need(old_resolved == backup / OLD and old_resolved.parent == backup and old_resolved.name == OLD, 'R79 removal boundary')
    need(not old.is_symlink() and not old.is_junction() and inventory(old) == old_before, 'R79 tree changed before cleanup')
    need(read_json(active_path) == read_json(BACKUP / 'release-channels/ACTIVE.json') == active, 'Channel metadata must agree before cleanup')
    need(sha(new / APK) == APK_SHA and len(regular_files(new / 'java')) == 209, 'Destination required immediately before cleanup')
    shutil.rmtree(old_resolved)
    receipt['removed'].append(str(old_resolved))
    save_receipt(receipt)
    temporary_resolved = temporary_apk.resolve(strict=True)
    need(temporary_resolved == WORK.resolve(strict=True) / 'package' / APK and temporary_resolved.parent == (WORK / 'package').resolve(strict=True), 'Temporary APK removal boundary')
    need(not temporary_apk.is_symlink() and sha(temporary_apk) == APK_SHA and sha(new / APK) == APK_SHA, 'Temporary APK removal identity')
    temporary_apk.unlink()
    receipt['removed'].append(str(temporary_resolved))
    expected_apks = {stable / active['channels']['stable-2p']['apk'], new / APK}
    actual_apks = {p for p in regular_files(BACKUP) if p.suffix.lower() == '.apk'}
    need(actual_apks == expected_apks and not temporary_apk.exists() and not old.exists(), 'Exactly two canonical installers required')
    need(all(sha(Path(path)) == value for path, value in receipt['preservedPolicyHashes'].items()), 'Archived effect policy changed')
    need(inventory(stable) == stable_before and inventory(BACKUP / 'effects') == effects_before, 'Protected backup changed during cleanup')
    need(inventory(new) == copied, 'Final R81 inventory drift')
    for path in [REPO / 'release-channels/README.md', BACKUP / 'release-channels/README.md']:
        atomic_bytes(path, README.encode('utf8'))
    receipt.update(utc=datetime.now(timezone.utc).isoformat(), phase='complete', passed=True, canonicalApkCount=2, cleanupPending=False, backupApkCount=2,
                   canonicalApks=sorted(str(p) for p in actual_apks), buildInputsManifestSHA256=sha(BACKUP / 'BUILD-INPUTS-VERIFIED.json'))
    receipt.pop('temporaryApkPreserved', None)
    save_receipt(receipt)
    print(json.dumps({key: receipt[key] for key in ['phase', 'passed', 'backupDirectory', 'apkSHA256', 'verifiedFileCount', 'javaSourceCount', 'canonicalApkCount', 'removed']}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
