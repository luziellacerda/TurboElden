## Atualizacao de integracao e login - 03/10/2026

Candidato atual `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, 1.902.718.870 bytes. Inclui **Manter conectado**, preferencia privada que controla a entrada automatica; usa licenca + Keystore, nao guarda codigo de ativacao nem Bearer. Desmarcar exige toque em Entrar nas proximas aberturas, mantendo a ativacao existente. Servidor continua autorizando cada sessao. Estado de instalacao e conferencias no aparelho: `build/closure-validation.json` (Git: `evidence/closure-validation.json`).

Instalado em 03/10 12:27:01, hash conferido, acesso salvo retomado. Sessao/perfil/catalogo 200 (996 itens da rede); capas 404 STATION_COVER_NOT_FOUND e autorizacao 404 STATION_ITEM_NOT_FOUND. Tela durante carga restaurada a 0. Checkbox compilado/instalado; alternancia individual na UI ainda nao conferida.

255 verificacoes locais aprovadas e 28 da ponte nativa no Android. Aliases do servidor integrados, inclusive Mega Drive BR; 1816 itens sinteticos assinados conferidos sem corte. Reuso por hash/tamanho assinados de arquivos anteriores, isolamento de recibos invalidos e diagnostico numerico sem dados pessoais adicionados. Os testes sinteticos nao comprovam conteudo publicado.

A revisao intermediaria eaebf48b foi instalada e confirmou sessao/perfil/catalogo 200, **996 itens frescos da rede**, capas 404 e autorizacao de download 404. Nenhum jogo chegou a transferencia. Ler `RETORNO-APP-FECHAMENTO-STATION-20261003.md` (Git: `docs/server/RETORNO-APP-FECHAMENTO-STATION-20261003.md`) para tarefas EXATAS do servidor e limites do cliente. Retorno do servidor 64912e1f continua declarando candidata NAO implantada. Ainda faltam capa 200, download/instalacao/jogo/retorno reais, acervo conciliado e eliminacao fisica integral do legado nativo. Nao promover a estavel nem declarar implementacao total concluida.

Registros anteriores abaixo sao historicos; seus hashes nao identificam o candidato atual.

# Handoff técnico da reconstrução TurboStations

## Verificacao no aparelho em 03/10/2026, 10:07 - carregamento corrigido

APK atual `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, SHA256 `43670211fe6de01438c0352b44875c43336c052d431582032680fa2c9265517f`, 1.902.702.486 bytes. Instalado com atualizacao -r, hash do base.apk identico, lastUpdateTime 10:07:58. Licenca salva reutilizada sem redigitar o codigo. Nao promovido a estavel.

Causa observada do loading: `StationFrontend.configure` recusava `Symbolic path refused`. Raizes confiaveis do contexto Android e do diretorio nativo agora passam por `toRealPath` antes dos controles de descendentes. O root nativo nao mudou na canonicalizacao; a raiz privada do Android deixou de provocar a recusa. Links simbolicos dentro da instalacao continuam rejeitados. Quatro testes Android isolados confirmaram raiz canonica, criacao normal, recusa de redirecionamento e ausencia de escrita fora da pasta; 204 testes locais passaram.

O aparelho publicou e aplicou 996 itens, chegou a 100% e abriu as plataformas. A barra apresenta itens e bytes UTF-8 preparados para a interface, nao bytes transferidos pela rede. Corrigida a visibilidade dos TextComponents para o texto nao ficar sobre o carrossel depois da conclusao. Captura final conferida. Tela ligada durante a carga restaurada ao valor anterior 0.

Contagem divergente relatada pelo mantenedor: espera mais de 800 SNES, mas existem 176 SNES e 28 SNES BR no catalogo recebido. As oito contagens no telefone coincidem exatamente com o handoff servidor ac869429 (996 total). Isso nao e corte do filtro SNES no cliente. Pedir catalogo completo ao servidor pelo novo handoff `docs/server/HANDOFF-SERVIDOR-CATALOGO-INCOMPLETO-STATION-20261003.md`. Nao preencher a lista com catalogo/CDN antigo nem inventar itemId/coverId.

