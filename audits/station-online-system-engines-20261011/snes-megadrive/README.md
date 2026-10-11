# SNES e Mega Drive — emuladores próprios no online

Auditoria de 11/10/2026 sobre R126 e fonte normal atual. Nenhum APK, rota, biblioteca offline, preferência, save, licença ou código congelado da R126 foi alterado por este trabalho. Não houve conexão ao servidor nem operação de telefone.

## Conclusão verificável

O modo normal usa **Snes9x EX+** para SNES e **MD.emu / Genesis Plus GX** para Mega Drive. O online R126 continua usando **bsnes / StationRetroActivity** e **clownmdemu / StationRetroActivity**, respectivamente. São cores e owners diferentes; chamar a Activity normal não cria uma sessão online compatível.

Há fonte atual completa e uma receita nativa local para os dois frontends normais. Portanto, a adaptação é concretamente desenvolvível conservando renderer, áudio, HUD, toque e controle físico originais. **Essa migração ainda não está implementada no APK.** Foi preparado somente um módulo candidato isolado de montagem de inputs, barreira de quadro/epoch e validação inicial de snapshots, descrito abaixo.

As falhas de snapshots identificadas são da fonte normal EX+, não do caminho bsnes/clownmdemu online atual. Não são evidência da causa de uma queda online observada na R126.

## Base exata localizada

| Item | Fonte / identidade |
| --- | --- |
| Upstream | `emu-ex-plus-alpha`, commit `1c12fac5ce49badaadff2e2f210dcc30b89f4943` |
| Arquivo original | SHA256 `c6494137f2dc680eaec5b802089503e1d8301da16d5226a368072f19b77c80ff` |
| Fonte normal atual, com HUD | `E:\ESTUDO APK\work\station-hud-lzgames-20261003\source` |
| SNES offline atual | `libsnes9x_explus.so`, 3.802.928 bytes, SHA256 `3adeeabe25117265cdd10138fc9631c58da7deda533ff0272a89d7e64bb77956` |
| MD offline atual | `libmdemu_station.so`, 6.755.552 bytes, SHA256 `889d18461fc14e765813d7ef197ecfc922786df8f1f961dd82443dd88aecd124` |
| Receita nativa existente | `versions/station-current-r55-20261006/exit-menus/build_native.py` e `select_engine.py` |
| SDK atual | `station-hud-lzgames-20261003/sdk/android-arm64`; Imagine/EmuFramework, módulos C++, libc++ e dependências de áudio/arquivo |
| Ferramentas | LLVM 22.1.8, CMake 4.4.2, Ninja, sysroot NDK r28c, ARM64/API26 |

As bibliotecas locais conferem com as entradas normais do APK R125. O empacotamento R126 conserva essas entradas. A preflight desta auditoria compara novamente os SHA das entradas pequenas diretamente no R126; não extrai mídias ou jogos. Primeiros receipts de integração pré-HUD são históricos e não selecionam a base atual.

Os hashes dos pontos de fonte estão em `source-pins.json`, com receipt em `evidence/source-preflight.json`. Qualquer cópia de desenvolvimento deve passar essa preflight antes de aplicar alterações. O namespace JNI e o atlas são selecionados separadamente por SNES/MD na cópia, sem tocar na base normal.

## Rotas reais e diferenças de identidade

| Sistema | Normal | Online atual R126 |
| --- | --- | --- |
| SNES | `SnesBootstrap.launch` → `com.imagine.BaseActivity`, processo `:snes`, metadata `snes9x_explus` | `bsnes-mercury-performance-79d7f9de-mt1-mp5-81b3daa38fb9`, `libstation_bsnes.so` |
| Mega Drive | `MegaBootstrap.launch` → `com.mdimagn.BaseActivity`, processo `:megadrive`, metadata `mdemu_station` | `clownmdemu-d43c2708-mp5-81b3daa38fb9`, `libstation_clownmdemu.so` |

Pontes normais: `versions/snes-explus-20261003/java/org/emulationstation/frontend/SnesBootstrap.java` e `versions/mega-explus-20261003/java/org/emulationstation/frontend/MegaBootstrap.java`. Elas entregam caminho e diretórios; não contêm descriptor Station, ponte de input, epoch, transporte ou owner de sessão.

