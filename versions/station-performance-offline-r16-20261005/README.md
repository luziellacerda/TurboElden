# TurboStations R16 — desempenho e acesso offline

Handoff técnico de 05/10/2026. Este conjunto reúne a remoção do SHA de conteúdo no fluxo de jogos, ajustes de escrita e medição do download, e acesso local com catálogo assinado já autorizado. O build Java combinado está congelado; instruções de reconstrução e hashes estão em [BUILD.md](BUILD.md).

## Estado desta entrega

O APK foi compilado, assinado e instalado por atualização no Samsung SM-A566E, com SHA do base.apk igual ao arquivo entregue. Classic Kong foi baixado e apareceu como instalado. O boot local foi conferido após encerrar o processo: Wi-Fi e dados móveis desligados, nenhuma rede padrão, catálogo salvo de 2.162 itens e nenhuma requisição HTTP. As conexões originais foram restauradas. `build-result.json` registra `installed: true` e `stable: false`. Gameplay e capas de jogos durante a sessão offline dedicada não foram testados; não declarar estabilidade geral.

| Item | Resultado registrado |
| --- | --- |
| APK | `TurboStations-Desempenho-Offline-R16-20261005.apk` |
| Tamanho | 2.036.268.564 bytes |
| SHA-256 | `b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1` |
| Base | R15 arquivado, SHA-256 `d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b` |
| Conteúdo preservado | 13.078 entradas; somente três entradas de conteúdo alteradas |
| Alterações no APK | `classes28.dex`, `lib/arm64-v8a/libstation_frontend.so`, `lib/arm64-v8a/libturbo_carousel.so` |
| Java | 787 verificações em 16 suítes; compilação API 34 / Java 8 |
| C++ | 32 verificações de taxa, fase e associação exata do trabalho |
| Assinatura e alinhamento | Certificado original conferido; bibliotecas alinhadas a 16 KiB |
| Dispositivo | Instalação confirmada pelo coordenador; Classic Kong recebido e exibido como instalado |
| Validação offline no dispositivo | Biblioteca retomada sem rede; catálogo em cache de 2.162 itens e zero HTTP; conexões restauradas |

Os hashes de build, APK e assinatura continuam sendo calculados para rastrear a entrega. A remoção de hash de conteúdo descrita abaixo é uma decisão do fluxo de jogos em execução.

## Pastas de referência

Neste documento, `W` significa `E:\ESTUDO APK\work\station-download-performance-20261005` e `C` significa `C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work`.

| Conteúdo | Local |
| --- | --- |
| APK e prova de empacotamento | `W\TurboStations-Desempenho-Offline-R16-20261005.apk`, `W\build-result.json` |
| Cliente Java final combinado | `W\client\src`, `W\client\tests` |
| DEX, fontes arquivadas e resultados finais | `W\client\build-final` |
| Bibliotecas e prova nativa | `W\native-build` |
| Entradas e recursos do carousel | `W\frontend-native` |
| Fontes alteradas, testes e comandos nativos | `C\work\station-native-rate-phase-20261005` |
| Benchmark local Android | `W\bench\nohash\android-shared-summary-20261005.json` e CSV correspondente |
| Handoff original do acesso offline | `E:\ESTUDO APK\work\station-offline-access-20261005\HANDOFF-OFFLINE-STATION-20261005.md` |

## Download e instalação

### Trabalho removido e caminho atual

- `StationFiles.replaceArtifact` recebe os jogos sem calcular SHA-256 do corpo. Usa leitura de 64 KiB e `BufferedOutputStream` de 256 KiB; faz `flush` antes de `FileDescriptor.sync` e publica por substituição atômica no mesmo diretório.
- `StationInstaller` não relê o pacote para fazer hash antes da instalação. RAW é copiado uma vez para a geração de instalação; ZIP/RAR/7z seguem para o extrator com as validações de formato e limites existentes.
- O pedido de download segue autorização, validação de tamanho, preparação do staging e abertura do GET. A busca de arquivos legados, seu hash e a reautorização ligada à busca de cinco segundos foram retirados. `StationExistingArtifact.find` não percorre o armazenamento e retorna `null`.
- Jogos já instalados continuam sendo identificados pelo recibo privado. Um arquivo arbitrário encontrado por nome e tamanho não é adotado como se fosse o artefato autorizado.
- `StationInstaller.find` valida o recibo, geração e caminho de entrada; confere existência, caminho seguro e tamanho do arquivo de entrada quando disponível. A lista do manifesto é consultada em memória. O método não percorre todos os arquivos acompanhantes no disco a cada publicação da coleção ou retorno do jogo.

