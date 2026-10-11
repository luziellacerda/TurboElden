# Sistemas restantes — emulador normal, rede real e integração pendente

Auditoria de 11/10/2026 do APK R126 assinado `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d`. Nenhum telefone foi operado, nenhuma partida iniciada, nenhum servidor alterado e nenhuma fonte produtiva modificada. A conferência completa do APK da tarefa principal está em `../evidence/current-apk-audit.json`.

## Resultado objetivo

As 50 linhas canônicas e os 78 aliases estão enumerados em [MATRIX.md](MATRIX.md); [matrix.json](matrix.json) contém comandos, componentes, DEX, bibliotecas/hashes, seleção online e o índice de aliases. Foram lidas 45 bibliotecas únicas e todos os componentes normais indicados pela matriz R120 estão presentes nos DEX R126. Oito bibliotecas de fallback não estão no APK. A auditoria não verifica a pasta externa de cores de um telefone atual.

Há 15 linhas com motor v3 localmente selecionável e 35 sem motor v3 elegível. N64/N64-BR/GameCube/Wii são quatro dessas linhas e representam três sistemas em dois backends nativos R126, Mupen e Dolphin. As onze restantes continuam com o runtime online histórico. Registro local, cadastro em produção, aprovação do jogo/modo e gameplay são verificações diferentes. Nenhum dado desta auditoria concede novos jogadores a um jogo.

Nos 33 sistemas deste relatório não existe adaptador Station específico nem entrada v3 elegível. Portanto, a preparação atual retorna indisponibilidade antes de lançar um emulador. Não é correto dizer que essas salas já abrem o emulador normal, nem cadastrar um hash de sua biblioteca normal como se tivesse o contrato Station.

## Código que determina a execução

- `versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay/StationOnlineGame.java:20`: exige `launchReady` e `station-stream.v3`, seleciona o primeiro motor elegível da plataforma e exige perfil autenticado por jogo/edição/modo.
- Mesmo arquivo, `:101`: backends aceitos são o runtime histórico, Mupen Station e Dolphin Station. Não aceita um backend Flycast/PPSSPP/ARMSX2/Cemu/Xemu/Yuzu ainda inexistente.
- `versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay/StationRoomsActivity.java:1095`: escolhe `StationN64Activity`, `StationDolphinActivity` ou o caminho histórico `StationRetroActivity`; não há lançamento normal genérico após a preparação de uma sala.
- `versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationOnlinePlatformPolicy.java:8`: converte aliases em pasta e canonical online. Os tetos desta classe não autorizam modos de jogos.
- Os oito headers locais `d1/native_flycast.h`, `native_psp.h`, `native_ps2.h`, `native_psvita.h`, `native_saturn.h`, `native_wiiu.h`, `native_xboxclassic.h` e `native_xbox360.h` têm SHA exatamente igual aos pins do `CAROUSEL-INPUT-MANIFEST.json` R124. Seus hooks chamam os bootstraps normais; o texto `libretro:` de alguns comandos é interceptado e não prova execução pelo RetroArch.

Não foi encontrado novo erro de roteamento normal nesses 33 sistemas. A lacuna online é uma integração ausente, não uma troca de nome do componente. Trocar apenas a Activity deixaria transporte, entrada, recuperação e hashes sem consumidor real.

## Famílias com emulador próprio

### Dreamcast, Atomiswave, Naomi e Naomi2 — Flycast

Normal: `FlycastBootstrap` → `com.flycast.emulator.NativeGLActivity`, processo `:flycast`; `libflycast.so` e `libturbo_flycast.so` presentes. O APK identifica Flycast `v2.7-44-ge36e9df2d`, commit `e36e9df2dcc1487acdb1dc7725766f1f5ba029b5`. Os mesmos hooks cobrem as quatro pastas; a seleção interna de máquina/conteúdo permanece do Flycast.

