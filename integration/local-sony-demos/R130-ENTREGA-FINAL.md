# R130 — configurações compactas e vídeo principal com loop selecionável

## Pacote

| Identidade | Valor |
|---|---|
| Fonte executável | [`c8e0a8c0f46a43b9d3cb16c3ab194a90cad18a54`](https://github.com/luziellacerda/TurboElden/commit/c8e0a8c0f46a43b9d3cb16c3ab194a90cad18a54) |
| Instalador local | `desenvolvimento/TurboStations-Premium-R130-20261011.apk` no backup único F |
| SHA256 | `d227b0af17600bf99ec097857bf182f6e7989f8ddc3b68b63e17c81f69eb30ad` |
| Tamanho | 2.237.522.133 bytes |
| Conferência | Assinatura original v2/v3, alinhamento16KiB e conjunto fechado de12payloads |

Os recibos atuais são [package-final.json](evidence/package-final.json), [runtime-final.json](evidence/runtime-final.json) e [STATUS.json](evidence/STATUS.json). As observações visuais da instalação anterior R129 permanecem históricas.

## Instalação e abertura observadas separadamente

O [recibo independente do Motorola](evidence/installation-motorola-r130.json) comprova a atualização R130 concluída em **11/10/2026 às 17:07:56 UTC**, com o SHA integral acima conferido no aparelho. Certificado/assinatura original, UID, data original de instalação e diretório de dados foram preservados; não houve desinstalação nem limpeza de dados.

A observação automática inicial terminou às **17:08:26 UTC** com `launchOutcome=unobserved`: ela não confirmou a abertura do frontend. Posteriormente, o carrossel completo foi observado no Motorola após o retorno da tela de criação de sala. A [observação física posterior](evidence/physical-observation-r130.json) registra esse resultado separadamente; não altera retroativamente o resultado do observador inicial.

O registro privado disponível mostra uma sequência completa de criação/resumo do SDL às **17:09:11 UTC**, posterior à primeira janela de observação, e aplicação do catálogo com **3.687 itens e capas privadas** às **17:09:16 UTC**. Não registrou fatal/ANR nessa janela. Esses fatos não determinam a causa da captura inicialmente preta. Instalação e frontend visível não comprovam autenticação, firmware pronto, ativação do servidor, estabilidade térmica ou gameplay.

## Alterações implementadas

- **Configurações:** organização compacta, alinhamento dos controles, clipping e restauração da matriz dos cards; alvos lógicos48dp preservados.
- **Vídeos:** opção persistente **Com loop / Sem loop** no painel EFEITOS GRÁFICOS, junto ao desligamento dos vídeos. O loop vale exclusivamente para a plataforma em destaque no carrossel principal. Coleções continuam com uma reprodução e parada dois frames antes do fim.
- **Consumo:** o loop reutiliza o MediaPlayer/decoder existente por pause/seek/start. Desligar vídeos, economia, saída da tela e background continuam prevalecendo. O loop não acrescenta consultas de preferência em disco/JNI por quadro nem aumenta a capacidade de decoders. Com loop mantém a reprodução ativa; Sem loop permite parar depois da primeira passagem. Não foi medida redução de CPU ou temperatura.
- **Sony offline:** retirada da confirmação genérica redundante antes do despacho oficial. As guardas de pacote/versão/certificado, URI, DEMO e disponibilidade permanecem. PS3 segue aPS3e2.43; PS4 segue importação PKG/biblioteca do Bachata S4 0.2.4.

DEX28 permite somente StationFrontend e famílias GraphicsPanel/Preferences; DEX35 permite somente SinglePassVideo720. Sets de classes, demais classes e inicializadores estáticos são conferidos no donor real. O recibo Java efetivo descreve a compilação da base **mais** o overlay DEX35, sem atribuir o DEX novo ao compilador antigo. LEDs, cache/preload, geometria do carrossel, máximo30fps dos menus e cores/opções/perfis/capacidades dos emuladores permanecem sob guardas de preservação. Os quatro IDs online N64/GameCube/Wii/PSX foram renovados para vincular o bundle compartilhado atual.

## Preparação Sony: evidências distintas

O [recibo sanitizado de preparação](evidence/sony-preparation-r130.json) é um procedimento dos emuladores oficiais, separado da instalação da Station R130.

| Observação | Resultado comprovado | Limite |
|---|---|---|
| aPS3e: preparação inicial | Instalador oficial exibiu sucesso do firmware4.93; assistente concluído e biblioteca principal vazia observados | Sem conferência privada dos arquivos de firmware nem jogo importado/iniciado |
| aPS3e: reentrada aquecida posterior | QuickStart ficou carregando e emitiu `RuntimeException: Library already loaded` em `Emulator.load_library` | Defeito de reentrada oficial2.43 continua aberto; sucesso do assistente não o resolve |
| Bachata S4 | Biblioteca vazia e configurações abriram; GLIBC selecionado e cinco drivers exibidos; nenhum erro de setup observado nessa janela | Não comprova compatibilidade de GPU/título nem gameplay |

Não houve bypass de Activity privada, limpeza de dados ou repetição de recuperação após a falha do aPS3e. Firmware e jogos não estão no APK Station nem no Git. DEMOs são amostras visuais, não jogos. PS3/PS4 continuam exclusivamente offline.

## Retorno do servidor: somente conferência

Foi lido o retorno [`310c6654769e9f602c9a9ad9ed1da6212d85e531`](https://github.com/luziellacerda/Servidor-pix/commit/310c6654769e9f602c9a9ad9ed1da6212d85e531), branch `feat/station-r128-aplicado-20261011`, documento [`r128-retorno-servidor-20261011.json`](https://github.com/luziellacerda/Servidor-pix/blob/310c6654769e9f602c9a9ad9ed1da6212d85e531/docs/station-android/online-plataformas-20261009/r128-retorno-servidor-20261011.json).

Ele registra `privateKitReceived=false` e `newR128EnginesActivated=false`. Reconhece a entrega R128; não confirma o complemento R129 `c433052ce12c662355dac81c9d9c106b5f283bb1` nem os IDs R130. A leitura não executou atualização, implantação ou reinício de serviço e não publicou outro handoff.

## Fechamento e reprodução

Foram conferidos no Motorola o menu compacto, os dois acessos Sony na faixa superior, a abertura do painel de efeitos por toque, as escolhas Com loop/Sem loop e o estado desativado dessas escolhas quando os vídeos estão desligados. Os vídeos ligados e Com loop foram restaurados. O novo botão PS4 abriu a biblioteca oficial vazia; o retorno ao carrossel não exibiu rótulos Sony fora do modal. Não foi repetida a abertura PS3 com o defeito de reentrada já registrado.

Essas conferências constam em `evidence/physical-observation-r130.json`, vinculadas a esta fonte e SHA. Imagem estática não comprova movimento, estabilidade, qualidade térmica ou partida real. Esta entrega não promove o pacote a estável nem certifica autenticação, ativação do servidor ou gameplay.

### Requisito posterior de integração interna

Após a instalação, o mantenedor esclareceu que PS3/PS4 devem estar incorporados ao APK Station e preparados automaticamente. A R130 preservada neste recibo usa os aplicativos externos oficiais e **não cumpre esse novo requisito**. A integração interna exige uma composição nova de código, recursos, manifesto, bibliotecas e preparação dos dados na UID Station; não é comprovada pela preparação realizada nos aplicativos externos do Motorola.

O único backup F conserva donors R126/R127/R128, fontes/ferramentas e recibos históricos. O atualizador copia o diff de fontes/documentos/recibos committed até o commit de organização explícito, incluindo as evidências R130. O manifesto é incremental: confere todos os nomes/tamanhos/stamps e atualiza hashes dos arquivos controlados; não é uma nova varredura integral. O reconstrutor privado `RECRIAR-PAYLOADS-R130.py` exige `--source` e recria somente os12payloads, com `client.jar`, `rooms.jar` e composição Java base+overlay; não cria outro APK. Reconstrução a partir de F continua pendente até seu próprio recibo de comparação.
