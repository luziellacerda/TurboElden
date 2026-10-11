# Cruzamento dos três últimos retornos reais do servidor — R117

O retorno foi lido no clone existente do Servidor-pix, na branch `origin/feat/station-online-all-platforms-20261009`, commit `141b488d6ad7fd3d2c8e74e76c1a004f1cb257fc`. Os três retornos atualizam **o mesmo handoff** `docs/station-android/HANDOFF-ONLINE-PLATAFORMAS-STATION-20261009.md`; não são três contratos diferentes nem pedidos APP → SERVIDOR. O aplicativo usa a fonte completa da R116 como base da R117, preservando as correções posteriores de cache, carregamento, identidade e consumo.

## Retornos e resultado do cruzamento

| Commit do servidor | Retorno real | Exigência para o aplicativo |
|---|---|---|
| `141b488d6ad7fd3d2c8e74e76c1a004f1cb257fc` | Capas PS2/PSP/Wii/Wii U atualizadas pelo catálogo hospedado. Recibo `capas-site-ps2-psp-wii-wiiu-20261010.json`. Catálogo 33, 3.940 IDs, 3.685 visíveis; 36 capas alteradas, item revision 33. | Atualizar o catálogo autenticado `catalog?metadata=1`; conservar itemId/coverId e invalidar somente a imagem da revisão antiga. A chave `coverId + item.revision` já existe na R116. Nenhuma arte deve ser associada pelo nome/posição ou embutida novamente no APK. |
| `5f9c019b6c87429f5cff2602701b29859acb1089` | Publicação de 36 Sega 32X e nove PSP; catálogo 32 e 45 capas. Recibo `sega32x-psp-publicados-20261010.json`. Limpeza do servidor é um recibo independente de manutenção. | Mappings `sega32x`/`psp` e descritores raw/ZIP já existem. PSP usa CSO bruto e 32X o launchPath `.32x` assinado. `metadata.players` não libera vagas online. Não transformar o relato de catálogo em motor PSP/32X online disponível. |
| `6dbc9e2f9efb13e7dd1d95b6884457fec293beca` | Publicação da auditoria de endpoints e ativação do código `7eb0e009d40ce01db86aea9c489937e9bd2fd00a`. Recibo `endpoint-review-20261010.json`. | Incorporar paginação v3, cursores separados de salas/pessoas, consultas com recuo após falhas transitórias, e sinopses de sala pelo itemId. Conciliar com a Activity atual e com os modelos R116; substituir a Activity inteira pela candidata de 212 fontes perderia correções posteriores. |

As referências de catálogo 31/32 e os números 3.895/3.640 em seções históricas do handoff identificam publicações anteriores. A revisão vigente declarada pelo retorno mais recente é **33 / 3.940 / 3.685**, com 255 aliases. O contrato `roomPresentation` ainda registra os números históricos da coleta de sinopses na revisão 31; não são uma nova contagem das descrições da revisão 33.

## Código do servidor conferido

Estas linhas referem-se ao código no commit `141b488d6ad7fd3d2c8e74e76c1a004f1cb257fc`:

- `src/TurboRamaSuiteOnlineServer/StationMultiplayer.cs:16`: `StationMultiplayerCommand` aceita Page 0 e RoomPageSize 100 por padrão, mantendo compatibilidade. Linha 152 valida page 0..40 e tamanhos 32/100. `View`, linhas 236–257, devolve page, roomPageSize, nextPage e totalRooms; a própria `room` independe do recorte. O limite máximo considerado da lista permanece 100 salas.
- `StationMultiplayer.cs:247` e `:254`: `platformPolicy.serverReady` e `serverPlatforms` são capacidades do servidor. `onlineAvailable` depende do perfil/motor real e não pode ser fabricado pelo cliente.
- `src/TurboRamaSuiteOnlineServer/StationOnline.cs:246` e `:247`: nextPeerPage e nextRoomPage independentes; o nextPage legado também permanece. Linha 248 considera a presença v3 mesmo fora da página visível.
- `src/TurboRamaSuiteOnlineServer/StationLibraryMonitor.cs:8`, `:10`, `:16` e `:18`: carimbo do catálogo carregado e recarga serializada por reloadGate. Linha 29 mantém a versão anterior por 120 segundos para grants em andamento.
- `StationMultiplayerEndpoints`, `StationOnlineEndpoints` e `StationEndpoints`: timeouts anteriores ao upgrade/capas recebem JSON 504 com código correspondente; cancelamento do chamador não produz uma nova resposta; capas desaparecidas recebem 404 `STATION_COVER_NOT_FOUND`. Essas mudanças já pertencem ao servidor, sem necessidade de reproduzir tratamento de serviço no Android.

