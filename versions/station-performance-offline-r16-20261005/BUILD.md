# Build e rastreabilidade — TurboStations R16

Este registro descreve o build concluído em 05/10/2026 e os insumos para reproduzi-lo em uma cópia nova. O cliente combinado em `W\client` e seus resultados `build-final` estão congelados. O escopo funcional, as limitações e as métricas estão em [README.md](README.md).

## Raízes e fontes

```text
W = E:\ESTUDO APK\work\station-download-performance-20261005
C = C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work
O = E:\ESTUDO APK\work\station-offline-access-20261005
N = C\work\station-native-rate-phase-20261005
```

O cliente Java final é `W\client\src`, com testes em `W\client\tests`. O pacote de fontes exato do módulo está em `W\client\build-final\station-client-sources.zip`; `test-results.json` identifica hashes individuais das fontes testadas. Usar esses arquivos finais para rastreabilidade, porque snapshots intermediários antecedem a integração e o ajuste de atualização offline.

O build nativo usa as fontes alteradas em `N\client\src\native` e `N\frontend-native`, os headers/recursos de `W\client\src\native` e `W\frontend-native`, e produz `W\native-build`. Os comandos completos usados estão gravados em `compiled-modules.json`. `N\source-manifest.json` registra o conjunto de fontes. A fonte anterior canônica em `E:\ESTUDO APK\work\station-netplay-20261004` não foi usada como destino de alterações desta entrega.

## Integração realizada

1. O delta de desempenho incluiu escrita bufferizada, caminho de jogos sem hash, remoção de busca de legado, entrada local sem varredura dos acompanhantes, fases e métricas.
2. O delta offline foi incorporado ao mesmo cliente, preservando `replaceArtifact` e o fluxo de desempenho. O ajuste posterior moveu HTTP da atualização automática para o trabalhador de polling, mantendo apenas a publicação no executor `commands`.
3. A versão interna do cliente foi definida como `1.0.8-station-performance-offline-r16-20261005`.
4. A união final passou pelas 16 suítes Java e foi compilada para Android; o DEX dessa união foi o único DEX Station empacotado no R16.
5. Os módulos nativos de taxa/fase foram compilados e conferidos, e o APK R15 exato recebeu apenas as três substituições autorizadas.

Scripts históricos em `C`: `optimize_station_transfer_20261005.py`, `apply_download_installer_user_policy.py`, `finalize_station_r16_sources.py` e `package_station_performance_r16.py`. São scripts de preparação/empacotamento com caminhos fixos e guardas de execução; não reaplicá-los sobre a árvore congelada. `W\offline-merge.json` registra a integração, mas seus hashes intermediários não substituem o manifesto final de fontes testadas.

O handoff offline original e o complemento estão em `O`:

| Arquivo | SHA-256 |
| --- | --- |
| `offline-delta.patch` | `02b9f583d0560e34c17cba7be432d9ca0b6f3817b09cfc4234354e84865d5ec1` |
| `offline-refresh-followup.patch` | `f28f3c6939c5378a6885dfcefb3acddfe99129a67f366cd4eec59dd1e0f512fd` |

O DEX do build offline isolado anterior e os resultados anteriores de 707/723/738 verificações não representam a união final. O registro final é de 787 verificações.

## Ferramentas Java/Android

| Ferramenta | Local usado |
| --- | --- |
| JDK 17 | `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin` |
| API Android 34 | `G:\Android\Sdk\platforms\android-34\android.jar` |
| D8 | `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar` |
| Build tools / zipalign / apksigner | `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15` |
| JSON para testes host | `E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar` |

O runner `client\run_tests.py` executa as suítes host e compila os fontes para API 34 / Java 8. O `client\build_module.py` gera JAR, AAR, arquivo de fontes e DEX com `min-api 26`. Ambos usam `STATION_BUILD_DIR` para o diretório de saída. O runner pode normalizar fontes; para reproduzir, primeiro copiar o cliente final para outra pasta isolada e configurar os caminhos nessa cópia. Não executar sobre o cliente congelado.

Sequência equivalente para uma **nova cópia**, com destinos escolhidos pelo operador:

```powershell
$r16ClientCopy = '<nova-copia-isolada-do-client-final>'
$env:STATION_BUILD_DIR = '<novo-diretorio-de-build-vazio>'
python (Join-Path $r16ClientCopy 'run_tests.py')
python (Join-Path $r16ClientCopy 'build_module.py')
```

