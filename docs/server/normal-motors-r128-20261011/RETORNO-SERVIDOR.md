# Retorno do servidor — R129 Final-Modal, capas e manutenção horária

O retorno c433052 foi incorporado à mesma entrega R128, com a identidade final R129 `cf623c7` / APK `89dd5439`. As alterações feitas pelo servidor neste repositório são somente estes dois arquivos de retorno. Fontes, receitas, assinatura e recibos Android do produtor permanecem intactos.

Os dois operadores administrativos estão preparados e os **68 testes executados com R129 passaram**; 18 selos públicos e quatro canonicais conferidos. **Publicação protegida pendente da senha na janela nativa Linux. Os quatro novos motores NÃO estão ativados.** O kit de seis bibliotecas R129 ainda não chegou; os modos reais por edição e a aprovação HLE PSX continuam necessários. Perfis genéricos históricos não foram promovidos. PS3/PS4 permanecem offline.

O produtor publicou recibo de instalação integral R129 no Motorola e observação Sony. O servidor não realizou instalação nem teste de gameplay; autenticação/partidas devem ser confirmadas separadamente. O cadastro abaixo usa o bundle final, nunca os IDs R128/intermediários:

| Sistema | Engine final R129 | Estado |
|---|---|---|
| PSX | `pcsx-rearmed-ff81ed17-player-v3-f31f0a3dbfc9` | Kit e aprovação HLE/modo pendentes |
| N64 | `mupen64plus-ae-33bf7021-n64-v3-6868eddfca6c` | Kit e modo por edição pendentes |
| GameCube | `dolphin-5102a033-gamecube-v3-9765756f70fd` | Kit e modo por edição pendentes |
| Wii | `dolphin-5102a033-wii-v3-9765756f70fd` | Kit e modo por edição pendentes |

Receber os seis arquivos em `/mnt/DADOS/station-r128-20261011/kit-privado`: `libpcsx_rearmed_libretro_android.so`, `libstation_psx_online.so`, `libstation_mupen64plus_core.so`, `libstation_mupen64plus_runtime.so`, `libstation_dolphin_online.so`, `libstation_dolphin_runtime.so`. Devem ser extraídos do APK R129 final pela receita selada, conferindo hashes e dependências reais. O arquivo APK final completo também serve de entrada. Não publicar binários privados, BIOS ou credenciais no Git.

A manutenção automática de hora em hora está instalada e ativa no servidor. Os ciclos de13h e14h terminaram com status0; o segundo encontrou este retorno R129 e main `9f598e2` de capas. O monitor consulta os três Gits, trata novidades e registra pendências sem declará-las concluídas. Autenticação Linux continua necessária para arquivos protegidos.

Capas: **2.255 vínculos / 2.150 imagens distintas**, com 671 associações ao modelo recente SNES,331Mega e28PSX. Originais antigos baixados; novos lotes em andamento. A preparação compila JPEG RGB480×720/qualidade90 e troca os vínculos de maneira transacional, preservando IDs, jogos, sinopses e correções do site PS2/PSP/Wii/WiiU. Os278casos não seguros conservam a capa existente. Até os recibos reais, a produção permanece no catálogo33, sem reinício da API.

A operação nativa já preparada espera a senha na janela Linux e o plano de capas. Instala os dois operadores no library-tools efetivo, confirma o import Python novo, qualifica scanner/sandbox/HTTPS sem reconstruir jogos e grava a matriz v3 fresca. O marcador `retomar-autenticado.json` faz o monitor atualizar este mesmo retorno após conclusão/falha. Não reaplicar um lote com `applied.json`; não usar operadores históricos.

Estado privado em `/mnt/DADOS/station-r128-20261011`; automação em `/home/lz-servidor/.local/share/turbostation-retornos`. Backup estável publicado antes das mudanças nos dois repositórios: branch `backup/station-antes-r128-capas-20261011` / tag equivalente. O handoff consolidado permanece `docs/station-android/HANDOFF-ONLINE-PLATAFORMAS-STATION-20261009.md` no Servidor-pix. O recibo detalhado está em `server-return.json` nesta pasta e no mesmo recibo existente do servidor.
