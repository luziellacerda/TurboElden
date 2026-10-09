# R95 — mapa da luz SNES e escolha de modo integrada

Base completa: R94, `ae9fd98e8a82086f85931f2e2ec2bb1d08aba195`, 220 fontes Java. Consulte `STATUS.json` e `INSTALLATION.json` para o estado final da entrega.

## Como o SNES percorre a capa

A cabeça de luz sobe pelas duas laterais simultaneamente, com uma volta a cada aproximadamente 3,47 segundos. A cauda perde intensidade atrás da cabeça; o trecho fora da passagem retorna a 30% do valor de referência. O núcleo pode ficar branco e recebe o halo existente. O efeito é calculado pela posição e pelo tempo, sem armazenar quadros anteriores.

A auditoria da R94 confirmou que GameCube já usava os mesmos coeficientes, cor SNES, ganho e relógio. A diferença estava nas partes da imagem tratadas: máscaras estreitas deixavam parte do brilho roxo pintado permanentemente acesa; os símbolos do rodapé não estavam incluídos. Extrair a função comum, sozinho, não corrigia isso.

R95 conserva o percurso, velocidade, ganho, 30 fps do menu e cálculos SNES. Adapta a área dos LEDs à moldura real do GameCube, incluindo seu halo e os símbolos de nuvem/pasta equivalentes. O aro do selo acompanha a mesma luz. As letras e estrelas prateadas do selo não são emissores no mapa original SNES e permanecem preservadas.

A correção de mapa Switch segmentado preparada nesta versão usa a referência real de Pokémon Café Mix capturada no Samsung. Ela não altera o motor dos jogos.

## Modo da partida

As escolhas de modo e quantidade passam a fazer parte da tela Criar sala, com capa visível e descrição correspondente à seleção. Modos diferentes não devem repetir um rótulo genérico que esconda sua diferença. A criação continua dependendo de confirmação e dos perfis verificados, sem habilitar capacidades não aprovadas. O contrato atual deste cliente permite até quatro jogadores online; não anuncia cinco como disponível.

## Limites e reprodução

- Somente `StationCoverLightingShader.java`, `StationRoomsActivity.java` e os dois espelhos GLSL nativos podem divergir da R94.
- As receitas conferem o conjunto completo de fontes, assinatura original e cada entrada do APK.
- Emuladores, protocolos, motores, mídia, downloads, dados e controles permanecem no conjunto R94.
- Ensaios de renderização no PC e reprodução de compilação não substituem aprovação visual no telefone nem gameplay.
- Sem nova implantação ou handoff de servidor por esta atualização visual.
- Capturas e artes de referência ficam fora do Git; somente código e evidências agregadas são publicados.

## Verificações

`tests/check_room_setup.py` extrai quatro métodos reais da Activity e usa fixtures controlados: 24 verificações do texto, 14 de consistência da seleção e 10 verificações de integração. Não é execução completa da Activity nem gameplay.

`tests/render_regression.py` compila e renderiza os shaders R94/R95 em GLES2 fora da tela. Nas seis fases verificadas, o SNES teve diferença máxima de **zero** por canal. O Switch segmentado apresentou 2.658 pixels alterados entre fases na referência capturada; essa imagem já renderizada serve para verificar o mapa e o movimento, não para medir a luminosidade original da arte.

As 220 fontes compilaram. O DEX do cliente permaneceu idêntico. O APK final altera apenas `classes35.dex` e `libturbo_carousel.so`, mantendo 13.224 entradas e os 59 vídeos. A compilação Java e a do carrossel foram reproduzidas byte a byte a partir do backup consolidado.

`tests/verify_gamecube.py` ativou o mapa nos 39 arquivos de capa analisados. Em dez renderizações comparativas de Wind Waker, o centro da arte, as três estrelas e os pixels prateados das letras tiveram diferença zero. As laterais, nuvem, pasta e aro ficaram mais escuros fora da passagem e mais claros sob a cabeça de luz. As médias registradas são valores RGB do ensaio, não medidas físicas de luminosidade ou consumo.

## Instalação pendente

A R95 está assinada e pronta, SHA256 `5c03e013ff01fd1bf1eaacebc25bf5640b7b9094428e843b3f320b75fa4cf431`. O Samsung saiu da USB antes do início da instalação. Portanto continua R94; Motorola R86. A reconexão já foi solicitada. `recipes/install_verified.py` retoma a atualização direta preservando os dados. A retirada do APK R94 e das cópias preliminares fica condicionada à instalação conferida.
