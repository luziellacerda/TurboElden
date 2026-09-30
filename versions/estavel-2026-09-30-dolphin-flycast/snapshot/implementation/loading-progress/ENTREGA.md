# INSTALADO — barra de preparação por etapas reais

Instalado em 2026-09-29T19:18:16.872763; Success e hash do APK instalado confirmados.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-loading-progresso.apk
SHA256: 0d5a0dccfa1a404759b93d9a32623a102b85e03dca240af0083a9bf04637226b
Fontes e montagem: E:\ESTUDO APK\work\native-carousel\implementation\loading-progress; native_loading_progress.h e loading-progress/java/org/emulationstation/frontend/LoadingOverlay.java. Compilar build_native.py; montar loading-progress/build.py.

Barra verde na tela existente de carregamento, percentual e nome da etapa. Indicador 0/33/66/100 representa três marcos concluídos, não percentual de bytes, shaders ou tempo: motor carregado, jogo carregado, callback de vídeo recebido e overlay encerrado normalmente. O motor não fornece progresso contínuo. Sem temporizador para aumentar percentual; sem pausa artificial na thread de emulação.
Intercepções em relocação verificadas: AndroidBridge show 0x373c54 e hide 0x373ddc; LibretroCore::load 0x2bd298; loadGame 0x2bdcb0. Todas as funções originais mantêm argumentos, retorno e callbacks. Conclusão somente no hide do loop (retorno 0x2abe30), após carga bem-sucedida e aumento do contador real de vídeo do estado Libretro (global 0x3cf338, campo 0x178). O caminho original de hide pode também resultar de timeout de 30 segundos: sem vídeo a barra não marca 100%. Erro/cancelamento não é sucesso.
100% aparece na transição final; 80ms visível e 160ms de fade, mantendo os 240ms totais anteriores. Ring/spinner e identidade visual aprovados preservados. Atualização de progresso via UI thread; o desenho para ao remover a view.

Menu de pausa limpo, ABRIR animado, sessão e demais mudanças anteriores mantidos. Somente família LoadingOverlay em classes5.dex e libturbo_carousel.so mudaram. Motores de emulação, outros DEX, mídia, ações e dados byte a byte preservados. Não implica pré-compilar todos os shaders.
Atualização sem desinstalar ou limpar dados; catálogo observado antes de instalar. Compilação/assinatura/instalação confirmadas; sem teste novo de abertura de jogo, navegação, aparência ou desempenho. Não afirmar aprovação visual.
Git estável estavel-2026-09-29-playlist-retro/acff0dc preservado; revisão não publicada/promovida.
Pendente após prioridades visuais: analisar Turborama Switch, Git e arquivos locais para integração do site de vendas com senha individual. Nenhuma integração comercial realizada.

## Histórico anterior