O código GGPO fixa dois participantes e o timeout de desconexão em 3.000 ms; o evento de desconexão lança exceção. O caminho de entrada inicializa quatro estados Maple, mas preenche somente os dois participantes GGPO. Assim, quatro portas locais não comprovam quatro participantes GGPO. [Fonte oficial fixada](https://github.com/flyinghead/flycast/blob/e36e9df2dcc1487acdb1dc7725766f1f5ba029b5/core/network/ggpo.cpp).

Integração concreta necessária: variante isolada Flycast, transporte dos datagramas GGPO pelo acesso Station, perfil inicial com o limite GGPO comprovado, identidade de conteúdo/opções/BIOS/estado inicial, pausa confirmada no emuthread por epoch/serial, retorno real do consumo de datagramas e proteção contra timeout/stop automático somente no modo Station. Expandir GGPO para três/quatro exige modificar sua enumeração de jogadores, buffers, handshake e callbacks; não é uma alteração de `maximumPlayers` no catálogo. Modos Dreamcast de rede nativa/BBA e modos arcade ligados em rede são outra família de protocolo, não equivalem ao GGPO existente.

### PSP e PSP-BR — PPSSPP

Normal: `PspBootstrap` → `org.ppsspp.ppsspp.PpssppActivity`, processo `:psp`; `libppsspp_jni.so` presente, proveniência PPSSPP 1.20.4. O ELF atual possui funções AdHoc, inclusive as interfaces compiladas de rede; isso não é uma prova de uma partida funcionando.

PPSSPP distingue AdHoc e infraestrutura; o relay AdHoc está documentado desde 1.20.1. Cada aparelho emula sua própria PSP. A rede de um jogo e os servidores de infraestrutura suportados não são uma sala de controles de um único console. [Documentação oficial](https://www.ppsspp.org/docs/multiplayer/quickstart/).

Integração necessária: fixar e adaptar o protocolo AdHoc/AemuPostoffice/PRO da versão 1.20.4, associar identidade/MAC/grupo/game ID aos participantes autenticados, preservar socket/datagrama e controle por instância e criar configuração privada por sessão. No caminho AdHoc, reusar a rede oficial é uma base real. Apenas mudar a URL do servidor para o endpoint HTTPS Station não implementa esse protocolo. Recuperação exige verificar relógios/timeout do jogo e confirmação nativa de pausa; não pode prometer que uma partida de infraestrutura aceita espera infinita. Cada jogo deve ter modo de rede comprovado e número de instâncias aprovado.

### PlayStation 2 e PlayStation 2-BR — ARMSX2

Normal: `Ps2Bootstrap` → `com.armsx2.Main`, processo `:ps2`; `libemucore_16k.so`/`libemucore_4k.so` presentes. O emulador atual é ARMSX2 2.7.2, e não o substituto histórico NetherSX2. As funções normais `NativeApp.runVMThread`, `pause`, `resume` e `shutdown` existem na fonte do doador; suas assinaturas sozinhas não comprovam uma barreira de CPU por epoch.

A versão fixada contém `LocalLinkAdapter`: um relay Ethernet em estrela sobre UDP, com autenticação, nonce e fragmentação, separado do backend DEV9 de Internet. O máximo de peers do túnel não é o número de jogadores de um jogo. A documentação oficial registra também o caminho DEV9 em sockets Android. [Fonte LocalLink fixada](https://github.com/ARMSX2/ARMSX2/blob/2.7.2/pcsx2/DEV9/LocalLinkAdapter.cpp), [interface](https://github.com/ARMSX2/ARMSX2/blob/2.7.2/pcsx2/DEV9/LocalLinkAdapter.h), [DEV9 oficial](https://armsx2.net/updates/2.6.4).

Os três blobs LocalLink/NetworkTab foram lidos diretamente da API pública e seus hashes estão em [primary-source-fetch.json](primary-source-fetch.json). A fonte `recv` limita a leitura a 16 datagramas por chamada; remove peers inativos após dez segundos. Isso não equivale a ordenar `shutdown` da VM, mas precisa ser conciliado com a retomada Station.

Integração necessária para jogos LAN: encapsular as mensagens LocalLink/Ethernet e preservar MAC, nonce, identidade de peers, fragmentos e descoberta; deixar DHCP/ARP/DEV9 no motor real. Opções privadas têm de ativar o adaptador correto antes do boot. Além disso, criar confirmação de pausa/retomada na thread da VM e proteger as rotas normais de resume/stop apenas na variante online. Jogos LAN/Internet PS2 têm modos e limites próprios; os dois pads locais não tornam todos esses jogos multiplayer por rede. Sincronizar coop local de um único PS2 seria um adaptador distinto, com estado/inputs/quadros determinísticos.

### PS Vita — Vita3K

Normal: `VitaBootstrap` → `VitaEntryActivity` → `org.vita3k.emulator.Emulator`, processo `:psvita`; `libVita3K.so` presente. A proveniência **do APK R126** é build 4115, commit curto `a366df69`, SHA da biblioteca `a133ff7e5397ae09d863e9583c37a5070024f0bc226630ae4a1fc40e77fed8db`. A árvore local histórica `e6ac4272...` e a revisão 4103 não são fonte exata desse motor 4115.

O projeto mantém um acompanhamento oficial de compatibilidade AdHoc por jogo. Isso não confirma todos os modos, nem prova que o motor Android 4115 expõe o protocolo necessário a Station. [Acompanhamento oficial](https://github.com/Vita3K/Vita3K/issues/3686).

Dependência concreta: recuperar/fixar o código nativo completo da build 4115 e seu estado AdHoc, identificar a ponte de sockets/matching e a barreira real do motor, depois adaptar o transporte e aprovar cada título/modo. A ausência de nomes AdHoc no dynsym não prova ausência da implementação: o motor pode registrar interfaces dinamicamente. Não usar a árvore antiga para construir um adaptador com um hash novo que alegue equivalência ao motor atual.

### Nintendo Switch — Yuzu integrado

Normal preservado: `AndroidBridge.launchIntent` → `GameLauncher` → `org.yuzu.yuzu_emu.bootstrap.BootstrapActivity` → `org.yuzu.yuzu_emu.activities.EmulationActivity`; processo principal. `libyuzu-android.so` está presente. O comando já corrigido na R120 aponta ao package atual `org.turboramastation.frontend` e conserva action/URI/MIME/content do launcher.

O ELF R126 tem 29 símbolos NetPlay, incluindo os JNI reais `netPlayCreateRoom`, `netPlayJoinRoom`, `netPlayRoomInfo`, `netPlayIsJoined` e `netPlayLeaveRoom`; a declaração correspondente existe no DEX. Isso confirma uma API de salas nativa disponível no binário, sem comprovar compatibilidade/gameplay ou integração Station. Evidência em `matrix.json/networkExports/libyuzu-android.so`.

Dependência concreta: fixar a revisão e a fonte exatas desse doador; documentar o protocolo/clock/dados da sala nativa e a interface do emuthread antes de adaptá-lo. Nenhum resultado oficial de outro fork ou de uma versão atual pode ser atribuído automaticamente a esse binário. O ponto de partida é sua API nativa real, com criação/join sem lobby público paralelo, transporte controlado e retomada por epoch; o renderer/input normais continuam do Yuzu. Não modificar novamente o launcher offline nem substituir o emulador por outra biblioteca para contornar a ausência de adaptador online.

### Saturn — Yaba Sanshiro

Normal: `SaturnBootstrap` → `SaturnActivity`, processo `:saturn`; `libturbo_saturn.so` presente. Fonte reconstruída Yaba Sanshiro 1.20.46, archive SHA `3eb2d610d178b8fd503bb13d7e50b8f8710711a26a1efb52780010a559a1b912`.

O `netlink.c` da fonte emula NetLink, mas o CMakeCache do build existente fixa `YAB_NETWORK:BOOL=OFF`; `src/CMakeLists.txt:851` só define `USESOCKET` quando essa opção é ligada. Portanto, a existência de `netlink.c` não comprova que sockets NetLink estejam compilados neste motor. [Fonte oficial indicada pelo doador](https://www.yabasanshiro.com/download).

Integração necessária para coop local: input/periféricos, estado inicial determinístico e gate da CPU no ciclo Yabause, mantendo sua Activity/EGL/Oboe. Para títulos NetLink: variante nativa com esse recurso compilado, modem/socket e timing próprios, aprovação separada do modo. São modelos diferentes. Não adicionar `launchReady=true` a um core que ainda não contém qualquer interface Station de pausa/ACK.

### Wii U — Cemu Android

Normal: `WiiUBootstrap` → `WiiUEntryActivity` → `info.cemu.cemu.emulation.EmulationActivity`, processo `:wiiu`; `libCemuAndroid.so` presente. A proveniência **do APK R126** é **SapphireRhodonite/Cemu DualScreen 0.5.2**, doador SHA `e1630fc51a4bbb18ef8499829fad011601d575726f019090abada6c9dd258387`. A árvore SSimco 0.5 anteriormente consultada é histórica, não fonte exata do motor atual.

O port se declara experimental e não garante as funcionalidades do desktop. Cemu desktop documenta recursos de Internet/serviços Wii U; isso não é uma implementação de coop local sincronizado pelas salas Station e não comprova paridade Android. [Fonte do port exato](https://github.com/SapphireRhodonite/Cemu/tree/0.5.2), [FAQ oficial Cemu](https://cemu.info/faq.html).

Dependência concreta: fonte exata 0.5.2, caminho CPU/input/VPAD/PAD e recursos de rede efetivamente compilados, gate que confirma pausa da CPU e perfil separado por jogo/mode/GamePad/remotes. Para rede dos próprios jogos, adaptar apenas o protocolo realmente suportado nessa revisão. Não enviar credenciais/sistema do Wii U pelo relay nem confundir o port Cemu com Dolphin GameCube/Wii.

### Xbox — X1Box/xemu

Normal: `XboxBootstrap` → `XboxEntryActivity` no processo `:xbox` → `com.izzy2lost.x1box.MainActivity` em `:xboxemu`; `libxemu.so` presente, doador X1Box 1.2.8. [Release do port](https://github.com/izzy2lost/xemu/releases/tag/1.2.8).

xemu documenta NIC emulado, NAT, bridge e túnel UDP Ethernet para System Link, com MAC único e versões compatíveis dos jogos. Essa é rede de consoles independentes; não equivale a quatro pads de um único Xbox. A documentação desktop não comprova que cada backend esteja exposto pelo port Android. [Rede oficial xemu](https://xemu.app/docs/networking/).

Integração necessária: verificar o backend UDP e configuração JNI desse port, criar túnel de Ethernet autenticado por roster Station, preservar broadcast/MAC/discovery e pausar de forma cooperativa na CPU QEMU sem matar sua rede/renderer. Alternativamente, coop local exigiria interface de frame/input/estado distinta. O número permitido deve vir do modo System Link ou coop do jogo, não do número de portas.

### Xbox 360 — XenDroid

Normal: `Xbox360Bootstrap` → `Xbox360EntryActivity` (`:xbox360`) → `Xbox360GameEntryActivity` → `xendroid.compose.EmulatorHostActivity` (`:xbox360emu`); `libe.so` presente. Versão XenDroid `0b1120187340be3644e28ceb7a04be04cd0f2e08`.

O código fixado `xsocket.cc` contém implementações guest TCP/UDP/VDP com Asio, bind/listen/connect/send/recv. Isso prova a base de sockets, sem demonstrar que todos os serviços Xbox Live/System Link e todos os jogos estejam implementados. [Fonte do doador](https://github.com/rfandango/XenDroid/tree/XenDroid-0b11201), [XSocket fixado](https://github.com/rfandango/XenDroid/blob/0b1120187340be3644e28ceb7a04be04cd0f2e08/emulator-core/src/main/cpp/xenia/src/xenia/kernel/xsocket.cc).

Integração necessária: auditar syscall/endereçamento/session/discovery de um jogo LAN real e sua biblioteca Android, adaptar esse fluxo por roster autenticado e controlar pausa de CPU/kernel sem inventar APIs de netplay de quadros. Não anunciar compatibilidade ampla apenas porque `XSocket` existe. Estado do jogo de rede e rollback de emulação são mecanismos distintos.

## Famílias cujo modo normal já é LibretroPlayer

Nesses casos o emulador normal é o core indicado abaixo, dentro do `LibretroPlayer` do app. Reusar o mesmo core não significa abrir outra Activity/renderer. A ligação precisa manter o proprietário normal dos callbacks de vídeo/áudio/input e integrar acesso/sincronização no ciclo de `retro_run`. O backend atual `libstation_retroarch.so` é um runtime completo que também executa os quadros; não é uma biblioteca de conexão independente já encaixada no `LibretroPlayer`.

O modelo clássico de sincronização pressupõe mesmo core/conteúdo e não substitui emulação de cabo/rede. Os recursos de save state e os símbolos exportados também não provam determinismo, estado inicial equivalente ou desempenho adequado. [FAQ oficial Libretro](https://docs.libretro.com/guides/netplay-faq/), [desenvolvimento de frontends](https://docs.libretro.com/development/frontends/).

| Sistema individual | Core normal | APK R126 | Capacidade documentada / limite da evidência | Dependência para Station |
|---|---|---|---|---|
| 3ds | Azahar Libretro | Presente | API Libretro; documentação de recursos não concede netplay. Rede de Citra/Azahar standalone não prova recurso nesse core | Fixar fonte/core; interface de rede 3DS se efetivamente exposta, perfil por modo; não conceder duas entradas P1/P2 de um único portátil |
| Gameboy | Gambatte | Presente | Netplay marcado não; multiplayer típico depende de link | Link não implementado nesse perfil/core; não usar segundo pad como cabo |
| Gameboy Color | Gambatte | Presente | Mesmo limite Gambatte | Perfil de link real separado, sem substituir core normal por hipótese |
| Gba | mGBA | Presente | Netplay marcado não no core; cabo/wireless não é classic pad netplay | Bridge do link real ou perfil comprovado distinto; não alegar gpSP porque o app usa mGBA |
| Master System | Genesis Plus GX | Presente | Netplay de frontend documentado | Gate/inputs/estado no LibretroPlayer e perfil exato de joypad/periférico |
| Nintendinho | FCEUmm | Presente | Netplay de frontend documentado | Gate/estado/input e opções/perfil de cada jogo; Four Score só se aprovado |
| Nintendo DS | melonDS | Ausente | Docs melonDS2021 marcam netplay não; melonDS DS é outro core | Instalar/fixar core pretendido para offline, depois integração WiFi real, sem alias enganoso de core novo |
| Odyssey 2 | O2EM | Ausente | Netplay marcado não | Dependência de core + prova de serialização/determinismo/input antes de habilitar salas |
| Pc Engine | Beetle PCE Fast | Presente | Netplay de frontend documentado | Integrar ciclo normal, modos/periféricos; teto default dois do app não representa todos os jogos com multitap |
| Pc Engine cd | Beetle PCE | Presente | Netplay de frontend documentado; mídia/BIOS/estado inicial importam | Conteúdo multitrack/CHD e opções fixados + gate no player; jogo/modo determina participantes |
| atari2600 | Stella | Ausente | Netplay de frontend documentado | Core fixado + input e switches/paddles específicos do jogo |
| atari7800 | ProSystem | Ausente | Netplay marcado não | Core + prova real do estado/determinismo; não fabricar elegibilidade |
| colecovision | blueMSX | Ausente | States/netplay marcados não | Core + estado serializável e teclado/keypad por jogador; a atual família não possui essa prova |
| fds | FCEUmm | Presente | Mesmo core e modelo frontend FCEUmm | Mídia/BIOS e escrita em disco privadas por sessão, perfil autenticado |
| gameandwatch | GW | Ausente | States/netplay marcados não | Core e serialização ausentes para recuperação; aprovar só jogos que realmente tenham modo multiplayer |
| gamegear | Genesis Plus GX | Presente | Netplay frontend documentado não comprova link Game Gear | Auditar link emulado; um segundo pad não substitui o cabo |
| jaguar | Virtual Jaguar | Ausente | Documentação atual anuncia Netplay/JagLink; versão ausente do APK não pode herdar essa capacidade | Fixar core/versão antes; perfil distingue coop local e JagLink/CatBox |
| sega32x | PicoDrive | Presente | Netplay de frontend documentado | Mesmo player/core, estado e pads/opções por jogo; nenhum engine Station atual |
| supergrafx | Beetle SGX | Presente | Netplay de frontend documentado | Mesmo player/core e estado/opções/periféricos aprovados |

Fontes oficiais por core: [Azahar](https://docs.libretro.com/library/azahar/), [Gambatte](https://docs.libretro.com/library/gambatte/), [mGBA](https://docs.libretro.com/library/mgba/), [Genesis Plus GX](https://docs.libretro.com/library/genesis_plus_gx/), [FCEUmm](https://docs.libretro.com/library/fceumm/), [melonDS2021](https://docs.libretro.com/library/melonds/), [O2EM](https://docs.libretro.com/library/o2em/), [Beetle PCE Fast](https://docs.libretro.com/library/beetle_pce_fast/), [Beetle PCE](https://docs.libretro.com/library/mednafen_pce/), [Stella](https://docs.libretro.com/library/stella/), [ProSystem](https://docs.libretro.com/library/prosystem/), [blueMSX](https://docs.libretro.com/library/bluemsx/), [GW](https://docs.libretro.com/library/gw/), [Virtual Jaguar](https://docs.libretro.com/library/virtual_jaguar/), [PicoDrive](https://docs.libretro.com/library/picodrive/), [Beetle SGX](https://docs.libretro.com/library/beetle_sgx/).

A marcação nas páginas é capacidade documentada do frontend/core upstream consultado, não prova do binário fixado R126. Na matriz, cada core presente tem seu SHA e seus nove exports Libretro essenciais conferidos. `retro_serialize` existir não comprova que seu resultado seja válido/estável. Cores ausentes não possuem identidade nativa atual para cadastrar. FBNeo também é um dos oito fallbacks normais ausentes; sua família e seu motor online histórico são analisados pelo relatório arcade da tarefa principal.

## Sequência mínima para uma integração real

1. Fixar fonte correspondente ao doador atual, opções/configuração e bibliotecas dependentes. Manter normal/offline e economia intactos; variante online separada com flag inicialmente falsa.
2. Escolher o modelo correto do **jogo/modo**: pads de um único console, cabo/link, Ethernet/LAN ou serviço de Internet. Assinar os perfis com conteúdo/edição, dispositivos e limites comprovados.
3. Criar launcher/descritor privado e Activity/processo que abra o emulador real. Backend próprio só fica aceito em `StationOnlineGame.runtime` e `StationRoomsActivity` quando houver consumidor nativo implementado.
4. Ligar transporte Station ao protocolo real. Preservar mensagens, ordenação, endereçamento, broadcast/fragmentação e ownership. ACK de entrega só depois do consumo efetivo, não do enfileiramento Java.
5. Implementar pausa confirmada pela CPU/VM e retomada por epoch/serial sem contorno por lifecycle, menu, watchdog ou save state. Durante espera, IO de recuperação precisa continuar. Perda de rede não autoriza shutdown; desync real fica em atenção/pausa. Isso não garante que um servidor externo ou protocolo de um jogo aceite reconexão infinita.
6. Exigir sala nova com identidades novas somente após build/hash/contrato reais; provas isoladas e gameplay físico separados. Medir latência, CPU e comportamento por jogo; não reduzir FPS de emuladores por consequência da integração.

**Estado final desta auditoria:** nenhum motor novo foi compilado/cadastrado/instalado. N64/GameCube/Wii continuam candidatos R126, sem promoção a estável. Os demais permanecem explicitamente pendentes; a matriz não mascara essa falta com um emulador diferente.
