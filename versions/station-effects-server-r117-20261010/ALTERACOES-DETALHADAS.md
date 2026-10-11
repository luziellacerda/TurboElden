# R117 — alterações detalhadas e limites da conferência

## Base e escopo

A fonte parte da R116 publicada no commit `2c7132bc2e023a8f8e17c3c15d8bc59fbe72ba7d`. O APK privado usado como base da receita é a R116 SHA-256 `3c5fb1cb84330b4cea635152e65b7498bf6baf15192371789945fcaf861226c1`.

A R117 atende três frentes: conciliação dos retornos do servidor, apresentação progressiva dos LEDs e opções para reduzir o trabalho gráfico dos menus. As Activities atuais foram conciliadas; não foram substituídas por versões antigas nem pela implementação R100 rejeitada. A árvore Java contém 230 fontes: as 226 da base, com nove modificadas, e quatro novas. Os manifestos finais identificam os bytes de cada fonte; este documento não substitui os manifestos.

Este texto registra fontes, testes isolados e evidências disponíveis. O estado de compilação, assinatura, instalação, aprovação visual, medição térmica e gameplay pertence a `STATUS.json` e aos recibos R117 produzidos pelo responsável da entrega. Nenhuma instalação ou estabilidade física é afirmada aqui.

## 1. Conciliação dos três retornos reais

| Commit do servidor | Retorno lido | Efeito necessário no app |
|---|---|---|
| `141b488d6ad7fd3d2c8e74e76c1a004f1cb257fc` | Capas PS2/PSP/Wii/Wii U vinculadas ao catálogo hospedado, catálogo 33 e 42 capas conferidas | Consumir o catálogo autenticado atual pelos IDs/revisões já suportados; preservar o cache de capas e a fila única R116 |
| `5f9c019b6c87429f5cff2602701b29859acb1089` | Publicação de 36 Sega 32X e nove PSP, catálogo 32, arquivos raw e caminhos de lançamento | Preservar o protocolo de identidade por edição e o processamento já existente; metadados de jogadores não aprovam netplay por conta própria |
| `6dbc9e2f9efb13e7dd1d95b6884457fec293beca` | Auditoria de endpoints e recibo de rollout da fonte `7eb0e009d40ce01db86aea9c489937e9bd2fd00a` | Aplicar paginação, recuperação restrita às consultas e apresentação das sinopses sem novas requisições por sala |

Os três commits atualizam o handoff `docs/station-android/HANDOFF-ONLINE-PLATAFORMAS-STATION-20261009.md` e seus recibos. Não foram confundidos com pedidos APP → SERVIDOR. A conferência final executou fetch explícito de todos os ramos no clone já existente; as branches relevantes continuaram em `141b488...`, sem retorno novo. O registro sanitizado está em `evidence/server-last-fetch-r117.json`.

O recibo do operador declara catálogo 33, 3.940 IDs, 3.685 visíveis e 255 aliases, com DLL `2c0d034476969cbed58b519b744e841111373f89a4bcd6abb9cd14543abcde35`, PID 2136303 e ativação dos endpoints em `2026-10-10T21:49:22.368044+00:00`. Essas são evidências fornecidas pelo servidor; esta tarefa não consultou o processo Linux ao vivo, não implantou código e não reiniciou serviços.

### Paginação e consultas

- Pessoas mantêm o cursor `page`; salas v3 usam `roomPage` separado. Ambos aceitam 0 a 40. A consulta v3 envia `roomPageSize:32`, preservando a resposta assinada e o limite negociado `clientMaximumPlayers:5` já existente.
- A apresentação conserva `peerPage`, `roomPage`, `nextPeerPage`, `nextRoomPage`, `serverPlatforms` e `platformPolicy`. A revisão local de apresentação não se torna prova de requisição ou revisão do servidor.
- A própria sala continua disponível independentemente da página da lista. A fonte recebida precisa corresponder aos cursores solicitados antes de pintar a página; uma resposta antiga não preenche uma página nova.
- O protocolo legado v1/v2 possui um único `page`. Seu fallback usa o cursor comum de heartbeat/events ao paginar salas; o app não inventa independência que esse protocolo não fornece.
- Somente `heartbeat`, `events` e `snapshot` retomam em falhas transitórias: HTTP 408/429/500/502/503/504, Offline, SocketTimeoutException ou SocketException. O recuo é de 1, 2, 4 e até oito segundos; Retry-After é limitado a 60 segundos. POLL_EXISTS aguarda um segundo, mantendo uma consulta pendente.
- 401/403 têm prioridade terminal, mesmo se houver um código de erro transitório. Cancelamento, TLS, assinatura, JSON, identidade inválida e serviço desativado permanecem terminais. Criar, entrar, pronto, iniciar, sair e mensagens não ganham repetição automática.

