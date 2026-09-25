# Handoff público

Esta entrega documenta a análise estática de `TurboramaStation-24-09.apk`. O [relatório técnico](RELATORIO-TECNICO.md) descreve o APK original; o repositório contém uma seleção sanitizada dos resultados. O [registro de publicação](PUBLICACAO.md) explica as exclusões.

## Entregáveis

| Caminho | Uso |
|---|---|
| [`RELATORIO-TECNICO.md`](RELATORIO-TECNICO.md) | Arquitetura, fluxos, armazenamento, servidores, telemetria e achados |
| [`../code/frontend/`](../code/frontend/) | Nove arquivos Java do pacote `org.emulationstation.frontend`, para navegação direta |
| [`../AndroidManifest-decodificado.xml`](../AndroidManifest-decodificado.xml) | Permissões, componentes e atributos Android |
| [`../artifacts/codigo-java-recursos-sanitizado.zip`](../artifacts/codigo-java-recursos-sanitizado.zip) | 3.353 Java e recursos selecionados da saída JADX |
| [`../artifacts/apktool-smali-recursos-sanitizado.zip`](../artifacts/apktool-smali-recursos-sanitizado.zip) | 6.198 Smali de cinco DEX, manifesto e recursos selecionados |
| [`../artifacts/analise-nativa-simbolos.zip`](../artifacts/analise-nativa-simbolos.zip) | Símbolos dinâmicos de `libmain.so` e explicação do artefato |
| [`../data/servidores.csv`](../data/servidores.csv) | Endpoints, função, condição de uso e verificações da análise |
| [`../data/sistemas-suportados.csv`](../data/sistemas-suportados.csv) | Plataformas, formatos e cores, com observações sobre evidência |
| [`../data/nomes-mame.csv`](../data/nomes-mame.csv) | 38.353 pares de nomes da base auxiliar MAME |
| [`../data/inventario-arquivos.csv`](../data/inventario-arquivos.csv) | Inventário do APK original |
| [`../data/hashes-componentes.csv`](../data/hashes-componentes.csv) | Hashes dos componentes originais |
| [`../data/exclusoes-publicacao.csv`](../data/exclusoes-publicacao.csv) | Arquivos omitidos na preparação da publicação |
| [`../CHECKSUMS.csv`](../CHECKSUMS.csv) | Tamanhos e SHA-256 dos arquivos publicados |
| [`../scripts/Parse-Catalog.ps1`](../scripts/Parse-Catalog.ps1) | Leitor local do cache de catálogo para CSV |

O inventário e os hashes originais incluem referências a arquivos que não foram publicados. São evidência sobre o APK analisado, não uma lista dos arquivos presentes no repositório. Use `CHECKSUMS.csv` para conferir esta entrega pública.

## Lista real da loja

Não foi obtido o catálogo remoto. A base `nomes-mame.csv` identifica nomes conhecidos do MAME e não determina os jogos oferecidos pela loja. Para analisar uma cópia autorizada do cache do aplicativo, copie o arquivo abaixo do aparelho:

```text
/storage/emulated/0/EmulationStation/.emulationstation/store/catalog-cache.json
```

Na raiz deste repositório, execute:

```powershell
.\scripts\Parse-Catalog.ps1 -CatalogPath 'C:\caminho\catalog-cache.json' -OutputPath '.\jogos-catalogo.csv'
```

O script não consulta o servidor nem recebe a chave de licença. Ele exporta os itens reconhecidos no JSON e foi conferido apenas com uma amostra sintética. URLs contidas no cache podem ser privadas ou assinadas; o arquivo de entrada e o CSV resultante devem permanecer fora desta publicação.

## Reproduzir a análise com o APK original

Ferramentas utilizadas: JADX 1.5.6, Apktool 3.0.3, LLVM 21 (`llvm-nm`/`llvm-objdump`), Sysinternals Strings 2.54 e Android `apksig` 8.5.2. O APK, os executáveis dessas ferramentas e os resultados privados não estão incluídos.

Comandos conceituais para uma cópia local do APK:

```text
jadx --deobf --show-bad-code -d <saida-jadx> <apk>
apktool d -f -o <saida-apktool> <apk>
llvm-nm -D -C --defined-only libmain.so
llvm-objdump -d -C libmain.so
```

Esses comandos reproduzem etapas da desmontagem, não uma compilação do aplicativo. A publicação contém Smali extraído dos cinco DEX e Java gerado pelo JADX; os dois formatos não devem ser tratados como código-fonte original. Há 32 arquivos Java de terceiros com marcações de erro/método não decompilado e nenhum com essas marcações no pacote Java do frontend.

Os arquivos originais desmontados permanecem na entrega local da análise. A versão pública omite BIOS, chaves, bibliotecas e dumps nativos potencialmente portadores de credenciais; por isso não é uma cópia integral recuperável do APK. Nenhum jogo, login ou endpoint privado do catálogo foi validado em execução.
