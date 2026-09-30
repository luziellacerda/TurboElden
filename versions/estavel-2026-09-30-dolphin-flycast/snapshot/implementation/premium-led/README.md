# LED premium nativo — 29/09/2026

Pedido: tornar o LED que percorre a célula principal mais realista e premium.

## Implementação

- Linha fina contínua com ponto luminoso, cauda gradual e dois decaimentos suaves de luz externa.
- Percurso medido em comprimento real, incluindo os arcos dos cantos arredondados, com uma volta em 3,8 segundos. Relógio inteiro contínuo; trocar sistema altera a cor sem reiniciar o movimento.
- Cores exatamente conforme laser-user-overrides.json; Switch azul/vermelho e CPS2 amarelo/azul preservados.
- Apenas o contorno e o halo externo: o centro do vídeo fica livre. Jogos continuam com cantos retos.
- Uma única faixa geométrica de 10 vértices e um shader analítico, sem textura adicional, vídeo, framebuffer ou blur extra. A região central da célula não é rasterizada pelo LED.
- O arquivo premium-selection-laser-android.glsl agora é fonte editável. prepare_laser.py incorpora esse arquivo e a paleta em laser_assets.h; build_native.py executa o preparador automaticamente. O shader desktop original fica preservado como referência.

## Entrega

Compilar build_native.py; empacotar system-videos/build_videos.py; instalar system-videos/install_videos.py; registrar premium-led/finalize.py.
Saída: TurboramaStation-led-premium-diagonal.apk.
Fontes imediatamente anteriores e seus registros: premium-led/before. APK de retorno: TurboramaStation-nave-video-cache.apk, SHA256 d7bf29b5c5498d948994cc4d2ce9e6e9ce3647b8e4d9eac4651823d5a39c30e6.

Preservar voo, pré-carga dos vizinhos, vídeos 720p únicos em loop 1×, motor estável, dados e navegação. Não promover ao Git estável sem pedido. Compilar/instalar não equivale a validação visual ou medição de FPS.

## Pedido adicional — voo diagonal e impressão de marcha à ré

- Corrigido o sinal da guinada: na câmera traseira screen-right equivale a world-X negativo. O sinal anterior inclinava o nariz contra a translação lateral.
- Profundidade de câmera reduzida de -0,40..1,90 para 0,12..1,10 nos pontos de controle; aproximação/afastamento alinhados ao ponto de fuga, sem troca brusca ou desaparecimento.
- Câmera com inclinação diagonal comum de 0,50 rad (~28,65°). Nave inteira, incluindo escape, gira sem distorcer a geometria. Estrelas e nuvens usam o mesmo referencial diagonal e ponto de fuga (0,84; 0,20).
- Estrelas agora projetam profundidade física com focal 2,9 e avanço constante 0,9 unidades/s, iguais ao volume de nuvens. O plano de névoa distante também usa as coordenadas diagonais. Sem rajadas de aceleração.
- Trajetória lateral, inclinação, turbina, casco e profundidade continuam compartilhando a pose. As curvas são contínuas e a vista permanece por trás.

Fontes adicionais: native_flight.h, native_space.h, native_space3d.h e space3d/clouds.frag. Cópias anteriores em before/.
