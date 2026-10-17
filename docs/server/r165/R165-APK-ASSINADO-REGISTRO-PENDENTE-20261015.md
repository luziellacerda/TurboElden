# R165 combinada — APK assinado; cadastro dos motores pendente

## Estado e autoridades

- O retorno PSX do servidor foi publicado no commit `3f55caa582255ad87b508e95d24880d775bb9fe7` do ramo `feat/station-psx-online-20261015`: `serverDataPublished=true`, 84 edições no catálogo, 23 modos online aprovados em 19 edições, todos para dois participantes. O próprio retorno declara `physicalAndroidGameplayValidated=false`.
- O APK R165 foi montado sobre a R164 estável (`903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210`) e assinado com o certificado original (`7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`). SHA-256 final: `9e7ab2441e9d75568d5d2b741b4a0ed42e9a2d9f823698c0f39dccdcb7c19145`, 2.715.466.850 bytes; assinatura v2/v3 e alinhamento 16 KiB conferidos. **O APK não acompanha este handoff no Git.**
- O kit independente R165, sem APK, ROM, BIOS, chave, serial ou registros brutos de aparelho, tem SHA-256 `2e260ba80f93a0a9f65c1e2dca2f0632ce29b321dd895ad84d737e5a5628179b`, 12.985.386 bytes e 43 arquivos. Ele inclui `MANIFESTO-ARQUIVOS.json`, `incoming.json`, `engines-apk.json`, binários e provas. Conferir o ZIP e cada entrada antes do cadastro.
- Entrega privada: commit `bbe57e5b8761f60a4e264ac97fe410e5f3a712b5` do repositório `luziellacerda/TurboramaEmulationStation`, ramo `handoff/station-r165-combined-20261015`, pasta `station-server-handoffs/r165/`. O remoto foi lido de volta com o mesmo tamanho e SHA-256. O repositório público do app contém somente este handoff textual; o kit não está nele.
- Fonte de montagem congelada em `9d59b79571bcfc6e502b99a028c951bcd72a1eaf`. Uma checagem da receita de assinatura foi corrigida depois: o registro tem dois motores distintos para `neogeo`; a receita agora conta as 13 entradas e confere separadamente as quatro selecionadas. Essa correção não altera o APK.
- O instalador EXE R165 foi atualizado fora do Git, SHA-256 `5485da08b493ee92c9f4bb553e42985c8240bfcdddb7970e6fd653bbe30ad0c1`. O manifesto aponta para o único APK final, sem cópia embutida; validação do APK e simulações passaram.
- Instalação piloto no Galaxy A56 concluída às `2026-10-15T17:24:24Z` por USB com `install -r`, sem limpar dados nem forçar parada. O recibo confirmou `SUCCESS` e o SHA-256 do APK instalado igual ao assinado. A abertura e o visual ainda dependem de observação no telefone; nenhuma partida R165 foi validada.

## Alterações efetivas do APK

Somente seis entradas mudaram: `classes35.dex`, `lib/arm64-v8a/libturbo_carousel.so`, `assets/station-online/engines.json` e os marcadores `libstation_psx_online.so`, `libstation_mupen64plus_runtime.so`, `libstation_dolphin_runtime.so`. As outras 13.855 entradas foram conferidas byte a byte contra a R164. `classes36.dex`, núcleo PSX, ponte N64, frontend, manifesto Android, modos e política de jogo permanecem idênticos. O DEX35 corrige a saída humana confirmada do anfitrião N64; o carrossel aumenta a largura da capa principal 10% sobre a R164 e restringe o suporte iluminado do Mega Drive ao perfil ativo. A auditoria não encontrou segundo motor simultâneo nem introduziu timer, thread, consulta ou desenho extra por quadro.

## Identidades exatas para cadastro aditivo

| Plataforma | `engineId` R165 | `runtimeSha256` |
| --- | --- | --- |
| PSX | `pcsx-rearmed-ff81ed17-player-v3-0a01a6ef6e99` | `0a01a6ef6e99f0bb9b62f04b7cc17642e11f0aef83b691a8c308fc1722952e4b` |
| N64 | `mupen64plus-ae-33bf7021-n64-v3-a74636835393` | `a746368353933cb7786897bf5a3f57635bd8456711878f3c3cf72872dbbc9772` |
| GameCube | `dolphin-5102a033-gamecube-v3-85dda51eaeda` | `85dda51eaeda8e5b2bcc1f3ee4ed560390ad1705037c0151818a028c5738474a` |
| Wii | `dolphin-5102a033-wii-v3-85dda51eaeda` | `85dda51eaeda8e5b2bcc1f3ee4ed560390ad1705037c0151818a028c5738474a` |

Esses IDs substituem apenas a identidade desta candidata; **preservar os registros R164**. O PSX publicado está vinculado ao ID R164 `pcsx-rearmed-ff81ed17-player-v3-1b315b86b4a7`; não libera automaticamente a R165. O core PSX continua `e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9`. O valor genérico `clientMaximumPlayers=5` é aceito pelo servidor e filtra os modos de dois; não foi alterado sem falha comprovada.

## Trabalho exigido do servidor

1. Ler o [commit privado do kit](https://github.com/luziellacerda/TurboramaEmulationStation/commit/bbe57e5b8761f60a4e264ac97fe410e5f3a712b5), verificar SHA-256 do ZIP e `MANIFESTO-ARQUIVOS.json`, e comparar `incoming.json` com `engines-apk.json` e a prova assinada. Não é necessário receber o APK.
2. Cadastrar aditivamente os quatro owners R165 pela rotina vigente, com baseline fresca, trava de varredura e recibo. Preservar os 79 motores e vínculos anteriores.
3. Reavaliar o vínculo dos 23 modos PSX aprovados para o novo ID PSX usando edição, conteúdo, core, runtime, perfil e capacidade exatos. O livro de aprovações PSX não foi copiado para o kit. Não transferir aprovação só por nome de jogo ou plataforma.
4. Vincular as decisões N64 já revisadas aos owners R165 conforme os registros de proveniência do kit; conferir as opções `cpu=dynarec`, `video=glide64mk2` e `inputDelay=2`. Preservar a elegibilidade de GameCube/Wii conforme a política vigente.
5. Aplicar ou devolver status explícito do conserto de saída confirmada do anfitrião N64, commit `220bc64e88466c8e4f8cbdd4ccee6ac3728772ca`, que permanece em ramo separado. O DEX35 do app não substitui essa parte do servidor.
6. Devolver recibo com quatro IDs, hashes, contagens de modos admitidos/recusados, estado do host-exit e resultado da consulta pública. Só então testar R165 online em Android: PSX em dois aparelhos com a mesma edição aprovada, primeiro quadro, som e controles independentes; N64 com saída do anfitrião. A R164 permanece o retorno estável até teste físico aprovado.

Não há solicitação de mudança adicional na lógica PSX do aplicativo no retorno `3f55caa`. Este handoff é de cadastro e prova de compatibilidade da identidade R165.
