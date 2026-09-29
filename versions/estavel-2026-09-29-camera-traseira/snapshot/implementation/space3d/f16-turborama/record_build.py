"""Documenta evidências do APK F-16 instalado; não altera backup nem aparelho.

Executar após instalação e verify_on_device.py. Navegação opcional deve estar em
space3d/f16-device-navigation.json: {"apk_sha256": "...", "results": [...]}.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess
import zipfile

F = Path(__file__).resolve().parent
D = F.parent
P = D.parent


def digest(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def sha(path):
    with Path(path).open('rb') as stream:
        return digest(stream)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def evidence(relative):
    path = (P / relative).resolve()
    require(path.is_relative_to(P.resolve()) and path.is_file(),
            'Evidência ausente ou fora da implementação: ' + str(relative))
    return path


def main():
    apk = P / 'TurboramaStation-carrossel-nativo-completo.apk'
    apk_hash = sha(apk)
    device_file = D / 'f16-device-validation.json'
    device = load(device_file)
    require(device.get('apk_sha256') == apk_hash,
            'Validação Android de outro APK. Execute verify_on_device.py nesta revisão.')
    require(device.get('installed_hash_matches') is True,
            'Igualdade do hash instalado não confirmada.')
    require(device.get('fatal_errors_in_collected_log') is False,
            'Ausência de erro fatal no trecho coletado não confirmada.')
    require(device.get('native_renderer', '').startswith('F16 ready;'),
            'Inicialização do renderizador F-16 não confirmada.')
    for key in ('time', 'installed_at', 'device', 'rom_size_mtime_preserved', 'stay_on'):
        require(bool(str(device.get(key, ''))), 'Campo Android obrigatório ausente: ' + key)
    shots = device.get('screenshots', [])
    require(bool(shots), 'O relatório Android não contém captura.')
    for relative in shots:
        evidence(relative)
    evidence(device.get('video', ''))

    module_hash = sha(P / 'libturbo_carousel.so')
    license_names = load(D / 'license-assets.json')
    require(isinstance(license_names, list) and bool(license_names), 'Lista de avisos/fontes inválida.')
    license_hashes = {}
    with zipfile.ZipFile(apk) as archive:
        with archive.open('lib/arm64-v8a/libturbo_carousel.so') as stream:
            require(digest(stream) == module_hash, 'Módulo nativo do APK difere da cópia local.')
        for name in license_names:
            local = (D / name).resolve()
            require(local.is_relative_to(D.resolve()), 'Caminho de aviso inválido: ' + name)
            license_hashes[name] = sha(local)
            with archive.open('assets/turbo-space3d/' + name) as stream:
                require(digest(stream) == license_hashes[name], 'Aviso/fonte difere no APK: ' + name)

    env = dict(os.environ)
    env['TEMP'] = env['TMP'] = str(P / 'tmp')
    java = r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe'
    signer = r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\apksigner.jar'
    signature = subprocess.check_output(
        [java, '-Djava.io.tmpdir=' + str(P / 'tmp'), '-jar', signer,
         'verify', '--verbose', '--print-certs', str(apk)],
        encoding='utf-8', errors='replace', env=env)
    match = re.search(r'Signer #1 certificate SHA-256 digest:\s*([0-9a-fA-F]{64})', signature)
    require(match is not None, 'Certificado não identificado.')
    certificate = match.group(1).lower()
    require(certificate == '7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825',
            'Certificado diferente da linha de atualização instalada.')
    for version in (2, 3):
        require(f'Verified using v{version} scheme (APK Signature Scheme v{version}): true' in signature,
                f'Assinatura v{version} não confirmada.')

    # build_native.py regenera space3d_shaders.h sem mudar seu conteúdo após o
    # harness; usar a data dos GLSL originais, não a data desse header gerado.
    sources = [P / 'native_space3d.h', P / 'native_space.h', P / 'native_flight.h', P / 'space3d_assets.h']
    sources += list(D.glob('*.glsl')) + list(D.glob('*.vert')) + list(D.glob('*.frag'))
    latest_source = max(path.stat().st_mtime for path in sources)
    graphics = {}
    for name in ('native-harness-report.json', 'native-harness-es2-report.json', 'preview-report.json'):
        path = D / name
        report = load(path)
        require(path.stat().st_mtime >= latest_source, 'Relatório gráfico anterior aos fontes: ' + name)
        if name.startswith('native-harness'):
            require(report.get('native_renderer') == 'PASS' and
                    report.get('shared_GLES100_shader_compile') == 'PASS' and
                    report.get('same_frame_cache') == 'PASS' and report.get('gl_errors') == 0,
                    'Harness gráfico não aprovado: ' + name)
            require(bool(report.get('tracked_GL_state_restored')), 'Estados GL não registrados: ' + name)
        else:
            require(report.get('shader_compilation') == 'PASS' and report.get('frames', 0) > 0,
                    'Prévia gráfica não aprovada.')
        graphics['space3d/' + name] = {'sha256': sha(path), 'result': report}

    integrity_file = P / 'package-integrity.json'
    integrity = load(integrity_file)
    require(integrity_file.stat().st_mtime >= apk.stat().st_mtime, 'Integridade anterior ao APK atual.')
    require(Path(integrity.get('apk', '')).resolve() == apk.resolve(), 'Integridade aponta para outro APK.')
    require(not integrity.get('removed') and integrity.get('changed') == ['classes5.dex'],
            'Mudança inesperada nos componentes originais.')

    navigation = {'status': 'Não verificada para este APK', 'platforms': 0}
    nav_file = D / 'f16-device-navigation.json'
    if nav_file.is_file():
        nav = load(nav_file)
        if isinstance(nav, dict) and nav.get('apk_sha256') == apk_hash:
            rows = nav.get('results')
            require(isinstance(rows, list) and bool(rows), 'Navegação atual sem resultados.')
            require(all(row.get('back') == 'PASS' and row.get('activity') == 'ESActivity' and
                        isinstance(row.get('games'), int) and row['games'] >= 0 for row in rows),
                    'Navegação atual contém falha ou linha incompleta.')
            require(len({row.get('filter') for row in rows}) == len(rows), 'Plataformas repetidas na navegação.')
            navigation = {'status': 'PASS', 'platforms': len(rows),
                          'catalog_games': sum(row['games'] for row in rows),
                          'report': 'space3d/f16-device-navigation.json',
                          'report_sha256': sha(nav_file), 'apk_sha256': apk_hash,
                          'scope': 'Entrada no catálogo e retorno nativo; não executa os jogos.'}

    model = load(D / 'model-manifest.json')
    shader = (D / 'ship.frag').read_text(encoding='utf-8')
    common = (D / 'scene-common.glsl').read_text(encoding='utf-8')
    require('vec2 shoulder=' in shader and '/.05480' in shader and '/.45' in shader,
            'Inscrições laterais desta revisão não identificadas no shader.')
    require('localFromWorld' in shader and all(token in common for token in
            ('turnPhase()', 'shipOffset()', 'worldFromLocal', 'localFromWorld')),
            'Movimento coordenado desta revisão não identificado nos fontes.')

    install_method = device.get('install_method', 'Método não registrado; hash instalado conferido.')
    installation = ('Atualização por adb install -r; pacote e certificado mantidos.'
                    if install_method in ('install -r', 'adb install -r') else str(install_method))
    nav_text = (f"{navigation['platforms']} catálogos: entrada e retorno nativo aprovados; "
                f"{navigation['catalog_games']} itens contados nas listas."
                if navigation['status'] == 'PASS' else
                'Navegação não contabilizada nesta revisão: falta relatório com o hash deste APK.')
    perf = device.get('performance')
    perf_text = 'Sem amostra de desempenho disponível neste relatório.'
    if perf:
        perf_text = (f"Amostra curta no Android: {perf['average_fps']:.2f} apresentações/s, "
                     f"mediana {perf['median_ms']:.2f} ms, p95 {perf['p95_ms']:.2f} ms; "
                     f"{perf['frames_over_25ms']} intervalos acima de 25 ms em {perf['intervals']}. "
                     'Não é teste prolongado de temperatura/bateria nem mede jogos.')
    scope = ['hash do APK instalado igual ao local', 'inicialização do F-16 no aparelho',
             'captura de tela e vídeo no aparelho', 'trecho de log sem erro fatal',
             'tamanho e data da ROM de referência conferidos']
    if navigation['status'] == 'PASS':
        scope.append('entrada e retorno nativo dos catálogos vinculados ao mesmo hash')
    now = datetime.datetime.now().astimezone().isoformat()
    remaining = list(device.get('untested', [])) + [
        'Avaliação visual final pelo usuário', 'Não houve verificação individual de todos os jogos e saves.']
    result = {'date': now, 'model': model.get('model', 'F-16 TURBORAMA'), 'apk': str(apk),
              'bytes': apk.stat().st_size, 'sha256': apk_hash, 'certificate_sha256': certificate,
              'native_module_sha256': module_hash, 'native_module_matches_apk': True,
              'license_assets_match': True, 'license_asset_sha256': license_hashes,
              'android_installed': True, 'installed_at': device['installed_at'],
              'installed_device': device['device'], 'installation_method': install_method,
              'installed_apk_hash_verified': True, 'android_tested': True,
              'android_validation_scope': scope, 'android_validation_report': 'space3d/f16-device-validation.json',
              'android_validation_report_sha256': sha(device_file), 'desktop_reports': graphics,
              'integrity_report': 'package-integrity.json', 'integrity_report_sha256': sha(integrity_file),
              'navigation': navigation,
              'geometry': {k: model.get(k) for k in ('vertices', 'triangles', 'maps', 'texture_size', 'nozzles')},
              'visual_changes': {'body_wordmarks': 2, 'wordmark_aspect_ratio': 8.21,
                                 'motion': 'Voo contínuo sempre visível; nuvens e estrelas com o mesmo ponto de fuga e velocidade constante.',
                                 'clouds': device.get('clouds_renderer'),
                                 'flight_sequence_renderer': device.get('flight_sequence_renderer')},
              'performance': perf, 'rom_reference': device['rom_size_mtime_preserved'],
              'stay_on': device['stay_on'], 'remaining': remaining}
    geometry = (f"{model['vertices']} vértices, {model['triangles']} triângulos, "
                f"{model['maps']} mapas {model['texture_size'][0]}×{model['texture_size'][1]}, "
                f"{len(model['nozzles'])} saída de motor registrada no manifesto.")
    content = f'''# F-16 TURBORAMA — revisão instalada e conferida

Registro: {now}

## APK

- Arquivo: {apk.as_posix()}
- Tamanho: {apk.stat().st_size} bytes.
- SHA256 local e instalado: `{apk_hash}`.
- Instalação registrada: {device['installed_at']}; aparelho {device['device']}.
- {installation}
- Certificado SHA256: `{certificate}`; assinaturas v2/v3 conferidas.
- Módulo nativo e {len(license_names)} arquivos de avisos/fontes iguais às cópias locais.

## Visual desta revisão

Duas inscrições TURBORAMA independentes nos ombros esquerdo e direito da fuselagem, com separação no dorso e proporção natural aproximada de 8,21:1. As inscrições nas asas e cauda também tiveram a proporção ajustada. Voo contínuo: inclinações suaves e pequenas mudanças de altura, sempre visível. A ação de entrada/saída do hiperespaço foi removida a pedido do usuário. O F-16 continua renderizado como geometria 3D; posição/tamanho/opacidade são compostos pelo renderer nativo. Nuvens por volume com 64 amostras em alvo 320×180 e névoa distante passam sob os controles, partindo do mesmo ponto de fuga das estrelas (0,65;0,32). O avanço usa o mesmo relógio nativo com velocidade constante. Não é vídeo nem sobreposição Java. Curva, inclinação, altura e motor têm variações suaves; bocal e volume do jato compartilham a transformação da aeronave.

{geometry} A iluminação e os materiais usam aproximações para tempo real. A arte aprovada é referência visual; a aeronave animada é geometria 3D.

## Evidências desta revisão

- Android: inicialização, captura/vídeo e ausência de erro fatal no trecho coletado, vinculados ao hash acima.
- {nav_text}
- Computador: harness GLES2 e GLES3 aprovados, zero erros GL e estados registrados preservados; prévia com compilação de shader aprovada. Os relatórios são posteriores aos fontes gráficos atuais e não substituem a captura Android.
- {perf_text}
- Integridade: {integrity['files_preserved']} entradas originais preservadas, {len(integrity['added'])} adições, zero remoções; única entrada original alterada: classes5.dex, ponte nativa existente.
- ROM de referência: tamanho/data preservados conforme relatório: `{device['rom_size_mtime_preserved']}`. Isto não verifica todos os jogos nem o conteúdo dos saves.
- Permanecer ligado ao carregar, valor registrado: `{device['stay_on']}`.

Relatório Android: [{device_file.name}]({device_file.as_posix()}). Captura: [{Path(shots[0]).name}]({evidence(shots[0]).as_posix()}). Vídeo: [{Path(device['video']).name}]({evidence(device['video']).as_posix()}). Registro completo: [space3d-build.json]({(P / 'space3d-build.json').as_posix()}).

## Limites e origem

Execução de jogos, downloads, saves e teste térmico/bateria prolongado não foram comprovados por esta verificação. Aprovação visual final cabe ao usuário.

Modelo-base: {model.get('source', '')}, commit `{model.get('source_commit', '')}`, licença {model.get('license', '')}. Autores, avisos e fontes correspondentes permanecem no APK. A autoria original da geometria não é nossa; regras dos materiais privados não restringem a licença do modelo.
'''
    section = f'''

## F-16 — revisão das inscrições e movimento, {now}

Este registro substitui conclusões anteriores sobre a revisão instalada. APK SHA256 `{apk_hash}`, {apk.stat().st_size} bytes; instalado em {device['installed_at']} no aparelho {device['device']}. {installation} Hash instalado igual ao local, certificado v2/v3 conferido, módulo nativo e {len(license_names)} avisos/fontes iguais ao APK.

- Duas inscrições laterais completas e separadas, proporção 8,21:1. Nuvens por volume (64 amostras, alvo320×180) sob a interface; névoa distante e estrelas com velocidade sincronizada. A pedido do usuário, voo sempre visível e avanço constante; foram removidos o desaparecimento, a entrada no hiperespaço e a aceleração das nuvens/estrelas. Ponto de fuga (0,65;0,32) compartilhado por constantes nativas e uniformes. A composição nativa move/redimensiona o resultado 3D; os shaders continuam animando casco/bocal/jato. Não é simulação física de voo nem vídeo.
- {geometry}
- Android: inicialização, captura/vídeo e trecho de log sem falha fatal. {nav_text}
- Harness GLES2/GLES3 aprovados nesta revisão dos fontes, sem erros GL e com restauração dos estados registrados. {perf_text}
- Integridade: {integrity['files_preserved']} entradas base preservadas, {len(integrity['added'])} adições, zero removidas; classes5.dex é a única entrada base alterada.
- ROM de referência tamanho/data: `{device['rom_size_mtime_preserved']}`. Valor stay_on: `{device['stay_on']}`. Não extrapolar para todos os jogos/saves; execução/download/save e estresse prolongado continuam sem comprovação nesta revisão.
- Consultar implementation/space3d-build.json, space3d/f16-device-validation.json e f16-turborama/RESULTADO-F16.md. Este registrador não altera backup, configuração do telefone ou arquivos do APK.
'''
    # Todas as conferências terminam antes de escrever a documentação.
    (P / 'space3d-build.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (F / 'RESULTADO-F16.md').write_text(content, encoding='utf-8')
    with (P.parent / 'HANDOFF-IMPLEMENTACAO-CARROSSEL-NATIVO.md').open('a', encoding='utf-8') as stream:
        stream.write(section)
    print(json.dumps({'registro': str(P / 'space3d-build.json'), 'apk_sha256': apk_hash,
                      'navegacao': navigation['status'], 'documentacao': str(F / 'RESULTADO-F16.md')},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
