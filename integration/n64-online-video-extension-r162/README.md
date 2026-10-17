# R162 — ponte de vídeo do N64 online

## Falha reproduzida na R161

No moto g52, a mesma edição de 007: The World Is Not Enough mostrou imagem no modo individual e tela preta no modo online. O registro online chegou a `Netplay is ready` e `PLAYING`, mas o plugin Glide64mk2 caiu em `SDL_SetVideoMode failed`. O plugin e o Dynarec eram os mesmos nos dois modos. A [análise física](../../docs/server/r161/physical-n64-video-failure-20261015.md) contém as linhas mínimas e os links para as fontes oficiais.

A ponte Android original do Mupen64Plus AE registra a extensão de vídeo em `libmupen64plus-core.so`. A sessão online usa `libstation_mupen64plus_core.so`; logo, a extensão era instalada no núcleo offline. O núcleo online caía no caminho SDL sem superfície Android.

## Delta limitado

- A [receita nativa](../../versions/station-mupen-online-r162-20261015/recipes/build_station_ae_bridge.py) compila `libstation_ae_bridge.so` a partir da fonte AE fixada em `33bf7021549d7873e976884370fbd1a8e7333bc7`. Ela liga `CoreOverrideVidExt` ao núcleo online e expõe o resultado da ligação. `libae-bridge.so` original não muda.
- A [receita DEX](recipe/build_dex.py) troca a ponte apenas quando existe uma sessão N64 online válida. Se a extensão não for registrada, `CoreStartup` retorna erro antes de executar a partida com tela preta. Offline seleciona a ponte original.
- O APK R162 foi montado a partir do APK assinado R161 exato. Só `classes35.dex`, `classes36.dex`, `engines.json` e os três marcadores vinculados mudaram; a ponte online foi acrescentada. As demais 13.854 entradas foram preservadas. Dentro dos dois DEX, 4.715 classes alheias à correção foram comparadas sem diferenças.
- Não foram alterados o núcleo N64, Glide64mk2, RSP HLE, Dynarec, `inputDelay=2`, controles, número de jogadores, transporte, saída, perfil offline, GameCube, Wii, PSX ou layout. Não há thread, timer nem polling novos.

O [empacotador](packaging/build_candidate.py), o [assinador](packaging/sign_private.py) e o [kit privado](packaging/package_private_kit.py) verificam hashes, ABI, opções e todas as entradas. A assinatura mantém o certificado original, v2/v3 e alinhamento de 16 KiB. APK e kit binários ficam fora do Git.

## Estado de validação

O APK assinado R162 tem SHA-256 `7ec742c4cae7b663f2198e347253986b4c4c5d0d0461052dd75df56ca6335dd7`. Foi instalado por cima no g52 e no A56, sem limpar dados, e os dois `base.apk` instalados apresentaram o mesmo hash. O cadastro das identidades R162 depende do recibo do servidor; a partida online, o áudio e a saída do anfitrião **não foram homologados**. No A56, o `DownloadService` estava em primeiro plano havia cerca de 40 minutos antes da instalação; o usuário relatava não haver download ativo, mas o estado órfão não foi comprovado. O serviço foi encerrado para instalar, reapareceu ao abrir o app, e o usuário confirmou que fechou um download. Alguns minutos depois o serviço já não constava nos registros. A abertura iniciou `LoginActivity` e chegou ao painel `ESActivity`, sem processo `:n64core`.

Na primeira abertura do g52 após a instalação, o Android iniciou `LoginActivity` e `ESActivity`; não iniciou `GameActivity` nem o processo `:n64core`. O painel de 24 plataformas abriu depois de 44,6 segundos de preparação do carrossel, dos quais 26,9 segundos foram pré-compilação dos programas MAGAZINE. Nesse intervalo a tela permaneceu em 0%; não houve ANR. O manifesto, o frontend nativo e o carrossel são byte a byte iguais aos da R161. O relato de abertura direta do N64 não se reproduziu nessa abertura e está sendo esclarecido com o proprietário. Não promover R162 a estável antes de testar N64 offline e jogar com dois telefones após o cadastro do kit.

A [auditoria separada da saída do anfitrião](HOST_EXIT_AUDIT.md) descreve uma corrida de encerramento e a prova ainda necessária do convidado. Nenhum ajuste de saída foi misturado na R162.
