# Revisão integral Station — 03/10/2026 — entrada atual

Leia primeiro [HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md](../../docs/server/HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md) e [mapa/integridade](../../docs/server/revisao-app-20261003/APPENDICE-MAPA-E-INTEGRIDADE.md).

Branch `revisao-integracao-station-servidor-20261003`, runtime `629a55a8cf48722460007944cf0bb737e9f8fb75`. APK instalado atual: SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, pacote `org.turboramastation.frontend`. Fonte: `versions/station-reconstruction-20261002/`. Esta revisão publica documentação e evidências; não gera outro APK nem promove a estável.

Sessão/perfil/catálogo200; total996 registrado na rede.176SNES/28SNESBR são contagens da exportação nativa, não histograma HTTP capturado. Capas404 e autorização404 não têm causa definitivamente localizada: revisar também o cliente. Há14 achados/limitações no handoff; inclusive retry de capas, concorrência de sessão, plataforma desconhecida, limite4096, instrumentação e texto de erro conclusivo demais. Não afirmar que o app está correto por receber200/404.

O código novo convive com renderer/launcher binários preservados; eliminação física integral do legado e execução de jogo por instalação Station ainda não comprovadas. Preservar Keystore, licença, dados, jogos, saves, design e motores. Build/temporários somente E:. Pedido ao servidor é revisão de código e evidências; não é deploy automático.

**Os estados e hashes abaixo são históricos. Este bloco e o novo handoff têm precedência para identificar o candidato atual.**

## Atualizacao de integracao e login - 03/10/2026

Candidato atual `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, 1.902.718.870 bytes. Inclui **Manter conectado**, preferencia privada que controla a entrada automatica; usa licenca + Keystore, nao guarda codigo de ativacao nem Bearer. Desmarcar exige toque em Entrar nas proximas aberturas, mantendo a ativacao existente. Servidor continua autorizando cada sessao. Estado de instalacao e conferencias no aparelho: `build/closure-validation.json` (Git: `evidence/closure-validation.json`).

Instalado em 03/10 12:27:01, hash conferido, licenca salva retomada. Catalogo fresco 996; capas e downloads bloqueados por 404 do servidor. Ver evidencia closure-validation.json.

255 verificacoes locais aprovadas e 28 da ponte nativa no Android. Aliases do servidor integrados, inclusive Mega Drive BR; 1816 itens sinteticos assinados conferidos sem corte. Reuso por hash/tamanho assinados de arquivos anteriores, isolamento de recibos invalidos e diagnostico numerico sem dados pessoais adicionados. Os testes sinteticos nao comprovam conteudo publicado.

A revisao intermediaria eaebf48b foi instalada e confirmou sessao/perfil/catalogo 200, **996 itens frescos da rede**, capas 404 e autorizacao de download 404. Nenhum jogo chegou a transferencia. Ler `RETORNO-APP-FECHAMENTO-STATION-20261003.md` (Git: `docs/server/RETORNO-APP-FECHAMENTO-STATION-20261003.md`) para tarefas EXATAS do servidor e limites do cliente. Retorno do servidor 64912e1f continua declarando candidata NAO implantada. Ainda faltam capa 200, download/instalacao/jogo/retorno reais, acervo conciliado e eliminacao fisica integral do legado nativo. Nao promover a estavel nem declarar implementacao total concluida.

Registros anteriores abaixo sao historicos; seus hashes nao identificam o candidato atual.

## Verificacao no aparelho em 03/10/2026, 10:07 - carregamento corrigido

APK atual `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, SHA256 `43670211fe6de01438c0352b44875c43336c052d431582032680fa2c9265517f`, 1.902.702.486 bytes. Instalado com atualizacao -r, hash do base.apk identico, lastUpdateTime 10:07:58. Licenca salva reutilizada sem redigitar o codigo. Nao promovido a estavel.

