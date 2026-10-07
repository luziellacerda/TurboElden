# R65 instalada no Samsung A56

Em 07/10/2026, a atualização R65 foi instalada com dados preservados e SHA completo conferido: `1858459b62a38a85cdd9fbeaafc68d3560008f154f99dd1431752aa0594eb081`. O telefone bloqueado impediu a conferência posterior do catálogo e dos jogos. CD, defeito gráfico do KOF98 e retomada online continuam pendentes de validação/correção conforme o relatório. [Recibo da instalação](docs/server/RECIBO-INSTALACAO-R65-SAMSUNG-20261007.json). O outro telefone não foi atualizado nesta etapa.

## Preparação e auditoria anteriores

# R65 — Neo Geo CD integrado; auditoria de Neo Geo/KOF

[Relatório completo, fontes e reprodução](versions/station-neogeo-cd-r65-20261007/README.md). Candidato sobre R64, APK SHA `1858459b62a38a85cdd9fbeaafc68d3560008f154f99dd1431752aa0594eb081`, somente `classes30.dex` alterado. 37 verificações locais e recompilação idêntica. Não instalado nem declarado estável. O CD anterior não tinha o helper de preparação integrado; R65 monta o CHD com neocdz e BIOS reconhecida. Na revisão14 do catálogo,13nomes de cartucho não constam no MAME0289, incluindo seis da coleção KOF; o defeito gráfico de KOF98 padrão permanece em investigação. USB desconectada antes da leitura de ROM/BIOS. Recuperação online continua pendente; demais mudanças R64 preservadas.

## Histórico preservado

# R64 candidata — controles online e diagnóstico de encerramento — 07/10/2026

Leia versions/station-online-controls-r64-20261007/README.md e o HANDOFF-QUEDA-ONLINE-APP-PARA-SERVIDOR-20261007.md. Mantenedor confirmou R63 jogando online/controles respondem, depois houve queda real às12:24:07Z. Causa exata ainda não comprovada; cliente descartava motivo detalhado. R64 mantém runtime/IDs/protocolo/timers, adapta visual SNES/Mega e adiciona registros seguros. Candidato compilado/testado, ainda não instalado. Não afirmar retomada implementada ou estabilidade geral; operador precisa correlacionarQ01–Q08. Preservar jogos/licença/saves/faixa/nativo/Binder.

## Histórico preservado

# R63 instalada nos dois aparelhos — 07/10/2026

Samsung A56 atualizado após liberação de espaço. Motorola Edge30 já havia sido atualizado. Nos dois, o SHA integral do APK instalado é `d9a35602ddc1141617df70d4b2b1f202d8646c538d4508f5fb3e53ef6b7abc4c`. Sem desinstalação, limpeza de dados, troca de assinatura ou mudança da configuração de tela ligada. UID e data original de instalação preservados. A entrada oficial LoginActivity retornou ao catálogo ESActivity, sem nova digitação de licença.

Recibos: `versions/station-auto-access-r63-20261006/evidence/installation-samsung-r63-20261007.json` e `versions/station-auto-access-r63-20261006/evidence/installation-motorola-r63-20261007.json`. As falhas anteriores de armazenamento abaixo são históricas e foram superadas. Conferências físicas ficam com o mantenedor; não foi validado gameplay em dupla, retorno online completo, latência externa ou controles online próprios. Criar sala nova usando os dois aplicativos R63. Nenhuma alteração funcional adicional foi feita por esta instalação.

## Histórico preservado

# R63 instalada no Motorola Edge30 — 07/10/2026

Atualização concluída e SHA integral `d9a35602ddc1141617df70d4b2b1f202d8646c538d4508f5fb3e53ef6b7abc4c` conferido no aparelho. Mesmo UID e data original de instalação, sem desinstalar, limpar dados ou modificar a configuração de tela ligada. Antes da instalação havia somente ESActivity no histórico ativo da TurboStations; não interrompemos partida. A entrada oficial LoginActivity retornou ao catálogo ESActivity, sem nova digitação de licença. A conferência seguinte mostrou StationRoomsActivity; depois a USB desconectou. A navegação física ficou com o mantenedor. O mantenedor fará as conferências físicas; sem gameplay em dupla comprovado.

