# Câmera traseira e deslocamentos laterais

## Correção solicitada pelo usuário

O sobrevoo em círculo entregue anteriormente foi rejeitado. O pedido esclarecido é ver a nave por trás, como em um jogo: as nuvens já dão a sensação de avanço e a nave faz movimentos de um lado para o outro. Essa interpretação substitui a rota oval e não autoriza recuperar movimentos de hiperespaço, sumiço ou aceleração do fundo.

## Entrega instalada

TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk, SHA256 54681d24d4ae912c0d081b276064264f95ad5e1d41e4e2851d2daa87169c4257. Instalado em 2026-09-29T15:38:48.924303, Success e hash do APK conferido no aparelho.

Atualização sem desinstalar, limpar dados ou mudar preferências. O app foi iniciado pela LoginActivity. Somente lib/arm64-v8a/libturbo_carousel.so mudou frente a sobrevoo.apk/e00b0e94. Motores estáveis 1.0.8/6727ab7, DEX, login aprovado, ícone v2, modelo, catálogo, downloads e demais entradas permanecem idênticos. Hash do módulo visual: 3b3c417be48fe84d6f29555e52443af56406f1f667a02d4f6288aea718fb5a6d.

## Movimento implementado

- Câmera centralizada atrás e um pouco acima da aeronave: (0, 0.95, -3.45), mirando (0, 0.03, 0.18). O eixo +Z do modelo aponta para longe do observador; a cauda e a saída do propulsor ficam voltadas para ele.
- Deslocamento horizontal entre 55.1% e 74.9% da largura da tela, centralizado na área de fundo à direita das capas. Altura central constante em 60%; quadro de renderização limitado a 72% da altura, com tamanho constante por proporção de tela.
- Correções de direção limitadas a +/-6.31 graus, preservando a vista traseira. Inclinação das asas acompanha a taxa de mudança da direção. Interpolação de quinta ordem, trechos retos e retorno contínuo no ciclo de 48 segundos.
- Movimento de posição, inclinação e direção derivam do mesmo comando. Sem órbita, volta completa, oscilação vertical independente ou zoom. Casco, profundidade e propulsor usam a mesma pose e câmera.
- Nuvens e estrelas mantêm origem e avanço constante; não foram aceleradas. Nave continua abaixo da interface e pode ser ocultada por capas opacas.
- Animação cinematográfica de interface; não é simulação física completa. Cache de renderização e ausência de thread nova preservados.

## Fontes, montagem e recuperação

`../native_flight.h`, `../native_space3d.h`, `../space3d/scene-common.glsl`. Shaders gerados automaticamente por prepare_shaders.py. Modelo, materiais e licenças preservados.

Reprodução pontual: `../build_native.py`, depois `build_rear_view.py`. Instalador `install_rear_view.py` recusa se uma EmulationActivity estiver ativa e atualiza com -r. A montagem completa `../package_apk.py --full` passa a terminar em camera-traseira.apk. O APK sobrevoo.apk foi mantido para comparação, mas seu movimento foi rejeitado.

`before/` contém os fontes e o módulo anteriores; o binário do módulo não entra na cópia protegida de fontes. `build-result.json` e `installed.json` registram a montagem e a instalação. `finalize_delivery.py` atualiza os registros a partir da instalação confirmada.

## Conferência realizada

Compilação, assinatura, comparação das entradas do APK e identidade instalada confirmadas. Não houve inspeção visual da animação pelo agente nem teste de desempenho nesta correção; aprovação do usuário pendente.
