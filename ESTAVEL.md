# Estável Station — SNES e Mega Drive

[Handoff técnico completo](docs/server/HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md) · [Manifesto](versions/estavel-station-snes-megadrive-20261003/MANIFESTO-ESTAVEL.json) · [Recuperação](versions/estavel-station-snes-megadrive-20261003/RESTAURACAO.md)

Branch/tag `estavel-station-snes-megadrive-20261003`. APK `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`. Catálogo1816/revisão3; acesso, capas, download, instalação, abertura e retorno SNES/Mega conferidos. Demais motores preservados, sem homologação global. A próxima ampliação para40mil será separada desta tag.

## Referências anteriores preservadas — não são o cliente Station atual

# Estável atual — Cemu Android 0.5.2 (30/09/2026)

APK aprovado e instalado: `E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk`. SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. [Manifesto](versions/estavel-2026-09-30-cemu-052/MANIFESTO-ESTAVEL.json) · [Restauração](versions/estavel-2026-09-30-cemu-052/RESTAURACAO.md) · [Código e handoff](versions/wiiu-cemu-052-20260930/README.md).

Cemu 0.5.2 integrado no mesmo APK; Mario Kart 8 abriu e o mantenedor confirmou controles ativos e retorno às plataformas sem novo login. A preparação RAR5 foi corrigida. Jogos e saves foram preservados. O sistema comercial de licenças ainda aguarda a conexão com o servidor. Este teste cobre um jogo e um aparelho; o port Android do Cemu continua experimental.

## Histórico anterior
# TurboramaStation — estavel-2026-09-30-plataformas-emuladores

Referência atual aprovada pelo mantenedor em 30/09/2026: “AGORA QUE TUDO ESTÁ OK SUBA COMO VERSÃO ESTÁVEL PARA GIT”, seguida das atualizações expressas de vídeo PSP BR e Game Gear. A designação estável é do mantenedor; não certifica todos os jogos e aparelhos.

- APK instalado por atualização, sem desinstalar nem limpar dados: `78accf4c2e0c7b5c786acb0ea7a187754a53253beb2c51a01fc40f5a18c649f2`.
- Tamanho: 1055782222 bytes. Hash real do APK no telefone conferido após instalação.
- APK congelado: `E:\ESTUDO APK\estaveis\2026-09-30-plataformas-emuladores\TurboramaStation-ESTAVEL-plataformas-emuladores.apk`.
- Fontes ativos: `E:\ESTUDO APK\work\native-carousel\implementation`.
- Revisão principal: `E:\ESTUDO APK\work\native-carousel\implementation\platform-xbox-pce-refresh`; ajuste final de vídeos: `E:\ESTUDO APK\work\native-carousel\implementation\platform-xbox-pce-refresh\final-videos`.
- Snapshot público: `versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation`.
- Repositório: https://github.com/luziellacerda/TurboElden ; ramos de destino `estavel` e `versao-funcional`; tag nova `estavel-2026-09-30-plataformas-emuladores`. Consulte PUBLICACAO.json para confirmação do envio, que é uma etapa posterior à preparação deste documento.

**PS2 parado por ordem expressa.** Manter ARMSX2 2.7.2. A tentativa NetherSX2 foi cancelada e nunca instalada; não executar receitas de `ps2-replacement`. Esta revisão não promete corrigir o defeito gráfico de God of War.

[Alterações completas](versions/estavel-2026-09-30-plataformas-emuladores/ALTERACOES.md) · [Restauração](versions/estavel-2026-09-30-plataformas-emuladores/RESTAURACAO.md) · [Manifesto](versions/estavel-2026-09-30-plataformas-emuladores/MANIFESTO-ESTAVEL.json)

## Alterações consolidadas

### Catálogo, carrossel e mídias

- 43 plataformas observadas nos registros nativos da revisão a59a07af. Agrupamento por fabricante mantido. Catálogo final com 53 categorias/18.049 registros; categorias internas e plataformas visíveis têm contagens diferentes.
- PSP BR: categoria original `Psp - BR`, 59 jogos e 59 capas, pasta `pspbr`, acesso original ESPECIAL, mesma rota PPSSPP integrada. IDs, URLs e permissões dos jogos preservados.
- Vídeos próprios: SNES BR, MegaDrive BR, Xbox 360, Xbox clássico, Naomi, Naomi 2, PSP BR e Game Gear. PSP BR usa `PSPBR.mp4`; Game Gear usa o arquivo do mantenedor chamado `GEMEGEAR.mp4`.
- Vídeos 720×720, 30 fps, velocidade 1×, loop, sem áudio; somente a célula principal reproduz. Limite de quatro players preparados da revisão anterior mantido. A mudança final 78accf4c altera os dois vídeos e seu mapeamento no módulo nativo, sem alterar catálogo/DEX/motores.
- Naomi e Naomi 2 preparados para receber jogos, com células selecionáveis, vídeos, sinopse e rota Flycast. Categorias vazias de propósito, conforme pedido expresso do mantenedor; não foram inventados links. Usar chaves/pastas `naomi` e `naomi2` ao integrar os itens futuros no catálogo.
- Naomi 3 não adicionado: não foi identificado arquivo nem catálogo correspondente. Não confundir com Model 2. NES BR expressamente excluído.
- Jaguar: 56 jogos válidos. PC Engine CD: dois CHDs válidos. Foram retiradas da lista 68 entradas que eram imagens, vídeos ou metadados, sem apagar arquivos do aparelho.
- 58 capas específicas de Jaguar/PC Engine CD incluídas localmente: 34 imagens existentes no PC e 24 da biblioteca pública libretro-thumbnails, com nomes correspondentes e origem registrada localmente. Captura da revisão a59a07af mostra Jaguar com suas capas e 56 jogos.

