# Receita R129

Esta receita não assina, instala nem promove um APK. O finalizador separado só
pode consumir `unsigned.apk` após o recibo `unsigned.package.json` conferir o
hash integral, o freeze e a identidade. A assinatura mantém o certificado já
instalado; `verify_final.py` confere o APK assinado real antes da promoção.

## Entradas preservadas

- Base de montagem: APK R126, SHA-256
  `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d`.
- Doador de DEX e prova dos payloads: APK R128, SHA-256
  `0189527c7537845562a2be4be15c0fab976c85f4f9c7f8ab884915c8bc3052dc`.
- `parent-offline-receipt`: recibo exato
  `integration/ps3-ps4-offline/evidence/offline-payloads.json`.
- `parent-offline-payloads`: diretório privado dos quatro payloads originais R128
  com nomes `AndroidManifest.xml`, `classes28.dex`, `classes39.dex` e
  `libturbo_carousel.so`. Todos são conferidos contra o recibo antes da identidade.
- `java-receipt`: recibo da compilação completa PSX/R124/R125/R126 com o
  `classes35Sha256` R128 preservado. As 206 fontes efetivas são reconferidas.
- `ndk` no construtor de identidade é a **raiz** do NDK. Já o construtor de
  payloads recebe em `--ndk` o diretório `toolchains/llvm/prebuilt/windows-x86_64/bin`,
  como a receita offline congelada.

## Sequência

Substitua os argumentos entre `<...>` pelos arquivos e diretórios privados atuais.
Os diretórios de saída devem ser novos, isolados das fontes. Não altere nenhum
arquivo Java/Python da integração durante ou depois da compilação.

```text
python -B integration/local-sony-demos/recipe/build_demo_payloads.py --donor <APK_R128> --jdk <JDK17> --android-jar <ANDROID_JAR> --d8-jar <D8_JAR> --apktool <APKTOOL_3_0_3_JAR> --parent-offline integration/ps3-ps4-offline --ndk <NDK_BIN> --native-inputs <INPUTS_NATIVOS_R124> --out <DEMO_PAYLOADS>

python -B integration/local-sony-demos/recipe/build_unsigned.py build --base <APK_R126> --donor <APK_R128> --ndk <NDK_ROOT> --java-receipt <RECIBO_JAVA_PSX> --parent-offline-receipt integration/ps3-ps4-offline/evidence/offline-payloads.json --parent-offline-payloads <PAYLOADS_R128_ORIGINAIS> --demo-receipt <DEMO_PAYLOADS>/demo-payloads.json --demo-payloads <DEMO_PAYLOADS> --out <ASSEMBLY>

python -B integration/local-sony-demos/recipe/build_unsigned.py check-unsigned --base <APK_R126> --assembly <ASSEMBLY>
```

`build_unsigned.py build` executa, em sequência:

1. Conferência integral do doador R128 e dos seis payloads compartilhados originais.
2. Extração apenas dos DEX6/35 preservados para o diretório da montagem.
3. Conferência dos quatro payloads e fontes congeladas R128 e dos três novos
   payloads da demonstração, com a prova de reprodução nativa R128.
4. Renovação somente das quatro identidades existentes PSX/N64/GameCube/Wii.
   Cores, opções, perfis, capacidades e protocolo permanecem idênticos à R128.
5. Freeze das fontes completas PSX + offline R128 + demonstrações locais.
6. Montagem dos mesmos dez payloads do overlay R128 sobre a base R126,
   conferência de todas as entradas preservadas e leitura independente do resultado.
7. Gravação de `source-freeze.json`, `identity/runtime-identity.json`,
   `unsigned.apk`, `unsigned.package.json` e `pipeline-unsigned.json`.

O overlay modifica DEX28/39 e o fallback de arte Sony no carousel; preserva
Manifest/DEX6/DEX35. As bibliotecas dos emuladores normais e os demais arquivos
do APK são comparados byte a byte. PS3/PS4 permanecem **somente offline**;
demonstrações locais não são jogos nem entradas novas do catálogo assinado.

## Verificação após assinatura pelo finalizador

```text
python -B integration/local-sony-demos/recipe/verify_final.py --base <APK_R126> --apk <APK_ASSINADO> --freeze <ASSEMBLY>/source-freeze.json --identity-receipt <ASSEMBLY>/identity/runtime-identity.json --receipt <ASSEMBLY>/verified-final.json --java <JAVA_EXE> --apksigner-jar <APKSIGNER_JAR> --zipalign <ZIPALIGN_EXE>
```

A importação pública `assembler()` de `assemble_apk.py` mantém compatibilidade
com `tooling/release/finalize_verified.py`. O recibo final informa R129 e não
declara instalação, ativação de servidor ou gameplay físico validado.
