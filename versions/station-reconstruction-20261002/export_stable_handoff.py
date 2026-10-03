"""Export documentation/integrity only. Does not build, install, modify server, or push Git."""
from pathlib import Path
import ast, hashlib, json, re, shutil, subprocess, zipfile

REPO = Path(r'C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git')
CANON = Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002')
MODULE = REPO / 'versions/station-reconstruction-20261002'
OUT = REPO / 'versions/estavel-station-snes-megadrive-20261003'
LOCAL = Path(r'E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive')
TAG = 'estavel-station-snes-megadrive-20261003'
SHA = '3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17'
DOC = 'HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md'

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

OUT.mkdir(parents=True, exist_ok=True)
LOCAL.mkdir(parents=True, exist_ok=True)
apk = CANON / 'build/apk/TurboStations-Station-CANDIDATO-20261003.apk'
assert digest(apk) == SHA
frozen = LOCAL / 'TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk'
if frozen.exists():
    assert digest(frozen) == SHA, 'Never overwrite another stable APK'
else:
    shutil.copy2(apk, frozen)
assert digest(frozen) == SHA

# Every source file in the Git mirror must match the input used by this build.
for tree in ('src', 'tests'):
    for path in (MODULE / tree).rglob('*'):
        if path.is_file():
            assert digest(path) == digest(CANON / path.relative_to(MODULE)), path

evidence_path = MODULE / 'evidence/storage-bootstrap-validation-20261003.json'
evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
evidence['stableScope'] = ['snes', 'megadrive']
evidence['gameLaunchPlatforms'] = ['snes', 'megadrive']
evidence['megaDriveExecution'] = {'observedAt': '2026-10-03 17:28:33 -03:00', 'game': 'Cutthroat Island (USA, Europe)', 'romBytes': 2097152, 'segaLogoAndIntroVisible': True, 'normalReturnWithoutLoginConfirmedByUser': True}
evidence['userObservation'] = 'User confirmed normal emulator-menu return without login for SNES and Mega Drive.'
write_json(evidence_path, evidence)
write_json(CANON / 'build/storage-bootstrap-validation-20261003.json', evidence)
write_json(OUT / 'EVIDENCIAS-FLUXO.json', evidence)

files = list((MODULE / 'src').rglob('*')) + list((MODULE / 'tests').rglob('*'))
files += list(MODULE.glob('*.py'))
files += [p for p in MODULE.glob('*.json')]
files += list((MODULE / 'tools').glob('*.json'))
inventory = []
for path in sorted(set(p for p in files if p.is_file())):
    inventory.append({'path': path.relative_to(REPO).as_posix(), 'sizeBytes': path.stat().st_size, 'sha256': digest(path)})
write_json(OUT / 'INVENTARIO-FONTES.json', {'scope': 'Available reconstructed module sources/tests/build scripts/contracts; not original source for every preserved binary.', 'files': inventory})

platform_source = MODULE / 'src/java/org/emulationstation/frontend/station/StationPlatforms.java'
mapping = {}
for match in re.finditer(r'names.put\("([^"]+)",new Platform\("([^"]+)","([^"]+)"\)\);|names.put\("([^"]+)",names.get\("([^"]+)"\)\);', platform_source.read_text(encoding='utf-8')):
    name, label, folder, alias, target = match.groups()
    if name:
        mapping[name] = {'label': label, 'folder': folder}
    else:
        mapping[alias] = {**mapping[target], 'aliasOf': target}
write_json(OUT / 'MAPA-PLATAFORMAS.json', {'source': platform_source.relative_to(REPO).as_posix(), 'sourceSha256': digest(platform_source), 'mappings': mapping})

tree = ast.parse((MODULE / 'link_native_services.py').read_text(encoding='utf-8'))
bindings = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bindings' for t in n.targets))
bindings.update({int(k, 16): v for k, v in json.loads((MODULE / 'src/native/service-bindings.json').read_text()).items()})
assert len(bindings) == 32
write_json(OUT / 'VINCULOS-NATIVOS.json', {'inputLibmainSha256': 'a1ae357dc29caac52d47386a71a0a9a685ecffb9c01d536f5af50b5ba658cda8', 'bindings': [{'entry': hex(k), 'function': v} for k, v in sorted(bindings.items())]})

jar = CANON / 'build/station-client.jar'
sources = {str(p.relative_to(MODULE / 'src/java').with_suffix('')).replace('\\', '.').replace('/', '.') for p in (MODULE / 'src/java').rglob('*.java')}
with zipfile.ZipFile(jar) as z:
    classes = sorted(n[:-6].replace('/', '.') for n in z.namelist() if n.endswith('.class') and n[:-6].replace('/', '.').split('$')[0] in sources)
javap = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\javap.exe')
result = subprocess.run([str(javap), '-p', '-s', '-classpath', str(jar), *classes], check=True, capture_output=True, text=True, encoding='utf-8')
(OUT / 'FUNCOES-JAVA-COMPILADAS.txt').write_text('JAR SHA256: ' + digest(jar) + '\nClasses: ' + str(len(classes)) + '\nCommand: javap -p -s -classpath station-client.jar <all project classes>\n\n' + result.stdout, encoding='utf-8')
lines = ['# Índice de declarações nos fontes', '', 'Índice de navegação, não parser semântico; assinaturas Java completas em FUNCOES-JAVA-COMPILADAS.txt. Declarações em linhas múltiplas continuam no fonte.', '']
for path in sorted((MODULE / 'src').rglob('*')):
    if path.suffix not in ('.java', '.cpp', '.hpp', '.c'):
        continue
    matches = []
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if re.search(r'\b(public|private|protected|static|JNIEXPORT|extern\s+"C")\b.*\([^;]*\)', line) or re.search(r'\bStation\w+\s*\(', line):
            matches.append((number, line.strip()))
    lines += ['## ' + path.relative_to(MODULE).as_posix(), '', '```text']
    lines += [str(n) + ': ' + text for n, text in matches]
    lines += ['```', '']
