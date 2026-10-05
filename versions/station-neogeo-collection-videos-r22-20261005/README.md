# TurboStations — vídeos das coleções Neo Geo — R22

## Pedido e escopo

O mantenedor indicou a pasta literal `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas\Sele;'ao` para os vídeos da seleção Neo Geo. Foram encontrados três arquivos: `fatalfury.mp4`, `megal slug.mp4` e `samurayshodow.mp4`. Os primeiros quadros foram lidos visualmente: Fatal Fury Special, Metal Slug e Samurai Shodown Neo Geo Collection.

Esta entrega altera a apresentação das coleções, usando o carrossel nativo e o player já existente. A relação entre jogo e coleção continua vindo do catálogo Station. O aplicativo não inventa pastas, não redistribui jogos por nomes e não muda IDs, motores, controles, downloads, dados ou sessão.

## Mapa confirmado no servidor

Fonte: Servidor-pix, commit `100e4bbd92aa4c85cda10a633e6463fbb24ae8ab`, `docs/station-android/biblioteca-neogeocd-20261005/catalogo-completo.tsv`, SHA256 `3dae0cfa3877fba31b9a347b58795fe0df95333aea628b9ea8be597b7ccfed6e`. Esse retorno identifica catálogo14; o TSV contém189NeoGeo visíveis. Esta é evidência publicada no Git, não uma nova captura HTTP ou do telefone.

| Pasta exata do catálogo Neo Geo | Jogos publicados | Vídeo de origem |
|---|---:|---|
| `# 4 - FATAL FURY COLEÇÃO #` | 4 | `fatalfury.mp4` |
| `# 1 - METAL SLUG COLEÇÃO #` | 9 | `megal slug.mp4` |
| `# 2 - SAMURAI SHODOWN COLEÇÃO #` | 6 | `samurayshodow.mp4` |

As outras coleções, incluindo Art of Fighters, The King of Fighters e Hacks, não receberam vídeo nesta pasta fornecida e conservam o fallback existente. Não renomear nem alterar as pastas do servidor para acomodar o nome do MP4.

## Local de trabalho

`E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005`

- `media/`: três MP4 destinados ao APK.
- `previews/`: primeiro quadro de cada vídeo, PNG para inspeção e RGB565 invertido verticalmente para o cache nativo.
- `neogeo_previews.S` e `.o`: somente três novos símbolos de prévia.
- `media-manifest.json`: caminho/hash de origem, parâmetros e hash das saídas, inspeção de streams e resultado da decodificação completa.
- `native/`: cópia integral do overlay final R21, acrescida dos dois headers de roteamento/prévias.
- `evidence/integration.json`: catálogo/folders observados, rotas exatas, comando NDK e hashes do overlay original preservado.
- `build-result.json`: identidade do APK, base e comparação de todas as entradas.

## Mídia

Fontes: H.264, 960×960, 24 fps, duração 6,041667 s. Saídas: H.264 Constrained Baseline nível 3.1, 720×720, yuv420p, 30 fps, sem áudio nem imagem anexada, sem B frames, `faststart`, GOP 60. O tempo de reprodução é preservado dentro de um quadro de saída. A conversão replica quadros conforme necessário, sem aceleração e sem inventar interpolação de movimento.

As fontes já são quadradas. A redução proporcional mantém toda a imagem: nenhum crop, deformação, faixa ou legenda adicionada. A repetição continua sendo controlada pelo player existente. Os três vídeos somam 9.029.298 bytes; as três prévias usam 3.110.400 bytes de pixels no binário. Os originais G: permanecem intactos.

## Código e fluxo

1. Catálogo autenticado fornece `platform` e `folderPath`.
2. `native_folders.h::folderVideo` resolve o item visível e chama `collectionVideoFor`.
3. `collection_video_policy.h` exige a família de plataforma correta e o nome completo da folha; só remove espaços e `#` nas extremidades, como antes. Não usa busca parcial.
4. A célula `Todos os jogos` conserva o vídeo principal da plataforma, pois `all=true` retorna sem vídeo específico de coleção.
5. `native_system_video720.h::video720Asset` usa o vídeo da coleção quando há correspondência; demais pastas conservam o comportamento anterior.
6. `video720_posters.h` acrescenta as prévias reais dos três vídeos. O objeto legado com 49 prévias é ligado uma vez, e `neogeo_previews.o` uma vez. Não combinar de novo o objeto legado com outra cópia de si mesmo.
7. O mesmo player reproduz somente o vídeo focado. Permanecem quatro slots existentes, política de prévias com oito texturas, pausa na entrada dos jogos/configurações e liberação ao sair. Esta entrega não acrescenta decodificador nem loop de renderização.

Os cinco vídeos SNES continuam no mapa original e restritos às plataformas SNES. Os três Neo Geo são restritos a `Neo Geo`, `neogeo` e `neo-geo`; não são automaticamente aplicados ao Neo Geo CD. Os programas de LED R20 e a rolagem/limitação das sinopses R21 devem permanecer byte a byte nos arquivos de origem copiados.

## Reconstrução

1. Executar `prepare_neogeo_collection_videos_r22.py` apenas para criar uma pasta nova, com os três originais disponíveis. Ele recusa substituir a pasta W22.
2. Executar `record_neogeo_collection_catalog_r22.py` para registrar o mapa acima a partir do commit exato. A primeira tentativa de ler o cache do aparelho foi recusada por `run-as` (pacote não debuggable); não houve mudança no aparelho nem tentativa de contornar essa proteção. A fonte aceita é o TSV publicado pelo servidor. Não publicar envelope com identificadores de licença/dispositivo/sessão.
3. Executar `integrate_neogeo_collection_videos_r22.py --catalog-folders <evidência> --base-native <overlay R21 final> --base-receipt <build-result R21 final>`. A receita recusa nomes não presentes na evidência e exige recibo de APK verificado. Nenhum fonte compartilhado R16/R20/R21 é editado.
4. Executar `package_neogeo_collection_videos_r22.py --base-apk <APK R21 verificado>`. A receita exige SHA da base, altera somente `libturbo_carousel.so`, adiciona exatamente três MP4 e compara cada entrada restante. Usa certificado existente e alinhamento 16 KiB.
5. Instalação somente após liberar USB com o chat coordenado, por atualização `adb install --no-incremental -r --user 0`, sem desinstalar ou limpar dados. Conferir hash do APK instalado e entrada/volta das três coleções.

