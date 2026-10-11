# Revisão do online compacto, três estilos e painel gráfico — R123

## Resultado

**PASS estático, sem bloqueador concreto identificado.** Revisão da fonte final R123 contra a R122. Foram inventariadas 234 fontes Java: 229 das 233 fontes da base são byte idênticas, quatro mudaram e uma foi acrescentada. Esta revisão cobre `StationRoomsActivity.java` e `StationActionButton.java`, além da preferência, bridge e geometria dos três estilos do carrossel: `StationFrontend`, `StationGraphicsPanel`, `StationCarouselStylePreferences`, `station_frontend.cpp`, quatro headers nativos alterados e o novo `station_carousel_geometry.h`. Os 22 arquivos de autoridade e 28 métodos críticos conferidos permanecem iguais. A revisão do online e da geometria foi somente leitura, sem testes, rede, servidor, aparelho ou alteração de produção. Separadamente, este agente recebeu a edição de apresentação de StationGraphicsPanel, revisada pelo responsável; suas provas host/compilação estão atribuídas na seção própria. Nenhum manifesto, receita de build ou índice Git foi alterado por este revisor.

Fontes revisadas:

- Rooms SHA256 `320a16f61973866bb38d8c191117b34714efc1b1cd042220c0cbd78485093556`.
- ActionButton SHA256 `c8741d3c47d73b137e36e7a3fe2e8f6b84c8afca3e90025422bcd442ab2795af`.
- Recibo agregado: `evidence/online-compact-static-r123.json`.

## Iniciar partida

| Caso | Evidência final |
| --- | --- |
| Clique repetido | `action()` linha 512 seta `busy=true` na UI antes de enfileirar. Um segundo clique não enfileira outro comando durante a ação. |
| Sala exibida ficou antiga | `paint()` captura a chave exibida; `startRoom()` linha 1033 compara a identidade antes de enfileirar e novamente no worker. |
| Anfitrião, prontidão e capacidade | `StationRoomStartState.reason()` permanece byte idêntico: host, estado waiting, participantes únicos, slots, limites 2–5 e quantidades permitidas continuam exigidos. |
| Transporte deixou de estar disponível | Transporte é conferido na UI e no worker. A chamada continua enviando roomId/generation/transport por `client.call()`, com o roteamento e a autenticação existentes. |
| Mudança em sala legada sem roster | `roomConfirmationKey()` linha 1023 conserva os campos anteriores e inclui host/protocolo/members/ready; troca de convidado ou confirmação invalida a chave exibida. |
| Falha durante solicitação | `failure()` linha 509 acrescenta somente `updateStartState()` após `busy=false`, dentro do guard existente active/epoch. Mensagem de status, feedback, cancelamento e rede permanecem iguais. |

O diálogo redundante anterior foi retirado; há um único botão Iniciar da sala e um único literal de comando start. Não foi removida a aceitação humana de entrar/trocar sala: `confirmWithCover()` conserva dismiss + accepted.run e seus botões agora ficam lado a lado.

A leitura local não substitui a validação do servidor. Um estado remoto pode mudar depois da última leitura local; a autoridade continua revalidando a solicitação.

## Apresentação e informações

- `RoomControls`, linha 336, mede texto, ícone e padding, mantém altura de toque 48dp e quebra em linhas quando falta largura. Somente TextViews/Buttons construídos pelo próprio fluxo são seus filhos. Não acrescenta timer ou polling.
- Chips de modo/quantidade mantêm alvos 48dp e face 32dp. Perfil escolhido, capacidades permitidas e callbacks de seleção continuam nos métodos originais.
- Sua sala mostra participantes, posições e prontidão com menos margens. Sinopse e instruções completas continuam disponíveis pelo toque no nome; as etapas anteriores também preservam detalhes por toque. Na revisão visual aditiva, o título repetido de Sua sala foi retirado do corpo; o cabeçalho Sua sala mantém os detalhes por toque e sua descrição acessível. O nome duplicado do corpo Criar fica oculto, mantendo o cabeçalho existente.
- Navegação lateral plana preserva seleção ciano e fundo transparente em todos os estados. Foco e pressionado usam marcador branco; seleção usa marcador ciano de 2×14dp, e desativado mantém a tipografia correspondente. Os callbacks e a animação condicionada às preferências permanecem iguais.

## Capas, lifecycle e contrato

`roomCoverCard()` linha 285 e `reconcileRoomRows()` linha 312 são idênticos à R122: a mesma sala/jogo conserva card, ancestral e TextureView anexados; removem-se somente linhas realmente diferentes. Artwork, shaders, cache e bootstrap/teardown GPU não foram modificados por estes dois arquivos.