Continuam pendentes: capa autenticada 200, descritor implantado e transferencia real, importacao verificavel dos jogos anteriores e eliminacao fisica do legado nativo residual. Inventario de dominios e evidencia estatica, nao captura de trafego. Fonte novo usa app.lzgames.com.br/v1/station; strings antigas ainda existem nas bibliotecas preservadas. Nao alegar migracao integral concluida.

Os registros abaixo sao historicos e nao substituem esta verificacao.

## Atualizacao posterior em 03/10/2026 - ativacao e carregamento

Codigo localizado no retorno privado `docs/senha-station-48h-20261002`, commit `01c391bea72dc27de8597e0c6d908caa96b18021`, arquivo `RETORNO-SENHA-STATION-48H-20261002.md`. O valor nao foi copiado para este handoff nem para logs. A pedido do mantenedor, foi inserido pela UI do telefone; o controlador concluiu o login e abriu ESActivity. O catalogo nativo permaneceu no indicador giratorio: ativacao aceita NAO significa frontend pronto.

Foi corrigida a publicacao pendente para usar o vetor que o GuiStore realmente observa. Foi adicionada barra desenhada no renderer nativo, com contagem de itens preparados e bytes UTF-8 preparados para a interface. A animacao e limitada ao trabalho concluido, e 100% depende do commit do modelo. Nao e percentual por tempo nem contagem de bytes baixados de jogos. Falhas mostram estado interrompido e diagnostico de etapa. Ainda falta confirmar visualmente o resultado no aparelho desbloqueado e fechar a causa do bloqueio inicial; nao declarar corrigido so pela compilacao.

Candidato instalado: `ae78dab6ab0eebda5ab872c6be4d2e293237010a65f02c4c3cbc1eaa064cc13e`, mesmo caminho de saida, 1.902.702.486 bytes, lastUpdateTime Android `2026-10-03 09:36:34`. Instalador retornou Success; hash no telefone desta revisao conferido e identico ao APK gerado. Tela permanece bloqueada; validacao visual pendente. O candidato anterior 38e78fde saiu do login mas ficou no loading. Sao agora 32 entradas nativas substituidas. Testes: 204 locais, 28 nativos do frontend; carga ELF com consulta do simbolo da pasta passou. Codigo e licenca do telefone foram preservados.

Novo retorno do servidor lido: `43bb54847e55750be451b614bcf827fb32ad7de4`, mesmo ramo `feat/station-artifact-descriptor-20261002` e mesmo handoff tecnico unico. Acrescenta homologacao HTTP isolada e correcao `de08858eac95084c116f146b642acd8748b43c35` na ordem de consumo do grant. Continua declarando descriptor NAO implantado e capas reais pendentes. Nao alterar a 5192 como consequencia desta leitura.

## Integracao do APK em 03/10/2026 - estado mais recente

