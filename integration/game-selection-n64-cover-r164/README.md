# R164 — seleção de jogos e mapeamento da capa N64

**Candidata assinada, instalada e conferida por `adb sha256sum` no Samsung A56; seleção visual e toques conferidos em 2340 × 1080.** O usuário aceitou o desenho com a proporção de 10% mantida. O cadastro dos novos motores no servidor, a publicação da nova arte e o gameplay N64 online R164 continuam pendentes. [Handoff do servidor](../../docs/server/r164/README.md) e [recibo físico sanitizado](../../docs/server/r164/evidence/a56-selection-qa.json).

## Mudança revisada

R163 preparou a seleção com capa principal maior, ações reposicionadas e dois perfis de luz N64: o da arte anterior e o da nova imagem de **1080° Snowboarding**. R164 parte do overlay nativo R163 e ajusta a geometria de desenho e toque dos controles existentes: capa principal mais estreita, cards menores, busca e atualização no topo, faixa de ações alinhada à base da capa e arranjo responsivo para telas largas e 16:9. Os seis IDs de ação `0–5` permanecem. Em 16:9, o botão online e `JOGAR` ganham posições próprias; o mesmo retângulo governa desenho e toque do online.

A [receita de ações](../game-selection-actions-r164/recipe/patch_actions.py) modifica somente `native_formation.h`, `station_bottom_action_layout.h` e `native_skin.h` e acrescenta `native_netplay.h` à cópia do overlay. O [compilador R164](recipe/build_native.py) exige os hashes R163 fixados e preserva `magazine_shader.h` e `native_magazine_field.h` byte a byte: o mapeamento de luz N64 não mudou nesta revisão. A [nota de geometria](../game-selection-actions-r164/review/REVIEW-NOTE.md) registra que o campo de relatório da borda direita diverge do desenho real e que proporções quase quadradas/verticais não foram validadas. As amostras estáticas são 2456 × 1080, 1920 × 1080 e 1280 × 720; o A56 foi capturado fisicamente em 2340 × 1080.

O `libturbo_carousel.so` resultante tem SHA-256 `bd3222558a43f8998d51b0b72010ecb8a94c7ae62a14d34b39863d13737a10d0`. O APK assinado tem SHA-256 `903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210` e 2.715.466.850 bytes, com o certificado original SHA-256 `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`. O hash do `base.apk` instalado no A56 confere. A [montagem](recipe/package_candidate.py) altera cinco entradas das 13.861 do APK R162; preserva as outras 13.856, as 40 partições DEX, `classes35.dex`, `classes36.dex`, a ponte de vídeo online e o frontend. Três marcadores de runtime e `engines.json` mudam para vincular a identidade dos quatro motores independentes ao novo binário visual, sem mudar suas políticas.

## Capa nova e limite de escopo

A imagem de referência N64 é PNG RGB 1024 × 1536, SHA-256 `2f8ee5b6d4c91979a7e75658def15f3daabc04b299aa44145f2c9a5efb3fdcc1`. A [receita R163](../game-selection-n64-cover-r163/recipe/patch_n64_cover.py) detecta pixels LED dessa moldura e mantém o perfil anterior para a capa antiga. A seleção física de 1080° Snowboarding ainda mostra a arte anterior servida pelo servidor; o app R164 **não publica** capa. A troca precisa do plano guardado no [handoff do servidor](../../docs/server/r164/README.md), pelo `itemId` e `coverId` exatos, com prova do catálogo e do corpo servido.

A prova de build fixa ABI, alinhamento Android de 16 KiB, avisos do compilador e ausência de novos timers, threads, workers, alocações ou draws por quadro. Isso limita o delta; não é uma medição de FPS, tempo de quadro ou consumo no A56. O relato do usuário de vídeo N64 online e sem engasgos significativos refere-se à **R162** no A56 e não foi instrumentado. A R164 teve seleção, busca e atualização exercitadas fisicamente; a capa **nova** e a partida N64 online ainda precisam de teste após publicação/cadastro.

## Inspeção física da seleção

Três capturas privadas de 2340 × 1080 confirmam capa grande 10% mais estreita, cards menores, faixa de ações escura alinhada à base da capa e ícone de atualização separado da busca. `JOGAR`, `JOGAR ONLINE`, `SAVES`, `APAGAR` e `VOLTAR` aparecem juntos. Tocar a primeira minicapa N64 selecionou 1080° Snowboarding; tocar atualização retornou à seleção 007/lista; pesquisar `1080` mostrou `1/1` e campo sem sobreposição das estrelas. O usuário aceitou: “MANTENHA PROPORÇÃO 10% COMO ESTAVA TODO RESTO DESIGN ESTA OK”. O [recibo](../../docs/server/r164/evidence/a56-selection-qa.json) traz hashes das capturas, sem publicar imagens nem identificador do aparelho.

## Entrega e retorno

As [receitas de assinatura](recipe/sign_private.py) e [kit privado](recipe/package_server_kit.py) exigem o APK e referências exatos. O kit R164 SHA-256 `37e3b9dd5b8efaae1a222b27661cb7a838689fa2b484b16268e2efa26d11457a` contém 40 entradas e segue somente pelo fluxo privado autorizado. **Não versionar APK, ZIP, PNG/JPEG, chaves, ROM ou dados de aparelho neste Git.**

Para concluir o aceite, obter o recibo de cadastro R164 e de publicação da nova capa, depois testar essa arte e o gameplay N64 entre aparelhos na mesma revisão. Em falha visual, reter o APK assinado anterior e os recibos para retorno pelo procedimento privado de instalação; em falha de cadastro ou arte, usar os backups e rollbacks próprios do servidor sem remover owners ou capas não relacionados. R164 permanece candidata até esses resultados.
