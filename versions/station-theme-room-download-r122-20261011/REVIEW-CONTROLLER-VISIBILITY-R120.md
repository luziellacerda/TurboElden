# R120 — visibilidade dos controles virtuais por motor

## Escopo e evidências

Auditoria estática das fontes privadas e do APK R119, seguida de uma adaptação Java restrita ao Dolphin. Não houve operação de telefone, teste de Bluetooth/USB, partida, leitura de handoff ou alteração de motores neste trabalho. Reconhecimento de um modelo de controle no Android não comprova que todos os botões, eixos, modos de pareamento ou slots desse modelo funcionem em todos os motores.

O inventário e as prioridades de lançamento são documentados separadamente na auditoria de rotas do responsável pela compilação. As linhas abaixo identificam a família de motor investigada; não escolhem um motor diferente para o sistema nem substituem a prioridade dos hooks atuais. Bibliotecas libretro não são responsáveis pela interface Android: a visibilidade precisa ser ajustada no host que realmente abre o jogo.

As fontes privadas sob `E:` servem para reproduzir a inspeção local e não são copiadas para publicação como mídia ou dependências binárias. A existência de um arquivo antigo numa pasta de integração, isoladamente, não prova que ele esteja na rota ativa do APK.

## Regra Android utilizada

Um controle físico é reconhecido por `InputDevice` não virtual que tenha a máscara completa `SOURCE_GAMEPAD` **ou** `SOURCE_JOYSTICK`. Teclado, mouse, controle remoto que informe apenas DPAD, touchscreen e dispositivos virtuais não acionam o novo adaptador. O número do dispositivo não é usado como slot de jogador.

