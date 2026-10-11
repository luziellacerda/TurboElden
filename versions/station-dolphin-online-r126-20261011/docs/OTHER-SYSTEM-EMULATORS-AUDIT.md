# Auditoria dos outros emuladores do sistema — R126

Data: 11/10/2026. Escopo: leitura das fontes, receitas, DEX/smali e entradas pequenas dos APKs locais. Esta auditoria não recompilou motores, não iniciou partidas, não operou aparelhos e não alterou o código congelado da R126. Somente este documento foi acrescentado.

## Resultado objetivo

A R126 acrescenta a ponte do Dolphin original para GameCube/Wii e preserva a ponte Mupen64Plus AE do N64. **Ela não migra SNES, Mega Drive, MAME/CPS/Neo Geo ou PS1 para os seus frontends normais.** Nessas plataformas ainda existem diferenças reais entre o motor/frontend offline e a rota online.

Há fontes e uma cadeia nativa local concreta para adaptar SNES/MD sem substituir a interface, renderização e controles normais. O adaptador Station desses dois motores ainda não existe. MAME4droid expõe APIs reais de netplay, mas o C/C++ correspondente não foi localizado no conjunto examinado. Para PS1 há o core libretro e a rota normal, mas o dono normal do loop de quadros ainda precisa ser mapeado e ter fonte/ABI exatos estabelecidos.

`launchReady` no manifesto do APK é uma declaração local. Não comprova cadastro/ativação no servidor, conexão efetiva, gameplay ou estabilidade.

| Plataforma | Rota normal existente | Rota online no manifesto R126 | Resultado desta auditoria |
| --- | --- | --- | --- |
| SNES | `com.imagine.BaseActivity`, processo `:snes`, Snes9x EX+ | `libstation_bsnes.so` / StationRetroActivity | Candidato concreto a adaptador nativo EX+, ainda não implementado |
| Mega Drive | `com.mdimagn.BaseActivity`, processo `:megadrive`, MD.emu/Genesis Plus GX | `libstation_clownmdemu.so` / StationRetroActivity | Candidato concreto a adaptador nativo MD.emu, ainda não implementado |
| CPS1/2/3 e Neo Geo cartucho | MAME4droid, processo `:mame` | `libstation_online_fbneo.so` / StationRetroActivity | API MAME de netplay existe; falta fonte/protocolo/gate do motor exato |
| Neo Geo CD | MAME4droid, processo `:mame` | `libstation_online_neocd.so` / StationRetroActivity | Mesmo requisito de ponte MAME; não é uma troca de Intent |
| PS1 | LibretroPlayer normal + PCSX ReARMed | `libstation_online_pcsx.so` / StationRetroActivity | Mapear e adaptar o owner normal de `retro_run`, renderer/input e pausa |

As rotas online restantes mantêm seus IDs, hashes e protocolos. Não foram substituídas por uma Activity offline que desconhece a sessão.

## Artefatos examinados

- APK R125: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R125-20261011.apk`, SHA256 `a3ed815c01fdb0bd06a3a2485991fe8d19a51c63fee0e9255a45ecd8a9b6d4a5`.
- APK R126: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R126-20261011.apk`; identidade registrada em `evidence/package-final-r126.json`, SHA256 `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d`.
- `assets/station-online/engines.json` do APK R126 foi lido diretamente. Foram examinadas entradas de código/proveniência, sem extração de mídias, ROMs ou BIOS.
- `evidence/unsigned-package-r126.json` registra 13.544 entradas preservadas e uma lista fechada de substituições. As bibliotecas offline SNES/MD/MAME/PSX não fazem parte dessa lista.

## SNES e Mega Drive: fonte atual e cadeia nativa local

### Proveniência e fonte efetivamente usada

Fonte original pinada:

`E:\ESTUDO APK\work\station-snes-explus-20261003\source\emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943`

Commit upstream `1c12fac5ce49badaadff2e2f210dcc30b89f4943`; arquivo de fonte SHA256 `c6494137f2dc680eaec5b802089503e1d8301da16d5226a368072f19b77c80ff`. A proveniência local está nos arquivos `upstream-provenance.json` das integrações SNES/Mega e também nos assets correspondentes do APK R125.

