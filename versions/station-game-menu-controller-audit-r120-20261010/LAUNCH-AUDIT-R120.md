# Auditoria de lançamento — R120

Base APK R119: `f5d0e434cb383a7103c77fd1e853b9f4721d283c30941860a21f1831bf6be674` (2.217.049.480 bytes). Todas as 50 plataformas canônicas de `StationPlatforms.java`, os 78 nomes aceitos pelo mapa final e os 43 perfis originais foram cruzados com a cadeia nativa, os class_defs dos 38 DEX, os componentes do Manifest e a listagem central ARM64 do APK.

## Conclusões

- Motor Switch preservado; corrigido o pacote no primeiro salto Android. O XML físico confirma o pacote antigo.
- Corrigidos os aliases exatos `megadrive--br`, `super-nintendo--br` e `pc-engine-cd`, encaminhando aos mesmos motores já previstos pelos nomes exibidos.
- Oito famílias possuem comandos originais válidos, mas a dependência não estava disponível na conferência do Motorola. Não foram trocados motores nem adicionadas bibliotecas nesta auditoria.
- A existência de comando, classe, biblioteca ou processo não equivale a um jogo funcionar. Nenhum gameplay foi validado nesta tarefa.

## Chamada efetiva e preservação

O JNI publica o nome do sistema em `Item.platform` (+0x60) e a pasta canônica em `Item.folder` (+0x78). `resolveLaunchCommand` passa a pasta ao hook. O comparador dos hooks respeita hífens e só ignora caixa/espaços finais; o lookup dos perfis originais normaliza letras/números. Por isso foram necessários os três aliases exatos.

A precedência é: n64CommandHook → megaCommandHook → gamecubeCommandHook (Switch/BR/Classic/demais) → XML original. Quando o XML não tem chave, o resolvedor usa perfil normalizado por pasta e depois nome; não significa ausência de comando. A cadeia de execução encaminha por identificador para o bootstrap próprio ou cai no `LibretroPlayer::run` original.

## Matriz individual de plataformas

Nas linhas com dependência disponível, as bibliotecas abaixo foram localizadas como entradas ARM64 do APK R119 junto das classes/Activities. Nas oito linhas indisponíveis, o nome representa a biblioteca solicitada pelo comando, ausente na conferência. O JSON anexo registra os DEX, bytes/CRC das entradas, processos exatos e todos os aliases de cada linha. “Pendente” significa que o motor não foi iniciado para provar gameplay.