### Sinopses e dados de sala

A descrição vem do item exato `client.item(itemId).description` no catálogo autenticado já em memória. Criar/Sua sala mostram quatro linhas; outras salas, convites e diálogos mostram duas, com leitura completa por toque. Perfil, vagas, modo e instruções continuam separados da sinopse, em Como jogar. Texto ausente mostra “Sinopse ainda não cadastrada.”; catálogo/item indisponível mostra “Sinopse indisponível no momento.”. Nenhuma nova chamada HTTP é criada para cada sala.

`StationApi.java` foi mantido: já valida envelopes/requestId e solicita metadata do catálogo. Substituí-lo pela candidata remota removeria APIs de mídia e o tratamento atual `ArtifactNetworkFailure`. `StationMultiplayerProfile.java` e `StationOnlineGame.java` também foram preservados, incluindo allowedPlayerCounts, identidade de conteúdo, configuração canônica e mensagens de disponibilidade mais recentes.

Os novos textos de PS2/Saturn e o alias `ps2br` não fabricam motores. `serverReady` e disponibilidade real do jogo são condições diferentes. Dreamcast/GC/Wii/Wii U/Switch/PS2/Saturn continuam dependentes dos perfis/adaptadores nativos reais definidos no contrato; jogadores informados no catálogo não autorizam abrir vagas extras.

## 2. LEDs: causa concreta e preparação progressiva

Na R116, o cálculo do campo estático respeitava quatro linhas por quadro, mas sua apresentação aguardava a conclusão integral. Uma altura de 960 linhas exige 240 quadros: aproximadamente oito segundos a 30 FPS. Isso explica o tempo de preparação do código, sem constituir medição física dessa revisão.

A R117 zera integralmente a textura candidata antes de publicá-la e prepara até quatro linhas por quadro em quatro faixas disjuntas. As faixas começam em regiões da moldura já medidas: y=565, 80, 1010 e 1454 no espaço da arte de 1536 linhas. No online, as sementes são ajustadas ao FIT_CENTER/letterboxing. As sementes ordenam o trabalho e não criam emissores onde a arte não possui luz.

Depois do primeiro pacote válido, o shader existente pode mostrar as regiões preparadas. Campo zero mantém a imagem base; regiões ainda não calculadas não precisam esconder a capa nem receber texels indefinidos. Cada linha termina sendo calculada exatamente uma vez, inclusive para alturas que não são múltiplas de quatro. O campo completo ainda pode exigir os mesmos oito segundos no exemplo; não há promessa de todas as luzes completas no primeiro quadro.

Há retenção de até três campos completos por contexto, limitada a 8 MiB adicionais. No online, o orçamento considera também os Bitmaps retidos. Ativo e candidato pertencem ao renderer atual e não fazem parte desse orçamento de retenção. Campos grandes não ficam guardados. Não há cache GL compartilhado entre carrossel e os workers online.

As chaves nativas incluem origem, identidade/revisão, modelo, dimensões e viewport. Upload, atualização/destruição da origem e mudança de catálogo invalidam os campos correspondentes. No online, Bitmap + getGenerationId, modelo e dimensões formam a identidade. Ao perder o contexto, nomes antigos são esquecidos; não são apagados no contexto novo. Desligar o LED cancela sua animação e libera seus recursos pelo caminho dono; religar prepara novamente a seleção atual.

### Qualidade e trabalho preservados

Os três arquivos que definem a matemática do efeito são idênticos aos arquivos publicados da R116:

| Arquivo | SHA-256 preservado |
|---|---|
| `native/d0/premium-magazine-led-android.glsl` | `8ec0c097d36cb5c82e4492d00335eda5fe59d2e3d205d10ef6a9845a9fb7ea61` |
| `native/d0/magazine_shader.h` | `71dc1dd7e1392b3ce4b0132dd0024161431ca76de9559d116f73dd74311bb23a` |
| `java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java` | `2e63f83cb14f20ce07a3854ce17ca7328438dfabf76de87daaa342778dbdfa4b` |

