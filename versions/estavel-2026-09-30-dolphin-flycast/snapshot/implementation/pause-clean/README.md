# Menu de pausa nativo — correção de proporções

Referência: tela real observada no dispositivo em 2026-09-29, outputs/exit-menu-current.png no workspace.
Fontes: native_pause_menu.h; inclusão em native_action_motion.h; hook adicional em native_carousel.cpp. Cópias anteriores nesta pasta com sufixo .before.
Componentes: painel preto com raio limitado, linhas discretas, fundos de opções com margem vertical, ícones nativos geométricos, rótulos à esquerda, saída vermelha, aviso de save contido. Botão ABRIR anterior permanece intacto.
Mapeamento ABI: GOT 0x3c1398 -> Font::buildTextCache 0x2e9304; somente chamador 0x2bc1cc do helper de texto Libretro. Rodapé original identificado pelo prefixo exato ESTE EMULADOR NAO TEM SALVAR AQUI. Nenhuma regra de save ou ação alterada.
Compile build_native.py; execute pause-clean/build.py; confirme saída normal da partida e tela de plataformas antes de pause-clean/install.py. PS2 compartilha ESActivity: não inferir ausência de partida apenas pela Activity.
Base botao-vivo-saida-premium.apk SHA256 325ef75675a84e81332bdd3eb4ddea3652e055d72e76e964f708114c50890bde. Apenas módulo visual nativo substituído. Não usar bases antigas que perdem a sessão persistente e o carregamento aprovado.
Sem teste de navegação/desempenho nesta revisão. Git estável preservado.
