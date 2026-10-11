# Demonstrações locais PS3 e PS4 — R129

Extensão isolada sobre a R128 assinada `0189527c7537845562a2be4be15c0fab976c85f4f9c7f8ab884915c8bc3052dc`. Acrescenta duas linhas de apresentação locais ao catálogo entregue ao carrossel, dois vídeos Sony do tema do proprietário e acesso à interface de configuração dos emuladores. Não modifica o catálogo autenticado, jogos reais, perfis online, downloads, renderer do carrossel, demais vídeos, economia, cache ou pré-carregamento.

Estado atual em [evidence/STATUS.json](evidence/STATUS.json), vinculado aos recibos finais corrigidos. A [primeira tentativa R129](evidence/first-candidate-startup-failure.json) foi instalada, mas apresentou falha na configuração do catálogo; não escolhe o instalador atual. A prova do contrato de `validWarmCoverPath` e a observação física de `IOException` estão registradas separadamente. Não foi alegado um log físico literal de caminho inválido. A conferência própria da versão Final-Modal está em [physical-observation-final.json](evidence/physical-observation-final.json). A conferência física final no Motorola observou o catálogo e as listas DEMO dos dois sistemas, com capa, nome, sinopse/aviso e contador1/1; ambos os marcadores exatos tinham83bytes. Os heróis, miniaturas e frames/posters das mídias Sony apareceram; movimento dos vídeos não foi validado por imagens estáticas. Os dois botões de configurações abriram, por toque humano, aPS3e Welcome e Bachata S4 0.2.4 com seu aviso inicial de notificações; nenhuma permissão foi respondida nem setup concluído. Após retornar pelo Login público à ESActivity, os textos Sony não vazaram no carrossel. O recibo público agregado do app está em `integration/local-sony-demos/evidence/physical-observation-final.json`. Autenticação, ativação de servidor, gameplay e melhora térmica continuam não validados.

## O que aparece

- PS3: **DEMO — Aventura orbital**, identificador `local-demo-ps3-orbital-v1`.
- PS4: **DEMO — Corrida neon**, identificador `local-demo-ps4-neon-v1`.
- Cada amostra tem capa PNG estática identificada como DEMO e sinopse explícita de que não contém jogo. Não anuncia capacidade multiplayer, avaliação ou compatibilidade física.

O caminho raiz dos arquivos de demonstração é o `romsRoot` efetivo recebido da integração nativa existente. Nele, a extensão cria apenas `ps3/DEMO-AventuraOrbital.iso` e `ps4/DEMO-CorridaNeon.pkg`, sem sobrescrever arquivos existentes. ISO/PKG de demonstração contêm um pequeno marcador textual, não conteúdo de console.

As duas capas ficam no diretório privado retornado por `Context.getNoBackupFilesDir()`, em `station-covers/local-demo-ps3-orbital-v1.png` e `station-covers/local-demo-ps4-neon-v1.png`. A raiz canônica deve ser exatamente `/data/data/org.turboramastation.frontend/no_backup` ou `/data/user/0/org.turboramastation.frontend/no_backup`; pasta e arquivos simbólicos são recusados. Esse é o formato legado já aceito por `validWarmCoverPath`, sem relaxar o parser nativo. Capas são desenhadas uma vez e reutilizadas; não há rede, serviço ou animação nova.

## Guardas

1. O catálogo real e seus IDs têm prioridade. Uma colisão com ID autenticado impede a inserção da amostra.
2. A preparação roda no trabalhador finito existente do catálogo; caminhos simbólicos e arquivos preexistentes que não correspondam à amostra são preservados e recusados.
3. O limite original de 4096 linhas do JNI é mantido. Amostras não podem invalidar um catálogo real que já ocupe a capacidade.
4. `start`, `remove` e `cover` interceptam somente IDs de amostras efetivamente publicados. Nenhuma solicitação HTTP de download, remoção ou capa é feita para eles. Resultado de capa `1` mantém a capa local já aquecida, conforme o tratamento original do JNI.
5. O botão Jogar usa o `localPath` da linha nativa: o `GuiStore::launchItem` original lê `Item.localPath` em `+0xb0`, usa `getPreferredPath` e substitui `%ROM%`/`%ROM_RAW%`. O hook Sony offline da R128 permanece intacto.
6. Na Activity Sony, o trabalhador confere autoridade do provedor, nome exato **e todos os bytes do marcador** antes de procurar ou chamar um emulador. Uma amostra mostra somente o aviso de demonstração. A extensão nunca envia um ISO/PKG falso ao aPS3e ou Bachata S4.
7. O catálogo Java autenticado não contém as amostras. `StationOnlineGame.profiles`, `classifications` e `prepare` já recusam `client.item(id)==null` antes de solicitar perfil ou criar sala. Nenhum engine ou perfil PS3/PS4 é adicionado.

## Alterações de payload

| Payload | Alteração permitida |
| --- | --- |
| `classes28.dex` | Somente os quatro métodos `publishCurrent`, `start`, `remove`, `cover` de `StationFrontend`; outras 270 classes, inclusive fábrica PSX, preservadas |
| `classes39.dex` | Helper local, guarda de demonstração e operação explícita de configuração na Activity Sony; política Sony idêntica à R128 |
| `libturbo_carousel.so` | Fallback de capa Sony em `syncModel`, duas opções do menu e mapas/posters Sony adicionais; renderer/motor de vídeo preservados |
| `assets/turbo-system-videos/720-ps3.mp4`, `720-ps4.mp4` | Dois originais locais silenciosos 720×720/24fps, copiados byte a byte do tema TURBORAMAx |

O fallback de arte não desenha efeitos nem muda rotas de jogos. Primeiro reproduz o carousel R128 e exige hash idêntico; depois aplica deltas delimitados de arte, menu e includes de mídia. Manifesto, `classes6.dex`, `classes35.dex`, motores e opções permanecem os da R128. Marcadores dos motores que incluem DEX/carousel compartilhados precisam ser renovados pelo pipeline R129.

A arte da plataforma usa o caminho privado `no_backup/station-covers/<demoId>.png` sob `/data/user/0/org.turboramastation.frontend`, conferido uma vez por plataforma Sony na montagem de uma lista de sistemas alterada. Requer a linha local do DEMO exato na própria plataforma e preserva arte de sistema já cadastrada. Não depende de `Item.coverPath`, que pertence à janela transitória de capas dos jogos; a revelação, a remoção fora da janela, a residência de texturas e a rotina por frame permanecem intactas.

## Compilação isolada

`recipe/build_demo_payloads.py` exige `--donor`, `--jdk`, `--android-jar`, `--d8-jar`, `--apktool`, `--parent-offline`, `--ndk`, `--native-inputs`, `--out`. O donor é exclusivamente a R128 assinada; `--parent-offline` aponta para `integration/ps3-ps4-offline`; `--native-inputs` reutiliza a árvore privada preservada `reconstrucao/native-inputs`; `--ndk` é o diretório `bin` LLVM. Saída deve ser um diretório novo fora das fontes.

A receita produz os três payloads compilados, dois assets de vídeo e `demo-payloads.json`. Confere as 271 classes antes e depois de remontar o DEX real, namespaces de DEX39, política Sony, reprodução nativa R128, exports, alinhamento 16 KiB, mídias/posters e congelamento de fontes. Não monta, assina ou instala APK. Não substitui prova de conferência visual ou gameplay.