As dependências e caminhos nos scripts devem apontar para os insumos acima ou seus equivalentes conferidos. Não se afirma reprodutibilidade binária de cada ZIP/JAR em ambiente diferente; comparar fontes, resultados, DEX e conteúdo empacotado, além de documentar qualquer diferença de ferramenta ou timestamp.

### Saídas Java finais

Diretório: `W\client\build-final`.

| Arquivo | Bytes | SHA-256 |
| --- | ---: | --- |
| `station-client.jar` | 152.419 | `e41854977e9c2dab786f431449c95afb759e80c653e02cbc990434f74a2c39a2` |
| `station-client.aar` | 137.668 | `5d5c3276648a53e54dbff80beb5c9d51931ee34c260252d45ed9bcef0bc0e06f` |
| `dex\classes.dex` | 153.144 | `ba3bf581a02a32484b4bed4de64cb78ae9e790b9ffe4030f93012703d8578c21` |
| `station-client-sources.zip` | 127.986 | `e1882298cbd21ea7de3661c6fbdcd1cbc6e11b2f6e93e3db8751b2cc1806c9b2` |

O DEX acima é instalado no APK com o nome `classes28.dex`. Evidências: `module-manifest.json` e `test-results.json` no mesmo diretório.

## Build nativo

Compilador Android: `E:\TurboEdenEngine\android-ndk-r28c\toolchains\llvm\prebuilt\windows-x86_64\bin\clang++.exe`. Alvo `aarch64-linux-android26`, C++17, `-O2`, `-shared`, `-fPIC`, `-Wl,-z,max-page-size=16384` e `-Wl,--no-undefined`.

- JNI: fonte `N\client\src\native\station_frontend.cpp`, includes de `W\client\src\native`, visibilidade oculta, `-Wall -Wextra -Werror`, exceção existente para `return-type-c-linkage`, `-static-libstdc++`, `--exclude-libs,ALL`, links `dl` e `log`.
- Carousel: fonte `N\frontend-native\native_carousel.cpp`, includes de `W\frontend-native`, objeto `video720_posters.o`, bibliotecas daquela pasta, `-nostdlib`, sem exceptions/RTTI/stack protector/builtin, soname `libturbo_carousel.so`, links `c`, `dl` e `log`.
- Teste host: `C:\Program Files\LLVM\bin\clang++.exe`, C++17, `-O2 -Wall -Wextra -Werror`, fonte `N\tests\transfer-rate-phases.cpp`.

`N\build_native.py` contém os comandos; `W\native-build\compiled-modules.json` registra os argumentos efetivamente usados. Para reconstrução, copiar/adaptar esse script para novas saídas e manter as entradas identificadas. Executá-lo sem adaptação escreve em `W\native-build`, que pertence ao conjunto congelado.

| Módulo | Bytes | SHA-256 |
| --- | ---: | --- |
| `libstation_frontend.so` | 3.014.848 | `ebb1a942dd59f62ab82d24d9021e382abab26d3258c7b266790a26ea00ad6cfe` |
| `libturbo_carousel.so` | 85.292.728 | `1d12a1f2f27d548751ce95cc178c6a436965d997d2260b4f45489e23c71cc111` |

Resultado: `PASS 32 native transfer rate, phase and exact job checks`. `native-validation.json` registra AArch64, LOAD `0x4000`, ABI `Progress` de 48 bytes, e três avisos de trigraph já existentes em headers de sinopse, sem erro. SHA do manifesto nativo: `c2496c17b938e70b26b91214abf3646b70978ce5a5b31af5b790849a20e47500`.

Os campos `apkPackaged: false` e `installed: false` de `compiled-modules.json` descrevem a etapa de módulos. Para o empacotamento posterior, usar `W\build-result.json`.

## Empacotamento e assinatura

Base exata, somente leitura:

```text
G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-NeoGeo-N64-R15-20261005.apk
SHA-256: d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b
```

`C\package_station_performance_r16.py` validou o SHA da base e a presença da integração offline, substituiu a lista permitida abaixo e manteve as demais entradas de conteúdo. O script recusa saídas já existentes; não rerodar para sobrescrever o APK entregue. Assinatura foi feita pelo fluxo local autorizado com o certificado original, sem distribuir credenciais ou a chave privada neste handoff.

