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
| PS Vita | **Vita3K** | `:psvita` | Firmware oficial 3.74 aplicado na abertura a partir dos PUPs já no aparelho. Usuário **Jogador** criado. Preferência `vita3k_app` / `initial_setup_completed` grava o setup como concluído, então o Vita3K abre a biblioteca e não a tela Install Firmware. Correção RAR5. PUPs fora do Git e do APK. | TESTE 01/10 pronto na abertura |
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

**Vita3K** — [pronto na abertura](versions/vita-wiiu-pronto-20261001/README.md)  
`VitaEntryActivity.ensureReady()` aplica os PUPs oficiais 3.74 que já estão no aparelho, cria o usuário Jogador e marca `initial_setup_completed`. A tela Install Firmware do Vita3K deixa de aparecer. Firmware fora do Git. Correção RAR5 compartilhada com a linha Wii U.

**Beetle PCE preciso** — PC Engine CD; Fast permanece onde já era usado.

---

## TESTE 01/10/2026 — carrossel de sistemas

Código nativo em [`versions/carousel-led-overlay-20261001`](versions/carousel-led-overlay-20261001/README.md), commit `ebc4821`.

- LED colorido continua no aro das células (cabeça e cauda andando no perímetro).
- Overlay cinza transparente que passava na frente da arte das células do **carrossel principal de sistemas** foi removido.
- Paleta em dois tons: Naomi 2 e Model 2 vermelho+azul; PS Vita branco+azul; Nintendo DS branco+vermelho; N64 e N64 BR amarelo+branco.
- Botão ABRIR estático nesse carrossel.
- Cemu 0.5.2, ARMSX2, FBNeo e o APK estável `7ce3fab3` intactos.

Pacote TESTE: `org.turboramastation.frontend`. SHA-256 do APK local após Vita+Wii U: `f53fa49ad4a10f3c75b5fb5636138987f877282d21a29d6da81c6bc058ab6fe6`.

---

## TESTE 01/10/2026 — PS Vita e Wii U prontos

Código em [`versions/vita-wiiu-pronto-20261001`](versions/vita-wiiu-pronto-20261001/README.md).

- **PS Vita:** a abertura aplica o firmware oficial 3.74 que já está no aparelho, cria o usuário Jogador e grava `initial_setup_completed`. O Vita3K abre a biblioteca; a tela Install Firmware não aparece. PUPs só no storage do app.
- **Wii U:** `keys.txt` do dono na pasta `Cemu/` (e cópia em `EmulationStation/bios/wiiu/`). A abertura copia o arquivo se a pasta do Cemu estiver vazia. Chaves fora do Git e do APK.
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
