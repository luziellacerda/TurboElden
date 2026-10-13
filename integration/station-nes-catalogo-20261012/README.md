# Leitura completa do catálogo com NES

O servidor oferece 4.435 jogos visíveis, incluindo 750 NES. A R138 instalada tem limites Java e JNI de 4.096 itens: recebe todos os 3.685 anteriores e os primeiros 411 NES. A composição seguinte precisa deste ajuste para mostrar os 750.

## Aplicação na produção do APK

1. Aplique `patch_catalog_capacity.py` à pasta `org/emulationstation/frontend/station` da composição atual e ao seu `station_frontend.cpp`:

   ```text
   python patch_catalog_capacity.py CAMINHO/STATION --native-source CAMINHO/station_frontend.cpp
   python patch_catalog_capacity.py CAMINHO/STATION --native-source CAMINHO/station_frontend.cpp --write
   ```

**Preservação conferida em 13/10:** o snapshot C++ abaixo é R124 e não contém os exports de loading R132 da composição R138. Aplique somente o patch de capacidade à fonte corrente. Antes de compilar, execute `audits/station-performance-preservation-20261013/recipe/verify_nes_preservation.py` sobre os diretórios antes/depois e o frontend corrente; a verificação recusa substituição pelo snapshot antigo e qualquer ajuste de workers/cache não relacionado.

2. Compile o cliente Java completo e o frontend pela receita vigente. Os cinco arquivos Java e o C++ nesta pasta registram o delta revisado sobre a fonte R124, herdada pela R138; o patch permite conservar as demais mudanças da composição corrente.
3. O pedido passa a ser `GET /v1/station/catalog?metadata=1&maximumItems=20000`, com a prova assinando o caminho **incluindo a query**. Continue validando assinatura, domínio, produto, licença, aparelho e sessão. O limite de corpo continua 64 MiB.
4. Preserve as estruturas ABI de `station_catalog_abi.hpp`. Os dois limites JNI de publicação/preparação passam a 20.000. As filas de jobs, os controles, os workers de imagens, os buffers e os limites de evidência por modo mantêm suas regras atuais.
5. Refaça os marcadores/selos dos bundles que incluem os artefatos alterados, usando os bytes finais. Assine com o certificado original e atualize os aparelhos preservando dados, licença e saves. Produza o kit privado correspondente quando houver mudança de identidade de motor.

## Contrato de leitura

O payload assinado acrescenta `totalItems` e `hasMore`. A consulta completa retorna 4.435 itens, `totalItems:4435`, `hasMore:false`. Sem `maximumItems`, o servidor retorna até 4.096 para manter os clientes existentes funcionando. Valores zero, negativos, duplicados ou superiores a 20.000 retornam 400.

`platform:"nes"` já resolve para Nintendinho. Use o `itemId`, `coverId`, `item.revision`, `folderPath`, `metadata` e o descritor de download recebidos. Cache da capa: `coverId + item.revision`; capas novas NES usam revisão 44. Cada arquivo JPEG servido tem 480×720. Obtenha os jogos por autorização e grant de uso único, conservando formato e `launchPath`.

Novos dados: 748 `.nes`, um `.fds`, um `.unf`; todos em formato de download `raw`. Os descritores são gerados pelo importador. Arquivo novo e capa JPEG com o mesmo nome-base em `nes/media/revista` entram pela rotina automática. O seed também associa nomes já conhecidos. Sinopse vem do `gamelist.xml`/seed ou do cadastro complementar quando ausente.

## Provas e limites

`build-check.json` registra compilação Java 8/API34, D8/API26, parser real com 4.435 itens e limite 20.000, recusa de duplicatas/excesso e frontend arm64/API26 com alinhamento 16 KiB e ABI preservada. São artefatos de qualificação; montagem/assinatura/instalação do novo APK acontecem no PC de produção. O servidor foi aplicado e a troca de capas publicada pelo scanner existente, sem reinício adicional.

NES está publicado para catálogo/capas/downloads. Um motor NES online correspondente ainda precisa de integração própria; `metadata.players` não autoriza partidas. Os registros R138 e as pendências dos quatro motores independentes continuam no handoff único.
