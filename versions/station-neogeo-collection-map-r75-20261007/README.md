# R75 — vídeos das coleções Neo Geo

## Resultado

Cinco nomes da tabela nativa tinham `COLEÇÃO` corrompido na R71. A comparação estrita não encontrava a arte específica e usava o vídeo genérico da plataforma. Os seis vídeos Neo Geo já estavam no APK. R74 preservava essa mesma biblioteca; o problema não foi introduzido no motor online R74.

Somente esses cinco literais foram corrigidos por escapes Unicode C++: Fatal Fury, Metal Slug, Samurai Shodown, Art of Fighting e The King of Fighters. `5 - HACKS` já estava correto; não atribuir sua eventual falha física à mesma causa. Neo Geo CD mantém a política anterior e não recebe associação inventada com as coleções de cartucho.

## Preservação

- Base APK R74 exata: `e56896f28b16645653bfd28311cd0a8a9a5458e6d443849916a4dede6dc7fafe`.
- Muda somente `lib/arm64-v8a/libturbo_carousel.so`; 13.224 outras entradas de conteúdo idênticas.
- 59 MP4 no pacote, sendo 58 do carrossel, preservados byte a byte; nenhum arquivo novo de mídia.
- Runtime online, DEX28/35, manifesto, engines, controles, motores e recursos offline idênticos à R74. Não precisa novo registro de motor por causa desta correção visual.
- A célula “Todos os jogos” permanece arredondada e as coleções continuam quadradas. Vídeos de 720 × 720 a 30 fps, sem áudio, um decoder e limite de 30 fps somente no menu permanecem iguais.

## Reprodução e testes

`recipes/build_carousel.py` reconstruiu a biblioteca R71 original byte a byte (`9671f553…`) antes de compilar o delta. Valida por SHA os 65 arquivos de fonte, os includes herdados e os sete objetos.

`recipes/run_tests.py` usa caminhos UTF-8 externos do catálogo do servidor. Em 150 verificações, a base R71 falha 51 vezes, todas nas rotas de Neo Geo; a correção passa em 150 de 150. Executa as funções reais de seleção e fallback com dados de interface simulados. Inclui as seis coleções, aliases, SNES/“Todos os jogos”, casos negativos e preservação da política de Neo Geo CD.

Regressões adicionais: 3.444 verificações de rotas/posters, 66 de cantos, 3.584 de navegação, 199.592 de política do decoder e compilação das verificações de configurações em 60 combinações. São testes no PC; reprodução visual e gameplay no Android ainda não foram conferidos nesta revisão.

## Compilação e entrega

- Fonte do delta: `native/collection_video_policy.h`.
- Build: `E:\ESTUDO APK\work\station-neogeo-collection-map-r75-20261007\native-build`.
- Empacotador: `recipes/package_r75.py`, com base R74 e certificado original obrigatórios; confere todas as entradas e o alinhamento de 16 KiB.
- APK final: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R75-20261007.apk`.
- SHA256: `1ab4fa3770570832ea5ff2e9b0ce4f8a26e0e24e210ad7652f4c96647fecad32`.
- Carrossel novo: `3c2e22bc94f3432280e2b08c2f26ab33508cd1278ee9bd750b48d45c35105a8b`.

Ainda não instalada. Os dois aparelhos estavam em partida e depois saíram da USB. Nenhuma sessão encerrada, configuração alterada ou dado limpo. Atualizar diretamente quando conectado e sem partida ativa.

O mantenedor relatou melhora grande e menos travamentos na R74. É relato de uso, sem medição nova ou promoção de estabilidade geral. A pesquisa de estabilidade fica em `docs/server/PESQUISA-ESTABILIDADE-R74-20261007.md` e não foi aplicada neste APK.
