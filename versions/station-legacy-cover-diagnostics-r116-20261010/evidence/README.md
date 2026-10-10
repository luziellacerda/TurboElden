# Evidência da R116

`package.json` registra o APK R116 compilado e assinado, hashes, entradas
alteradas e os testes executados. `installation-motorola-r116.json`,
`reinstallation-motorola-r116.json` e `installation-samsung-r116.json`
registram instalação direta e conferência do hash integral nos dois aparelhos.
Os horários desses recibos são os horários reportados pelo aparelho.

A primeira abertura e a progressão da lista SNES foram observadas no Motorola.
O primeiro quadro online, os cenários de rede/429 e o gameplay não foram
validados fisicamente nesta revisão. Os contadores agregados não incluem
sessões, tokens, seriais nem capturas pessoais.

`package-r115-inherited.json`, `physical/`, `frontend/`, `r112-base/` e
`test-fixture-rerun/` foram herdados da base para rastreabilidade. Eles não são
prova de compilação ou funcionamento físico da R116.

Capturas herdadas, fixtures geradas, logs e receitas de medição que contêm
identificadores do aparelho permanecem locais e são excluídos do Git.
