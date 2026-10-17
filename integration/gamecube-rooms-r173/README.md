# R173 — entrada nas salas GameCube

Base imutável: R172 estável, APK `4a92627952a4f9673ff402667825fcb1f926aaf85a44bef7882559f000c56c5b`.
O proprietário pediu continuar o GameCube e relatou Mario Kart como sala completa.
O diagnóstico real mostrava capacidade 2, um jogador, nenhuma conexão de jogo.

## Causa reproduzida

`StationGamePlayerInfo.fromVerifiedProfile` não reconhecia
`dolphin-gamecube-four-ports-v1`, embora o motor, o servidor e o perfil assinado
já o implementassem. O código retornava `pending()`. Assim `forRoom` informava
`confirmed=false`, `acceptingPlayers=false` e `vacancies=-1`. A lista escondia
o botão de entrada e mostrava “Partida em andamento ou sala completa”.

O probe sobre `rooms.jar` efetivo da montagem R172 reproduziu esses quatro
resultados. A fonte congelada tem SHA-256
`8245787c3f2575401d8c5f514377e7817c4dae7a1f873d548c135cedeb260fb5`.
Isso prova uma falha de apresentação/entrada; não atribui travamento de gameplay
ao servidor ou promete desempenho do Dolphin.

## Diferença

Uma condição aceita esse identificador exato, com máximo de quatro. Permanecem
as verificações de aprovação, contagens, identidade e elenco. Não habilita GBA,
cinco jogadores, controles inventados, jogos individuais ou modos recusados.
O overlay fica nesta pasta; a fonte histórica é preservada.

O probe cobre 82 verificações de vagas 2–4, sala completa/em andamento,
controles desconhecidos, recusa/solo e elencos inválidos. A prova Android e o
teste físico devem ser registrados separadamente, após instalação conferida.

## Compilação

Receita sucessora da R172: um overlay no DEX35, versão 15/R173, três marcadores
de identidade e `engines.json`. Preservar integralmente as demais entradas,
39 DEX, os núcleos/dependências reais, assinatura original, dados, opções de
emulação e PSX `inputDelayFrames=8`. Os quatro IDs precisam de cadastro exato
antes do teste nos aparelhos, pois o fingerprint inclui o DEX35 compartilhado.

Os binários, classpaths e ferramentas privados continuam fora do Git. Os
recibos finais indicarão a fonte realmente congelada e os hashes resultantes.
A R172 continua sendo o ponto estável; esta pasta não promove a candidata,
não publica atualização geral e não comprova gameplay por HTTP ou build.

Estado operacional posterior à compilação: [cadastro e instalação R173](../../docs/server/GAMECUBE-R173-20261017.md).
