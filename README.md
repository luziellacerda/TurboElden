# Estável atual — Cemu Android 0.5.2 (30/09/2026)

APK aprovado e instalado: `E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk`. SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. [Manifesto](versions/estavel-2026-09-30-cemu-052/MANIFESTO-ESTAVEL.json) · [Restauração](versions/estavel-2026-09-30-cemu-052/RESTAURACAO.md) · [Código e handoff](versions/wiiu-cemu-052-20260930/README.md).

Cemu 0.5.2 integrado no mesmo APK; Mario Kart 8 abriu e o mantenedor confirmou controles ativos e retorno às plataformas sem novo login. A preparação RAR5 foi corrigida. Jogos e saves foram preservados. O sistema comercial de licenças ainda aguarda a conexão com o servidor. Este teste cobre um jogo e um aparelho; o port Android do Cemu continua experimental.

## Histórico anterior
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

# Versão estável atual — TurboramaStation

**Comece por [ESTAVEL.md](ESTAVEL.md): APK exato, pastas, hashes e restauração.**

Ramos `estavel` e `versao-funcional`; tag `estavel-2026-09-30-dolphin-flycast`. Dolphin e Flycast atualizados dentro do APK; design preservado, retorno corrigido e login mantido. [Alterações completas](versions/estavel-2026-09-30-dolphin-flycast/ALTERACOES.md) · [Fontes congelados](versions/estavel-2026-09-30-dolphin-flycast/). APK e ativos privados permanecem locais.

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

Os 38.353 nomes MAME são uma base auxiliar de reconhecimento de nomes. Não representam jogos disponíveis no catálogo comercial, ROMs incluídas ou compatibilidade testada. A lista real da loja é fornecida por um servidor após validação de licença e não foi obtida nesta análise.

## Ler um catálogo local autorizado

O aplicativo mantém seu catálogo em `/storage/emulated/0/EmulationStation/.emulationstation/store/catalog-cache.json`. Com uma cópia desse cache, o script abaixo exporta os itens para CSV:

```powershell
.\scripts\Parse-Catalog.ps1 -CatalogPath 'C:\caminho\catalog-cache.json' -OutputPath '.\jogos-catalogo.csv'
```

O script lê apenas o arquivo local. Foi conferido com dados sintéticos, sem um catálogo real do serviço. O CSV gerado pode incluir URLs privadas ou assinadas e não faz parte desta publicação.

## Limites do material

Este é um estudo de engenharia reversa, não um projeto Android compilável. O código C++ original não foi recuperado, e os pacotes sanitizados não permitem reconstruir integralmente o APK. O JADX deixou marcações de erro ou método não decompilado em 32 arquivos de bibliotecas de terceiros; nenhuma dessas marcações aparece no pacote Java do frontend. Os jogos e os serviços autenticados não foram executados/testados.

Os resultados descrevem o arquivo identificado pelo hash acima e o estado observado em 25/09/2026. O material de terceiros conserva seus direitos e avisos existentes; este repositório não atribui uma nova licença ao código recuperado.

## TurboramaStation + TurboEden em um aplicativo

A pasta [`versions/turboeden-unico/`](versions/turboeden-unico/) documenta a versão 1.0.8 executada em aparelho e publica o tema editável. A navegação do tema é carrossel de sistemas, seguido pelos jogos do sistema selecionado. O APK de teste contém chaves e firmware privados, portanto não foi incluído no Git.
