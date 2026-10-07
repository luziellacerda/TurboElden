# R66 — preparação automática da BIOS já incluída no APK

07/10/2026. TurboStations Android. **Compilada, assinada e reproduzida; ainda não instalada.** A última instalação conferida no Samsung A56 é R65. O telefone saiu da USB durante a preparação da R66.

## Causa comprovada e correção da análise anterior

A R65 integrava o lançador CD, porém sua preparação procurava firmware apenas na pasta privada de importação e em `content/neocdz.zip`. Ela não lia os recursos já presentes no APK. Por isso apresentava “Falta a BIOS” embora os arquivos corretos já existissem.

Foram encontrados e identificados estes recursos **dentro do APK R65**, sem baixar ou acrescentar firmware:

| Asset existente | Bytes | SHA-1 |
|---|---:|---|
| `assets/bios/neocd/neocd.bin` | 524288 | `7bb26d1e5d1e930515219cb18bcde5b7b23e2eda` |
| `assets/bios/neocd/000-lo.lo` | 131072 | `5992277debadeb64d1c1c64b0a92d9293eaf7e4a` |
| `assets/bios/neocd/uni-bioscd.rom` | 524288 | `5142f205912869b673a71480c5828b1eaed782a8` |

Os mesmos três SHA-1 foram lidos no telefone em `EmulationStation/.emulationstation/bios/neocd/`. A BIOS não precisava ser fornecida pelo usuário ou servidor; faltava ligar a preparação do novo lançador aos assets existentes. Essa lacuna era do cliente R65.

## Implementação

- `MameEntryActivity.prepareCd` entrega um leitor de `getAssets()` ao helper, na mesma thread de preparação já existente.
- `NeoCdSupport.prepare(..., BundledAssets)` reaproveita primeiro firmware/auxiliar válidos da pasta privada e do `neocdz.zip` junto ao disco.
- Se faltar uma dependência, lê os assets conhecidos, valida tamanho/CRC/SHA-1 e salva atomicamente na pasta privada. A seleção de firmware já importado é preservada.
- Com dependências completas, o fluxo continua para o driver CDZ e `-cdrom` da R65. Em uma abertura posterior válida não relê nem regrava os assets.
- Instalação nova ou reinstalação sem pasta privada não depende de cópia manual por ADB: o APK prepara os recursos sozinho ao abrir um CD.
- Assets ausentes/inválidos e disco inválido geram erro explícito; não ignoramos integridade nem fabricamos sucesso. Importação manual permanece como alternativa, não requisito da instalação normal com este APK.
- O overload anterior, sem assets, permanece disponível para testes e consumidores anteriores. Bibliotecas, controles, saves, configurações do emulador, carrossel, licença e código de salas não foram alterados.

## Artefato e reprodução

- Base: `TurboStations-Premium-R65-20261007.apk`, SHA `1858459b62a38a85cdd9fbeaafc68d3560008f154f99dd1431752aa0594eb081`.
- Trabalho: `E:\ESTUDO APK\work\station-neogeocd-bios-r66-20261007`.
- APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R66-20261007.apk`.
- SHA-256: **`e4397fd743c410ea060f17446706d9475b5568caad379e1a6df37672c60398d1`**; 2.093.413.965 bytes.
- DEX `classes30.dex`: **`1dcfa1e69686a326e22c54b9adc7c6013644e69d14642664e2ab7b5e2eee4ff4`**.
- Certificado: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
- Só `classes30.dex` alterado; 13.218 outras entradas comparadas integralmente/preservadas, incluindo todos os assets de BIOS. Nenhuma mídia adicionada. APK alinhado em 16 KiB.

```powershell
python recipes/build_bridge.py --work 'E:\ESTUDO APK\work\r66-repro-novo' --expected-dex 1dcfa1e69686a326e22c54b9adc7c6013644e69d14642664e2ab7b5e2eee4ff4
python recipes/test_bios.py --work 'E:\ESTUDO APK\work\r66-testes-novo' --apk 'G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R65-20261007.apk'
```

Executar a partir desta pasta, com Python e JDK17. As receitas localizam o source por seu caminho e exigem saída nova em E:. Para empacotar, copiar `recipes/package_r66.py` à raiz da saída do build; ela lê `evidence/build.json` e `dex/classes.dex`. Fornecer as quatro variáveis `STATION_KEYSTORE`, `STATION_KEY_ALIAS`, `STATION_KS_PASS`, `STATION_KEY_PASS` por ambiente, com a assinatura original. Ela exige a base exata e recusa sobrescrever o candidato existente. Não publicar chaves ou material de firmware. O snapshot contém código/receitas/recibos; o APK base é dependência externa por hash.

## Testes e limites

**66 verificações locais passaram:** 37 do helper/CLI anteriores e 29 da leitura dos assets reais do APK, incluindo pasta privada vazia, firmware importado preservado, fallback UniBIOS, limite/tamanho/identidade, ausência/corrupção, disco inválido, segunda abertura sem leitura/escrita e preservação do disco. A recompilação independente gerou DEX idêntico.

Os testes com a BIOS real usaram CHD de cabeçalho sintético para exercitar a preparação, sem emular um jogo. Não são prova de gameplay, som ou controles CD. As cópias de teste geradas em E: foram removidas após os testes; fontes/recibos permanecem. Nenhuma ROM, BIOS, APK, serial ou log pessoal está neste snapshot.

KOF '98/cartuchos e os 13 nomes de conjunto sem registro continuam na auditoria R65. Recuperação online também continua pendente; esta revisão não altera protocolo ou timers. Não declarar estabilidade geral ou os 239 jogos validados.

Para o servidor: considerar R66 ao responder o pedido NG-01–NG-07. Não pedir ao usuário firmware CD que o APK já possui, nem modificar descritores para enviar uma cópia adicional como solução para este defeito. Conferir ainda a integridade/estrutura dos discos e as pendências de cartucho; sem implantação Linux por consequência deste documento.