**A base de uma adaptação deve ser a fonte normal atual com o HUD, não o primeiro donor importado:**

`E:\ESTUDO APK\work\station-hud-lzgames-20261003\source`

Esse conjunto contém Snes9x, MD.emu, EmuFramework e Imagine. As bibliotecas de saída desse diretório conferem integralmente com as entradas normais do APK R125 e com o inventário R55:

| Entrada normal | Bytes | SHA256 atual |
| --- | ---: | --- |
| `libsnes9x_explus.so` | 3.802.928 | `3adeeabe25117265cdd10138fc9631c58da7deda533ff0272a89d7e64bb77956` |
| `libmdemu_station.so` | 6.755.552 | `889d18461fc14e765813d7ef197ecfc922786df8f1f961dd82443dd88aecd124` |

Os primeiros receipts de integração tinham hashes diferentes porque importavam as bibliotecas oficiais antes da recompilação do HUD. Eles não são a base nativa atual.

Receita já existente no Git:

`versions/station-current-r55-20261006/exit-menus/build_native.py`

Ela aponta explicitamente para `station-hud-lzgames-20261003/source`, `sdk` e `station-arm64.cmake`, recompila Imagine/EmuFramework e os emuladores, e copia as saídas finais. O SDK local contém `libimagine.a`, `libemuframework.a`, `libmednafen_common.a`, libc++ e as dependências de áudio/arquivo, os arquivos pkg-config e os módulos C++.

Ferramentas e dependências locais identificadas:

- `C:\Program Files\LLVM\bin\clang.exe` e LLVM auxiliares.
- CMake 4.4.2 instalado; Ninja usado pela receita.
- Sysroot `E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\sysroot`.
- Toolchain `E:\ESTUDO APK\work\station-hud-lzgames-20261003\station-arm64.cmake`: ARM64/API26/páginas de 16 KiB.
- `sdk\android-arm64`: libc++/libc++abi, ogg, vorbis, FLAC, xz e libarchive já presentes.

`select_engine.py` recompila namespaces/atlas distintos. A seleção altera a cópia de fonte e o SDK compartilhado; qualquer novo trabalho precisa copiar/pinar essa base para uma árvore isolada e executar SNES/MD sequencialmente. Não deve trocar os arquivos offline ou reaproveitar um SDK incremental de outro namespace sem conferir sua seleção.

Esta auditoria constatou fonte, receita, dependências e saídas existentes coincidentes. Não fez uma nova reprodução binária da compilação.

### O netplay SNES encontrado não está pronto no EX+ atual

Na fonte normal atual:

- `Snes9x/src/snes9x/netplay.cpp:7` condiciona a implementação histórica a `NETPLAY_SUPPORT`.
- `Snes9x/CMakeLists.txt:19` não define essa macro; `Snes9x/src/CMakeLists.txt` não inclui `netplay.cpp` nem `server.cpp`.
- `Snes9x/src/snes9x/netplay.h:171` declara conexão, espera de heartbeat, joypads, sincronização e envio; a versão de protocolo é 10, com até oito clientes no protocolo histórico.
- **`Snes9x/src/snes9x/snes9x.h:292` declara `NetPlay` e `NetPlayServer` constantes em zero.** O código histórico tenta escrever `Settings.NetPlay` em `netplay.cpp:278` e `:839`. Definir a macro/incluir os arquivos sem adaptar a implementação não resolve esse conflito.
- O EX+ atual não chama `S9xNPConnectToServer`, `S9xNPWaitForHeartBeat` ou `S9xNPGetJoypad` no frontend/loop atual examinado.
- O protocolo histórico inclui operações de ROM, freeze file e SRAM (`netplay.h:55`–`:58`); não pode ser conectado diretamente ao contrato Station nem habilitado com transferência de conteúdo irrestrita.

Portanto, há código real de netplay histórico como referência, mas não uma API funcional do SNES normal que possa ser ativada somente com flag Java. A integração Station deve ser feita no C++ atual ou restaurar/adaptar explicitamente aquela implementação, com contrato próprio e validação.

### MD.emu: o que existe e o que falta

Na fonte atual `MD.emu/src`, a busca por netplay/rollback não encontrou implementação. O core usado pelo normal é Genesis Plus GX; o online atual usa clownmdemu. Esses motores não compartilham automaticamente estados, opções, hashes ou IDs.