Causa observada do loading: `StationFrontend.configure` recusava `Symbolic path refused`. Raizes confiaveis do contexto Android e do diretorio nativo agora passam por `toRealPath` antes dos controles de descendentes. O root nativo nao mudou na canonicalizacao; a raiz privada do Android deixou de provocar a recusa. Links simbolicos dentro da instalacao continuam rejeitados. Quatro testes Android isolados confirmaram raiz canonica, criacao normal, recusa de redirecionamento e ausencia de escrita fora da pasta; 204 testes locais passaram.

O aparelho publicou e aplicou 996 itens, chegou a 100% e abriu as plataformas. A barra apresenta itens e bytes UTF-8 preparados para a interface, nao bytes transferidos pela rede. Corrigida a visibilidade dos TextComponents para o texto nao ficar sobre o carrossel depois da conclusao. Captura final conferida. Tela ligada durante a carga restaurada ao valor anterior 0.

Contagem divergente relatada pelo mantenedor: espera mais de 800 SNES, mas existem 176 SNES e 28 SNES BR no catalogo recebido. As oito contagens no telefone coincidem exatamente com o handoff servidor ac869429 (996 total). Isso nao e corte do filtro SNES no cliente. Pedir catalogo completo ao servidor pelo novo handoff `docs/server/HANDOFF-SERVIDOR-CATALOGO-INCOMPLETO-STATION-20261003.md`. Nao preencher a lista com catalogo/CDN antigo nem inventar itemId/coverId.

Continuam pendentes: capa autenticada 200, descritor implantado e transferencia real, importacao verificavel dos jogos anteriores e eliminacao fisica do legado nativo residual. Inventario de dominios e evidencia estatica, nao captura de trafego. Fonte novo usa app.lzgames.com.br/v1/station; strings antigas ainda existem nas bibliotecas preservadas. Nao alegar migracao integral concluida.

Os registros abaixo sao historicos e nao substituem esta verificacao.

# TurboStations - cliente Station integrado em APK candidato

## Atualizacao posterior em 03/10/2026 - ativacao e carregamento

Codigo localizado no retorno privado `docs/senha-station-48h-20261002`, commit `01c391bea72dc27de8597e0c6d908caa96b18021`, arquivo `RETORNO-SENHA-STATION-48H-20261002.md`. O valor nao foi copiado para este handoff nem para logs. A pedido do mantenedor, foi inserido pela UI do telefone; o controlador concluiu o login e abriu ESActivity. O catalogo nativo permaneceu no indicador giratorio: ativacao aceita NAO significa frontend pronto.

Foi corrigida a publicacao pendente para usar o vetor que o GuiStore realmente observa. Foi adicionada barra desenhada no renderer nativo, com contagem de itens preparados e bytes UTF-8 preparados para a interface. A animacao e limitada ao trabalho concluido, e 100% depende do commit do modelo. Nao e percentual por tempo nem contagem de bytes baixados de jogos. Falhas mostram estado interrompido e diagnostico de etapa. Ainda falta confirmar visualmente o resultado no aparelho desbloqueado e fechar a causa do bloqueio inicial; nao declarar corrigido so pela compilacao.

Candidato instalado: `ae78dab6ab0eebda5ab872c6be4d2e293237010a65f02c4c3cbc1eaa064cc13e`, mesmo caminho de saida, 1.902.702.486 bytes, lastUpdateTime Android `2026-10-03 09:36:34`. Instalador retornou Success; hash no telefone desta revisao ainda precisa ser conferido. O candidato anterior 38e78fde saiu do login mas ficou no loading. Sao agora 32 entradas nativas substituidas. Testes: 204 locais, 28 nativos do frontend; carga ELF com consulta do simbolo da pasta passou. Codigo e licenca do telefone foram preservados.

Novo retorno do servidor lido: `43bb54847e55750be451b614bcf827fb32ad7de4`, mesmo ramo `feat/station-artifact-descriptor-20261002` e mesmo handoff tecnico unico. Acrescenta homologacao HTTP isolada e correcao `de08858eac95084c116f146b642acd8748b43c35` na ordem de consumo do grant. Continua declarando descriptor NAO implantado e capas reais pendentes. Nao alterar a 5192 como consequencia desta leitura.

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
