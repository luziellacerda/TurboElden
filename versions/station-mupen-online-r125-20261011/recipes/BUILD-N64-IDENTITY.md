# Montagem N64 Station R125

O APK de entrada é a R124 exata, SHA256 `aeeb2f8167a442db5a58b990cf6d45b613fab42b1e7a9bbc0bf3214b260420c4`. A biblioteca online tem SONAME próprio e não substitui o core Mupen offline. Compilar com `build_native.py`, fonte AE `33bf7021549d7873e976884370fbd1a8e7333bc7` e NDK r28c. O recibo precisa indicar 79 fontes compiladas, zero objetos reaproveitados e alinhamento LOAD de 16 KiB.

## Identidade após congelar fontes

Primeiro finalizar Java, hooks smali, DEX35, DEX36 e manifesto AXML. Nenhum payload preliminar pode ser apresentado como compilação final.

```
python build_runtime_identity.py freeze --base <R124.apk> --core <libstation_mupen64plus_core.so> --upstream <AE original> --payload classes35.dex=<DEX35 final> --payload classes36.dex=<DEX36 final> --payload AndroidManifest.xml=<AXML final> --out <G R125/freeze.json>
python build_runtime_identity.py build --base <R124.apk> --freeze <freeze.json> --ndk <NDK r28c> --out <G R125/runtime novo>
```

A receita confere os sete arquivos do overlay contra as fontes realmente usadas na compilação. O fingerprint inclui as fontes Java/native/smali, o core completo, DEX/AXML finais, as opções exatas de `StationN64Launch` e o fechamento das 12 dependências reais carregadas pelo AE. Não inclui caminhos privados ou horários. Se qualquer fonte ou payload mudar após o freeze, a receita recusa gerar ou empacotar uma identidade antiga.

`libstation_mupen64plus_runtime.so` expõe somente a identidade e seu manifesto. Não executa um jogo, não confirma READY e não substitui o emulador. É compilada para AArch64/API23 e alinhamento 16 KiB. Seu hash final forma um ID novo de engine. O protocolo de recuperação continua `station-stream.v3`, com wire Mupen `SN64/1`, máximo de quatro portas e perfil `direct-four-ports-v1`. A recuperação para o fluxo de inputs durante reconexão; não implementa rollback de savestate.

O asset resultante substitui somente a entrada N64 parallel antiga, na mesma posição. As outras dez entradas e políticas permanecem iguais. Isso evita que o filtro que seleciona a primeira engine ativa encontre um N64 legado antes da nova engine. O servidor deve registrar o ID, core/runtime, opções e perfil novos; nenhum ID antigo é reutilizado ou aceito como alias.

## APK unsigned

```
python package_r125.py --base <R124.apk> --freeze <freeze.json> --runtime-dir <runtime novo> --out <G R125/candidato-unsigned.apk>
```

Quatro entradas podem mudar: AndroidManifest.xml, classes35.dex, classes36.dex e assets/station-online/engines.json. Só duas entradas são acrescentadas: as bibliotecas Station Mupen de core/runtime. O montador conserva e confere os hashes de todas as outras entradas, incluindo emuladores offline, plugins, mídias e recursos. Remove somente os metadados da assinatura anterior. Não assina, alinha ou instala; esses passos precisam usar a assinatura já autorizada, verificar o mesmo certificado e preservar dados do telefone.

Os recibos de geração/ELF/identidade não demonstram gameplay. Testes físicos ainda precisam confirmar bootstrap, dois aparelhos, portas 2–4, controle externo, reconexão e saída humana. Uma identidade compilada não significa registro já ativo no servidor.
