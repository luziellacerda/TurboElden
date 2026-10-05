# R23B — painel de jogos uniforme: jogadores, estrelas, console, título e contagem

## Estado exato da entrega

Fontes e SO R23B compilados: `48eda90ac617b1dbd318f8932883386466d5f3cc8cb10ec6586a4b499d953fab`, 93843368 bytes. Pasta `E:\ESTUDO APK\work\station-game-details-r23-20261005`. **Não existe APK separado R23B neste momento.** A primeira revisão R23A foi instalada por atualização, SHA `58c61a4d1e74396ffbefb2c5b6108e1c78a951164080a3b0f32de696330233e8`; hash do telefone igual. O aparelho bloqueou antes da conferência visual. R23B acrescenta a contagem solicitada depois dessa instalação. O chat coordenado vai juntar este overlay com os quatro arquivos do LED R24 e instalar uma entrega única; consultar recibo R24 quando existir. Não dizer que a contagem B já foi instalada nem promover estabilidade geral.

## Organização pedida

Mesma implementação para todas as listas de jogos (`!systemsMode && !folderMode`), sem condição exclusiva de Nintendo 64:

- Quantidade real da lista aberta abaixo da sinopse, no lugar antigo do título, com ícone de pasta. Responde ao filtro/pesquisa pela contagem do vetor visível; não é um número fixo de catálogo.
- Ícone de pessoas e quantidade de jogadores acima do console.
- Cinco estrelas com preenchimento proporcional, nota numérica em escala de 0 a 5 e legenda **Nota do catálogo**, também acima do console.
- Nome do jogo centralizado abaixo da foto do console, com redução de fonte e recorte para nomes longos.
- Sinopse completa com a rolagem R21 preservada. A barra só aparece se a altura medida exceder o espaço; textos curtos não precisam dela.
- Console continua fora do principal/coleções. Sem arte ou em tela estreita, texto usa largura disponível e metadados usam a faixa inferior válida; não há coluna vazia reservada para hardware inexistente.

Os ícones são vetores locais; não há imagem remota, timers ou animação nova. Estrelas fracionárias são recortadas horizontalmente pelo renderer nativo. Textos de quantidade/jogadores/nota/título têm seus próprios limites. Contagem e texto são atualizados quando seleção, lista, revisão ou tamanho mudam.

## Origem dos dados; nenhuma nota inventada

Catálogo publicado pelo servidor: commit `100e4bbd92aa4c85cda10a633e6463fbb24ae8ab`, `docs/station-android/biblioteca-neogeocd-20261005/catalogo-completo.tsv`, SHA `3dae0cfa3877fba31b9a347b58795fe0df95333aea628b9ea8be597b7ccfed6e`. Snapshot de 2.212 IDs; não depende de comparar títulos parecidos.

| Plataforma | Itens | Jogadores no servidor | XMLs ligados exatamente | Notas disponíveis |
| --- | ---: | ---: | ---: | ---: |
| Mega Drive | 887 | 855 | 887 | 749 |
| Mega Drive BR | 94 | 90 | 94 | 87 |
| SNES | 644 | 617 | 644 | 618 |
| SNES BR | 191 | 191 | 191 | 191 |
| N64 | 157 | 156 | 156 | 156 |
| Neo Geo | 189 | 162 | 189 | 185 |
| Neo Geo CD | 50 | 50 | 0 | 0 |

Jogadores: campo não vazio do catálogo tem prioridade; 27 ausências Neo Geo são preenchidas do XML com ID exato. Total 2.148 conhecidos / 64 ausentes. Notas: 1.986 conhecidas / 226 ausentes; nove zeros explícitos são notas zero, não ausência. Ausência recebe **Não informado** ou **Sem avaliação**. Não há quantidade de avaliações nem prova de média de avaliações de usuários; a interface identifica claramente nota do catálogo/XML.

SNES/Mega usam `station-synopses.json` já embarcado, por `sourceSha256 + sourceOrdinal` original, nunca `descriptionSource*`. N64/Neo Geo usam os XML originais com ROM path normalizado e algoritmo exato do servidor `station_ + sha256(platform + ':' + relativePosixPath)[:32]`, aceitando só IDs publicados. Nomes diferentes no XML não mudam o vínculo. O XML local de Neo Geo CD não cobre seus IDs atuais; não aproveitar nota de edição cartucho para CD.