Candidato completo gerado: `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, 1.902.702.486 bytes, SHA256 `38e78fde7dce574969aadeab2cd709b32df12b94bcd819fe595bd079af8204d2`. Nao e versao estavel. Instalacao e validacao autenticada devem ser confirmadas pelo registro de aparelho mais recente; a geracao do pacote nao comprova login real.

Instalacao Android concluida em 03/10/2026, lastUpdateTime 09:18:57. SHA256 do base.apk instalado conferido: 38e78fde7dce574969aadeab2cd709b32df12b94bcd819fe595bd079af8204d2. LoginActivity abriu sem falha no buffer de crashes consultado. Usuario foi solicitado a digitar o codigo diretamente no aparelho. Ativacao real ainda aguarda resultado.

### Aplicativo efetivamente integrado

- Quatro DEX substituidos: classes5 (ciclo de vida/servico), classes6 (autorizacao SDL), classes8 (retirada do auth/catalog antigo), classes28 (cliente Station novo no lugar de GameDownload). LocalPassword, AuthSession, LocalCatalog, HttpBridge, StationTransfer e GameDownload antigos foram removidos, incluindo referencias de tipos nos DEX. Nenhuma classe nova duplicada.
- `libstation_frontend.so` conecta o CatalogService nativo aos comandos por itemId do cliente Station. Nao fabrica URL e nao intercepta cliques. `libstation_archive.so` instala ZIP/RAR/7z usando libarchive. Sessao, perfil, catalogo, capas e grants usam exclusivamente as rotas Station no cliente reconstruido.
- `libmain.so` teve 31 implementacoes de entrada de servicos substituidas por ligacoes ao fonte novo. Os 4.409 enderecos dos simbolos originais foram mantidos porque o renderer/carrossel depende desse layout. Isto e integracao binaria verificavel; NAO significa que o C++ completo original foi recuperado ou recompilado.
- Restam rotinas antigas sem uso demonstrado no frontend atual dentro do binario nativo (incluindo scrapers historicos e ponte HTTP). As entradas ativas de catalogo/licenca/telemetria foram substituidas, mas a eliminacao fisica integral de todo o legado nativo ainda nao foi concluida. Nao apresentar essa entrega como reescrita integral limpa.
- Removido `assets/turboretro/catalog.json`. Nao existe retorno automatico ao catalogo antigo se o servidor falhar. Recursos de design, motores, demais DEX e manifesto foram preservados; 10.803 entradas comparadas por SHA256. Assinatura igual a base, alinhamento 16 KiB verificado.
- Historico de uso local preservado; sem consulta de IP ou telemetria remota antiga. Downloads usam servico em primeiro plano apenas enquanto ativos, fila limitada e eventos. Capas persistem por ID/revisao; trabalho de capas e suspenso quando a interface fica oculta.

### Evidencias e limites

204 verificacoes locais (19 arquivos, 68 protocolo, 36 cache/sessao, 20 coordenacao, 61 instalacao). No Android: 26 verificacoes sinteticas da ponte nativa; oito de leitura segura de arquivos; carregamento ELF e compatibilidade ABI aprovados. `build/apk/apk-report.json`, `build/device-integration-results.json` e `build/test-results.json` registram as evidencias. Isso nao substitui ativacao, capa 200, download real e retorno de um jogo.

Jogos e saves anteriores nao sao apagados. Jogos antigos fora de `.station-v2` ainda nao sao importados para os novos recibos: falta correspondencia verificavel entre IDs do servidor e arquivos existentes. Nao associar por aproximacao de nome nem indicar tudo como instalado. Geracoes antigas de uma atualizacao bem-sucedida sao preservadas; limpeza controlada de versoes substituidas ainda e pendente. Remocao interrompida agora usa recibo com `removing=true`, permitindo repetir a operacao sem declarar instalacao valida.

### Responsabilidades do servidor (Servidor-pix, somente canal Station)

Ultimo retorno lido: `feat/station-artifact-descriptor-20261002`, `9c0d9d5dab83ad1037009e5150fb4174fcddcbd6`, arquivo `docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md`. Contrato implementado em `96326aa0aeb164820cec26f8b5911fcdb47fc8ee` e `1bfb619c21becffe40aaa597e100fcb3719c2e72`. Nao assumir implantacao porque o servidor foi religado. Comprovar descriptor assinado em producao e arquivos do indice, capa autenticada 200 e transferencia integral. O cliente recusa grant sem artifact/itemRevision e nunca volta ao CDN antigo.

`STA-` e prefixo de licenseId. O codigo de ativacao e Base64URL canonico de 32 bytes (43 caracteres). O usuario possui o codigo e o digitara no telefone; nao solicitar segredo pelo chat. Nome vem de /me. Nenhum servico Linux foi alterado.

### Receita exata, executada na raiz E:

1. `prepare_test_dependency.py`, `run_tests.py`, `build_module.py`.
2. `build_archive.py`, `build_frontend.py` (JDK17, SDK34, NDK r28c nos caminhos dos scripts; bibliotecas oficiais verificadas por hash).
3. `prepare_dex_input.py`: extrai/descompila DEX da base d8104343, nunca da arvore Java realocada obsoleta.
4. `link_native_services.py` (requer LIEF apenas para leitura/metadados), `build_app_dex.py`, `package_apk.py`.
5. Rodar fixtures nativas no Android; instalar apenas o candidato com assinatura igual usando atualizacao -r. Nao desinstalar, limpar dados ou sobrescrever o APK de entrada/estavel.

Raiz canonica: `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`. Base: `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk` (d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b). Git: TurboElden, ramo `station-reconstrucao-20261002`, pasta `versions/station-reconstruction-20261002`. Nao mover referencias estaveis nem publicar APK, ROM, BIOS, firmware ou credenciais no Git.

As secoes abaixo sao historicas. Onde disserem modulo isolado, 142/202 testes ou APK ainda nao gerado, prevalece este registro.

## Atualização confirmada em 03/10/2026 — prevalece sobre o estado histórico abaixo

Retorno lido: Servidor-pix `feat/station-artifact-descriptor-20261002`, commit `9c0d9d5dab83ad1037009e5150fb4174fcddcbd6`. Código do contrato: `96326aa0aeb164820cec26f8b5911fcdb47fc8ee` e `1bfb619c21becffe40aaa597e100fcb3719c2e72`.

- Correção da interpretação anterior: `STA-` identifica **licenseId**. O código digitado pelo comprador é Base64URL canônico de 32 bytes (43 caracteres). `StationApi.token(code)` já estava correto; não flexibilizar a validação por causa do texto antigo.
- `itemRevision` e `artifact` são agora contrato confirmado no código do servidor, com fileName, sizeBytes, sha256, format, launchPath, expandedSizeBytes e fileCount. A implantação e o índice de produção continuam pendentes no último retorno.
- Fontes locais consomem o descritor assinado, validam SHA256 antes de extrair e publicam um manifesto somente após instalação completa. ZIP, RAR e 7z usam libarchive nativa. O catálogo nativo e o APK integrado ainda não estão concluídos.
- Última execução local: 202 verificações passaram e os fontes compilaram para Android API 34. Leitor nativo Android: oito verificações sintéticas passaram (ZIP, 7z, RAR5 e recusas de arquivos inseguros/cancelamento). Isso não comprova download autenticado de produção.
- Consulta pública após o usuário informar reinício: `/v1/station/catalog` retornou 401 JSON `STATION_SESSION_INVALID`, sem credenciais. `/ready/station` no domínio público retornou HTML do portal; não usar esse 200 como prontidão da API. O handoff usa essa sonda apenas localmente no servidor.
- Nenhum APK instalado nem serviço Linux alterado nesta implementação. Ainda é necessário retirar os fluxos antigos, integrar a interface e testar com sessão real antes de liberar.

O restante é o registro histórico de 02/10/2026; propostas e pendências antigas devem ser confrontadas com esta atualização.


## Estado atual

Este documento orienta a continuação do APK TESTE `org.turboramastation.frontend`. O cliente Station foi reconstruído em fonte Java, compilado para Android e testado localmente. **O login foi conectado ao cliente nos fontes e compilado. A ligação do catálogo nativo e o empacotamento em um APK novo continuam pendentes. O APK atual ainda contém as conexões antigas.**

A reconstrução está em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`. Os fontes novos ficam em `src\java\org\emulationstation\frontend\station`. A biblioteca compilada fica em `build\station-client.aar`; `build\dex\classes.dex` contém somente esse módulo. Não instalar esse DEX isolado nem simplesmente anexá-lo ao APK: isso manteria os dois clientes e não atenderia à substituição solicitada.

