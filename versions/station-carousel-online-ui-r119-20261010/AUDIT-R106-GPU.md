# Auditoria do consumo restante na R106

## Evidência física disponível

Na mesma cena online com uma capa em evidência:

- R105: GPU mediana 91,46%;
- R106: GPU mediana 80,40%;
- R106: CPU média observada 66,73% e FPS médio 49,92 no conjunto de superfícies.

Esses números mostram que mover o classificador para o vértice funcionou, mas
não isolam todo o custo da Activity. O FPS agregado inclui superfícies
independentes e não significa que a capa esteja desenhando a 50 fps.

## Fonte do custo da capa

Na R106, `StationOnlineCoverView.java:64` agenda a capa a cada 34 ms e
`StationOnlineCoverView.java:30` envia um novo `FrameCount` ao GLES. A
visibilidade já é corretamente bloqueada em `StationOnlineCoverView.java:63`.

O classificador migrou para o vértice, porém o fragmento ainda executa em cada
quadro:

- máscara central e `emitterWithRegion` em
  `StationCoverLightingShader.java:701-702`;
- oito amostras de emissor a 2 px e oito a 5 px em
  `StationCoverLightingShader.java:703-710`.

Isso representa 17 avaliações estáticas de emissor/halo por fragmento dentro
do suporte conservador, além da textura base. Dependendo do modelo, cada
avaliação pode consultar a arte. O trabalho é repetido mesmo que bitmap,
plataforma e tamanho permaneçam iguais; somente o envelope de luz depende do
quadro.

A R106 também publica `texture.setAlpha(1)` na thread de UI depois de toda
troca de buffer (`StationOnlineCoverView.java:129`), embora a textura já esteja
visível depois do primeiro quadro.

## Outros renderizadores observados

O hiperespaço é uma superfície separada de 144 estrelas a 25 fps
(`StationHyperspaceView.java:13,25`). Ele já usa estado de Activity,
visibilidade, foco e animações em `StationHyperspaceView.java:40`. Alterá-lo
agora confundiria a medição da capa e mudaria o fundo, portanto ficou fora da
R107.

As estrelas de avaliação fazem uma passagem finita. Lotties aparecem nos
estados vazios e já respeitam visibilidade/foco. Eles não estavam ativos na
cena física usada para comparar a capa selecionada.

## Correção da candidata R107

O FBO em `StationOnlineCoverView.java:166-176` prepara os quatro valores
estáticos. A chave em `StationOnlineCoverView.java:167` impede reconstrução por
quadro. O fragmento animado lê o campo em
`StationCoverLightingShader.java:720-723`. A criação exige duas unidades de
textura (`StationOnlineCoverView.java:120-121`), confere FBO completo na linha
171 e retorna ao renderizador direto da R106 nas linhas 134 e 185.

A revelação da TextureView agora tem guarda única na linha 190.

## Critério físico de aceitação

Medir R106 e R107 na mesma capa, brilho, tema, aparelho, resolução, carga,
temperatura inicial e janela de 60 segundos. Registrar:

1. mediana/p95 de GPU e média de CPU;
2. FPS da superfície e quadros perdidos;
3. memória gráfica e RSS;
4. temperatura antes/depois;
5. capturas no mesmo `FrameCount` ou mesma fase aparente;
6. ausência de novas gerações do campo com a tela parada;
7. ausência de atividade após ocultar ou sair do online;
8. funcionamento do retorno direto em caso de FBO rejeitado.

Sem essa comparação, a R107 continua candidata de fonte. O modelo CPU limita
o erro de quantização, mas não comprova driver, captura nem redução física.