O download mantém um trabalhador e a fila existente. A sessão é protegida durante a autorização e a abertura do GET; o corpo é consumido depois da liberação dessa proteção. Não foi acrescentado paralelismo de partes, limitador de bytes ou espera para regular a taxa.

### Validações preservadas e limites aceitos

Continuam as validações de manifesto e descritor assinados, tamanho recebido, limites de extração, assinatura de formato, caminhos, symlinks, arquivos esperados, referências CUE/M3U na instalação, espaço, cancelamento e transação. Falha ou cancelamento preservam a instalação anterior e limpam o parcial. A remoção continua limitada aos arquivos pertencentes à instalação; arquivos desconhecidos, como saves, não viram alvos por estarem na mesma pasta.

**Conteúdo modificado sem mudar o tamanho não é detectado pelo SHA no download, na instalação nem na abertura local.** Um pacote RAW com bytes diferentes e tamanho válido pode ser aceito. Os extratores ainda podem rejeitar conteúdo inválido pelas próprias regras de formato. A ausência ou alteração de um arquivo acompanhante não provoca uma varredura ao abrir a coleção; pode aparecer somente quando o emulador precisar dele. Um arquivo de entrada ausente ou com tamanho incompatível continua invalidando a abertura pelo recibo.

`StationFiles.Receipt.sha256` fica vazio no caminho de jogos, significando **não calculado**. A auditoria não encontrou consumidor de execução que exija esse campo preenchido nesse caminho. O `sha256` do descritor autorizado é mantido como metadado esperado do servidor; ele não comprova que os bytes locais foram conferidos no R16. O `replace` genérico continua calculando digest para seus demais usos de metadados/cache.

TLS, confiança do certificado, assinaturas do protocolo e identificação de proprietário/dispositivo continuam presentes. O SHA usado pelo netplay para identidade de ROM/core e compatibilidade de sala também continua. O DEX de salas foi preservado exatamente; isso não constitui uma nova declaração de estabilidade do netplay.

### Conexão e vida útil do corpo HTTP

O transporte conserva os timeouts de conexão de 10 segundos e leitura de 30 segundos. Usa corpo com codificação `identity`. Uma resposta só é considerada concluída e reutilizável após EOF e comprimento exato. Fechamento parcial ou cancelamento desconectam a resposta; `ArtifactTransfer.close` é idempotente. Dessa forma, um corpo incompleto não volta ao pool como conexão pronta. Não há `sleep` novo no caminho de transferência.

## Fases, progresso e diagnóstico

Ao terminar o corpo de rede, a interface passa de `Baixando` para `Preparando` antes da instalação. Os contadores globais e a ABI são preservados: o total inclui artefato mais conteúdo instalado. Assim, um RAW pode terminar de receber a rede em 50% do trabalho global. Esse percentual não é a porcentagem exclusiva da rede.

O código nativo calcula MB/s usando bytes recebidos somente em `Baixando`, relógio monotônico e janela mínima de 500 ms. A taxa é a média desde o primeiro evento dessa fase e reinicia em tentativa nova, total novo ou regressão do relógio. Preparação e extração não entram na taxa. O renderer associa o progresso ao trabalho exato, mostra `AGUARDANDO`, `BAIXANDO`, `PREPARANDO` ou `PROCESSANDO`, e só exibe taxa durante download. MB é decimal; o benchmark abaixo usa MiB. A estrutura `Progress` mantém 48 bytes.

As métricas são emitidas uma vez ao concluir cada fase com sucesso. `status=0`, `count` contém o valor da fase; não há log por bloco, credenciais ou caminhos. A implementação usa relógio monotônico.

| Evento final | Unidade e abrangência |
| --- | --- |
| `AUTHORIZE_ELAPSED_MS` | ms, de antes de `acquireItem` até o retorno de `owner.authorize`; inclui obtenção/renovação de sessão e reconciliação exigida pelo fluxo |
| `ARTIFACT_HEADERS_ELAPSED_MS` | ms, ao redor de `api.openArtifact`; cobre abertura da conexão e recebimento/validação dos cabeçalhos |
| `DOWNLOAD_ELAPSED_MS` | ms, cópia para staging e fechamento da resposta; inclui escrita, flush, fsync e publicação do staging, exclui autorização e cabeçalhos |
| `DOWNLOAD_BYTES` | bytes recebidos na fase concluída |
| `INSTALL_ELAPSED_MS` | ms, instalação completa: cópia/extração, recibo e publicação |

