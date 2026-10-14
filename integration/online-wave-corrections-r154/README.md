# R154: preservar o céu e limitar a sombra às células

A R153 foi rejeitada no teste visual do Galaxy A56. Embora tenha corrigido a
seleção de Ondas Online, substituiu o céu com névoa visto na R152 e escureceu
toda a parte direita da tela. O pedido é manter esse fundo claro e sombrear
somente a faixa atrás das capas pequenas do carrossel.

Esta revisão parte do APK R152 assinado, SHA-256
`f06747b7a953813de5281ddd71f15d8cf36bf8a0ab78920bbe226dabb3c7448e`.
O modo Online restaura o gradiente e as nuvens efetivamente usados
pela R152 e sobrepõe as quatro curvas do modelo da sala online. As cores dos
sistemas, em RGB, são as mesmas da R152; a espessura e a transparência
seguem os parâmetros da sala. O modo Ondas anterior, as configurações e os
outros fundos mantêm suas fontes. A malha de sombra existente conserva uma
chamada de desenho e passa a 782 vértices para sombrear a faixa das seis ou
dez células, inclusive a borda da última capa; fora dela volta ao fade da R152.

Na sala online, as quatro curvas têm alfa RGBA `0x17/0x22/0x3A/0x24` e traços
`14/7/2,2/1,3` pixels em bitmap limitado a 1280×720, ampliado para a tela.
A R153 usava alfa `0x5C/0x70/0x9A/0x72` no tema claro e uma escala de traço
dependente somente da altura; por isso as linhas eram mais fortes e, em tela
larga, de largura diferente da sala. A R154 usa os alfas da sala e a escala
`max(1, largura/1280, altura/720)`; preserva as Béziers e as cores por sistema
do tema claro, sem mudar a animação do modo Ondas já existente.

A receita nativa reproduz a biblioteca R153 byte a byte como conferência de
compilação, mas a R153 rejeitada não é o doador do APK nem dos IDs de motor.
No APK, somente o carrossel, três marcadores de identidade
online e o registro desses motores podem mudar. Os 40 DEX, a ponte frontal e
o restante do aplicativo devem permanecer idênticos à R152. O kit de servidor
deve corresponder ao APK R154 final e seguir a linhagem direta R152→R154, sem
herdar os IDs da R153 rejeitada.

Estado: fonte R154 preparada para validação nativa; APK, assinatura, instalação,
prova visual no aparelho e cadastro no servidor ainda não concluídos. O kit
R153 rejeitado não deve ser entregue ou aplicado ao servidor.
