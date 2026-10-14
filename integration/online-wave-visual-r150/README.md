# R150 visual: azul, ondas e capa grande SNES

Status em 14/10/2026: **APK R150 compilado, assinado e instalado no Galaxy A56**.
SHA-256 do APK e do pacote instalado:
`e1f9332b5164138b0782a9147bfd47779044e131c758a5dcc4000ae0f3742245`.
Kit privado R150 preparado, SHA-256
`60a73b495a007de144e89ddc21cf8c5d46d011a7c14dba4701d73a8d7628393f`.
O kit ainda não foi aplicado no servidor. A arte nova de referência não estava
presente na biblioteca SNES do aparelho durante a conferência visual.

Este conjunto é uma alteração visual isolada sobre a R149 funcional assinada
(`698e8a7914cc7be2facc00e6701ff1f3533fa13f763358b51578a35d25c2741e`).
A comparação integral das entradas do APK R148/R149 encontrou somente cinco
mudanças: `classes10.dex`, o manifesto `engines.json` e três bibliotecas dos
motores Dolphin/N64/PSX. As partições DEX 28/35/40 e `libmain.so`, usadas por
estas receitas visuais, são byte a byte iguais. A montagem R150 deve preservar
as cinco entradas R149 sem modificação. A montagem R150 foi feita a partir
da R149 assinada.
`recipe/verify_r149_rebase.py` reproduz a prova com SHA256 das 13.860 entradas
dos dois APKs assinados e grava o recibo em local privado.

## Fundo e ondas

O fundo azul passa de `#287EB5 → #5DAEDE` para `#226FA7 → #509ACC` nas telas
nativas e nos dez literais Java delimitados. O visual das ondas nativas aproxima
a composição de quatro curvas da sala online. Mantém 32 segmentos, 33 amostras,
dois `flightSin` por amostra, 66 vértices e uma chamada de desenho por faixa.
Centros, amplitudes e espessuras mudam; relógio e malha por faixa permanecem.
A própria sala online conserva sua geometria Bézier e o redesenho só ao mudar
de tamanho; seus dois tons azuis acompanham o fundo moderado.

SNES/SNES BR usa quatro faixas amarelo, azul, verde e vermelho. Isso acrescenta
uma faixa, 66 vértices e uma chamada de desenho por quadro somente nessa
família. N64 já usa cinco faixas. As demais famílias mantêm cores e quantidades.
Não há nova thread, alocação, textura, temporizador ou acesso à rede.

`recipe/prepare_native_overlay.py` exige os três SHA exatos dos cabeçalhos
visuais mantidos na R149, emite somente eles e comprova inversão integral. A
compilação deve preservar o cabeçalho R148 que oculta somente sinopses de
sistemas e permaneceu igual na R149.
`recipe/prepare_dex_color_overlay.py` lê os DEX reais da R149 decodificados;
o decodificador e `verify_r149_rebase.py` validam os SHA das três partições.
A receita exige os SHA de sete classes e seus métodos, troca somente dez
ARGB em métodos existentes, emite sete classes e comprova reversão exata.
Nunca repor uma partição DEX antiga inteira.
`recipe/patch_dex_binary.py` localiza as dez instruções `const` 31i pelas
tabelas de classes, métodos e protótipos dos DEX assinados R149. Troca apenas
os imediatos de quatro bytes e a integridade dos cabeçalhos, com inversão
byte a byte. O verificador Java pinado usa dexlib2 para percorrer fronteiras
reais de instruções, conferindo opcode, registrador e literal antes/depois.
`--inspect` calcula os três SHA previstos sem gravar DEX ou APK;
as sete classes smali decodificadas diretamente da R149 são o oráculo de
métodos e valores. Na montagem futura, decodificar novamente os DEX alterados
e conferir essas sete classes e todas as demais antes de aceitar o pacote.

## Capa selecionada de jogos SNES

O usuário forneceu a arte original Chrono Trigger 5120×7680 como amostra da
família de capas novas; SHA256
`fefec62a6a3a3933973a695764321050952130a263f7a71f02ed47a9276b9f09`.
A amostra permanece fora do Git. Em coordenadas do shader 1024×1536, os LEDs
violeta laterais ocupam x14–32 e x994–1011, y401–910. As quatro amostras
antigas (`49,565`, `963,565`, `120,42`, `900,42`) somam cerca de 1 na assinatura
e não a habilitam; quatro amostras nos centros dos novos LEDs somam 4. O
resultado permanece ao reduzir a arte a 480×720 ou 262×393. O shader converte
UV normalizada para a malha lógica 1024×1536; o mapa independe da resolução
física do JPEG. As duas regiões
laterais e os dois ícones violeta do rodapé foram mapeados para os pixels da
nova capa. A identificação e a emissão usam os mesmos quatro samples, curva
de luz existente com troca de canais para violeta, contorno, ganho, ritmo de
varredura, cache e quota de bake já existentes. Áreas fora dos LEDs deixam de
ser processadas pelo mapa SNES. A nova arte recebe o subperfil uniforme `0,25`
somente se a plataforma for SNES/SNES BR. O perfil `0` e seu mapa original
permanecem para capas de outras plataformas que usam o fallback; nenhum outro
modelo é alterado. As condicionais de perfil não acrescentam amostras por pixel.
O subperfil SNES `0,25` executa apenas a classificação e o mapa novos: pula a
detecção Mega Drive e o mapa SNES legado. Ambos ficam disponíveis somente ao
fallback de perfil `0`, sem processamento paralelo sobre a capa SNES.
O cache do campo estático identifica esse subperfil com a chave `9`; as
chaves `0–8` e a política de invalidação anterior permanecem iguais.

Apenas a capa grande selecionada na biblioteca de jogos SNES recebe raio de
1,8% da menor dimensão. A geometria usa 16 vértices no mesmo draw da capa,
com UV/cor interpolados e sem máscara de bitmap. O toque nas quinas acompanha
o contorno. Miniaturas, capas de sistemas, vídeo SNES e capas de outras
plataformas mantêm a forma anterior. `recipe/prepare_snes_cover_overlay.py`
exige os SHA dos quatro cabeçalhos nativos de origem, emite somente os quatro e
comprova inversão byte a byte. A arte original não é embutida na saída.
Na variante do classificador por vértice, os 12 vértices adicionais podem
representar até 96 leituras pequenas de textura por quadro; o mapa reduz a
área SNES processada por fragmento. A variante de classificação por fragmento
continua com o mesmo número de amostras por pixel.

## Verificação e publicação

As receitas passaram leitura dos SHA de entrada, limites de substituição e
inversão integral. A compilação reproduziu R145 e R149 byte a byte e manteve a
ABI da biblioteca visual. O APK R150 assinado alterou exatamente oito das
13.860 entradas da R149: a biblioteca visual, três DEX de cor, três marcadores
de motor e `engines.json`. As outras 13.852 entradas são idênticas. A
assinatura original v2/v3 e o alinhamento de 16 KiB foram verificados. A
instalação USB preservou os dados do app, e o SHA-256 do pacote instalado é
idêntico ao do APK assinado. A biblioteca de jogos SNES abriu no Galaxy A56;
as capas antigas visíveis não exibiram o contorno da arte nova,
como previsto pela detecção dessa arte. A capa Chrono Trigger usada como
referência de emissão não apareceu no catálogo do aparelho; portanto, o efeito
aceso na arte nova e a jogabilidade física ainda exigem conferência antes de
promover esta revisão como estável.
