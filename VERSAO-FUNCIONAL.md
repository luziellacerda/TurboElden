# Carrossel — LED colorido e overlay cinza (01/10/2026)

Código nativo no ramo `versao-funcional`. O LED colorido permanece no aro das células do carrossel principal de sistemas; o overlay cinza transparente da arte foi removido. [Código e handoff](versions/carousel-led-overlay-20261001/README.md). Cemu 0.5.2 estável `7ce3fab3` / tag `estavel-2026-09-30-cemu-052` permanece. APK, `.so` e mídias ficam fora do Git.

## Histórico anterior
# Estável atual — Cemu Android 0.5.2 (30/09/2026)

APK aprovado e instalado: `E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk`. SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. [Manifesto](versions/estavel-2026-09-30-cemu-052/MANIFESTO-ESTAVEL.json) · [Restauração](versions/estavel-2026-09-30-cemu-052/RESTAURACAO.md) · [Código e handoff](versions/wiiu-cemu-052-20260930/README.md).

Cemu 0.5.2 integrado no mesmo APK; Mario Kart 8 abriu e o mantenedor confirmou controles ativos e retorno às plataformas sem novo login. A preparação RAR5 foi corrigida. Jogos e saves foram preservados. O sistema comercial de licenças ainda aguarda a conexão com o servidor. Este teste cobre um jogo e um aparelho; o port Android do Cemu continua experimental.

## Histórico anterior
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

# Referência funcional atual

A versão atual está documentada em [ESTAVEL.md](ESTAVEL.md), tag `estavel-2026-09-30-dolphin-flycast`. As referências abaixo são HISTÓRICAS e não identificam o APK atual.

## Histórico preservado

# Versão funcional — branch separada

Versão atual: **1.0.2-catalogo-local**, com abertura e jogos confirmados pelo usuário. Essa confirmação não equivale a teste de todos os jogos e plataformas.

- [Código, compilação e evidências da versão atual](versions/catalog-local/README.md).
- [Release e APK atual](https://github.com/luziellacerda/TurboRetroEmu/releases/tag/v1.0.2-catalogo-local).
- [Versão histórica 1.0-funcoes](versions/functional/README.md): mantida para rastreabilidade; use a versão atual, que corrige a abertura e o catálogo.
- [Análise original na main](https://github.com/luziellacerda/TurboRetroEmu/tree/main), preservada no commit `89e8e0848a73587e0cfd30fe7535e5dce82303af`.

Os arquivos originais do estudo não foram alterados. Os APKs ficam anexados às releases, não no histórico Git. Esta atualização contém exclusivamente o material do aplicativo Android.

A release atual contém o snapshot de catálogo dentro do APK completo. A chave usada para consultar o catálogo não foi incorporada. Os critérios de sanitização dos documentos históricos descrevem a publicação inicial do estudo; as releases completas são publicações distintas solicitadas pelo mantenedor. Os direitos dos componentes de terceiros permanecem com seus respectivos titulares.
