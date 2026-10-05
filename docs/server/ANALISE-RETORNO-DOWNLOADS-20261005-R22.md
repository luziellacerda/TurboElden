# Retorno de downloads cruzado com o APK R22 — 05/10/2026

## Fontes exatas

- Servidor-pix, branch `feat/station-raw-transfer-20261005`, commit `11be7f3a725d236439be820dd0a3e6c517e771f5`: [retorno](https://github.com/luziellacerda/Servidor-pix/blob/11be7f3a725d236439be820dd0a3e6c517e771f5/docs/station-android/RETORNO-DOWNLOADS-SEM-VERIFICACOES-20261005.md).
- Cliente preparado em TurboElden, commit `6f012a7`, `versions/station-raw-transfer-20261005`.
- APK R22 instalado: SHA256 `f7dfc90f0614644548f16cfc7a518ba869589c815adacd6adb9f411f6a97de29`, comprovado pelo hash do `base.apk` no telefone.

## Resultado da leitura e comparação

A otimização está preparada em fonte e módulos, **ainda não incorporada ao APK instalado**. A comparação das entradas reais do APK encontrou:

| Módulo | SHA256 instalado R22 | SHA256 preparado no retorno |
|---|---|---|
| `classes28.dex` | `ba3bf581a02a32484b4bed4de64cb78ae9e790b9ffe4030f93012703d8578c21` | `0f2748eaf8f4f1622f2537c94495d48843f2d8a69ae933485de2fa35772b9ddd` |
| `lib/arm64-v8a/libstation_archive.so` | `9b6576b07b3e44dc48e5ec478cfb8db16852aa1aca0a7895cb567e7b57ff8c7a` | `3edbb4bd08af6ae4585b53c3243c56921f2bedac475298612bf88f042e62c54c` |

Foi lido o diff de `StationInstaller` contra R16 e o código de extração proposto. O novo caminho `installStaged` move o RAW recebido para a geração instalada por renomeação atômica, em vez de copiar todo o corpo. Continua com cópia transacional quando o filesystem não admite essa renomeação, condicionada ao espaço. A fila usa o recibo dos bytes recebidos e evita reabrir o corpo para conferências de conteúdo; ZIP configura `zip:ignorecrc32=1`. A API mantém licença/descritor assinado, caminhos e limites; não é remoção dessas regras de autorização.

A preparação de Metal Slug CD antes duplicava a escrita de um corpo de431.225.741bytes. O delta corrige isso e a contagem RAW que deixava o download em50% antes da cópia. Também evita consulta integral antecipada do catálogo: atualiza somente quando a revisão do grant exige conciliação.

O servidor registrou821verificações Java em18suítes e14JNI, além de builds Android. Esses testes foram feitos pelo produtor e não foram reexecutados nesta leitura. Não há prova de desempenho da nova revisão no aparelho.

## Gargalo externo continua separado

O retorno mediu aproximadamente3,225MB/s para o CHD e4,000MB/s para o ZIP no HTTPS público; o caminho local atingiu cerca de300MB/s. Não são medições do telefone e não identificam isoladamente o responsável pelo caminho externo. Nenhum novo limitador, deploy ou restart foi aplicado nesta leitura.

## Integração necessária

Usar o APK vigente comprovado, conciliando a guarda da receita que ainda aponta para R20. Substituir somente os dois módulos acima, preservar R21/rolagem, R22/vídeos/prévias, motores, recursos N64, MAME, salas, certificado, licença, jogos e saves. A revisão R23 visual está em preparação no chat coordenado e também deve ser preservada caso já esteja concluída.

Depois de assinar e instalar por atualização, medir separadamente autorização, rede e preparação de um CHD grande, além de ZIP/cancelamento/retorno. Não voltar ao APK R20 para aplicar o delta e não misturar a ponte Neo Geo CD preparada separadamente. Nesta tarefa foram feitas somente leitura e comparação do retorno de downloads.