Brilho, ganho, halo, cabeça, rastro, velocidade e relógio do LED não são reduzidos. O campo nativo continua RGBA16F, e o online, RGBA8. Não foi introduzido cálculo monolítico, espera de conclusão GL ou retorno temporário ao kernel pesado no caminho otimizado. Quatro submissões curtas podem acrescentar algum custo de classificação/submissão; os testes isolados não demonstram redução térmica ou menor consumo medido.

O manifesto nativo congelado contém inputs de reconstrução herdados anteriores à fonte pública R116. Uma diferença contra esse manifesto, isoladamente, não significa que o shader foi alterado nesta entrega. A identidade acima foi conferida contra os arquivos publicados da R116; o manifesto congelado continua sendo a referência dos objetos privados de mídia/ABI usados na receita.

## 3. Efeitos gráficos e modo leve

O botão ao lado do seletor de tema alterna o desligamento geral. O estado geral não apaga as escolhas individuais: ao religar, são restaurados os efeitos que estavam selecionados. As preferências ficam em `station_graphics_r117`, com máscara individual, estado geral, fundo e revisão. O padrão é máscara 63, efeitos gerais ativos e modo Céu, preservando o visual normal da base.

Configurações ganha EFEITOS e um painel opaco com seis opções independentes:

| Opção | Bit | Quando desligada |
|---|---|---|
| LEDs das capas | 1 | Não prepara/anima os campos LED; a capa original continua visível |
| Vídeos do carrossel | 2 | Aposenta os decoders e mantém imagem/quadro estático |
| Fundo animado | 4 | Interrompe o movimento do céu ou das ondas |
| Ícones e Lotties | 8 | Mantém os ícones em quadro estático, sem seus callbacks de animação |
| Efeitos das células | 16 | Suspende brilhos/animações decorativas existentes dos botões/células |
| Transições visuais | 32 | Desativa as transições visuais abrangidas pelas opções dos menus |

O estado Java é imutável. A ponte JNI publica máscara, modo e revisão conjuntamente em um único snapshot atômico. A leitura nativa usa esse snapshot, sem JNI, IO ou escrita de preferências por quadro. Listeners e callbacks observam attach/detach, foco, visibilidade e lifecycle.

A revisão final encontrou um gesto EFEITOS pendurado quando Settings era fechado por Back entre DOWN e UP. O responsável corrigiu o reset em `requestSettingsClose`, `settingsClosedHook` e na mudança de owner. O teste extrai as funções reais e inclui o gesto de produção, verificando reabertura com novo ponteiro; ele não é um teste de toque físico no telefone. A fonte final deve ser distinguida da primeira compilação anterior a essa correção; a recompilação e seu recibo final pertencem ao responsável da entrega.

O painel oferece Céu, Ondas e Sem fundo. As ondas usam três faixas preenchidas simples, com objetos Paint/Path reaproveitados e gradiente reconstruído apenas na mudança de tamanho. O movimento só agenda quadros quando a opção está escolhida, a view está visível e tem foco. O caminho nativo usa faixas simples equivalentes. O padrão do online permanece o fundo estático existente; escolher Ondas ativa somente essa alternativa. Não se afirma que ondas tenham consumo zero ou ganho térmico medido.

Desligar os efeitos não interrompe downloads, mensagens, consultas autorizadas, navegação ou comandos de jogo. A interface continua podendo redesenhar quando necessário. Os menus mantêm o orçamento de 30 FPS; os callbacks Android abrangidos usam cadência de 34 ms. A taxa dos emuladores, sincronização da partida e entrada do controle não recebem esse limite dos menus.

## 4. Vídeos desligados sem células vazias

A revisão do caminho estático encontrou que retornar antes de desenhar o vídeo, enquanto a formação ocultava o JPG, deixaria as células escuras. A formação agora preserva o JPG quando VIDEO está desligado e o utiliza como segurança para GLES/programa/poster indisponível.

O caminho estático prefere o quadro retido. Quando ele falta, admite no máximo um poster já incorporado por quadro do menu, começando pela seleção; os demais surgem progressivamente sobre os JPGs. A proporção e a regra de cantos das coleções são preservadas.