(OUT / 'MAPA-FUNCOES-FONTE.md').write_text('\n'.join(lines), encoding='utf-8')

entries = []
with zipfile.ZipFile(apk) as z:
    for info in z.infolist():
        with z.open(info) as stream:
            entries.append({'path': info.filename, 'sizeBytes': info.file_size, 'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()})
write_json(OUT / 'INVENTARIO-APK.json', {'apkSha256': SHA, 'entries': entries})
report = json.loads((CANON / 'build/apk/apk-report.json').read_text(encoding='utf-8'))
manifest = {'name': 'Station estável — SNES e Mega Drive', 'tag': TAG, 'sourceParentCommit': '2834e3b101ce4e957414bccd13154c8a70af2f01', 'sourceRevision': 'The commit resolved by the immutable tag contains this complete source snapshot.', 'package': report['package'], 'versionName': report['versionName'], 'versionCode': report['versionCode'], 'clientVersion': '1.0.8-station-storage-20261003.3', 'apkPath': str(frozen), 'apkSha256': SHA, 'apkSizeBytes': frozen.stat().st_size, 'signerSha256': report['signerSha256'], 'basePath': report['base'], 'baseSha256': report['baseSha256'], 'canonicalSource': str(CANON), 'gitSource': MODULE.relative_to(REPO).as_posix(), 'serverHandoffCommit': 'fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61', 'serverApiReleaseReported': 'fd13c0d27eaab6a4dcf931a9cd64c3dcd7dd50c4', 'catalogRevision': 3, 'catalogPublicCount': 1816, 'catalogPrivateCountReported': 2071, 'stableScope': ['SNES content download/install/launch/normal return', 'Mega Drive content download/install/launch/normal return'], 'futureCapacityTarget': 40000, 'capacity40000Implemented': False, 'fullEmulatorMatrixVerified': False, 'commerceEndToEndVerified': False, 'hostChecks': 327, 'androidRootChecks': 10, 'privateDependenciesRequired': ['Exact base APK', 'Existing signing identity', 'Android SDK/NDK and build tools specified in scripts'], 'handoff': 'docs/server/' + DOC, 'apkNotCommitted': True}
write_json(OUT / 'MANIFESTO-ESTAVEL.json', manifest)
(OUT / 'README.md').write_text('# Station estável — SNES e Mega Drive\n\n[Handoff completo](../../docs/server/' + DOC + ') · [Manifesto](MANIFESTO-ESTAVEL.json) · [Recuperação](RESTAURACAO.md) · [Fontes](../station-reconstruction-20261002/)\n\nTag `' + TAG + '`. APK SHA256 `' + SHA + '`. Catálogo1816/revisão3; SNES e Mega Drive com download/instalação/abertura/retorno conferidos. Não é certificação de todos os jogos/motores. Os inventários neste diretório identificam fontes, métodos compilados,32 vínculos nativos, aliases e cada entrada do APK.\n\nMeta seguinte:40mil jogos; a tag mantém os limites antigos e o funcionamento comprovado.\n', encoding='utf-8')
(OUT / 'RESTAURACAO.md').write_text('# Recuperação exata\n\n1. Resolver a tag `' + TAG + '` sem mover tags históricas.\n2. Ler o manifesto e comparar o SHA256 do APK privado `' + str(frozen) + '` com `' + SHA + '`.\n3. Com o jogo encerrado normalmente, atualizar o pacote `org.turboramastation.frontend` com a mesma assinatura, usando `adb install --no-incremental -r --user 0`. Não desinstalar nem limpar dados.\n4. Conferir o APK instalado, sessão,1816 itens/revisão3, capas e os jogos já instalados.\n5. A base de build é d8104343, não um dos APKs candidatos intermediários. Fontes canônicos em `' + str(CANON) + '`, mirror no Git `versions/station-reconstruction-20261002`. Receita detalhada no handoff, seção13.\n\nO Git não guarda a chave privada, APK/base, ROMs ou BIOS. Se o APK congelado faltar, reconstruir com as dependências exatas e validar o novo artefato; não afirmar hash idêntico automaticamente. Se a chave Keystore do telefone tiver sido apagada, recuperação administrativa da licença é necessária; não contornar autenticação. Esta recuperação não troca índice/DLL do servidor.\n', encoding='utf-8')

for path in OUT.iterdir():
    if path.is_file():
        shutil.copy2(path, LOCAL / path.name)
shutil.copy2(REPO / 'docs/server' / DOC, LOCAL / DOC)
shutil.copy2(REPO / 'docs/server' / DOC, CANON / DOC)
print(json.dumps({'stableApk': str(frozen), 'sha256': SHA, 'sourceFiles': len(inventory), 'classes': len(classes), 'nativeBindings': len(bindings), 'apkEntries': len(entries), 'platformNames': len(mapping)}, ensure_ascii=False))
