# Montagem atual R127

`recipe/assemble_apk.py` prepara a atualização sobre a base R126 exata:

`F:\TurboStations-Backup-Completo-20261011\desenvolvimento\bases-necessarias\TurboStations-Premium-R126-20261011.apk`

SHA256: `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d`.

Destino final assinado previsto:

`F:\TurboStations-Backup-Completo-20261011\desenvolvimento\TurboStations-Premium-R127-20261011.apk`.

A base e o instalador R124 do backup não são sobrescritos. Unsigned/alinhado são temporários necessários da única árvore de trabalho; não são novas bases congeladas. A receita não assina nem instala.

## Alterações permitidas

Substitui somente:

- `AndroidManifest.xml`
- `classes6.dex`
- `classes28.dex`
- `classes35.dex`
- `assets/station-online/engines.json`
- `lib/arm64-v8a/libstation_mupen64plus_runtime.so`
- `lib/arm64-v8a/libstation_dolphin_runtime.so`

Adiciona somente `lib/arm64-v8a/libstation_psx_online.so`.

Os dados de assinatura v1 antigos (`META-INF/MANIFEST.MF` e arquivos `.SF/.RSA/.DSA/.EC` diretamente em META-INF) são removidos. Outros arquivos de META-INF são preservados. O bloco de assinatura v2/v3 original não é copiado na reconstrução ZIP.

Todos os demais conteúdos descomprimidos permanecem idênticos, inclusive owner/core PSX normais, SDL, cores N64/Dolphin, seus plugins/hooks, DEX10/12/36, SNES/Mega Drive, mídias, configurações e economia. Não se promete identidade dos bytes comprimidos nem dos offsets: a montagem e o alinhamento podem mudá-los.

## Ordem de execução

1. Congelar as fontes produtivas e os quatro payloads de DEX/manifesto reais. `build_runtime_identity.py` vincula as fontes/transformações produtivas e esses payloads aos três runtimes. Receitas e fontes produtivas devem estar concluídas antes dessa identidade; documentos/provas não entram no fingerprint.
2. Gerar `runtime-identity.json` schema3, fingerprints canônicos, engines e bibliotecas. A PSX usa o core normal, duas portas Standard, PXL1 e atraso de entrada canônico de quatro quadros. N64/Dolphin recebem novos marcadores por causa dos DEX/manifesto compartilhados, mantendo seus cores e opções.
3. Criar o manifesto de montagem com `--write-freeze`, fornecendo os oito `--payload nome=arquivo` exatos e `--identity-receipt`. O manifesto só é escrito depois de validar os arquivos, fontes, fingerprints embutidos e engines. Ele contém `schemaVersion:1`, `revision:R127`, `sourceFrozen:true`, `baseApkSha256`, `identityReceiptSha256` e o mapa `payloads` com `path/sha256/bytes`.
4. Executar `--check-inputs`. Esse modo não grava APK nem altera arquivos.
5. Executar a montagem com `--out` novo. A receita usa streaming em blocos de 1MiB, conserva ordem, comentário e metadados das entradas existentes, proíbe ZIP64 e duplicatas, lê novamente cada entrada e compara SHA256. Revalida fontes e payloads ao terminar.
6. Alinhar o unsigned com a ferramenta Android real (`zipalign -P 16 -f 4 unsigned.apk aligned.apk`). Assinar o aligned com a mesma chave local já autorizada, preservando o certificado abaixo; credenciais nunca entram na receita, no Git ou nos recibos públicos.
7. Executar `recipe/verify_final.py` com o APK assinado e as ferramentas reais. O verificador chama `java -jar apksigner.jar verify --verbose --print-certs` e `zipalign -P 16 -c 4`; exige assinatura v2/v3 e o certificado original, além de conferir novamente todas as entradas e dependências.

Certificado exigido: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

`profile.json` mantém `launchReady:false` como estado da política ainda sem validação física/ativação. O asset de engines da candidata compilada pode conter `launchReady:true` para reconhecer o backend implementado. Isso não comprova cadastro ou ativação na produção. O início continua dependendo do contrato autenticado, da identidade exata e da aprovação individual de jogo/modo para a política HLE e as duas portas Standard deste frontend normal. Não habilita multitap nem quatro jogadores por capacidade genérica da plataforma.

Parâmetros de montagem:

```text
assemble_apk.py --base BASE_R126 --freeze FREEZE_JSON --identity-receipt RUNTIME_JSON --write-freeze
  --payload AndroidManifest.xml=AXML
  --payload classes6.dex=DEX6
  --payload classes28.dex=DEX28
  --payload classes35.dex=DEX35
  --payload assets/station-online/engines.json=ENGINES_JSON
  --payload lib/arm64-v8a/libstation_mupen64plus_runtime.so=N64_MARKER
  --payload lib/arm64-v8a/libstation_dolphin_runtime.so=DOLPHIN_MARKER
  --payload lib/arm64-v8a/libstation_psx_online.so=PSX_RUNTIME

assemble_apk.py --base BASE_R126 --freeze FREEZE_JSON --identity-receipt RUNTIME_JSON --check-inputs
assemble_apk.py --base BASE_R126 --freeze FREEZE_JSON --identity-receipt RUNTIME_JSON --out UNSIGNED_APK

verify_final.py --base BASE_R126 --apk FINAL_APK --freeze FREEZE_JSON --identity-receipt RUNTIME_JSON
  --receipt LOCAL_VERIFICATION_JSON --java JAVA_EXE --apksigner-jar APKSIGNER_JAR --zipalign ZIPALIGN_EXE
```

Cada token de arquivo acima é um argumento separado; em PowerShell usar arrays de argumentos para preservar espaços dos caminhos. As receitas recusam sobrescrever APKs, freezes e recibos existentes.

## Evidência e limites

A prova `tests/package_probe.py` usa seis casos de ZIPs sintéticos pequenos: conjunto fechado, assinaturas, streaming, duplicatas/ZIP64/extras, EOCD e preservação por montagem. Não usa nem monta APK real, não testa uma identidade final de runtime, não verifica assinatura Android e não opera telefone. O agregado público está em `evidence/package-probe.json`.

A base R126 foi lida: 13.559 entradas, ZIP clássico válido, sete substituições presentes e a biblioteca PSX nova ausente. Isso não é montagem R127.

O `.package.json` completo fica junto ao unsigned local privado, pois contém o mapa de hashes de todas as entradas. Não publicar esse manifesto completo de mídia/ativos privados. Publicar apenas agregados, hashes selecionados dos motores/fontes e resultados efetivos. Compilação, assinatura e instalação são estados separados; nenhum recibo declara ativação do servidor, estabilidade ou gameplay físico sem evidência real.
