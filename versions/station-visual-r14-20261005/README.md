# R14 — célula original, vídeo inteiro e botões por função

## Pedido e resultado implementado

Pedido de 05/10/2026: manter o tamanho original das células, preencher com vídeo sem cortar ou esticar a imagem e redesenhar os botões inferiores com ícones, cores por função e efeito dentro da borda. Esta revisão substitui a geometria larga da R13. Não muda catálogo, subpastas, IDs, seleção de jogos, downloads, licença, emuladores, salas ou contratos de servidor.

- `coverSlot` voltou à geometria original: plataformas e coleções quadradas; capas dos jogos continuam no formato anterior. Não há faixa preta nem texto novo sobre células. Textos que já estão gravados nos vídeos fornecidos continuam na imagem.
- Bomberman, Donkey Kong, Top Gear e PT-BR: imagem principal inteira em 720×405, centralizada em um quadro 720×720, sem crop ou deformação. O espaço superior/inferior usa cópia desfocada da própria imagem, preparada no PC. Não há segundo vídeo nem desfoque em tempo real no telefone. Mario já é quadrado e seus bytes R13 foram preservados.
- MP4 H.264 baseline, 30 fps, velocidade normal, sem áudio e em loop. Mantidos um player ativo na célula selecionada, cache limitado de prévias, players aquecidos e pausas ao abrir jogo/configurações ou esconder o app. Nenhuma espera de navegação foi adicionada.
- Botões nativos com ícones vetoriais, texto separado do ícone e cores: Jogar/Abrir verde; Jogar online ciano; Salvar azul; Apagar coral; Atualizar âmbar; Voltar cinza azulado; Baixar azul claro. O ícone principal muda conforme o estado instalado já fornecido pelo catálogo. O contorno animado está inteiramente dentro do retângulo do botão; não há halo exterior.
- Ícones/contornos usam o renderer nativo e o relógio do frame visível. Não foram criados timers, threads, texturas, decodificadores ou overlays para os botões. Controles desabilitados continuam distintos; confirmação de apagar mantém a condição nativa.

## Mídia e seleção

Originais privados intactos em `C:\Users\Admin\Videos\New folder`. Resolução por `collectionVideoFor`, somente SNES/SNES BR, nome da folha com espaços/# externos ignorados. `Todos os jogos` resolve o mesmo vídeo da plataforma; outras coleções sem clip próprio usam vídeo dessa plataforma. Final Fight/Mega Man não têm clip próprio entre os cinco fornecidos. IDs, nomes e jogos vêm do catálogo assinado, não desse mapa visual.

`collection_video_policy.h` conserva `aspect` como metadado de origem; a geometria não usa mais esse campo. Removido `folderVideoAspect`. Todos os MP4 derivados são quadros quadrados prontos para a textura 720×720 existente. Vídeos privados não são enviados ao Git: manifestos contêm caminhos, filtros e SHA256. Não confundir a cópia privada local ignorada pelo Git com arquivo publicado.

## Pastas e arquivos exatos

- Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004\native`.
- Build, backup antes da mudança, mídia, testes e recibos R14: `E:\ESTUDO APK\work\station-netplay-20261004\visual-r14`.
- APK: `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Visual-R14-20261005.apk`.
- SHA256 APK: `a1566d3d34305e01f5f445b6b61fb3db4e35fc8a4bc8a2f3e493fb3a433a38bf`, 2.006.925.798 bytes.
- Base R13 arquivada com SHA conferido: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Colecoes-Videos-R13-20261005.apk`, SHA256 `1dd21157ce0a0fcf5836bb3827e1eed90637eaac8fa09559f3dc0eb15ccf5a60`.
- R12 anterior: mesma pasta G:, `TurboStations-Netplay-Internet-R12-20261005.apk`, SHA256 `7684c6eee87985d8259becca9a22a9f4c7e3203f7c097df37da6998975596514`.

Código R14: `native_formation.h` (células quadradas), `native_folders.h` (retira somente helper de aspecto), `native_game_actions.h` (paleta, ícones e contorno), `native_action_motion.h` (Abrir usa o renderer compartilhado), `native_skin.h` (reserva espaço para ícones e estado instalado), `native_netplay.h` (reserva espaço no texto Online; despacho/toque intactos). `video720_posters.o` canônico foi regenerado com os quadros iniciais novos; `video720_posters.h` e suas 49 entradas não mudaram desde R13.

