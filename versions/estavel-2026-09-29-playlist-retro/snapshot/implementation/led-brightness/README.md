# LED mais intenso na célula em evidência

Pedido: o LED da célula principal estava apagado.

Ajustado apenas o efeito de foco: opacidade base do contorno de 0,34 para 0,72; núcleo ligeiramente mais definido; ponto luminoso de 10 para 14 unidades proporcionais; halo próximo e difuso mais fortes; cauda mais longa. A entrada do foco inicia em 75% e atinge 100% em 120ms. Mantidos o percurso arredondado, volta em 3,8s, cores de cada sistema, uma única faixa de 10 vértices e a área interna livre para o vídeo. Sem novas texturas, players ou passes de renderização.

Fontes: premium-selection-laser-android.glsl e native_laser.h. prepare_laser.py gera laser_assets.h durante build_native.py.
Compilar: build_native.py; montar: system-videos/build_videos.py; instalar: system-videos/install_videos.py; registrar: led-brightness/finalize.py.
Saída: TurboramaStation-led-intenso.apk.
Versão anterior: TurboramaStation-videos-retorno-pronto.apk, SHA256 bff401319cd120530ce429c7ca6415881acdcb0460e0eba6f8845c247ab07e41. Fontes e registros anteriores guardados em before/.

Correção de vídeo ao retornar, pré-carga, nave diagonal, motor estável e regras do aplicativo preservados. Compilação/instalação não equivalem a conferência visual ou medição de desempenho. Não promover o Git estável sem pedido.