## Escopo e autorização

O mantenedor autorizou descompilar o que for necessário, recriar o código indisponível e criar/executar testes locais. O trabalho é somente no TurboStations. Os outros aplicativos Turborama e o servidor não foram modificados. As compilações, ferramentas e temporários desta reconstrução estão em E:.

## Fontes de verdade

| Evidência | Identificação |
| --- | --- |
| APK de entrada | `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk` |
| SHA256 da entrada | `d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b` |
| Tamanho da entrada | 1.898.675.776 bytes |
| Código das rotas Station | Servidor-pix `origin/feat/station-library-grant-20261002`, `b1159c9` |
| Última auditoria de produção consultada | Servidor-pix `origin/docs/auditoria-producao-station-20261002`, `07b4cab` |
| Identificadores de plataformas no catálogo vivo documentado | Handoff do servidor `ac86942`, oito plataformas e 996 itens |
| Git do aplicativo | Local `34d53ae`, remoto `versao-funcional` `0544607`, conforme auditoria inicial |

Todos os ramos do servidor foram atualizados para leitura com fetch nesta rodada. A auditoria 07b4cab relata 48 respostas 404 de capa, nenhuma capa 200 e nenhuma transferência completa de jogo comprovada. Esses números são do documento do servidor; não são novas medições feitas por este cliente.

