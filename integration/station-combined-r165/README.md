# R165 combinada — preparo sem APK

Esta receita congela uma futura candidata única sobre o APK assinado R164,
SHA-256 `903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210`.
Ela ainda **não** é um APK, não foi assinada, instalada, cadastrada no servidor
nem validada em partida física. A R164 permanece como retorno estável.

## Escopo permitido

Se o retorno PSX não pedir código novo, somente seis entradas do APK podem
mudar: `classes35.dex`, `lib/arm64-v8a/libturbo_carousel.so`,
`assets/station-online/engines.json` e os três marcadores de runtime PSX,
N64 e Dolphin. As demais 13.855 entradas, inclusive `classes36.dex`, os
núcleos, as pontes online/offline e o frontend, devem ficar byte a byte iguais.
O DEX35 API26 já aprovado é o da receita `n64-host-exit-r165`, commit
`68fe58dadbf33538b7ad1607c88af80a7a3fc0fe`. O commit da presente receita
e das fontes visuais deve ser outro e é fornecido em `--source-commit`.

A biblioteca visual futura é passada por `--native`. Ao lado dela, exige-se
`native-receipt.json` com esquema `station.r165.selection-native.v1`,
`sourceLibrarySha256` igual ao carrossel R164, `sourceReceiptSha256` igual ao
recibo nativo R164, `outputSha256` da nova biblioteca, `passed`, `abiPreserved`,
`compilerWarningsUnchanged` e `effectRoutingAudited` verdadeiros,
`extraPerFrameDrawCalls` e `newTimersThreadsHeapAllocations` iguais a zero,
e `sourceFilesSha256` contendo os caminhos Git de todas as receitas produtivas
da largura e do Mega Drive. A receita confere cada fonte contra o commit
congelado e compara exports, dependências, SONAME e alinhamento ELF de 16 KiB.
O recibo deve nascer de auditoria real; não preencher campos por suposição.

## Prévia sem montagem

Depois de congelar as fontes num commit, executar `package_candidate.py`
com `--base`, `--dex-dir`, `--source-commit` e `--check-inputs-only`. Sem
`--native`, a prévia informa `nativePending=true` e valida doador/DEX. Com
`--native`, valida também recibo, fonte e ABI. Essa operação não cria APK.
`--ndk` e `--out` são exigidos somente para a montagem futura; a saída deve
ser diretório novo fora do repositório. A montagem recalcula os três
marcadores com ambos os hashes novos de DEX35 e carrossel, atualiza os quatro
`engineId` e lê de volta o ZIP inteiro, conferindo cada entrada.

## Dependências externas

Antes da montagem, ler o retorno do servidor sobre PSX. Se ele exigir
alteração produtiva no app, esta receita de seis entradas deve ser revista;
não afrouxar as guardas para acomodar mais alterações. Se o retorno aprovar
somente edições PSX HLE no servidor, manter o motor PSX e suas opções R164.

Após a montagem e assinatura com o certificado original, será necessário
entregar um novo kit privado **sem APK** e cadastrar aditivamente os quatro
`engineId` da candidata (PSX, N64, GameCube e Wii). Os IDs R164 cadastrados
no servidor não aceitam automaticamente os novos marcadores, mesmo quando
as políticas de jogo são idênticas. Só depois do recibo de cadastro cabem os
testes online nos telefones. O conserto de saída do anfitrião do servidor
também depende de aplicação e confirmação próprias.

O pacote final exige espaço para APK sem assinatura, APK alinhado e APK
assinado ao mesmo tempo (aproximadamente 8,2 GB ao todo). Conferir o espaço
livre em E: e F: e distribuir os temporários antes de montar. Não usar C:
como área de trabalho de APK nem publicar APK, chave, ROM ou kit privado no
Git público.
