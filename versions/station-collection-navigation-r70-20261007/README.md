# R70 — entrada das coleções, configurações no rodapé e vídeos

Sucessora da R69 instalada e salva na tag `estavel-menu30fps-colecoes-r69-20261007`, commit `17cd4718740e79c62e0522a1b0d3c363d7177068`. R69 permanece recuperável. Esta entrega reúne os pedidos posteriores e não substitui aquela tag.

## Correção: coleção abre no último jogo

A entrada já zerava a seleção. O problema reproduzido ocorria no rebuild seguinte: o código original reencontrava o jogo na lista completa da plataforma, depois o filtro da coleção encurtava a lista sem recalcular a posição. Uma posição fora do novo limite era reduzida ao último item.

Exemplo comprovado pelo teste: coleção `[2,4]`, selecionado primeiro jogo; rebuild amplia para `[0,1,2,4]` e reposiciona o mesmo jogo no índice 2; o filtro antigo volta a `[2,4]` mas transforma o cursor 2 em 1, selecionando o último jogo.

`native_folders.h::filterFolderGames` e `native_search_state.h::stationSearchScope` agora preservam o índice original do item e calculam sua nova posição durante a filtragem. Se o item selecionado sumiu, selecionam o primeiro. Cursor/animação só são realinhados quando necessário. Entrada nova continua no primeiro jogo; navegação normal mantém a seleção escolhida. Voltar continua restaurando a coleção pelo caminho/kind. Não há reset contínuo do cursor nem alteração do identificador de restauração nativo em `0x630`.

`evidence/navigation-diagnosis.json` documenta os offsets e trechos binários comparados com o APK R69. O mesmo teste falha na R69 e passa na R70 com 3.584 verificações. Isso é prova local do defeito reproduzido; a observação Android é registrada separadamente.

## Configurações no rodapé das coleções

O robô Lottie usa o mesmo controle e ação de configurações. Só quando `systemsMode && folderMode` seu retângulo vai ao canto inferior direito, alinhado verticalmente a ABRIR/VOLTAR. `native_skin.h` e `native_profile_name.h` usam o mesmo helper, impedindo que o nome carregado reposicione o botão no topo. Desenho e toque originais usam `+0x1410`; não foi criada outra sobreposição.

Tamanho, animação, pausas, avatar e nome permanecem. Plataformas principais e listas individuais de jogos conservam a posição anterior. Teste constexpr cobre 60 combinações de resolução, comprimento de nome e flags.

## Novos vídeos

Super Mario (`SUPER MARIO COLEÇÃO.mp4`) substitui o vídeo anterior; Top Gear (`top gear coleção.mp4`) foi atualizado novamente após a R69. Ambos vêm da pasta `Sele;'ao` indicada pelo mantenedor, com hashes em `mapping.json`. Mario corresponde a `## SUPER MARIO ##`, Top Gear a `## TOP GEAR ##` no snapshot do catálogo registrado. Os outros dez arquivos dessa pasta mantêm seus hashes.

Saída 720 × 720, 30 fps, H.264 baseline, sem áudio, em loop e velocidade original, sem corte nem distorção. Conversão de 24/25 fps para 30 não acelera o vídeo. Cada poster vem do primeiro frame do vídeo empacotado. Continuam 57 vídeos totais e somente um decoder ativo.

## Escopo do limite de 30 fps

O limitador está em `GuiStore::render`, através de `paceStoreMenu`. Ele regula o catálogo/carrossel, não o loop dos emuladores. Motores, configurações e taxas dos jogos não foram alterados. Diálogo de menu parado mantém 15 fps; menu até 30 fps. Não foi medida redução térmica percentual.

## Build, reprodução e preservação

Base APK R69 SHA-256 `901e5eb495a858fc6877f7a22e325b5fcb3b73807af8c6d2888c90f1425773e4`. Overlay: cinco headers alterados, um helper novo; `collection_video_policy.h` está copiado mas idêntico à R69. Receita valida todos os hashes da árvore base e mantém os objetos anteriores, acrescentando apenas os posters R70.

Build final: `E:\ESTUDO APK\work\station-collection-navigation-r70-20261007-final2`. A pasta sem `2` contém tentativa interrompida pelo teste de funções herdadas não usadas; não produziu APK. O teste final conserva avisos como erros exceto `unused-function` para os helpers herdados que esse teste isolado não chama.

APK final: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R70-20261007.apk`.

Executar `recipes/build_r70.py` com destino E: novo. Com a assinatura original configurada privadamente nas variáveis STATION_KEYSTORE, STATION_KEY_ALIAS, STATION_KS_PASS e STATION_KEY_PASS, executar `recipes/package_r70.py`. O pacote altera somente `libturbo_carousel.so` e os vídeos Mario/Top Gear; preserva todas as outras entradas, DEX, motores, controles, faixa INSTALADO, política de cantos R69, licenças e saves. Recibos contêm hashes e comparação integral.

`recipes/install_verified.py --workspace <build>` exige R69 exata, um telefone autorizado e nenhuma Activity de emulação ativa. Instala com `-r`, confere hash integral/UID/data original, sem desinstalar nem limpar dados. Nenhuma implantação Linux ou mudança de contrato online; retomada de partida segue o pedido REC-01 a REC-09 da R67.

Fontes, testes e recibos podem ser publicados; APK, mídias privadas, objetos, segredos e capturas pessoais ficam fora do Git. Consulte STATUS e recibo de instalação para distinguir compilação, instalação e conferência física.

## Estado da entrega

APK R70 SHA-256 `c12ee4e2928a629be4a2cc6dc9201fc7c5722e21a1fa8385d21da7a7dc69a32e`, 2.118.780.321 bytes. Assinatura e alinhamento conferidos, 13.221 outras entradas preservadas. Todos os testes locais passaram. Instalação não iniciou: nenhum aparelho apareceu na USB na conferência anterior ao envio. R69 continua a última versão comprovadamente instalada no A56. Aguardando reconexão; sem conferência visual R70 no aparelho.
