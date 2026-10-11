# Revisão independente do fluxo online e das saídas — R121

Revisão de fontes R120/R121 e dos registros privados já capturados em 11/10/2026. Nenhum teste novo, compilação, operação Android, operação de servidor ou alteração produtiva foi realizado nesta revisão. O recibo agregado está em `evidence/online-flow-exit-static-r121.json`; não contém sessões, seriais, caminhos de jogos ou pilhas privadas completas.

## Resultado e alcance

Os 22 arquivos de autoridade/transporte/preparação examinados são byte idênticos à R120. Os 14 métodos de escolha, ações, criação, entrada, início, lançamento e saída comparados em `StationRoomsActivity` têm texto idêntico, após normalizar apenas finais de linha. A R121 muda a apresentação e o ciclo das capas, não os comandos de sala. A comparação é de fonte: não substitui a conferência do APK final.

A leitura não identificou um novo deadlock Java ou um novo HTTP/hash de ROM na UI no caminho dos botões. Há pontos de espera/IO herdados que devem continuar documentados; não se pode afirmar que todo esse caminho é livre de bloqueios. A amostra física aponta para espera de renderização, sem provar causa exclusiva ou estabilidade após a correção.

## ANR capturado: o que a pilha mostra

- Evento de entrada: `StationRoomsActivity`, espera de **5.002 ms** por MotionEvent; dump às **23:57:32 de 10/10, UTC−03** (**02:57:32 UTC de 11/10**).
- A UI é `tid=1`, renomeada **SDLActivity**, não uma thread chamada literalmente `main`. Está em `HardwareRenderer.nSyncAndDrawFrame` → `DrawFrameTask::drawFrame` → `pthread_cond_wait`.
- RenderThread está em `GrGLProgramBuilder::CreateProgram` e espera um mutex dentro do driver Adreno. O dump não identifica o proprietário desse mutex.
- Dois Workers `Station-cover-GLES` estão em `glCompileShader` e `glLinkProgram`. A convergência justifica reduzir recriação e serializar init/teardown; não prova um ciclo de deadlock do driver.
- A consulta HTTP de events está em `pool-5-thread-1`. Sua leitura de socket não aparece na pilha da UI capturada.
- O SIGSEGV de **23:54:07.998 local**, thread VulkanWorker, é separado. O recibo R120 registra atualização do pacote às **23:54:51** e conferência UTC às 02:54:58; portanto esse crash anterior não é evidência de falha da R120 final instalada.

## Caminho completo: trabalho e dono da execução

| Etapa | Interface | Trabalho fora da interface | Observação |
| --- | --- | --- | --- |
| Abrir online | Constrói views e inicia conexão | Executor `events`: enter, heartbeat e events; executor agendado: capabilities/snapshot | Ciclo de vida/epoch invalida retornos antigos. |
| Escolher jogo | Percorre catálogo/motores já em memória, monta adapter e troca seleção | Fila existente de capas: armazenamento/HTTP, leitura limitada e decode | A montagem do adapter ainda é CPU na UI; não foi cronometrada. |
| Criar → escolher modo/capacidade | Exibe opções verificadas e fixa contexto | Executor `commands`: consulta de perfis assinados | Sem consulta de rede por linha de sinopse ou participante. |
| Confirmar criação | Desabilita ações e mostra progresso | `commands`: edição instalada, identidade/ROM/core/runtime SHA, perfil e capacidade | SHA e leitura de ROM não são executados pelo botão na UI. |
| Criar efetivamente | Só navega após confirmação | `commands`: um comando create e validação da resposta | Sem replay automático de create. |
| Aceitar/entrar | Confirma jogo, geração e perfil | `commands`: prepare antes de leave/join, resposta e membership | Uma falha local preserva a sala anterior antes do leave. |
| Estou pronto | Botão envia ready com sala/geração fixadas | `commands`: ação única; novo snapshot | Participantes vêm da sala assinada, não da página de pessoas. |
| Iniciar | Mostra os participantes e confirma contexto | `commands`: revalida último snapshot e envia start uma vez | Não inicia por status de capa ou informação descritiva do catálogo. |
| Preparar/lançar | UI só recebe Intent quando a preparação termina | `commands`: tickets, bindings, configs/overlays/autoconfig/BIOS e fsync | O consumo posterior do pequeno launch JSON ocorre na NativeActivity; ver limites abaixo. |
| Conectar a partida | NativeActivity, vínculo Messenger e painel de conexão | Serviço principal: autoridade HTTP; tunnels: socket/WebSocket e filas | Serviço não faz HTTP no Handler principal. |
| Sair da sala | Registra intenção humana e termina Activity | Presença executa saída remota posteriormente | A saída v3 mantém um commit local síncrono. |
| Sair da partida | Confirmação humana chama o callback existente | Autoridade envia leave em executor; teardown nativo permanece no dono original | Apresentação não altera protocolo, saves, slots ou emulador. |