## Evidências e limites

APK final: `E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\TurboStations-NeoGeo-Colecoes-R22-20261005.apk`, 2.053.643.400 bytes, SHA256 **`f7dfc90f0614644548f16cfc7a518ba869589c815adacd6adb9f411f6a97de29`**. Só `lib/arm64-v8a/libturbo_carousel.so` alterado; três MP4 adicionados; todas as13.080entradas restantes comparadas e preservadas. Certificado original e alinhamento16KiB conferidos. O recibo de instalação separado define o estado do aparelho.

**Instalado por atualização em 05/10/2026**, partindo da R21 exata. O hash do `base.apk` instalado é idêntico ao acima. O aplicativo foi iniciado pelo launcher público, sem desinstalar nem limpar dados. Ver `evidence/installation.json` na publicação e `device-evidence/installation.json` no diretório de trabalho.

O log do aparelho confirmou os três vídeos preparados e retomados quando focados: Metal Slug às16:26:08/13, Samurai Shodown às16:26:14/20 e Fatal Fury às16:26:17/18. A navegação também abriu Samurai Shodown com6jogos e retornou às coleções. A captura às16:26:55 já mostrava os jogos da coleção The King of Fighters; não é prova visual do vídeo Metal Slug selecionado.

**Limite observado:** numa pré-carga posterior, depois de várias entradas/saídas e mudanças de foco, Fatal Fury registrou `Video first-frame timeout` às16:26:40. O mesmo arquivo havia preparado/retomado corretamente antes. A causa não foi isolada, e esta entrega não alterou o player Java existente. Não declarar ausência de travamentos, erro de codec comprovado ou reprodução sustentada dos três vídeos a partir desses logs. A prévia real está embutida, mas recuperação posterior e loop sustentado precisam de conferência específica.

As verificações de mídia passaram por todos os quadros dos três vídeos. **3.317 verificações C++ passaram**, exercitando os nomes completos, caminhos aninhados, caracteres decorativos, separação entre plataformas, `Todos os jogos`, entradas inválidas e nomes semelhantes que não devem casar. Compilação NDK e conferência de APK ficam registradas nas evidências próprias.

Overlay Android compilado com NDK r28c/arm64/API26, SHA256 `13a44bdf6c5a10b5bdaa70e9831c960e5450aa1fe9a0f140dc0a89779f4ba6c3`. Base final R21: APK `4c6bf41312be20e98ff15a6b7fbc2f85bb470bca1af39058ab362e39015543b4`, SO `f802efdc262bd6a0818bfee5b833499179bd910cc2f5b93da0d644504168d3ba`. As fontes do overlay R21 conferem com o manifesto da compilação, o SO da base confere com o APK e cada fonte copiada permanece idêntica após a integração. Somente os dois headers novos fazem o roteamento/prévias dos vídeos.

Regressões locais adicionais: **140 verificações de rolagem** e **15.375 de visibilidade/layout** passaram. Conferência dos símbolos compilados encontrou exatamente52prévias (49anteriores e3novas), sem duplicação. Orçamento existente de8texturas e limite de4slots preservados. Isso comprova a política/código; não mede consumo/FPS no aparelho.

O APK e o SO R21 foram arquivados, com SHA/tamanho conferidos antes de remover apenas as duplicatas em E:. Caminhos atuais:

- R21 APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Consoles-Sinopses-R21-20261005.apk`.
- R21 SO: `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-console-games-only-r21-20261005\libturbo_carousel.so`.
- R22 SO: `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-neogeo-collection-videos-r22-20261005\libturbo_carousel.so`.

Fontes, objetos de ligação e evidências ficam em E:. Para a receita de pacote, usar `--native-so <SO R22 arquivado>`. Para o próximo desenvolvimento, copiar W22/native e ligar **W16/frontend-native/video720_posters.o uma vez mais W22/neogeo_previews.o uma vez**, conforme comando exato em `evidence/integration.json`. Usar apenas o objeto legado deixa três símbolos faltando; somar o legado duas vezes duplica49símbolos.

Não declarar instalado ou visualmente aprovado sem recibo do aparelho. Não declarar nova estabilidade geral, consumo ou FPS sustentado sem medição. Nenhum deploy ou alteração no servidor foi feito nesta tarefa.

## Retorno posterior de downloads, lido nesta tarefa

Servidor-pix `11be7f3a725d236439be820dd0a3e6c517e771f5`, `RETORNO-DOWNLOADS-SEM-VERIFICACOES-20261005.md`: delta preparado em TurboElden `6f012a7`. **Não está neste APK.** R22 mantém `classes28.dex` SHA `ba3bf581a02a32484b4bed4de64cb78ae9e790b9ffe4030f93012703d8578c21` e `libstation_archive.so` SHA `9b6576b07b3e44dc48e5ec478cfb8db16852aa1aca0a7895cb567e7b57ff8c7a`. O retorno propõe substituir só esses dois módulos, preservando esta entrega visual. A receita original tem guarda R20; deve ser conciliada com a sucessora vigente comprovada. A leitura do retorno não instalou esses módulos nem alterou o servidor.
