# DEX R135 de saída online

`build_dex.py` produz **somente `classes35.dex`**, sobre o APK R134 exato
`f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2`.
Não monta APK, não renova runtime IDs, não assina, não instala nem acessa serviços.

## Escopo exato

A partição R134 tem SHA256
`d5a689c7e60df0d3a822f97f17a27875c7c1b38da00f44419735724d4d1dda76`
e 606 classes. Apenas as 24 classes antigas de `StationDolphinSession` e
`StationGameSession` podem ser substituídas/removidas; `StationHumanDeparture`
entra nessa mesma partição. As sintéticas de D8 somente podem pertencer às três
famílias. As outras **582 classes** são comparadas em cada arquivo projetado
por baksmali, incluindo debug info, anotações, campos, métodos e valores
estáticos explícitos. O conjunto de classes antes/depois também é conferido.

Os helpers são cópias novas da implementação R134. `AssembleScopedPartition`
restaura os arrays de inicialização estática que o assembler original poderia
aparar em classes externas; `VerifyScopedPartition` usa o escopo novo R135 e
aceita apenas DEX35/três famílias. As ferramentas/fontes históricas permanecem
intactas. O DEX montado é decodificado novamente e comparado antes do recibo.

## Programa e ferramentas

O único programa de D8 é o JAR produtivo fechado de nove classes Java8,
SHA256 `8e746f8fa449cfebae14b9db68b0080ffa9a9bfb6a45300449c4d2f7c9ce2bc4`.
O recibo de sua compilação, cada `.class` major version 52 e os três fontes
produtivos são conferidos por hashes já publicados. Esta etapa não recompila
os fontes Java. Android SDK API34 é biblioteca; rooms/client são apenas
classpath. Nenhum SDK, dependência, fixture ou classe de teste é incorporado.

D8 build-tools35 usa `--release --min-api 28 --lib ANDROID_API34`.
API28 preserva a política do donor; não eleva o requisito do aplicativo para
API34. APKtool3.0.3 e executáveis JDK17 também têm pins constantes. O compilador
JDK17 é usado somente para as ferramentas de montagem/verificação, fora do APK.
Advertências de resolução de D8 causam falha e exigem revisão.

Todos os argumentos são obrigatoriamente explícitos:

```text
python build_dex.py
  --donor EXACT_SIGNED_R134_APK
  --overlay-jar EXACT_REVIEWED_JAVA8_OVERLAY_JAR
  --compile-receipt PUBLIC_COMPILE_PRODUCTION_RECEIPT
  --jdk-bin PINNED_JDK17_BIN
  --android-jar PINNED_ANDROID_API34_JAR
  --d8-jar PINNED_BUILD_TOOLS35_D8_JAR
  --apktool PINNED_APKTOOL_3_0_3_JAR
  --rooms-jar PINNED_CURRENT_ROOMS_JAR
  --client-jar PINNED_UNCHANGED_CLIENT_JAR
  --out NEW_OR_EMPTY_PRIVATE_BUILD_DIRECTORY
  --source-commit FULL_FROZEN_SOURCE_COMMIT
```

`--check-inputs-only` valida donor, quarenta partições, classes, fontes, recibo e
ferramentas sem escrever/compilar. O commit pode ser omitido somente nesse
preflight anterior ao congelamento; nesse caso a saída declara
`sourceCommitVerified=false`. A compilação exige commit de 40 caracteres e
compara cada fonte Java/receita Python/helper e SOURCE-PINS com `git show`.
Essa verificação se repete ao final. Diretórios não vazios são recusados; nada
é apagado, sobrescrito ou movido do donor/backup/source tree.

## API do recibo para a composição superior

Saídas locais: `classes35.dex` e `dex-compilation.json`.

- `schema`: `station.online-lifecycle.dex.r135.v1`.
- `status`: `compiled-dex-payload-only`; `passed=true` somente após todos os gates.
- `sourceCommit`, `sourceCommitVerified`, `sourceSha256`, `sourcePinsSha256`,
  `sourceCanonicalSha256`: congelamento explícito dos fontes efetivos.
- `baselineApkSha256`/`baselineApkBytes`, `baselineDexSha256`: donor exato.
- `inputSha256`: programa, recibo e ferramentas/classpaths pinados.
- `inputFiles={name:{path,bytes,sha256}}`: vínculo privado dos nove inputs reais
  para reconferência pela identidade superior. Os caminhos absolutos ficam no
  recibo local e devem ser sanitizados em documentação pública.
- `partition=classes35.dex`, `changedDexPartitions=[classes35.dex]`.
- `payload={name,bytes,sha256}`: DEX aprovado a consumir.
- `preservedDexSha256`: hashes das outras 39 partições do APK R134.
- `allowedFamilies`, `originalAllowedTypes`, `finalAllowedTypes`, `addedTypes`,
  `removedTypes`, `modifiedTypes`, `d8SyntheticTypes`: delta completo, sem alias.
- `baselineClassSha256`, `outputClassSha256`, `unchangedClassSha256`: mapas
  completos de projeção por classe, com `unchangedClasses=582`.
- `unrelatedClassesByteIdentical=true`,
  `classDeltaRestrictedToAllowedFamilies=true`, `staticInitializersPreserved=true`,
  `restoredInitializerArrays`, `scopeDeclarationSha256`: gates da partição.
- `productiveJavaTarget=8`, `classMajorVersion=52`, `androidCompileApi=34`,
  `dexMinimumApi=28`: alvos distintos e explícitos.
- `productiveSourcesChanged=false`, `compileOnlyClassesPackaged=false`,
  `sdkOrDependenciesPackaged=false`, `testsOrFixturesPackaged=false`.
- `runtimeIdentityBuilt=false`, `apkAssembled=false`, `signed=false`,
  `installed=false`, `physicalGameplayValidated=false`, `productionAccess=false`.

Os hashes de classe descrevem projeção determinística baksmali, não slices
contíguos do DEX: a montagem reorganiza índices/offsets internos. O APK superior
deve preservar byte a byte as outras entradas, gerar as identidades finais pelo
contrato existente e conferir assinatura/alinhamento por sua própria receita.
Este recibo isolado não comprova funcionamento físico ou ausência de ANR.
