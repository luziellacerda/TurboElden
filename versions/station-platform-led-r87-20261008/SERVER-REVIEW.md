# Retorno único do servidor — leitura para R87

Fonte: commit `9502c02e43cf375640b8f99de281a1efe9eb5358`, branch `docs/station-r81-server-return-20261008` do Servidor-pix. Documento: `docs/station-android/HANDOFF-UNICO-FECHAMENTO-ONLINE-1A4-STATION-20261008.md`, retorno de execução R81 e `online-1a4-completo-20261008/production-observation.json`. Código comparado com a base `a4fd0d7`.

## Evidência publicada pelo operador

- Ativação v3: 08/10/2026 21:07:53 UTC; verificação pública às 21:08:56 UTC.
- Serviço `turborama-station-api.service`, PID 1536467, NRestarts 0.
- Fonte DLL `db50a980fcfe01a9b0fee65316f67f43c63ac11c`; SHA256 `cdf14b8067de415413c503de787c6d621c6e8f0466eb2cdd7c0eced8b5a619af`.
- Registro de perfis SHA256 `f3eb13fcb474edb5a1b549a3509aa47505765210b38d1f1dd81bc157b4ec555c`.
- MultiplayerEnabled=true, MultiplayerLegacyCapacityGate=false; dez motores legados preservados.
- 1.816 perfis aprovados ativos: 835 SNES e 981 Mega Drive. Dezessete adicionais preparados ainda não publicados não entram nessa contagem.
- Super Bomberman 2 USA/BattleSingle oferece 2, 3 ou 4 vagas. Perfil genérico para duas vagas não equivale a comprovação física de dois jogadores em cada jogo.
- Observação às 22:00:34 UTC: zero sessões v2/v3 ativas. Testes sintéticos publicados não equivalem a partida Android em quatro aparelhos.

## Código e impacto no app

A configuração deixou de impor o acoplamento entre habilitação multiplayer e bloqueio legado. O caminho v3 continua exigindo perfis exatos e recuperação. Snapshot multiplayer foi acrescentado à prontidão. Não foi encontrada necessidade de um novo APK somente para essa ativação: R86/R87 preservam as identidades funcionais de R81.

O retorno descreve trabalho adicional: ajuda de modos assinada ainda não publicada/consumida; correção isolada do adaptador Sega, ainda dependente de core ARM64, presets e identidade coordenada; candidatos não qualificados e plataformas sem motor online. Esses itens não foram silenciosamente incorporados à atualização visual R87.

Não houve implantação, reinício, mudança de flags ou operação de salas nesta leitura. A evidência de produção é a publicada pelo operador; não se alegou observação direta de sessões autenticadas nem estabilidade em gameplay.
