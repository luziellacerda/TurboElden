# PSX, CPS e Neo Geo/MAME — motores reais no R126

Auditoria de 11/10/2026 sobre o APK R126 identificado pelos recibos finais, SHA256 `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d`. Inspeção somente leitura das entradas do pacote, ABI AArch64, fontes locais e fontes oficiais fixadas por commit. O probe desta pasta passou **40 verificações de bytes, símbolos, instruções e descritor**. Isso identifica o código executável e suas fronteiras; não demonstra gameplay, determinismo, estabilidade, consumo ou uma adaptação instalada.

## Resultado por sistema

| Sistema | Motor/owner normal | Motor/owner online empacotado | Classificação | Motor normal usado no online? |
| --- | --- | --- | --- | --- |
| PlayStation/PSX | LibretroPlayer + PCSX-ReARMed `ff81ed1` | StationRetroActivity/RetroArch + PCSX-ReARMed `c8816799` | Mesma família, revisão e owner diferentes | Não |
| CPS1 | MAME4droid 1.41.2 / MAME 0.289 | StationRetroActivity/RetroArch + FBNeo `95153da1` | Família e owner diferentes | Não |
| CPS2 | MAME4droid 1.41.2 / MAME 0.289 | StationRetroActivity/RetroArch + FBNeo `95153da1` | Família e owner diferentes | Não |
| CPS3 | MAME4droid 1.41.2 / MAME 0.289 | StationRetroActivity/RetroArch + FBNeo `95153da1` | Família e owner diferentes | Não |
| Neo Geo AES/MVS, ZIP | MAME4droid 1.41.2 / MAME 0.289 | StationRetroActivity/RetroArch + FBNeo `95153da1` | Família e owner diferentes | Não |
| Neo Geo CD | MAME4droid 1.41.2 / MAME 0.289 | StationRetroActivity/RetroArch + NeoCD `b1e04c73` | Família e owner diferentes | Não |
| MAME/Arcade genérico | MAME4droid 1.41.2 / MAME 0.289 | Sem descritor genérico de plataforma MAME em `engines.json` | Motor online genérico ausente | Não |

As cinco rotas CPS/Neo Geo prontas no manifesto histórico declaram máximo de **dois jogadores**, não equivalência ao MAME normal. O descritor Geolith/`.neo` permanece `launchReady=false`; ele não substitui a rota ZIP. A célula FBNeo possui sua própria rota normal e fica na auditoria paralela das outras famílias. Os aliases normais MAME também incluem Model2, mas seu catálogo/driver online não foi aprovado nesta análise.

## Identificação dos binários reais

| Biblioteca ARM64 | Bytes | SHA256 |
| --- | ---: | --- |
| `libmain.so`, owner LibretroPlayer normal | 4.588.272 | `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6` |
| `libpcsx_rearmed_libretro_android.so`, PSX normal | 1.582.960 | `e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9` |
| `libstation_online_pcsx.so`, PSX online | 1.547.280 | `4de0afbd3bb113a4b9927b5b250860194b485f278d1dced81501dc6555fa18a8` |
| `libMAME4droid.so`, MAME normal | 366.992.944 | `ab587eec36db170387baa743d1078912927d6b9c0e2fe8057d56225739d62d71` |
| `libmame4droid-jni.so`, JNI normal | 32.856 | `a7dea2fc4fb73a7a57fccb5ffc2dca3faf53ac11b7f54b1337b04da09edaf108` |

As duas bibliotecas MAME são idênticas às entradas do donor MAME4droid 1.41.2, cujo APK tem SHA256 `b2e05497f4c7b8b0d5ac84a4755569050f60a4c9c69c7e219f6783bd9c5bb2ad`. Isso prova preservação/proveniência binária, sem provar reprodução da compilação nativa a partir dos fontes públicos.

## PSX: fronteira exata de execução, renderer e input

No `libmain.so` conferido, `LibretroPlayer::run` inicia em `0x2a9718`. O owner contém o processamento SDL, o único avanço do core, áudio, upload de vídeo, saves e apresentação no mesmo laço. Os endereços são virtuais ELF, específicos ao hash acima.

| Operação normal | Callsite |
| --- | --- |
| `SDL_PollEvent` | `0x2abe48` |
| `LibretroCore::run` → `retro_run` | `0x2ae610` |
| Áudio SDL | `0x2aeac4` |
| Upload de vídeo | `0x2aec5c` |
| Tamanho/serialização de estado | `0x2add78` / `0x2addac` |
| Desserialização de estado | `0x2b081c` |
| Pacing e swap SDL | `0x2b142c` / `0x2b1444` |

