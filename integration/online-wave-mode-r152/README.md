# R152: novo modo Ondas online e fade do carrossel

Revisão visual sobre a R151 assinada. O modo **Ondas** anterior mantém sua fonte
`drawNativeWaves` byte a byte. Uma quarta escolha, **Online**, usa as quatro
curvas cúbicas da tela Jogar online como fundo estático dos sistemas. O tema
claro usa a paleta do sistema selecionado; o tema escuro usa quatro tons neutros.
As curvas são refeitas somente ao mudar tamanho, tema ou paleta e ocupam uma
chamada de desenho por quadro, sem temporizador, thread ou textura adicional.
Na própria tela Jogar online, a escolha Online mostra o fundo estático que já
existia. Céu, Ondas e Sem fundo conservam seus comportamentos.

O fade diagonal já existente permanece uma única malha, calculada quando muda
a geometria da capa. A queda de opacidade começa mais tarde e mantém pelo
menos 36% de preto na borda direita. Esse desenho continua atrás das capas e
é comum a todos os fundos ativos. Em Sem fundo a tela já é preta.

O quarto valor exige uma ampliação de `background > 2` para `background > 3`
na ponte de preferências. `patch_frontend_mode.py` altera um único byte da
instrução AArch64, prova a inversão e confirma a desmontagem. Os DEX 28/35
são montados por método: quatro métodos mais a constante de preferência no
DEX 28 e dois métodos no DEX 35. A conferência pós-montagem exige todas as
outras classes e métodos iguais à R151, inclusive as classes internas da sala.

`build_native.py` reproduz a biblioteca R151 exata antes da nova camada visual.
`build_java.py` compila as quatro fontes contra as dependências fixadas;
`assemble_dex.py` faz a montagem delimitada. `build_candidate.py` exige todos
os recibos, o commit completo de fontes e oito entradas alteradas na APK:
carrossel, ponte gráfica, dois DEX, três marcadores de motor e o registro de
motores. Os outros 13.852 itens do pacote devem permanecer idênticos.

Estado: APK R152 assinado e conferido, com 13.852 entradas preservadas e 38
partições DEX intactas. O kit independente correspondente também está pronto,
com seis bibliotecas de motor e vinte dependências; o resumo da ponte gráfica
no cadastro PS1 confere com o arquivo do APK. Há uma cópia do APK e do kit em F:.
O kit ainda não foi aplicado no servidor e a R152 não foi instalada nem aceita
visualmente no aparelho. A R151 instalada e a R143 estável permanecem intactas.
O cadastro N64 no servidor exige confirmação separada.
