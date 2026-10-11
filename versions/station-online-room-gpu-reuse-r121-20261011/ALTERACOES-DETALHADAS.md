# R121 — alterações detalhadas

## StationRoomsActivity

Reconciliador por identidade do tipo/sala/jogo retém o card e o ancestor da TextureView. Não remove e reinsere a capa em mudanças de prontidão ou participantes. Apenas conteúdo/ações do card são reconstruídos pelo snapshot novo. Linhas removidas saem da hierarquia e liberam seu renderer; callbacks antigos de capa validam a identidade atual antes de aplicar bitmap. A reordenação conserva o ancestor anexado. Ações de criar/entrar/start/launch, validação assinada, paginação e entrega continuam preservadas.

## StationOnlineCoverView

Gate de lifecycle apenas para init/compilação e teardown nos Workers. Contador atômico reserva release na interface; init adia no próprio Worker se houver releases pendentes, usando a cadência existente, sem espera circular. close sinaliza cancelamento imediatamente; checks entre as etapas impedem compilação/fallback/upload após fechamento. SurfaceTexture continua de posse do Worker e só é liberada depois dos jobs anteriores e teardown. Bootstrap publica Handler em onLooperPrepared e drena fila concorrente, sem getLooper síncrono na UI. eglTerminate só sucede eglInitialize bem-sucedido. Android faz contagem de referências do display, preservada com esse pareamento.

Draw, shader, gain, rastro, frequência, light-field incremental, limites de cache, prioridade IO/decode e regras de visibilidade/foco/lifecycle continuam os existentes. O gate não serializa quadros nem entrada do jogo. Compilar o primeiro shader ainda pode custar tempo no driver; não há promessa de primeiro LED instantâneo ou de ausência de contenção de HWUI.

## Capas — StationCoverLayout/CreateGameCard/FlowPanel

Geometria pura usa dimensão recebida da View. Hero limita-se a 30% da largura útil e 86% da altura útil, reserva coluna de conteúdo e gap. Sala/convite usa miniatura de até76×112dp. Confirmação utiliza dimensão do diálogo, sem vincular tamanho à altura física da tela. A imagem e LED preservam a proporção, sem crop/stretch. Fluxo estreito empilha a miniatura; texto/instruções continuam roláveis dentro de sua área. Layout real Android/portrait não foi executado pelo teste matemático.

## Saída online — StationExitPanel e StationRetroActivity

Painel de largura máxima420dp, superfícies carvão, hierarquia textual, ícones, seleção azul/ciano e saída diferenciada. Continuar recebe foco e somente fecha o painel; sair fecha o painel e chama o callback humano original uma vez. Ações ficam lado a lado; telas estreitas/fontes grandes empilham. Alvos mínimos48dp. confirmExit usa o mesmo helper visual; substituição reversível desse único corpo prova que todas as outras partes de StationRetroActivity ficaram byte idênticas à R120.

## Pausa nativa — native/d1/native_pause_menu.h

Paleta/foco/ícones/linhas coerentes com saída online e uma camada de desenho a menos no fundo. Callers e ABI originais conservados. O campo0x30 é ALTURA da linha; a posição antiga0,88×altura já alinhava texto após ícone. A revisão nomeia esse campo, sem alegar que existia deslocamento por88% de largura. Não muda callback, touch bounds, estado enabled, saves, exit ou motor.

## Limites e evidências

Leia REVIEW-ONLINE-FLOW-EXIT-R121 para os pontos de IO/boot/cancel herdados na UI e os donos reais de cada menu. Não foi redesenhado menu de motor cuja fonte integral está ausente. O ANR capturado converge com renderização, mas o dono do mutex Adreno/ciclo de deadlock não foi demonstrado. O crash nativo anterior à atualização final é separado.

Testes de host/revisão não são gameplay nem prova de eliminação de ANR ou redução térmica. Compare os recibos de package/build/installation da R121 e seus hashes; recibos herdados não qualificam este APK. Nenhum servidor, ROM, licença, save, chave de usuário, runtime ou perfil de motor é modificado por esta entrega.