No donor SNES, `BaseActivity.smali:2398` chama `consumeGamePath` em `intentDataPath`; `onCreate` é final e chama `NativeActivity.onCreate` em `:3299`. A biblioteca normal é escolhida pela metadata da Activity. A API de caminho atual não deve ser confundida com seleção/validação de uma variante nativa online. Uma nova entrada/receita precisa validar descriptor e escolher metadata/biblioteca antes dessa criação, preservando o contrato JNI original. Isso ainda não foi implementado.

## Pontos nativos reais para o adaptador

As referências abaixo são da árvore normal atual pinada, relativas a `source/`.

| Necessidade | Ponto exato | O que já existe |
| --- | --- | --- |
| Owner de emulação | `EmuFramework/src/EmuSystemTask.cc:42` | Thread própria/event loop; commands Suspend/Resume/Exit |
| ACK de suspensão existente | `EmuSystemTask.cc:76`, `:133`, `:142` | O worker recebe comando e reconhece por semáforo; o Station epoch/serial ainda não existe |
| Agendamento | `EmuSystemTask.cc:376` e `:443` | `advanceFrames` calcula quadros e chama `sys.runFrames` |
| Quadros ocultos | `EmuFramework/src/EmuSystem.cc:571`, `:580` | `runFrames` pode emular vários quadros, alguns sem vídeo; fast-forward também usa esse caminho |
| SNES quadro real | `Snes9x/src/main/Main.cc:310`, `:349` | `S9xMainLoop`, vídeo e áudio originais; `S9xDeinitUpdate` em `:361` |
| SNES input real | `Snes9x/src/main/input.cc:36` | `deviceId` → `S9xGetJoypadBits(player)`; toque/controle físico têm esse mesmo destino |
| SNES estados | `Snes9x/src/main/Main.cc:116`, `:138` | Freeze/unfreeze em memória, sem novo loop de emulação |
| MD quadro real | `MD.emu/src/main/Main.cc:57` | `RAMCheatUpdate`, `system_frame`, `audio_update` e `EmuAudio` originais |
| MD input real | `MD.emu/src/main/input.cc:32`, `:41` | `deviceId` → `playerIdxMap` → `input.pad[]` |
| MD estados | `MD.emu/src/main/Main.cc:103`, `:108` | `state_load` / `state_save` em memória |
| Saves/config | `EmuFramework/src/EmuApp.cc:314`, `:335`, `:558`; `AutosaveManager.cc:46`, `:56` | Config/autosave/SRAM normais, incluindo gravação ao ir para segundo plano |
| Estado manual pelo HUD | `EmuFramework/src/gui/StationHudView.cc:365` | Menu original chama save/load; precisa guarda somente na variante online |

### Controles e periféricos

O SNES moderno não usa o helper legacy 1.4 para joypads: o caminho atual escreve `S9xGetJoypadBits` do core moderno. `SnesKey` em `Snes9x/src/main/system.ccm:41` mantém bits 4–15: A=7, B=15, X=6, Y=14, L=5, R=4; direções/Start/Select nos bits originais. O adaptador deve capturar esses bits sem substituir os botões ou o BSP-D3 por um template RetroArch.

`setupSNESInput` em `input.cc:155` usa joypad no port0 e MP5 no port1, com os jogadores 1–4 nesse multitap. Capacidade técnica do frontend: cinco pads. A quantidade da sala continua dependente do jogo/edição/modo assinado.

No MD, `MdKey` em `system.ccm:33` é convertido para `bit(code-1)` em `input.cc:42`: A=0x0040, B=0x0010, C=0x0020, Start=0x0080 e X/Y/Z/Mode nos bits 8–11. Para dois pads, `playerIdxMap` usa índices 0/4; Team Player usa 0/1/2/3 (`input.cc:148` e `:197`). J-Cart usa mapeamento próprio (`:143`), portanto não é sinônimo de Team Player.

**Diferença de contrato atual:** `StationOnlinePlatformPolicy.maximum` permite SNES=5, mas Mega Drive continua no default=2. `StationMultiplayerProfile` conhece `megadrive-sega-teamplayer-v1` até4, porém rejeita `maximumPlayers > policy.maximum` antes disso. Nenhum teto foi alterado. O candidato testa capacidade nativa MD2/3/4; isso não autoriza salas de3/4 no app atual.

O profile atual de SNES usa controller IDs libretro (`257` para multitap); o profile MD aplica opções `clownmdemu_input_protocol`. Um adaptador EX+ precisa novas opções/identidades canônicas próprias. Não enviar as opções clownmdemu ao Genesis Plus GX ou declarar compatibilidade de estados entre cores diferentes.

