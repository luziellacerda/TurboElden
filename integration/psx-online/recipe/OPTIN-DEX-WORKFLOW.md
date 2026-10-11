# Partições completas SDL e fábrica

`assemble_optin_dex.py` reproduz as duas partições a partir do APK R126 completo, somente leitura. Não aceita outro APK, outro JAR ou diretório de saída existente. Não monta, assina ou instala um APK.

```powershell
python -X utf8 assemble_optin_dex.py `
  --apk <APK-R126-exato> `
  --jdk <JDK17> `
  --apktool <apktool_3.0.3.jar-exato> `
  --out <diretorio-novo-temporario>
```

Os caminhos são parâmetros locais. Nenhum helper compilado de uma árvore histórica é necessário. O único JAR do classpath é o `apktool_3.0.3.jar` SHA256 `dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423` (15.478.013 bytes). Os três auxiliares Java desta pasta são compilados com o JDK17 informado para `<out>/tools`; o classpath de execução é `<out>/tools;<apktool>`. A montagem original utilizou Temurin17.0.20.1+1 no Windows. O workflow exige Windows para conservar separadores, ordenação e finais de linha do smali conferido.

## Base e sequência

APK completo: SHA256 `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d`, 2.233.970.789 bytes. A leitura confirma o arquivo inteiro e somente os dois DEX necessários; não extrai jogos ou mídias.

Para cada partição, o workflow:

1. Compila `DecodeDolphinPartition.java`, `AssembleDolphinPartition.java` e `VerifyOptinPartition.java` usando somente o JAR fixado.
2. Decodifica todos os arquivos da partição, depois confere o SHA da única classe que receberá o hook.
3. Executa `patch_sdl_optin.py` ou `patch_factory_optin.py`, que exige donor exato e inversão byte idêntica. A saída separada substitui somente aquela classe na árvore derivada.
4. Compara todas as outras classes com o donor decodificado usando `VerifyOptinPartition`, conservando a lista inteira de classes.
5. Monta a partição completa com `AssembleDolphinPartition` e confere SHA, bytes e contagem de classes do resultado.
6. Grava `complete-dex-receipt.json`, os dois recibos de hooks, os hashes das fontes e o classpath por nome/hash. Não registra caminhos pessoais no recibo agregado.

| Partição | Classes | Classes preservadas no smali | Única classe alterada | SHA256 do resultado |
|---|---:|---:|---|---|
| classes6.dex | 50 | 49 | org.libsdl.app.SDLActivity | 61ff49b6253a9f31f0519c2517a6b2b5b55c5af53c529cfd728bd052f0c5dacb |
| classes28.dex | 271 | 270 | org.emulationstation.frontend.station.StationComponentFactory | 5966ef8405701fa946c60fe6d922726cd74c27783a4cb76d240dfa4bc324de9d |

A comparação byte idêntica se refere ao smali das classes preservadas. A remontagem pode mudar índices e ordem no DEX. As classes Java novas da integração PSX são compiladas separadamente; estes DEX conservam seu conjunto original e não devem receber definições duplicadas. `DecodeOneClass.java` é um auxiliar de inspeção e não participa deste workflow completo.

Os resultados já conferidos estão em `evidence/complete-dex-receipt.json`. Esta entrega completa a receita; não executa novamente a montagem nem representa teste Android, gameplay ou instalação.
