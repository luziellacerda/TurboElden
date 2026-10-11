# R123 — revisão independente do modelo De lado

Revisão de leitura, encerrada em 11/10/2026. Nenhuma fonte de produção foi editada pelo revisor e nenhum build, teste, acesso ao servidor ou operação de telefone foi executado nesta revisão. Não encontrei bloqueador concreto nas fontes finais identificadas em `evidence/review-carousel-side-r123.json`.

## Geometria, imagem e toque

A projeção usa `dx = x - cx`, `dy = y - cy` e `W = 1 + depth * dx`: `x' = cx + c * dx / W`, `y' = cy + vertical * dy / W`. A matriz homogênea implementa exatamente esses numeradores e denominador, em ordem column-major, e é composta à direita da MVP original. A inversa resolve primeiro `dx = (x' - cx) / (c - depth * (x' - cx))`, depois recupera y com o mesmo W. O teste de toque aplica essa inversa antes dos limites e cantos originais.

Com os parâmetros finais de 45° e distância focal de 1,2 larguras, W permanece positivo dentro do slot: mínimo aproximadamente 0,7054. A escala limita toda a projeção ao slot anterior. Os quatro cantos fornecem os extremos de clipping nesse domínio; arredondamento inferior/superior do scissor contém a imagem inteira. O culling anterior permanece válido porque a projeção não sai do slot. Índices e prioridade de pintura continuam os originais.

UVs, cores, blend, quantidade de vértices e chamadas de desenho são conservados. O caminho homogêneo permite a interpolação de textura com o W projetado, evitando deformar a imagem somente como dois triângulos afins. Vídeo/poster e faixa INSTALADO encaminham a mesma projeção. O hero selecionado usa identidade.

## MVP e estado GL

O achado real do autor — renderer nativo usa `u_mvp`, enquanto vídeo/faixa próprios usam `MVPMatrix` — foi corrigido. Disponibilidade e desenho usam o mesmo lookup, primeiro `u_mvp`, depois `MVPMatrix`. Sem programa/uniforme reconhecido, a verificação inicial mantém desenho e picking planos.

O desenho guarda os 16 floats da MVP atual e restaura o mesmo uniforme por RAII após a única chamada ao renderer. Todos os retornos anteriores à guarda ocorrem antes de qualquer escrita. A transformação não modifica programa, textura, framebuffer, viewport ou blend. O ponteiro temporário de projeção também volta ao anterior após capa/faixa e após `roundedCoverQuad`.

O recibo do autor `evidence/renderer-mvp-r123.json` identifica o ELF preservado e os corpos do renderer: strip `0x2e5470`, 320 bytes, e helper `0x2e4de0`, 276 bytes. A lista agregada não contém troca de programa/MVP nem chamada indireta. Esta revisão conferiu o recibo e os pontos de integração; não repetiu o disassembly privado. Um shader externo trocado entre disponibilidade e draw pode usar o fallback XY/UV afim documentado pelo autor; isso não foi alegado como suporte universal.

## Preservação e custo

Reta e Diagonal mantêm as equações anteriores e não entram nas novas chamadas GL. Efeitos das células ou mestre desligados mantêm geometria identidade, preservando a preferência. Getter/ponte/persistência são separados da máscara e revisão de efeitos, com resolução nativa única e leitura inicial no worker existente. O painel remove listeners ao sair.

Foi conferida identidade byte a byte com R122 de oito fontes de rotas, LED/campo/shader, fundo, troca de tema, posição da faixa e preferências gerais. No vídeo e faixa, a alteração geométrica consiste apenas no encaminhamento do strip existente. Nenhuma fila, cache, decoder, limite de FPS ou carregamento foi aumentado. Não existe novo timer, worker, tarefa ou loop contínuo.

De lado acrescenta trabalho finito a cada strip já existente: consultas do programa/location/MVP, composição da matriz e duas escritas do uniforme. Esse custo não foi medido no aparelho. O limite de 30 fps dos menus permanece; não se conclui ganho térmico ou estabilidade da GPU a partir desta revisão.

## Evidências e limites

O autor registrou 81.435 verificações de geometria, 64 de preferências, 19 guardas e 512 da ponte em `evidence/carousel-geometry-r123.json`, além da prova estática do renderer. São provas isoladas do autor, não execuções desta revisão. Incluem restauração da matriz, os dois nomes de uniforme, clipping/picking, identidade de hero/Reta e preservação de UV/cor/draw count. Aparência, interação física, consumo e gameplay continuam dependentes da conferência do APK final no telefone.
