# Seleção de jogos: capa principal 10% mais larga que a R164

Preparação para a próxima compilação combinada. A R164 assinada e instalada permanece intacta. A receita [`patch_width.py`](recipe/patch_width.py) exige uma cópia dos 14 cabeçalhos nativos R164 conferidos pelo recibo SHA-256 `c39fc9350cb643cd64bd227a874b9bee2d29bde914a963d6d5e153633e16c3eb` e pelo binário SHA-256 `bd3222558a43f8998d51b0b72010ecb8a94c7ae62a14d34b39863d13737a10d0`. Recusa a pasta original e qualquer entrada divergente antes de gravar.

O multiplicador da capa de jogo selecionada muda de `0.90` para `0.99` em **dois lugares**: `coverSlot()` em `native_formation.h` (desenho, mapeamento da arte e toque) e `stationBottomGameAction()` em `station_bottom_action_layout.h` (ações e ícones). A altura, posição superior, raio de canto, seis IDs de ação, miniaturas, faixa escura, busca, catálogo, iluminação e motores ficam na R164. Os demais 12 cabeçalhos permanecem byte a byte iguais. Não há novo timer, thread, worker, alocação ou chamada de desenho por quadro.

| Tela | Largura principal R164 → preparada | Início das miniaturas e ações | Verificação estática |
| --- | ---: | ---: | --- |
| 2340 × 1080 (A56) | 690,93 → 760,03 px | x=870,01 px | Cinco botões de 269,19 × 70,20 px; busca/atualizar separados |
| 1920 × 1080 | 690,93 → 760,03 px | x=850,27 px | Botão online de 280,80 px; três secundários de 233,54 px |
| 1280 × 720 | 460,62 → 506,68 px | x=566,84 px | Botão online de 187,20 px; três secundários de 155,69 px |

A checagem numérica da receita confirma ganho exato de 10%, área positiva para todos os botões, borda final dentro da tela, separação de busca/atualizar, largura positiva da busca e miniaturas conservadas. O posicionamento de cada botão e seu toque usam a mesma função nativa R164; a capa desenhada e tocada usam `coverSlot()`. O arranjo quase quadrado/vertical já era uma limitação documentada da R164 e não foi alterado aqui.

Para incorporar, copiar a pasta `overlay` da R164 para um diretório de montagem separado e executar `python recipe/patch_width.py --overlay <cópia>`. Compilar o carousel dessa cópia com a cadeia fixada R164, depois combinar com as outras correções aprovadas e os IDs correspondentes. O patch não produz APK nem promove a revisão; após a montagem será necessária conferência visual e de toque no aparelho.
