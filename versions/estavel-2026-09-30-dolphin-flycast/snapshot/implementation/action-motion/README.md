# Botão vivo e seleção de saída refinada

Correção após feedback: o usuário queria os efeitos internos do CTA animado do site, não o botão submit Entrar estático usado antes. Referência https://app.lzgames.com.br/login; seletor .apk-download-cta no CSS público. Trecho exato em reference-animated-button.css.

ABRIR: degradê se desloca em ciclo 3,8s; faixa diagonal clara atravessa o interior em ciclo 2,5s; três brilhos com defasagem em ciclo 2,2s; seta se move em 1,15s; contorno pulsa suavemente. Paleta permanece Turborama verde/preto, sem o amarelo/laranja predominante do CTA de download. Blur exterior largo retirado. Implementação nativa com malha arredondada, sem nova imagem, shader, FBO, player, temporizador ou trabalho fora da renderização da UI. Não afirmar FPS medido.

Menu de pausa/saída Libretro/PS2: painel com acabamento em gradiente, opções como botões arredondados, aro de seleção fino e brilho interno discreto. Saída selecionada usa vermelho. Quatro barras retangulares do foco antigo removidas. Ações, posições, texto e hitboxes preservados. Tela de carregamento aprovada intacta.

Fontes: native_action_motion.h, native_skin.h. Compilar build_native.py; montar action-motion/build.py sobre ps2-visual-turborama.apk. Apenas biblioteca visual nativa muda; todos os DEX (incluindo loading aprovado e sessão), motores e assets preservados. Estável Git anterior não será movida/publicada automaticamente.
