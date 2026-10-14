# R147 — propriedade da inicialização Dolphin e limpeza após falha

Preparação privada. Produção exige novo escopo
`integration/dolphin-boot-cleanup-r147-20261014` e commit congelado distinto.
Outputs somente em `E:/StationDolphinBootCleanupR147-20261014`.
Nenhum APK, instalação, kit aplicado ou gameplay é inferido desta preparação.

## Base e guardas

Base assinada R146 `04930201ad2f1c016f3385b3f08248ed4fa112d482a98761d00494b7a937468a`,
2.715.073.551 bytes, fonte `bfea454d04ef297e9dfd1b397e0bf25df3937e93`.
Prova parent `aafab1ca2231a5eeef8e2e282e4ce1b95f52111f752daaee82c6ec0afda81474`.
Os 28 pins produtivos R146 são conferidos no disco e no Git original.

DEX10 muda uma classe, quatro métodos existentes. 4.991 classes totais,
4.990 intactas; nenhum campo, método ou classe adicionado/removido.
Os 40 campos e 63 métodos da classe são preservados, exceto os quatro métodos
solicitados. As instruções/branches/try da representação canônica ed45 são
qualificadas; a inversão integral recupera a classe original 7dcbc. São três
trechos curtos de monitor, sem JNI/callback sob o monitor, threads/timers novos
ou chamadas JNI por quadro. As outras 39 partições DEX permanecem byte exatas.

O motor Dolphin só é aceito depois de recompilar integralmente a base original
f7ebe048..., incluindo o original não stripped 92b1951... e quatro hooks iguais.
Somente uma linha `s_is_booting.Clear()` no retorno antecipado por BootSessionData
nulo é autorizada. MainAndroid.cpp deve ser recuperável integralmente por inversão.
O builder deve preservar a árvore original, reproduzir os 94 inputs gerados da base e
reconstruir targets completos; objetos arquivados não substituem a compilação.
Na fase produtiva só o objeto MainAndroid.cpp.o desses 94 inputs pode mudar;
os outros 93 continuam byte exatos, com fonte/objeto identificado no build.ninja.
Os assets de empacotamento são redirecionados para a área nova, e a ausência
original de scmrev.cpp dentro da árvore é preservada.
Um receipt de prova somente de fonte ou somente de baseline é rejeitado como
core produtivo. SHA/bytes novos vêm exclusivamente do receipt real qualificado.

CPU/JIT/caches, opções, controles, perfis, capacidade, timers, rota R146,
READY/ACK e execução normal/surface/stop permanecem. ABI/exports/dependências/
SONAME/16 KiB são conferidos no motor efetivo. O carrossel 2e15 e outros motores
permanecem inteiramente iguais. Custo físico de processamento não foi medido.

## Identidades e pacote

Seis substituições: DEX10, core Dolphin, três wrappers originais e engines.json.
13.854 entradas de 13.860 permanecem, zero adições/remoções. O payload completo
de 345 entradas muda somente DEX10. O core Dolphin não integra esse mapa herdado;
é qualificado separadamente pelo receipt nativo e seus vínculos existentes.

As referências atuais duplicadas são corrigidas exatamente: DEX10 em
preservedPayloadSha256 dos três owners; core Dolphin em compiledBackendSha256
de N64/Dolphin; coreSha256 somente Dolphin e descritores GC/Wii. Uma inversão
dessas referências deve recuperar o objeto inteiro anterior. PSX/N64 mantêm
seus próprios cores, opções e controladores. Não há exclusão genérica de política.

nativeBuild continua como proveniência histórica da base. productiveTransforms
mantém a forma de mapa SHA e acrescenta os inputs congelados R147 e três vínculos
da qualificação atual: receipt nativo, core final e mapa canônico de fontes nativas.
Nove descritores RetroArch e oito IDs ativos permanecem; novos IDs independentes
exigem kit correspondente, sem ampliar aprovações por jogo/HLE.

## Closure e interfaces

common.source_map inclui helpers da raiz, recipe/java/tests/evidence/smali/
reference-java/native, os 23 inputs SOURCE-READY originais e o SOURCE-READY.json.
O README original consumido pelo verificador fica pinado. Árvore nativa completa
e outputs privados de baseline não são globados como fonte de integração; seus
recibos externos de closure continuam SHA fixos e exigidos pelo builder nativo.
Todos produtores devem fornecer o mesmo mapa global congelado; native sourceSha
é o subset exato de quatro arquivos.

- DEX: `build_dex.py --base --jdk-bin --apktool --out --source-commit`.
- Native: parâmetros completos de stage/build/closure/NDK do produtor nativo;
  somente execução revista e autorizada após guarda de original intacto.
- Identidade: `--base --dex-dir --dex-receipt --native --native-receipt --ndk --out --source-commit`.
- Montagem: os mesmos parâmetros de DEX/native, `--identity --out --source-commit`.
- Final: `--base --apk --receipt --dex-dir --dex-receipt --native --native-receipt --java --apksigner --zipalign --out`.

Identidade/montagem/final aceitam `--parent-proof`, com default da prova R146 em E:.
unsigned: `TurboStations-Premium-R147-dolphin-boot-unsigned.apk`.
Certificado original, v2/v3, todos hashes, identidades e políticas são relidos
no APK final. R143 estável e R145/R146 congeladas não são modificadas.
