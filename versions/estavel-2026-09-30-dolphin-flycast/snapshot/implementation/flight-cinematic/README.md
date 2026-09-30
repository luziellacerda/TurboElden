# Nave com profundidade e vídeos vizinhos preparados

## Pedido atual

A nave deve ir e voltar pela tela, aproximar-se e afastar-se, com escape menos rígido. O usuário também relatou atraso ao retornar para cartões que ficaram fora da tela à esquerda e pediu mantê-los preparados.

## Voo e escape

- Percurso cíclico de 36 segundos, seis pontos ligados por interpolação de quinta ordem com posição, velocidade e aceleração contínuas, inclusive na emenda. Não há pontos de parada bruscos.
- A trajetória cobre a região livre do carrossel. Aproximação/afastamento vêm de translação no eixo de visão da câmera e projeção do modelo 3D; a fuselagem, a profundidade e a saída da turbina usam a mesma pose.
- Inclinação e direção dependem das derivadas do percurso; limite de inclinação de 31,5 graus. Potência acompanha o deslocamento em profundidade com resposta distribuída por 0,75s, evitando mudanças instantâneas.
- Escape volumétrico com 48 amostras: ruído transportado para trás, mistura de escalas, pequenas estruturas móveis, borda difusa, menor opacidade e cauda irregular. A curvatura responde às taxas de guinada/arfagem, presa à saída real da turbina e recortada pela profundidade da fuselagem.
- Renderização da nave e do escape tem alvo de 60Hz; atmosfera permanece a 30Hz e o deslocamento de nuvens/estrelas mantém velocidade constante. Isso é configuração de renderização, não benchmark do aparelho.
- É uma animação procedural com curvas e efeitos volumétricos; aparência e desempenho ainda precisam de conferência visual no aparelho.

Referências usadas: relação entre curva e inclinação [NASA](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/aircraft-motion-turns/) e composição de emissão/absorção e detalhe de ruído [NVIDIA GPU Gems](https://developer.nvidia.com/gpugems/gpugems/part-vi-beyond-triangles/chapter-39-volume-rendering-techniques).

## Vídeos prontos ao voltar

- Até dois cartões anteriores e dois seguintes à região visível permanecem preparados. Prioridade para as células visíveis e depois para as anteriores, que causaram o atraso relatado.
- O vídeo fora da tela prepara seu primeiro quadro e pausa; player, textura e quadro permanecem válidos. Ao voltar, retoma a mesma instância, sem abrir arquivo, preparar codec ou voltar ao início.
- Até 12 clipes únicos, limitado pela capacidade declarada do aparelho. Células que compartilham arquivo usam uma instância. Fora da janela de vizinhança, recursos são liberados. Não promete cache para todos os sistemas simultaneamente.
- Entrar em jogos, abrir modal ou pausar a Activity libera também os vídeos em espera; não permanecem ativos na emulação.
- Mantidos apenas MP4 da pasta caratulas indicada, 720 × 720 / 60fps codificados, velocidade 1×, um vídeo por célula. Nada de atlas, segunda versão, fotos animadas ou mudança nas cores do usuário. Os sete sistemas ativos sem arquivo na pasta continuam pendentes.

## Caminhos

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
Voo: native_flight.h, native_space3d.h, space3d/scene-common.glsl, space3d/plume.frag.
Pré-carga: native_system_video720.h e system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java.
Montagem: build_native.py e system-videos/build_videos.py.
APK alvo: TurboramaStation-nave-video-cache.apk.
Instalar: system-videos/install_videos.py; recusa emulação ativa e preserva dados.
Registros finais: system-videos/build-result.json e installed.json; cópia em flight-cinematic após finalização.
Fontes anteriores guardados em flight-cinematic/before; registros do último APK em system-videos/revisions/720-single.

A referência estável congelada em E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira e o commit/tag do Git permanecem intocados. Esta revisão não está promovida a estável.
