# R21 — sinopses delimitadas e console somente nos jogos

## Pedido e entrega

O mantenedor pediu remover a foto adicional do hardware do carrossel principal e limitar as sinopses de todos os sistemas à área da tela, com barra de rolagem para textos longos. Esta revisão usa a camada nativa existente. A regra é compartilhada por plataformas, coleções e jogos; o nome do item e os botões permanecem fora da área rolável.

APK: `E:\ESTUDO APK\work\station-console-games-only-r21-20261005\TurboStations-Consoles-Sinopses-R21-20261005.apk`
SHA-256: `4c6bf41312be20e98ff15a6b7fbc2f85bb470bca1af39058ab362e39015543b4`
Tamanho: 2041527332 bytes. SO: `f802efdc262bd6a0818bfee5b833499179bd910cc2f5b93da0d644504168d3ba`.

Instalado como atualização em `org.turboramastation.frontend`; hash do base.apk conferido. Jogos, saves e sessão preservados. Conferência visual e limites constam de `evidence/visual-android.json`. Não promove estabilidade geral nem prova desempenho de emuladores.

## Fluxo no código

1. `native_info.h::updateSystemInfo` identifica modo, item mapeado, revisão e tamanho da tela. Sem mudança, não remede nem reconstrói o texto em cada quadro.
2. Plataformas usam `system_infos.h`; coleções usam `describeFolder`; jogos usam primeiro a descrição do catálogo e depois o índice local Station/legado. Os textos locais antes separados por form-feed agora têm quebras de linha. Não há paginação temporizada nem truncamento do texto dos jogos nos antigos buffers de 2/8 KiB.
3. `stationInfoLayout` define a área do texto. O hardware só reserva coluna à direita quando é lista de jogos, existe arte e há largura suficiente. Plataformas/coleções usam a largura livre inteira; retrato/arte ausente não reservam espaço.
4. `TextComponent` original recebe largura e altura zero, que ativa a altura automática real. A altura calculada em +0x58, multiplicada pela escala .82, determina se existe transbordamento. Se houver, mede outra vez reservando a barra.
5. `drawSystemInfoLayer` desloca o texto pelo offset e aplica `Renderer::pushClipRect/popClipRect` ao retângulo transformado. Só o texto é recortado. Barra e foto são desenhadas na camada nativa; console explicitamente recusado nas plataformas/coleções.
6. `touchHook` encaminha a `touchSynopsis` antes do carrossel nativo. Arrastar texto ou barra move somente a sinopse; tocar na trilha posiciona o indicador. Capas têm prioridade onde sobrepõem a descrição. Modais/filtro/mensagens de fechamento desativam novas capturas.
7. `station_synopsis_scroll.h` limita offset ao intervalo real, trata multitoque, resize e mudança de seleção. Gesto cancelado continua consumindo eventos daquele dedo até soltá-lo, evitando acionar botões por um UP sem DOWN. Novo item começa do início. Textos curtos não exibem barra nem capturam arrasto.

## Medidas e ABI auditadas

A base real `libmain.so` usada é a R19/R20, SHA-256 `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6`. Funções confirmadas por símbolos/desmontagem: pushClipRect 0x2e2800, popClipRect 0x2e2aac, setSize 0x2771d8, setPosition 0x277194, transformação Vector3f 0x2e1274 (retorno HFA s0/s1/s2). TextComponent render 0x2d2dc4 não recorta por conta própria; altura zero ativa auto-height. Não chamar calculateExtent como void: usa retorno std::string via x8.

Eventos recebidos: tipo int +0 (0 down/1 move/2 up), dedo uint64 +8 e coordenadas float +0x10/+0x14 em pixels. Roda de mouse não chega a este hook; nenhuma ação de roda foi inventada. Atalhos de controle existentes foram preservados.

## Testes e preservação

