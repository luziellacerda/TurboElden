# Carregamento e menu de pausa/saída — Turborama

Tela de carregamento existente: LoadingOverlay de classes5.dex, chamada por ESActivity.showLoadingOverlay e hideLoadingOverlay. Novo desenho preto/verde, marca TURBORAMA, detalhes vermelhos, anel verde e nome do jogo limitado à largura. Mesmas chamadas/lógica de exibição e remoção; sem porcentagem artificial. Invalidação da tela existente limitada a 30Hz enquanto visível; sem player/vídeo/3D.

Menu de pausa/saída PS2: LibretroPlayer::run da base 1.0.8. Chamadas de desenho mapeadas por disassembly e texto JOGO PAUSADO, A ESCOLHER B VOLTAR AO JOGO. Retornos drawRect: 0x2af2fc escurecimento, 0x2af34c painel, 0x2af374 faixa, 0x2afe40 linhas, 0x2afe64 linha antiga, 0x2afea4/0x2afedc/0x2aff08/0x2aff34 foco. Somente esses desenhos são personalizados pelo hook existente; ações, limites de toque e execução do motor intactos. Preto/verde, saída selecionada vermelha. Este menu é compartilhado por cores Libretro; não é o menu próprio do Switch.

Compilar build_native.py; empacotar ps2-turborama-ui/build.py em cima de TurboramaStation-abrir-lzgames.apk. Substitui libturbo_carousel.so e apenas a família LoadingOverlay em classes5.dex; sessão classes8.dex, engines e mídia preservadas. Fonte native_skin.h e java/.../LoadingOverlay.java.

Sem novo teste visual ou de navegação. Usuário foi solicitado a deixar o menu aberto para identificação visual. Estável Git anterior preservada; revisão não publicada automaticamente. A análise da integração de vendas permanece pendente após as prioridades visuais.
