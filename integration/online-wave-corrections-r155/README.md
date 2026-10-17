# R155: faixas preenchidas e gradiente contínuo

A R153 e a R154 foram rejeitadas na revisão visual do Galaxy A56. A R155
implementa quatro faixas largas, preenchidas e animadas no modo Ondas Online,
no estilo `StationWaveBackground`. Elas usam as cores RGB do console por índice
cíclico nos dois temas. O modo 3 tem base plana azul no tema claro e preta no
escuro, sem nuvens, e um gradiente contínuo em diagonal no canto inferior
direito, sem banda horizontal. O modo 0 mantém céu e nuvens. A função das ondas
do modo 1 e a rota preta do modo 2 permanecem inalteradas; o novo degradê do
carrossel é compartilhado entre os modos. No Galaxy A56, o usuário aceitou a
geometria e o degradê, mas após nova avaliação considerou as ondas pouco vivas
e pediu movimento mais variado e tonalidade do azul escuro ao azul claro. A
R155 não recebeu aprovação visual final e será substituída pela R156.

O APK doador é a R152 assinada, SHA-256
`f06747b7a953813de5281ddd71f15d8cf36bf8a0ab78920bbe226dabb3c7448e`.
A reprodução nativa byte a byte da R154 serviu somente para controlar o ambiente
de compilação; a R154 não entrou na linhagem dos IDs online. As quatro fontes
R155 foram congeladas no commit `9f3fe342042b06a94ae07ad23dd665b131ef29d7`.
A auditoria do APK final encontrou exatamente cinco entradas alteradas e 13.855
preservadas; os 40 DEX e `libstation_frontend.so` são idênticos à R152. Os IDs
de PSX, N64, GameCube e Wii foram vinculados diretamente à R152.

O APK assinado R155 tem SHA-256
`dba9cd2d77748711ff86818c02315488c205edd67ec8773c8e813ce3bc609c9f`.
Foi instalado no A56; o hash do APK instalado bateu e o `firstInstallTime` foi
preservado. O kit privado vinculado a esse APK foi gerado após uma aprovação
visual inicial, posteriormente revista, com SHA-256
`18c998faf37cb9ba88690031a6f5b0a3cf8cd46dcb81459fc28f2d94738e44a4`.
O kit está retido: não entregar, cadastrar ou aplicar no servidor. A última
revisão com aplicação confirmada no servidor é a R152. Nenhuma partida física
foi validada pela R155.

Estado: compilada, assinada e instalada no A56; geometria e degradê aceitos,
movimento e tonalidade das ondas pendentes de correção na R156. Kit R155
preparado e retido, sem cadastro ou aplicação no servidor. Não aplicar os kits
R153, R154 ou R155.
