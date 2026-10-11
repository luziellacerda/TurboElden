# Entrada PSX com o owner normal

A entrada chama o `LibretroPlayer::run(const std::string& coreAbsolute, const std::string& romAbsolute)` estático real do `libmain.so` normal. Não chama o SDL_main do catálogo, não instancia um segundo core e não usa StationRetroActivity. O owner não foi reconstruído de fonte C++: a biblioteca original é reutilizada com guardas SHA/segmentos e o adaptador específico atua apenas no processo privado. O offline não recebe hooks.

## Arranque comprovado no ELF

1. Activity SDL original em `:station_psx_online`, bibliotecas SDL2/main/bridge. Autorização somente após descritor privado revalidado e Binder da sala confirmado. Não força StationLogin.ready.
2. `FileSystem::setHomePath` privado, `AndroidBridge::init`, Settings, instalação do adaptador e `Renderer::init` reais. O run recebe core absoluto; ele não resolve comando libretro.
3. Player inicializa áudio (`SDL_INIT_AUDIO` em 0x2ab0f8; OpenAudioDevice em 0x2ab1c8). O helper chamado em 0x2ab49c inicializa GAMECONTROLLER (0x2b6ea4) e abre os gamepads (0x2a7cc8). O caller normal desmonta InputManager antes do run; não criamos outro InputManager.
4. Font::get em 0x2ab934 pede `:/sst_medium_condensed.ttf`. ResourceManager tenta primeiro HOME/.emulationstation/resources. Launch copia o asset original e JNI exige seu SHA antes de Renderer/owner.
5. Settings lê Player1Controller/Player2Controller e o bool de apresentação LibretroStretch em0x2a9cfc. Launch copia apenas essas duas strings e esse bool validado do HOME normal `Environment.getExternalStorageDirectory()/EmulationStation/.emulationstation/es_settings.cfg`. Não copia saves, BIOS, catálogo ou opções do core offline para a sessão.

O asset game_controller_db.txt existe, mas o owner normal não importa GameControllerAddMappingsFromRW; a inspeção não provou que esse arquivo seja usado no arranque. Não introduzimos novos mappings que diferem da rota normal.

## Processo e saída

YuzuApplication do APK continua no manifesto. A fábrica escolhe Application básica somente se API>=28 e processName for exatamente `org.turboramastation.frontend:station_psx_online`. Todos os outros processos executam a fábrica original. Isso evita no PSX o PlatformAssets/installKeys/Freedreno do initializer Yuzu, que não reconhece esse nome novo.

O JNI chama onOwnerThreadStarted no próprio SDL_main antes da espera de preparação. A Activity conserva a Thread real: o SDLMain original limpa mSDLThread antes de chamar finish, então null sozinho não prova término. A autorização humana apenas permite encerrar; Session primeiro aguarda transporte/threads e Binder encerrados, publica humanCleanupComplete e a Activity exige também Thread.TERMINATED (não NEW). Join ocorre em worker, nunca na UI ou na própria SDL thread. Depois super.finish envia RESULT pelo Binder e só o PID exatamente :station_psx_online é encerrado; falha não autoriza encerramento. A prova JVM de24checks está em evidence/human-exit-gate.json.

Os dois hooks SDL são opt-in por tipo da Activity. O gate exige Session.authorizedToStart; onDestroy inesperado não manda SDL_QUIT nem faz join na UI. Back/Menu/Guide exibem confirmação; somente o positivo humano autoriza o owner, encerra o transporte e deixa o SDL retornar. Falha de preparo ou rede permanece pausada e exige saída humana. O original input/render do SDL/Player permanece.

## Interface JNI

StationPsxBridge.nativeStatus devolve exatamente20 long: coreReady,failed,localPaused,humanAuthorized,epoch,controlSerial,nextFrame,stateSerial,paused,stateReady,inFrame,applyingState,closed,pauseAckValid,pauseAckEpoch,pauseAckSerial,pauseAckNextFrame,pauseAckStateSerial,initialStateSynced,drained.

RendererReady é apenas infraestrutura; CoreReady confirma load/estado reais mas não é READY da sala. ACK exige checkpoint real do owner no epoch/serial. Cada serial novo revoga a execução; Resume exige ACK daquele serial, STATE aplicado e filas drenadas. nativeTakeCommit distingue eventos de execução/aplicação da confirmação de bytes copiados (nativeCopied/nativeReleaseReceipt). Nenhuma chamada JNI IO executa core ou aplica snapshot.

## Reprodução

`recipe/build_entry.py --ndk <NDK28c> --owner <fontes-owner> --protocol <fontes-PXL1> --pinned-options <diretório-PsxPinnedOptions.h> --out <temporário>` compila ARM64/API28/O2/C++20, compartilha libc++ e exige LOAD16KiB/no-undefined. Confere os15 exports JNI, SDL_main/JNI_OnLoad e impede fonte alterada durante compilação. Não liga ou modifica libmain/SDL2/core donors.

`recipe/assemble_optin_dex.py --apk <R126-exato> --jdk <JDK17> --apktool <JAR-exato> --out <temporário-novo>` reproduz as partições completas com os três helpers Java incluídos nesta pasta; o workflow e os hashes estão em `recipe/OPTIN-DEX-WORKFLOW.md`. `patch_sdl_optin.py` e `patch_factory_optin.py` recebem smali original separado e escrevem saída distinta. As provas de inverso byte idêntico e montagem em DEX estão em evidence. As partições completas classes6/28 preservam50/271classes;49/270fontes de classes são byte idênticas ao donor e somente SDLActivity/StationComponentFactory possuem hooks opt-in. DecodeOneClass lê somente uma classe de um DEX do APK, não extrai mídias nem participa do workflow completo.

As provas são compilação/ABI/assemblagem e mocks isolados. Não houve execução Android, BSP-D3, jogo real, sincronização física, teste térmico ou instalação nesta frente. A inclusão em APK final, identidade/cadastro e teste em sala real pertencem à montagem final.