O código do servidor, e não uma descrição antiga do handoff, confirmou: challengeId e sessionId são 64 caracteres hexadecimais; nonce, token e grant são Base64URL canônicos de 32 bytes; os erros usam a propriedade `code`.

## Componentes reconstruídos

| Fonte | Responsabilidade implementada |
| --- | --- |
| `StationApi` | Ativação, prova assinada pelo aparelho, abertura de sessão, perfil, catálogo, capa, autorização e download para área temporária. Confere assinatura RSA PSS, domínio, produto, aplicação, aparelho, licença, sessão e correspondência do challenge. |
| `StationHttp` | HTTPS com confiança do Android, verificação de hostname e pin SPKI. Somente as rotas Station enumeradas; sem redirects, sem fallback e sem URLs fornecidas pelo catálogo. Fecha conexão em sucesso, falha ou cancelamento. |
| `StationCrypto` | Reutiliza o alias Android Keystore `turborama.station.device.v1`. A chave privada não é exportada. |
| `StationSessions` | Um proprietário da sessão, token somente em memória, renovação sob demanda 15 segundos antes da validade de 180 segundos. Reutiliza `no_backup/station-license-id.txt`. Nenhum polling periódico. |
| `StationCatalog` | Modelo imutável com os cinco campos reais do servidor. Não fabrica URL nem extensão. Limite de 4096 itens, conforme StationLibrary. |
| `StationCatalogStore` | Guarda o envelope assinado de maneira atômica; releitura verifica assinatura e identidade. Cache é dado de exibição e exige uma sessão válida; nunca concede login. Rejeita queda de revisão. |
| `StationCoverStore` | Cache persistente por coverId e revisão, reaproveitamento de arquivo validado, limite entre requisições, espera após 429 e supressão temporária de 404 repetido. Não baixa capas no construtor. |
| `ExistingCoverCache` | Migração somente de leitura do cache anterior `station-covers/revisions.tsv` e imagens cuja revisão confere. Não apaga o arquivo anterior. |
| `StationFiles` | Arquivo parcial exclusivo, validação de tamanho, SHA256 calculado, hash esperado quando fornecido, sincronização e publicação atômica. Erro ou cancelamento preserva o destino anterior. |
| `StationPlatforms` | 50 mapeamentos locais comprovados e oito aliases do catálogo documentado no servidor. Plataforma desconhecida não vira pasta por aproximação. |
| `StationAndroid` | Composição real das dependências Android; valida dimensões e decodificação de capas com BitmapFactory. |
| `StationCoordinator` | Coordena o login, perfil, catálogo, cache, capas e autorização; negação da licença retira a autorização da interface. |
| `auth/LoginActivity` e `auth/StationLogin` | Layout atual ligado ao controlador, consulta fora da thread visual, retomada da licença salva, cancelamento ao destruir a tela e retirada da senha local nos fontes reconstruídos. |

O limite do envelope de catálogo foi elevado para 12 MiB para acomodar os 4096 itens máximos com textos Unicode escapados e Base64URL; capas continuam limitadas a 5 MiB, conforme servidor. O catálogo vivo documentado de 996 itens não é o limite contratual.

A busca estática no fonte novo não encontrou Squareweb, Miami, drawers, LocalPassword, LocalCatalog, GameDownload ou `station.invalid`. Isso comprova a ausência no **módulo novo**, não a retirada desses componentes do APK atual.