### Xbox clássico

- X1 BOX oficial 1.2.8 incorporado ao mesmo APK: classes do aplicativo, recursos, menus, SDL3, libxemu e conversor XISO. Motor nativo recebido do APK oficial; ponte própria compilada.
- Processos separados `:xbox` (menus) e `:xboxemu` (emulação); aplicação principal não carrega outros motores nesses processos. Android mínimo efetivo do doador: 10/API29; a ponte apresenta mensagem em versões anteriores.
- Bibliotecas auxiliares e classes Android isoladas para evitar colisão com os motores já instalados. Tabela de controles própria `xboxcontrollerdb.txt`, preservando a tabela dos demais motores.
- 54 jogos Xbox do catálogo do mantenedor, chave/pasta `xbox`. O rótulo Xbox clássico nas configurações chama o menu oficial.
- Configuração inicial copia somente arquivos ausentes do conjunto local do mantenedor: MCPX, BIOS e disco QCOW2. Não baixadas BIOS de terceiros. Preferências e caminhos existentes são preservados.
- Entrada pelo botão Jogar leva o caminho local ao Launcher oficial. Retorno da opção correspondente é direcionado à TurboramaStation; menus/jogo/retorno Xbox clássico ainda não foram observados individualmente nesta publicação.

### PC Engine CD

- Nova rota usa Beetle PCE preciso (mednafen_pce), Android ARM64 oficial de 30/09/2026. A versão Fast continua disponível para os sistemas que já a utilizavam.
- Diagnóstico anterior encontrou ausência de syscard3 no diretório de BIOS e itens de mídia listados como jogos. A integração prepara syscard3 local somente se ausente e mantém os dois jogos CHD verdadeiros.
- BIOS veio de arquivo próprio do mantenedor; cabeçalho de copiador removido após conferir hash conhecido. Nenhum arquivo existente não vazio é sobrescrito.
- O núcleo preciso privilegia fidelidade; não há promessa de mais FPS. Abertura do Addams Family com esse núcleo ainda precisa de conferência específica. Compatibilidade de save states entre núcleos não foi presumida.

### Melhorias anteriores preservadas desde a última estável

- Dolphin 2609-7 e Flycast v2.7-44; ARMSX2 2.7.2 e PPSSPP 1.20.4; GameCube pela rota Dolphin; Wii U Cemu 0.5; Xbox 360 XenDroid; PS Vita Vita3K; Saturn YabaSanshiro Android 1.20.46.
- Saturn passou do core antigo para integração Android compilada do código oficial, com GLES/Oboe. Christmas NiGHTS exibiu imagem e retornou mantendo login. RetroAchievements e Vulkan não estão incluídos nessa integração.
- Wii U: correção de contador JNI depois de separar namespaces e preparação de RAR com cancelamento/progresso; PS Vita: firmware oficial preparado e correção de RAR5. Conferir os handoffs específicos para os limites e os jogos ainda pendentes.
- Nave e estrelas removidas a pedido do mantenedor; atualizações de menu, vídeos, pesquisa por plataforma, LED por sistema, redução de players e suspensão em segundo plano mantidas. Capas dos jogos continuam sem arredondamento.
- Opções de cada emulador continuam nos próprios menus; esta revisão não força presets de desempenho.

## Capas salvas no telefone

O código original já mantém as capas baixadas em `/sdcard/EmulationStation/.emulationstation/store/covers`. A conferência encontrou 1.765 arquivos, 245.819.565 bytes, inclusive arquivos de 25/09/2026 preservados após as atualizações.

`CatalogService::refreshInstalledState()` enumera essa pasta, associa o identificador `.img` à entrada e restaura o caminho local. `queueCoverDownloads()` ignora entradas com caminho local preenchido. Esse comportamento foi preservado; não foi necessário acrescentar outro downloader nem alterar o servidor. As 58 novas capas locais usam `files/turbo-game-covers` e `copyIfAbsent`, sem rede. A conferência foi estática e de arquivos; não foi realizada captura de todo o tráfego de rede.

## Conferências e limites

- Compilação, assinatura, alinhamento de bibliotecas, conflitos de classes, IDs de recursos e integridade das entradas preservadas conferidos no empacotamento.
- Revisão a59a07af instalada e hash do telefone igual; carrossel com 43 plataformas e Jaguar com capas observados.
- Revisão final 78accf4c instalada com sucesso, hash real igual. Última consulta encontrou aplicativo carregado e painel de notificações do Android em primeiro plano; não há captura visual específica dos dois vídeos finais.
- Aprovação geral do mantenedor registrada. Não declarar teste individual de todos os jogos, desempenho em todos os aparelhos ou resolução de PSX/God of War. Xbox clássico, PC Engine CD, Wii U, Xbox 360 e jogos completos de PS Vita mantêm pendências específicas de execução.
- Nenhum jogo/save foi apagado nesta revisão. Não houve mudança de PS2, publicação de BIOS/firmware/ROMs nem substituição de tags anteriores.
