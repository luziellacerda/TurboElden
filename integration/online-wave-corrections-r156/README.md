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

A revisão de código deve provar que só a rotina ativa das faixas do modo 3
mudou, sem helpers visuais sem uso nem novos timers, threads ou alocações de
heap. A geometria usa uma chamada de desenho para as três faixas. Essas são
verificações estáticas; ainda não há medição física de consumo ou bateria.

Estado: fontes R156 preparadas e guardas estáticas aprovadas; compilação nativa
e congelamento em commit ainda pendentes. Não há APK R156 assinado ou instalado,
aprovação física ou kit R156 gerado. Nada da R156 foi aplicado no servidor. A
R152 é a última revisão com aplicação confirmada; os kits R153, R154 e R155
estão retidos e não devem ser aplicados.
