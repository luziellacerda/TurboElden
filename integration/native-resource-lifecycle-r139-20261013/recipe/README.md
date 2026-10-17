# Receita de montagem R139

Base imutável: APK R138 SHA256 `9183462e4d45cfcf2d2599d9e682b81890fee7b094505bf3073ab8183dd1dd10`. Runtime de referência `463bdb0b409e028aa34f6c9a09d291a3715ffb3eacb8f18ee28843e7373eb80f`.

O único arquivo nativo permitido é `frontend/drivers/platform_unix.c`, sobre a versão R138 SHA256 `e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2`. O overlay final deve estar em `native/source/frontend/drivers/platform_unix.c`. O compilador usa o mesmo arquivo completo de fontes de cinco jogadores, NDK r28c, API26, flags e época de compilação da R138. Primeiro recompõe a R138 e confere código, dados, regiões de carga e relocations; somente `.comment` e identidade GNU podem diferir. Depois copia o overlay R139 e exige que todos os outros arquivos continuem exatos.

```text
python recipe/build_native_r139.py --delivery INPUTS_FIVE_PLAYER --work ABSOLUTE_NEW_BUILD_DIRECTORY --ndk NDK_R28C --baseline-runtime EXACT_R138_SO --mode baseline
python recipe/freeze_r139_sources.py --source-commit FROZEN_GIT_COMMIT --out NEW_NATIVE_SOURCE_FREEZE_JSON
python recipe/build_native_r139.py --delivery INPUTS_FIVE_PLAYER --work SAME_BUILD_DIRECTORY --ndk NDK_R28C --baseline-runtime EXACT_R138_SO --mode candidate --overlay integration/native-resource-lifecycle-r139-20261013/native/source/frontend/drivers/platform_unix.c --source-freeze NATIVE_SOURCE_FREEZE_JSON
```

O congelamento é preparado antes da fase candidate, vinculando o commit, a fonte nativa e os arquivos de suporte por papel. A fase candidate grava `candidate.so` e `candidate.json`, referenciando o SHA256 desse congelamento. O builder confere o inventário integral de fontes contra o arquivo original mais o overlay R138 e exige apenas uma diferença na candidata. `--jobs` limita somente a compilação local; seu padrão é quatro e o máximo é seis.

```text
python recipe/package_r139.py --baseline EXACT_R138_APK --runtime CANDIDATE_SO --runtime-sha EXPLICIT_CANDIDATE_SHA256 --runtime-receipt CANDIDATE_JSON --source-freeze NATIVE_SOURCE_FREEZE_JSON --out ABSOLUTE_NEW_ASSEMBLY_DIRECTORY
python recipe/verify_apk_r139.py --baseline EXACT_R138_APK --work SAME_ASSEMBLY_DIRECTORY --candidate CANDIDATE_APK --candidate-sha EXPLICIT_APK_SHA256 --receipt NEW_VERIFICATION_JSON
```

A embalagem muda exatamente `lib/arm64-v8a/libstation_retroarch.so` e `assets/station-online/engines.json`: nove descritores recebem o hash e o sufixo do novo runtime, mantendo oito ativos e Geolith inativo. Todas as opções HLE, capacidades por jogo, perfis, dispositivos, protocolos e os quatro owners independentes PSX/N64/GameCube/Wii ficam iguais. São exigidas 13.858 outras entradas e todos os 40 DEX byte idênticos. Os três wrappers R137 são conferidos por seus fingerprints; seus mapas não vinculam as duas entradas substituídas.

`unsigned.package.json` conserva o mapa completo de hashes escrito pelo montador, sem substituí-lo pelo resumo retornado. A verificação adicional percorre cada entrada do APK com hash real e pode ser usada depois de alinhamento/assinatura. O recibo distingue verificação de conteúdo, assinatura, alinhamento, instalação e gameplay. Estas receitas não assinam, instalam ou acessam o servidor.

Os oito registros ativos com IDs novos precisam de cadastro administrativo no servidor e de resposta assinada fresca pelo contrato existente v3. Esta atualização não cria endpoints e não altera autenticação, READY/ACK, geração, perfis ou elegibilidade de modos. Publicar fontes/recibos não confirma cadastro ou implantação.

Teste de escopo sem criar APK:

```text
python tests/test_package_scope.py --baseline-apk EXACT_R138_APK --receipt NEW_SCOPE_TEST_RECEIPT
```
