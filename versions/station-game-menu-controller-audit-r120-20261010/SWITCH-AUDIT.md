# Auditoria Switch — R120

Base: R119 `13b21b9dc08adf7b1820fdeb09bec47a810c1ea5`. Análise estática de fontes, APKs locais exatos e regiões ELF. Não houve teste, jogo iniciado nem operação de telefone nesta auditoria.

## Referências reais

| Referência | APK SHA-256 | Pacote |
| --- | --- | --- |
| Estável Cemu 30/09, tag `estavel-2026-09-30-cemu-052` | `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b` | `org.emulationstation.frontend` |
| Estável 2 jogadores R76, fonte `a81c7fde61c6d048b4cea4c746052bd7304e600e` | `d7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51` | `org.turboramastation.frontend` |
| R119 atual | `f5d0e434cb383a7103c77fd1e853b9f4721d283c30941860a21f1831bf6be674` | `org.turboramastation.frontend` |

A estável Dolphin 30/09 tem metadados no Git, mas o APK citado não existe mais naquele destino local. Não foi usado como se estivesse disponível.

## O que foi preservado

O motor `lib/arm64-v8a/libyuzu-android.so` é idêntico nas três referências: 35.518.648 bytes, SHA-256 `c82b35d81aa4b9521a64bf79e7d617fb418df5e9b728b5b228b4860e55d1a72b`.

Da R76 à R119, as 38 entradas DEX só diferem em `classes28.dex` e `classes35.dex`. Os DEX Switch (`classes.dex`, `classes2.dex`, `classes8.dex`), Manifest, recursos binários e os 7.195 arquivos de recursos comparados são idênticos. Não há evidência de troca recente do motor Switch ou de seu menu por essas versões.

Como os DEX da estável 30/09 têm índices diferentes, a comparação não usou hashes de instruções com referências numéricas como prova semântica. A saída de decompilação normalizada de `SwitchConfigPatcher`, `TurboEdenBridge`, `GameLauncher`, `EmulationActivity` e `EmulationFragment` é igual. Os três primeiros foram decompilados integralmente. Nas duas Activities maiores há avisos/fallback em alguns métodos; a igualdade dessa saída não constitui uma prova formal de equivalência de todo o bytecode. A preservação R76â†’R119, por outro lado, foi demonstrada por igualdade dos DEX completos. `YuzuApplication.onCreate` só acrescentou guardas para outros processos/emuladores; o fluxo Switch principal permanece.

## Defeito concreto da chamada

`ESActivity.getArguments()` e `installResources()` chamam `TurboEdenBridge.prepare()`. Este chama `SwitchConfigPatcher.apply()`, que ainda grava no XML um comando com `package=org.emulationstation.frontend`. O pacote atual, desde o candidato de aplicativo separado, é `org.turboramastation.frontend`.

`CatalogService.findLaunchCommand` em `libmain.so` (`0x1888e0`) lê o comando XML. O caminho `AndroidBridge.launchIntent` (`0x37271c`, argumento em `0x372a14–0x372a30`) converte diretamente `IntentSpec.package` para string JNI. `GameLauncher.launch` usa `Intent.setClassName(pkg, cls)`, sem remapear o pacote. O primeiro salto pode apontar a um pacote antigo ausente ou a outra instalação antiga. Já o salto seguinte de `BootstrapActivity` usa `getPackageName()` e mantém a URI recebida.

Essa incompatibilidade é demonstrada no código. Ainda falta correlacionar o erro relatado no aparelho com a primeira falha de lançamento. Motor igual sozinho não comprova funcionamento físico.

## Correção mínima aplicada na fonte R120

`native/d0/native_carousel.cpp`, função `gamecubeCommandHook`, reconhece os aliases Switch catalogados antes do fallback. Retorna o comando Android original com apenas `package=org.turboramastation.frontend` corrigido.

São preservados `BootstrapActivity`, `ACTION_VIEW`, `%ROM_RAW%`, `application/octet-stream`, `content=1`, motor, firmware/keys existentes, preferências de qualidade e controles. Não foram alterados DEX, outros emuladores, fila econômica, preloads, LEDs, cache nem limite de 30 fps. Não há inclusão de APK, ROM, BIOS ou dado pessoal neste documento.

Compilação Android e conferência física ficam com o fechamento conjunto da R120. Posteriormente, por autorização explícita, o harness HOST das funções reais de comando passou 146 verificações; detalhes e limites estão em `LAUNCH-AUDIT-R120.md`. Não houve gameplay ou lançamento Switch nesta subtarefa.

Evidência estruturada: `evidence/switch-static-audit.json`.

## Fallback original dos demais sistemas

A ausência de um sistema no XML não significa ausência de comando. `findLaunchCommand` devolve uma string vazia, e `resolveLaunchCommand` procura um dos 43 perfis originais por pasta e depois nome, normalizando letras e números. Com perfil, monta `libretro: core=<core>_libretro_android.so`. A tabela inteira extraída com relocations do ELF é idêntica à estável Cemu de 30/09 e está em `evidence/original-launch-profile-table-r120.json`. Os hooks nativos e comandos explícitos existentes têm precedência.

| Plataforma sem comando no XML observado | Fallback original | Observação |
| --- | --- | --- |
| Atari 2600 | `stella_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| Atari 7800 | `prosystem_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| Colecovision | `bluemsx_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| Nintendo DS | `melonds_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| Jaguar | `virtualjaguar_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| Odyssey 2 | `o2em_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| Game & Watch | `gw_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| FBNeo | `fbneo_libretro_android.so` | Disponibilidade local não medida nesta subtarefa |
| PlayStation 2 e BR | `armsx2_libretro_android.so` | Hook `native_ps2.h` intercepta o identificador e abre `Ps2Bootstrap`/`com.armsx2.Main`, usando o motor integrado |

Para cores que permanecem no caminho libretro original, a verificação real usa `<EmulationStation>/.emulationstation/cores/<core>_libretro_android.so` e os assets necessários, ou o caminho bundled. Não encontrar uma biblioteca com esse nome nas entradas `lib/arm64-v8a` do APK não comprova ausência no aparelho. Esta auditoria separa configuração da rota, disponibilidade do motor e funcionamento físico.