| Plataforma | Pasta real | Motor/execução offline | Biblioteca ARM64 principal | Estado |
| --- | --- | --- | --- | --- |
| 3ds | `3ds` | LibretroPlayer: azahar | `libazahar_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Arcade | `arcade` | MAME4droid Current | `libMAME4droid.so, libmame4droid-jni.so` | Rota/componentes presentes; gameplay pendente |
| Atomiswave | `atomiswave` | Flycast Android | `libflycast.so, libturbo_flycast.so` | Rota/componentes presentes; gameplay pendente |
| Dreamcast | `dreamcast` | Flycast Android | `libflycast.so, libturbo_flycast.so` | Rota/componentes presentes; gameplay pendente |
| GameCube | `gamecube` | Dolphin Android | `libdolp.so` | Rota/componentes presentes; gameplay pendente |
| Gameboy | `gameboy` | LibretroPlayer: gambatte | `libgambatte_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Gameboy Color | `gameboy-color` | LibretroPlayer: gambatte | `libgambatte_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Gba | `gba` | LibretroPlayer: mgba | `libmgba_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Master System | `master-system` | LibretroPlayer: genesis_plus_gx | `libgenesis_plus_gx_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| MegaDrive | `megadrive` | MD.emu EX+ | `libmdemu_station.so` | Rota/componentes presentes; gameplay pendente |
| MegaDrive - BR | `megadrive--br` | MD.emu EX+ | `libmdemu_station.so` | Rota/componentes presentes; gameplay pendente |
| Neo Geo | `neo-geo` | MAME4droid Current | `libMAME4droid.so, libmame4droid-jni.so` | Rota/componentes presentes; gameplay pendente |
| Neo Geo CD | `neo-geo-cd` | MAME4droid Current | `libMAME4droid.so, libmame4droid-jni.so` | Rota/componentes presentes; gameplay pendente |
| Nintendinho | `nintendinho` | LibretroPlayer: fceumm | `libfceumm_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Nintendo 64 | `nintendo-64` | Mupen64Plus AE | `libmupen64plus-core.so` | Rota/componentes presentes; gameplay pendente |
| Nintendo 64 - BR | `nintendo-64--br` | Mupen64Plus AE | `libmupen64plus-core.so` | Rota/componentes presentes; gameplay pendente |
| Nintendo DS | `nintendo-ds` | LibretroPlayer: melonds | `libmelonds_libretro_android.so` | Dependência indisponível no Motorola |
| Odyssey 2 | `odyssey-2` | LibretroPlayer: o2em | `libo2em_libretro_android.so` | Dependência indisponível no Motorola |
| PSP | `psp` | PPSSPP Android | `libppsspp_jni.so` | Rota/componentes presentes; gameplay pendente |
| Pc Engine | `pc-engine` | LibretroPlayer: mednafen_pce_fast | `libmednafen_pce_fast_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Pc Engine cd | `pc-engine-cd` | LibretroPlayer: mednafen_pce | `libmednafen_pce_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Playstation 1 | `psx` | LibretroPlayer: pcsx_rearmed | `libpcsx_rearmed_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| Playstation 2 | `ps2` | ARMSX2 Android | `libemucore_16k.so, libemucore_4k.so` | Rota/componentes presentes; gameplay pendente |
| Playstation 2 - BR | `ps2br` | ARMSX2 Android | `libemucore_16k.so, libemucore_4k.so` | Rota/componentes presentes; gameplay pendente |
| Psp - BR | `psp` | PPSSPP Android | `libppsspp_jni.so` | Rota/componentes presentes; gameplay pendente |
| Psvita | `psvita` | Vita3K Android | `libVita3K.so` | Rota/componentes presentes; gameplay pendente |
| Super Nintendo | `super-nintendo` | Snes9x EX+ | `libsnes9x_explus.so` | Rota/componentes presentes; gameplay pendente |
| Super Nintendo - BR | `super-nintendo--br` | Snes9x EX+ | `libsnes9x_explus.so` | Rota/componentes presentes; gameplay pendente |
| Switch | `switch` | Yuzu Android (unchanged) | `libyuzu-android.so` | Pacote corrigido; gameplay pendente |
| atari2600 | `atari2600` | LibretroPlayer: stella | `libstella_libretro_android.so` | Dependência indisponível no Motorola |
| atari7800 | `atari7800` | LibretroPlayer: prosystem | `libprosystem_libretro_android.so` | Dependência indisponível no Motorola |
| colecovision | `colecovision` | LibretroPlayer: bluemsx | `libbluemsx_libretro_android.so` | Dependência indisponível no Motorola |
| cps1 | `cps1` | MAME4droid Current | `libMAME4droid.so, libmame4droid-jni.so` | Rota/componentes presentes; gameplay pendente |
| cps2 | `cps2` | MAME4droid Current | `libMAME4droid.so, libmame4droid-jni.so` | Rota/componentes presentes; gameplay pendente |
| cps3 | `cps3` | MAME4droid Current | `libMAME4droid.so, libmame4droid-jni.so` | Rota/componentes presentes; gameplay pendente |
| fbneo | `fbneo` | LibretroPlayer: fbneo | `libfbneo_libretro_android.so` | Dependência indisponível no Motorola |
| fds | `fds` | LibretroPlayer: fceumm | `libfceumm_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| gameandwatch | `gameandwatch` | LibretroPlayer: gw | `libgw_libretro_android.so` | Dependência indisponível no Motorola |
| gamegear | `gamegear` | LibretroPlayer: genesis_plus_gx | `libgenesis_plus_gx_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| jaguar | `jaguar` | LibretroPlayer: virtualjaguar | `libvirtualjaguar_libretro_android.so` | Dependência indisponível no Motorola |
| mame | `mame` | MAME4droid Current | `libMAME4droid.so, libmame4droid-jni.so` | Rota/componentes presentes; gameplay pendente |
| naomi | `naomi` | Flycast Android | `libflycast.so, libturbo_flycast.so` | Rota/componentes presentes; gameplay pendente |
| naomi2 | `naomi2` | Flycast Android | `libflycast.so, libturbo_flycast.so` | Rota/componentes presentes; gameplay pendente |
| saturn | `saturn` | Saturn integrado | `libturbo_saturn.so` | Rota/componentes presentes; gameplay pendente |
| sega32x | `sega32x` | LibretroPlayer: picodrive | `libpicodrive_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| supergrafx | `supergrafx` | LibretroPlayer: mednafen_supergrafx | `libmednafen_supergrafx_libretro_android.so` | Rota/componentes presentes; gameplay pendente |
| wii | `wii` | Dolphin Android | `libdolp.so` | Rota/componentes presentes; gameplay pendente |
| wiiu | `wiiu` | Cemu Android | `libCemuAndroid.so` | Rota/componentes presentes; gameplay pendente |
| xbox | `xbox` | x1box/xemu | `libxemu.so` | Rota/componentes presentes; gameplay pendente |
| xbox360 | `xbox360` | Xendroid | `libe.so` | Rota/componentes presentes; gameplay pendente |

