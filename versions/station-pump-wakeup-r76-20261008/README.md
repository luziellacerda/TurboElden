# TurboStations R76 — correção da fila de envio

Código APP-01 integrado sobre R74, com os vídeos Neo Geo da R75. **Compilada, testada localmente e assinada; consulte STATUS e recibos de instalação para cada aparelho. Não declarada estável geral.**

Leia [handoff completo](HANDOFF-APP-R76-PARA-SERVIDOR-20261008.md), [matriz TLS](tests/TRANSPORT-TESTS.md), STATUS.json e evidence/package.json.

APK SHA-256: `d7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51`.
DEX35: `c03ea2f4aa30c5e32654c575115583f72815b9701c16791c4f94c6ade753f2ff`.

201 fontes: 200 preservadas, somente StationRecoveryTunnel.java muda. DEX28, runtime 804b2acfea4c, rs4, controles, mídia e carrossel R75 permanecem exatos. 13.224 entradas preservadas contra R75. Registro de dez engines já ativo no servidor; não exige novo cadastro/reinício.

Corrida reproduzida 64/64 e corrigida 64/64; 1.466 verificações/143 casos; 20 repetições concorrentes; 1.206 regressões; 101 verificações de sessão/42 guardas. Seis execuções TLS/WSS/TCP passaram, com 30.817.216 bytes exatos incluindo crédito cheio e reconexões. A pausa do core é simulada; não equivale a gameplay real.

A DLL candidata do servidor 6f27c6c continua fora da homologação desta entrega. Os ensaios usaram 32ce9 e ab192bf. Preservar limites, autenticação e dados.

## Instalação

Samsung A56 atualizado em 08/10/2026 às 11:25:32 UTC por streaming direto. Hash integral do APK no aparelho conferido; UID e data original preservados, sem desinstalação ou limpeza de dados. A entrada oficial abriu a ESActivity. Não houve teste de partida nesta instalação.

Motorola Edge 30 atualizado em 08/10/2026 às 11:44:14 UTC por streaming direto. Hash integral, UID e data original conferidos. Ambos os aparelhos agora têm o mesmo APK R76; não houve teste de partida em dupla nesta instalação.