Esse caminho não inicia MediaPlayer, não consulta capacidade, não atualiza SurfaceTexture e não faz rede. Um decoder que já existia continua encerrando pelo procedimento anterior. Depois de admitidos os posters, não há novos uploads no estado estático. Contexto incompatível ou recurso inválido mantém o JPG. Com VIDEO ativo, o trecho de preparação/reprodução permanece idêntico à R116 após o gate: resolução, FPS dos arquivos, UVs, matriz, passagem única e retenção dois quadros antes do final não são alterados.

## 5. Arquivos da implementação

### Java: quatro fontes novas e nove modificadas

| Arquivo sob `java/` | Alteração |
|---|---|
| `client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java` | Nova fonte: persistência, estado imutável, máscara, restauração das escolhas, listeners e revisão |
| `client/src/java/org/emulationstation/frontend/station/StationGraphicsPanel.java` | Nova fonte: painel/aba EFEITOS, controles individuais, fundo e lifecycle opaco |
| `client/src/java/org/emulationstation/frontend/station/StationWaveBackground.java` | Nova fonte: três ondas simples, buffers reaproveitados e agendamento somente visível |
| `netplay-src/org/emulationstation/frontend/netplay/StationMagazineRows.java` | Nova fonte: planejador de linhas nas quatro faixas, ajustado ao FIT_CENTER |
| `client/src/java/org/emulationstation/frontend/station/StationFrontend.java` | Inicializa/publica preferências e encaminha o botão geral; conserva o preload/cache/publicação R116 |
| `netplay-src/org/emulationstation/frontend/netplay/StationActionButton.java` | Aplica as opções a efeitos de botões, mantendo ações e geometry atuais |
| `netplay-src/org/emulationstation/frontend/netplay/StationGameRatingView.java` | Interrompe/reconcilia a animação das estrelas conforme ICONS e lifecycle |
| `netplay-src/org/emulationstation/frontend/netplay/StationHyperspaceView.java` | Integra visibilidade/opções ao fundo estático atual; não restaura o antigo motor de traços |
| `netplay-src/org/emulationstation/frontend/netplay/StationLottieIllustration.java` | Quadro estático quando ICONS está desligado e retomada condicionada ao lifecycle |
| `netplay-src/org/emulationstation/frontend/netplay/StationOnlineClient.java` | Cursores, apresentação assinada conciliada, políticas preservadas e matriz de backoff somente para consultas |
| `netplay-src/org/emulationstation/frontend/netplay/StationOnlineCoverView.java` | Campo parcial válido, planner, cache limitado e opção LED/lifecycle |
| `netplay-src/org/emulationstation/frontend/netplay/StationOnlinePlatformPolicy.java` | Normaliza `ps2br` para `ps2` |
| `netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java` | Paginação independente/fallback, consultas recuperáveis, sinopses por itemId, detalhes e alternativa de fundo |

`StationApi`, `StationMultiplayerProfile`, `StationOnlineGame`, renderers de emulador e classes de controle não foram substituídos. As demais 217 fontes Java da base permanecem identificadas pelo manifesto sem alteração de bytes.

### Ponte e carrossel nativos

| Arquivo | Alteração ou função preservada |
|---|---|
| `frontend/station_frontend.cpp` | Ponte JNI e snapshot atômico das preferências, com validação de máscara/modo/revisão e comando do botão geral |
| `native/d0/native_graphics.h` | Novo acesso ao snapshot, sem JNI/IO por quadro |
| `native/d0/native_graphics_ui.h` | Novo botão ao lado do tema, toque e abertura do painel Android |
| `native/d0/native_magazine_rows.h` | Novo planejador de quatro faixas para a preparação incremental |
| `native/d0/native_carousel.cpp` | Conecta botão/gates, respeita VIDEO/LED e mantém fila/publicação progressiva da base |
| `native/d0/native_magazine_field.h` | Campo candidato zerado, preparo parcial, chave completa, retenção limitada e invalidação de origem/contexto |
| `native/d0/native_magazine.h` | Apresenta campo parcial válido e respeita a preferência de LED |
| `native/d0/native_formation.h` | Mantém o JPG de segurança quando VIDEO está desligado; preserva proporção/cantos nesse caminho |
| `native/d0/native_system_video720.h` | Admissão estática limitada de posters, reaproveitamento retido e encerramento do decoder existente |
| `native/d0/native_game_actions.h` | Respeita CELL_EFFECTS nos efeitos existentes de ABRIR/VOLTAR, mantendo os comandos |
| `native/d0/native_info.h` | Respeita ICONS nas estrelas |
| `native/d0/native_lottie_gear.h` | Respeita ICONS no robô |
| `native/d0/native_settings.h` | Acrescenta a aba/ação EFEITOS e limpa o gesto em close/Back/mudança de owner |
| `native/d0/native_space.h` | Seleciona céu/ondas/sem fundo e aplica o gate do fundo |
| `native/d0/native_theme_switch.h` | Mantém seleção de tema, aplicando ícone estático/transição desligada quando solicitado |
| `native/d0/magazine_shader.h`, `premium-magazine-led-android.glsl` | Matemática do LED preservada contra a fonte pública R116 |
| `native/d0/video720_retained_draw_state.h`, `video720_retained_fastpath_policy.h` | Wrappers/política retidos da base, sem alteração |
| `native/station_cover_plan.hpp`, `native/d0/station_chatbot_state.h` | Planejamento/publicação e estado do robô da base preservados |

