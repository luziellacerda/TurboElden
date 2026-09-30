# INSTALADO — botão ABRIR animado e seleção de saída refinada

Instalado em 2026-09-29T18:49:15.043730; Success e SHA256 do APK no aparelho conferidos.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-botao-vivo-saida-premium.apk
SHA256: 325ef75675a84e81332bdd3eb4ddea3652e055d72e76e964f708114c50890bde
Fontes e montagem: E:\ESTUDO APK\work\native-carousel\implementation\action-motion; native_action_motion.h e native_skin.h.

ABRIR: degradê interno em movimento, faixa diagonal de luz, três pontos luminosos e seta animada. Referência correta apk-download-cta do site app.lzgames.com.br/login, com CSS salvo em action-motion/reference-animated-button.css. Não confundir com o Entrar estático usado antes. Paleta adaptada para verde Turborama; halo externo compacto. Animação usa o ciclo nativo existente, sem timer, textura ou player novo.
Pausa/saída Libretro/PS2: painel escuro arredondado, opções arredondadas, seleção verde e Sair em vermelho, brilho interno discreto. Retirada a antiga moldura quadrada. Mesmas ações, textos e áreas de toque. Switch tem menu próprio não alterado nesta revisão.
Tela de carregamento aprovada preservada byte a byte: classes5.dex idêntico. Login persistente, demais DEX, mídia e motores também idênticos. Somente lib/arm64-v8a/libturbo_carousel.so mudou em relação a TurboramaStation-ps2-visual-turborama.apk.

Compilar build_native.py; montar action-motion/build.py. Base e hashes em build-result.json. Instalação por atualização, sem limpar dados ou desinstalar. Tela de plataformas observada antes de instalar; não houve teste de navegação, partida, desempenho ou conferência visual posterior. Não afirmar aprovação visual.
Estável Git estavel-2026-09-29-playlist-retro/acff0dc preservada; revisão não publicada/promovida.
Pendente após as prioridades visuais: analisar Turborama Switch, Git e arquivos locais para integração do site de vendas com senha individual. Nenhuma integração comercial realizada.

## Histórico anterior