O recibo declara DLL `2c0d034476969cbed58b519b744e841111373f89a4bcd6abb9cd14543abcde35`, PID 2136303, sem novo restart nas publicações de dados, e ativação da revisão de endpoints em `2026-10-10T21:49:22.368044+00:00`. Isso é **evidência do recibo do operador**, não uma nova leitura ao vivo do processo Linux feita nesta tarefa.

## Modelos conciliados na R117

- `StationOnlineClient.java:11–12`: setters de peer page e room page separados, ambos validados entre 0 e 40. O campo `page` existente permanece o cursor de pessoas; `roomPage` passa a ser o cursor das salas v3.
- `StationOnlineClient.java:19`: requests v3 enviam `page:roomPage`, `roomPageSize:32` e `clientMaximumPlayers:5` compatível com o runtime atual.
- `StationOnlineClient.java:48`, `:54`: apresentação combina nextPeerPage/nextRoomPage com fallback legado e conserva o **page real de cada fonte**. Mantém `serverPlatforms` e `platformPolicy`, que a candidata remota de paginação omitira. Não modifica os snapshots assinados nem reutiliza a revisão local de apresentação como prova de requisição.
- `StationOnlineClient.java:75`: `pollRetryDelay` aceita somente as falhas transitórias especificadas para consultas: HTTP 408/429/500/502/503/504, Offline, SocketTimeoutException e SocketException. Recuo 1/2/4/8 segundos; Retry-After pode ampliar até 60 segundos; POLL_EXISTS fica em um segundo. 401/403, TLS, assinatura, JSON/identidade, cancelamento e serviço desativado permanecem terminais. O método não repete nenhuma ação por si só.
- `StationOnlinePlatformPolicy.java:16`: alias `ps2br` normalizado para `ps2`.
- `assets/station-online/engines.json`: acrescenta somente políticas explicativas PS2/Saturn pendentes e corrige a descrição do Switch. Os registros reais de motores/hashes/runtime permanecem preservados; não foi criado motor fictício para essas plataformas.

`StationApi.java` não exigiu substituição: `multiplayer`, linha 210, já valida resposta assinada e requestId; `catalogSnapshot`, linha 235, já pede metadata=1; os campos opcionais de página são aceitos. A candidata remota removia APIs de mídia e o tratamento `ArtifactNetworkFailure` do downloader atual, por isso a R116 foi preservada nesse arquivo. `StationMultiplayerProfile.java` é logicamente igual à candidata remota; valida perfil aprovado, edição, engine/runtime/core, allowedPlayerCounts, configuração canônica e vagas reais.

`StationOnlineGame` da R116 também é mais recente: conserva mensagens diferenciadas `single-player`, `content-identity-pending`, `mode-pending` e `online-engine-pending`, além de calcular identidade usando `contentIdentityScheme`. Substituí-lo pela candidata remota reverteria essas correções.

## Integração da tela

A Activity atual recebeu os fragmentos equivalentes ao contrato, conciliados pelo responsável da tela:

1. Reinicia o cursor correspondente em zero ao navegar entre Pessoas/Salas. Aplica setPeerPage/setRoomPage e busca a página solicitada; enquanto a fonte recebida tiver outra página, mostra consulta em andamento.
2. Renderiza paginação de pessoas com peerPage/nextPeerPage e de salas com roomPage/nextRoomPage. A própria sala continua disponível mesmo em uma página vazia.
3. Usa `pollRetryDelay` somente em heartbeat/events/snapshot, respeitando cancelamento e um único poll pendente. Criar/entrar/pronto/iniciar/leave/chat não têm repetição automática.
4. Busca a sinopse em `client.item(itemId).description` do catálogo verificado já em memória: quatro linhas em Criar/Sua sala, duas nas outras salas, leitura completa por toque/Ver detalhes. Modo e instruções dos perfis permanecem em Como jogar. Nenhuma nova requisição por sala. Ausência de texto mostra `Sinopse ainda não cadastrada.`; catálogo indisponível, `Sinopse indisponível no momento.`.