`generate_game_details.py` valida hashes fixados, duplicatas, caminho relativo e intervalo 0–1. Converte rating para milésimos; UI multiplica por 5 para estrelas e arredonda número para uma casa. `station_game_details.h` contém IDs ordenados e busca binária, sem prefixos presumidos. Existem 741 IDs sem prefixo e 1.471 com `station_`; ambos chegam intactos: StationCatalog -> StationPublication -> StationFrontend campo0 -> station_frontend.cpp Item.id -> native_info strData(item).

## Limitação de atualização de metadados

A ponte Java/nativa atual transfere descrição, mas não jogadores/nota em Item. Este delta incorpora o índice auditado offline ao SO e funciona sem nova chamada ao servidor. Novos IDs ainda não presentes mostram ausência de dados até gerar um índice atualizado. Não afirmar que jogadores/notas de novos jogos serão obtidos automaticamente do servidor. Para ampliar, auditar novo TSV/XML, atualizar hashes/identidades e testes do gerador e recompilar; não criar aliases por título, não inferir quantidade pela plataforma. Uma futura ampliação da ponte de metadados precisa contrato explícito e teste próprio, preservando esta apresentação.

## Código e testes

Somente `native_info.h` muda sobre o overlay R22; novos `station_game_details.h` e `station_game_panel_layout.h`. Os demais headers são bytes da R22, incluindo navegação, N64, clipping/arrasto R21 e vídeos de coleção R22. JSON de build contém SHA de cada fonte. R23A alterou somente SO no APK, com 13.083 entradas preservadas, certificado original/16 KiB verificados; nenhuma alteração em servidor, Java, motores, downloads, licença ou saves.

- 12 testes Python de geração, identidade, ausência/zero e proveniência passaram.
- 11.070 verificações C++ exercitaram todos os 2.212 registros e IDs inválidos/aliases.
- 26.834 verificações C++ de geometria: metadados/foto/título sem sobreposição e distância do rodapé, telas grandes/pequenas/retrato/inválidas.
- Oito testes extraídos do formatador real de contagem: zero, singular, 157/644/887/2.212/40.000 e máximo uint32.
- Android arm64/API26 compilado; avisos antigos de trigraph nos XMLs preservados.
- R21 já confirmou no telefone clipping/arrasto/barra/início/fim em 007 N64 e sinopses curtas de plataformas/coleções. Usuário pediu conferência adicional SNES/Mega/NeoGeo; permanece pendente até APK integrado e tela desbloqueada. Nenhuma comprovação de todos os sistemas individualmente deve ser presumida.

## Compilação e próxima integração

Trabalho: `E:\ESTUDO APK\work\station-game-details-r23-20261005`. Comando em `evidence/native-build.json` / `recipes/compile_details_r23.py`. Includes herdados W16: `E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native`. Ligar **uma vez cada** `video720_posters.o` W16 e `E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\neogeo_previews.o`. São 49 previews antigos + 3 novos; usar apenas o primeiro objeto perde as coleções Neo Geo.

Este snapshot inclui todos os headers/C++/GLSL finais, exceto `console_assets.h` gerado; usar a mesma geração das sete artes R20 e hash no manifesto. Insumos do gerador podem ser realocados com argumentos; hashes e receita preservam a identidade. Não publicar APK, ROM, BIOS, chaves ou catálogo com URL/token.

Base R22 arquivada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-NeoGeo-Colecoes-R22-20261005.apk`, SHA `f7dfc90f0614644548f16cfc7a518ba869589c815adacd6adb9f411f6a97de29`. Arquivo R23A/receita de instalação estão em W23; consulte arquivamento posterior antes de usar seu caminho E. R23A histórico fica em `history-r23a`; seu SO 0bacfd... não contém a contagem B e não deve ser escolhido como final. SO B atual 48eda... é o recibo autoridade de fonte para R24; verificar todos seus hashes antes de sobrepor somente os quatro arquivos LED combinados.

O delta downloads `6f012a7` permanece separado e não integra R23A/B. Próxima montagem deve comparar todas as entradas contra a base APK e publicar recibo próprio. Instalar apenas atualização, sem desinstalação/limpeza de dados e sem interromper jogo ativo.

## Integração concluída em R24

A preparação descrita acima foi concluída através do APK R24 `d35516420934aeda7cee96af6185a17506146ae7fa2c28f867d6e7c44e721a0b`, com SO integrado `bf702a1eee840a850df007f2eb684d9aa7ef7ca7bec486e84bb01f9d9450b2e6`. Não houve APK independente R23B. Consulte os recibos de instalação e casos visuais no snapshot R24. Fonte e SO independente R23B permanecem históricos, intactos; R25/R26 substituem as posições dos metadados por novos pedidos do mantenedor.
