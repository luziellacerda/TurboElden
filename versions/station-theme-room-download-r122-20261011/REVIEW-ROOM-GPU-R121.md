# R121 — reuso das capas online e ciclo de vida EGL

## Evidência e alcance

O Android registrou ANR de despacho de entrada na tela **Sua sala**. A pilha da thread principal aguardava `DrawFrameTask::drawFrame`/`HardwareRenderer.nSyncAndDrawFrame`; não estava executando requisição HTTP. A `RenderThread` aguardava um mutex interno do driver Adreno durante criação de programa. No registro posterior à instalação final R120, dois `Station-cover-GLES` estavam respectivamente em compilação e link de shaders. O registro anterior à instalação final já continha a espera HWUI e um Worker em link. O padrão é herdado; a evidência não identifica o dono do mutex nativo nem prova uma causa única do ANR.

O SIGSEGV Vulkan/SDL anterior à instalação final é um evento distinto. Capturas, números de aparelho, identificadores pessoais e logs completos permanecem privados; este documento registra somente conclusões agregadas.

## Correção de produção

Somente duas fontes Java foram alteradas por esta correção:

| Fonte | Mudança |
|---|---|
| `java/netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java` | `RoomRow`, `roomCoverCard`, `beginRoomRows` e `reconcileRoomRows` conservam o card por tipo, identidade da sala/convite e jogo. |
| `java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineCoverView.java` | `GpuLifecycle`, bootstrap assíncrono e cancelamento coordenam inicialização/liberação dos Workers. |

Na mesma sala e no mesmo jogo, o `StationCreateGameCard`, seu ancestral e seu `TextureView` continuam anexados. São atualizados os textos, participantes e ações do snapshot atual; somente o corpo de ações é reconstruído. Convites e salas da lista também conservam a superfície por identidade. Reordenação usa `bringChildToFront`, sem remover e recolocar o card preservado. Cards que desapareceram são descartados e saem do mapa; não há retenção ilimitada de páginas antigas. A conclusão de uma carga de capa é aceita somente se a mesma instância ainda pertence ao mapa. Uma capa já carregada não é solicitada novamente a cada revisão.

Cada capa mantém seu Worker e seu contexto EGL. O gate exclusivo abrange apenas inicialização/compilação e teardown; desenhos normais permanecem independentes, com a cadência existente de 34 ms. `close` marca cancelamento imediatamente e registra a liberação pendente por contador atômico, sem pegar o gate EGL na UI. Uma inicialização não começa enquanto houver liberação pendente: retorna ao fluxo de quadros já existente, sem aguardar uma tarefa que possa estar atrás dela no mesmo Handler. Uma chamada de driver já em execução não é interrompida; ao retornar, o Worker verifica cancelamento antes de continuar ou publicar a capa.

O Handler é publicado em `onLooperPrepared`; o construtor não aguarda `HandlerThread.getLooper` na thread principal. Uma fila concorrente pequena entrega somente as tarefas recebidas durante o bootstrap. `onSurfaceTextureDestroyed` conserva `false`; o Worker libera o `SurfaceTexture` após seu último trabalho e teardown. Essa posse explícita segue o [contrato Android de SurfaceTextureListener](https://developer.android.com/reference/android/view/TextureView.SurfaceTextureListener#onSurfaceTextureDestroyed(android.graphics.SurfaceTexture)).

`eglTerminate` foi preservado e agora depende de `displayInitialized`, marcado somente após `eglInitialize` retornar sucesso. A [implementação Android de egl_display.cpp](https://android.googlesource.com/platform/frameworks/native/+/master/opengl/libs/EGL/egl_display.cpp), blob consultado `b1a287fcecab124516dfeed979b5b8db9958f1a0`, possui referências de inicialização e liberação do display. O contrato EGL genérico, isoladamente, não demonstra que o teardown antigo necessariamente invalidava a HWUI. Não foi feita essa atribuição causal.

## Preservação

Os corpos de `createRoom`, `prepareRoom`, `join`, `joinConfirmed`, `startDialog`, `launch`, `action`, `command`, `deliver`, descoberta multiplayer e paginação são iguais à base R120. Os callbacks de comando são preservados. Tickets, validação, autenticação, protocolos, recovery, slots de 2–5 jogadores, motores e controles não foram alterados.

Também foram conservados shader, modelos de plataforma, uniformes/ganho, desenho final, quota incremental, cache de campo, foco, visibilidade fora da tela, preferências gráficas, fila/caches das capas e vídeos locais. As medidas/cores/fontes pertencem às mudanças de apresentação separadas desta R121; esta correção não as redefiniu.

## Verificações realizadas

Receita `tests/verify_room_gpu_reuse_r121.py` extrai os corpos reais da produção sem modificar suas instruções e os executa em Java com stubs de hierarquia, Handler e liberação EGL:

- **6.939 verificações de reuso:** 600 atualizações da mesma sala/jogo, reordenação sem detach, troca de jogo/sala, páginas removidas, identidades duplicadas, callback atrasado rejeitado e retry após ausência de capa.
- **46 verificações de ciclo de vida**, incluindo **400 inicializações concorrentes**: no máximo uma compilação/init simultânea, prioridade de liberações pendentes, desligar/ligar antes da liberação, close idempotente, falha de init, bootstrap e close antes do Looper pronto.
- **1.211 verificações de balanço EGL:** falha de initialize não termina o display; 200 ciclos bem-sucedidos terminam exatamente uma vez cada.
- **45 guardas de código:** contrato preservado, callbacks, ausência de detach do card equivalente, posse de SurfaceTexture, bootstrap sem espera, política visual e cadência.

Recibo: `evidence/room-gpu-reuse-r121.json`, com hashes das duas fontes e da receita. O módulo completo de salas/dependências, **184 fontes Java**, compilou contra Android 34 e a API client R120; recibo `evidence/room-module-javac-r121.json`. Nenhum arquivo Java de produção novo foi necessário.

## Limites e próxima conferência

Os stubs não executam HWUI, driver Adreno ou shaders reais. A compilação inicial ainda pode ser cara em um driver específico; esta alteração elimina recriações redundantes demonstradas e controla concorrência/cancelamento. Não confirma redução de temperatura, ausência definitiva de ANR, sessão online estável ou gameplay. A compilação do APK e a conferência física da R121 são etapas do fluxo principal, com seus próprios recibos.