Outros headers de implementação/ABI foram restaurados como inputs da compilação integral do carrossel; restauração de arquivo não significa novo efeito. Sete objetos privados de mídia e três stubs permanecem locais, com hashes conferidos pelo manifesto congelado. Não se publicou pixels, vídeo, BIOS ou ROM como arrays de código.

### Políticas, receita e rastreabilidade

- `assets/station-online/engines.json`: textos/políticas PS2/Saturn/Switch. Os registros de motores/core/runtime não recebem novas identidades por esta alteração visual.
- `build.py`: fases explícitas prepare/compile/package; base R116 exata, fontes/inputs conferidos, duas bibliotecas da interface recompiladas, duas DEX completas, verificação de exports/alinhamento e comparação integral das outras entradas do APK.
- `recipes/build-r117-arguments.json`: argumentos explícitos; compilação em E:, temporários do APK e destino final em G:. Senhas não fazem parte do arquivo nem da receita.
- `JAVA-SOURCE-MANIFEST-R116.json` e `CAROUSEL-INPUT-MANIFEST-R116.json`: referências congeladas. `JAVA-SOURCE-MANIFEST.json` e `CAROUSEL-INPUT-MANIFEST.json`: inputs finais desta fonte.
- `SERVER-CROSSCHECK.md`: contrato, leitura do código do servidor, diferenças conciliadas e hashes dos documentos recebidos.
- `.gitignore`: exclui mídia, objetos privados, APKs, logs, fixtures geradas, capturas e receitas pessoais de medição. Os documentos `*-R116-HERDADO*` e recibos `*-inherited*` são históricos da base.

## 6. Evidências disponíveis

| Evidência | Resultado e alcance |
|---|---|
| `evidence/lobby-recovery-r117-tests.json` + `tests/StationLobbyRecoveryR117Test.java.in` + `recipes/test_lobby_recovery_r117.py` | 54 verificações executadas no cliente/política reais: cursores, fallback, snapshot imutável, identidade, própria sala, políticas, limites e matriz transitória/terminal |
| `evidence/graphics-state-rows-r117.json` + `recipes/test_graphics_r117.py` + `tests/StationGraphicsPreferencesTest.java` | 51 verificações de preferências/estado, executadas no host |
| `evidence/graphics-state-rows-r117.json` + `recipes/test_graphics_r117.py` + `tests/magazine_rows_test.cpp` | 2.659.588 verificações do planejador nativo real, alturas 1–1536, quota e cobertura |
| `evidence/graphics-state-rows-r117.json` + `recipes/test_graphics_r117.py` + `tests/StationMagazineRowsTest.java` | 7.978.753 verificações do planejador Java, alturas 1–1536 e três formas de letterboxing |
| `evidence/led-progressive-checks.json` + `tests/verify_led_progressive.py` | 818 verificações executadas nas funções reais de retenção com mocks GL/contexto; orçamento/LRU, revisão, viewport, nome reciclado, mudança de contexto e campo grande |
| `evidence/video-static-checks.json` + `tests/verify_video_static.py` | 156 verificações dos helpers reais de vídeo estático; prioridade, admissão, matriz/UV/cantos, contexto e falhas |
| `tests/video720_retained_draw_state_test.cpp` | Prova isolada reportada para restauração com VAO e atributos individuais |
| `evidence/graphics-integration-guards.json` + `tests/verify_graphics_integration.py` | 33 guardas de escopo/integração no código |
| `evidence/graphics-settings-lifecycle-r117.json` + `tests/verify_graphics_settings_lifecycle.py` | 2.435 verificações executadas nas funções reais de close e gesto de produção: 200 ciclos close-before-UP/reabertura/novo ponteiro, owner e janela já fechada |
| `evidence/LED-PROGRESSIVO-R117.md`, `evidence/VIDEO-ESTATICO-R117.md` | Explicação dos caminhos, qualidade preservada e limites dos probes |
| `evidence/server-last-fetch-r117.json` | Último fetch de todos os ramos; nenhum retorno relevante posterior a `141b488...` |

