# R93 — GameCube com o motor de LEDs do SNES

Base atual R92: fonte a4ec50ac38f60550681344495fa05a40679c12db, recibo fc8fd99c976a016a30f6834c79cfe6f9db79d23f. Pedido: LEDs GameCube baseados no SNES em brilho, intensidade e velocidade. A capa The Wind Waker foi observada no Samsung antes da alteração; coincide com a moldura roxa dos arquivos locais.

## Alteração

- A mesma função GLSL compartilhada pelo carrossel e pela capa online mantém o relógio, varredura e halo do SNES. Nenhum novo motor, temporizador, draw pass ou mudança de30fps.
- GameCube preserva roxo. Sua detecção e transferência de luminosidade passam a usar os cálculos do SNES trocando apenas os canais R/G: o par luminoso R/B da arte violeta recebe o tratamento do par G/B da arte ciano. Ganho1,6, cabeça3,0, cauda2,2, halo2/5pixels e velocidade0,0048porquadro do relógio60Hz equivalente permanecem idênticos. Uma passagem vertical dura aproximadamente3,47s; a tela segue limitada a30fps.
- Completa o mapa GameCube com aro roxo do selo, centro854/1238 raio128 na arte1024×1536, e separador luminoso do rodapé472–485/1420–1495. As laterais mantêm o mapa existente. A máscara de cor mantém letras brancas, estrelas e ilustração fora dos emissores.
-39arquivos locais foram medidos; todos têm pixels roxos nas laterais e no aro. Isso não declara que todo o catálogo remoto tem a mesma arte. O reconhecimento bilateral da moldura continua impedindo luz em capas comuns sem o modelo compatível. O efeito atua na capa em evidência, como o SNES; não cria renderizadores para todas as miniaturas.

Somente GameCube(modelo5) muda de tratamento. Perfis de outros sistemas mantêm os mesmos cálculos e parâmetros. LEDs e capa online continuam compartilhando exatamente o mesmo texto GLSL. Downloads R92ladoalado, cancelamento, vídeo remotoR91, demais elementos visuais e emuladores preservados.

## Compilação e entrega

220Java compilados; único Java alterado StationCoverLightingShader.java. Dois arquivos nativos alterados: premium-magazine-led-android.glsl e seu cabeçalho gerado magazine_shader.h. Compilação/link GLSL emANGLE documentados; não são medição térmica, teste de gameplay nem aprovação visual no Samsung. Nenhum jogo foi iniciado para essa alteração.

Somenteclasses35.dex e libturbo_carousel.so mudam noAPK. Todos os outros arquivos, vídeos, engines, manifesto e assinatura original conferidos. Backup Java/carrossel reproduzido idêntico. R93 instalada diretamente noSamsung com hash/UID/dados preservados. Motorola continuaR86. Aprovação final do efeito pelo mantenedor ainda pendente.

Nenhuma alteração ou handoff de servidor. Ativação do serviço de vídeos R91 continua não confirmada. Git contém código e recibos; fotos/capturas/ROM/BIOS/APK/licenças permanecem privados. Canal e hash corrente emrelease-channels/ACTIVE.json.