## Oito dependências ausentes na conferência

| Plataforma | Core solicitado pelo fallback |
| --- | --- |
| Nintendo DS | `melonds_libretro_android.so` |
| Odyssey 2 | `o2em_libretro_android.so` |
| atari2600 | `stella_libretro_android.so` |
| atari7800 | `prosystem_libretro_android.so` |
| colecovision | `bluemsx_libretro_android.so` |
| fbneo | `fbneo_libretro_android.so` |
| gameandwatch | `gw_libretro_android.so` |
| jaguar | `virtualjaguar_libretro_android.so` |

A leitura ADB feita pelo responsável confirmou que `/storage/emulated/0/EmulationStation/.emulationstation/cores` não existe no Motorola. Esses oito nomes também não têm a entrada normal `lib<core>_libretro_android.so` no APK R119. Isso registra a dependência indisponível nesta instalação; não declara que o comando está errado, que nenhum instalador poderia obter o core ou que houve um teste físico de lançamento.

## Verificação HOST autorizada

As seis funções reais de seleção de comando foram extraídas da fonte fechada R120 e compiladas com MSVC x64. UiString, strAssign, strData e o resolvedor XML original são mocks delimitados. Resultado: **146 verificações, zero falhas, 37 passagens preservadas ao fallback original**. Foram cobertos os 50 folders, 78 aliases do catálogo após a resolução para a pasta e 18 aliases diretos/caso desconhecido.

O teste prova o encaminhamento desses comandos no código compilado HOST. Não valida a ABI ARM64, JNI, assets/BIOS, engine, rede, GPU ou gameplay. O fallback ELF e a tabela de perfis foram lidos separadamente; não são emulados nesse harness.

Arquivos reproduzíveis: `tests/launch_command_host.cpp`, `tests/launch-command-host-cases.json` e `tests/build-launch-command-host.cmd`; resultado em `evidence/launch-command-host-r120.json`.

## Online separado do lançamento normal

A sala online usa autorização de lançamento e capacidades do catálogo assinado. Não deriva capacidade de rede do comando offline nem da presença de uma biblioteca. Esta matriz não marca plataformas indiscriminadamente como `launchReady`, não reduz validações e não altera a versão/identidade de nenhum motor online. Os componentes `StationRoomsActivity`, `StationRetroActivity` e `StationDolphinNetplayActivity` pertencem ao fluxo separado.

Evidência completa: `evidence/launch-matrix-r120.json`. Sem mudanças nos limites econômicos, vídeos, LEDs, cache ou 30 fps nesta documentação.
