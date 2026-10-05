# TurboStations R17 — abrir diretamente subpastas únicas

## Estado

Pedido: “pasta com apenas uma sub pasta abre direto que tiver dentro”. Alteração nativa compilada e testada no PC. Integração/instalação serão feitas junto da correção de acesso do Neo Geo, no chat **Desmonte o APK de testes (2)**. Não afirmar já instalado: o telefone permanece com R16 até o recibo da próxima entrega.

## Comportamento

- Plataforma sem subcoleções abre diretamente seus jogos, sem a tela intermediária contendo apenas “Todos os jogos”. Plataforma vazia abre a lista vazia e permite voltar.
- Pasta com uma única subpasta, sem jogos diretamente nessa pasta, entra automaticamente nela. A regra acompanha sequências de subpastas únicas.
- Ao chegar a jogos, mostra a lista. Ao chegar a várias opções, mostra o carrossel de coleções normalmente.
- Se há jogos na pasta e também uma subpasta, mantém a escolha para não esconder os jogos da pasta principal. “Todos os jogos” continua reunindo o conteúdo inteiro quando há uma escolha real na raiz.
- Voltar usa o histórico de telas realmente exibidas, pulando as etapas ocultas. Restaura seleção por caminho e tipo da célula, não por índice; se aquela célula desapareceu do catálogo, usa a primeira opção existente.
- Não troca IDs, emuladores, caminhos de jogos, capas, vídeos, sinopses, filtros, download, autenticação ou acesso offline.

## Implementação

Único arquivo funcional alterado: `native_folders.h`.

`openFolderPath` consulta `StationCatalog_visitFolders` com a plataforma e o caminho assinados já publicados pelo módulo Station. Com zero filhos abre jogos; com um filho e zero jogos diretos segue o filho; nos demais casos mostra menu. Confere caminho descendente e limita a sequência a16iterações; metadados Java já limitam a profundidade a8 componentes. Sem clique simulado, coordenadas ou sobreposição Java.

`FolderBackEntry[16]` guarda somente cada menu real anterior, seleção original e kind da célula. `openSelectedFolder` empilha antes de entrar; `backFromFolder` restaura essa tela com `showFolderMenu`, ou volta às plataformas quando não há menu anterior. `resetFolderNavigation` limpa o histórico. Refresh de um menu visível preserva seleção e não navega espontaneamente para outra tela.

## Base exata e fontes

Base APK R16 instalado: SHA256 `b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1`.

Arquivo preservado em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Desempenho-Offline-R16-20261005.apk`. Cópia original em E removida somente após os dois hashes conferirem. Recibo `r16-archive.json`. Nenhum jogo, dado de telefone ou fonte removido.

Raiz desta alteração: `E:\ESTUDO APK\work\station-single-folder-r17-20261005`.

- `native/native_folders.h`: fonte nova.
- `before/native_folders.h`: fonte anterior R16.
- `native/native_carousel.cpp` e `native/native_search_download.h`: cópias exatas do overlay de desempenho R16, originalmente `C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\station-native-rate-phase-20261005\frontend-native`.
- Headers e objeto de mídia não alterados: `E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native`. Não reconstruir usando somente o cpp antigo dessa pasta, pois as mudanças de desempenho do R16 estão no overlay acima.
- JNI Java/Station permanece a R16 final, `station-download-performance-20261005/client/build-final`, salvo a correção separada de classes30 do Neo Geo na futura união.

Receita compilada completa em `tests.json`: NDK r28c, alvo aarch64-linux-android26, C++17/O2, biblioteca compartilhada sem runtime C++, alinhamento máximo16KiB. Três avisos de trigraph nas sinopses já existiam na base; nenhum erro de compilação.

Saída `libturbo_carousel.so` SHA256 **`4d2b962e09c7924e7b9b14042ee4b43e08d704bedae021131668303ae42fb39d`**. Só esta biblioteca deve substituir a entrada correspondente do R16 para aplicar a navegação. Não empacotar SO/JNI/DEX antigos por wildcard. No pacote conjunto, documentar também a alteração independente de classes30, conferir todas as entradas preservadas e usar a mesma assinatura sem desinstalar/limpar dados.

## Testes e conferência pendente

**3030 verificações C++ passaram**, executando o header nativo real com a ponte de coleções em memória. Cobrem catálogos planos/vazios, cadeias únicas UTF8, raiz com jogos próprios, ramificação no final da cadeia, linhas de jogos diretos, Todos os jogos, IDs/índices originais, volta sem laço, seleção após inserção/remoção e centenas de repetições de refresh/retorno. O mesmo teste rejeitou a implementação anterior. Compilação Android passou.

Ainda falta prova no APK conjunto no telefone: Nintendo64/NeoGeo sem subcoleções→jogos diretamente; voltar→plataforma selecionada. SNES com várias coleções→menu preservado; escolher coleção e voltar deve preservar seleção. Não marcar estável nem declarar gameplay com base nos testes de navegação.