No novo adaptador, a enumeração inicial e os eventos `onInputDeviceAdded`, `onInputDeviceChanged` e `onInputDeviceRemoved` atualizam a presença. A volta dos controles virtuais ocorre somente depois da remoção do último dispositivo reconhecido. Não há timer, polling por quadro ou troca de mapeamento físico. Referências: [Android: entrada de controles](https://developer.android.com/games/sdk/game-controller/controller-input), [InputDevice](https://developer.android.com/reference/android/view/InputDevice), [InputDeviceListener](https://developer.android.com/reference/android/hardware/input/InputManager.InputDeviceListener).

## Resultado por família

| Família/motor investigado | Detecção encontrada | Ocultação e restauração existentes | Resultado e correção mínima |
|---|---|---|---|
| SNES / Mega Drive — emu-ex-plus-alpha | Enumeração inicial e listener add/remove/change encaminhados ao InputManager. | `VController` em `AUTO` oculta com entrada física e volta ao retirar; opções manuais ON/OFF são respeitadas. | Já existe hotplug. A condição `keyInputIsPresent()` inclui teclado; não equivale à nova regra GAMEPAD/JOYSTICK. Preservar o comportamento atual nesta entrega; uma mudança futura deve restringir a presença no próprio InputManager, sem forçar a preferência manual. |
| GameCube / Wii — Dolphin 2609-7 | O motor já tem listener de dispositivos para o input físico. | Overlay segue `MAIN_SHOW_INPUT_OVERLAY`; não há ligação direta entre esse listener e a visibilidade. | **Adaptado na R120:** suprimir somente `InputOverlay`, liberar seus overrides de toque e restaurar seu layout original no último disconnect. Motor e input físico preservados. |
| Dreamcast / Naomi — Flycast v2.7-44 | InputDeviceManager registra listener; add/change vazios e registro de controle ocorre na primeira entrada. | `VGamepad.show()/hide()` existe; delegate pode mostrar novamente e usa timer de 10 s. `hide()` muda só Visible, e `hitTest()` não consulta Visible. | Gap confirmado nas fontes investigadas. Apenas chamar hide não basta. Ajuste futuro precisa impedir reabertura do delegate e liberar somente pointer/axis virtuais; preservar portas Maple e eventos de menu. **Não aplicado neste ciclo.** |
| Arcade / Neo Geo — MAME4droid Current | Listener remove limpa os IDs conhecidos; add/change vazios. | TouchController consulta `isHideTouchController`; restauração é atualizada ao remover controle conhecido. Teclado/mouse também podem ocultar. | Já há restauração para controles registrados; conexão só se torna efetiva após input. Correção futura: presença independente para apresentação em add/change, sem reatribuir IDs nem apagar mapeamentos. |
| Nintendo 64 — Mupen64PlusAE | Entradas de joystick/key disparam ocultação; há timer de auto-hide. | `GameOverlay.onTouchControlsHide/Show` públicos; Show força a volta de uma camada ocultada, sem getter público que explique quem a ocultou. | Não aplicar watcher genérico: poderia restaurar uma opção manual desligada ou esconder o FPS junto. Necessita flag transitória no proprietário dos controles, preservando estado manual e timer existente. **Não adaptado na R120.** |
| PSP — PPSSPP 1.20.4 | Listener Android informa pad connected/disconnected ao motor. | `ShowTouchControls` é persistente; `TouchButtonHideSeconds` controla opacidade por inatividade, não presença do controle. | Não há comando Java de mudança transitória de visibilidade comprovado nos arquivos lidos. Ajuste seguro exige setter/UI message definido no motor e liberação dos toques; não esconder EGL/gameSurface nem reescrever INI após init esperando efeito imediato. |
| PlayStation 2 — integração ARMSX2 | Fonte upstream NativeApp tem input físico; APK contém `kr.co.iefriends.pcsx2.MainActivity`. | Fonte decoded possui `makeButtonTouch/configureOnTouchListener`; a classe upstream `com.armsx2.ui.touch.TouchControls` não foi encontrada literalmente no DEX atual. | Proveniência do motor e superfície Java precisam ser conciliadas antes de editar overlay. Não concluir capacidade de hotplug a partir de um upstream diferente ou do donor AetherSX2 removido. Nenhum ajuste feito nessa família. |
| Wii U — Cemu Android 0.5.2 | NativeInputDeviceListener e ControllerCallbacks recebem add/change/remove. | InputOverlaySurfaceView recebe `setVisible()` através de StateFlow derivado de SideMenuState. Nenhum gate de presença ligado a esse estado foi encontrado nos arquivos listados. | Listener de mapeamento não prova auto-hide. Ajuste futuro deve ocorrer no proprietário de StateFlow, usando supressão transitória e release touch; chamar setVisible isoladamente pode ser revertido pelo collector. |
| Xbox clássico — wrapper xemu Android | Enumeração inicial, listener add/remove/change e máscara completa GAMEPAD/JOYSTICK. | `shouldShow = !hasPhysicalController`; `onScreenController` volta após último disconnect. | Já implementado no wrapper inspecionado; a regra não exclui `isVirtual`. Confirmar a rota/DEX exatos na auditoria de lançamento antes de prometer comportamento físico. Nenhuma alteração adicional. |
| Xbox 360 — XenDroid | GAMEPAD/JOYSTICK no dispatch de eventos físicos. | Overlay Compose deriva de `show_touch_overlay`; toggle manual persiste a opção. Não foi encontrado listener de presença que suprima essa camada nos arquivos investigados. | Futuro: gate transitório de hardware no Compose, preservando a opção configurada e o dispatch físico. Não persistir OFF na configuração global. |
| PlayStation Vita — Vita3K | Enumera dispositivos não virtuais GAMEPAD/JOYSTICK; listener add/change/remove atualiza estado atual. | `hideOverlayWhenControllerConnected` default true; máscara zero quando conectado e opção ativa; máscara original recuperada depois do último disconnect. | Já tem implementação completa na fonte merged inspecionada. Não adicionar watcher concorrente. Preferência manual permanece respeitada. |
| Saturn — wrapper Yabause | Eventos físicos de key/joystick já separados do touch na classe Pad. | Desenho/toque dependem da opção manual `touch`; não há listener de presença no wrapper lido. | Futuro: flag transitória só para desenho e pointers virtuais. Não usar `releaseAll()`: limpa também `external` e alteraria input físico. |
| Nintendo Switch — Yuzu integrado | Activity listener add/change/remove atualiza InputHandler e notifica Fragment. | Fragment guarda `overlayHiddenByPhysicalController`, oculta com `HIDE_OVERLAY_ON_CONTROLLER_INPUT` e restaura somente quando foi ele que ocultou. | Preservado. Classes/motor foram conferidos separadamente como idênticos R76→R119. R120 corrige a rota de package, sem alterar esse motor/overlay. |
| NES, GB/GBC, GBA, PS1, 32X, PCE/SuperGrafx, PCE CD, 3DS e outras rotas libretro do host integrado | O header de lançamento identifica cores/hooks; não comprova o proprietário do touch do host privado. | Não foi confirmado um setter de visibilidade de touch nessa superfície nativa privada. | Cobertura de overlay ainda depende da rota exata do host e da sua API; não transplantar o comportamento EX+ ou do RetroArch online por nome de core. Não escondemos a superfície de emulação como atalho. |
| Online — runtime RetroArch Station fixado | Driver Android registra/reutiliza portas por input/nome; não foi encontrado listener Java de remoção conectado à visibilidade. | `input_overlay_hide_when_gamepad_connected` decide por `input_config_get_device_name(0) != NULL`; Java do app não expõe setter de overlay em execução. | A configuração inicial não comprova restauração após retirar Bluetooth/USB. Nenhuma ponte segura existente foi confirmada. Alteração do runtime exige código correspondente, hash e registro próprios; **runtime/IDs/protocolo não alterados na R120**. |

## Adaptação Dolphin efetivamente implementada

Arquivo novo: `java/client/src/java/org/emulationstation/frontend/station/StationControllerPresence.java`.

O factory criado pelo responsável principal chama `StationControllerPresence.install()` no Application original. Essa função registra callbacks uma única vez e não consulta serviços antes de o Application ser anexado ao Context. Somente o resume da Activity exata `org.dolphinemu.dolphinemu.activities.EmulationActivity` registra o listener de input. Aplicações e processos dos outros motores são preservados.

O adaptador localiza apenas a classe exata `org.dolphinemu.dolphinemu.overlay.InputOverlay`, confirma as APIs públicas `onDestroy()` e `refreshControls()` e guarda sua visibilidade. Antes de ocultar, envia ACTION_CANCEL e executa o release dos overrides virtuais. ACTION_CANCEL sozinho não é suficiente no tratamento DOWN/UP dessa versão. A camada usa INVISIBLE para preservar geometria; GameSurface, diálogos, teclado, movimento físico e slots não são interceptados.

Na retirada do último controle, o adaptador chama `refreshControls()`, que lê o tipo/configuração/layout original do motor, e restaura a visibilidade anterior. Não grava preferências. Pausa/stop retiram listener e callback de layout; destroy evita chamada ao input nativo que o motor já possa ter descarregado. Um erro na ponte impede ocultação e tenta recuperar os controles. Repetidos layouts não liberam/desativam novamente uma camada que já foi suprimida. Uma camada originalmente invisível ou desligada não é ativada apenas por existir um controle.

### Por que onDestroy do overlay não encerra o emulador

Na fonte específica usada para a auditoria, `InputOverlay.kt:onDestroy` (431–433) chama somente `unregisterControllers` (435–448). Essa função remove os overrides de GameCube/Wii e limpa os indicadores de registro. Não é o `Activity.onDestroy` e não encerra emulação, arquivos, saves, renderização ou recursos do jogo.

`refreshControls` (986+) primeiro remove os mesmos overrides, limpa os drawables virtuais e os registra novamente segundo `MAIN_SHOW_INPUT_OVERLAY` (1003+) e os tipos configurados. No C++ `ControllerInterface/Touch/InputOverrider.cpp:198–224`, Unregister limpa `ClearInputOverrideFunction` e os flags `overriding` dos controles de toque. O caminho de entrada física permanece no controller original.

Fonte oficial correspondente: [Dolphin InputOverlay no commit 5102a033](https://raw.githubusercontent.com/dolphin-emu/dolphin/5102a0339c2177575378107b76541e47cc52122d/Source/Android/app/src/main/java/org/dolphinemu/dolphinemu/overlay/InputOverlay.kt). As linhas locais incluem alterações de integração já existentes, sem mudança nesse par de operações.

### Evidência de teste local

Receita: `tests/verify_controller_presence_r120.py`. Recibo: `evidence/controller-presence-r120.json`.

Resultado: **PASS 68 verificações**, compilando o helper real sem modificá-lo, com stubs Android/Dolphin. Cobre exclusão de teclado/mouse/virtual, conexão inicial, conexão tardia, dois controles e último disconnect, mudança de source, 1.000 callbacks de layout sem release repetido, pause/destroy, overlay separado de GameSurface e falha de release sem ocultação.

É teste isolado de política/lifecycle, não validação de JNI num aparelho, de botão BSP-D3, de Bluetooth, de emulação ou de jogo online. SHA do helper/receita constam no recibo e devem ser reconferidos se o código for alterado depois desta execução.

## Localizadores exatos das evidências privadas

Todos os caminhos desta seção são absolutos e somente de leitura para esta auditoria.

### EX+ / SNES / Mega

Base: `E:/ESTUDO APK/work/station-snes-explus-20261003/source/emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943`.

- `EmuFramework/src/vcontrols/VController.cc:577–608`: setPhysicalControlsPresent/updateAutoOnScreenControlVisible.
- `EmuFramework/src/EmuInput.cc:241–249`: updateInputDevices / keyInputIsPresent.
- `EmuFramework/src/EmuApp.cc:456–474`: enumeração inicial e callback de device change.
- `imagine/src/base/android/inputConfig.cc:300+`: InputDeviceListenerHelper.
- `imagine/src/base/android/imagine-v9/src/main/java/com/imagine/InputDeviceListenerHelper.java:40,62,84,89`: onAdded/onRemoved e registro/unregister.

### Dolphin

Base: `E:/ESTUDO APK/work/native-carousel/implementation/dolphin-integration/source`.

- `Source/Android/app/src/main/java/org/dolphinemu/dolphinemu/overlay/InputOverlay.kt:431,435,986,1003`: release/refaz layout e preferência.
- `Source/Android/app/src/main/java/org/dolphinemu/dolphinemu/features/settings/model/BooleanSetting.kt:279`: MAIN_SHOW_INPUT_OVERLAY.
- `Source/Android/app/src/main/java/org/dolphinemu/dolphinemu/features/input/model/ControllerInterface.kt`: listener físico; não define visibilidade do overlay.
- `Source/Android/jni/Input/InputOverrider.cpp`: ponte JNI de Unregister.
- `Source/Core/InputCommon/ControllerInterface/Touch/InputOverrider.cpp:198–224`: limpar override/overriding; nenhuma saída do motor.

### Flycast

Base: `E:/ESTUDO APK/work/native-carousel/implementation/flycast-integration/source`.

- `shell/android-studio/flycast/src/main/java/com/flycast/emulator/periph/InputDeviceManager.java:21,44,66,70,78,201`: listener e registro por primeira entrada.
- `shell/android-studio/flycast/src/main/java/com/flycast/emulator/emu/VGamepad.java`: JNI show/hide.
- `shell/android-studio/flycast/src/main/java/com/flycast/emulator/emu/VirtualJoystickDelegate.java:39,267`: timer de hide e show.
- `core/ui/vgamepad.cpp:260–268`: flag Visible e hitTest.

### MAME / N64

- `E:/ESTUDO APK/work/native-carousel/implementation/mame-current/donor-decoded/smali/com/seleuco/mame4droid/input/InputHandler.smali:618–680`: isHideTouchController.
- Na mesma integração, `input/GameController.smali:5266,6548` e `input/GameController$1.smali:46,52,58`: isEnabled, registro e callbacks.
- `E:/ESTUDO APK/work/station-n64-complete-20261005/donor/smali/paulscode/android/mupen64plusae`: `game/GameActivity.smali:6787,7977,8310`, `game/GameOverlay.smali:496,545` e `persistent/GlobalPrefs.smali:1371,1387`.

### PSP / PS2 / Cemu

- `E:/ESTUDO APK/work/native-carousel/implementation/psp-integration/upstream/PpssppActivity.java:816+`: listener físico.
- PPSSPP oficial [Config.cpp v1.20.4](https://raw.githubusercontent.com/hrydgard/ppsspp/v1.20.4/Core/Config.cpp): DefaultShowTouchControls, ShowTouchControls, TouchButtonHideSeconds.
- PPSSPP oficial [GamepadEmu.cpp v1.20.4](https://raw.githubusercontent.com/hrydgard/ppsspp/v1.20.4/UI/GamepadEmu.cpp): opacity por last touch; não prova auto-hide na conexão.
- `E:/ESTUDO APK/work/native-carousel/implementation/ps2-integration/upstream/NativeApp.java:510`: referência upstream TouchControls; comparar com classes15 antes de aplicar.
- `E:/ESTUDO APK/work/native-carousel/implementation/ps2-integration/current-decoded/smali/kr/co/iefriends/pcsx2/MainActivity.smali:1043,1873,1998`: makeButtonTouch/configureOnTouchListener; donor histórico, não identificado como suficiente para recompilar o DEX atual.
- `E:/ESTUDO APK/work/native-carousel/implementation/emulator-completion/wiiu-052/donor-decoded/smali/info/cemu/cemu/emulation`: `EmulationActivity.smali:1827–1950` listeners; `EmulationViewModel.smali:37,347` StateFlow; `inputoverlay/InputOverlaySurfaceView.smali:3590` setVisible; `common/input/InputDeviceListener.smali` na raiz `info/cemu/cemu` encaminha add/change/remove.

### Xbox / Vita / Saturn / Switch

- `E:/ESTUDO APK/work/native-carousel/implementation/platform-xbox-pce-refresh/upstream/MainActivity.kt:465–531`: scan/source/add/remove/change e visibility.
- `E:/ESTUDO APK/work/native-carousel/implementation/xbox360-integration/upstream/EmulatorHostActivity.kt:128,266–305,560,718–727`: Compose e toggle; `EmulatorSession.kt:100–101` get/set da opção.
- `E:/ESTUDO APK/work/native-carousel/implementation/platform-media-refresh/psvita/merged/smali_classes23/org/vita3k/emulator/Emulator.smali:5696,7654,7660,7713,7749,7761,7773`: estado e callbacks.
- No mesmo `smali_classes23`, `tvita3kc/shaded/u11.smali:1678` enumera; `tvita3kc/shaded/tg0.smali:418,479–670` aplica opção+connected; `org/vita3k/emulator/overlay/OverlayConfig.smali:120–133,413` default true/getter.
- `E:/ESTUDO APK/work/native-carousel/implementation/saturn-modern/java/org/emulationstation/frontend/SaturnActivity.java:39,146–156`: wrapper, pad físico e virtual; releaseAll limpa também external.
- `C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/switch-audit-readonly-20261010/r119/r119-EmulationActivity.java:642,658,858–879` e `r119-EmulationFragment.java:1305–1323`: código decompilado do classes.dex exato R119; não é fonte autoritativa para recompilar o emulador. A comparação de identidade/semântica é documentada pelo responsável da auditoria Switch.

### Online

Arquivo de fonte correspondente: `E:/ESTUDO APK/work/station-server-integration-r99-20261009/incoming/versions/station-five-player-support-20261009/native/retroarch-corresponding-source.tar.gz` e seu `CORRESPONDING-SOURCE-MANIFEST.json`.

- Runtime preservado: `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc`.
- RetroArch commit: `69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576`.
- `runloop.c:5733–5745`: ocultar/recuperar por device_name(0), unload/init overlay.
- `input/input_driver.c:5360`: lógica equivalente.
- `input/drivers/android_input.c:984,1050+`: recover_port / handle_hotplug por input; os callbacks Java de remoção não estão ligados a um setter público do app.
- Em R119/R120 `StationRetroActivity` expõe JNI de recovery/status/quit/bind/unbind; nenhum setter live de overlay foi confirmado. Preservar IDs de engine, protocolo station-stream.v2, validação, slot online e BSP-D3.

## Limitações e próximos passos delimitados

A R120 não deve ser descrita como conserto universal de todos os controles. Ela acrescenta o adaptador Dolphin e conserva os comportamentos existentes que já tratam presença/restauração nas famílias auditadas. Gaps de N64/Flycast/PPSSPP/PS2/Cemu/XenDroid/Saturn e host privado estão identificados acima, com o proprietário correto onde mudar e a razão de não ocultar indiscriminadamente Views ou superfícies.

Validação necessária no aparelho, a cargo do fluxo principal: iniciar sem controle, conectar um controle real, verificar apenas touch desaparecendo, manter controles físicos e menu original, retirar o último controle e verificar retorno do touch; repetir com dois dispositivos e preferências manuais desligadas. Não declarar gameplay estável, todos os modelos configurados ou runtime online reparado com os testes de stubs.
