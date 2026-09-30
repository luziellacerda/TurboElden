# INSTALADO — carregamento e pausa/saída PS2 Turborama

Instalado em 2026-09-29T18:40:12.796134, Success e hash do aparelho conferidos.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-ps2-visual-turborama.apk
SHA256: 4a488ed290da6ac8ded7f066e365d283fcac4762f7c2d52896ac7972336ef450
Fontes, montagem e registros: E:\ESTUDO APK\work\native-carousel\implementation\ps2-turborama-ui

Tela de carregamento existente personalizada: fundo preto/verde, TURBORAMA, nome do jogo e anel verde com detalhe vermelho. Mesmo show/hide, sem progresso inventado; animação somente enquanto visível. Menu nativo Libretro de pausa/saída com painel escuro, foco verde e saída selecionada vermelha. Retornos drawRect exatos mapeados em README.md; sem alteração de hitboxes/ações. PS2 usa esse menu; Switch tem menu próprio e não foi alterado nesta etapa.
Inclui ABRIR com degradê/halo do botão Entrar de app.lzgames.com.br/login e correção de sessão persistente. Somente classes5.dex/família LoadingOverlay e libturbo_carousel.so mudaram em relação à base abrir-lzgames.apk; motores, demais DEX, mídia e autenticação conferidos intactos.

Tela das plataformas observada antes da instalação. Sem teste de abertura de jogo, de saída ou nova inspeção das telas personalizadas. Não afirmar essas verificações. Instalação por atualização, sem limpar dados, jogos ou saves. Usuário ainda pode conferir o visual no aparelho.
Compilar build_native.py; montar ps2-turborama-ui/build.py; instalador desta entrega só foi usado após observar o carrossel, pois PS2 compartilha ESActivity. Para reinstalar, confirmar sempre que usuário saiu da partida. Não reutilizar um screenshot antigo como autorização/estado atual.
Estável Git estavel-2026-09-29-playlist-retro/acff0dc permanece intacta. Esta revisão não foi promovida/publicada.
Pendente após prioridades visuais: análise Turborama Switch/Git/arquivos locais e integração do site de vendas com senha por usuário; URL fornecida app.lzgames.com.br/login. Nenhuma integração comercial implementada.

## Histórico anterior