Não existe `VERIFY_ELAPSED_MS` no enum final. Uma fase que falha não emite sua duração de conclusão; usar também os eventos existentes de erro. Somar as quatro durações ajuda a localizar demora antes do primeiro byte, escrita e instalação, mas não inclui necessariamente fila, atualização visual ou todo o tempo percebido pelo usuário. Os logs Android usam o observador `StationService`.

### Cuidado ao interpretar o status de publicação do catálogo

No R16, `StationFrontend` registra `CATALOG_PUBLISHED` com a expressão herdada `library.cached ? 503 : 200`. Na observação de boot com cache informada pelo coordenador, houve `CATALOG_CACHE status=0` e `CATALOG_PUBLISHED status=503 count=2162`. Esse 503 identifica localmente uma biblioteca vinda do cache: **não comprova resposta HTTP 503 do servidor**. Para diagnosticar uma falha remota, consultar o trace HTTP separado. A semântica desse evento não foi alterada no APK já instalado. A observação inicial de cache foi complementada pelo teste dedicado sem rede, registrado em `evidence/offline-device.json`.

## Acesso offline

O acesso local usa o catálogo assinado já obtido para a instalação e o proprietário atuais. O login consulta a licença salva e o catálogo local **antes do HTTP**. `StationApi.restoreLocalCatalog` valida RSA-PSS, autoridade/key ID, domínio do catálogo, esquema/produto/aplicação, proprietário e identidade do dispositivo no Keystore. A restauração não cria bearer ou grant novo nem persiste token de acesso.

Com catálogo válido e sem bloqueio persistido, a coleção local abre sem depender do bearer curto, do relógio ou de nova consulta ao servidor. Nome local e capas em cache são reaproveitados para o mesmo proprietário. Não há limite novo de dias offline. Primeira ativação, cache inválido ou chave de dispositivo diferente ainda exigem rede; apenas conhecer uma licença não autoriza a restauração.

A consulta de capa tenta o cache antes de obter sessão. Novas capas, downloads, salas e presença continuam dependendo de rede. A disponibilidade de rede é consultada pelo transporte Android; a permissão necessária já estava no manifesto da base R15. Wi-Fi sem internet ou servidor sem resposta não passam a bloquear o boot de uma coleção local válida.

O ajuste complementar da atualização automática executa HTTP no trabalhador de polling e envia apenas a publicação ao executor `commands`. Um perfil remoto demorado não ocupa esse executor e não bloqueia a resolução de um jogo local. Cancelamento e verificação de geração continuam impedindo publicação de resposta antiga.

Falhas de transporte/503 mantêm a biblioteca local. Um 401 invalida a sessão de rede, sem apagar automaticamente a autorização local anterior. Uma negativa explícita 403 `STATION_LICENSE_DENIED` ou `STATION_DEVICE_DENIED`, recebida pelos fluxos tratados pelo coordenador, bloqueia o proprietário e persiste `owner.blocked`. Se gravar o bloqueio falhar, o cache do proprietário é removido para evitar liberação indevida. Nova autenticação com catálogo autorizado pode limpar o bloqueio; negativa de sessão antiga não substitui uma sessão nova.

O catálogo assinado prova uma autorização anterior. Um aparelho desconectado não recebe revogação nova do servidor. O comportamento offline é política local solicitada para esta entrega; não representa implantação de um novo certificado offline no backend.

## Evidência de desempenho

### Download real após instalação do R16

O coordenador informou um download concluído de **Classic Kong, 262.144 bytes**, com as métricas abaixo. A interface mostrou `INSTALADO` / `JOGAR` e 26 jogos instalados.

| Fase | Duração |
| --- | ---: |
| Autorização | 141 ms |
| Conexão e cabeçalhos | 136 ms |
| Corpo e escrita em disco | 86 ms |
| Instalação | 102 ms |
| Soma das fases registradas | 465 ms |

Esta é uma observação real no telefone, informada pelo coordenador após a assinatura. O arquivo pequeno e a ausência de uma comparação equivalente anterior não permitem atribuir um ganho percentual ao R16 ou estimar a taxa sustentada de jogos grandes. O tempo de corpo inclui disco; 465 ms não inclui necessariamente fila e atualização visual. Os registros estão em `evidence/download-metrics.txt` e `evidence/installation.json`; o modelo do aparelho consta acima.

### Benchmark local Android

Fonte: `W\bench\nohash\android-shared-summary-20261005.json`, com resultados brutos em `android-shared-results-20261005.csv`. São dados sintéticos de 64 MiB, três rodadas por caso, Dalvik/Linux aarch64 e destino no armazenamento compartilhado do Android. A tabela usa a mediana da execução sem instrumentação detalhada.

