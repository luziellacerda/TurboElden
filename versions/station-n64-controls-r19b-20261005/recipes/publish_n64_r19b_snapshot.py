from pathlib import Path
import datetime, hashlib, json, re, shutil

C = Path(__file__).resolve().parent
W = Path(r'E:\ESTUDO APK\work\station-n64-controls-r19-20261005')
repo = C / 'work/TurboElden-git'
out = repo / 'versions/station-n64-controls-r19b-20261005'
assert not out.exists(), 'Snapshot already exists; review before updating'
out.mkdir()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copy(src, rel):
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    assert digest(src) == digest(dest)

observed = {
    'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'revision': 'R19B',
    'apkSHA256': 'c8fcb15f0951cf5874ac9de2fa2f2e9bfbe26813b7e9ddea5b897355cea4157c',
    'installedByUpdate': True,
    'installedHashVerified': True,
    'game': '007 - The World Is Not Enough',
    'launchWindowLocal': '2026-10-05 15:22:39.563 through 15:22:41.317 America/Fortaleza',
    'gameActivity': 'paulscode.android.mupen64plusae.game.GameActivity',
    'gameTitleScreenObserved': True,
    'ownInputPluginObserved': 'mupen64plus-input-android',
    'controllerResponse': {'confirmedBy': 'maintainer', 'response': 'Sim, aparecem e respondem'},
    'ownMenuAndReturn': {'confirmedBy': 'maintainer', 'response': 'Sim, abriu o menu e voltou sem login'},
    'usbDisconnectedAfterInitialCapture': True,
    'phoneOnlyPreferenceFixes': False,
    'settingsGearVisualCheck': False,
    'performanceMeasurement': False,
    'allGamesVerified': False,
    'stablePromotion': False,
    'localScreenshot': {
        'path': str(W / 'device-evidence/n64-r19b-game.png'),
        'sha256': digest(W / 'device-evidence/n64-r19b-game.png'),
        'published': False,
    },
}
(W / 'device-evidence/n64-device-result.json').write_text(json.dumps(observed, ensure_ascii=False, indent=2)+'\n', 'utf8')
copy(C / 'HANDOFF-N64-CONTROLES-R19.md', 'README.md')
shutil.copy2(C / 'HANDOFF-N64-CONTROLES-R19.md', W / 'HANDOFF-N64-CONTROLES-R19B.md')
for name in ('native_carousel.cpp','native_folders.h','native_n64.h','native_search_download.h'):
    copy(W / 'native' / name, 'native/' + name)
copy(W / 'before/native_n64.h', 'before/native_n64.h')
for name in ('n6_styles.xml','n6_strings.xml'):
    copy(W / 'resources/res/values' / name, 'resources/res/values/' + name)
    copy(W / 'before-resources/res/values' / name, 'before-resources/res/values/' + name)
copy(W / 'merge_resources.py', 'recipes/merge_resources.py')
for name in (
    'prepare_n64_controls_r19.py','test_build_n64_controls_r19.py',
    'audit_n64_resolver_r19.py','package_n64_controls_r19.py',
    'fix_n64_resources_r19b.py','verify_archive_n64_resources_r19b.py',
    'package_n64_controls_r19b.py','archive_r18_for_r19.py','archive_r17_binary_for_r19.py',
):
    copy(C / name, 'recipes/' + name)
copy(C / 'publish_n64_r19b_snapshot.py', 'recipes/publish_n64_r19b_snapshot.py')
for name in ('routes.cpp','old-routes.cpp'):
    copy(W / 'tests' / name, 'tests/' + name)
copy(Path(r'E:\ESTUDO APK\work\station-single-folder-r17-20261005\tests\navigation.cpp'), 'tests/navigation.cpp')
for name in (
    'build-result-r19b.json','build-result.json','tests.json','source-base.json',
    'resource-tests.json','compiled-resource-tests.json','resolver-evidence.json',
    'r18-archive.json','r17-binary-archive.json','r19-archive.json','resources-archive.json',
    'bundled-prefix.txt','resolved-run.txt','android-build.log','routes.log','old-routes.log',
    'navigation.log','resources-build.log','signature.log',
):
    copy(W / name, 'evidence/' + name)
for name in ('installation-r19b.json','n64-device-result.json'):
    copy(W / 'device-evidence' / name, 'evidence/' + name)
lines=(W / 'device-evidence/n64-r19b-logcat.txt').read_text('utf8').splitlines()
selected=[line for line in lines if re.search(r'\b(?:TurboN64|GameActivity|CoreService|CoreInterface):',line)
          and not re.search(r'(?:content://|file://|/storage/|/data/|token|Bearer)',line,re.I)]
assert any('Opening upstream N64 game:' in line for line in selected)
assert any('M64PLUGIN_INPUT:mupen64plus-input-android' in line for line in selected)
(out / 'evidence/n64-runtime.log').write_text('\n'.join(selected)+'\n','utf8')
(out / '.gitattributes').write_text('* -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n','utf8')
files=sorted(p for p in out.rglob('*') if p.is_file())
manifest={'revision':'R19B','files':[{'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files]}
(out / 'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
agents=repo/'AGENTS.md'
old=agents.read_text('utf8')
header='''# R19B — N64 próprio, abertura e controles conferidos — 05/10/2026

Leia `versions/station-n64-controls-r19b-20261005/README.md`. APK instalado por atualização: `E:\\ESTUDO APK\\work\\station-n64-controls-r19-20261005\\TurboStations-N64-Controles-R19B-20261005.apk`, SHA256 `c8fcb15f0951cf5874ac9de2fa2f2e9bfbe26813b7e9ddea5b897355cea4157c`, 2.036.265.660 bytes; hash do telefone idêntico.

N64: prefixo `lib`/caminhos resolvidos e slugs Station corrigidos no despacho; agora abre Mupen64Plus AE próprio. Primeiro R19 fechava por classe Material conflitante; R19B corrige 11 referências XML e o algoritmo de importação. Testes: 240 rotas + 3030 navegações + 80125 checks XML; comparação dos 43618 recursos compilados mostrou somente essas 11 diferenças. APK muda somente carousel SO e resources.arsc, preservando 13079 entradas, DEX/motores, NeoGeo R18, offline/download R16 e navegação R17. Certificado original/16KiB conferidos.

Android: 007 abriu em GameActivity/CoreService próprios, com entrada Android do Mupen. Mantenedor confirmou botões respondendo, menu próprio e saída sem login. USB caiu depois da captura inicial; controles/retorno são confirmação do mantenedor. Engrenagem do N64 não recebeu conferência visual nesta rodada; FPS/outros jogos não validados. Não promover a estável geral. Não houve correção só no telefone nem mudança no servidor.

Fontes finais: overlay native em `E:\\ESTUDO APK\\work\\station-n64-controls-r19-20261005`, demais headers/objetos de `station-download-performance-20261005/frontend-native`. Usar recursos R19B. Base R18 e primeiro R19 arquivados em `G:\\BAKUP SISTEMA APP 03-10-2026\\apks-candidatos-visuais` (duplicatas E removidas após hashes iguais). Não instalar primeiro R19. Trabalho visual R20 separado ainda não integra esta revisão. Preservar jogos/saves/licença e atualizar sem limpar dados.

## Histórico anterior

'''
agents.write_text(header+old,'utf8')
print(json.dumps({'snapshot':str(out),'files':len(files)+1,'bytes':sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),'evidence':observed},ensure_ascii=False,indent=2))
