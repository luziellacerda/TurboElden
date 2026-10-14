# R155: faixas preenchidas e gradiente contínuo

A R153 e a R154 foram rejeitadas na revisão visual do Galaxy A56. A R155
prepara quatro faixas largas, preenchidas e animadas no modo Ondas Online,
no estilo `StationWaveBackground`. Elas usam as cores RGB do console por índice
cíclico nos dois temas. O modo 3 tem base plana azul no tema claro e preta no
escuro, sem nuvens, e um gradiente contínuo em diagonal no canto inferior
direito, sem banda horizontal. O modo 0 mantém céu e nuvens. A função das ondas
do modo 1 e a rota preta do modo 2 permanecem inalteradas; o novo degradê do
carrossel é compartilhado entre os modos. Tudo isso ainda precisa da
conferência visual no aparelho.

O APK doador é a R152 assinada, SHA-256
`f06747b7a953813de5281ddd71f15d8cf36bf8a0ab78920bbe226dabb3c7448e`.
A reprodução nativa byte a byte da R154 serve somente para controlar o ambiente
de compilação; a R154 não entra na linhagem dos IDs online. O empacotamento
exige um commit completo das quatro fontes R155, recibo nativo correspondente,
exatamente cinco entradas alteradas e 13.855 preservadas. Os 40 DEX e a ponte
frontal devem continuar idênticos à R152. Os IDs de PSX, N64, GameCube e Wii
serão vinculados diretamente à R152 e ao APK R155 final.

Os scripts de assinatura e do kit estão em caminhos privados R155 separados.
O kit de servidor só pode ser gerado após aprovação visual explícita da versão
exata instalada, registrada com o SHA-256 do APK. Mesmo depois de gerado, o
kit não indica cadastro ou aplicação no servidor.

Estado: fontes nativas preparadas e aguardando revisão estática. Compilação,
assinatura, instalação, aprovação visual e kit R155 pendentes.