Samsung A56 permanece na R62: a tentativa R63 foi recusada pelo Android por falta de armazenamento, e o hash114dba8a da R62 foi conferido após a recusa. Atualizar o Samsung para R63 antes da partida em dupla. Não afirmar que os dois aparelhos estão atualizados. Recibos: `versions/station-auto-access-r63-20261006/evidence/installation-motorola-r63-20261007.json` e `versions/station-auto-access-r63-20261006/evidence/installation-samsung-r63-failed-storage-20261007.json`.

## Histórico de preparação preservado

# R63 — convite curto e senha automática integrados sobre R62

Leia `versions/station-auto-access-r63-20261006/HANDOFF-APP-R63-PARA-SERVIDOR-20261006.md`, STATUS e recibos. Retorno 8d9c670/candidato 1e0f862 conciliados com R62: 161 Java, 158 preservados, três alterados; runtime 899e3527/IDs autopass1. APK d9a35602/DEX e910f431, 302 testes no Windows e recompilação idêntica pela restauração publicada. Visual, Binder, saída e motores locais preservados. Instalação aguarda saída da partida no Motorola; Samsung R62/Motorola R58. Atualizar ambos antes do teste em dupla. Sem gameplay físico comprovado, estabilidade geral ou deploy Linux.

## Histórico preservado

# R62 — handoff do servidor integrado no APK

Leia `versions/station-online-integrated-r62-20261006/HANDOFF-APP-R62-PARA-SERVIDOR-20261006.md`, STATUS e recibos. Fonte atual = R55 + R57 + nove Java R62. Retorno7c6e167/implementaçãof8b019d6 incorporados; agora há DEX/APK Android real. Inclui capas maiores/Sua sala, miniaturas autenticadas, botões finos e criação que só navega após confirmação. Nativo/faixa/motores preservados; sem deployLinux. APK114dba8a. Testes locais10TCP+255salas+14criação e454ParcelAndroidA56 passaram. Gameplay2aparelhos/saídaonline completa/controles online próprios ainda pendentes; não marcar estável geral. Usar recibos para identificar qual APK está em cada telefone.

## Histórico preservado

# Prontidão conciliada com a fonte online R55 e visual R57 — 06/10/2026

Leia `docs/server/RETORNO-ANALISE-APP-R55-STATION-20261006.md` e `versions/station-relay-readiness-r57-20261006/README.md`. Fonte funcional recebida:9d3d45f; sucessora visual considerada:8980cd4; implementação atual:f8b019d6; retorno servidor:e9d86a2. A R57 foi instalada no Motorola segundo o recibo recebido. A versão do outro telefone ainda precisa ser conferida.

O delta conserva o canal ResultReceiver e a saída idempotente da R54, mais o layout atual da R57: Criar sala, barra fina, capas e faixa INSTALADO. Todos os157 hashes Java da composição R57 coincidem com o recibo de produção. São155 arquivos preservados, dois alterados e um novo;158 fontes compilaram Java8/API34 em api-check-only. As39 provas de transporte e255 funcionais se aplicam aos mesmos componentes, sem repetição por alteração visual.

Não há novo DEX/APK compilado ou instalado nem gameplay físico comprovado. Sem alteração de servidor necessária para este delta. No PC usar as receitas novas em station-relay-readiness-r57-20261006, sobre APKbaseR57/e6159fa3, com dependências e certificado originais. Os empacotadores antigos R41/R55 não servem para a sucessora. Não limpar dados ou trocar assinatura; conferir ambos os aparelhos e testar Battletoads, confirmação, inputs e saída/retorno. Controles online próprios, latência externa e aquecimento medido continuam pendentes.

## Histórico anterior

# Sucessora visual R57 — fonte funcional online R55 preservada

Leia [R57: barra fina e Criar sala](versions/station-layout-r57-20261006/README.md) e seu `STATUS.json`. APK SHA `e6159fa3564f0b30c1415b062f42e08e47ea625832e1b2640375b3e8b2b55566`. A fonte atual é o snapshot R55 mais o overlay R57 explicitamente listado; não há mudança no protocolo/motor online. Faixa INSTALADO e posição das capas permanecem idênticas à R55. O pedido de revisão funcional R55 no servidor continua válido; ao alterar a Activity de salas, considerar também o layout R57. Candidato de prontidão d1b535c não integrado; nenhuma partida em dupla declarada corrigida.

## Publicação R55 e histórico preservados

# Fonte atual do app: R55 enviada para análise do servidor — 06/10/2026

