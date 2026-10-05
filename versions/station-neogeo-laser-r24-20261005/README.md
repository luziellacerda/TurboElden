# R24 — laser Neo Geo/CD no padrão do SNES

## Pedido e causa encontrada

O mantenedor informou que o efeito Neo Geo CD não tinha o movimento nem a proporção do Super Nintendo. Na R20/R22, a revista Neo Geo usava `neoMagazine`: quatro amostras próximas, brilho apenas aditivo, base `.25`, cauda `1.7` e cabeça `2.5`. Isso mantinha os emissores acesos mesmo longe do feixe. O quadrado/vídeo CD tinha outro ganho, cabeça normalizada `.018` e relógio aproximado de 10.417 ms para três passagens. SNES usa cabeça `.007`, cauda `.100`, halo 2/5 pixels de referência e contraste variável conforme o feixe passa.

## Alteração implementada

- A revista Neo Geo/CD passa pelo **mesmo corpo do shader das revistas SNES/Mega**. Foram removidos a composição separada `neoMagazine` e seu desvio de saída.
- Conserva a assinatura e o mapa medido da moldura Neo Geo, além das cores originais dos emissores (azul, vermelho, verde, amarelo). Não aplica o mapa Neo Geo a qualquer imagem: a assinatura continua obrigatória.
- Mesmo movimento vertical e relógio de 60 Hz equivalente: `frame=floor(ms*60/1000)`, `phase=(frame%625)*.0048`; três passagens a cada 625 frames. Cabeça `.007`, cauda `.100`, transição `.28/.38` e potência `.18+2.2*tail+3*head`. Largura proporcional à altura da própria arte, sem depender da posição da célula na tela.
- Mesmo ganho 1.6, halo compacto de 2/5 pixels de referência, recuperação do núcleo quente e brilho de contorno. Cor e geometria continuam próprias de cada plataforma. Neo Geo não entra no efeito intermitente do N64.
- O quadrado/vídeo CD usa esses mesmos parâmetros, convertendo a escala 1536 para 1254. O feixe anterior `.018` era cerca de 2,57 vezes mais largo. Os círculos, ícones e borda permanecem encaixados na foto; os pontos impressos do rodapé ficam fora da máscara.
- O programa 2D e o OES usam o mesmo código e a mesma geometria. Todas as amostras OES aplicam `videoTransform`, inclusive as do halo. A textura e o player continuam sendo os existentes.
- Uma área conservadora ao redor dos emissores evita as amostras adicionais no restante do quadrado. Não foi criado framebuffer, player, timer ou passagem de blur. Isso limita o trabalho novo, mas **não equivale a uma medição de GPU no aparelho**.
- O laser externo de foco do carrossel (`native_laser.h`/`laser_assets.h`) permanece igual. O ajuste está nas luzes que fazem parte da imagem.

## Base exata e integração com o layout

Não existe APK separado R23B. A composição desta entrega é:

1. APK R23A instalado: `58c61a4d1e74396ffbefb2c5b6108e1c78a951164080a3b0f32de696330233e8`, fonte de todas as entradas que não mudam.
2. Fontes R23B liberadas pelo chat coordenado, commit `8ead3d767bae957cf82ced448931c69dd0e92a1d`, SO compilado `48eda90ac617b1dbd318f8932883386466d5f3cc8cb10ec6586a4b499d953fab`.
3. Somente quatro arquivos alterados em relação a esse overlay: `magazine_shader.h`, `premium-magazine-led-android.glsl`, `native_neogeocd_square.h`, `neogeocd-square.glsl`.

O recibo `native-build.json` verifica os hashes de todos os arquivos R23B e preserva os demais exatamente. Portanto, inclui a contagem abaixo da sinopse, título abaixo do console e jogadores/estrelas acima, conforme R23B. Preserva rolagem R21, vídeos das três coleções Neo Geo R22, único vídeo focado e controles/motores/downloads existentes.

O link nativo inclui **uma vez cada** `W16/frontend-native/video720_posters.o` (49 prévias) e `W22/neogeo_previews.o` (três prévias novas). Não substituir pelo objeto antigo sozinho, nem duplicar símbolos. Fontes finais completas estão em `native/` deste snapshot; includes/stubs restantes são os W16 registrados no comando do recibo.

