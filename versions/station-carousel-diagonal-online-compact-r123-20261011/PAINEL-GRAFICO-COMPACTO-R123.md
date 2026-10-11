# Painel de efeitos gráficos R123

A captura do painel anterior mostrava blocos poligonais altos, títulos em caixa alta e textos de estado repetidos. A revisão altera somente a apresentação de `StationGraphicsPanel.java`.

## Apresentação

- Cabeçalho compacto: título de 18 sp, subtítulo de 10 sp e Voltar com alvo de 48 dp.
- Controle geral de altura mínima de 48 dp, sem padding vertical extra, em uma linha com título de 14 sp, resumo de 11 sp e interruptor alinhado à direita. O resumo continua indicando quantas opções estão ativas ou que a economia preserva as escolhas.
- Ambiente em uma linha segmentada: Ondas, Céu e Desligado. Carrossel em outra: Reta, Diagonal e De lado. Cada opção tem alvo de 48 dp; o fundo visível ocupa 32 dp em condições normais de fonte.
- Os efeitos individuais ficam em linhas de altura mínima de 56 dp, com título de 13 sp, detalhe de 11 sp e interruptor de 48 dp. Removidos os textos visuais repetidos ATIVO/DESATIVADO; o estado continua nos interruptores e nas descrições de acessibilidade.
- Uma superfície discreta agrupa a lista, com separadores. Nenhum bloco poligonal ou animação adicional. Paisagem larga mantém duas colunas; retrato empilha os grupos. O conteúdo permite rolagem quando não cabe, sem esticar os grupos para ocupar a altura livre.

## Comportamento preservado

`open`, `createContent`, criação e encerramento do Dialog, vínculo aos listeners e atualização no Activity válido mantêm seus corpos anteriores. Mantidos os handlers de controle geral, fundo e opções independentes; o seletor de carrossel amplia o intervalo para o estilo 2 e chama o mesmo `setStyle`. O modo geral de economia conserva as escolhas individuais e desabilita os controles correspondentes. O estilo continua condicionado aos efeitos de células.

Os desenhos são estáticos e usam os mesmos callbacks de estado do Android. Não foi acrescentado timer, tarefa de rede, thread, shader ou ciclo de quadros.

## Evidências e limites

Fonte SHA256: `7b8483c4775e2f1c2c543f74308be153a4b5b601d1edde3f00881721d0e96654`.

`tests/verify_graphics_panel_r123.py` passou 34 guardas estáticas e compilou os dois fontes reais Panel/StylePreferences contra Android API 34. O desenho combina o alfa ARGB de cada fill/rim/rail com o alfa do Drawable; canais transparentes não são desenhados. O corpo real de ConsoleSurface também foi executado com stubs gravadores em 1.080 casos / 5.508 verificações de transparência, cores parciais e chamadas repetidas. O recibo é `evidence/graphics-panel-compact-r123.json`. Os resultados não representam renderização de pixels Android, medição física de Views, toque, consumo, GPU ou gameplay. A conferência final no aparelho pertence à entrega do APK pelo mantenedor.