`StationOnlineCoverView`, `StationCoverLightingShader`, `StationCreateGameCard`, `StationCoverLayout`, `StationFlowPanel` e `StationRetroActivity` conferem byte a byte. `launch()` linha 1043, criação, preparação, join, commands, polling, epochs e lifecycle das salas também permanecem iguais. Não há alteração de engine, core, protocolo, tickets, assinatura, input/slots ou autenticação nesta revisão.

## Reta, Diagonal, De lado e preservação gráfica

**Sem bloqueador concreto identificado na leitura final.** CURRENT=0/Reta continua padrão; DIAGONAL=1 conserva a rotação 2D anterior e LATERAL=2/De lado acrescenta a perspectiva. O enum é aceito pela preferência, pelo setter JNI e pelo painel sem migrar graphicsState/mask/background/revision.

| Área | Evidência final |
| --- | --- |
| Geometria | `station_carousel_geometry.h` retorna identidade no estilo original, efeitos desligados, posição inválida ou selecionada. Diagonal preserva as operações anteriores; De lado usa homografia central com Y equivalente a 45° e focal 1,2 larguras, mantendo W positivo e bounds no slot. Esses parâmetros são da adaptação Android, não declarados pelo XML PC. |
| Hero, transição e seleção | `coverSlot`, `flowFormationHook`, política de cantos e `formationTouch` permanecem iguais à base. O índice/float de animação anterior não é reiniciado. Hero é identidade; sexto vizinho, prioridades, carregamento e 30 fps existentes permanecem. |
| Arte, vídeo e faixa | Arte e faixa usam a projeção do slot; vídeos/posters entram pelo wrapper que guarda/restaura esse contexto. UV/cor/count/src/dst não mudam. A composição MVP*H produz divisão homogênea e interpolação UV/W; as faces mantêm sua geometria local anterior. |
| Estado GL | Lookup reconhece u_mvp original e MVPMatrix de vídeo/faixa. Cada strip projeta e restaura os 16 floats por RAII. A função preservada de strip não muda programa ou MVP; não há GLuint/contexto/localização cacheados. A tabela POD de funções GLES é resolvida uma vez. |
| Toque e recorte | A inversa desfaz a mesma homografia antes do teste de limites/cantos. O scissor contém os quatro cantos, com arredondamento exterior. A ordem inversa de hit-test e a seleção original permanecem. |
| Qualidade e lifecycle | Roundrect, shaders de hero/LED/faixa/fundo, clock, decoder, filtros, cache e lifecycle não são reescritos. Vídeo/faixa recuperam os fontes R122 removendo somente os encaminhamentos de desenho. Não há novo shader, FBO, vértice, draw, timer, worker, decoder ou IO por quadro. |

O XML local foi lido: `gamecarousel-approved-dashboard.xml:483` declara coverflow, pivô central, slide/420 ms, até 13 itens / sete vídeos. O Android mantém os seis vizinhos e a política anteriores. O XML não fixa ângulo Y/focal dos vizinhos e não existe prova de fonte exata do renderer PC; não se afirma reprodução visual idêntica. `REFERENCIA-CARROSSEL-DIAGONAL.md` distingue essas referências da adaptação 45° / 1,2w.

O recibo `renderer-mvp-r123.json` foi conferido contra o ELF exato libmain da base R122, SHA256 `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6`. Este revisor releu no APK e rehashou os três intervalos: strip 0x2e5470 / 320 bytes (`9d31095b…`), error-check 0x2e4de0 / 276 bytes (`972d616c…`) e setter 0x2e55b0 / 296 bytes (`09f34f9b…`). A análise do autor identifica os calls e ausência de troca de programa/MVP na strip; o setter fica fora dela. ELF/disassembly permanecem privados. Não é execução numa GPU.

Reta/Diagonal/efeitos desligados não entram nas consultas GL adicionais. De lado consulta programa/localização/matriz e faz duas gravações de MVP por strip; esse custo de driver/composição não foi medido no telefone. Se MVP falta antes do slot, desenho/toque usam Reta. O fallback posterior para um programa externo não examinado pode projetar XY com UV afim aproximado; suporte a shaders externos arbitrários não é afirmado.

Os 124 inputs nativos continuam com quatro headers alterados e um novo ; 74 outros públicos e 45 hashes privados da base permanecem. A primeira montagem R123 já teve os 45 privados efetivos rehashados; a receita da nova montagem exige novamente SHA/conjunto/identidade dos inputs. Os 12 inputs frontend mantêm 11 iguais e somente station_frontend.cpp modificado; quatro auxiliares locais/documentais continuam iguais. Nada privado integra esta publicação.

## Painel gráfico compacto e transparência

Este agente editou somente StationGraphicsPanel para o pedido visual, separado da revisão independente do online/nativo. Fonte final SHA256 `7b8483c4775e2f1c2c543f74308be153a4b5b601d1edde3f00881721d0e96654`.

