# R164 — ponto estável de retorno para N64 em dois jogadores

**Registro de 15/10/2026.** O mantenedor informou que testou `007: The World Is Not Enough` online em **dois telefones na revisão mais recente**, com dois jogadores em partida, e pediu para salvar esta versão como estável. Este registro preserva a R164 como ponto de retorno para o cenário observado; não amplia o relato para três/quatro jogadores nem declara encerrada a falha de saída do anfitrião.

## Identidade preservada

- Fonte/receita do app: commit `1ae4a17f8addec954eb741ad691a37167597c50e`, ramo `build/station-selection-n64-cover-r164-20261015`.
- APK assinado R164: SHA-256 `903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210`, 2.715.466.850 bytes; arquivo privado `E:\StationVisualR164SelectionActions-20261015\final\TurboStations-Premium-R164-selection-actions.apk`. O APK não vai para o Git.
- Instalação A56: SHA-256 do `base.apk` conferido com o APK assinado no [recibo de seleção](evidence/a56-selection-qa.json).
- Instalação moto g52: `adb install -r` concluiu com `Success`; `sha256sum` do `base.apk` instalado retornou o mesmo SHA-256 integral. Dados preservados pela instalação de atualização.
- Servidor: [retorno efetivo R164](https://github.com/luziellacerda/Servidor-pix/blob/fix/station-r164-server-20261015/docs/station-android/r164/server-return.json), commit `346a74907a04b074a0fa7ae03a82de9cf7a9bf8c`. O kit privado SHA-256 `37e3b9dd5b8efaae1a222b27661cb7a838689fa2b484b16268e2efa26d11457a` foi aplicado; o motor N64 R164 e os 399 perfis revisados estão cadastrados.
- Capa `1080° Snowboarding`: publicada no catálogo revisão 100 e observada na seleção N64 do A56, com o snowboarder azul e a prancha vermelha da nova arte. O corpo servido foi conferido pelo servidor; a observação física foi visual, sem extração dos bytes de cache do telefone.

## Alcance do teste humano

O relato confirma uma partida online N64 de **dois jogadores** em `007: The World Is Not Enough` com os dois telefones atualizados. Não foram entregues nesta etapa medições de latência, quadros, temperatura ou registros USB da partida. O mantenedor informou expressamente que **não testou três nem quatro jogadores**. A saída do anfitrião e o aviso ao convidado também não foram descritos no relato.

## Pendências conhecidas

- O caminho de saída do anfitrião da R164 conserva a condição de corrida descrita em [HOST_EXIT_AUDIT.md](../../../integration/n64-online-video-extension-r162/HOST_EXIT_AUDIT.md): o convidado pode permanecer à espera se o frame terminal se perder ou o pedido `leave` ficar sem confirmação. Há correção de servidor preparada separadamente; ela não está implantada por este registro. A eventual repetição limitada do `leave` no app exigiria novo APK e nova identidade de motores.
- Prova física em três/quatro aparelhos, saída do anfitrião e comportamento sob perda de sinal permanecem abertas. Não usar o teste de dois jogadores como homologação desses cenários.
- O Edge 30 não foi incluído na confirmação de instalação R164: uma tentativa de transferência USB foi interrompida depois de ficar sem progresso. Não inferir que o aparelho foi atualizado.
- PSX continua sem modos por edição aprovados com HLE; a presença do motor no APK/servidor não libera jogos PSX online.

Este marco preserva código, receita e identidades verificadas para retorno. Não cria cópia adicional do APK, não publica binários privados e não altera a lógica de outros sistemas.
