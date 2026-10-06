# TurboStations R55 — fonte atual para análise do servidor

Esta é a versão instalada no Motorola em 06/10/2026. A R41 continua no histórico; **não é a base atual do aplicativo**.

Leia primeiro [HANDOFF-APP-R55-PARA-SERVIDOR-20261006.md](HANDOFF-APP-R55-PARA-SERVIDOR-20261006.md).

- `netplay-src/` e `dependency-src/`: os 156 fontes usados para gerar `classes35.dex` da R54, preservado integralmente na R55.
- `client/src/`: cliente de licença, catálogo, capas e downloads efetivamente incorporado na R53 e preservado na R55.
- `native/`, `native-dependencies/`: código do carrossel e dependências de código da R55. Recursos de mídia e metadados gerados ficam externos e identificados por hash.
- `exit-menus/`: alteração do HUD de Snes9x EX+ e MD.emu, incluída a partir da R42.
- `tests/`, `client/tests/`: fontes dos testes; `evidence/` contém resultados anteriores e comparação integral dos APKs refeita nesta publicação.
- `STATUS.json`: estado atual, evidências e limites. Não marcar como estável geral nem como netplay homologado.
- `SOURCE-MANIFEST.json`: origem e hash de cada fonte exportado, conferidos contra os recibos da compilação.
- `EXTERNAL-BUILD-INPUTS.json`: entradas mantidas fora do Git. **Este snapshot não é uma reconstrução autônoma do APK inteiro.**

O candidato do servidor em `../station-relay-readiness-20261006/` ainda precisa ser conciliado com esta fonte. Copiar sua Activity da R41 por cima da atual perderia o ajuste de ResultReceiver e o encerramento idempotente da R54.

As receitas em `recipes/original/` documentam comandos e caminhos originais. Não as executar nesta cópia como se os caminhos de trabalho/recursos privados estivessem restaurados. Nenhum APK, certificado privado, licença, ROM, BIOS, save ou mídia privada é publicado aqui.