Header menor, controle geral alinhado, ambiente/estilo em segmentos de face 32 dp / alvo 48 dp e opções em linhas mínimas de 48 dp, sem padding vertical extra ou rótulos visuais ATIVO/DESATIVADO repetidos. Paisagem larga tem duas colunas; rolagem continua disponível para alturas/fontes que não comportem o conteúdo. Não foi demonstrada ausência de scroll por medição de Views Android.

Os métodos de API/lifecycle e handlers de preferências continuam iguais; somente o intervalo do estilo acrescenta 2. Escolhas individuais, economia, gate CELL_EFFECTS, foco e descrições acessíveis são conservados. Os desenhos estáticos combinam alfa ARGB de fill/rim/rail com o alfa do Drawable e pulam resultado zero; a revisão do responsável detectou e corrigiu a anterior perda de transparência causada por setAlpha(255).

`graphics-panel-compact-r123.json`: 34 guardas, 1.080 casos / 5.508 verificações do corpo real ConsoleSurface com stubs Paint/Canvas e dois fontes reais compilados contra API 34. Não são pixels/medidas Android, toque, consumo ou GPU físicos. Detalhes em `PAINEL-GRAFICO-COMPACTO-R123.md`.

## Revisão visual após a primeira instalação R123

A captura real mostrou quatro fundos laterais preenchidos. Os pixels interiores conferidos têm exatamente `0xff142033`, cor do primeiro selector `-state_enabled` da ActionButton inicialmente compilada. A fonte normal da navegação já era transparente. A hierarquia capturada depois estava no bloqueio do telefone; portanto **não foi estabelecido que os quatro Views estavam desativados**, nem foi atribuída causa única à propagação de estados do drawable.

O APK real foi inspecionado por leitura dos class_defs dos **38 DEX / 51.323 definições de classe**: `StationActionButton` e `StationRoomsActivity` têm uma definição cada, ambas em `classes35.dex`. Esse DEX possui 480 classes, 646.424 bytes e SHA256 `e892722f8d9961fc2caa4d052ead17dfb87bb072af98b630d66e00d6655835c2`, igual ao payload da primeira compilação R123. Os aliases de compilação originais correspondem a Rooms `780a0bfa…` e ActionButton `865e0957…`; não há evidência de duplicação ou de DEX antigo para essas classes nesse APK.

O ajuste final conferido acrescenta uma rota de navegação independente, transparente também nos estados pressed/focused/disabled, com apenas marcadores estreitos; limpa tint após atribuir o background. O selector de ações comuns e seus callbacks continuam próprios, mantendo alvos 48dp. Nenhum listener, timer ou efeito contínuo novo foi acrescentado.

Nos chips, `setupChoice()` aplicava o espaçamento antes de `renderRoomSetup()` trocar o background por um InsetDrawable. A [fonte primária de View.setBackgroundDrawable()](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android14-release/core/java/android/view/View.java) confirma que o padding do background pode substituir o padding do View. `applyChoiceFace()` agora reaplica 12dp nas laterais após cada background. O resumo usa altura natural, sem ScrollView com peso, e o aviso de prontidão só fica oculto quando idêntico ao status já mostrado; status, erro e elegibilidade de iniciar são preservados.

Foram comparados novamente **17 corpos críticos com os aliases exatos da primeira R123 instalada** e **28 corpos com a R122**; permanecem iguais. Nenhuma criação, entrada, pronto, início, payload, epoch, polling, autenticação, transporte, launch ou reuso GPU foi alterado nesta correção visual. O novo APK e sua conferência física ficam com o responsável pela entrega; as provas de drawable do autor usam stubs e não validam pixels Android.

## Evidência consultada e limites

O recibo do autor `evidence/room-compact-r123.json` corresponde aos hashes finais e registra **3.203 casos / 23.202 verificações**, mais **332 casos de drawable / 1.640 verificações** e **100 guardas**, além de compilação das duas classes reais com API34. São provas isoladas no host; não foram reexecutadas por este revisor.

O recibo do carrossel `evidence/carousel-geometry-r123.json` também corresponde a todas as fontes finais conferidas e registra **81.435 verificações de geometria / 64 de preferência / 19 guardas / 512 verificações da bridge**, link isolado da bridge Android26 e syntax NDK do carousel/frontend; o painel final tem sua própria compilação API34 atribuída acima. O recibo não afirma link integral do APK ou desempenho/qualidade visual observados no aparelho.

Compilação integral, APK e instalação ficam com o responsável pela entrega. Conferência física do layout, escalas de fonte, fluxo entre aparelhos, gameplay e consumo ainda depende de evidência Android. Não se afirma ausência de ANR, estabilidade de partida ou redução térmica por comparação estática.