## Guardas semânticas lidas e preservadas

Estas condições são inspeção de código; não são um novo resultado de testes.

1. `StationRoomState.accept`: instance válida e fixa; revision antiga é recusada.
2. `deliver`: só aplica retorno se Activity ativa e generation/epoch coincidem.
3. `paint`: recusa revision antiga, página de pessoas/salas diferente e apresentação já pintada.
4. `action`: busy/active/client/state antes de enfileirar; uma execução de `work.run`, sem laço de retry de mutação.
5. `createRoom`: precisa de item selecionado, nenhuma sala atual e contexto ainda igual ao abrir opções.
6. `confirmRoomSetup`/`prepareRoom`: perfil permite a capacidade e contexto/seleção continuam iguais.
7. `sameRoomSetupProfile`: item, conteúdo, engine, core, runtime, profileId/hash, mode, controllerProfile, maximum e allowed precisam coincidir.
8. `StationOnlineGame.prepare`: ROM e bibliotecas locais devem corresponder às identidades assinadas; extensão também é verificada.
9. `createVerifiedRoom`: verifica item/capacidade, confirmação da criação, anfitrião/membership e identidade antes de navegar.
10. `joinConfirmed`: prepare antes de leave; mudança de sala só se a anterior continua solo/waiting; geração/perfil e membership da resposta são conferidos.
11. `command`: captura roomId e generation exibidos para ready/leave; não infere sala pelo índice da lista.
12. `StationRoomStartState`: apenas anfitrião, waiting, participantes distintos/slots válidos, quantidade permitida, todos ready e transporte autorizado.
13. `roomConfirmationKey`/`updateStartState`: mudança de instance/sala/item/geração/perfil/hash/capacidade/roster invalida a confirmação aberta.
14. Callback Iniciar revalida reason e a chave de confirmação no worker, imediatamente antes do comando start.
15. `StationLaunchPolicy` e `launch`: estado elegível, geração válida, sem recoveryStarted indevido; launchKey e LaunchReturn impedem lançamento duplicado.
16. Tickets: ligação, protocolo, caminho, expiração, geração, jogo, hash, papel/slot e número de links são conferidos.
17. UI do lançamento: active/epoch ainda iguais antes de `startActivityForResult`; arquivo órfão é descartado e binding abortado quando necessário.
18. `StationSessionService`/`StationSessionLink`: sendingUid do próprio app e identidade anchor/sala/geração/attempt; não há cast local de Binder entre processos.
19. Polls transitórios repetem somente leitura; TLS/assinatura/autorização/cancelamento/falha terminal param o ciclo. create/join/ready/start não entram nessa política.
20. Saída: evento 4 é ação humana; desaparecimento do vínculo local não equivale a leave remoto. Evento 6 comunica falha separadamente, com lógica idêntica à R120.

## Paint, locks e capas

`action` pode produzir dois paints de conclusão: `deliver` publica a resposta, depois o callback limpa busy, executa conclusão e força `painted=-1`. Isso é herdado e serve à atualização dos botões; não foi removido por esta revisão. Em R120 esses paints recriavam o cartão/capa da sala. Em R121 atualizam o conteúdo das ações mantendo `RoomRow` e a TextureView por identidade de tipo/id/item.

