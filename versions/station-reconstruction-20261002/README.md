# TurboStations - cliente Station integrado em APK candidato

APK TESTE gerado, assinado e instalado em 03/10/2026. SHA256 instalado: `38e78fde7dce574969aadeab2cd709b32df12b94bcd819fe595bd079af8204d2`. Login aberto; ativacao autenticada, catalogo/capas e download de producao ainda aguardam validacao. **Nao e versao estavel nem entrega aprovada ao consumidor.**

## O que foi integrado

Quatro DEX substituem login local e clientes antigos; o cliente Station recebe sessao/perfil/catalogo/capas e descritor assinado do jogo. Servico nativo liga as acoes do carrossel aos IDs reais. Instalador verifica tamanho/hash, extrai ZIP/RAR/7z, publica recibo atomico e remove somente seus arquivos. Cancelamento/falha preservam a instalacao anterior. Servico de download opera somente durante trabalhos ativos.

31 entradas de servicos de libmain foram substituidas. Renderer e carrossel continuam binarios originais; os enderecos exigidos pelo layout foram preservados. Rotinas nativas historicas sem uso no frontend atual ainda existem. **Nao alegar fonte C++ integral recuperado nem eliminacao fisica completa do legado.**

## Documentacao e evidencias

- [Handoff do aplicativo, pastas e limites](HANDOFF-RECONSTRUCAO-TURBOSTATIONS.md).
- [Contrato e responsabilidades do servidor](HANDOFF-SERVIDOR-CONEXAO-E-INSTALACAO.md).
- [Manifesto do APK](evidence/apk-report.json): 10.803 entradas preservadas por hash, mesma assinatura, manifesto inalterado.
- [204 verificacoes locais](evidence/test-results.json).
- [26 verificacoes nativas de frontend, oito de arquivos e carga ELF](evidence/device-integration-results.json).
- [Retorno do servidor](https://github.com/luziellacerda/Servidor-pix/blob/9c0d9d5dab83ad1037009e5150fb4174fcddcbd6/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md).

## Reproducao local

Trabalhar na raiz `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`. Python3, JDK17, AndroidSDK34, NDKr28c, CMake/Ninja, apktool3.0.3, build-tools35.0.0 e LIEF (metadados ELF). Caminhos exatos nos scripts. APK privado de entrada e Keystore original obrigatorios; o Git nao contem binarios privados.

1. `prepare_test_dependency.py`, `run_tests.py`, `build_module.py`.
2. `build_archive.py`, `build_frontend.py`.
3. `prepare_dex_input.py`, `link_native_services.py`, `build_app_dex.py`, `package_apk.py`.
4. Fixtures Android em `prepare_archive_device_test.py` e `prepare_frontend_device_test.py`; teste de carga em `tests/native_link_smoke.cpp`.

Saida: `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`. Nao executar finalizadores historicos. Nao anexar apenas o DEX ao APK antigo. Nao alterar referencias estaveis.

## Pendencias reais

Comprovar producao do descriptor e das capas no servidor. Validar ativacao no telefone. Resolver importacao verificavel dos jogos antigos para IDs/recibos Station (os arquivos foram preservados, mas nao sao reconhecidos por adivinhacao). Encerrar retirada do legado nativo residual e limpeza segura de geracoes substituidas antes de declarar migracao integral concluida. Nenhum servico Linux foi alterado.