- 15.375 verificações C++ de layout: principal/coleções sem foto e sem coluna vazia; retângulos dos jogos preservados. O teste de requisito falha na R20 anterior.
- 140 verificações C++ de rolagem: início/fim, indicador, arrasto, texto curto, dimensões inválidas, multitoque, mudança de item/tamanho, cancelamento por modal e reutilização do ID.
- Compilação Android arm64/API26 concluída. Três avisos herdados de trigraph nas sinopses; nenhum erro.
- Certificado original e alinhamento 16 KiB conferidos.
- Comparação completa do APK: somente `lib/arm64-v8a/libturbo_carousel.so` mudou; 13080 entradas preservadas. DEX, motores, autenticação, transferência, assets e resources.arsc N64 são iguais à R20. Nenhuma alteração no servidor.
- Controles/menu N64 R19B, acesso Neo Geo R18, retorno de pastas R17, offline/download R16 e LEDs R20 preservados por bytes dos insumos. Isso não equivale a retestar todos os motores no telefone.

## Reconstrução e pastas exatas

Trabalho e temporários: `E:\ESTUDO APK\work\station-console-games-only-r21-20261005`. Overlay completo local em `native/`. Este snapshot publica os headers/C++/GLSL, exceto `console_assets.h` gerado (19 MB), cujo hash está no recibo. Gerar esse header a partir dos sete PNGs e receita de `../station-console-led-r20-20261005/`, que foram preservados.

Includes/objeto restantes: `E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native`: `video720_posters.o`, `libc.so`, `libdl.so`, `liblog.so` e headers herdados. Nunca usar o antigo SO de saída como se fosse a versão corrente. Fontes congeladas R20: `E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005\native`.

Base APK R20 arquivada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Consoles-LED-R20-20261005.apk`, SHA `64eae3ab4dd253e25ee826dd23bf02c947e5cbd1db70e6b07f759d988d465904`. SO R20 também arquivado em G; `evidence/r20-archives.json` prova cópia/hash/tamanho antes de remover duplicatas E. As fontes não foram apagadas.

Para refazer no mesmo workspace, restaurar este snapshot nas subpastas correspondentes de W21 e console_assets.h idêntico, usar `recipes/compile_synopsis_r21.py` e depois `package_console_games_r21.py`. A receita usa o comando integral em `evidence/native-build.json`, recompila ambos testes host e confere fontes preservadas versus R20. Ela não sobrescreve um APK já existente. Assinar com o certificado original; a chave não é publicada.

Instalar com `install_synopsis_r21.py` somente com ESActivity e sem processos de emulação. Atualização `-r --no-incremental --user 0`, sem desinstalar/limpar dados; conferir hash no aparelho e iniciar pelo launcher público. Nenhuma correção depende de preferência manual aplicada só no telefone.

## Próxima revisão coordenada

W22 de vídeos das coleções Neo Geo deve partir deste APK e copiar integralmente o overlay R21. Não empacotar sobre R20 nem perder a rolagem e a restrição dos consoles. O motor Neo Geo CD recebido separadamente continua fora deste delta. Não incluir mudanças paralelas sem revisão dos respectivos inputs.

Capturas e registros completos ficam localmente em `device-evidence/`; não publicar dados pessoais, catálogo privado, APK, ROM ou BIOS. O Git contém fontes, receitas e recibos sanitizados.

## Conferência final no Android

Em 05/10/2026, R21 foi conferida no Samsung SM-A566E. SNES e N64 no principal e coleções Neo Geo não exibiram hardware extra. No jogo 007, sinopse de 882 bytes/797px em viewport de 406,1px exibiu barra; arrasto do texto moveu a descrição, arrasto do indicador voltou ao início, toque no fim da trilha exibiu a última linha. Texto permaneceu recortado acima do título e dos botões, e a foto N64 ficou à direita. VOLTAR restaurou N64 no principal sem login. Capturas locais referenciadas por hash no recibo; nenhum jogo foi iniciado ou dado apagado nesta conferência. A regra é comum a todos os sistemas, mas não se afirma teste manual de cada plataforma individual.