Primitivas reais suficientes para um adaptador novo:

| Função | Fonte atual e linha | Uso real |
| --- | --- | --- |
| Quadro SNES | `Snes9x/src/main/Main.cc:310`, chamada `S9xMainLoop` em `:349` | Executa o core e publica vídeo/áudio pelo EmuFramework original |
| Input SNES | `Snes9x/src/main/input.cc:36` | Usa o deviceId e bits de joypad do core; mesmo caminho de toque/controle físico |
| Estado SNES | `Snes9x/src/main/Main.cc:116` e `:138` | Read/write de snapshot em memória |
| Multitap SNES | `Snes9x/src/main/input.cc:155` | Porta 0 joypad; porta 1 MP5 com jogadores 1–4 |
| Quadro MD | `MD.emu/src/main/Main.cc:57` | `system_frame` seguido de `audio_update` e áudio original |
| Input MD | `MD.emu/src/main/input.cc:32` e `:41` | Aplica deviceId por `playerIdxMap` em `input.pad[]` |
| Estado MD | `MD.emu/src/main/Main.cc:103` e `:108` | `state_load`/`state_save` em memória |
| Multitap MD | `MD.emu/src/main/input.cc:148` e `:151` | Team Player e mapeamento dos quatro pads; J-Cart tem caminho próprio em `:143` |

`AppMeta::maxPlayers` é cinco no SNES e quatro no MD. Isso é capacidade do frontend, **não prova que cada jogo oferece esse número**; o perfil da sala precisa usar o catálogo/protocolo de periférico específico do jogo.

`EmuFramework/src/EmuSystemTask.cc:42` cria a thread real de emulação. O worker possui comandos de suspensão/retomada/saída e reconhecimento por semáforo (`:76`, `:133`, `:142`). `advanceFrames` em `:376` chama `sys.runFrames` em `:443`. `EmuSystem.cc:571` e `skipFrames` chamam `runFrame` também para quadros sem renderização.

Esses são pontos reais para manter o mesmo renderer, áudio, HUD, toque e BSP-D3, inserindo transporte/input e barreira **antes de cada quadro efetivamente emulado**, inclusive quadros omitidos da renderização. O core não deve ganhar um segundo loop paralelo nem o controlador escrever diretamente nos pads remotos fora do quadro acordado.

### Trabalho ainda necessário para os candidatos SNES/MD

1. Criar variante nativa online isolada da fonte normal atual, com nome/namespace próprios, mantendo as bibliotecas offline e preferências existentes intactas.
2. Acrescentar API Station de preparo, input local por slot assinado, aplicação conjunta de input por quadro, ACK de pausa do worker real, epoch, retomada e saída exclusivamente autorizada. Não basta marcar READY na Activity antes da pausa real.
3. O worker deve permanecer responsivo a suspensão/saída. Um `wait` de rede indefinido dentro de `runFrame` impediria o event loop de processar seu `SuspendCommand`, criando risco concreto de deadlock/ANR.
4. Pinar opções de região/periférico/clock/cheats e estado inicial/SRAM. O SNES usa relógio do aparelho em `srtcemu.cpp:28` e `spc7110emu.cpp:111`; jogos que usam esses relógios exigem tratamento determinístico próprio ou exclusão explícita do perfil online.
5. Guardar estados manuais/rewind/reset/fast-forward e qualquer avanço unilateral só na variante online. As ações existem em `EmuInput.cc:58`, `:87`, `:111`, `:196` e `:204`; o HUD também usa as APIs de state. Preferências e controles físicos offline continuam preservados.
6. Isolar arquivos de sessão e autosaves. As pontes normais `SnesBootstrap`/`MegaBootstrap` só entregam caminho e storage; não carregam o descriptor de sessão, owner/barreira ou novos exports.
7. Gerar novos IDs/core/runtime/options hashes e contrato de perfil. Não reutilizar identidades bsnes/clownmdemu nem seus estados para EX+/Genesis Plus GX.
8. Validar em provas isoladas e depois gameplay real. O código localizado não demonstra que essa migração já funciona.

## MAME4droid / CPS / Neo Geo

Achados cruzados com o auditor nativo e conferidos no donor local:

