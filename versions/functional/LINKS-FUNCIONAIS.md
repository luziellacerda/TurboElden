# Mapa dos links nesta variante

“Preservado” indica que o caminho de código e o endereço não foram removidos. Não significa que o servidor foi testado em um aparelho ou que dispensa credenciais próprias.

| Função | Link ou origem | Situação |
|---|---|---|
| Jogos já instalados | Armazenamento local/EmulationStation | Sem necessidade de catálogo online para a lista local; exige arquivos e emulador/core compatíveis |
| Catálogo da loja | `https://samboxmanager.squareweb.app/drawers.json` | Preservado, mas GET anônimo retornou HTTP 401: Key obrigatória |
| Catálogo autorizado | `https://samboxmanager.squareweb.app/drawers.json/{chave}/android` | Preservado; nenhuma chave criada ou enviada nesta etapa |
| Cache da loja | `/.emulationstation/store/catalog-cache.json` | Leitura preservada quando existe e StoreUrl está configurada |
| Downloads de jogos e capas do catálogo | URLs contidas na resposta/cache do catálogo | Preservados; os destinos variam por item e dependem de acesso autorizado |
| Cores Libretro ARM64 | `https://buildbot.libretro.com/nightly/android/latest/arm64-v8a/{core}_libretro_android.so.zip` | Preservado |
| Recursos Dolphin | `https://buildbot.libretro.com/assets/system/Dolphin.zip` | Preservado |
| Recursos PPSSPP | `https://buildbot.libretro.com/assets/system/PPSSPP.zip` | Preservado |
| Capas e metadados TheGamesDB | `https://api.thegamesdb.net/v1` | Preservado; sujeito às regras da API |
| Capas e metadados ScreenScraper | `https://www.screenscraper.fr/api2` | Preservado; sujeito às regras da API |
| RetroAchievements em core compatível | `https://retroachievements.org/dorequest.php` | Código do core preservado; depende de configuração/conta |
| Rede Dolphin | `https://lobby.dolphin-emu.org` e `stun.dolphin-emu.org` | Código do core preservado; depende da função online escolhida |
| Recursos do core Suyu | `https://suyu.dev` | Referências do core preservadas; não testadas nesta etapa |

## Comunicação desativada no frontend

| Serviço | Endereço antigo | Como foi desativado |
|---|---|---|
| Licenciamento KeyAuth | `https://keyauth.win/api/1.2/` | POST retorna erro local, sem envio |
| Telemetria e relatórios de falha | `{StoreUrl}/telemetry/android` ou TelemetryUrl personalizado | POST retorna erro local, sem envio |
| Descoberta de IP público | `https://api.ipify.org` ou TelemetryIpUrl personalizado | Rotina de consulta retorna antes de iniciar rede |

O domínio do catálogo não foi bloqueado por inteiro: ele também hospeda funções de uso. Não há servidor novo de assinatura/plano nesta variante.
