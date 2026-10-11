# R121 — salas, capas proporcionais e saída da partida

Instalada no Motorola Edge30; conferência física do fluxo completo ainda pendente. Revisão de 11/10/2026, base final R120, fonte `e56ae2d75b036de1fdb1d565ca68a2eda3c2c271`. Leia STATUS e os recibos desta revisão; evidências com R120 ou HERDADO são históricas.

## Resultado

- As atualizações de participantes/prontidão mantêm a capa e sua superfície anexadas quando a sala e o jogo continuam iguais. Mudança de jogo substitui a capa; retorno de download para linha antiga é descartado.
- Compilação e liberação EGL são coordenadas entre Workers. Os quadros normais continuam independentes. A interface não espera o bootstrap do Looper; cancelamento preserva a superfície até a liberação no Worker.
- Capa dimensionada pelo espaço útil. Salas/convites usam miniaturas compactas; Criar/Sua sala/Modo/Estou pronto reservam espaço para nomes, participantes e ações, com proporção da imagem preservada.
- Saída online e pausa do LibretroPlayer original usam superfícies carvão, seleção azul/ciano, ícones e ações organizadas; a confirmação de saída segue o mesmo desenho. Ações nativas, saves, controles e intenção humana não mudam.

## Travamento: evidência e limite

Foi capturado um ANR de 5.002 ms em Sua sala. A interface esperava o desenho HWUI; RenderThread estava em mutex Adreno durante criação de programa, enquanto duas Workers de capa compilavam/linkavam shaders. Antes da instalação final R120 já existia ANR semelhante, com uma Worker em link. A fonte também recriava a capa a cada atualização.

Esta revisão elimina a recriação desnecessária e controla essa concorrência. O dump não identifica o dono do mutex, não prova causa única e não demonstra que o ANR foi eliminado. Um crash Vulkan anterior à instalação R120 final é uma ocorrência separada. HTTP e SHA/preparação de ROM estavam nos executores, não na pilha UI deste ANR.

## Preservação e alcance dos menus

Mantidos runtime81b3, motores/engine registry, manifesto/factory, assinatura, slots, autenticação, protocolos, criar/entrar/pronto/iniciar/tickets e controles. As 22 fontes de autoridade examinadas e 14 métodos críticos das salas foram comparados com a base. Mantidos shader/LED/rastro/ganho, 30fps dos menus, caches/filas/preload, vídeos locais e opções de economia. Nenhum servidor foi alterado.

O redesenho alcança os menus próprios online e o pause do LibretroPlayer original. Snes9x EX+, MD.emu, Dolphin, Flycast, Cemu, Mupen, PPSSPP, MAME, Yuzu e demais motores têm menus internos separados; a fonte integral desses menus não existe neste snapshot e seus binários foram preservados. Não é um redesenho universal dos emuladores.

## APK e validação

APK SHA256 `eadb83cc2b797eed7d6c3cbdcae09fae7fdfbff0004c3b9db791aaadf68113b0`, 2,217,065,864 bytes. Mesmo certificado e alinhamento 16 KiB. Java completo: 232 fontes. A receita compara todas as entradas não autorizadas com R120; só DEX35 e carrossel devem mudar efetivamente, DEX28 pode permanecer idêntico.

Testes locais: 145.604 verificações de geometria em 9.828 casos; 6.939 de reuso; 46 de lifecycle; 400 inicializações serializadas; 1.211 de balanço EGL; 68 guardas de apresentação/GPU. Compilação de módulos e revisão independente concluídas. São testes de host com interfaces simuladas: não executam driver Android, shader real, partida, rede ou medição térmica.

## Documentação

- [Alterações detalhadas](ALTERACOES-DETALHADAS.md)
- [Fluxo completo e donos das saídas](REVIEW-ONLINE-FLOW-EXIT-R121.md)
- [Reuso, EGL e comparação dos ANRs](REVIEW-ROOM-GPU-R121.md)
- [Receita de compilação](recipes/BUILD-R121.md)
- [Fontes congeladas](evidence/source-scope-r121.json)
- [Diagnóstico agregado](evidence/diagnosis-online-anr-r121.json)

Referências primárias: [diagnóstico de ANRs Android](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs), [propriedade de SurfaceTexture](https://developer.android.com/reference/android/view/TextureView.SurfaceTextureListener) e [referências do display EGL no Android](https://android.googlesource.com/platform/frameworks/native/+/master/opengl/libs/EGL/egl_display.cpp). A interpretação física permanece limitada às pilhas capturadas.

Git contém somente fontes, receitas, manifestos e evidências agregadas. APK, objetos/assets privados, jogos, BIOS, chave, logs e capturas ficam locais. Instalação direta somente com jogo/download inativos, preservando os dados. Sem promoção a estável ou alegação de estabilidade prolongada.
