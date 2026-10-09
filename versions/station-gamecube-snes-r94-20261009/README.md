# R94 — GameCube com o mesmo efeito do SNES

Pedido final: tudo igual ao Super Nintendo, mudando somente o mapa dos LEDs.

A R93 ainda forçava uma cor GameCube (0.64,0.08,1.0). Agora a capa GameCube recebe a configuração real de cor do SNES, consultando o mesmo registro laserConfigs; o shader mantém essa entrada, sem substituí-la. A capa online também usa a mesma entrada que o SNES.

O relógio, varredura, intensidade, núcleo branco, halo de 2/5 pixels e composição já são compartilhados e permanecem inalterados. O mapa GameCube e a leitura dos canais da moldura roxa são preservados. Os demais sistemas e telas mantêm seus cálculos. Não cria motor, temporizador ou camada adicional. Menu 30 fps, downloads, vídeos, dados e emuladores preservados.

Esta revisão sucede a R93, cujo visual não foi aprovado pelo mantenedor. Compilação, instalação e conferência física devem ser consultadas nos recibos; não pressupõem aprovação visual, desempenho térmico ou estabilidade online.

## Pedidos adicionais na mesma atualização

Switch: mesma curva SNES, luz vermelha existente (1,.025,.008) e mapa Switch. PS1: mesma curva SNES, luz branca (1,1,1) e mapa PS1. Os três perfis usam a mesma recuperação de núcleo, luminância, pico branco, varredura e halo do SNES. As diferenças permitidas são reconhecimento/posicionamento da moldura e cor. A conversão dos canais da arte serve somente para ler a energia dos LEDs coloridos nas imagens; não altera ganho ou velocidade.

## Criar sala no espaço disponível

Novo pedido incorporado antes da instalação: remove o ScrollView e a moldura de Criar sala. Capa proporcional limitada também pela altura disponível, informações e ações no mesmo painel; Escolher jogo e Criar sala lado a lado. Nome online permanece editável sem caixa nem borda. Nomes longos ocupam até duas linhas; detalhes extensos permanecem disponíveis ao tocar no texto. Demais listas/salas e callbacks/contrato de criação não mudam.

## Entrega

220 fontes Java e carrossel compilados. Compilação/link GLSL no PC conferidos; isso não é aprovação visual nem medição de desempenho no Android. APK muda somente classes35.dex e libturbo_carousel.so; 13.224 entradas e 59 vídeos preservados, com mesma assinatura. Backup recompila Java e carrossel byte a byte idênticos.

R94 instalada diretamente no Samsung com hash integral e UID/dados preservados. Motorola não atualizado. Aprovação visual final dos três perfis ainda pendente. Não houve mudança de servidor, emuladores, protocolo, sessão, FPS ou downloads. Layout de Criar sala e nome online atualizado conforme pedido.
