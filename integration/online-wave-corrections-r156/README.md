# R156: três ondas azuis com movimento mais vivo

Na revisão da R155, o usuário aceitou a geometria e o degradê diagonal do
carrossel, mas pediu mais movimento e variação nas ondas. A R156 prepara três
faixas largas preenchidas, como na sala online, com movimento independente mais
vivo e transição fixa de azul escuro para azul claro em todos os consoles e
temas. O modo Ondas anterior mantém a paleta por console. O degradê diagonal
aceito na R155, sem faixa horizontal, deve permanecer.

O APK doador e a linhagem dos IDs de motor partem diretamente da R152 assinada,
SHA-256 `f06747b7a953813de5281ddd71f15d8cf36bf8a0ab78920bbe226dabb3c7448e`.
A biblioteca nativa R155, SHA-256
`f0adaf5fdf9c1fe9ddb86bac2195599a441b69fe0fe9b222d911d6daa2c8f5b2`,
serve apenas para reproduzir e controlar o ambiente de compilação. A R155 não
é doadora do APK, dos IDs nem do kit.

A receita exige fonte R156 congelada em commit, recibo nativo com três faixas
em 154 vértices e prova do novo movimento/azul fixo. No APK, somente a
biblioteca do carrossel, três marcadores de runtime e `engines.json` podem
mudar: cinco entradas no total, 13.855 preservadas, inclusive os 40 DEX e
`libstation_frontend.so`. O kit só poderá ser preparado após aprovação visual
do APK R156 exato instalado, ligada ao commit e SHA-256 desse arquivo.

A revisão de código confirmou que só a rotina ativa das faixas do modo 3 mudou.
O helper novo é usado nessa rotina, e o helper sem uso da R155 foi removido. Não
há novos timers, threads, alocações de heap ou chamadas de desenho. A geometria
usa 154 vértices em uma chamada, contra 206 vértices na R155; são 159 cálculos
de seno por quadro, contra 200 na R155. A R152 era estática e a animação atual
tem custo adicional em relação a ela. Essas são verificações estáticas; ainda
não há medição física de consumo ou bateria.

Fonte registrada no commit `4d2c6b1c73c63204e7928b4aa556b668035fa6f3`.
A biblioteca nativa passou no recibo de compilação. O APK R156 assinado tem
SHA-256 `a072af70c04f0b9f9455b22a856bcdf0995b42da5650c2f9ee87243d17f5d5a6`.
A comparação preservou 13.855 de 13.860 entradas, incluindo 40 DEX, e a
assinatura original v2/v3. O mesmo SHA-256 foi conferido no `base.apk` instalado
no Galaxy A56, sem alterar `firstInstallTime` ou `dataDir`.

Estado: APK instalado para teste físico. A aprovação visual do usuário ainda
está pendente; o kit R156 não foi gerado nem aplicado no servidor. A R152 é a
última revisão com aplicação confirmada; os kits R153, R154 e R155 estão retidos
e não devem ser aplicados.