## Erros / limitações concretos antes de ligar esses motores ao online

### SNES: retorno de snapshot interpretado incorretamente

`Snes9x/src/main/Main.cc:124` usa `if(!unfreezeStateFrom(buff))`. Em `src/snes9x/snapshot.h:18`–`:24`, SUCCESS=1 e WRONG_FORMAT=-1, WRONG_VERSION=-2 etc. `!(-1)` é falso: esses erros negativos não provocam a exceção desse wrapper.

A futura ponte deve exigir **retorno exatamente igual a SUCCESS**, além de limites de tamanho/hash/formato, e permanecer pausada se o core recusar estado. A prova isolada reproduz a lógica com os valores reais do header; não executa ROM. Não houve correção dos saves offline nesta auditoria.

### MD: decoder de snapshot normal não recebe tamanho do buffer

`MdSystem::readState` em `Main.cc:103` entrega somente `buff.data()` a `state_load`. Em `genplus-gx/state.cc:106`–`:125`, o tamanho é lido do cabeçalho; o caminho raw faz `memcpy(state.get(), buffer+4, -inbytes32)` sem verificar comprimento de origem/capacidade de destino. `INT32_MIN` também não pode ser negado com segurança em int32. `state.h:34` usa `load_param` sem verificar o limite em cada leitura; loaders de VDP/som também precisam região limitada.

Isso torna incorreto expor o decoder normal diretamente a um snapshot recebido de rede, mesmo de um participante autenticado. O candidato só implementa validação do envelope raw e cursor limitado. **Não chama `state_load`, não altera o decoder e não garante segurança dos seus loaders internos.** O trabalho necessário inclui comprimento explícito, validação de cada leitura/subcontexto, formato exato atual e tratamento de falha sem executar o core. Validação do envelope sozinha não é essa correção completa.

### Netplay histórico do SNES não pode simplesmente ser habilitado

`NETPLAY_SUPPORT` não está nas definições da build e os fontes `netplay.cpp`/`server.cpp` não entram no CMake atual. Além disso, `snes9x.h:292` tornou `Settings.NetPlay` / `NetPlayServer` constantes em0, enquanto o código histórico escreve `Settings.NetPlay` em `netplay.cpp:278` e `:839`. Definir somente a macro cria conflito concreto. O frontend atual também não chama `S9xNPWaitForHeartBeat` / `S9xNPGetJoypad`.

O protocolo histórico tem envio de ROM, SRAM e freeze files; não deve ser habilitado indiscriminadamente. MD.emu não possui implementação de netplay/rollback localizada na fonte atual examinada.

### A pausa deve ocorrer no worker e evitar bloqueio do event loop

Um wait de rede sem limite dentro de `runFrame` impediria o mesmo worker de receber `SuspendCommand`, causando risco de deadlock/ANR. A integração precisa uma barreira não bloqueante, desativar callbacks de quadros enquanto está esperando e acordar o owner por mensagem quando chegar input/STATE. Marcar READY na Activity ou apenas chamar a suspensão normal não cria o ACK Station epoch/serial.

Também não basta guardar o único quadro com vídeo: `runFrames`, `skipFrames` e fast-forward podem executar outros quadros. Somente online, o agendamento deve executar exatamente os quadros canonicalmente comprometidos, todos passando pela mesma barreira. O core continua na taxa NTSC/PAL do sistema; 30fps do carrossel não limita jogos.

### Estado/configuração determinísticos e armazenamento

SNES lê relógio do aparelho em `srtcemu.cpp:28` e `spc7110emu.cpp:111`; jogos com esses coprocessadores exigem relógio determinístico fixado pelo profile ou exclusão explícita. Snapshots comuns não demonstram que o RTC é igual. Região, multitap/inputport, VRAM/echo, SuperFX clock, DSP interpolation e cheats precisam do mesmo perfil. MD precisa região/video, pad3/6, Team Player ou J-Cart e cheats igualmente fixados.

`EmuApp` carrega core/session options, autosaves/SRAM e grava configuração ao background. Alterar somente flags em memória e gravar novamente no storage normal mudaria preferências offline. A variante online deve usar diretórios de sessão isolados e apenas importar preferências visuais/controles selecionadas; nenhum save normal pode ser sobrescrito. Estados manuais, rewind, reset e fast-forward unilaterais precisam guarda online nas APIs reais, além de qualquer mudança de UI.