O protocolo legado v1/v2 possui um único campo `page`: ao paginar salas legadas, o controle usa o cursor comum de heartbeat/events. Não afirmar independência que esse protocolo não oferece. No v3, `roomPage` é enviado somente à fonte multiplayer e o cursor de pessoas continua separado.

## Preservação de consumo e dependências reais

A indicação de “quatro workers atuais” no handoff foi escrita para a candidata antiga do servidor. Não é requisito criptográfico nem de protocolo. A fila única R116 de IO/decode Java, prioridades de capa visível, warmup limitado, cache persistente, lifecycle, vídeos locais e orçamento dos menus de 30 fps são preservados. Não restaurar a fila antiga de quatro workers para ler o catálogo 33.

O contrato continua exigindo adaptadores nativos reais para Dreamcast/GC/Wii/Wii U/Switch/PS2/Saturn conforme plataforma, controles e modo. PS2 Play!/LRPS2 não declara netplay upstream; Saturn exige adaptador Station e BIOS legítima. O patch de paginação/apresentação não resolve essas dependências nativas. A admissão continua baseada em perfil aprovado e allowedPlayerCounts, nunca no teto da plataforma ou em metadata.players.

## Verificação executada

`recipes/test_lobby_recovery_r117.py` compilou as classes reais modificadas contra as dependências R116 e executou **54 verificações**: cursores separados/fallback legado, snapshot imutável, identidade recusada, própria sala legada, status de presença, serverPlatforms/platformPolicy preservados, limites de página, PS2 BR e toda a matriz de recuperação/erros terminais, incluindo prioridade de 401/403 sobre qualquer código de erro. Resultado em `evidence/lobby-recovery-r117-tests.json`. Não é teste de UI Android/WAN/gameplay ou medida de aquecimento.

## Receita de compilação conciliada

`build.py` oferece fases explícitas `--prepare`, `--compile` e `--package`. A base é o APK R116 SHA-256 `3c5fb1cb84330b4cea635152e65b7498bf6baf15192371789945fcaf861226c1`; Java e os inputs nativos só são aceitos depois da atualização dos manifestos finais. As duas bibliotecas da interface (`station_frontend.cpp` e `native_carousel.cpp`) são recompiladas, junto dos módulos Java completos. Os sete objetos privados de mídia e os três stubs são conferidos contra `CAROUSEL-INPUT-MANIFEST-R116.json` congelado; não são publicados no Git. A receita recusa mudança de assinatura, perda de exports existentes e alinhamento menor que 16 KiB. O pacote final pode alterar somente dois DEX, duas bibliotecas da interface e a política `engines.json`; todas as outras entradas são comparadas integralmente por SHA-256, incluindo o runtime dos emuladores.

Os argumentos explícitos ficam em `recipes/build-r117-arguments.json`: temporários de compilação em E:, temporários do APK em G:. Nenhuma senha está incluída; a fase de assinatura exige variáveis de ambiente já fornecidas. A validação de sintaxe/argumentos passou. A execução posterior completa compilou as 230 fontes Java e as duas bibliotecas da interface; assinatura original e alinhamento de 16 KiB conferidos. Recibos: `evidence/build-r117.json` e `evidence/package-r117.json`. A instalação direta no Motorola e a conferência básica do carrossel/opções constam de `evidence/installation-motorola-r117.json` e `evidence/physical-smoke-r117.json`; não representam validação WAN/gameplay ou redução térmica.

## Identidade dos documentos lidos

| Arquivo do retorno vigente | SHA-256 |
|---|---|
| HANDOFF-ONLINE-PLATAFORMAS-STATION-20261009.md | `8d116e24b3d6ac480d43d07697d9dbd9d4a4297f977f4b9f22d9c24cf66d2f54` |
| server-integration-contract.json | `e777c3b8c9f40b40e5eae9046359a96e8562a5299359cb5e54f5be7a27033be6` |
| endpoint-review-20261010.json | `4ef78c81a846b3d114ad8fdb32bd46cd239df5ecfb959857590492fd292591f0` |
| sega32x-psp-publicados-20261010.json | `1da6ebd8bd5f59c1706a73b9396634876e6a8f0a3c527a5b6a38f585cd076a7b` |
| capas-site-ps2-psp-wii-wiiu-20261010.json | `524a355a40ac4bbd73dceddf09f6d577a067fcd1dc12f281475c3b47191205e0` |