## Testes e limites da evidência

`build/test-results.json` registra os resultados e hashes dos fontes. A última execução completou:

- 19 verificações de gravação, integridade, cancelamento e preservação do destino.
- 68 verificações de protocolo e catálogo, com autoridade RSA criada somente para os testes.
- 36 verificações de sessão, cache, migração de capas e mapeamento de pastas.
- 19 verificações de integração entre login, perfil, catálogo, capas, renovação e bloqueio.
- Compilação contra Android API 34 em bytecode Java 8.
- Geração de DEX com API mínima 26 e biblioteca AAR.

Total: **142 verificações locais**. As respostas dos testes são controladas em memória e seguem os campos lidos no servidor. Isso não é teste autenticado contra produção. O caminho BitmapFactory foi compilado, mas não executado no Android nesta rodada. Não houve medição de desempenho de GPU ou alteração dos emuladores.

O telefone voltou à USB durante a rodada. O pacote instalado informa versão `1.0.8-turboeden-unico`, código 11, última atualização em 02/10/2026 às 16:47:06 e cerca de 2,9 GiB livres. O Android recusou `run-as` porque o pacote não é depurável; dados privados não foram lidos. Nenhum APK foi instalado nem jogo encerrado nesta rodada.

## Recuperação nativa

Foi analisada uma cópia exata de `libmain.so` do APK de entrada, SHA256 `a1ae357dc29caac52d47386a71a0a9a685ecffb9c01d536f5af50b5ba658cda8`. Ghidra produziu 455 saídas de funções, incluindo thunks, sem falhas de descompilação. Isso é pseudocódigo de análise, **não o projeto C++ original nem fonte diretamente recompilável**.

Os arquivos estão em `decompiled`, com `functions.tsv` e `references.tsv`. O projeto Ghidra e os logs foram preservados. Os endereços da saída Ghidra têm base de imagem 0x100000 adicionada; para confrontar com `native_carousel.cpp`, subtrair essa base.

Foram recuperadas as responsabilidades de CatalogService, CatalogItem, GuiStore, LicenseService, TelemetryService e ponte HTTP. O renderer e os motores continuam no binário original. `native_carousel.cpp` também depende de endereços e layout desse binário; recompilar somente esse arquivo não recompila GuiStore.

### Dados recuperados para orientar o código novo

`CatalogItem` ocupa 0xe8 bytes no arm64 analisado. Os campos string observados ficam em: id 0x00, nome 0x18, URL de jogo antiga 0x30, URL de capa antiga 0x48, rótulo de plataforma 0x60, pasta 0x78, nome de arquivo 0x90, caminho local 0xb0 e capa local 0xc8. Há flag de instalação em 0xa8. Os bytes finais 0xe0 a 0xe2 participam do estado de capa; seus significados individuais ainda precisam ser fechados antes de reproduzir o layout em código.

`CatalogService` ocupa 0x138 bytes. Foram observados estado em 0x50, vetor de itens em 0x88, revisão em 0xa8, contagem de instalados em 0xb0, vetor pendente em 0xd0, pedidos de capas em 0xe8, prioridade de capas em 0x100 e downloads ativos em 0x120.

| Função original | Endereço sem a base Ghidra | Uso na reconstrução |
| --- | --- | --- |
| refresh | 0x18f790 | Substituir origem do catálogo por snapshot Station direto |
| parseItems | 0x1904f0 | Eliminar leitura de gavetas e URLs antigas |
| adoptItems | 0x192778 | Publicação do catálogo para a interface |
| updateCovers | 0x192f10 | Conectar coverId ao caminho local validado |
| updateDownloads | 0x193cfc | Estado de transferência e instalação |
| applyPendingCatalog | 0x194924 | Momento seguro para trocar o modelo mostrado |
| refreshInstalledState | 0x194a60 | Reconciliar jogos existentes sem confundir parcial com instalado |
| startDownload | 0x1961ec | Autorizar itemId e instalar artefato confirmado |
| cancelDownload | 0x196a2c | Cancelar a operação e limpar somente seus temporários |
| uninstall | 0x196cd4 | Remover arquivos pertencentes ao jogo sem atingir saves |