## Candidato isolado comprovado

Diretório: `candidates/station-explus-frame-gate-20261011`.

Implementado e testado:

- montagem de input do anfitrião pelo roster exato; origem autenticada fornecida pelo caller, spoof de slot rejeitado;
- inputs completos por quadro, retry idempotente, conflito rejeitado, fila fixa de32 quadros sem drop/reorder automático;
- owner único, lease por quadro, ACK de consumo somente depois de `complete` pelo owner;
- pausa por epoch/serial reconhecida somente após checkpoint real do owner e fim do quadro atual;
- aplicação de estado por callback no owner, sem lock de rede durante a chamada; falha/exception não habilitam retomada;
- input local em staging separado dos pads comprometidos; bits SNES/MD originais;
- nenhuma desconexão por timeout/input faltante; saída somente após autorização explícita e observação pelo owner;
- guardas do resultado SNES, envelope raw MD sem overflow e cursor limitado, sem expor os decoders normais.

Provas: **82.297 checks** com owners sintéticos, incluindo SNES2/3/4/5, MD2/3/4, memória limitada, input local concorrente, pausa durante quadro e erros de snapshot. O objeto/arquivo estático compilou para **ARM64/API26**, 27.932 bytes; não é ANativeActivity, biblioteca de emulador ou APK. Receipts e hashes estão em `evidence/` do candidato e desta auditoria.

**Não implementado:** hooks nos motores originais, decoder MD limitado em todos os subcontextos, ponte JNI, descriptor/lifecycle/storage Android, transporte/parser WSS v3, profiles/identidades canônicas, registro no servidor ou gameplay. O módulo não está linkado ao Snes9x/MD.emu e não mudou a R126. Não declarar migração, correção de partidas, estabilidade, redução térmica ou equivalência de desempenho com base nessa prova.

O componente invalida sua fila lógica ao reconhecer nova pausa/aplicar estado. A conciliação disso com DATA/IDs ainda pendentes e ACK cumulativo do transporte não faz parte da prova. A futura ponte precisa tratar explicitamente cada payload por epoch/serial; limpar a fila lógica não autoriza perder bytes de um stream. O callback de estado também exige ownership dos bytes válido e imutável até retornar.

## Plano mínimo executável para a migração

1. Copiar fonte/SDK normal atual para uma árvore local nova, conferir manifesto/preflight e compilar SNES/MD sequencialmente com a seleção de namespaces/atlas. Preservar byte a byte as duas bibliotecas offline.
2. Acrescentar biblioteca online com nome distinto e entrada validada antes da NativeActivity. Descriptor fresco, profile/ROM/bibliotecas aprovados, diretórios confinados e vínculo de sessão/result autêntico, sem abrir offline enquanto a sessão online está ativa.
3. Criar endpoint JNI do módulo no mesmo processo do engine. Aplicar perfil e isolar configuração/saves **antes** de `loadSystemOptions`, `loadSessionOptions`, `launchSystem` e autosave; somente o owner toca o estado/core.
4. Integrar montagem/commit de input por quadro no transporte v3, com parser fragmentado/bounded e uniqueDeliveryId real. Validar cada origem e roster. ACK de frame recebido só após consumo real; transferências de snapshot separadas e limitadas.
5. Inserir a barreira no owner e nos quadros reais, guardando skipForward/fast-forward/turbo/reset/load-state unilateral. Remover callbacks enquanto aguarda input e acordar por mensagem do endpoint; sem segundo core loop, polling ou wait de rede no UI thread.
6. Corrigir a validação SNES e a leitura limitada completa MD antes de aceitar estados recebidos. Testar truncamentos, overflow, versões incompatíveis e falha parcial com CPU permanecendo pausada.
7. Gerar novas identidades core/runtime/options/controller/ROM/perfil. Os IDs bsnes/clownmdemu ficam preservados. Três/quatro jogadores MD exigem mudança explícita de política/catalogação autorizada; a capacidade do frontend não substitui suporte do jogo.
8. Validar build de emulador completo/Android, autenticação, saves/controle/offline, pausas reais e ensaio em dois/múltiplos aparelhos; somente então selecionar a nova rota para profile cadastrado. Não desativar o online atual por uma candidata incompleta.

Esse plano descreve alterações concretas sustentadas pela fonte. As etapas restantes estão explicitamente pendentes; não existe código morto/flag que pretenda representar uma ponte já entregue.
