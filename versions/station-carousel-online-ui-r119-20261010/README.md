# R119 — carrossel, configurações e interface online

Base exata R118, fonte `3a72119a69b5da6b4f326f053a13ddebae5a7f69`. Branch `fix/station-carousel-online-ui-r119-20261010`. Não selecionar instalador pelo histórico herdado.

## Alterações

- Prioridade das capas acompanha o hero e seis miniaturas visíveis da lista filtrada, mantendo nove entradas e fila única. As duas últimas miniaturas deixam de ficar fora da prioridade.
- Configurações nativas com navegação/valores alinhados, áreas de toque de48 dp e cores azul-marinho/ciano. Cor do céu separada de seu seletor.
- Efeitos agrupados em Controle geral, Fundo, Capas e mídia e Interface; duas colunas quando a paisagem comporta. Escolhas individuais preservadas, estados Economia/Sem fundo explícitos.
- Online dividido em Partidas/Acesso, ações/campos alinhados, molduras externas redundantes retiradas e paleta coerente.
- Sessão online usa motor RetroArch interno sem seu menu RGUI. Back/Menu/Guide abrem painel próprio; entradas de jogo, BSP-D3, slots, cores, runtime, protocolo e identidades permanecem.

Leia ALTERACOES-DETALHADAS.md, REVIEW-ONLINE-MENU-R119.md e STATUS.json para causas, limites e recibos.

## Reprodução

Receita build.py com argumentos explícitos recipes/build-r119-arguments.json, fases prepare/compile/package. Exige APK R118 SHA256 `960b62397fdff20491a5b842dcab0451fade5d786beb84c40e6a9d91ae456e42`, SDK/JDK/NDK identificados e objetos privados R118 conferidos por hash. Compilação em E:, montagem/final em G:. Chave local aceita somente com certificado idêntico.

Git não contém APK, jogos, BIOS, imagens privadas, chaves ou capturas. Nenhum teste novo executado nesta revisão. Compilação não comprova gameplay, aparência completa ou redução térmica. Recibos históricos herdados não são resultados R119. Sem alteração do servidor ou promoção a estável.

## Entrega confirmada

Instalada diretamente no Motorola Edge30, SHA integral e dados preservados. Usuário confirmou capas carregando; captura da lista SNES em Clay Fighter mostra hero e seis miniaturas completas. Painel Efeitos gráficos observado em duas colunas. Fonte publicada `13b21b9dc08adf7b1820fdeb09bec47a810c1ea5`, remoto conferido. Gameplay online e medida térmica não executados nesta revisão.