`LibretroCore::run` em `0x2be414` verifica o core carregado e despacha o ponteiro real de `retro_run`; há um gate de pausa local no owner em `0x2ae600`. O `inputPoll` real em `0x2b587c` usa os eventos/controles SDL. O `inputState` em `0x2b62b0` rejeita portas maiores que 1; a instrução dessa condição foi conferida em `0x2b6308`. Portanto, o frontend normal observado oferece **duas portas**. A capacidade multitap do core não torna esse callback capaz de quatro participantes. A documentação libretro distingue a capacidade do core dos recursos implementados pelo frontend. [PCSX-ReARMed oficial](https://docs.libretro.com/library/pcsx_rearmed/).

A versão retornada pelo core normal é `r26 ff81ed1`; a proveniência local associa o commit completo `ff81ed17a15241d2f3730cdd7585b38e172532ca`, cuja alteração oficial corrige registradores ARM64 preservados durante o `retro_run`. O core online foi compilado de `c8816799b50388e61cfe237fe2cdbb7d8175f20a`, com outro hash. Mesmo mantendo a família PCSX-ReARMed, essas duas revisões não têm identidade de execução/estado implicitamente intercambiável. [Commit normal oficial](https://github.com/libretro/pcsx_rearmed/commit/ff81ed17a15241d2f3730cdd7585b38e172532ca).

### Fonte disponível e impedimento concreto

Os cores PCSX têm fonte/proveniência; falta o **fonte C++ exato do LibretroPlayer Android e sua receita nativa**. O pacote antigo `psx-integration/libmain.so` é outro binário; não serve como base para os endereços desta revisão. Os scripts encontrados remontam APKs a partir de Smali, recursos e ELF prontos.

A busca atual nos clones existentes conferiu HEAD, caminhos e conteúdo do histórico local de TurboElden-git, TurboRetroEmu e TurboRetroEmu-funcional. Foram lidos **687 blobs únicos C/C++/headers** do histórico TurboElden; zero definições de LibretroPlayer/LibretroCore. Os outros dois históricos têm zero blobs nessas extensões. Não houve erro nessa leitura Git. Buscas de nomes/declarações nas pastas de trabalho também não localizaram as definições. O inventário histórico mais amplo examinou nove unidades e 440 arquivos compactados; teve pastas inacessíveis e objetos ausentes em um clone parcial. A conclusão é ausência **nos locais e objetos acessíveis pesquisados**, não ausência universal em qualquer backup.

### Adaptação real necessária

A implementação deve integrar o sincronizador **antes do avanço real do core**, mantendo o owner SDL responsivo enquanto a partida aguarda conexão. Bloquear indefinidamente dentro de `retro_run` congelaria eventos/renderer; retornar sem quadro enganaria áudio, pacing e contadores. Nenhum desses wrappers foi criado.

Com o owner recuperado, os pontos obrigatórios são: inputs por slot assinado usando os controles normais; barrier CPU/GPU após quadro concluído, com ACK por epoch/revisão; retomada apenas com permissão atual; serialização/replay com vídeo/áudio suprimidos corretamente; opções/região/BIOS/periféricos/memory cards fixados; bloqueio online de reset/save/load/fast-forward incompatíveis; isolamento de saves; cancelamento somente humano. A identidade deve incluir frontend/core/opções reais. Uma skin ou a troca do nome da biblioteca não atende isso. O protocolo libretro de NetPlay sincroniza input/estado no frontend, não apenas o desenho dos controles. [NetPlay libretro oficial](https://docs.libretro.com/development/retroarch/netplay/).

## MAME4droid: implementação oficial utilizável e diferenças reais

A fonte oficial inspecionada é MAME4droid-Current `9df33ca197df96d8e206740b94fc54be4e379550`, release 1.41.2. A base MAME 0.289 pode ser recuperada pelo commit oficial `f34f02505e32c1993c6a782b6814232cbfc74e36`, tag `mame0289`. Nenhum clone ou checkout novo foi feito. [Release do port](https://github.com/seleuco/MAME4droid-Current/releases/tag/v1.41.2), [base oficial](https://github.com/mamedev/mame/commit/f34f02505e32c1993c6a782b6814232cbfc74e36).

O código do port oferece NetPlay nativo real: protocolo **14**, callbacks de pacotes em `netplay_t`, integração em `myosd_netplay_input_update`, buffers de estados/inputs e carga diferida em fronteira limpa do scheduler. Porém, o handle contém um único peer e aplica host/cliente exclusivamente às portas P1/P2. A estrutura UDP também contém um único endereço de cliente. Logo, são **dois peers de rede** na implementação examinada, mesmo que determinados drivers aceitem mais controles locais. Três/quatro telefones exigem redesign real de roster, inputs, histórico e recuperação. [Handle/protocolo](https://github.com/seleuco/MAME4droid-Current/blob/9df33ca197df96d8e206740b94fc54be4e379550/src/osd/myosd/netplay/netplay.h), [transporte](https://github.com/seleuco/MAME4droid-Current/blob/9df33ca197df96d8e206740b94fc54be4e379550/src/osd/myosd/netplay/skt_netplay.h).

A integração do OSD chama pre/post-frame, injeta inputs e escolhe rollback ou lockstep conforme o tamanho/limites dos estados. A API de estado prevê carga no scheduler e supressão de áudio/vídeo durante replay. Isso é uma base real para adaptação; não prova determinismo nem suporte de estado de todos os drivers/jogos do catálogo. [Fronteira do frame](https://github.com/seleuco/MAME4droid-Current/blob/9df33ca197df96d8e206740b94fc54be4e379550/src/osd/myosd/netplay/myosd_netplay.cpp), [contrato de estados](https://github.com/seleuco/MAME4droid-Current/blob/9df33ca197df96d8e206740b94fc54be4e379550/src/osd/myosd/netplay/myosd_netplay.h).

### Recuperação automática incompatível com o pedido

O fonte tem três caminhos concretos que precisam de alteração **apenas na variante Station**: silêncio de rede por dez segundos durante espera do peer marca desconexão; falha de envio por quatro segundos encerra conexão; espera dura de rollback acima de 1.500 iterações pode liberar o frame apesar de inputs pendentes. O primeiro e terceiro ficam em `myosd_netplay.cpp` linhas 971–979 e 1069–1077; o envio em `skt_netplay.cpp` linhas 486–499. Devem virar espera recuperável por epoch com CPU realmente parada, mantendo transporte/eventos vivos e distinguindo falha fatal de perda transitória. Remover timeouts sem esse controle deixaria risco de espera/ANR/desync. [Caminho de envio](https://github.com/seleuco/MAME4droid-Current/blob/9df33ca197df96d8e206740b94fc54be4e379550/src/osd/myosd/netplay/skt_netplay.cpp).

O bridge preciso deve substituir os callbacks de pacote pelo DATA opaco Station-v3; confirmar consumo nativo do pacote completo; controlar pausa/retomada/epoch na fronteira real do scheduler; preservar JNI/input/renderer normais; impedir encerramentos automáticos nessa opção e autorizar teardown humano. ROM-set, driver, BIOS, NVRAM, mídia e formato de estado precisam de perfis/identidades MAME novos. As identidades FBNeo/NeoCD não podem ser reaproveitadas para MAME.

### Compilação nativa ainda não reproduzida

O repositório público é um overlay do port, não a árvore MAME completa. `howtobuild.txt` manda combinar MAME base e modificar makefile/Lua para o OSD; não fixa todas as alterações/flags do donor. O `Android.mk` disponível compila somente `mame4droid-jni.c`; não recompila `libMAME4droid.so`. O Gradle declara NDK `28.2.13676358`, compatível com o NDK local inventariado. Ainda é necessário recuperar/fixar a árvore base, modificações de build/driver, opções e dependências, reproduzir a biblioteca normal e só então compilar a variante online isolada. [Instrução do port](https://github.com/seleuco/MAME4droid-Current/blob/9df33ca197df96d8e206740b94fc54be4e379550/howtobuild.txt), [JNI build](https://github.com/seleuco/MAME4droid-Current/blob/9df33ca197df96d8e206740b94fc54be4e379550/android-MAME4droid/app/src/main/jni/Android.mk).

## Entregas e limites

- `package-abi-evidence.json`: 40 verificações aprovadas contra entradas reais do APK.
- `source-evidence.json`: matriz, versões, commits/hash dos fontes, pontos de frame/recuperação e limites da busca.
- `probe_psx_package.py`: procedimento reproduzível que lê o APK e falha se hashes/ABI não forem exatos.

Não foi alterado APK, fonte congelado R126, binário normal, registry, servidor, checkout/index ou telefone. Não há adapter PSX/MAME instalado por esta auditoria. A entrega identifica os obstáculos específicos e a fronteira de implementação; não declara migração universal. Artefatos extraídos/disassembly ficam locais, fora da pasta pública. Nenhuma ROM, BIOS, licença, serial, credencial ou log pessoal compõe estas entregas.