A compilação conjunta das 230 fontes Java foi reportada antes do build completo. Nenhum desses probes mede frame pacing, temperatura, percepção visual no aparelho, estabilidade WAN ou gameplay em múltiplos telefones. Resultados do APK completo e sua instalação são registrados separadamente pelo responsável da entrega.

`evidence/REVIEW-LIFECYCLE-GL.md` é uma revisão herdada da base. Sua afirmação de manter o ImageView até terminar o campo descreve o gate antigo; o caminho R117 confirmado publica o primeiro pacote válido, com zeros preservando a base. Esse documento herdado não deve ser apresentado como prova da nova publicação parcial.

## 7. Preservação e pendências precisas

Permanecem: uma fila de IO/decode de capas, prioridade da capa visível, cache persistente por coverId+revision, warmup de até 64 tentativas/20 segundos, publicação progressiva de nove itens com pulso de 80 ms, cancelamento por lifecycle/geração, vídeos locais, uma passagem, retenção dois quadros antes do fim e orçamento de 30 FPS dos menus. Não se adotaram os quatro workers da candidata antiga citada pelo servidor.

Continuam necessários no aparelho:

1. Medir tempo até o primeiro LED visível e até o campo completo, no carrossel e no online, inclusive ao revisitar a mesma capa.
2. Conferir seleção rápida, 20 ciclos de background/foreground, recriação de surface e liga/desliga durante a preparação; observar memória/contextos GL e frame pacing.
3. Conferir vídeos desligados: JPG imediato, poster progressivo, ausência de célula vazia, retomada da seleção e nenhuma reprodução escondida.
4. Verificar persistência/restauração das opções e modos Céu/Ondas/Sem fundo; comparar CPU/GPU/temperatura com o mesmo aparelho, tela e janela de medição.
5. Conferir paginação, resposta obsoleta, falhas de rede/429 e sinopses em Criar/Sua sala/convites/outros diálogos; validar uma sala nova real com os perfis já liberados.

A liberação das plataformas pendentes é trabalho dos adaptadores/perfis reais; esta entrega não a substitui por flags. Ausência de sinopse no catálogo autenticado é uma pendência de conteúdo identificável pelo itemId, e não motivo para inventar texto dentro da sala.

A publicação deve usar somente o snapshot R117 aprovado, sem `git add` da raiz contendo outras versões locais. A auditoria de candidatos e sugestões para cópias redundantes estão em `evidence/PUBLICATION-AUDIT-R117.md`. Nenhum arquivo foi staged, commitado, enviado ou apagado por esta subtarefa de documentação.

## 8. Entrega executada e conferência inicial

O build final compilou 230 fontes Java e as duas bibliotecas da interface, assinou com o certificado original e confirmou alinhamento 16 KiB. SHA final `fce3be2821abcb89da05b18370a36dadc0a78f1f5f8381ccbc8a0ba2c2645372`, 2.217.033.096 bytes; cinco entradas alteradas, 13.543 preservadas byte a byte.

Atualização direta no Motorola Edge30 em 11/10/2026 00:55:50 UTC, sem APK extra no aparelho, desinstalação ou limpeza. SHA integral instalado, UID e instalação original conferidos. A preparação inicial concluiu e o carrossel autenticado abriu. Botão Modo leve, aba EFEITOS com seis controles e opções de fundo, e fundo Ondas foram observados; céu e efeitos ativos originais restaurados. Recibos agregados em `evidence/installation-motorola-r117.json` e `evidence/physical-smoke-r117.json`; capturas ficam privadas.

A conferência básica não mede o primeiro LED nas listas/online, frame pacing, temperatura, persistência após reinício de processo ou estabilidade multiplayer. Samsung não atualizado para R117 nesta entrega.
