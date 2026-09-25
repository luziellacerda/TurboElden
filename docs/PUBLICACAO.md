# Escopo da publicação sanitizada

Esta versão pública preserva o estudo do APK e o código decompilado que pode ser revisado sem distribuir o material sensível identificado. Os arquivos completos da análise permanecem locais. O APK original, as BIOS, as chaves e as bibliotecas nativas não foram enviados ao repositório.

## O que foi mantido

- Documentação, manifesto Android decodificado e script de leitura de catálogo local.
- Os nove Java do frontend em formato navegável e todos os 3.353 Java recuperados no arquivo JADX sanitizado.
- Os 6.198 Smali e recursos selecionados da saída Apktool.
- Recursos Android e assets de interface fora das pastas de BIOS e pacotes de sistema.
- Símbolos dinâmicos desmangleados de `libmain.so`, sem código binário, strings completas ou disassembly.
- Endpoints públicos identificados, com placeholders no lugar da chave usada no caminho do catálogo.
- Base auxiliar MAME de 38.353 pares de nomes e mapas de sistemas/cores.
- Inventário e hashes dos componentes originais, além dos checksums da entrega pública.

## O que foi omitido

| Origem | Exclusão | Motivo |
|---|---|---|
| APK original | `TurboramaStation-24-09.apk` | Preserva BIOS, chaves e bibliotecas sensíveis |
| Ambas as saídas de decompilação | `assets/bios/**` | 81 arquivos de BIOS/firmware e chaves; 38.148.111 bytes no APK desmontado |
| Dentro de `assets/bios` | `suyu/keys/prod.keys` e `title.keys` | Material de chaves; nenhum valor foi publicado |
| Ambas as saídas de decompilação | `assets/packs/**` | Pacotes de sistema/firmware, inclusive `Dolphin.zip` |
| Ambas as saídas de decompilação | `lib/**` | Oito bibliotecas nativas; o binário principal contém configuração de serviços e possíveis credenciais |
| Saída JADX | `META-INF/**` e `DebugProbesKt.bin` | Metadados de assinatura e payload binário fora do escopo do estudo publicado |
| Recursos Kotlin | `*.kotlin_builtins` | Metadados binários do runtime, omitidos da seleção publicada |
| Saída Apktool | `original/**` | Cópias de metadados/manifesto originais, dispensadas na versão pública |
| Análise nativa | `libmain-strings.txt` | Contém valores opacos e campos ligados à autenticação dos serviços; não foi feita redação parcial com garantia de cobertura |
| Análise nativa | `libmain-disassembly.txt` | Instruções e referências podem permitir recuperar valores de credenciais do binário |
| Entrega local | ZIPs completos e manifesto da entrega privada | Foram substituídos por pacotes sanitizados e checksums próprios desta publicação |

O registro de arquivos omitidos está em [`../data/exclusoes-publicacao.csv`](../data/exclusoes-publicacao.csv), com 229 registros de exclusão entre as cópias das diferentes saídas e os materiais nativos. Hashes e nomes dos arquivos omitidos podem aparecer no inventário original, mas seu conteúdo não está incluído.

## Revisão de dados sensíveis

A inspeção identificou as chaves de firmware em `assets/bios/suyu/keys` e configuração nativa relacionada a KeyAuth, TheGamesDB e ScreenScraper. A presença de um identificador de serviço não comprova que ele seja uma credencial secreta; os valores foram omitidos independentemente dessa classificação. Nenhuma credencial foi usada para testar um serviço.

Buscas textuais por campos de credenciais e formatos de chave privada em Java, Smali e recursos textuais não encontraram valores adicionais que exigissem redação nesses arquivos. Esse resultado é limitado à inspeção estática e aos padrões analisados; não é uma garantia geral de ausência de dados sensíveis. Para a parte nativa, a publicação foi limitada aos símbolos, cuja finalidade é documentar nomes e organização de funções.

Não foram incluídos `license.json`, `catalog-cache.json`, chaves de licença de usuários nem resultados de um catálogo autenticado. O CSV de servidores usa `{CHAVE}` como placeholder e não expõe uma licença real.

## Limites e procedência

A sanitização altera o conteúdo dos pacotes: eles não são equivalentes ao APK original, não preservam uma assinatura Android utilizável e não formam um projeto compilável. Os hashes originais servem para identificar o arquivo estudado; os hashes em [`../CHECKSUMS.csv`](../CHECKSUMS.csv) verificam os arquivos publicados.

O repositório não atribui uma nova licença a código, recursos ou bases de terceiros. Avisos existentes nos arquivos mantidos devem ser preservados. A documentação distingue evidência observada, inferências e verificações limitadas; disponibilidade de jogos, compatibilidade em execução e comportamento autenticado dos serviços permanecem fora do que foi confirmado.