## Construção segura e reprodução

Os scripts de preparação são de aplicação única e fazem backup. Não executá-los de novo sobre a árvore já alterada.

1. `prepare_visual_r14.py`: parte das fontes R13, remove a proporção variável, confere hash de cada original, converte quatro clips, conserva Mario e extrai primeiro frame RGB565 bottom-up de cada um.
2. O objeto legado de **44** prévias está em `collection-video-r13/before/video720_posters.o`. O script o combina com os cinco novos símbolos `station_collection_video_0..4` por `ld.lld -r`. **Não combinar com o objeto R13 já contendo os cinco símbolos**, para evitar duplicação. O arquivo canônico consolidado passa a ter 49 prévias.
3. Copiar `native_game_actions_r14.h` para o `native_game_actions.h` canônico e executar `apply_action_visual_r14.py` sobre o restante R13. Os snapshots `native/` deste pacote já refletem a versão final; não reaplicar patches neles.
4. `test_build_visual_r14.py` é reexecutável: testes reais no host, prova de conteúdo visual integral, decodificação completa dos cinco vídeos e link Android arm64/API26 com o objeto consolidado real. Necessita clang/LLD e sysroot NDK r28c, Python com Pillow/imageio-ffmpeg. Não usa imagens sintéticas no APK.
5. `package_visual_r14.py`: parte do APK R13 de hash exato; arquiva/verifica antes de retirar duplicata em E:, troca quatro MP4s e um SO, mantém compressão e todas as outras entradas, alinha 16KiB, assina com o certificado original e compara SHA256 de cada entrada. Recusa sobrescrever APK de saída existente.

O Git é fonte/manifesto; não contém APK, chaves de assinatura, objetos privados nem mídias. A árvore nativa completa e as dependências anteriores estão na pasta canônica; snapshots anteriores do ramo documentam sua composição. Não aplicar builders históricos contra o APK novo como se fossem incrementais.

## Conferências realizadas no PC

- 4.096 combinações de geometria/ícones/cores/estados/tempo: todos os vértices dentro dos botões, inclusive o contorno animado.
- 1.836 posições/tamanhos do carrossel: células de plataforma/coleção quadradas.
- 443 verificações reais de navegação: IDs/índices preservados, Todos os jogos, pastas diretas/aninhadas, Voltar, catálogos planos/vazios e 200 atualizações.
- Chamadas e gesto de Online byte a byte iguais em seus métodos; retângulos de toque nativos preservados.
- Decodificação completa dos cinco MP4s passou. Comparação do quadro principal com a fonte redimensionada integralmente comprovou 720×405, posição y=157, razão16:9. Erro médio absoluto RGB após compressão entre3,33 e5,77/255; sem crop no primeiro quadro. Filtro aplicado a todos os quadros conserva essa geometria.
- Biblioteca arm64 compilada. Apenas três avisos antigos de trigraph em sinopses, sem erro. APK assinado com certificado `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` e alinhado16KiB.
- Cinco entradas alteradas, **11.106 preservadas**, nenhuma adicionada/removida. Todos os DEX e motores iguais à R13. `classes35.dex` das salas/internet: `8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae`.

Estado de instalação, observação visual e limites Android: consultar `evidence/device-result.json` quando presente. `build-result.json` registra o momento da compilação; não deve ser usado sozinho para deduzir instalação posterior. Não promover a estável sem aprovação.

## Servidor e trabalho paralelo

Nenhuma alteração/deploy de servidor é necessária para esta correção visual. Preserva R12 WSS/netplay; operador ainda precisa publicar a entrega `feat/station-netplay-internet-r12-20261005`, commit `d358e5f4d127a607bdf0c1ce3e4f4c2b4eaa7504`, e a partida entre dois aparelhos/redes segue sem prova nesta revisão. A entrega paralela NeoGeo/taxa `c8e240a` permanece no Git e não foi aplicada por este delta. Não substituir classes35 nem native carousel pelas versões anteriores ao R14.
