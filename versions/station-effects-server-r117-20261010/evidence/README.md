# Evidência da R117

`build-r117.json` identifica as fontes, ferramentas e payloads compilados.
`package-r117.json`, quando presente, identifica o APK final assinado,
as cinco entradas alteradas e a comparação integral das demais entradas.
O estado vigente está em `../STATUS.json`.

As verificações R117 incluem preferências gráficas, preparação progressiva,
vida útil/cache de campos GL, vídeo estático, fechamento de configurações,
paginação e recuperação de consultas. Os recibos distinguem execução de
funções reais sob mocks, verificações de fonte e compilação Android.
Nenhum deles representa aprovação visual no telefone, medição térmica
ou gameplay pela internet. Contadores agregados não incluem sessões,
tokens, seriais nem capturas pessoais.

Os recibos com `r116` ou `inherited` no nome são históricos da base.
Instalações R116 não comprovam instalação R117.
`physical/`, `frontend/`, `r112-base/` e `test-fixture-rerun/` são materiais
locais herdados, excluídos da publicação R117.

Capturas herdadas, fixtures geradas, logs e receitas de medição que contêm
identificadores do aparelho permanecem locais e são excluídos do Git.

## Conferência física básica R117

`installation-motorola-r117.json` registra a atualização direta, hash integral e dados preservados. `physical-smoke-r117.json` registra carrossel autenticado, aba EFEITOS, botão Modo leve e fundo Ondas; céu e efeitos originais restaurados. Capturas permanecem privadas. Essa conferência não qualifica todas as telas, tempo até primeiro LED, redução térmica ou gameplay. Recibos de build/pacote/publicação anteriores à instalação mantêm seu estado histórico naquele horário.