A versão atual é **R55**, instalada no Motorola e identificada pelo APK SHA-256 `4c8de4f899af291becdf22c0b551df5e03a813f7ecf536fb360436a5d24d7b39`. Leia [o handoff R55 APP → SERVIDOR](versions/station-current-r55-20261006/HANDOFF-APP-R55-PARA-SERVIDOR-20261006.md) e [o snapshot atual](versions/station-current-r55-20261006/README.md).

R42–R55 ficaram anteriormente apenas no PC/aparelho; esta publicação corrige a defasagem. O candidato de prontidão do servidor d1b535c está preservado, mas foi derivado da R41 e **ainda não foi integrado na R55**. Conciliar com `StationSessionChannel`, fechamento idempotente e HUD atuais: não substituir a Activity inteira pela R41. R55 não é estabilidade geral, não tem partida entre dois aparelhos comprovada nem controles online próprios corrigidos. Não executar a receita de empacotamento R41 sobre R55. Fontes, hashes, testes e dependências externas estão no snapshot; nenhum APK, segredo ou mídia privada foi publicado.

## Histórico anterior — as referências R41 abaixo não identificam o APK atual

# TurboramaStation — TurboElden

Frontend Android da TurboramaStation (pacote de estudo `org.emulationstation.frontend`; TESTE lado a lado `org.turboramastation.frontend`). Um único APK reúne o carrossel nativo e os motores oficiais, cada um em processo próprio.