| Destino dentro do APK | Origem |
| --- | --- |
| `classes28.dex` | `W\client\build-final\dex\classes.dex` |
| `lib/arm64-v8a/libstation_frontend.so` | `W\native-build\libstation_frontend.so` |
| `lib/arm64-v8a/libturbo_carousel.so` | `W\native-build\libturbo_carousel.so` |

O fluxo preservou compressão das entradas existentes, alinhou bibliotecas armazenadas a 16 KiB e outras entradas armazenadas a quatro bytes, conferiu `zipalign -c -P 16 4`, assinou e conferiu novamente alinhamento/certificado. A comparação final exigiu conjunto de entradas sem duplicatas, conteúdo idêntico fora das três substituições e preservação exata do DEX de salas. Metadados da assinatura são recriados no processo de assinatura.

### APK final conferido

| Campo | Valor |
| --- | --- |
| Arquivo | `W\TurboStations-Desempenho-Offline-R16-20261005.apk` |
| Registro | `W\build-result.json`, criado `2026-10-05T17:29:47.030505+00:00` |
| Bytes | `2036268564` |
| SHA-256 APK | `b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1` |
| SHA-256 certificado | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| SHA-256 salas / `classes35.dex` | `8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae` |
| Entradas de conteúdo preservadas | `13078` |
| Entradas de conteúdo alteradas | `3` |
| Comparação completa / alinhamento | `allPackageEntriesVerified: true`, `alignment16KiB: true` |
| Instalação / estabilidade no registro | `installed: true`, `stable: false` |

O registro atual inclui instalação confirmada com hash idêntico e o download real de Classic Kong de 262.144 bytes: 141 ms de autorização, 136 ms de cabeçalhos, 86 ms de corpo/escrita e 102 ms de instalação. A interface mostrou INSTALADO/JOGAR e 26 instalados. Duas aberturas sem rede retomaram o catálogo local de 2.162 itens sem HTTP, e as conexões originais foram restauradas. Recibos estão em `evidence/installation.json`, `download-metrics.txt` e `offline-device.json`. Gameplay e estabilidade geral continuam sem aprovação nesta revisão.

O campo `gameDownloadContentHashEnabled: false` se refere ao caminho de recebimento/instalação/abertura local dos jogos. A identidade SHA do netplay, assinaturas públicas do protocolo e hashes de build permanecem; não interpretar esse campo como ausência de criptografia ou de SHA no APK inteiro.

## Índice de evidências e complementos pendentes

| Evidência | Uso |
| --- | --- |
| `W\client\build-final\test-results.json` | 787 verificações, 16 suítes, API 34 / Java 8 e fontes individuais |
| `W\client\build-final\module-manifest.json` | Hashes e tamanhos JAR/AAR/DEX/fontes |
| `W\native-build\compiled-modules.json` | Comandos, hashes e 32 verificações C++ |
| `W\native-build\native-validation.json` | Arquitetura, alinhamento, ABI e manifesto de fontes |
| `W\build-result.json` | Base, APK assinado, certificado e comparação completa |
| `W\bench\nohash\android-shared-summary-20261005.json` | Benchmark local Android; não mede internet |
| `O\HANDOFF-OFFLINE-STATION-20261005.md` | Contrato offline e histórico da implementação |

Servidor associado: `feat/station-neogeo-throughput-20261005`, commit `41837c695b880323441002d837c35b850f942cc3`. As medições de servidor citadas no README são históricas. Acrescentar separadamente prova de deploy/publicação, commit final do pacote de entrega e logs do dispositivo. A instalação e o download curto confirmados pelo coordenador estão registrados acima; o candidato ainda não é promovido a estável.

O script de instalação publicado recebe o dispositivo por `STATION_ADB_SERIAL`; o valor específico do aparelho não foi incluído no Git.

O `.gitattributes` deste snapshot preserva os bytes das fontes congeladas, incluindo suas quebras de linha, para manter os hashes registrados. Apenas a cópia publicada do logcat offline teve CRCRLF normalizado para LF, sem alteração dos eventos. Os espaços nas linhas de contexto dos patches são parte do formato. `SOURCE-MANIFEST.json` identifica os bytes de todos os arquivos publicados.
