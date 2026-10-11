# Composição Sony interna

Este diretório prepara os recursos privados e fornece a extração comum dos owners PS3 e PS4. Os owners e a nova Factory são fontes separadas. O ponto de partida é o APK R130 exato; a composição deve preservar integralmente seus 39 DEX, bibliotecas existentes, recursos, vídeos, LEDs, cache, controle, assinaturas e dados. Os novos hosts entram em um DEX adicional. A Factory nova intercepta o componente Sony já declarado e delega todos os demais componentes à Factory atual. Nada neste diretório altera o renderer ou inicia trabalho no frontend.

## API dos owners

Pacote `org.emulationstation.frontend.sony`:

| API | Contrato |
| --- | --- |
| `StationSonyAssets.prepare(Context, system, expectedManifestSha256)` | Prepara/verifica o módulo em worker, somente no processo `:station_ps3` ou `:station_ps4` correspondente. |
| overload com `StationSonyAssets.Progress` | Recebe o progresso no mesmo worker; não cria executor, serviço, polling ou callback na UI. |
| `Prepared.nativeDirectory()` | Diretório privado das bibliotecas exatas; pode ser o nativeLibrarySearchPath do classloader filho PS4. |
| `Prepared.nativeFile(basename)` | Somente um arquivo declarado e preparado. |
| `Prepared.assetFile(relative)` | Asset original relativo, por exemplo `config/config.yml`, `runtime/runtime.zip` ou `derived/owner.dex`. Um único prefixo `assets/` também é aceito. |
| `StationSonyAssets.loadNative(Prepared, basename)` | PS3: carrega dependências privadas Bionic em ordem e depois a entrada. Não carrega hooks por conveniência. |
| `StationSonyAssets.nativeLoadPlan(Prepared, basename)` | Retorna `File[]` ordenado e validado sem carregar. O bootstrap **definido no classloader filho PS4** executa `System.load` desses paths, preservando o contexto de `JNI_OnLoad/FindClass`. |

As constantes `StationSonyAssetPins.PS3_MANIFEST_SHA256` e `PS4_MANIFEST_SHA256` são fontes geradas no preparo privado. Devem ser compiladas com o host somente depois de congelar o owner DEX e os demais inputs.

Cada módulo usa `no_backup/station-sony/<system>/<moduleId>`. Caminhos relativos são fechados, symlinks são recusados, cada arquivo tem lock próprio, SHA-256 e tamanho exatos, estágio atômico e permissão somente leitura. Uma chamada no thread principal é recusada. Arquivos verificados ficam em cache somente dentro do processo; a primeira chamada de um novo processo verifica seus bytes. Não há acesso a disco por frame nem tarefas permanentes. A cópia/verificação inicial tem custo de I/O e espaço e não é prova de menor consumo.

## Inputs privados

O builder recusa APKs diferentes dos dois originais auditados:

| Sistema | APK | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| PS3 | aPS3e 2.43 | `c5a58fb056ae333b8bd6ed69e6bfacdd1e5bf7e0ac2134456a0622bd94a3e466` | 40122859 |
| PS4 | Bachata S4 0.2.4 GitHub | `4077b0d0b80e354c71eff1ce2c003f122449ac266eb27a6ac26744d3f9809a08` | 207779222 |

Os originais estão no backup único, em `desenvolvimento/emuladores-oficiais-current`. A receita confere os bytes integrais do APK; os certificados publicados no recibo são os auditados anteriormente, não uma nova verificação de assinatura feita pela receita.

O mantenedor autorizou explicitamente acrescentar o firmware PS3 4.93 e o material PKG comum PS4 **somente ao APK local**. O PUP privado tem SHA-256 `158471fd834f8ea8036136b6aab43cd86c7ba73d79ca30e0af3c0fe0001cf365`, 206197916 bytes. Ele entra em `sony/ps3/upstream/PS3UPDAT.PUP`; o owner usa `assetFile("PS3UPDAT.PUP")` e o importador nativo real. Nenhum conteúdo de firmware, chave, APK, jogo ou log pessoal pertence ao Git.

O input `--ps4-derived` é JSON privado com:

```json
{
  "schema": "station.sony.ps4.derived.v1",
  "sourceApkSha256": "4077b0d0b80e354c71eff1ce2c003f122449ac266eb27a6ac26744d3f9809a08",
  "files": [
    {"path": "upstream/derived/owner.dex", "file": "<arquivo privado>", "bytes": 0, "sha256": "<hash real>"},
    {"path": "upstream/derived/pkg-rsa.bin", "file": "<arquivo privado>", "bytes": 0, "sha256": "<hash real>"}
  ]
}
```