Ramo padrão deste Git: `versao-funcional`.  
Estável Cemu 0.5.2: tag [`estavel-2026-09-30-cemu-052`](https://github.com/luziellacerda/TurboElden/tree/estavel-2026-09-30-cemu-052), commit `f6d7c04`, APK SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. Detalhes em [ESTAVEL.md](ESTAVEL.md).

O Git publica receitas, pontes, diffs e handoffs. APK, `.so`, BIOS, firmware, ROMs, chaves, saves e vídeos permanecem locais.

---

## Emuladores — o que mudou

Todos os motores abaixo foram incorporados ou atualizados **dentro do mesmo aplicativo**. A ponte Java/nativa da TurboramaStation é compilada aqui; o C++ de cada emulador vem do APK ou do lançamento oficial identificado no manifesto da revisão. Opções de desempenho continuam nos menus de cada motor.

| Sistema | Motor | Processo | O que mudou | Estado |
|---|---|---|---|---|
| GameCube / Wii | **Dolphin 2609-7** (`5102a033`) | `:dolphin` | Motor e menus oficiais Android no APK. Core Libretro antigo removido da base. Saves copiados só se ausentes. Configurações oficiais isoladas. Jogo Wii e retorno sem novo login confirmados. | Estável (tag dolphin-flycast) |
| Dreamcast / Atomiswave / Naomi / Naomi 2 | **Flycast v2.7-44** (`e36e9df2`) | `:flycast` | Motor e menus oficiais. Rotas nativas passam ao Flycast. Botão **VOLTAR AO MENU** no cabeçalho. Toque rápido no retorno corrigido. Fundo Turborama no menu. Naomi e Naomi 2 com célula, vídeo, sinopse e rota; categorias vazias de propósito. | Estável; Naomi preparado para jogos |
| PS2 | **ARMSX2 2.7.2** | `:ps2` | Motor e menus oficiais no APK. GTA San Andreas abriu e voltou às plataformas. Menu de saída com identidade Turborama. | Parado por ordem expressa; permanece 2.7.2 |
| PSP / PSP BR | **PPSSPP 1.20.4** | `:psp` | Motor e menus oficiais. PSP BR (`pspbr`) na mesma rota, 59 jogos da categoria original. Mantenedor confirmou PSP. | Integrado |
| Wii U | **Cemu Android 0.5.2** | processo Cemu isolado | Atualização do Cemu 0.5 (SSimco) para **0.5.2** (SapphireRhodonite). GamePad do jogador 1 habilitado na primeira abertura. Correção RAR5 (Mario Kart 8 deixou de ser tratado como corrompido). Ponte JNI do DataStore reconstruída no namespace isolado. Mario Kart 8 abriu, controles responderam, Sair voltou às plataformas sem login. TESTE 01/10: `keys.txt` do dono já na pasta `Cemu/`; a abertura copia o arquivo se a pasta estiver vazia. Chaves fora do Git. | Estável atual (`7ce3fab3`); TESTE com keys no aparelho |
| Xbox clássico | **X1 BOX 1.2.8** (xemu) | `:xbox` menus, `:xboxemu` jogo | Classes, SDL3, libxemu e conversor XISO do APK oficial. Tabela de controles própria. JOGAR entrega o ISO ao launcher. Retorno à TurboramaStation. BIOS/MCPX/HDD só copiados se ausentes. 54 jogos da chave `xbox`. | Integrado na estável de plataformas |
| Xbox 360 | **XenDroid 0b11201** | processo próprio | Motor oficial, 24 jogos/24 capas, vídeo 720, configurações isoladas. | Experimental; candidato publicado, instalação adiada na época |
| PS Vita | **Vita3K 4115** (`a366df69`) | `:psvita` | Firmware oficial 3.74 no APK TESTE (`assets/psvita-firmware/`); a abertura copia para `files/psvita/setup/`, aplica, cria o usuário **Jogador** e grava `vita3k_app` / `initial_setup_completed`. Motor nativo atualizado 4103 → **4115** (Java idêntico ao 4103; só `libVita3K.so`). PUPs e keys fora do Git. | TESTE 02/10 com 4115 + 3.74 |
| Saturn | **YabaSanshiro Android 1.20.46** | `:saturn` | Core Libretro antigo substituído pela integração Android oficial (GLES/Oboe). Christmas NiGHTS abriu e voltou mantendo login. Vulkan e RetroAchievements fora desta integração. | Integrado |
| PC Engine CD | **Beetle PCE preciso** (`mednafen_pce`) | Libretro ARM64 | Rota nova no núcleo preciso. Fast permanece nos sistemas que já o usavam. `syscard3` local só se ausente. Dois CHDs válidos. | Integrado |
| Jaguar | núcleo já da base | — | 56 jogos válidos; 68 entradas que eram imagem/vídeo/metadado saíram da lista. 58 capas Jaguar/PCE CD locais. | Catálogo corrigido |
| Arcade / FBNeo / MAME | cores já da base + Flycast onde cabe | — | Mapa Arcade passou a `ARCADE.mp4`. Vídeos FBNeo e MAME recompostos 720×720 / 30 fps. Capacidade de prévias acompanha o mapa (44 entradas). | Vídeos atualizados |

### Detalhe por motor

**Dolphin 2609-7** — [alterações](versions/estavel-2026-09-30-dolphin-flycast/ALTERACOES.md) · [GameCube](versions/atualizacao-2026-09-30-gamecube-wiiu/README.md)  
Motor oficial Android, commit `5102a0339c2177575378107b76541e47cc52122d`. GameCube usa esta rota (37 jogos na atualização de 30/09). Dependências isoladas. `libdolphin_libretro_android.so` saiu da base. O Dolphin instalado à parte no telefone continua independente.

**Flycast v2.7-44** — mesmo manifesto dolphin-flycast  
Motor oficial `v2.7-44-ge36e9df2d`. Dreamcast e Atomiswave usam identificadores já existentes. Ajuste de toque: o clique único entre dois quadros deixava de registrar; a ponte conserva a transição no menu principal. Dois retornos observados em 30/09 às 10:23. Candidato posterior de arraste `3085d9fc` ficou de fora.

**ARMSX2 2.7.2** — [PS2/PSP](versions/atualizacao-2026-09-30-ps2-psp/README.md)  
Pedido de subir enquanto testa. GTA renderizou e a saída para plataformas foi confirmada. Tentativa NetherSX2 cancelada e nunca instalada. God of War segue com o defeito gráfico conhecido.

**PPSSPP 1.20.4** — mesma atualização PS2/PSP  
PSP BR permanece na rota PPSSPP, pasta `pspbr`, acesso ESPECIAL original.

**Cemu 0.5.2** — [handoff](versions/wiiu-cemu-052-20260930/README.md) · [RAR5](versions/wiiu-rar5-fix-20260930/README.md) · [keys na abertura](versions/vita-wiiu-pronto-20261001/README.md)  
Doador `Cemu.DualScreen.0.5.2.apk` SHA-256 `e1630fc51a4bbb18ef8499829fad011601d575726f019090abada6c9dd258387`, MPL-2.0. `WiiUBootstrap` liga o GamePad 1 se estiver desligado. `libarchive` RAR5 ignora entradas de diretório. DataStore JNI no namespace `twiiucor`. Teste em Mario Kart 8, um aparelho; o port Android continua experimental. No TESTE, `WiiUEntryActivity.ensureKeys()` deixa `Cemu/keys.txt` pronto copiando o arquivo já existente no aparelho (`EmulationStation/bios/wiiu` ou a própria pasta Cemu). O `keys.txt` permanece local.

**X1 BOX 1.2.8** — [plataformas](versions/estavel-2026-09-30-plataformas-emuladores/ALTERACOES.md)  
Android mínimo efetivo API 29. Ponte apresenta aviso em versões anteriores. TESTE posterior (pacote `org.turboramastation.frontend`) ajustou xemu: OpenGL, 30 FPS, frame skip, OpenSL, DSP desligado, volume 0,7, e atualizou o vídeo 720 da célula Xbox. Esses ajustes de TESTE ficam no APK local; o Git desta pasta descreve a integração 1.2.8.

**XenDroid 0b11201** — [Xbox 360](versions/atualizacao-2026-09-30-xbox360/README.md)  
Lançamento [XenDroid-0b11201](https://github.com/rfandango/XenDroid/releases/tag/XenDroid-0b11201). Compilado e assinado; instalação adiada quando o telefone descarregou.

**YabaSanshiro 1.20.46** — Saturn Android oficial, GLES/Oboe, processo `:saturn`.

**Vita3K 4115** — [pronto na abertura](versions/vita-wiiu-pronto-20261001/README.md) · [3.74 no APK TESTE](versions/vita-t-firmware-20261001/README.md) · [motor 4115](versions/vita-engine-4115-20261002/README.md)  
`VitaEntryActivity` copia os três PUPs oficiais 3.74 de `assets/psvita-firmware/` para `files/psvita/setup/`, aplica no Vita3K, cria o usuário Jogador e marca `initial_setup_completed`. Em 02/10 o `libVita3K.so` passou do build 4103 para o contínuo oficial **4115** (`a366df69`); o Java do doador é o mesmo do 4103. Pacotes PUP e `keys.txt` fora do Git. Correção RAR5 compartilhada com a linha Wii U.

**Beetle PCE preciso** — PC Engine CD; Fast permanece onde já era usado.

---

## TESTE 01/10/2026 — carrossel de sistemas

Código nativo em [`versions/carousel-led-overlay-20261001`](versions/carousel-led-overlay-20261001/README.md), commit `ebc4821`.

- LED colorido continua no aro das células (cabeça e cauda andando no perímetro).
- Overlay cinza transparente que passava na frente da arte das células do **carrossel principal de sistemas** foi removido.
- Paleta em dois tons: Naomi 2 e Model 2 vermelho+azul; PS Vita branco+azul; Nintendo DS branco+vermelho; N64 e N64 BR amarelo+branco.
- Botão ABRIR estático nesse carrossel.
- Cemu 0.5.2, ARMSX2, FBNeo e o APK estável `7ce3fab3` intactos.

Pacote TESTE: `org.turboramastation.frontend`. SHA-256 local após Vita3K 4115 (02/10): `0e7974e1a324c4aabfb475d1fa9081f4307efd52ca099323bcafdd852694478b`. Base 01/10 (T + 3.74, motor 4103): `5090cb83e0d69957e22227b748848ce112c8aa302361cc71b5f336937fbfc7f5`.

Cliente Station deste ponto (02/10, lista no aparelho, sem Miami): [`versions/station-catalogo-20261002`](versions/station-catalogo-20261002/README.md). APK local SHA-256 `c11b98bf0df770ed78a285a38fb897317a5b6ee496ba6b121e2d52304a400a9a`.

---

## TESTE 01/10/2026 — PS Vita e Wii U prontos

Código em [`versions/vita-wiiu-pronto-20261001`](versions/vita-wiiu-pronto-20261001/README.md).

- **PS Vita:** a abertura aplica o firmware oficial 3.74, cria o usuário Jogador e grava `initial_setup_completed`. O Vita3K abre a biblioteca; a tela Install Firmware não aparece.
- **Wii U:** `keys.txt` do dono na pasta `Cemu/` (e cópia em `EmulationStation/bios/wiiu/`). A abertura copia o arquivo se a pasta do Cemu estiver vazia. Chaves fora do Git e do APK.
- Cemu 0.5.2 estável, ARMSX2, FBNeo e o APK `7ce3fab3` intactos.

---

## TESTE 01/10/2026 — ícone T e firmware Vita no APK

Código em [`versions/vita-t-firmware-20261001`](versions/vita-t-firmware-20261001/README.md).

- **Avatar:** o S roxo ao lado de JOGADOR saiu. Sem foto, o cabeçalho mostra o T verde da Turborama (`profile_mockup.png`).
- **PS Vita:** os três componentes oficiais 3.74 (componentes, firmware, fontes) vão no APK TESTE em `assets/psvita-firmware/`. Na primeira abertura a Turborama copia para `files/psvita/setup/` e o Vita3K instala. Pacotes PUP fora do Git.
- Cemu 0.5.2 estável, ARMSX2, FBNeo e o APK `7ce3fab3` intactos.

---

## TESTE 02/10/2026 — Vita3K 4115

Código em [`versions/vita-engine-4115-20261002`](versions/vita-engine-4115-20261002/README.md).

- **Motor:** contínuo oficial Android build **4115** (`a366df69`). Java do doador igual ao 4103; só `libVita3K.so` muda.
- **Firmware 3.74** continua no APK TESTE. Keys do Wii U continuam no aparelho, fora do APK e deste Git.
- **Wii U no POCO (Mali-G720):** tela preta com Vulkan sem BCn (`VK_FORMAT_BC1`…`BC5`). No A56 (Xclipse) a imagem aparece.
- **PS Vita lista vazia após instalar:** o RAR pode entregar o patch antes do jogo base (`Install app before patch`); `ux0/app` fica vazia. O 4115 não altera esse instalador.
- Backup local `G:\BAKUP SISTEMA APP 02-10-2026` (fora do Git).
- Cemu 0.5.2 estável, ARMSX2, FBNeo e o APK `7ce3fab3` intactos.

---

## Linha do tempo das revisões de motor

1. **29/09** — carrossel 720p, LED, playlist retrô ([tag](versions/estavel-2026-09-29-playlist-retro/)).
2. **30/09 manhã** — Dolphin 2609-7 + Flycast v2.7-44, retorno corrigido ([tag](versions/estavel-2026-09-30-dolphin-flycast/)).
3. **30/09** — ARMSX2 2.7.2 + PPSSPP 1.20.4 ([PS2/PSP](versions/atualizacao-2026-09-30-ps2-psp/)).
4. **30/09** — GameCube na rota Dolphin; Cemu 0.5 no APK ([GameCube/Wii U](versions/atualizacao-2026-09-30-gamecube-wiiu/)).
5. **30/09** — XenDroid Xbox 360 experimental ([Xbox 360](versions/atualizacao-2026-09-30-xbox360/)).
6. **30/09** — 43 plataformas, Xbox clássico 1.2.8, PCE CD preciso, PSP BR, Naomi preparado, vídeos BR ([tag plataformas](versions/estavel-2026-09-30-plataformas-emuladores/)).
7. **30/09** — vídeos BR/NDS e Arcade/FBNeo/MAME ([BR](versions/atualizacao-2026-09-30-videos-br/), [arcade](versions/atualizacao-2026-09-30-videos-arcade/)).
8. **30/09 noite** — Cemu 0.5.2 + RAR5 + GamePad ([tag cemu-052](versions/estavel-2026-09-30-cemu-052/), [código](versions/wiiu-cemu-052-20260930/)).
9. **01/10** — carrossel: LED mantido, overlay cinza removido ([código](versions/carousel-led-overlay-20261001/)).
10. **01/10 noite** — PS Vita sem assistente de firmware; Wii U com `keys.txt` na pasta do Cemu ([código](versions/vita-wiiu-pronto-20261001/)).
11. **01/10 noite** — avatar T no lugar do S; firmware Vita 3.74 dentro do APK TESTE ([código](versions/vita-t-firmware-20261001/)).
12. **02/10** — Vita3K nativo 4103 → 4115; 3.74 e keys como no GitHub ([código](versions/vita-engine-4115-20261002/)).

Cliente de licença comercial Android: [station-android-client-20260930](versions/station-android-client-20260930/). Login comercial desligado até URL, chave pública e rotas do servidor.

---

## Documentação histórica do estudo

# TurboRetroEmu — estudo do TurboramaStation

Análise estática do APK `TurboramaStation-24-09.apk`, realizada em 25/09/2026. O repositório reúne documentação, código Java decompilado, Smali, recursos selecionados e mapas de servidores, sistemas e nomes MAME. A publicação foi sanitizada para omitir BIOS, chaves, bibliotecas nativas e dumps que podem conter credenciais.

O aplicativo analisado é um frontend Android derivado do EmulationStation, com SDL2 e Libretro, pacote `org.emulationstation.frontend`. O APK original tem SHA-256 `9DC39817F23975F15E9FB75BBE98E7A7519567E06805F5746C1F475CBCF57396`.

## Comece aqui

- [Relatório técnico](docs/RELATORIO-TECNICO.md): arquitetura, licença, downloads, execução, telemetria e achados.
- [Handoff](docs/HANDOFF.md): arquivos entregues, uso e limitações de reprodução.
- [Escopo da publicação](docs/PUBLICACAO.md): exclusões e critérios da sanitização.
- [Frontend Java navegável](code/frontend/): nove arquivos da integração Android.
- [Manifesto Android decodificado](AndroidManifest-decodificado.xml).

## Código e dados

| Material | Conteúdo |
|---|---|
| [Java e recursos sanitizados](artifacts/codigo-java-recursos-sanitizado.zip) | Saída JADX, com 3.353 arquivos Java e recursos selecionados |
| [Smali e recursos sanitizados](artifacts/apktool-smali-recursos-sanitizado.zip) | Saída Apktool, com 6.198 arquivos Smali e recursos selecionados |
| [Símbolos nativos](artifacts/analise-nativa-simbolos.zip) | Símbolos dinâmicos desmangleados de `libmain.so`, sem binário, strings ou disassembly |
| [Servidores](data/servidores.csv) | Destinos encontrados, finalidade e condição de uso |
| [Sistemas e cores](data/sistemas-suportados.csv) | Plataformas, formatos e referências observadas ou inferidas |
| [Nomes MAME](data/nomes-mame.csv) | 38.353 pares `mamename`/`realname` da base auxiliar do APK |
| [Inventário original](data/inventario-arquivos.csv) | Nomes e tamanhos das entradas do APK original, inclusive arquivos omitidos |
| [Hashes originais](data/hashes-componentes.csv) | SHA-256 dos componentes originais para identificação |
| [Exclusões da publicação](data/exclusoes-publicacao.csv) | Registro dos arquivos que não foram publicados |
| [Checksums da publicação](CHECKSUMS.csv) | Integridade dos arquivos publicados |

Os 38.353 nomes MAME são uma base auxiliar de reconhecimento de nomes. A lista real da loja é fornecida por um servidor após validação de licença e não foi obtida nesta análise.

## Ler um catálogo local autorizado

O aplicativo mantém seu catálogo em `/storage/emulated/0/EmulationStation/.emulationstation/store/catalog-cache.json`. Com uma cópia desse cache, o script abaixo exporta os itens para CSV:

```powershell
.\scripts\Parse-Catalog.ps1 -CatalogPath 'C:\caminho\catalog-cache.json' -OutputPath '.\jogos-catalogo.csv'
```

O script lê apenas o arquivo local. Foi conferido com dados sintéticos, sem um catálogo real do serviço. O CSV gerado pode incluir URLs privadas ou assinadas e não faz parte desta publicação.

## Limites do material

Este é um estudo de engenharia reversa. O código C++ original do frontend não foi recuperado, e os pacotes sanitizados não permitem reconstruir integralmente o APK. O JADX deixou marcações de erro ou método não decompilado em 32 arquivos de bibliotecas de terceiros; nenhuma dessas marcações aparece no pacote Java do frontend.

Os resultados descrevem o arquivo identificado pelo hash acima e o estado observado em 25/09/2026. O material de terceiros conserva seus direitos e avisos existentes; este repositório não atribui uma nova licença ao código recuperado.

## TurboramaStation + TurboEden em um aplicativo

A pasta [`versions/turboeden-unico/`](versions/turboeden-unico/) documenta a versão 1.0.8 executada em aparelho e publica o tema editável. A navegação do tema é carrossel de sistemas, seguido pelos jogos do sistema selecionado. O APK de teste contém chaves e firmware privados, portanto não foi incluído no Git.
