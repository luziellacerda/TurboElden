# Compilação isolada dos menus R134

Estas receitas produzem **três payloads**, sem montar, assinar ou instalar APK:

- `classes28.dex`: somente `StationGraphicsPanel` e suas classes internas/lambdas.
- `classes40.dex`: somente `Ps3Activity`/`Ps4Activity` e suas classes internas/lambdas.
- `lib/arm64-v8a/libturbo_carousel.so`: somente dois textos PS3/PS4, com igual tamanho.

Donor obrigatório R133: SHA `945f7ded35e551d638135a05140c32218eb38277d10eaf21e3f83087d71da112`, 2.714.971.151 bytes. As fontes históricas permanecem intactas.

## 1. Java e DEX

`build_java_payloads.py` exige:

```text
--source-commit FULL_COMMIT
--donor SIGNED_R133_APK
--jdk PINNED_JDK17
--android-jar PINNED_ANDROID34_JAR
--lambda-stubs PINNED_BUILD_TOOLS35_CORE_LAMBDA_STUBS
--d8-jar PINNED_BUILD_TOOLS35_D8
--apktool PINNED_APKTOOL_3_0_3
--client-jar CURRENT_BASE_CLIENT_CLASSPATH
--graphics-dependencies-jar CURRENT_R130_VIDEO_CLIENT_CLASSPATH
--sony-host-jar CORRECTED_R131_SONY_HOST_CLASSPATH
--bridge-jar CURRENT_R130_BRIDGE_CLASSPATH
--out NEW_ISOLATED_G_DIRECTORY
```

`--check-inputs-only` verifica inputs/fontes/commit/donor sem escrever ou compilar. Os dez hashes de ferramentas/classpaths são constantes na receita. Fontes `java/` e `recipe/` `.java/.py` são congeladas em mapa completo; cada byte é conferido por `git show` do commit explícito e novamente após compilação.

`javac` usa o bootstrap Android real e os stubs oficiais de assinatura de lambda, com `-source 8 -target 8`, sem API de bootstrap Java SE. Os jars de classes existentes ficam somente no classpath. Apenas os três fontes produtivos são programa de D8; qualquer classe de outro namespace emitida é rejeitada.

O compilador grava `java-compilation.json`, dois recibos individuais, scopes explícitos e logs privados. **38 DEX restantes** ficam registrados com seus SHAs originais.

## 2. Delta exato de classes

As versões novas de `VerifyScopedPartition.java`/`AssembleScopedPartition.java` reutilizam a projeção byte a byte de baksmali e a restauração dos inicializadores estáticos explícitos da ferramenta original. Não alteram as ferramentas congeladas anteriores.

O scope declara as famílias exatas e todos os tipos antigos/finais. Classes internas/lambdas geradas por D8 podem entrar ou sair somente dentro dessas famílias. A árvore final deve corresponder exatamente ao conjunto antigo externo mais o conjunto novo declarado. Nenhuma mudança de classe externa é admitida.

Antes da montagem e após decodificar o DEX real montado, todas as classes externas são comparadas byte a byte na projeção `localsDirective=true`, `sequentialLabels=true`, `debugInfo=true`. Os mapas completos antigo/final/externo e os tipos adicionados/removidos/modificados ficam no recibo. `classDeltaRestrictedToAllowedFamilies` qualifica essa regra; não significa que o conjunto inteiro de classes tenha permanecido igual.

## 3. Textos nativos

`patch_settings_labels.py` recebe `--donor` ou `--carousel`, e destinos novos `--output`/`--receipt` em G:. Exige a biblioteca R133 `baf0f07c89b2a0a8e788b211809c389511830805f386647461487706bcdb9709`.

Troca somente `PS3 • ABRIR EMULADOR` e `PS4 • ABRIR EMULADOR` pelos respectivos textos `CONFIGURAÇÃO`: uma ocorrência C-string completa de 22 bytes para cada texto, em segmento LOAD de leitura. O plural ultrapassaria o tamanho original e é rejeitado. A inversão deve recuperar a biblioteca inteira original. Tamanho, header ELF64/AArch64, LOAD/alinhamento16KiB e todos os bytes fora desses dois intervalos permanecem iguais.

## 4. Recibo agregado

```text
aggregate_payloads.py
  --java-receipt JAVA_COMPILATION_JSON
  --labels-receipt LABEL_PATCH_JSON
  --out NEW_G_PAYLOAD_RECEIPT_JSON
```

Schema `station.settings.refinement.payloads.v1`:

- `baseApkSha256`/`baseApkBytes`, `sourceCommit`, `sourceSha256`, `sourceCanonicalSha256`;
- `baselinePayloadSha256`, `payloads` (os três records `path/bytes/sha256`);
- `javaReceipt`/`labelsReceipt` com records exatos;
- `dexScopes`: `allowedFamilyRoots`, mapas completos `baselineClassSha256`/`outputClassSha256`, `unchangedClassSha256`, deltas e guardas;
- `preservedDexSha256` (38), `inputSha256`/`inputFiles`;
- `approvedScopes`: `graphics-settings-grouped-pages`, `sony-emulator-settings-and-return`, `native-sony-settings-action-labels`;
- inversão nativa e alinhamento16KiB confirmados; APK/assinatura/instalação/gameplay continuam falsos nesta etapa.

O agregado reverifica fontes/commit, todos os artefatos/classpaths e a inversão/reexecução exata do patch nativo. Esses recibos não comprovam ainda abertura do menu ou gameplay no Android. A identidade/runtime e o APK final são responsabilidade do pipeline superior.
