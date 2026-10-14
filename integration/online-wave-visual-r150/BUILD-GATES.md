# Portões de montagem R150 sobre a R149 assinada

Este é o plano de produção; a inspeção atual não compilou nem instalou a R150.
Iniciar a montagem apenas depois da instalação e do teste funcional da R149 e
da verificação de espaço no aparelho de teste. Congelar as receitas R150 em um
novo commit antes de gerar artefatos finais.

## 1. Doadores e sobreposições

- Exigir APK R149 assinado SHA-256
  `698e8a7914cc7be2facc00e6701ff1f3533fa13f763358b51578a35d25c2741e`,
  2.715.089.935 bytes, 13.860 entradas.
- Exigir DEX10 SHA-256
  `1f1b285af161fbf85573c081bee3bc6e4c95f90485d8d405ae064b86feb9144e`
  e `libmain.so` SHA-256
  `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6`.
- Validar os sete cabeçalhos nativos preparados em `native-rebased` e
  `snes-cover-rebased` contra os `outputSha256` dos dois recibos. Colocá-los
  juntos em uma única camada de include prioritária, mais o cabeçalho
  `r132_native_info.h` R148 SHA-256
  `af31da6851bb2ce6742aca553b361fdb5beccab87c68a4874a6c6febbb89b0b6`.
  Nenhuma entrada privada, arte JPEG ou caminho de máquina vai para o Git.

## 2. Reproduzir e alterar o carrossel

- Verificar novamente os 158 inputs e comando nativos originais R145. Compilar
  a base e reproduzir o carrossel anterior R145/R147 byte a byte; aplicar o
  cabeçalho R148 e reproduzir o carrossel R149/R148 SHA-256
  `313de078f8c300b6c7944de2ce03292de697532bc1a493b7406fdbb8260fbd28`.
- Em compilação separada, injetar os sete cabeçalhos visuais e o mesmo
  `r132_native_info.h`. Aplicar o patch de rótulos histórico. Verificar
  exports, dependências ELF, SONAME e alinhamento 16 KiB iguais aos anteriores.
  Conferir que sinopses dos jogos/coleções permanecem e a sinopse dos sistemas
  segue oculta. Apenas `libturbo_carousel.so` pode mudar nesta etapa nativa.

## 3. DEX visuais de origem R149

- Usar `recipe/patch_dex_binary.py` sobre o APK R149 exato com o oráculo
  `dex-r149-direct`. Ele localiza dinamicamente sete classes/métodos e dez
  instruções `const` 31i. O verificador Java/dexlib2 pinado percorre as
  fronteiras reais de cada instrução e confirma offset, opcode, registrador e
  literal antes e depois; uma sequência parecida dentro de operando ou payload
  não serve como alvo. Muda apenas os dez imediatos de cor e os cabeçalhos
  de integridade de `classes28.dex`, `classes35.dex` e `classes40.dex`.
- Os SHA-256 previstos em inspeção somente leitura são, respectivamente,
  `a93a7257257cdd36841c6b8990b957a756ee3635f39a47881ba09c5b08d080bf`,
  `ede5309d31dd44910d4e5b841604ab5fe3e1129ba693d7ee490ad0974047efbc`
  e `e5f74abfb3ec7e182dacbf16db56a968c6fc62af8a098f16a729ffe2fe7bc282`.
  A inversão de cada partição precisa recuperar a R149 byte a byte.
- Depois de gravar os três DEX, decodificá-los com o decodificador pinado e
  comparar as sete classes completas ao oráculo smali. Comparar as demais
  classes e todos os outros bytes das três partições ao doador R149. Os outros
  37 DEX, sobretudo `classes10.dex`, devem permanecer byte a byte iguais.

## 4. Identidade, APK e assinatura

- Os três marcadores de motor vinculam 345 hashes. Atualizar nessa lista
  somente o carrossel e os DEX 28/35/40; manter os outros 341 hashes, inclusive
  DEX10, iguais à R149. Recompilar os marcadores com as mesmas políticas e gerar
  quatro novos IDs para PSX, N64, GameCube e Wii em `engines.json`. Os IDs
  literais R149 não podem ser reutilizados com payloads R150 diferentes.
- O APK sem assinatura e o assinado devem alterar **exatamente oito** das
  13.860 entradas R149: carrossel, DEX 28/35/40, três marcadores e
  `engines.json`. Confirmar SHA de todas as 13.860 entradas, 13.852 preservadas,
  37 partições DEX preservadas, 13 registros de motor com nove descritores
  RetroArch iguais, `libmain.so` igual e DEX10 igual.
- Assinar com a autoridade original, exigir certificado SHA-256
  `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`,
  esquemas v2/v3, alinhamento 16 KiB e leitura integral pós-assinatura.

## 5. Kit e backup

- Preparar kit privado R150 correspondente aos quatro novos IDs e hashes do
  APK assinado. Exigir seis ELF, vinte dependências, os mesmos 78 modos
  revisados, zero nova aprovação PS1 HLE e políticas idênticas. Marcar
  `serverApplied=false` até retorno verificável do servidor.
- Copiar APK assinado, kit e comprovantes para backup privado incremental em
  F:, com hash de origem e destino. Copiar também a referência de arte Chrono
  Trigger fornecida pelo usuário, SHA-256
  `fefec62a6a3a3933973a695764321050952130a263f7a71f02ed47a9276b9f09`,
  apenas para a pasta privada de provas. A arte não integra APK, kit ou Git.
- Instalar somente quando o aparelho estiver livre de partida/download e tiver
  espaço suficiente, preservando dados. Testar tela principal, sala online,
  SNES e jogo GameCube offline. O teste R149 antecede esta instalação.