| Fragmento fornecido ao leitor | Caminho anterior | Saída bufferizada sem hash | Redução da mediana do tempo |
| --- | ---: | ---: | ---: |
| 8 KiB | 717,257 ms / 89,229 MiB/s | 239,859 ms / 266,824 MiB/s | 66,56% |
| 16 KiB | 330,033 ms / 193,920 MiB/s | 258,708 ms / 247,383 MiB/s | 21,61% |
| 64 KiB | 376,286 ms / 170,083 MiB/s | 287,241 ms / 222,809 MiB/s | 23,66% |

Esses números medem o caminho local de cópia/escrita, sem HTTP, TLS, Wi-Fi, internet ou servidor. Não são a velocidade de download do aplicativo R16. Houve variação de armazenamento/fsync e outras variantes foram mais rápidas em alguns casos; três rodadas não sustentam promessa universal de ganho. O harness conferiu conteúdo fora da transferência cronometrada e confirmou explicitamente que a variante sem hash não rejeita divergência de conteúdo de mesmo tamanho. Tamanho, excesso de bytes, cancelamento, preservação do anterior e limpeza do parcial foram exercitados.

### Referência histórica do servidor

Servidor associado: branch `feat/station-neogeo-throughput-20261005`, commit `41837c695b880323441002d837c35b850f942cc3`. Este handoff identifica o código; não atesta novo deploy ou medição de produção do servidor.

O registro histórico em `C\work\TurboElden-git\versions\station-neogeo-rate-20261005\README.md` informa, no Linux e com artefato autorizado de 65.243.904 bytes, API 316,35 MB/s, Nginx 259,99 MB/s e HTTPS público 3,76/4,37 MB/s; controle de upload 3,77 MB/s e duas conexões 4,34 MB/s agregados. Não foi identificado limitador artificial naquele recorte. Esses dados são do registro anterior, não da internet atual do telefone e não do benchmark local acima.

## Testes e provas

`W\client\build-final\test-results.json` registra 787 verificações em 16 suítes: Offline 48, Performance 71, CatalogPoll 33, AutomaticCatalog 6, Folders 29, Files 32, Api 75, OnlineApi 27, Storage 36, Coordinator 25, Installer 60, Closure 86, Bootstrap 25, CoverConcurrency 41, TransferReuse 13 e CoverPublication 180.

As suítes abrangem tamanho/formato/caminho, cancelamento/rollback, recibos e entrada ausente, ausência de varredura de acompanhantes, transição de fase, métricas, resposta HTTP parcial/completa, protocolo assinado, acesso local sem HTTP, validade por proprietário/dispositivo, negativa persistida e publicação concorrente. Os testes offline usam assinatura real de fixtures e incluem a barreira de perfil HTTP lento enquanto outra chamada abre o jogo local. São testes locais com dados controlados.

`W\native-build\compiled-modules.json` e `native-validation.json` registram 32 verificações C++, arquitetura AArch64 e segmentos LOAD alinhados a `0x4000`. `W\build-result.json` registra comparação de todas as entradas de conteúdo, preservação do DEX de salas, certificado e alinhamento do APK final.

## Evidências Android e limites restantes

- `evidence/installation.json`: atualização sem desinstalar/limpar dados, SHA idêntico e download de Classic Kong; `evidence/download-metrics.txt` contém as correlações e métricas sem credenciais.
- `evidence/offline-device.json` e `evidence/offline-logcat.txt`: retomada de ESActivity sem rede, cache de 2.162 itens, zero traces HTTP e restauração do Wi-Fi/dados móveis. As duas aberturas mediram retomada da Activity em 0,666/0,717s, não todo o carregamento visual. Após 12s sem rede, a segunda captura mostrou artes das plataformas e sinopse; a primeira captura aos 4s ainda tinha prévias transitórias. Capas de jogos e gameplay offline não foram exercitados no aparelho.
- Permanecem sem prova nesta revisão: taxa sustentada com arquivo grande; gameplay/retorno de cada emulador; capas e partida durante a sessão dedicada sem rede; partida netplay entre dois aparelhos.
- Nenhum servidor foi modificado ou implantado por esta entrega. O teste local de nohash não altera os grants/sessões do servidor. Não promover tags estáveis sem validação específica do mantenedor.

O snapshot será publicado no ramo de trabalho `feat/station-capas-visuais-netplay-20261003`. O commit da publicação pode ser consultado pelo histórico deste diretório; não confundir os commits do servidor com esta versão do app.
