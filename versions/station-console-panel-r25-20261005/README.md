# R25 — estrelas, ícone de jogadores e console maior

## Pedido confirmado

Remover nota numérica e a legenda “Nota do catálogo”. Ao lado das estrelas colocar o ícone de jogadores com “1 player”, “2 players”, conforme o jogo. O console deve aproveitar o máximo do espaço disponível. A quantidade da lista continua abaixo da sinopse, e o nome do jogo abaixo do console.

## Implementação

- `native_info.h`: remove criação, atualização e renderização dos componentes de nota/legenda. Mantém as cinco estrelas, com preenchimento proporcional ao dado real existente. Sem avaliação, ficam vazias; nenhuma nota é inventada.
- `station_players_label.h`: contagem vem do registro publicado para o ID exato. Faixa `1-2` apresenta `2 players`, `1` apresenta `1 player`, `1-16` apresenta `16 players`, e `8+` permanece `8+ players`. Campo vazio mostra traço junto do ícone, sem assumir um jogador. Não é regra de multiplayer online.
- `station_game_panel_layout.h`: estrelas e jogadores passam a ocupar uma linha única. Foto começa em `top+.045H` (antes `top+.115H`) e termina em `.818H` (antes `.811H`). Título conserva sua faixa `.825H..895H`, acima dos botões.
- `native_console.h` e `station_console_fit.h`: calculam, uma vez por upload/contexto, o retângulo contendo todos os pixels com alfa não zero. Preservam um texel transparente de margem quando disponível. A textura original não é editada; coordenadas UV ignoram apenas margem transparente. Escala uniforme máxima que cabe no espaço, sem cortar nenhum pixel visível, sem esticar e sem invadir sinopse, metadados ou título.
- Mantém o comportamento para telas estreitas/sem imagem: metadados usam a faixa disponível, sem reservar coluna vazia.

Sete imagens conferidas: SNES, Mega Drive, N64, Neo Geo, Neo Geo CD, Naomi e Naomi 2. Aliases regionais continuam compartilhando suas imagens. A estrutura usa o mesmo layout para todas as listas; a existência de arte continua regida pela tabela já implementada.

## Base e preservação

Base exata R24 `d35516420934aeda7cee96af6185a17506146ae7fa2c28f867d6e7c44e721a0b`, commit `171ef6eff09744d2739b3f68db6b06b8bbbdea33`.

Só três fontes herdados mudam: `native_info.h`, `native_console.h`, `station_game_panel_layout.h`. Acrescenta os dois helpers descritos acima. Todos os quatro arquivos LED R24 permanecem exatos. Vídeos R22, sinopse rolável R21, layout/base de dados R23B, contador da lista, nomes, motores, controles, sessões e download permanecem.

## Testes e pacote

772.456 verificações no PC passaram: labels/capacidades do buffer, faixas lado a lado, limites dos retângulos, telas e proporções diversas, UV e **todos os pixels não transparentes das sete imagens**. Cada imagem ocupa a maior escala uniforme possível dentro da área. Host e NDK arm64/API26 compilados.

APK assinado com certificado existente, alinhamento 16 KiB verificado. Somente `lib/arm64-v8a/libturbo_carousel.so` muda; **13.083 entradas preservadas por comparação completa**. SHA final: `0d62d806fb0fd7ef45cf0167dd6908794e180e81171c8f7fa0b3e701aa78baad`, 2.053.850.368 bytes. SO: `310a1a73f9bf3ff11b3d06674ccd5c4e9cb6a736da6aba40b3a1a104d1be8bcc`.

Teste de geometria não equivale a prova visual no aparelho. Consulte STATUS e eventual installation/visual evidence para o estado posterior. Sem promoção de estabilidade geral ou alegação de FPS/temperatura.

## Caminhos canônicos

- APK: `E:\ESTUDO APK\work\station-console-panel-r25-20261005\TurboStations-Console-Players-R25-20261005.apk`.
- Fontes/evidências: mesma pasta, subpastas `native`, `evidence`, `tests`. Compilação/temporários em E.
- SO final arquivado: `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-console-panel-r25-20261005\libturbo_carousel.so`.
- APK base R24 arquivado: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-NeoGeo-Laser-R24-20261005.apk`.
- Renders de PC R24: `G:\BAKUP SISTEMA APP 03-10-2026\evidencias-visuais\station-neogeo-laser-r24-20261005`. Cópias conferidas antes de retirar duplicatas E; manifesto em `evidence/compiled-output-archives.json`. Fontes, scripts de teste, imagens de referência e relatório final R24 continuam em E.
- Dependências nativas W16: `E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native`.
- Objetos: `W16/video720_posters.o` e `E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\neogeo_previews.o`, uma vez cada.

## Reprodução e instalação

Fontes finais completos estão em `native/`. `evidence/native-build.json` traz comando, hashes de origem/destino e teste. Recipes preserva preparação, build, arquivo e empacotamento, com guardas para não sobrescrever revisões. A receita de preparação precisa dos dois helpers junto dela; a receita de build precisa do teste C++ junto dela (copiar de `tests/`). Não executar receitas históricas sobre revisão posterior.

Instalação somente por atualização, mesmo certificado, sem limpar dados. Exige hash R24 no telefone e frontend aberto, para não fechar partida. Nenhum servidor foi alterado. Delta de downloads Servidor-pix `11be7f3`/`6f012a7` continua separado do APK; não anunciar sua implantação nesta atualização visual.

## Instalação e revisão posterior

R25 foi instalada por atualização às 17:17 (05/10), sem limpar dados e com hash do aparelho igual ao APK. Uma captura de Mega Man X/coleção com cinco jogos confirmou os elementos presentes; **o mantenedor rejeitou seu alinhamento visual**. A observação funcional não é aprovação estética.

Pedido posterior, implementado em R26: estrelas junto do estado Não instalado no cabeçalho; pasta e contagem substituem as estrelas acima do console; contagem anterior abaixo da sinopse removida. Também foram pedidos todos os botões inferiores mais estreitos.

APK R25 agora arquivado em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Console-Players-R25-20261005.apk`. As imagens, testes e demais evidências continuam em E:. A referência E: anterior é histórica.
