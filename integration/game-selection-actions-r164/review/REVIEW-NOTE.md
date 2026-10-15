# R164 — nota de revisão geométrica

Revisão estática da receita `recipe/patch_actions.py` contra o overlay nativo R163. Nenhum arquivo de receita, fonte nativa ou APK assinado foi alterado.

## Borda direita da faixa de ações

O desenho nativo proposto usa `left = contentLeft - 0.008*w` e largura `end.x + end.w - left + 0.012*h`. Como o último botão termina em `0.975*w`, a borda direita real é **`0.975*w + 0.012*h`**. A faixa começa em `contentLeft - 0.008*w`, fica em `y = 0.896*h`, tem altura `0.084*h` e termina verticalmente em `0.980*h`, alinhada à capa principal.

O campo `geometry[].strip` da receita calcula largura `right - contentLeft + 0.020*w`, portanto relata borda direita **`0.987*w`**. A diferença do relato para o desenho é `0.012*(w-h)`; é uma divergência do relatório geométrico, não do desenho ou do alvo de toque.

| Tela | Borda real | Borda relatada | Excesso relatado |
| --- | ---: | ---: | ---: |
| 2456 × 1080 | 2407.56 px | 2424.072 px | 16.512 px |
| 1920 × 1080 | 1884.96 px | 1895.04 px | 10.08 px |
| 1280 × 720 | 1256.64 px | 1263.36 px | 6.72 px |

## Limite de proporção do arranjo estreito

No ramo `w < 2.03*h`, cada um dos três botões secundários inferiores recebe largura `(0.907*w - 0.8997520462*h)/3`. Ela é positiva nas amostras 16:9 (256.57 px em 1920 × 1080; 171.05 px em 1280 × 720). Em 1080 × 1080, cai para 2.61 px. Em `w/h <= 0.9920088713`, torna-se não positiva e a função retorna retângulos vazios para todos os botões inferiores e o principal; apenas o ícone de atualização continua com retângulo. Portanto, a auditoria atual confirma as proporções 16:9 solicitadas, mas não valida layouts quase quadrados ou verticais.

Não foi identificado desencontro entre desenho e toque nas amostras 16:9: os cinco botões nativos compartilham a geometria de `stationBottomGameAction`, o botão online usa o mesmo retângulo para desenho e toque, e o ícone de atualização permanece dentro de seu alvo original.