- Rota normal em `E:\ESTUDO APK\work\native-carousel\implementation\native_mame.h:40`: `openMame` → `MameBootstrap.launch` → `MameEntryActivity` → MAME4droid, processo `:mame`.
- O mesmo header cobre MAME/CPS1–3/Neo Geo/CD. FBNeo é excluído explicitamente em `native_mame.h:4`.
- Fonte de integração Java: `E:\ESTUDO APK\work\native-carousel\implementation\mame-current\java`.
- Donor: `mame-current\MAME4droid.2026-1.41.2-release.apk`, com `donor-decoded`/smali. Bibliotecas normais `libMAME4droid`/`libmame4droid-jni`.

APIs reais de `donor-decoded/smali/com/seleuco/mame4droid/Emulator.smali`:

| Linha | API |
| ---: | --- |
| 1550 | `netplayGetDiagnostics()String` |
| 1556 | `netplayGetProtocolVersion()int` |
| 1562 | `netplayInit(String,int,int)int` |
| 1568 | `netplayResync()int` |
| 1574–1589 | Detector de desync, InternetMode, IP family, local port, mode e endereço de punch |
| 2869 | `runT()` nativo |
| 3180 / 3192 | `setAnalogData` / `setDigitalData` nativos |

Há indicadores `NETPLAY_HAS_CONNECTION`, `NETPLAY_HAS_JOINED` e rollback no mesmo arquivo. A pausa Java não comprova que o core parou no epoch exigido nem que os pacotes internos já foram consumidos.

**Lacuna delimitada:** não foi localizado C/C++ desse motor no conjunto `mame-current` examinado; nele há donor APK, smali e bridges. É necessário identificar o código exato e seu protocolo/transport/ownership antes de encapsular netplay em Station e reconhecer pausa/delivery real. `netplayInit` sozinho não cumpre esses requisitos.

A R126 continua usando FBNeo para CPS/Neo Geo cartucho e NeoCD para Neo Geo CD no online. A disponibilidade de netplay no MAME não torna os cores intercambiáveis.

## PS1 / PCSX ReARMed

- A matriz normal `versions/station-game-menu-controller-audit-r120-20261010/LAUNCH-AUDIT-R120.md` identifica LibretroPlayer normal + `libpcsx_rearmed_libretro_android.so`.
- A integração local é `E:\ESTUDO APK\work\native-carousel\implementation\psx-integration`; `upstream-commit.json` registra PCSX ReARMed `ff81ed17a15241d2f3730cdd7585b38e172532ca`.
- Esse commit pinado é do **core**, não fonte/proveniência comprovada do frontend LibretroPlayer normal. A pasta examinada contém artefatos upstream/previous e integração; não resolve o código original do Player.
- O manifesto R126 continua identificando no online `libstation_online_pcsx.so`, core SHA256 `4de0afbd3bb113a4b9927b5b250860194b485f278d1dced81501dc6555fa18a8`.

Manter a mesma ABI libretro não conserva por si só o renderer, menu, mapeamento físico ou owner normal dos quadros. O adaptador precisa interceptar a fronteira `retro_run` no Player normal, input ports, loader/state/options e pausa reconhecida pela thread real. Deve evitar executar um loop Station em paralelo com o loop original.

**Lacuna delimitada:** mapear esse frontend/ABI exatos e obter sua fonte reproduzível ou um ponto binário determinístico auditável antes de propor a migração. A presença do core e de snapshots não é confirmação de um adaptador pronto.

## Limites da conclusão

SNES/MD possuem os melhores candidatos concretos neste levantamento: fonte normal atual, renderer/input/HUD originais, receitas nativas e saídas coincidentes já locais. Seu trabalho restante é construir a integração de sessão determinística, e não redesenhar controles nem trocar o motor offline.

MAME/PSX exigem os pontos de fonte/ABI/protocolo descritos acima. Nenhuma dessas lacunas foi preenchida por troca de Intent, fallback silencioso ou redução das verificações de compatibilidade.

Esta auditoria não altera o funcionamento entregue da R126, a economia de CPU do carrossel, efeitos, autenticação, saves/licenças ou o contrato de produção. Não afirma que todos os sistemas já usam os emuladores normais no online.
