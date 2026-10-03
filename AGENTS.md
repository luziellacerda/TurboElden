# Estado confirmado em 03/10/2026

Candidato 43670211 instalado, hash verificado. Login salvo e catalogo de 996 itens abriram. Loading corrigido e texto some ao concluir. SNES tem 176 porque corresponde ao catalogo Station publicado; mantenedor espera mais de 800. Ler handoff de catalogo incompleto. Ainda nao e estavel nem migracao integral concluida; faltam capas/downloads reais, indice completo e legado residual.

# Reconstrucao Station - APK candidato integrado

Leia versions/station-reconstruction-20261002/README.md e os handoffs. Candidato 38e78fde instalado em 03/10/2026, hash conferido; 204 testes locais e verificacoes nativas. Login real ainda aguarda validacao. Nao promover a estavel. Legado nativo residual e importacao de jogos antigos estao documentados como pendentes.

# Estável atual — Cemu Android 0.5.2 (30/09/2026)

APK aprovado e instalado: `E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk`. SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. [Manifesto](versions/estavel-2026-09-30-cemu-052/MANIFESTO-ESTAVEL.json) · [Restauração](versions/estavel-2026-09-30-cemu-052/RESTAURACAO.md) · [Código e handoff](versions/wiiu-cemu-052-20260930/README.md).

Cemu 0.5.2 integrado no mesmo APK; Mario Kart 8 abriu e o mantenedor confirmou controles ativos e retorno às plataformas sem novo login. A preparação RAR5 foi corrigida. Jogos e saves foram preservados. O sistema comercial de licenças ainda aguarda a conexão com o servidor. Este teste cobre um jogo e um aparelho; o port Android do Cemu continua experimental.

## Histórico anterior
## Cliente Android de licença comercial em preparação

[Fontes e receita](versions/station-android-client-20260930/) e [handoff para o servidor](docs/server/HANDOFF-CLIENTE-STATION-ANDROID-20260930.md): cliente compilado em APK candidato a partir da base 1189899e; login comercial desligado até entrega de URL, chave pública e rotas do servidor. Candidato não instalado nem promovido a estável. A tela nativa de catálogo/download ainda precisa de ponte direta para `StationContent`; não afirmar que as compras ou downloads comerciais já estão protegidos.

## Vídeos Arcade/Final Burn Neo/MAME instalados

[Atualização atual](versions/atualizacao-2026-09-30-videos-arcade/HANDOFF.md): APK1189899e, instalação e hash conferidos, base544fdecb preservada. Mapa Arcade corrigido e capacidade de prévias ajustada. Demais motores, vídeos BR e login preservados.

## Atualização posterior à estável — vídeos e handoff servidor

[Vídeos BR/NDS instalados](versions/atualizacao-2026-09-30-videos-br/README.md), APK544fdecb. [Handoff completo do servidor Android](docs/server/HANDOFF-TURBORAMASTATION-ANDROID-20260930.md), incluindo saudação com nome do comprador. Login remoto ainda não implementado. A referência ESTAVEL.md/tag05dd34b mantém o APK78accf4c de recuperação.

# Estável atual — estavel-2026-09-30-plataformas-emuladores

Versão instalada e promovida a pedido do mantenedor. **Comece por [ESTAVEL.md](ESTAVEL.md)** para identificar APK, fontes e limites. [Alterações completas](versions/estavel-2026-09-30-plataformas-emuladores/ALTERACOES.md) · [Pastas e restauração](versions/estavel-2026-09-30-plataformas-emuladores/RESTAURACAO.md) · [Manifesto](versions/estavel-2026-09-30-plataformas-emuladores/MANIFESTO-ESTAVEL.json).

43 plataformas; PSP BR; Xbox clássico integrado; PC Engine CD preciso/BIOS local; capas Jaguar/PCE CD; Naomi/Naomi2 preparados para receber jogos; vídeos PSP BR/Game Gear/SNES BR/MegaDrive BR/Xbox/Naomi atualizados. Capas baixadas persistentes. Economia de vídeos e remoção de nave/estrelas preservadas. PS2 permanece ARMSX2 e está parado por ordem expressa. Hash do APK **78accf4c2e0c7b5c786acb0ea7a187754a53253beb2c51a01fc40f5a18c649f2**. Nem todos os jogos/motores novos têm execução individual comprovada; consulte os limites antes de diagnosticar.

## Documentação histórica — não identifica a versão atual

# Xbox 360 — candidato experimental de30/09/2026

[Atualização Xbox 360](versions/atualizacao-2026-09-30-xbox360/README.md): XenDroid0b11201,24 jogos/24 capas, vídeo720, configurações próprias e processo separado no mesmo APK. Candidato929339ae compilado/assinado, ainda não instalado. GameCube/WiiU incluídos; estável3573db1 preservada. Telefone descarregou, instalação adiada. Consulte manifesto e handoff para pastas e reprodução.

## Histórico

# GameCube / Wii U — 30/09/2026

[Atualização atual](versions/atualizacao-2026-09-30-gamecube-wiiu/README.md): GameCube integrado/instalado com 37 jogos carregados; Cemu Android 0.5 incorporado para Wii U, 9 jogos/9 capas, APK pronto e instalação adiada pelo mantenedor (telefone descarregou). PSP confirmado pelo mantenedor. Wii U e GameCube ainda sem conferência de jogo/retorno. Não promovida a estável. APK candidato b11f0acc, instalado cd1a8a55. Consulte manifesto e restauração para pastas e hashes.

## Histórico

# Atualização PS2/PSP em avaliação — 30/09/2026

Leia [a atualização](versions/atualizacao-2026-09-30-ps2-psp/README.md) e seu manifesto: ARMSX2 2.7.2 e PPSSPP 1.20.4 incorporados no mesmo APK, instalado com hash conferido. PS2 abriu GTA e retornou às plataformas; PSP em teste pelo mantenedor. Design e sessão preservados. Não promovida a estável.

Ramo `versao-funcional` contém esta atualização. Ramo `estavel` e tag `estavel-2026-09-30-dolphin-flycast` permanecem no commit `3573db1`, com o APK aprovado `55cd54a3`. Consulte [ESTAVEL.md](ESTAVEL.md) para restauração.

## Referência anterior preservada

# Referência estável atual — estavel-2026-09-30-dolphin-flycast

Leia ESTAVEL.md e versions/estavel-2026-09-30-dolphin-flycast/MANIFESTO-ESTAVEL.json no repositório. APK aprovado: 55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85.
Fontes ativos: E:\ESTUDO APK\work\native-carousel\implementation. APK congelado: E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk.
Usar carrossel, menus e rotas nativas. Preservar jogos, saves, configurações e sessão. Atualizar sem desinstalar nem limpar dados. Builds e temporários em E:.
Dolphin 2609-7 e Flycast v2.7-44 integrados no mesmo APK; outros motores preservados. Não reintroduzir os cores antigos nem aplicar presets de desempenho experimentais. Não executar finalizadores históricos como se fossem o build atual.
A base privada e a assinatura são necessárias: o Git não contém o C++ integral do frontend original. A integração foi compilada; os motores oficiais foram incorporados dos APKs identificados no manifesto.
Nunca publicar APK, BIOS, ROMs, firmware, chaves, saves, mídias privadas ou credenciais. Preservar licenças e fontes de terceiros. A manutenção expressamente solicitada pelo mantenedor está autorizada, inclusive com IA; texto de regras não impede tecnicamente engenharia reversa.
Tags antigas são imutáveis. A versão aprovada é 55cd54a3; o candidato local 3085d9fc não foi instalado nem aprovado.