Os números acima são esquema, não recibo válido. As duas linhas reais são produzidas pela receita do owner PS4. O descriptor vincula path lógico/bytes/hash e a origem auditada; paths físicos não mudam a identidade ao reproduzir em outra pasta. O hash do JSON original fica no recibo privado de preparação. O DEX filho isola as classes SDL3/PS4 necessárias, sem importar o DEX completo do emulador nem alterar as classes SDL2 existentes na Station.

## Receita e contrato da montagem

`recipe/prepare_assets.py` oferece:

```text
prepare(ps3_apk: Path, ps4_apk: Path, out: Path,
        ps4_derived: Path, ps3_firmware: Path) -> dict
```

CLI: `--ps3-apk`, `--ps4-apk`, `--ps4-derived`, `--ps3-firmware`, `--out`; todos são obrigatórios. `out` deve ser uma pasta privada nova ou vazia. A receita não assina, instala, modifica inputs, escolhe uma versão por data nem apaga outputs anteriores.

Saídas:

- `assets/sony/{ps3,ps4}/module.json`: descriptor fechado, schemaVersion 1, pins completos e moduleId derivado do conjunto real.
- `assets/sony/<system>/native/<basename>`: todas as bibliotecas originais, sem renomear ou alterar bytes.
- `assets/sony/<system>/upstream/<path>`: assets selecionados e originais/derivados privados.
- `generated-java/org/emulationstation/frontend/sony/StationSonyAssetPins.java`: pins a compilar no host novo.
- `sony-assets.json`: mapa `payloads` com nomes finais ZIP, paths privados, SHA-256 e tamanho, detalhes ELF e origem de cada módulo. Não é recibo de APK nem de gameplay.

A seleção original PS3 contém sete libs e 62 assets: configuração, notices, patch disponível e 59 ícones RPCS3. São 69 arquivos/65972150 bytes, antes do PUP privado. `patch.yml` é preservado, mas sua aplicação por jogo não é adivinhada. PS4 contém 16 libs e 209 assets: runtime ZIP/manifest/native manifest, notices e repositório de patches; 225 arquivos/201420150 bytes, antes dos dois derivados. A base de catálogo de 117 MB, drivers alternativos e perfis dexopt do APK estrangeiro são omitidos porque não são usados pelo owner mínimo. Recursos gráficos do launcher estrangeiro não são mesclados.

O empacotador final deve acrescentar **exatamente** o mapa de payloads selado, mais os novos DEX/Manifest definidos pela composição, conferir todos os bytes herdados do R130 e vincular o source freeze a cada receita/owner/arquivo gerado. O mesmo certificado e as mesmas pastas Station permanecem. Novos compartilhados exigem os marcadores online atuais serem reavaliados pelo procedimento próprio; isto não cria suporte online Sony.

## Loader e limites verificados

`System.load(path absoluto)` não isola sozinho `DT_NEEDED`. A receita fecha o grafo privado Bionic por SONAME e sistema; o helper recusa SONAME já mapeado de outro path. PS3 usa seus `lang_System`, `hardware_ProcessorInfo` e `libe` originais no processo próprio. PS4 usa seu `libc++_shared` original **antes** de seus módulos no classloader próprio. A libc++ da Station não é substituída.

`libXss.so`, `libbachata_host_loader.so` e `libxkbcommon.so` são GLIBC, não Bionic. São preservados como arquivos privados, mas nunca incluídos no plano `System.load`. O owner deve seguir o ramo nativo real auditado; não há fallback genérico para carregá-los.

A leitura dos PT_LOAD reais confirmou alinhamento de 16 KiB em todas as bibliotecas Bionic e 64 KiB nos três artefatos GLIBC. A receita guarda alinhamento e congruência de cada segmento. Isso descreve os ELF originais, sem afirmar validação em dispositivo de página 16 KiB, bootstrap concluído, firmware importado, emulação, qualidade ou estabilidade.

Fontes PS3/JNI foram localizadas no upstream; a correspondência entre fonte pública e binário completo não foi reconstruída aqui. As fontes Android/frontend completas do release Bachata continuam ausentes do portal auditado; o core público e os notices não provam que todo o binário seja recompilável. A integração local preserva os originais e seus avisos; não declara que substituiu toda a implementação por fonte própria ou resolveu obrigações de distribuição pública.
