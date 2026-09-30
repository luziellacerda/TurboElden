# Progresso de preparação do PS2/Libretro

0%: nenhuma das três etapas concluída. 33%: LibretroCore::load retornou true. 66%: LibretroCore::loadGame retornou true. 100%: hide do loop após os retornos anteriores e incremento do contador de callback de vídeo. São etapas, não percentual contínuo do trabalho ou tempo restante. UI mostra a contagem de três etapas para explicitar isso.

ABI da base estável: GOT 0x3c1718 -> 0x373c54 show; 0x3c1740 -> 0x373ddc hide; 0x3c2828 -> 0x2bd298 core.load; 0x3c2840 -> 0x2bdcb0 core.loadGame. Retorno de hide do loop 0x2abe30. Estado Libretro em 0x3cf338; contador de vídeo no campo 0x178, incrementado pelo callback em 0x2b3e3c (software) / 0x2b3ee8 (hardware). Hide original também ocorre por fallback após 30 segundos, por isso hide sozinho não é sucesso. Nenhum callback ou instrução de motor é alterado.

Fontes: native_loading_progress.h e java/org/emulationstation/frontend/LoadingOverlay.java. Integração em native_carousel.cpp. Cópia anterior em native_carousel.cpp.before e LoadingOverlay.before.java. Build nativo em build-native.log, montagem em build.py. Base exata menu-pausa-clean.apk, SHA256 62326c8d027ab9bf4fb60a7a9bcd9cf711bd64a80d0bd90c28f0c28991d9816c. Só módulo nativo e família LoadingOverlay de classes5.dex podem mudar; script confere o restante.

Instalar somente após saída normal do jogo e observação atual das plataformas. PS2 compartilha ESActivity. Não inferir ausência de jogo apenas pela Activity. Não usar scripts antigos como etapa final: eles podem remover autenticação persistente/menu corrigido.
Progresso não antecipa shaders nem altera resolução/FPS/velocidade. Não houve teste de execução nesta entrega. Git estável preservado.