`roomRows` não altera o snapshot ou a autoridade. Callbacks de imagem conferem identidade da linha; linhas removidas limpam bitmap antes do detach. `bringChildToFront` conserva o ancestral e a superfície nas mudanças de ordem. O próprio cartão continua usando o bitmap do hero; `setImageBitmap` retorna cedo para a mesma instância.

A revisão encontrou que o construtor R120 chamava `HandlerThread.getLooper` na UI, que pode esperar a inicialização do Looper, conforme o [contrato Android](https://developer.android.com/reference/android/os/HandlerThread#getLooper()). A fonte final R121 elimina essa chamada: publica o Handler em `onLooperPrepared` e usa fila concorrente apenas durante o bootstrap, sem espera da UI. O recibo desta revisão já usa essa fonte final.

O gate EGL da R121 é adquirido somente nos Workers para init/teardown. A UI reserva liberação por contador atômico, publica tarefa e retorna. Uma inicialização não espera uma liberação pendente no mesmo worker. Draw continua independente; serializar init não elimina toda contenção potencial do driver/HWUI. `displayInitialized` impede terminar um display cujo `eglInitialize` não teve sucesso; isso preserva o balanço da referência EGL compartilhada.

Não há `Future.get`, latch await ou join na UI dos botões examinados. Os awaits de conexão/crédito e socket read/write estão nos workers dos tunnels. `StationRoomState` tem locks curtos em memória; `StationOnlineClient.compose` clona JSON sob seu próprio lock no worker. `StationSessions` pode esperar empréstimos/renovação HTTP sob seu monitor, mas os caminhos examinados o chamam nos executores de rede. A UI não adquiriu esse monitor no ANR observado.

Os callbacks mutantes do multiplayer tunnel para `StationMultiplayerSession` ocorrem depois de sair do gate do tunnel. A leitura não encontrou uma inversão concreta Session↔gate nesse caminho. Chamadas JNI de status/stalled sob o gate continuam existentes; a implementação completa do runtime preservado não foi alterada nem executada por esta revisão.

## Pontos residuais herdados: não atribuir ao ANR sem evidência

| Ponto | Código | Limite |
| --- | --- | --- |
| Saída explícita v3 | `StationRoomsActivity.exitRooms`: SharedPreferences.commit sob `StationRoomLeaveIntent.class` | Pequeno IO síncrono para preservar a intenção humana. A duração não foi medida. |
| Consumo do lançamento | `StationRetroActivity.onCreate` → `StationRetroLaunch.consume` | Leitura local limitada a 16 KiB, canonical path, delete e JSON; sem HTTP/ROM SHA, porém na UI. |
| Inicialização do motor | `StationRetroActivity.onCreate`: loadLibrary/NativeActivity preparation; criação de sockets loopback/TLS | O motor próprio continua dono do bootstrap. A duração nesta tentativa não foi medida. |
| Descarte/segredo | `StationRetroLaunch.discard`/`clearSecret` chamados pelo lançamento/saída | Delete de arquivo pequeno na UI em alguns caminhos. |
| Cancelamento | `StationApi.Cancellation.cancel` → `HttpsURLConnection.disconnect` | Abort síncrono sob monitor de cancellation; usado também no lifecycle da UI. Não houve essa pilha no ANR. |
| Montagem de escolha/paint | Adapter do catálogo e textos/ações/roster em memória | CPU de UI permanece; não há uma medição de pior catálogo nesta revisão. |

Esses itens são limites reais de escopo, não diagnóstico de que causaram os 5.002 ms. Não foi pedido nesta revisão trocar a persistência de saída, bootstrap nativo, autenticação ou transporte.

## Menus de saída efetivamente alcançados

`StationExitPanel.create` possui um chamador produtivo: `StationRetroActivity.showExitMenu`. Entram por Back, Menu, ButtonMode/Guide, callback de Back API33 e botão de menu do online. `StationExitPanel.confirm` também é usado pelo botão Sair do painel de conexão. Continuar apenas dismiss; Sair chama `requestHumanExit` existente. O runtime online tem `menu_driver=null`; este painel não redesenha o menu interno do RetroArch nem os menus de outros processos.

`native_pause_menu.h` é apresentação do pause do **LibretroPlayer original da libmain**: painel/ações interceptados por caller `0x2af34c`/`0x2afe40`; texto do caller `0x2bc1cc`, hook da função `0x2e9304`. Não altera dispatch/touch/enabled state/save/exit. É alcançado quando a cadeia de lançamento termina no LibretroPlayer original, não quando um bootstrap externo inicia outro motor.

| Dono | Plataformas/rota | Fonte do dono do menu nesta R121 |
| --- | --- | --- |
| StationRetroActivity / StationExitPanel | Fluxo StationRooms online autorizado, runtime `station_retroarch` | Java do painel/callback está presente. Runtime integral upstream não está neste snapshot; binário preservado. |
| LibretroPlayer da libmain | Fallback original: GB/GBC/GBA/NES/FDS/Master System/Game Gear/PC Engine/CD/SuperGrafx/PS1/32X/3DS e cores fallback disponíveis | Hooks de apresentação `native_pause_menu.h`/`native_skin.h` presentes; implementação original e touch/action ficam no binário libmain. |
| Snes9x EX+ | SnesBootstrap → `com.imagine.BaseActivity`, processo `:snes` | Somente rota nativa local; menu EX+ integral não está aqui. |
| MD.emu EX+ | MegaBootstrap → `com.mdimagn.BaseActivity`, processo `:megadrive` | Somente rota nativa local; menu EX+ integral não está aqui. |
| Flycast | Dreamcast/Atomiswave/Naomi → NativeGLActivity, `:flycast` | Rota local; NativeGLActivity/menus upstream não estão aqui. |
| Dolphin | GameCube/Wii → EmulationActivity, `:dolphin`; netplay próprio pelo wrapper StationDolphinNetplayActivity | Wrapper e helper de presença estão presentes; EmulationActivity/EmulationFragment/menu próprios não estão aqui. |
| Cemu | WiiUBootstrap → `info.cemu.cemu.emulation.EmulationActivity`, `:wiiu` | Rota local; Activity/menu Cemu não estão aqui. |
| Mupen64Plus AE | N64Bootstrap → GameActivity/CoreService, `:n64core` | Rota local; menu/Activity upstream não estão aqui. |
| PPSSPP | PspBootstrap → PpssppActivity, `:psp` | Rota local; menu PPSSPP próprio não está aqui. |
| MAME4droid | Arcade/CPS/NeoGeo → MAME4droid, `:mame` | Rota local; Activity/menu próprios não estão aqui. |
| ARMSX2 | PS2/BR → bootstrap e Activity próprios | Rota local; Activity/menu ARMSX2 não estão aqui. |
| Yuzu | BootstrapActivity → EmulationActivity, processo principal | Component factory delegada/helper presentes; Activity/Fragment/menu upstream não estão aqui. |
| Saturn/Vita3K/x1box/xemu/Xendroid | Bootstraps/Activities próprios | Rotas locais, menus próprios em DEX/bibliotecas preservados; fonte integral dos donos ausente nesta revisão. |

Referência da cadeia/DEX/componentes: `LAUNCH-AUDIT-R120.md` e `evidence/launch-matrix-r120.json`, herdados da R120. Os headers privados de rota disponíveis no diretório local não são fonte dos menus upstream; não devem ser confundidos com cobertura de apresentação universal. As oito dependências fallback ausentes no Motorola continuam uma limitação histórica da matriz, sem troca de motor nesta tarefa.

## Limites finais

Esta revisão cobre o fluxo de código, a convergência da amostra de ANR, a apresentação R121 atual e os donos reais de saída. Não comprova eliminação de ANR, tempo de shader, qualidade final no aparelho, gameplay, latência de rede, aquecimento ou redesenho de todos os emuladores. A compilação/empacotamento final precisa conferir fontes/manifestos fechados e preservação de runtime, engines, manifesto, assinatura e entradas não autorizadas.
