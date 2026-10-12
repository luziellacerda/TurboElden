# Integração Java

A proposta não altera classes Java. `StationOnlineGame` consome as opções fixas do manifesto; `StationMultiplayerProfile` inclui essas opções na configuração canônica do controle e exige o SHA-256 correspondente da resposta assinada. `StationRetroLaunch` grava a mesma string em `core-options.cfg` para todos os participantes.

Usar a cadeia Java efetiva R137 como donor. Trocar apenas o manifesto SNES desta proposta e a correção nativa de ciclo de vida depois de sua verificação. Não recompor o DEX por causa da opção HLE, não usar uma Activity histórica e não criar fallback de perfil ou desativar a verificação assinada.