A função antiga updateDownloads usa a existência do caminho para marcar instalação, inclusive após falha. O novo instalador deverá publicar um registro somente depois de validar e finalizar os arquivos. A troca do catálogo também deve manter o ponto seguro usado por GuiStore para não invalidar seleção, texturas ou downloads ativos.

## O que falta no aplicativo

1. Recriar o serviço nativo de catálogo e conectar suas ações ao cliente tipado, preservando o renderer e o design. A descompilação recuperou informações para isso; essa integração ainda não está implementada.
2. Empacotar a nova LoginActivity e ligar os controles de entrada/retorno da ESActivity ao mesmo proprietário da sessão. O login novo está compilado e conectado ao controlador nos fontes; LocalPassword e AuthSession antigos ainda estão no APK não alterado.
3. Implementar instalação e manifesto de arquivos com o descritor confirmado pelo servidor. O método atual novo `downloadToStaging` deliberadamente só baixa bytes; ele não cria entrada falsa em gamelist nem marca um jogo como instalado.
4. Remover as classes antigas e suas referências, os caminhos de rede de CatalogService, LicenseService e TelemetryService que pertencem ao frontend antigo. As conexões próprias dos motores devem ser auditadas separadamente.
5. Construir o APK completo, verificar classes e bibliotecas, testar no aparelho login, catálogo, capa, baixar, cancelar, jogar, apagar e voltar. Só então avaliar estabilidade.

## Dependências do servidor

O documento `HANDOFF-SERVIDOR-CONEXAO-E-INSTALACAO.md` descreve as informações ainda necessárias. O servidor entrega o jogo com Content-Length e tipo genérico, mas não fornece nome, formato ou hash assinado. Não existe fundamento para salvar todos os jogos como ZIP. Capas válidas também precisam responder 200 no índice do Linux.

## Reprodução e arquivos de build

Usar `prepare_test_dependency.py`, `run_tests.py` e `build_module.py`, nessa ordem. A dependência JSON de testes está fixada por SHA256 em `tools/json-dependency.json`; no Android é usado org.json da plataforma. Os scripts de edição de execução única na raiz são histórico da reconstrução e não fazem parte do build.

A máquina usa JDK 17, Python em `C:\Python314`, SDK em `G:\Android\Sdk` e D8 em `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar`. Nenhuma ferramenta foi instalada globalmente nesta rodada. Ghidra e JDK 25 portáteis estão em `tools`, com seus hashes em `tools-manifest.json`.

Não promover esta etapa como versão estável. O resultado entregue aqui é um módulo compilado e testado localmente, com integração do APK ainda pendente.

## Publicação do handoff no servidor

O pedido específico para a equipe do servidor está no Servidor-pix, commit 7ac4fad9e0132db378f6e78e6494fedb08f614c3, branch docs/cliente-reconstruido-station-20261002, arquivo docs/station-android/HANDOFF-CLIENTE-RECONSTRUIDO-STATION-20261002.md.

[Handoff do servidor com tarefas, responsáveis e formato de retorno](https://github.com/luziellacerda/Servidor-pix/blob/7ac4fad9e0132db378f6e78e6494fedb08f614c3/docs/station-android/HANDOFF-CLIENTE-RECONSTRUIDO-STATION-20261002.md).

A revisão separa o que existe do que é proposta, identifica exatamente produto/aplicação/pacote/rotas e solicita o retorno em docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md. Nenhum serviço Linux ou APK foi alterado nesta revisão documental.

Foi identificada uma pendência adicional no código do cliente 0840028: StationApi.activate exige Base64URL de 32 bytes para o código do comprador, enquanto o handoff humano descreve o formato STA-. A equipe Android deve corrigir essa validação de acordo com a emissão e o contrato reais confirmados pelo servidor. Os 142 checks anteriores não comprovam a aceitação desse formato comercial. A revisão documental não mudou fontes Java nem executou novamente os testes.
