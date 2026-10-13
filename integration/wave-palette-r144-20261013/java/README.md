# Salas online: somente brilho das ondas

O usuário corrigiu o escopo: a sala online permanece com o tema e suas cores atuais; recebe apenas mais brilho. A paleta por sistema pertence ao carrossel nativo.

`org/emulationstation/frontend/station/StationWaveBackground.java` conserva todos os bytes da fonte produtiva atual, exceto doze constantes ARGB de `updatePalette(int)`. A fonte da última compilação completa R124 é byte idêntica à publicação, SHA256 `fa038decbe408ca4d05c873f2aad4553b2bde8bc091ee162cda3e9881483c5cd`. As revisões seguintes preservam esta família, conforme os escopos e a comparação canônica do montador; não usar uma Activity histórica para montar o APK.

| Gradiente | Alpha anterior | Alpha novo |
|---|---|---|
| Topos das três faixas | `20 / 18 / 18` | `60 / 58 / 50` |
| Rodapés das três faixas | `08 / 06 / 05` | `28 / 24 / 20` |

Os valores da tabela são hexadecimais. RGB, tema preto/azul, fundo opaco, geometria, fase, `SAMPLES=24`, `FRAME_MILLIS=34`, objetos Paint/Path, listeners, foco, visibilidade e economia são exatos. Nenhum campo, import, método, preferência, timer, consulta de rede ou ponte de plataforma foi adicionado.

O baseline integral permanece em `evidence/StationWaveBackground-R143.java.txt`, para comparação, sem entrar como fonte compilável. `evidence/java-source-preservation.json` registra a inversão byte exata: ao desfazer as doze constantes, recupera-se o SHA original. Essa prova é de fonte, não de renderização Android ou aprovação visual.

O montador deverá alterar exclusivamente o conteúdo de `updatePalette` em `StationWaveBackground` da partição DEX28 real da R143. Preserve as demais instruções, campos, classes, lambdas e DEX35 completo; particularmente a mitigação g52 e os reparos online aceitos. A preparação anterior com `setPlatform` e uma ponte RoomsActivity foi cancelada antes de compilar e arquivada apenas fora do Git; não é fonte desta revisão.