## Evidências de PC

`evidence/led-tests.json` contém os resultados, arquivos reais utilizados e hashes:

- Oito programas GLES compilados/ligados no ANGLE sem erro GL.
- 135 comparações de saída dos modelos antigos: **133 exatas**, duas de Mega Drive com diferença máxima de **1/255 em canais**, nenhuma maior. Inclui capas reais SNES, Mega Drive, N64 e dois Neo Geo. Não afirmar 135 comparações byte-idênticas.
- 126 comparações do envelope normalizado entre o SNES e o quadrado CD: 125 exatas, uma com arredondamento de até 1/255.
- Dez pares entre textura 2D e OES exatos. Movimento observado nas duas artes Neo e no quadrado/vídeo CD; assinatura funciona também na textura reduzida. Imagens sem moldura reconhecida e os pontos inferiores não recebem luz indevida nos controles testados.
- A otimização da área vazia tem sete comparações exatas e três com diferença máxima de 1/255. Essa tolerância é explícita no teste e nos resultados.
- Build Android arm64/API26, certificado existente, alinhamento de 16 KiB e preservação integral do pacote passaram. Só `lib/arm64-v8a/libturbo_carousel.so` muda; **13.083 entradas preservadas**.

Os testes são renderizações reais com `glDrawArrays/glReadPixels`. PNGs de referência não são repintados para imitar resultados. OES no PC usa EGLImage, não MediaPlayer Android; não comprova FPS/temperatura, reprodução sustentada nem aprovação estética no aparelho.

## Arquivos locais canônicos

| Recurso | Local |
| --- | --- |
| APK final | `E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005\TurboStations-NeoGeo-Laser-R24-20261005.apk` |
| Fontes/build/testes | `E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005` |
| SO final | `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-neogeo-laser-r24-20261005\libturbo_carousel.so` |
| APK base R23A | `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Jogadores-Estrelas-R23-20261005.apk` |
| Fontes R23B | `E:\ESTUDO APK\work\station-game-details-r23-20261005\native` |
| SO R23B | `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-game-details-r23b-20261005\libturbo_carousel.so` |
| Dependências W16 | `E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native` |
| Objeto adicional R22 | `E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\neogeo_previews.o` |

SHA APK: **d35516420934aeda7cee96af6185a17506146ae7fa2c28f867d6e7c44e721a0b**, 2.053.849.968 bytes.

SHA SO: **bf702a1eee840a850df007f2eb684d9aa7ef7ca7bec486e84bb01f9d9450b2e6**, 93.846.600 bytes.

`compiled-output-archives.json` registra as cópias conferidas antes de remover duplicatas de E, incluindo um SO histórico R16 de `native-build`. Nenhum fonte foi movido ou removido. Compilação e temporários permanecem em E.

## Reprodução e estado do aparelho

Use os fontes finais deste snapshot com o comando e os hashes em `evidence/native-build.json`. `recipes/` conserva preparação, otimização, build, empacotamento, arquivo e instalação. As receitas de preparação têm guardas de execução única: não reaplicar sobre versões posteriores. Para testes, os dois scripts de `tests/` devem ficar juntos; requerem Python com numpy/Pillow, ANGLE e referências privadas listadas no relatório (não publicadas no Git).

Instalar apenas por atualização, mesmo certificado, sem limpar dados. A receita confere o APK instalado R23A, que o frontend está aberto e o hash final. **Instalação R24 concluída às 17:01 de 05/10: atualização sem limpar dados; SHA do telefone idêntico.** SNES aberto com sessão preservada. LED específico Neo Geo ainda não recebeu conferência visual no aparelho; painel em outras plataformas é conferido pelo chat coordenado. Consultar `STATUS.json` e eventual `evidence/installation.json` para o estado posterior. A conferência do painel em várias plataformas está coordenada com o chat original.

Downloads do retorno Servidor-pix `11be7f3`/cliente `6f012a7` continuam separados; não foram introduzidos nesta mudança de LED. Nenhum servidor, jogo, save, sessão, tag estável ou motor foi alterado.
